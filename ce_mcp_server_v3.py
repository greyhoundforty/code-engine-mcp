#!/usr/bin/env python3
"""
IBM Code Engine MCP Server - Model Context Protocol Implementation

This MCP server provides Claude Code and Claude Desktop with tools to interact with
IBM Cloud Code Engine services. It exposes 22 tools across 6 categories for managing
serverless applications, batch jobs, builds, and related resources.

AVAILABLE TOOLS (22 total):

Project Management (2 tools):
  - list_projects: List all Code Engine projects
  - find_project_by_name: Find project by name with resource group filtering

Application Management (7 tools):
  - list_applications: List apps in a project
  - get_application: Get app details and configuration
  - create_application: Create app from pre-built image
  - update_application: Update app configuration
  - create_app_from_source: Deploy from local source (build + deploy)
  - list_app_revisions: List application deployment history
  - get_app_revision: Get specific revision details

Build Management (5 tools):
  - create_build: Create build configuration from Git source
  - list_builds: List build configurations
  - create_build_run: Execute a build
  - get_build_run: Get build run status
  - list_build_runs: List build runs with filtering

Job Management (4 tools):
  - list_jobs: List batch jobs
  - get_job: Get job details
  - list_job_runs: List job executions
  - get_job_run: Get job run status

Domain Management (2 tools):
  - list_domain_mappings: List custom domain mappings
  - get_domain_mapping: Get domain mapping details

Secret Management (2 tools):
  - list_secrets: List secrets (data masked)
  - get_secret: Get secret details (data masked)

CONFIGURATION:
  Required environment variables:
    - IBMCLOUD_API_KEY: IBM Cloud API key for authentication
  Optional environment variables:
    - IBMCLOUD_REGION: IBM Cloud region (default: us-south)
    - LOG_LEVEL: Logging level (default: INFO)

USAGE:
  Run as MCP server via Docker:
    docker run -i --rm --env-file ~/.mcp.env code-engine-mcp:latest

  Run locally for development:
    export IBMCLOUD_API_KEY=your-api-key
    python3 ce_mcp_server_v3.py

SECURITY:
  - All secret values are automatically masked in responses
  - API keys loaded via environment variables (never cached)
  - Container runs as non-root user
  - Ephemeral containers (--rm flag)

See TOOLS.md for detailed documentation of all available tools.
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
        ),
        types.Tool(
            name="create_application",
            description="Create a new Code Engine application with specified configuration",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Code Engine project ID"
                    },
                    "app_name": {
                        "type": "string",
                        "description": "Name for the new application"
                    },
                    "image_reference": {
                        "type": "string",
                        "description": "Container image reference (e.g., 'icr.io/namespace/image:tag')"
                    },
                    "image_port": {
                        "type": "integer",
                        "description": "Port the application listens on (default: 8080)",
                        "default": 8080
                    },
                    "scale_min_instances": {
                        "type": "integer",
                        "description": "Minimum number of instances (default: 0)",
                        "default": 0
                    },
                    "scale_max_instances": {
                        "type": "integer",
                        "description": "Maximum number of instances (default: 10)",
                        "default": 10
                    },
                    "scale_cpu_limit": {
                        "type": "string",
                        "description": "CPU limit per instance (e.g., '1', '0.5')",
                        "default": "1"
                    },
                    "scale_memory_limit": {
                        "type": "string",
                        "description": "Memory limit per instance (e.g., '4G', '2G')",
                        "default": "4G"
                    },
                    "managed_domain_mappings": {
                        "type": "string",
                        "description": "Domain mapping visibility: 'local_public', 'local_private', 'local'",
                        "default": "local_public"
                    }
                },
                "required": ["project_id", "app_name", "image_reference"],
                "additionalProperties": False
            }
        ),
        types.Tool(
            name="update_application",
            description="Update an existing Code Engine application",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Code Engine project ID"
                    },
                    "app_name": {
                        "type": "string",
                        "description": "Name of the application to update"
                    },
                    "image_reference": {
                        "type": "string",
                        "description": "New container image reference"
                    },
                    "scale_min_instances": {
                        "type": "integer",
                        "description": "Minimum number of instances"
                    },
                    "scale_max_instances": {
                        "type": "integer",
                        "description": "Maximum number of instances"
                    },
                    "scale_cpu_limit": {
                        "type": "string",
                        "description": "CPU limit per instance"
                    },
                    "scale_memory_limit": {
                        "type": "string",
                        "description": "Memory limit per instance"
                    }
                },
                "required": ["project_id", "app_name"],
                "additionalProperties": False
            }
        ),
        types.Tool(
            name="create_build",
            description="Create a new build configuration for building container images from source",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Code Engine project ID"
                    },
                    "build_name": {
                        "type": "string",
                        "description": "Name for the build configuration"
                    },
                    "output_image": {
                        "type": "string",
                        "description": "Output container image reference (e.g., 'icr.io/namespace/image:tag')"
                    },
                    "output_secret": {
                        "type": "string",
                        "description": "Name of secret for pushing to container registry"
                    },
                    "source_url": {
                        "type": "string",
                        "description": "Git repository URL containing source code"
                    },
                    "source_revision": {
                        "type": "string",
                        "description": "Git branch, tag, or commit (default: 'main')",
                        "default": "main"
                    },
                    "source_context_dir": {
                        "type": "string",
                        "description": "Directory in repo containing source (default: root)"
                    },
                    "strategy_type": {
                        "type": "string",
                        "description": "Build strategy: 'dockerfile' or 'buildpacks' (default: 'dockerfile')",
                        "default": "dockerfile"
                    },
                    "strategy_spec_file": {
                        "type": "string",
                        "description": "Path to Dockerfile (default: './Dockerfile')",
                        "default": "./Dockerfile"
                    },
                    "strategy_size": {
                        "type": "string",
                        "description": "Build resources: 'small', 'medium', 'large', 'xlarge' (default: 'medium')",
                        "default": "medium"
                    }
                },
                "required": ["project_id", "build_name", "output_image", "output_secret", "source_url"],
                "additionalProperties": False
            }
        ),
        types.Tool(
            name="create_build_run",
            description="Execute a build to create a container image from source code",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Code Engine project ID"
                    },
                    "build_name": {
                        "type": "string",
                        "description": "Name of existing build configuration to execute"
                    },
                    "name": {
                        "type": "string",
                        "description": "Optional name for this build run"
                    }
                },
                "required": ["project_id", "build_name"],
                "additionalProperties": False
            }
        ),
        types.Tool(
            name="get_build_run",
            description="Get the status and details of a build run",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Code Engine project ID"
                    },
                    "build_run_name": {
                        "type": "string",
                        "description": "Name of the build run"
                    }
                },
                "required": ["project_id", "build_run_name"],
                "additionalProperties": False
            }
        ),
        types.Tool(
            name="list_builds",
            description="List all build configurations in a project",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Code Engine project ID"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of builds to return (default: 100)",
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
            name="list_build_runs",
            description="List build runs in a project, optionally filtered by build name",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Code Engine project ID"
                    },
                    "build_name": {
                        "type": "string",
                        "description": "Optional: filter by build configuration name"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of build runs to return (default: 100)",
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
            name="find_project_by_name",
            description="Find a Code Engine project by name, optionally filtered by resource group",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_name": {
                        "type": "string",
                        "description": "Name of the project to find"
                    },
                    "resource_group_id": {
                        "type": "string",
                        "description": "Optional resource group ID to filter search"
                    }
                },
                "required": ["project_name"],
                "additionalProperties": False
            }
        ),
        types.Tool(
            name="create_app_from_source",
            description="Deploy application from local source using Code Engine's integrated build-source feature. Packages source, builds Docker image, and deploys automatically.",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Code Engine project ID"
                    },
                    "app_name": {
                        "type": "string",
                        "description": "Name of the application to create"
                    },
                    "source_path": {
                        "type": "string",
                        "description": "Path to source code directory (default: '.')",
                        "default": "."
                    },
                    "port": {
                        "type": "integer",
                        "description": "Port the application listens on (default: 8080)",
                        "default": 8080,
                        "minimum": 1,
                        "maximum": 65535
                    },
                    "image_name": {
                        "type": "string",
                        "description": "Optional custom image name (e.g., 'private.us.icr.io/namespace/image:tag')"
                    },
                    "min_scale": {
                        "type": "integer",
                        "description": "Minimum number of instances (default: 1)",
                        "default": 1,
                        "minimum": 0,
                        "maximum": 100
                    },
                    "max_scale": {
                        "type": "integer",
                        "description": "Maximum number of instances (default: 10)",
                        "default": 10,
                        "minimum": 1,
                        "maximum": 100
                    },
                    "cpu_limit": {
                        "type": "string",
                        "description": "CPU limit per instance (default: '0.5')",
                        "default": "0.5"
                    },
                    "memory_limit": {
                        "type": "string",
                        "description": "Memory limit per instance (default: '4G')",
                        "default": "4G"
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
        elif name == "create_application":
            return await handle_create_application(arguments)
        elif name == "update_application":
            return await handle_update_application(arguments)
        elif name == "create_build":
            return await handle_create_build(arguments)
        elif name == "create_build_run":
            return await handle_create_build_run(arguments)
        elif name == "get_build_run":
            return await handle_get_build_run(arguments)
        elif name == "list_builds":
            return await handle_list_builds(arguments)
        elif name == "list_build_runs":
            return await handle_list_build_runs(arguments)
        elif name == "find_project_by_name":
            return await handle_find_project_by_name(arguments)
        elif name == "create_app_from_source":
            return await handle_create_app_from_source(arguments)
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

async def handle_create_application(arguments: dict) -> list[types.TextContent]:
    """Handle create_application tool call"""
    try:
        project_id = arguments.get('project_id')
        app_name = arguments.get('app_name')
        image_reference = arguments.get('image_reference')
        
        # Optional parameters
        kwargs = {}
        if 'image_port' in arguments:
            kwargs['image_port'] = arguments['image_port']
        if 'scale_min_instances' in arguments:
            kwargs['scale_min_instances'] = arguments['scale_min_instances']
        if 'scale_max_instances' in arguments:
            kwargs['scale_max_instances'] = arguments['scale_max_instances']
        if 'scale_cpu_limit' in arguments:
            kwargs['scale_cpu_limit'] = arguments['scale_cpu_limit']
        if 'scale_memory_limit' in arguments:
            kwargs['scale_memory_limit'] = arguments['scale_memory_limit']
        if 'managed_domain_mappings' in arguments:
            kwargs['managed_domain_mappings'] = arguments['managed_domain_mappings']
        
        app = ce_client.create_application(
            project_id=project_id,
            app_name=app_name,
            image_reference=image_reference,
            **kwargs
        )
        
        raw_json = json.dumps(app, indent=2, default=str)
        
        return [types.TextContent(
            type="text",
            text=f"**Application {app_name} created successfully!**\n\n```json\n{raw_json}\n```"
        )]
    
    except CodeEngineError as e:
        return [types.TextContent(type="text", text=f"Code Engine API error: {str(e)}")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Unexpected error: {str(e)}")]

async def handle_update_application(arguments: dict) -> list[types.TextContent]:
    """Handle update_application tool call"""
    try:
        project_id = arguments.get('project_id')
        app_name = arguments.get('app_name')
        
        # Build kwargs from optional parameters
        kwargs = {}
        if 'image_reference' in arguments:
            kwargs['image_reference'] = arguments['image_reference']
        if 'scale_min_instances' in arguments:
            kwargs['scale_min_instances'] = arguments['scale_min_instances']
        if 'scale_max_instances' in arguments:
            kwargs['scale_max_instances'] = arguments['scale_max_instances']
        if 'scale_cpu_limit' in arguments:
            kwargs['scale_cpu_limit'] = arguments['scale_cpu_limit']
        if 'scale_memory_limit' in arguments:
            kwargs['scale_memory_limit'] = arguments['scale_memory_limit']
        
        app = ce_client.update_application(
            project_id=project_id,
            app_name=app_name,
            **kwargs
        )
        
        raw_json = json.dumps(app, indent=2, default=str)
        
        return [types.TextContent(
            type="text",
            text=f"**Application {app_name} updated successfully!**\n\n```json\n{raw_json}\n```"
        )]
    
    except CodeEngineError as e:
        return [types.TextContent(type="text", text=f"Code Engine API error: {str(e)}")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Unexpected error: {str(e)}")]

async def handle_create_build(arguments: dict) -> list[types.TextContent]:
    """Handle create_build tool call"""
    try:
        project_id = arguments.get('project_id')
        build_name = arguments.get('build_name')
        output_image = arguments.get('output_image')
        output_secret = arguments.get('output_secret')
        source_url = arguments.get('source_url')
        
        # Optional parameters
        kwargs = {}
        if 'source_revision' in arguments:
            kwargs['source_revision'] = arguments['source_revision']
        if 'source_context_dir' in arguments:
            kwargs['source_context_dir'] = arguments['source_context_dir']
        if 'strategy_type' in arguments:
            kwargs['strategy_type'] = arguments['strategy_type']
        if 'strategy_spec_file' in arguments:
            kwargs['strategy_spec_file'] = arguments['strategy_spec_file']
        if 'strategy_size' in arguments:
            kwargs['strategy_size'] = arguments['strategy_size']
        
        build = ce_client.create_build(
            project_id=project_id,
            build_name=build_name,
            output_image=output_image,
            output_secret=output_secret,
            source_url=source_url,
            **kwargs
        )
        
        raw_json = json.dumps(build, indent=2, default=str)
        
        return [types.TextContent(
            type="text",
            text=f"**Build configuration {build_name} created successfully!**\n\n```json\n{raw_json}\n```"
        )]
    
    except CodeEngineError as e:
        return [types.TextContent(type="text", text=f"Code Engine API error: {str(e)}")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Unexpected error: {str(e)}")]

async def handle_create_build_run(arguments: dict) -> list[types.TextContent]:
    """Handle create_build_run tool call"""
    try:
        project_id = arguments.get('project_id')
        build_name = arguments.get('build_name')
        
        # Optional parameters
        kwargs = {'build_name': build_name}
        if 'name' in arguments:
            kwargs['name'] = arguments['name']
        
        build_run = ce_client.create_build_run(
            project_id=project_id,
            **kwargs
        )
        
        run_name = build_run.get('name', 'unnamed')
        status = build_run.get('status', 'unknown')
        
        raw_json = json.dumps(build_run, indent=2, default=str)
        
        return [types.TextContent(
            type="text",
            text=f"**Build run {run_name} started!**\n\nStatus: {status}\n\nUse `get_build_run` with name '{run_name}' to check progress.\n\n```json\n{raw_json}\n```"
        )]
    
    except CodeEngineError as e:
        return [types.TextContent(type="text", text=f"Code Engine API error: {str(e)}")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Unexpected error: {str(e)}")]

async def handle_get_build_run(arguments: dict) -> list[types.TextContent]:
    """Handle get_build_run tool call"""
    try:
        project_id = arguments.get('project_id')
        build_run_name = arguments.get('build_run_name')
        
        build_run = ce_client.get_build_run(
            project_id=project_id,
            build_run_name=build_run_name
        )
        
        status = build_run.get('status', 'unknown')
        status_details = build_run.get('status_details', {})
        
        summary = f"**Build Run: {build_run_name}**\n\n"
        summary += f"Status: **{status}**\n"
        
        if status_details:
            if 'completion_time' in status_details:
                summary += f"Completed: {status_details['completion_time']}\n"
            if 'start_time' in status_details:
                summary += f"Started: {status_details['start_time']}\n"
            if 'reason' in status_details:
                summary += f"Reason: {status_details['reason']}\n"
        
        output_image = build_run.get('output_image', 'N/A')
        summary += f"\nOutput Image: {output_image}\n"
        
        raw_json = json.dumps(build_run, indent=2, default=str)
        
        return [types.TextContent(
            type="text",
            text=f"{summary}\n\n**Full Details:**\n```json\n{raw_json}\n```"
        )]
    
    except CodeEngineError as e:
        return [types.TextContent(type="text", text=f"Code Engine API error: {str(e)}")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Unexpected error: {str(e)}")]

async def handle_list_builds(arguments: dict) -> list[types.TextContent]:
    """Handle list_builds tool call"""
    try:
        project_id = arguments.get('project_id')
        limit = arguments.get('limit', 100)
        
        builds = ce_client.list_builds(project_id=project_id, limit=limit)
        
        if not builds:
            formatted_summary = f"No build configurations found in project {project_id}."
        else:
            formatted_summary = f"Found {len(builds)} build configurations in project {project_id}:\n\n"
            for build in builds:
                formatted_summary += f"• **{build.get('name', 'Unknown')}**\n"
                formatted_summary += f"  Output: {build.get('output_image', 'Unknown')}\n"
                formatted_summary += f"  Source: {build.get('source_url', 'Unknown')}\n"
                formatted_summary += f"  Strategy: {build.get('strategy_type', 'Unknown')}\n"
                formatted_summary += f"  Created: {build.get('created_at', 'Unknown')}\n\n"
        
        raw_json = json.dumps(builds, indent=2, default=str)
        
        return [types.TextContent(
            type="text",
            text=f"{formatted_summary}\n\n**Raw JSON Data:**\n```json\n{raw_json}\n```"
        )]
    
    except CodeEngineError as e:
        return [types.TextContent(type="text", text=f"Code Engine API error: {str(e)}")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Unexpected error: {str(e)}")]

async def handle_list_build_runs(arguments: dict) -> list[types.TextContent]:
    """Handle list_build_runs tool call"""
    try:
        project_id = arguments.get('project_id')
        build_name = arguments.get('build_name')
        limit = arguments.get('limit', 100)
        
        build_runs = ce_client.list_build_runs(
            project_id=project_id,
            build_name=build_name,
            limit=limit
        )
        
        context = f" for build '{build_name}'" if build_name else ""
        
        if not build_runs:
            formatted_summary = f"No build runs found{context} in project {project_id}."
        else:
            formatted_summary = f"Found {len(build_runs)} build runs{context} in project {project_id}:\n\n"
            for run in build_runs:
                formatted_summary += f"• **{run.get('name', 'Unknown')}**\n"
                formatted_summary += f"  Status: {run.get('status', 'Unknown')}\n"
                formatted_summary += f"  Build: {run.get('build_name', 'Unknown')}\n"
                formatted_summary += f"  Created: {run.get('created_at', 'Unknown')}\n"
                if run.get('output_image'):
                    formatted_summary += f"  Image: {run.get('output_image')}\n"
                formatted_summary += "\n"
        
        raw_json = json.dumps(build_runs, indent=2, default=str)
        
        return [types.TextContent(
            type="text",
            text=f"{formatted_summary}\n\n**Raw JSON Data:**\n```json\n{raw_json}\n```"
        )]
    
    except CodeEngineError as e:
        return [types.TextContent(type="text", text=f"Code Engine API error: {str(e)}")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Unexpected error: {str(e)}")]

async def handle_find_project_by_name(arguments: dict) -> list[types.TextContent]:
    """Handle find_project_by_name tool call"""
    try:
        project_name = arguments.get('project_name')
        resource_group_id = arguments.get('resource_group_id')

        logger.info(f"Finding project: {project_name}")
        if resource_group_id:
            logger.info(f"Filtering by resource group: {resource_group_id}")

        project = ce_client.find_project_by_name(
            project_name=project_name,
            resource_group_id=resource_group_id
        )

        if not project:
            rg_context = f" in resource group {resource_group_id}" if resource_group_id else ""
            return [types.TextContent(
                type="text",
                text=f"Project '{project_name}' not found{rg_context}."
            )]

        # Format project details
        formatted_summary = f"**Found Project: {project.get('name')}**\n\n"
        formatted_summary += f"• **ID:** {project.get('id')}\n"
        formatted_summary += f"• **Region:** {project.get('region', 'Unknown')}\n"
        formatted_summary += f"• **Status:** {project.get('status', 'Unknown')}\n"
        formatted_summary += f"• **Resource Group ID:** {project.get('resource_group_id', 'Unknown')}\n"
        formatted_summary += f"• **Created:** {project.get('created_at', 'Unknown')}\n"

        raw_json = json.dumps(project, indent=2, default=str)

        return [types.TextContent(
            type="text",
            text=f"{formatted_summary}\n\n**Raw JSON Data:**\n```json\n{raw_json}\n```"
        )]

    except CodeEngineError as e:
        return [types.TextContent(type="text", text=f"Code Engine API error: {str(e)}")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Unexpected error: {str(e)}")]

async def handle_create_app_from_source(arguments: dict) -> list[types.TextContent]:
    """Handle create_app_from_source tool call"""
    try:
        project_id = arguments.get('project_id')
        app_name = arguments.get('app_name')
        source_path = arguments.get('source_path', '.')
        port = arguments.get('port', 8080)
        image_name = arguments.get('image_name')
        min_scale = arguments.get('min_scale', 1)
        max_scale = arguments.get('max_scale', 10)
        cpu_limit = arguments.get('cpu_limit', '0.5')
        memory_limit = arguments.get('memory_limit', '4G')

        logger.info(f"Creating app '{app_name}' from source: {source_path}")

        app = ce_client.create_app_from_source(
            project_id=project_id,
            app_name=app_name,
            source_path=source_path,
            port=port,
            image_name=image_name,
            min_scale=min_scale,
            max_scale=max_scale,
            cpu_limit=cpu_limit,
            memory_limit=memory_limit
        )

        # Format application details
        formatted_summary = f"**✅ Application '{app_name}' created successfully!**\n\n"
        formatted_summary += f"• **Name:** {app.get('name')}\n"
        formatted_summary += f"• **Project ID:** {project_id}\n"
        formatted_summary += f"• **Status:** {app.get('status', 'Building')}\n"

        if app.get('endpoint'):
            formatted_summary += f"• **🌐 Endpoint:** {app.get('endpoint')}\n"
        else:
            formatted_summary += f"• **Status:** Build in progress, endpoint will be available once deployment completes\n"

        formatted_summary += f"• **Port:** {port}\n"
        formatted_summary += f"• **Scale:** {min_scale}-{max_scale} instances\n"
        formatted_summary += f"• **Resources:** {cpu_limit} CPU, {memory_limit} memory\n"

        if image_name:
            formatted_summary += f"• **Image:** {image_name}\n"

        formatted_summary += f"\n**Note:** Code Engine is packaging source from '{source_path}', "
        formatted_summary += "building the Docker image, and deploying the application. "
        formatted_summary += "This may take a few minutes. Use `get_application` to check deployment status.\n"

        raw_json = json.dumps(app, indent=2, default=str)

        return [types.TextContent(
            type="text",
            text=f"{formatted_summary}\n\n**Raw JSON Data:**\n```json\n{raw_json}\n```"
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