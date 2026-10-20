"""Domain mapping tools (2): list_domain_mappings, get_domain_mapping."""

import json

import mcp.types as types

from tools.base import ToolDefinition
from tools.registry import register
from utils import CodeEngineClient, CodeEngineError, format_domain_mappings_summary

_PROJECT_ID = {"type": "string", "description": "Code Engine project ID"}
_LIMIT = {"type": "integer", "description": "Maximum number to return (default: 100)", "default": 100, "minimum": 1, "maximum": 200}

# ---------------------------------------------------------------------------
# list_domain_mappings
# ---------------------------------------------------------------------------

async def _list_domain_mappings(client: CodeEngineClient, args: dict) -> list[types.TextContent]:
    try:
        mappings = client.list_domain_mappings(project_id=args["project_id"], limit=args.get("limit", 100))
        summary = format_domain_mappings_summary(mappings, project_id=args["project_id"])
        raw = json.dumps(mappings, indent=2, default=str)
        return [types.TextContent(type="text", text=f"{summary}\n\n**Raw JSON Data:**\n```json\n{raw}\n```")]
    except CodeEngineError as e:
        return [types.TextContent(type="text", text=f"Code Engine API error: {e}")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Unexpected error: {e}")]


register(ToolDefinition(
    name="list_domain_mappings",
    description="List domain mappings in a specific Code Engine project",
    input_schema={
        "type": "object",
        "properties": {"project_id": _PROJECT_ID, "limit": _LIMIT},
        "required": ["project_id"],
        "additionalProperties": False,
    },
    handler=_list_domain_mappings,
))

# ---------------------------------------------------------------------------
# get_domain_mapping
# ---------------------------------------------------------------------------

async def _get_domain_mapping(client: CodeEngineClient, args: dict) -> list[types.TextContent]:
    try:
        mapping = client.get_domain_mapping(project_id=args["project_id"], domain_name=args["domain_name"])
        raw = json.dumps(mapping, indent=2, default=str)
        return [types.TextContent(type="text", text=f"**Domain Mapping Details for {args['domain_name']}:**\n```json\n{raw}\n```")]
    except CodeEngineError as e:
        return [types.TextContent(type="text", text=f"Code Engine API error: {e}")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Unexpected error: {e}")]


register(ToolDefinition(
    name="get_domain_mapping",
    description="Get detailed information about a specific domain mapping",
    input_schema={
        "type": "object",
        "properties": {
            "project_id": _PROJECT_ID,
            "domain_name": {"type": "string", "description": "Name of the domain mapping"},
        },
        "required": ["project_id", "domain_name"],
        "additionalProperties": False,
    },
    handler=_get_domain_mapping,
))
