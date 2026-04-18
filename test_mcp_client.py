#!/usr/bin/env python
"""
Test client for MCP server running over stdio.
Follows proper MCP protocol: initialize -> initialized -> call_tool.
Handles streaming responses with timeout and process monitoring.
"""

import json
import select
import subprocess
import sys
import time


def send_request(process, request):
    """Send a JSON-RPC request to the server."""
    request_json = json.dumps(request)
    process.stdin.write(request_json + "\n")
    process.stdin.flush()


def read_streaming_response(process, expected_id=None, timeout=5.0):
    """
    Read and parse streaming responses from the server.
    Handles responses that may be prefixed with "data: ".
    """
    start_time = time.time()
    
    while True:
        elapsed = time.time() - start_time
        if elapsed > timeout:
            return None
        
        if process.poll() is not None:
            return None
        
        try:
            ready, _, _ = select.select([process.stdout], [], [], 0.1)
            if not ready:
                continue
        except (ValueError, OSError):
            time.sleep(0.01)
            continue
        
        line = process.stdout.readline()
        if not line:
            return None
        
        line = line.strip()
        if not line:
            continue
        
        json_str = line
        if line.startswith("data:"):
            json_str = line[5:].strip()
        
        try:
            response = json.loads(json_str)
            if expected_id is None or response.get("id") == expected_id:
                return response
        except json.JSONDecodeError:
            continue


def test_mcp_server():
    """Test MCP server following proper protocol."""
    
    # Start the server process
    process = subprocess.Popen(
        [sys.executable, "mcp_server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    
    # Give the server a moment to initialize
    time.sleep(0.5)
    
    try:
        # Step 1: Send initialize request
        print("Sending initialize request...")
        initialize_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0"
                }
            }
        }
        send_request(process, initialize_request)
        
        # Read initialize response
        init_response = read_streaming_response(process, expected_id=1)
        if init_response:
            print(f"Initialize response: {json.dumps(init_response, indent=2)}")
        else:
            print("No initialize response received (timeout or process died)")
            return
        
        # Step 2: Send initialized notification
        print("\nSending initialized notification...")
        initialized_notification = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {}
        }
        send_request(process, initialized_notification)
        
        # Step 3: Send tools/list request
        print("\nSending tools/list request...")
        list_tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        send_request(process, list_tools_request)
        
        # Read tools/list response
        list_response = read_streaming_response(process, expected_id=2, timeout=10.0)
        if list_response:
            print(f"Tools list response: {json.dumps(list_response, indent=2)}")
        else:
            print("No tools list response received (timeout or process died)")
            return
        
        # Step 4: Send tools/call request
        print("\nSending tools/call request...")
        call_tool_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "analyze_csv_schema",
                "arguments": {
                    "csv_path": "data/sample_contacts.csv"
                }
            }
        }
        send_request(process, call_tool_request)
        
        # Read call_tool response
        tool_response = read_streaming_response(process, expected_id=3, timeout=30.0)
        if tool_response:
            print(f"\nTool response: {json.dumps(tool_response, indent=2)}")
        else:
            print("No tool response received (timeout or process died)")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Print any stderr output
        try:
            process.stdin.close()
        except Exception:
            pass
        
        stderr_output = process.stderr.read()
        if stderr_output:
            print("\nServer stderr:")
            print(stderr_output)
        
        # Clean up
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()


if __name__ == "__main__":
    test_mcp_server()
