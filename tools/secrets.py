"""Secret management tools (2): list_secrets, get_secret."""

import json

import mcp.types as types

from tools.base import ToolDefinition
from tools.registry import register
from utils import CodeEngineClient, CodeEngineError, format_secrets_summary, mask_sensitive_data

_PROJECT_ID = {"type": "string", "description": "Code Engine project ID"}
_LIMIT = {"type": "integer", "description": "Maximum number to return (default: 100)", "default": 100, "minimum": 1, "maximum": 200}

# ---------------------------------------------------------------------------
# list_secrets
# ---------------------------------------------------------------------------

async def _list_secrets(client: CodeEngineClient, args: dict) -> list[types.TextContent]:
    try:
        secrets = client.list_secrets(project_id=args["project_id"], limit=args.get("limit", 100))
        masked = [mask_sensitive_data(s) for s in secrets]
        summary = format_secrets_summary(masked, project_id=args["project_id"])
        raw = json.dumps(masked, indent=2, default=str)
        return [types.TextContent(
            type="text",
            text=f"{summary}\n\n**Raw JSON Data (sensitive data masked):**\n```json\n{raw}\n```",
        )]
    except CodeEngineError as e:
        return [types.TextContent(type="text", text=f"Code Engine API error: {e}")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Unexpected error: {e}")]


register(ToolDefinition(
    name="list_secrets",
    description="List secrets in a specific Code Engine project (sensitive data masked)",
    input_schema={
        "type": "object",
        "properties": {"project_id": _PROJECT_ID, "limit": _LIMIT},
        "required": ["project_id"],
        "additionalProperties": False,
    },
    handler=_list_secrets,
))

# ---------------------------------------------------------------------------
# get_secret
# ---------------------------------------------------------------------------

async def _get_secret(client: CodeEngineClient, args: dict) -> list[types.TextContent]:
    try:
        secret = client.get_secret(project_id=args["project_id"], secret_name=args["secret_name"])
        masked = mask_sensitive_data(secret)
        raw = json.dumps(masked, indent=2, default=str)
        return [types.TextContent(
            type="text",
            text=f"**Secret Details for {args['secret_name']} (sensitive data masked):**\n```json\n{raw}\n```",
        )]
    except CodeEngineError as e:
        return [types.TextContent(type="text", text=f"Code Engine API error: {e}")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Unexpected error: {e}")]


register(ToolDefinition(
    name="get_secret",
    description="Get detailed information about a specific secret (sensitive data masked)",
    input_schema={
        "type": "object",
        "properties": {
            "project_id": _PROJECT_ID,
            "secret_name": {"type": "string", "description": "Name of the secret"},
        },
        "required": ["project_id", "secret_name"],
        "additionalProperties": False,
    },
    handler=_get_secret,
))
