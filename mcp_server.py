#!/usr/bin/env python

import asyncio

from fastmcp import FastMCP
from src.alignment_service import analyze_csv_schema


def create_server() -> FastMCP:
    server = FastMCP(name="canonical-alignment-server")

    @server.tool(name="analyze_csv_schema")
    def analyze_csv_schema_tool(csv_path: str):
        try:
            result = analyze_csv_schema(csv_path)
            return result
        except Exception as e:
            return {"error": str(e)}

    return server

    return server


async def main() -> None:
    server = create_server()
    await server.run_stdio_async()


if __name__ == "__main__":
    asyncio.run(main())