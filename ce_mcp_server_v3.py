#!/usr/bin/env python3
"""
IBM Code Engine MCP Server - Minimal Implementation
Tries to run without InitializationOptions
"""

import asyncio
import json
import logging
import os
import sys
import traceback
from typing import Any, Dict, List, Optional

# Import MCP components
from mcp.server import Server
import mcp.types as types

# Import our utilities
from utils import (
    create_code_engine_client,
    CodeEngineClient,
    CodeEngineError,
    format_project_summary,
    format_apps_summary
)

# Configure logging
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO').upper(),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global Code Engine client
ce_client: Optional[CodeEngineClient] = None

# MCP Server instance
server = Server("ibm-code-engine-mcp")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available Code Engine tools"""
    return [
        types.Tool(
            name="list_projects",
            description="List all IBM Code Engine projects in your account",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer", 
                        "description": "Maximum number of projects to return (default: 100)",
                        "default": 100,
                        "minimum": 1,
                        "maximum": 200
                    }
                },
                "additionalProperties": False
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """Handle tool calls for Code Engine operations"""
    global ce_client
    
    try:
        # Ensure we have a client
        if ce_client is None:
            logger.error("Code Engine client not initialized")
            return [types.TextContent(
                type="text",
                text="Error: Code Engine client not initialized. Please check your IBM Cloud API key."
            )]
        
        # Route to appropriate handler
        if name == "list_projects":
            return await handle_list_projects(arguments)
        else:
            return [types.TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )]
    
    except Exception as e:
        logger.error(f"Error handling tool call {name}: {e}")
        return [types.TextContent(
            type="text",
            text=f"Error executing {name}: {str(e)}"
        )]

async def handle_list_projects(arguments: dict) -> list[types.TextContent]:
    """Handle list_projects tool call"""
    try:
        limit = arguments.get('limit', 100)
        projects = ce_client.list_projects(limit=limit)
        
        # Format the response
        formatted_summary = format_project_summary(projects)
        raw_json = json.dumps(projects, indent=2, default=str)
        
        return [
            types.TextContent(
                type="text",
                text=f"{formatted_summary}\n\n**Raw JSON Data:**\n```json\n{raw_json}\n```"
            )
        ]
    
    except CodeEngineError as e:
        return [types.TextContent(type="text", text=f"Code Engine API error: {str(e)}")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Unexpected error: {str(e)}")]

async def main():
    """Main function to run the MCP server"""
    global ce_client
    
    try:
        # Initialize Code Engine client
        logger.info("Initializing IBM Code Engine MCP Server (minimal)...")
        
        api_key = os.getenv('IBMCLOUD_API_KEY')
        region = os.getenv('IBMCLOUD_REGION', 'us-south')
        
        if not api_key:
            logger.error("IBMCLOUD_API_KEY environment variable not set")
            sys.exit(1)
        
        # Create the Code Engine client
        ce_client = create_code_engine_client(api_key=api_key, region=region)
        logger.info(f"Code Engine client initialized for region: {region}")
        
        # Run the MCP server
        logger.info("Starting minimal MCP server...")
        
        # Try the simplest possible approach
        from mcp.server.stdio import stdio_server
        
        async with stdio_server() as (read_stream, write_stream):
            logger.info("Connected to stdio streams")
            # Try running with minimal parameters
            try:
                logger.info("Attempting to run server without InitializationOptions...")
                await server.run(read_stream, write_stream)
            except TypeError as e:
                logger.error(f"Server.run failed without InitializationOptions: {e}")
                logger.info("Server might require initialization options that we couldn't find")
                raise
        
    except KeyboardInterrupt:
        logger.info("Server interrupted by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())