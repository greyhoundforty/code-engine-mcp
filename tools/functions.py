"""Function management tools (6): list, get, create, update, delete, list_runtimes."""

import json

import mcp.types as types

from tools.base import ToolDefinition
from tools.registry import register
from utils import (
    CodeEngineClient,
    CodeEngineError,
    format_functions_summary,
)

_PROJECT_ID = {"type": "string", "description": "Code Engine project ID"}
_NAME = {"type": "string", "description": "Function name"}
_LIMIT = {
    "type": "integer",
    "description": "Maximum number to return (default: 100)",
    "default": 100,
    "minimum": 1,
    "maximum": 200,
}
_ENV_VARS = {
    "type": "array",
    "description": "Environment variables as a list of {name, value} objects",
    "items": {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "value": {"type": "string"},
        },
        "required": ["name"],
    },
}

# ---------------------------------------------------------------------------
# list_functions
# ---------------------------------------------------------------------------


async def _list_functions(client: CodeEngineClient, args: dict) -> list[types.TextContent]:
    try:
        functions = client.list_functions(project_id=args["project_id"], limit=args.get("limit", 100))
        summary = format_functions_summary(functions, project_id=args["project_id"])
        raw = json.dumps(functions, indent=2, default=str)
        return [types.TextContent(
            type="text",
            text=f"{summary}\n\n**Raw JSON Data:**\n```json\n{raw}\n```",
        )]
    except CodeEngineError as e:
        return [types.TextContent(type="text", text=f"Code Engine API error: {e}")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Unexpected error: {e}")]


register(ToolDefinition(
    name="list_functions",
    description="List serverless functions in a Code Engine project",
    input_schema={
        "type": "object",
        "properties": {"project_id": _PROJECT_ID, "limit": _LIMIT},
        "required": ["project_id"],
        "additionalProperties": False,
    },
    handler=_list_functions,
))

# ---------------------------------------------------------------------------
# get_function
# ---------------------------------------------------------------------------


async def _get_function(client: CodeEngineClient, args: dict) -> list[types.TextContent]:
    try:
        fn = client.get_function(project_id=args["project_id"], name=args["name"])
        raw = json.dumps(fn, indent=2, default=str)
        return [types.TextContent(
            type="text",
            text=f"**Function '{args['name']}':**\n```json\n{raw}\n```",
        )]
    except CodeEngineError as e:
        return [types.TextContent(type="text", text=f"Code Engine API error: {e}")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Unexpected error: {e}")]


register(ToolDefinition(
    name="get_function",
    description="Get details of a specific serverless function",
    input_schema={
        "type": "object",
        "properties": {"project_id": _PROJECT_ID, "name": _NAME},
        "required": ["project_id", "name"],
        "additionalProperties": False,
    },
    handler=_get_function,
))

# ---------------------------------------------------------------------------
# create_function
# ---------------------------------------------------------------------------


async def _create_function(client: CodeEngineClient, args: dict) -> list[types.TextContent]:
    try:
        kwargs = {}
        for opt_key in ("scale_cpu_limit", "scale_memory_limit", "scale_max_execution_time",
                        "scale_down_delay", "managed_domain_mappings", "run_env_variables"):
            if opt_key in args:
                kwargs[opt_key] = args[opt_key]
        fn = client.create_function(
            project_id=args["project_id"],
            name=args["name"],
            code_reference=args["code_reference"],
            runtime=args["runtime"],
            **kwargs,
        )
        raw = json.dumps(fn, indent=2, default=str)
        return [types.TextContent(
            type="text",
            text=f"**Created function '{args['name']}':**\n```json\n{raw}\n```",
        )]
    except CodeEngineError as e:
        return [types.TextContent(type="text", text=f"Code Engine API error: {e}")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Unexpected error: {e}")]


register(ToolDefinition(
    name="create_function",
    description=(
        "Create a serverless function in a Code Engine project. "
        "Use list_function_runtimes to see available runtime values."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "project_id": _PROJECT_ID,
            "name": _NAME,
            "code_reference": {
                "type": "string",
                "description": (
                    "Reference to the function code. Either a container registry image "
                    "reference (e.g. 'icr.io/namespace/image:tag') or an inline code bundle "
                    "in data-URL format."
                ),
            },
            "runtime": {
                "type": "string",
                "description": (
                    "Managed runtime identifier. Examples: 'nodejs-20', 'nodejs-22', "
                    "'nodejs-24', 'python-3.11', 'python-3.13'. "
                    "Use list_function_runtimes for the full list."
                ),
            },
            "scale_cpu_limit": {
                "type": "string",
                "description": "CPU limit (e.g. '0.25', '0.5', '1'). Default: '0.25'",
            },
            "scale_memory_limit": {
                "type": "string",
                "description": "Memory limit (e.g. '256M', '512M', '1G'). Default: '1G'",
            },
            "scale_max_execution_time": {
                "type": "integer",
                "description": "Maximum execution time in seconds (max 120). Default: 60",
            },
            "managed_domain_mappings": {
                "type": "string",
                "description": "Visibility of the auto-generated endpoint: 'local', 'local_public', or 'local_private'",
                "enum": ["local", "local_public", "local_private"],
            },
            "run_env_variables": _ENV_VARS,
        },
        "required": ["project_id", "name", "code_reference", "runtime"],
        "additionalProperties": False,
    },
    handler=_create_function,
))

# ---------------------------------------------------------------------------
# update_function
# ---------------------------------------------------------------------------


async def _update_function(client: CodeEngineClient, args: dict) -> list[types.TextContent]:
    try:
        kwargs = {}
        for opt_key in ("runtime", "code_reference", "scale_cpu_limit", "scale_memory_limit",
                        "scale_max_execution_time", "scale_down_delay", "managed_domain_mappings",
                        "run_env_variables"):
            if opt_key in args:
                kwargs[opt_key] = args[opt_key]
        fn = client.update_function(
            project_id=args["project_id"],
            name=args["name"],
            **kwargs,
        )
        raw = json.dumps(fn, indent=2, default=str)
        return [types.TextContent(
            type="text",
            text=f"**Updated function '{args['name']}':**\n```json\n{raw}\n```",
        )]
    except CodeEngineError as e:
        return [types.TextContent(type="text", text=f"Code Engine API error: {e}")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Unexpected error: {e}")]


register(ToolDefinition(
    name="update_function",
    description="Update configuration of an existing serverless function",
    input_schema={
        "type": "object",
        "properties": {
            "project_id": _PROJECT_ID,
            "name": _NAME,
            "runtime": {"type": "string", "description": "New runtime identifier"},
            "code_reference": {"type": "string", "description": "New code reference"},
            "scale_cpu_limit": {"type": "string", "description": "CPU limit (e.g. '0.5')"},
            "scale_memory_limit": {"type": "string", "description": "Memory limit (e.g. '512M')"},
            "scale_max_execution_time": {"type": "integer", "description": "Max execution seconds"},
            "managed_domain_mappings": {
                "type": "string",
                "enum": ["local", "local_public", "local_private"],
            },
            "run_env_variables": _ENV_VARS,
        },
        "required": ["project_id", "name"],
        "additionalProperties": False,
    },
    handler=_update_function,
))

# ---------------------------------------------------------------------------
# delete_function
# ---------------------------------------------------------------------------


async def _delete_function(client: CodeEngineClient, args: dict) -> list[types.TextContent]:
    try:
        client.delete_function(project_id=args["project_id"], name=args["name"])
        return [types.TextContent(
            type="text",
            text=f"Function '{args['name']}' deleted from project {args['project_id']}.",
        )]
    except CodeEngineError as e:
        return [types.TextContent(type="text", text=f"Code Engine API error: {e}")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Unexpected error: {e}")]


register(ToolDefinition(
    name="delete_function",
    description="Delete a serverless function from a Code Engine project",
    input_schema={
        "type": "object",
        "properties": {"project_id": _PROJECT_ID, "name": _NAME},
        "required": ["project_id", "name"],
        "additionalProperties": False,
    },
    handler=_delete_function,
))

# ---------------------------------------------------------------------------
# list_function_runtimes
# ---------------------------------------------------------------------------


async def _list_function_runtimes(client: CodeEngineClient, args: dict) -> list[types.TextContent]:
    try:
        runtimes = client.list_function_runtimes()
        raw = json.dumps(runtimes, indent=2, default=str)
        if not runtimes:
            return [types.TextContent(type="text", text="No function runtimes found.")]
        names = [r.get("name", r.get("id", "unknown")) for r in runtimes]
        summary = f"Available function runtimes ({len(runtimes)}):\n" + "\n".join(f"• {n}" for n in names)
        return [types.TextContent(
            type="text",
            text=f"{summary}\n\n**Raw JSON Data:**\n```json\n{raw}\n```",
        )]
    except CodeEngineError as e:
        return [types.TextContent(type="text", text=f"Code Engine API error: {e}")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Unexpected error: {e}")]


register(ToolDefinition(
    name="list_function_runtimes",
    description=(
        "List available managed runtimes for Code Engine functions "
        "(e.g. nodejs-20, nodejs-22, nodejs-24, python-3.11, python-3.13)"
    ),
    input_schema={
        "type": "object",
        "properties": {},
        "additionalProperties": False,
    },
    handler=_list_function_runtimes,
))
