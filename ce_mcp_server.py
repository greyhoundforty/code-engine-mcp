#!/usr/bin/env python3
"""
IBM Code Engine MCP Server
Provides MCP tools for interacting with IBM Code Engine resources
"""

import asyncio
import json
import logging
import os
import sys
import traceback
from typing import Any, Dict, List, Optional

import mcp.types as types
from mcp.server import Server
import mcp.server.stdio

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
    """
    List available Code Engine tools
    """
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
        ),
        types.Tool(
            name="list_app_revisions",
            description="List revisions for a specific application",
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
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of revisions to return (default: 100)",
                        "default": 100,
                        "minimum": 1,
                        "maximum": 200
                    }
                },
                "required": ["project_id", "app_name"],
                "additionalProperties": False
            }
        ),
        types.Tool(
            name="get_app_revision",
            description="Get detailed information about a specific application revision",
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
                    },
                    "revision_name": {
                        "type": "string",
                        "description": "Name of the revision"
                    }
                },
                "required": ["project_id", "app_name", "revision_name"],
                "additionalProperties": False
            }
        ),
        types.Tool(
            name="list_domain_mappings",
            description="List domain mappings in a specific Code Engine project",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Code Engine project ID"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of domain mappings to return (default: 100)",
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
            name="get_domain_mapping",
            description="Get detailed information about a specific domain mapping",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Code Engine project ID"
                    },
                    "domain_name": {
                        "type": "string",
                        "description": "Name of the domain mapping"
                    }
                },
                "required": ["project_id", "domain_name"],
                "additionalProperties": False
            }
        ),
        types.Tool(
            name="list_secrets",
            description="List secrets in a specific Code Engine project",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Code Engine project ID"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of secrets to return (default: 100)",
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
            name="get_secret",
            description="Get detailed information about a specific secret",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Code Engine project ID"
                    },
                    "secret_name": {
                        "type": "string",
                        "description": "Name of the secret"
                    }
                },
                "required": ["project_id", "secret_name"],
                "additionalProperties": False
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """
    Handle tool calls for Code Engine operations
    """
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
        elif name == "list_app_revisions":
            return await handle_list_app_revisions(arguments)
        elif name == "get_app_revision":
            return await handle_get_app_revision(arguments)
        elif name == "list_domain_mappings":
            return await handle_list_domain_mappings(arguments)
        elif name == "get_domain_mapping":
            return await handle_get_domain_mapping(arguments)
        elif name == "list_secrets":
            return await handle_list_secrets(arguments)
        elif name == "get_secret":
            return await handle_get_secret(arguments)
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
        
        # Also include raw JSON for detailed analysis
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
        
        # Format the response
        formatted_summary = format_apps_summary(apps, project_id)
        
        # Also include raw JSON for detailed analysis
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
        summary += f"• Updated: {app.get('updated_at', 'Unknown')}\n"
        
        if app.get('endpoint'):
            summary += f"• Endpoint: {app.get('endpoint')}\n"
        
        if app.get('scaling'):
            scaling = app.get('scaling', {})
            summary += f"• Min Instances: {scaling.get('min_scale', 'Unknown')}\n"
            summary += f"• Max Instances: {scaling.get('max_scale', 'Unknown')}\n"
        
        # Include raw JSON
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

async def handle_list_app_revisions(arguments: dict) -> list[types.TextContent]:
    """Handle list_app_revisions tool call"""
    try:
        project_id = arguments.get('project_id')
        app_name = arguments.get('app_name')
        limit = arguments.get('limit', 100)
        
        if not project_id or not app_name:
            return [types.TextContent(type="text", text="Error: project_id and app_name are required")]
        
        revisions = ce_client.list_app_revisions(
            project_id=project_id, 
            app_name=app_name, 
            limit=limit
        )
        
        # Format the response
        if not revisions:
            summary = f"No revisions found for application {app_name}"
        else:
            summary = f"Found {len(revisions)} revisions for application **{app_name}**:\n\n"
            for revision in revisions:
                summary += f"• **{revision.get('name', 'Unknown')}**\n"
                summary += f"  Status: {revision.get('status', 'Unknown')}\n"
                summary += f"  Image: {revision.get('image_reference', 'Unknown')}\n"
                summary += f"  Created: {revision.get('created_at', 'Unknown')}\n\n"
        
        # Include raw JSON
        raw_json = json.dumps(revisions, indent=2, default=str)
        
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

async def handle_get_app_revision(arguments: dict) -> list[types.TextContent]:
    """Handle get_app_revision tool call"""
    try:
        project_id = arguments.get('project_id')
        app_name = arguments.get('app_name')
        revision_name = arguments.get('revision_name')
        
        if not project_id or not app_name or not revision_name:
            return [types.TextContent(type="text", text="Error: project_id, app_name, and revision_name are required")]
        
        revision = ce_client.get_app_revision(
            project_id=project_id,
            app_name=app_name,
            revision_name=revision_name
        )
        
        # Format the response
        summary = f"**Revision: {revision.get('name', 'Unknown')}**\n\n"
        summary += f"• Application: {app_name}\n"
        summary += f"• Status: {revision.get('status', 'Unknown')}\n"
        summary += f"• Image: {revision.get('image_reference', 'Unknown')}\n"
        summary += f"• Created: {revision.get('created_at', 'Unknown')}\n"
        
        # Include raw JSON
        raw_json = json.dumps(revision, indent=2, default=str)
        
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

