"""Service binding tools (4): list, get, create, delete."""

import json

import mcp.types as types

from tools.base import ToolDefinition
from tools.registry import register
from utils import (
    CodeEngineClient,
    CodeEngineError,
    format_bindings_summary,
)

_PROJECT_ID = {"type": "string", "description": "Code Engine project ID"}
_LIMIT = {
    "type": "integer",
    "description": "Maximum number to return (default: 100)",
    "default": 100,
    "minimum": 1,
    "maximum": 200,
}

# ---------------------------------------------------------------------------
# list_bindings
# ---------------------------------------------------------------------------


async def _list_bindings(client: CodeEngineClient, args: dict) -> list[types.TextContent]:
    try:
        bindings = client.list_bindings(project_id=args["project_id"], limit=args.get("limit", 100))
        summary = format_bindings_summary(bindings, project_id=args["project_id"])
        raw = json.dumps(bindings, indent=2, default=str)
        return [types.TextContent(
            type="text",
            text=f"{summary}\n\n**Raw JSON Data:**\n```json\n{raw}\n```",
        )]
    except CodeEngineError as e:
        return [types.TextContent(type="text", text=f"Code Engine API error: {e}")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Unexpected error: {e}")]


register(ToolDefinition(
    name="list_bindings",
    description="List service bindings in a Code Engine project",
    input_schema={
        "type": "object",
        "properties": {"project_id": _PROJECT_ID, "limit": _LIMIT},
        "required": ["project_id"],
        "additionalProperties": False,
    },
    handler=_list_bindings,
))

# ---------------------------------------------------------------------------
# get_binding
# ---------------------------------------------------------------------------


async def _get_binding(client: CodeEngineClient, args: dict) -> list[types.TextContent]:
    try:
        binding = client.get_binding(project_id=args["project_id"], binding_id=args["binding_id"])
        raw = json.dumps(binding, indent=2, default=str)
        return [types.TextContent(
            type="text",
            text=f"**Service Binding '{args['binding_id']}':**\n```json\n{raw}\n```",
        )]
    except CodeEngineError as e:
        return [types.TextContent(type="text", text=f"Code Engine API error: {e}")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Unexpected error: {e}")]


register(ToolDefinition(
    name="get_binding",
    description="Get details of a specific service binding",
    input_schema={
        "type": "object",
        "properties": {
            "project_id": _PROJECT_ID,
            "binding_id": {"type": "string", "description": "Service binding ID"},
        },
        "required": ["project_id", "binding_id"],
        "additionalProperties": False,
    },
    handler=_get_binding,
))

# ---------------------------------------------------------------------------
# create_binding
# ---------------------------------------------------------------------------


async def _create_binding(client: CodeEngineClient, args: dict) -> list[types.TextContent]:
    try:
        binding = client.create_binding(
            project_id=args["project_id"],
            component_name=args["component_name"],
            component_resource_type=args["component_resource_type"],
            prefix=args["prefix"],
            secret_name=args["secret_name"],
        )
        raw = json.dumps(binding, indent=2, default=str)
        return [types.TextContent(
            type="text",
            text=(
                f"**Created service binding for '{args['component_name']}':**\n"
                f"```json\n{raw}\n```"
            ),
        )]
    except CodeEngineError as e:
        return [types.TextContent(type="text", text=f"Code Engine API error: {e}")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Unexpected error: {e}")]


register(ToolDefinition(
    name="create_binding",
    description=(
        "Bind an IBM Cloud service instance to a Code Engine app, job, or function. "
        "The service credentials are exposed as environment variables prefixed with `prefix`. "
        "Requires a service credential secret already created in the project."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "project_id": _PROJECT_ID,
            "component_name": {
                "type": "string",
                "description": "Name of the app, job, or function to bind the service to",
            },
            "component_resource_type": {
                "type": "string",
                "description": "Resource type of the component",
                "enum": ["app_v2", "job_v2", "function_v2"],
            },
            "prefix": {
                "type": "string",
                "description": (
                    "Prefix for environment variables injected by this binding "
                    "(e.g. 'COS' makes variables like COS_APIKEY, COS_URL)"
                ),
            },
            "secret_name": {
                "type": "string",
                "description": (
                    "Name of the existing service credential secret in the project "
                    "(created via the IBM Cloud console or CLI)"
                ),
            },
        },
        "required": ["project_id", "component_name", "component_resource_type", "prefix", "secret_name"],
        "additionalProperties": False,
    },
    handler=_create_binding,
))

# ---------------------------------------------------------------------------
# delete_binding
# ---------------------------------------------------------------------------


async def _delete_binding(client: CodeEngineClient, args: dict) -> list[types.TextContent]:
    try:
        client.delete_binding(project_id=args["project_id"], binding_id=args["binding_id"])
        return [types.TextContent(
            type="text",
            text=f"Service binding '{args['binding_id']}' deleted from project {args['project_id']}.",
        )]
    except CodeEngineError as e:
        return [types.TextContent(type="text", text=f"Code Engine API error: {e}")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Unexpected error: {e}")]


register(ToolDefinition(
    name="delete_binding",
    description="Delete a service binding from a Code Engine project",
    input_schema={
        "type": "object",
        "properties": {
            "project_id": _PROJECT_ID,
            "binding_id": {"type": "string", "description": "Service binding ID"},
        },
        "required": ["project_id", "binding_id"],
        "additionalProperties": False,
    },
    handler=_delete_binding,
))
