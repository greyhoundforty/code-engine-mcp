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
    format_apps_summary,
    format_jobs_summary,
    format_job_runs_summary,
    mask_sensitive_data
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
            name="list_jobs",
            description="List batch jobs in a specific Code Engine project",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Code Engine project ID"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of jobs to return (default: 100)",
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
            name="get_job",
            description="Get detailed information about a specific batch job",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Code Engine project ID"
                    },
                    "job_name": {
                        "type": "string",
                        "description": "Name of the job"
                    }
                },
                "required": ["project_id", "job_name"],
                "additionalProperties": False
            }
        ),
        types.Tool(
            name="list_job_runs",
            description="List job runs for a specific job or all jobs in a project",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Code Engine project ID"
                    },
                    "job_name": {
                        "type": "string",
                        "description": "Optional job name to filter runs (if not provided, lists all job runs)"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of job runs to return (default: 100)",
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
            name="get_job_run",
            description="Get detailed information about a specific job run",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Code Engine project ID"
                    },
                    "job_run_name": {
                        "type": "string",
                        "description": "Name of the job run"
                    }
                },
                "required": ["project_id", "job_run_name"],
                "additionalProperties": False
            }
        ),
        types.Tool(
            name="list_secrets",
            description="List secrets in a specific Code Engine project (sensitive data masked)",
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
            description="Get detailed information about a specific secret (sensitive data masked)",
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
        elif name == "list_app_revisions":
            return await handle_list_app_revisions(arguments)
        elif name == "get_app_revision":
            return await handle_get_app_revision(arguments)
        elif name == "list_domain_mappings":
            return await handle_list_domain_mappings(arguments)
        elif name == "get_domain_mapping":
            return await handle_get_domain_mapping(arguments)
        elif name == "list_jobs":
            return await handle_list_jobs(arguments)
        elif name == "get_job":
            return await handle_get_job(arguments)
        elif name == "list_job_runs":
            return await handle_list_job_runs(arguments)
        elif name == "get_job_run":
            return await handle_get_job_run(arguments)
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
        applications = ce_client.list_applications(project_id=project_id, limit=limit)
        
        formatted_summary = format_apps_summary(applications)
        raw_json = json.dumps(applications, indent=2, default=str)
        
        return [types.TextContent(
            type="text",
            text=f"{formatted_summary}\n\n**Raw JSON Data:**\n```json\n{raw_json}\n```"
        )]
    
    except CodeEngineError as e:
        return [types.TextContent(type="text", text=f"Code Engine API error: {str(e)}")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Unexpected error: {str(e)}")]

async def handle_get_application(arguments: dict) -> list[types.TextContent]:
    """Handle get_application tool call"""
    try:
        project_id = arguments.get('project_id')
        app_name = arguments.get('app_name')
        application = ce_client.get_application(project_id=project_id, app_name=app_name)
        
        raw_json = json.dumps(application, indent=2, default=str)
        
        return [types.TextContent(
            type="text",
            text=f"**Application Details for {app_name}:**\n```json\n{raw_json}\n```"
        )]
    
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
        revisions = ce_client.list_app_revisions(project_id=project_id, app_name=app_name, limit=limit)
        
        # Format summary
        if not revisions:
            formatted_summary = f"No revisions found for application {app_name} in project {project_id}."
        else:
            formatted_summary = f"Found {len(revisions)} revisions for application {app_name}:\n\n"
            for revision in revisions:
                formatted_summary += f"• **{revision.get('name', 'Unknown')}**\n"
                formatted_summary += f"  Status: {revision.get('status', 'Unknown')}\n"
                formatted_summary += f"  Created: {revision.get('created_at', 'Unknown')}\n"
                if revision.get('scale_config'):
                    scale = revision.get('scale_config', {})
                    formatted_summary += f"  Scale: {scale.get('min_scale', 0)}-{scale.get('max_scale', 1)} instances\n"
                formatted_summary += "\n"
        
        raw_json = json.dumps(revisions, indent=2, default=str)
        
        return [types.TextContent(
            type="text",
            text=f"{formatted_summary}\n\n**Raw JSON Data:**\n```json\n{raw_json}\n```"
        )]
    
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
        revision = ce_client.get_app_revision(project_id=project_id, app_name=app_name, revision_name=revision_name)
        
        raw_json = json.dumps(revision, indent=2, default=str)
        
        return [types.TextContent(
            type="text",
            text=f"**App Revision Details for {revision_name}:**\n```json\n{raw_json}\n```"
        )]
    
    except CodeEngineError as e:
        return [types.TextContent(type="text", text=f"Code Engine API error: {str(e)}")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Unexpected error: {str(e)}")]

async def handle_list_domain_mappings(arguments: dict) -> list[types.TextContent]:
    """Handle list_domain_mappings tool call"""
    try:
        project_id = arguments.get('project_id')
        limit = arguments.get('limit', 100)
        domain_mappings = ce_client.list_domain_mappings(project_id=project_id, limit=limit)
        
        # Format summary
        if not domain_mappings:
            formatted_summary = f"No domain mappings found in project {project_id}."
        else:
            formatted_summary = f"Found {len(domain_mappings)} domain mappings in project {project_id}:\n\n"
            for mapping in domain_mappings:
                formatted_summary += f"• **{mapping.get('name', 'Unknown')}**\n"
                formatted_summary += f"  Status: {mapping.get('status', 'Unknown')}\n"
                formatted_summary += f"  Created: {mapping.get('created_at', 'Unknown')}\n"
                if mapping.get('target'):
                    target = mapping.get('target', {})
                    formatted_summary += f"  Target: {target.get('type', 'Unknown')} - {target.get('name', 'Unknown')}\n"
                formatted_summary += "\n"
        
        raw_json = json.dumps(domain_mappings, indent=2, default=str)
        
        return [types.TextContent(
            type="text",
            text=f"{formatted_summary}\n\n**Raw JSON Data:**\n```json\n{raw_json}\n```"
        )]
    
    except CodeEngineError as e:
        return [types.TextContent(type="text", text=f"Code Engine API error: {str(e)}")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Unexpected error: {str(e)}")]

async def handle_get_domain_mapping(arguments: dict) -> list[types.TextContent]:
    """Handle get_domain_mapping tool call"""
    try:
        project_id = arguments.get('project_id')
        domain_name = arguments.get('domain_name')
        domain_mapping = ce_client.get_domain_mapping(project_id=project_id, domain_name=domain_name)
        
        raw_json = json.dumps(domain_mapping, indent=2, default=str)
        
        return [types.TextContent(
            type="text",
            text=f"**Domain Mapping Details for {domain_name}:**\n```json\n{raw_json}\n```"
        )]
    
    except CodeEngineError as e:
        return [types.TextContent(type="text", text=f"Code Engine API error: {str(e)}")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Unexpected error: {str(e)}")]

async def handle_list_jobs(arguments: dict) -> list[types.TextContent]:
    """Handle list_jobs tool call"""
    try:
        project_id = arguments.get('project_id')
        limit = arguments.get('limit', 100)
        jobs = ce_client.list_jobs(project_id=project_id, limit=limit)
        
        formatted_summary = format_jobs_summary(jobs)
        raw_json = json.dumps(jobs, indent=2, default=str)
        
        return [types.TextContent(
            type="text",
            text=f"{formatted_summary}\n\n**Raw JSON Data:**\n```json\n{raw_json}\n```"
        )]
    
    except CodeEngineError as e:
        return [types.TextContent(type="text", text=f"Code Engine API error: {str(e)}")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Unexpected error: {str(e)}")]

async def handle_get_job(arguments: dict) -> list[types.TextContent]:
    """Handle get_job tool call"""
    try:
        project_id = arguments.get('project_id')
        job_name = arguments.get('job_name')
        job = ce_client.get_job(project_id=project_id, job_name=job_name)
        
        raw_json = json.dumps(job, indent=2, default=str)
        
        return [types.TextContent(
            type="text",
            text=f"**Job Details for {job_name}:**\n```json\n{raw_json}\n```"
        )]
    
    except CodeEngineError as e:
        return [types.TextContent(type="text", text=f"Code Engine API error: {str(e)}")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Unexpected error: {str(e)}")]

async def handle_list_job_runs(arguments: dict) -> list[types.TextContent]:
    """Handle list_job_runs tool call"""
    try:
        project_id = arguments.get('project_id')
        job_name = arguments.get('job_name')  # Optional
        limit = arguments.get('limit', 100)
        job_runs = ce_client.list_job_runs(project_id=project_id, job_name=job_name, limit=limit)
        
        formatted_summary = format_job_runs_summary(job_runs, job_name=job_name or "")
        raw_json = json.dumps(job_runs, indent=2, default=str)
        
        return [types.TextContent(
            type="text",
            text=f"{formatted_summary}\n\n**Raw JSON Data:**\n```json\n{raw_json}\n```"
        )]
    
    except CodeEngineError as e:
        return [types.TextContent(type="text", text=f"Code Engine API error: {str(e)}")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Unexpected error: {str(e)}")]

async def handle_get_job_run(arguments: dict) -> list[types.TextContent]:
    """Handle get_job_run tool call"""
    try:
        project_id = arguments.get('project_id')
        job_run_name = arguments.get('job_run_name')
        job_run = ce_client.get_job_run(project_id=project_id, job_run_name=job_run_name)
        
        raw_json = json.dumps(job_run, indent=2, default=str)
        
        return [types.TextContent(
            type="text",
            text=f"**Job Run Details for {job_run_name}:**\n```json\n{raw_json}\n```"
        )]
    
    except CodeEngineError as e:
        return [types.TextContent(type="text", text=f"Code Engine API error: {str(e)}")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Unexpected error: {str(e)}")]

async def handle_list_secrets(arguments: dict) -> list[types.TextContent]:
    """Handle list_secrets tool call"""
    try:
        project_id = arguments.get('project_id')
        limit = arguments.get('limit', 100)
        secrets = ce_client.list_secrets(project_id=project_id, limit=limit)
        
        # Mask sensitive data
        masked_secrets = [mask_sensitive_data(secret) for secret in secrets]
        
        # Format summary
        if not masked_secrets:
            formatted_summary = f"No secrets found in project {project_id}."
        else:
            formatted_summary = f"Found {len(masked_secrets)} secrets in project {project_id}:\n\n"
            for secret in masked_secrets:
                formatted_summary += f"• **{secret.get('name', 'Unknown')}**\n"
                formatted_summary += f"  Type: {secret.get('format', 'Unknown')}\n"
                formatted_summary += f"  Created: {secret.get('created_at', 'Unknown')}\n"
                if secret.get('data'):
                    data_keys = list(secret['data'].keys())
                    formatted_summary += f"  Keys: {', '.join(data_keys)}\n"
                formatted_summary += "\n"
        
        raw_json = json.dumps(masked_secrets, indent=2, default=str)
        
        return [types.TextContent(
            type="text",
            text=f"{formatted_summary}\n\n**Raw JSON Data (sensitive data masked):**\n```json\n{raw_json}\n```"
        )]
    
    except CodeEngineError as e:
        return [types.TextContent(type="text", text=f"Code Engine API error: {str(e)}")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Unexpected error: {str(e)}")]

async def handle_get_secret(arguments: dict) -> list[types.TextContent]:
    """Handle get_secret tool call"""
    try:
        project_id = arguments.get('project_id')
        secret_name = arguments.get('secret_name')
        secret = ce_client.get_secret(project_id=project_id, secret_name=secret_name)
        
        # Mask sensitive data
        masked_secret = mask_sensitive_data(secret)
        
        raw_json = json.dumps(masked_secret, indent=2, default=str)
        
        return [types.TextContent(
            type="text",
            text=f"**Secret Details for {secret_name} (sensitive data masked):**\n```json\n{raw_json}\n```"
        )]
    
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
        logger.info("Starting MCP server with proper initialization...")
        
        # Import required MCP components
        from mcp.server.stdio import stdio_server
        from mcp.server import InitializationOptions
        
        # Create initialization options
        init_options = InitializationOptions(
            server_name="ibm-code-engine-mcp",
            server_version="1.0.0",
            capabilities={}
        )
        
        async with stdio_server() as (read_stream, write_stream):
            logger.info("Connected to stdio streams")
            logger.info("Running server with InitializationOptions...")
            await server.run(read_stream, write_stream, init_options)
        
    except KeyboardInterrupt:
        logger.info("Server interrupted by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())