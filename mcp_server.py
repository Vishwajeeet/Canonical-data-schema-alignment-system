#!/usr/bin/env python

import asyncio

from fastmcp import FastMCP
from src.alignment_service import analyze_csv_schema


def create_server() -> FastMCP:
    server = FastMCP(name="canonical-alignment-server")

    @server.tool(name="analyze_csv_schema")
    async def analyze_csv_schema_tool(csv_path: str) -> dict:
        """
        Analyze a CSV file and map its schema to the canonical schema.
        
        Args:
            csv_path: Path to the CSV file to analyze.
            
        Returns:
            Dict with keys:
            - "accepted": List of mappings that passed validation
            - "needs_review": List of {mapping, reason} objects needing human review
            {"error": "error message"} if analysis fails.
        """
        try:
            # Run the blocking alignment service call in a thread pool
            # Service already returns JSON-serializable format
            result = await asyncio.to_thread(analyze_csv_schema, csv_path)
            return result
        except Exception as e:
            return {"error": str(e)}

    return server


async def main() -> None:
    server = create_server()
    await server.run_stdio_async()


if __name__ == "__main__":
    asyncio.run(main())