async def handle_list_domain_mappings(arguments: dict) -> list[types.TextContent]:
    """Handle list_domain_mappings tool call"""
    try:
        project_id = arguments.get('project_id')
        limit = arguments.get('limit', 100)
        
        if not project_id:
            return [types.TextContent(type="text", text="Error: project_id is required")]
        
        domain_mappings = ce_client.list_domain_mappings(project_id=project_id, limit=limit)
        
        # Format the response
        if not domain_mappings:
            summary = f"No domain mappings found in project {project_id}"
        else:
            summary = f"Found {len(domain_mappings)} domain mappings in project {project_id}:\n\n"
            for mapping in domain_mappings:
                summary += f"• **{mapping.get('name', 'Unknown')}**\n"
                summary += f"  Status: {mapping.get('status', 'Unknown')}\n"
                summary += f"  Component: {mapping.get('component', {}).get('name', 'Unknown')}\n"
                summary += f"  Created: {mapping.get('created_at', 'Unknown')}\n\n"
        
        # Include raw JSON
        raw_json = json.dumps(domain_mappings, indent=2, default=str)
        
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

async def handle_get_domain_mapping(arguments: dict) -> list[types.TextContent]:
    """Handle get_domain_mapping tool call"""
    try:
        project_id = arguments.get('project_id')
        domain_name = arguments.get('domain_name')
        
        if not project_id or not domain_name:
            return [types.TextContent(type="text", text="Error: project_id and domain_name are required")]
        
        domain_mapping = ce_client.get_domain_mapping(
            project_id=project_id,
            domain_name=domain_name
        )
        
        # Format the response
        summary = f"**Domain Mapping: {domain_mapping.get('name', 'Unknown')}**\n\n"
        summary += f"• Status: {domain_mapping.get('status', 'Unknown')}\n"
        summary += f"• Component: {domain_mapping.get('component', {}).get('name', 'Unknown')}\n"
        summary += f"• TLS Secret: {domain_mapping.get('tls_secret', 'None')}\n"
        summary += f"• Created: {domain_mapping.get('created_at', 'Unknown')}\n"
        
        # Include raw JSON
        raw_json = json.dumps(domain_mapping, indent=2, default=str)
        
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

async def handle_list_secrets(arguments: dict) -> list[types.TextContent]:
    """Handle list_secrets tool call"""
    try:
        project_id = arguments.get('project_id')
        limit = arguments.get('limit', 100)
        
        if not project_id:
            return [types.TextContent(type="text", text="Error: project_id is required")]
        
        secrets = ce_client.list_secrets(project_id=project_id, limit=limit)
        
        # Format the response
        if not secrets:
            summary = f"No secrets found in project {project_id}"
        else:
            summary = f"Found {len(secrets)} secrets in project {project_id}:\n\n"
            for secret in secrets:
                summary += f"• **{secret.get('name', 'Unknown')}**\n"
                summary += f"  Format: {secret.get('format', 'Unknown')}\n"
                summary += f"  Created: {secret.get('created_at', 'Unknown')}\n\n"
        
        # Include raw JSON (but mask sensitive data)
        masked_secrets = []
        for secret in secrets:
            masked_secret = secret.copy()
            if 'data' in masked_secret:
                masked_secret['data'] = {key: "***MASKED***" for key in masked_secret['data'].keys()}
            masked_secrets.append(masked_secret)
        
        raw_json = json.dumps(masked_secrets, indent=2, default=str)
        
        return [
            types.TextContent(
                type="text",
                text=f"{summary}\n\n**Raw JSON Data (sensitive data masked):**\n```json\n{raw_json}\n```"
            )
        ]
    
    except CodeEngineError as e:
        return [types.TextContent(type="text", text=f"Code Engine API error: {str(e)}")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Unexpected error: {str(e)}")]

async def handle_get_secret(arguments: dict) -> list[types.TextContent]:
    """Handle get_secret tool call"""
    try:
        project_id = arguments.get('project_id')
        secret_name = arguments.get('secret_name')
        
        if not project_id or not secret_name:
            return [types.TextContent(type="text", text="Error: project_id and secret_name are required")]
        
        secret = ce_client.get_secret(
            project_id=project_id,
            secret_name=secret_name
        )
        
        # Format the response
        summary = f"**Secret: {secret.get('name', 'Unknown')}**\n\n"
        summary += f"• Format: {secret.get('format', 'Unknown')}\n"
        summary += f"• Created: {secret.get('created_at', 'Unknown')}\n"
        summary += f"• Updated: {secret.get('updated_at', 'Unknown')}\n"
        
        if secret.get('data'):
            summary += f"• Keys: {', '.join(secret.get('data', {}).keys())}\n"
        
        # Mask sensitive data in JSON
        masked_secret = secret.copy()
        if 'data' in masked_secret:
            masked_secret['data'] = {key: "***MASKED***" for key in masked_secret['data'].keys()}
        
        raw_json = json.dumps(masked_secret, indent=2, default=str)
        
        return [
            types.TextContent(
                type="text",
                text=f"{summary}\n\n**Raw JSON Data (sensitive data masked):**\n```json\n{raw_json}\n```"
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
        logger.info("Initializing IBM Code Engine MCP Server...")
        
        # Get configuration from environment
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
        
        # Use the correct MCP server stdio setup
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                types.InitializationOptions(
                    server_name="ibm-code-engine-mcp",
                    server_version="1.0.0",
                ),
            )
    
    except KeyboardInterrupt:
        logger.info("Server interrupted by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())