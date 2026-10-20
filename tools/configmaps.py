"""Configmap management tools (5): list, get, create, update, delete."""

import json

import mcp.types as types

from tools.base import ToolDefinition
from tools.registry import register
from utils import (
    CodeEngineClient,
    CodeEngineError,
    format_config_maps_summary,
)

_PROJECT_ID = {"type": "string", "description": "Code Engine project ID"}
_NAME = {"type": "string", "description": "Name of the configmap"}
_LIMIT = {
    "type": "integer",
    "description": "Maximum number to return (default: 100)",
    "default": 100,
    "minimum": 1,
    "maximum": 200,
}
_DATA = {
    "type": "object",
    "description": "Key-value pairs to store in the configmap (string values only)",
    "additionalProperties": {"type": "string"},
}

# ---------------------------------------------------------------------------
# list_config_maps
# ---------------------------------------------------------------------------


async def _list_config_maps(client: CodeEngineClient, args: dict) -> list[types.TextContent]:
    try:
        cms = client.list_config_maps(project_id=args["project_id"], limit=args.get("limit", 100))
        summary = format_config_maps_summary(cms, project_id=args["project_id"])
        raw = json.dumps(cms, indent=2, default=str)
        return [types.TextContent(
            type="text",
            text=f"{summary}\n\n**Raw JSON Data:**\n```json\n{raw}\n```",
        )]
    except CodeEngineError as e:
        return [types.TextContent(type="text", text=f"Code Engine API error: {e}")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Unexpected error: {e}")]


register(ToolDefinition(
    name="list_config_maps",
    description="List configmaps in a Code Engine project",
    input_schema={
        "type": "object",
        "properties": {"project_id": _PROJECT_ID, "limit": _LIMIT},
        "required": ["project_id"],
        "additionalProperties": False,
    },
    handler=_list_config_maps,
))

# ---------------------------------------------------------------------------
# get_config_map
# ---------------------------------------------------------------------------


async def _get_config_map(client: CodeEngineClient, args: dict) -> list[types.TextContent]:
    try:
        cm = client.get_config_map(project_id=args["project_id"], name=args["name"])
        raw = json.dumps(cm, indent=2, default=str)
        return [types.TextContent(
            type="text",
            text=f"**Configmap '{args['name']}':**\n```json\n{raw}\n```",
        )]
    except CodeEngineError as e:
        return [types.TextContent(type="text", text=f"Code Engine API error: {e}")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Unexpected error: {e}")]


register(ToolDefinition(
    name="get_config_map",
    description="Get details of a specific configmap",
    input_schema={
        "type": "object",
        "properties": {"project_id": _PROJECT_ID, "name": _NAME},
        "required": ["project_id", "name"],
        "additionalProperties": False,
    },
    handler=_get_config_map,
))

# ---------------------------------------------------------------------------
# create_config_map
# ---------------------------------------------------------------------------


async def _create_config_map(client: CodeEngineClient, args: dict) -> list[types.TextContent]:
    try:
        cm = client.create_config_map(
            project_id=args["project_id"],
            name=args["name"],
            data=args.get("data"),
        )
        raw = json.dumps(cm, indent=2, default=str)
        return [types.TextContent(
            type="text",
            text=f"**Created configmap '{args['name']}':**\n```json\n{raw}\n```",
        )]
    except CodeEngineError as e:
        return [types.TextContent(type="text", text=f"Code Engine API error: {e}")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Unexpected error: {e}")]


register(ToolDefinition(
    name="create_config_map",
    description="Create a configmap in a Code Engine project",
    input_schema={
        "type": "object",
        "properties": {
            "project_id": _PROJECT_ID,
            "name": _NAME,
            "data": _DATA,
        },
        "required": ["project_id", "name"],
        "additionalProperties": False,
    },
    handler=_create_config_map,
))

# ---------------------------------------------------------------------------
# update_config_map  (replace — full replacement of all key-value pairs)
# ---------------------------------------------------------------------------


async def _update_config_map(client: CodeEngineClient, args: dict) -> list[types.TextContent]:
    try:
        cm = client.replace_config_map(
            project_id=args["project_id"],
            name=args["name"],
            data=args.get("data"),
        )
        raw = json.dumps(cm, indent=2, default=str)
        return [types.TextContent(
            type="text",
            text=f"**Updated configmap '{args['name']}':**\n```json\n{raw}\n```",
        )]
    except CodeEngineError as e:
        return [types.TextContent(type="text", text=f"Code Engine API error: {e}")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Unexpected error: {e}")]


register(ToolDefinition(
    name="update_config_map",
    description=(
        "Replace all key-value pairs in a configmap (full replacement). "
        "Any keys not included in `data` will be removed."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "project_id": _PROJECT_ID,
            "name": _NAME,
            "data": _DATA,
        },
        "required": ["project_id", "name"],
        "additionalProperties": False,
    },
    handler=_update_config_map,
))

# ---------------------------------------------------------------------------
# delete_config_map
# ---------------------------------------------------------------------------


async def _delete_config_map(client: CodeEngineClient, args: dict) -> list[types.TextContent]:
    try:
        client.delete_config_map(project_id=args["project_id"], name=args["name"])
        return [types.TextContent(
            type="text",
            text=f"Configmap '{args['name']}' deleted from project {args['project_id']}.",
        )]
    except CodeEngineError as e:
        return [types.TextContent(type="text", text=f"Code Engine API error: {e}")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Unexpected error: {e}")]


register(ToolDefinition(
    name="delete_config_map",
    description="Delete a configmap from a Code Engine project",
    input_schema={
        "type": "object",
        "properties": {"project_id": _PROJECT_ID, "name": _NAME},
        "required": ["project_id", "name"],
        "additionalProperties": False,
    },
    handler=_delete_config_map,
))
