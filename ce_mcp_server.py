#!/usr/bin/env python3
"""
IBM Code Engine MCP Server - Alternative Implementation
Uses a different approach to MCP server initialization
"""

import asyncio
import json
import logging
import os
import sys
import traceback
from typing import Optional

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
        ),
        types.Tool(
            name="list_applications",
            description="List applications in a specific Code Engine project",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Code Engine project ID"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of applications to return (default: 100)",
                        "default": 100,
                        "minimum": 1,
                        "maximum": 200
                    }
                },
                "required": ["project_id"],
                "additionalProperties": False
            }
        ),
        types.Tool(
            name="get_application",
            description="Get detailed information about a specific application",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Code Engine project ID"
                    },
                    "app_name": {
                        "type": "string",
                        "description": "Name of the application"
                    }
                },
                "required": ["project_id", "app_name"],
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
        elif name == "list_applications":
            return await handle_list_applications(arguments)
        elif name == "get_application":
            return await handle_get_application(arguments)
        else:
            return [types.TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )]

    except Exception as e:
        logger.error(f"Error handling tool call {name}: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
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

async def handle_list_applications(arguments: dict) -> list[types.TextContent]:
    """Handle list_applications tool call"""
    try:
        project_id = arguments.get('project_id')
        limit = arguments.get('limit', 100)

        if not project_id:
            return [types.TextContent(type="text", text="Error: project_id is required")]

        apps = ce_client.list_applications(project_id=project_id, limit=limit)
        formatted_summary = format_apps_summary(apps, project_id)
        raw_json = json.dumps(apps, indent=2, default=str)

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

async def handle_get_application(arguments: dict) -> list[types.TextContent]:
    """Handle get_application tool call"""
    try:
        project_id = arguments.get('project_id')
        app_name = arguments.get('app_name')

        if not project_id or not app_name:
            return [types.TextContent(type="text", text="Error: project_id and app_name are required")]

        app = ce_client.get_application(project_id=project_id, app_name=app_name)

        # Format the response
        summary = f"**Application: {app.get('name', 'Unknown')}**\n\n"
        summary += f"• Status: {app.get('status', 'Unknown')}\n"
        summary += f"• Image: {app.get('image_reference', 'Unknown')}\n"
        summary += f"• Created: {app.get('created_at', 'Unknown')}\n"

        if app.get('endpoint'):
            summary += f"• Endpoint: {app.get('endpoint')}\n"

        raw_json = json.dumps(app, indent=2, default=str)

        return [
            types.TextContent(
                type="text",
                text=f"{summary}\n\n**Raw JSON Data:**\n```json\n{raw_json}\n```"
            )
        ]

    except CodeEngineError as e:
        return [types.TextContent(type="text", text=f"Code Engine API error: {str(e)}")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Unexpected error: {str(e)}")]

async def run_server():
    """Run the MCP server using different approaches"""
    try:
        # Method 1: Try the standard stdio approach
        logger.info("Trying standard stdio approach...")

        try:
            import mcp.server.stdio
            if hasattr(mcp.server.stdio, 'stdio_server'):
                logger.info("Using mcp.server.stdio.stdio_server")

                # Try to find InitializationOptions
                init_options = None
                try:
                    from mcp.server.models import InitializationOptions
                    init_options = InitializationOptions(
                        server_name="ibm-code-engine-mcp",
                        server_version="1.0.0",
                        capabilities={}
                    )
                    logger.info("Using InitializationOptions from mcp.server.models")
                except ImportError:
                    try:
                        from mcp.server import InitializationOptions
                        init_options = InitializationOptions(
                            server_name="ibm-code-engine-mcp",
                            server_version="1.0.0",
                            capabilities={}
                        )
                        logger.info("Using InitializationOptions from mcp.server")
                    except ImportError:
                        logger.warning("InitializationOptions not found - trying without it")
                        init_options = None

                async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
                    if init_options:
                        await server.run(read_stream, write_stream, init_options)
                    else:
                        # Try running without InitializationOptions
                        await server.run(read_stream, write_stream)
                return
        except (ImportError, AttributeError) as e:
            logger.warning(f"Standard stdio approach failed: {e}")

        # Method 2: Try direct stdio import
        try:
            from mcp.server.stdio import stdio_server
            logger.info("Using direct stdio_server import")

            async with stdio_server() as (read_stream, write_stream):
                # Try without initialization options first
                try:
                    await server.run(read_stream, write_stream)
                except TypeError:
                    # If it requires initialization options, we'll handle that separately
                    logger.warning("Server.run requires initialization options, but they're not available")
                    raise
            return
        except ImportError as e:
            logger.warning(f"Direct stdio import failed: {e}")

        # Method 3: Try alternative approach
        logger.warning("Trying alternative server startup...")
        logger.error("All stdio methods failed. Please check MCP library version.")
        raise Exception("Could not initialize MCP stdio server")

    except Exception as e:
        logger.error(f"Server startup failed: {e}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise

async def main():
    """Main function to run the MCP server"""
    global ce_client

    try:
        # Initialize Code Engine client
        logger.info("Initializing IBM Code Engine MCP Server...")

        api_key = os.getenv('IBMCLOUD_API_KEY')
        region = os.getenv('IBMCLOUD_REGION', 'us-south')

        if not api_key:
            logger.error("IBMCLOUD_API_KEY environment variable not set")
            sys.exit(1)

        # Create the Code Engine client
        ce_client = create_code_engine_client(api_key=api_key, region=region)
        logger.info(f"Code Engine client initialized for region: {region}")

        # Run the MCP server
        logger.info("Starting MCP server...")
        await run_server()

    except KeyboardInterrupt:
        logger.info("Server interrupted by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
