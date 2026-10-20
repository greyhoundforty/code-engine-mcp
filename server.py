#!/usr/bin/env python3
"""
IBM Code Engine MCP Server

Wires the MCP protocol to the tool registry.  All tool definitions live
in the tools/ package; this file only handles startup and I/O plumbing.

Configuration (environment variables):
  IBMCLOUD_API_KEY  — required
  IBMCLOUD_REGION   — optional, default: us-south
  LOG_LEVEL         — optional, default: INFO
"""

import asyncio
import logging
import os
import sys

from mcp.server import InitializationOptions, Server
from mcp.server.stdio import stdio_server

import tools  # noqa: F401 — triggers registration of all 22 tools
from tools import registry
from utils import CodeEngineError, create_code_engine_client

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def create_server(client) -> Server:
    """Build and return a configured MCP Server bound to *client*."""
    app = Server("ibm-code-engine-mcp")

    @app.list_tools()
    async def list_tools():
        return registry.get_all()

    @app.call_tool()
    async def call_tool(name: str, arguments: dict):
        return await registry.dispatch(name, arguments, client)

    return app


async def main() -> None:
    api_key = os.getenv("IBMCLOUD_API_KEY")
    region = os.getenv("IBMCLOUD_REGION", "us-south")

    if not api_key:
        logger.error("IBMCLOUD_API_KEY environment variable not set")
        sys.exit(1)

    try:
        client = create_code_engine_client(api_key=api_key, region=region)
    except CodeEngineError as exc:
        logger.error(f"Failed to initialise Code Engine client: {exc}")
        sys.exit(1)

    logger.info(f"IBM Code Engine MCP Server starting (region: {region})")
    app = create_server(client)

    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="ibm-code-engine-mcp",
                server_version="1.0.0",
                capabilities={},
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
