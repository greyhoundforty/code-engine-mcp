"""Application management tools (7): list, get, create, update, revisions, source deploy."""

import json
import logging

import mcp.types as types

from tools.base import ToolDefinition
from tools.registry import register
from utils import (
    CodeEngineClient,
    CodeEngineError,
    format_apps_summary,
    format_app_revisions_summary,
)

logger = logging.getLogger(__name__)

_PROJECT_ID = {"type": "string", "description": "Code Engine project ID"}
_APP_NAME = {"type": "string", "description": "Name of the application"}
_LIMIT = {"type": "integer", "description": "Maximum number to return (default: 100)", "default": 100, "minimum": 1, "maximum": 200}

# ---------------------------------------------------------------------------
# list_applications
# ---------------------------------------------------------------------------

async def _list_applications(client: CodeEngineClient, args: dict) -> list[types.TextContent]:
    try:
        apps = client.list_applications(project_id=args["project_id"], limit=args.get("limit", 100))
        summary = format_apps_summary(apps)
        raw = json.dumps(apps, indent=2, default=str)
        return [types.TextContent(type="text", text=f"{summary}\n\n**Raw JSON Data:**\n```json\n{raw}\n```")]
    except CodeEngineError as e:
        return [types.TextContent(type="text", text=f"Code Engine API error: {e}")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Unexpected error: {e}")]


register(ToolDefinition(
    name="list_applications",
    description="List applications in a specific Code Engine project",
    input_schema={
        "type": "object",
        "properties": {"project_id": _PROJECT_ID, "limit": _LIMIT},
        "required": ["project_id"],
        "additionalProperties": False,
    },
    handler=_list_applications,
))

# ---------------------------------------------------------------------------
# get_application
# ---------------------------------------------------------------------------

async def _get_application(client: CodeEngineClient, args: dict) -> list[types.TextContent]:
    try:
        app = client.get_application(project_id=args["project_id"], app_name=args["app_name"])
        raw = json.dumps(app, indent=2, default=str)
        return [types.TextContent(type="text", text=f"**Application Details for {args['app_name']}:**\n```json\n{raw}\n```")]
    except CodeEngineError as e:
        return [types.TextContent(type="text", text=f"Code Engine API error: {e}")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Unexpected error: {e}")]


register(ToolDefinition(
    name="get_application",
    description="Get detailed information about a specific application",
    input_schema={
        "type": "object",
        "properties": {"project_id": _PROJECT_ID, "app_name": _APP_NAME},
        "required": ["project_id", "app_name"],
        "additionalProperties": False,
    },
    handler=_get_application,
))

# ---------------------------------------------------------------------------
# list_app_revisions
# ---------------------------------------------------------------------------

async def _list_app_revisions(client: CodeEngineClient, args: dict) -> list[types.TextContent]:
    try:
        revisions = client.list_app_revisions(
            project_id=args["project_id"],
            app_name=args["app_name"],
            limit=args.get("limit", 100),
        )
        summary = format_app_revisions_summary(revisions, app_name=args["app_name"], project_id=args["project_id"])
        raw = json.dumps(revisions, indent=2, default=str)
        return [types.TextContent(type="text", text=f"{summary}\n\n**Raw JSON Data:**\n```json\n{raw}\n```")]
    except CodeEngineError as e:
        return [types.TextContent(type="text", text=f"Code Engine API error: {e}")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Unexpected error: {e}")]


register(ToolDefinition(
    name="list_app_revisions",
    description="List revisions for a specific application",
    input_schema={
        "type": "object",
        "properties": {"project_id": _PROJECT_ID, "app_name": _APP_NAME, "limit": _LIMIT},
        "required": ["project_id", "app_name"],
        "additionalProperties": False,
    },
    handler=_list_app_revisions,
))

# ---------------------------------------------------------------------------
# get_app_revision
# ---------------------------------------------------------------------------

async def _get_app_revision(client: CodeEngineClient, args: dict) -> list[types.TextContent]:
    try:
        revision = client.get_app_revision(
            project_id=args["project_id"],
            app_name=args["app_name"],
            revision_name=args["revision_name"],
        )
        raw = json.dumps(revision, indent=2, default=str)
        return [types.TextContent(type="text", text=f"**App Revision Details for {args['revision_name']}:**\n```json\n{raw}\n```")]
    except CodeEngineError as e:
        return [types.TextContent(type="text", text=f"Code Engine API error: {e}")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Unexpected error: {e}")]


register(ToolDefinition(
    name="get_app_revision",
    description="Get detailed information about a specific application revision",
    input_schema={
        "type": "object",
        "properties": {
            "project_id": _PROJECT_ID,
            "app_name": _APP_NAME,
            "revision_name": {"type": "string", "description": "Name of the revision"},
        },
        "required": ["project_id", "app_name", "revision_name"],
        "additionalProperties": False,
    },
    handler=_get_app_revision,
))

# ---------------------------------------------------------------------------
# create_application
# ---------------------------------------------------------------------------

async def _create_application(client: CodeEngineClient, args: dict) -> list[types.TextContent]:
    try:
        optional_keys = ["image_port", "scale_min_instances", "scale_max_instances",
                         "scale_cpu_limit", "scale_memory_limit", "managed_domain_mappings"]
        kwargs = {k: args[k] for k in optional_keys if k in args}
        app = client.create_application(
            project_id=args["project_id"],
            app_name=args["app_name"],
            image_reference=args["image_reference"],
            **kwargs,
        )
        raw = json.dumps(app, indent=2, default=str)
        return [types.TextContent(type="text", text=f"**Application {args['app_name']} created successfully!**\n\n```json\n{raw}\n```")]
    except CodeEngineError as e:
        return [types.TextContent(type="text", text=f"Code Engine API error: {e}")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Unexpected error: {e}")]


register(ToolDefinition(
    name="create_application",
    description="Create a new Code Engine application with specified configuration",
    input_schema={
        "type": "object",
        "properties": {
            "project_id": _PROJECT_ID,
            "app_name": {"type": "string", "description": "Name for the new application"},
            "image_reference": {"type": "string", "description": "Container image reference (e.g., 'icr.io/namespace/image:tag')"},
            "image_port": {"type": "integer", "description": "Port the application listens on (default: 8080)", "default": 8080},
            "scale_min_instances": {"type": "integer", "description": "Minimum number of instances (default: 0)", "default": 0},
            "scale_max_instances": {"type": "integer", "description": "Maximum number of instances (default: 10)", "default": 10},
            "scale_cpu_limit": {"type": "string", "description": "CPU limit per instance (e.g., '1', '0.5')", "default": "1"},
            "scale_memory_limit": {"type": "string", "description": "Memory limit per instance (e.g., '4G', '2G')", "default": "4G"},
            "managed_domain_mappings": {"type": "string", "description": "Domain mapping visibility: 'local_public', 'local_private', 'local'", "default": "local_public"},
        },
        "required": ["project_id", "app_name", "image_reference"],
        "additionalProperties": False,
    },
    handler=_create_application,
))

# ---------------------------------------------------------------------------
# update_application
# ---------------------------------------------------------------------------

async def _update_application(client: CodeEngineClient, args: dict) -> list[types.TextContent]:
    try:
        optional_keys = ["image_reference", "scale_min_instances", "scale_max_instances",
                         "scale_cpu_limit", "scale_memory_limit"]
        kwargs = {k: args[k] for k in optional_keys if k in args}
        app = client.update_application(project_id=args["project_id"], app_name=args["app_name"], **kwargs)
        raw = json.dumps(app, indent=2, default=str)
        return [types.TextContent(type="text", text=f"**Application {args['app_name']} updated successfully!**\n\n```json\n{raw}\n```")]
    except CodeEngineError as e:
        return [types.TextContent(type="text", text=f"Code Engine API error: {e}")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Unexpected error: {e}")]


register(ToolDefinition(
    name="update_application",
    description="Update an existing Code Engine application",
    input_schema={
        "type": "object",
        "properties": {
            "project_id": _PROJECT_ID,
            "app_name": {"type": "string", "description": "Name of the application to update"},
            "image_reference": {"type": "string", "description": "New container image reference"},
            "scale_min_instances": {"type": "integer", "description": "Minimum number of instances"},
            "scale_max_instances": {"type": "integer", "description": "Maximum number of instances"},
            "scale_cpu_limit": {"type": "string", "description": "CPU limit per instance"},
            "scale_memory_limit": {"type": "string", "description": "Memory limit per instance"},
        },
        "required": ["project_id", "app_name"],
        "additionalProperties": False,
    },
    handler=_update_application,
))

# ---------------------------------------------------------------------------
# create_app_from_source
# ---------------------------------------------------------------------------

async def _create_app_from_source(client: CodeEngineClient, args: dict) -> list[types.TextContent]:
    try:
        app_name = args["app_name"]
        source_path = args.get("source_path", ".")
        port = args.get("port", 8080)
        min_scale = args.get("min_scale", 1)
        max_scale = args.get("max_scale", 10)
        cpu_limit = args.get("cpu_limit", "0.5")
        memory_limit = args.get("memory_limit", "4G")
        image_name = args.get("image_name")

        logger.info(f"Creating app '{app_name}' from source: {source_path}")

        app = client.create_app_from_source(
            project_id=args["project_id"],
            app_name=app_name,
            source_path=source_path,
            port=port,
            image_name=image_name,
            min_scale=min_scale,
            max_scale=max_scale,
            cpu_limit=cpu_limit,
            memory_limit=memory_limit,
        )

        summary = f"**✅ Application '{app_name}' created successfully!**\n\n"
        summary += f"• **Name:** {app.get('name')}\n"
        summary += f"• **Project ID:** {args['project_id']}\n"
        summary += f"• **Status:** {app.get('status', 'Building')}\n"

        if app.get("endpoint"):
            summary += f"• **🌐 Endpoint:** {app.get('endpoint')}\n"
        else:
            summary += "• **Status:** Build in progress, endpoint will be available once deployment completes\n"

        summary += f"• **Port:** {port}\n"
        summary += f"• **Scale:** {min_scale}-{max_scale} instances\n"
        summary += f"• **Resources:** {cpu_limit} CPU, {memory_limit} memory\n"
        if image_name:
            summary += f"• **Image:** {image_name}\n"
        summary += (
            f"\n**Note:** Code Engine is packaging source from '{source_path}', "
            "building the Docker image, and deploying the application. "
            "This may take a few minutes. Use `get_application` to check deployment status.\n"
        )

        raw = json.dumps(app, indent=2, default=str)
        return [types.TextContent(type="text", text=f"{summary}\n\n**Raw JSON Data:**\n```json\n{raw}\n```")]
    except CodeEngineError as e:
        return [types.TextContent(type="text", text=f"Code Engine API error: {e}")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Unexpected error: {e}")]


register(ToolDefinition(
    name="create_app_from_source",
    description="Deploy application from local source using Code Engine's integrated build-source feature. Packages source, builds Docker image, and deploys automatically.",
    input_schema={
        "type": "object",
        "properties": {
            "project_id": _PROJECT_ID,
            "app_name": {"type": "string", "description": "Name of the application to create"},
            "source_path": {"type": "string", "description": "Path to source code directory (default: '.')", "default": "."},
            "port": {"type": "integer", "description": "Port the application listens on (default: 8080)", "default": 8080, "minimum": 1, "maximum": 65535},
            "image_name": {"type": "string", "description": "Optional custom image name (e.g., 'private.us.icr.io/namespace/image:tag')"},
            "min_scale": {"type": "integer", "description": "Minimum number of instances (default: 1)", "default": 1, "minimum": 0, "maximum": 100},
            "max_scale": {"type": "integer", "description": "Maximum number of instances (default: 10)", "default": 10, "minimum": 1, "maximum": 100},
            "cpu_limit": {"type": "string", "description": "CPU limit per instance (default: '0.5')", "default": "0.5"},
            "memory_limit": {"type": "string", "description": "Memory limit per instance (default: '4G')", "default": "4G"},
        },
        "required": ["project_id", "app_name"],
        "additionalProperties": False,
    },
    handler=_create_app_from_source,
))
