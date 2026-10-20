"""Project management tools: list_projects, find_project_by_name."""

import json
import logging

import mcp.types as types

from tools.base import ToolDefinition
from tools.registry import register
from utils import CodeEngineClient, CodeEngineError, format_project_summary

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# list_projects
# ---------------------------------------------------------------------------

_LIST_PROJECTS_SCHEMA = {
    "type": "object",
    "properties": {
        "limit": {
            "type": "integer",
            "description": "Maximum number of projects to return (default: 100)",
            "default": 100,
            "minimum": 1,
            "maximum": 200,
        }
    },
    "additionalProperties": False,
}


async def _list_projects(client: CodeEngineClient, args: dict) -> list[types.TextContent]:
    try:
        projects = client.list_projects(limit=args.get("limit", 100))
        summary = format_project_summary(projects)
        raw = json.dumps(projects, indent=2, default=str)
        return [types.TextContent(type="text", text=f"{summary}\n\n**Raw JSON Data:**\n```json\n{raw}\n```")]
    except CodeEngineError as e:
        return [types.TextContent(type="text", text=f"Code Engine API error: {e}")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Unexpected error: {e}")]


register(ToolDefinition(
    name="list_projects",
    description="List all IBM Code Engine projects in your account",
    input_schema=_LIST_PROJECTS_SCHEMA,
    handler=_list_projects,
))

# ---------------------------------------------------------------------------
# find_project_by_name
# ---------------------------------------------------------------------------

_FIND_PROJECT_SCHEMA = {
    "type": "object",
    "properties": {
        "project_name": {
            "type": "string",
            "description": "Name of the project to find",
        },
        "resource_group_id": {
            "type": "string",
            "description": "Optional resource group ID to filter search",
        },
    },
    "required": ["project_name"],
    "additionalProperties": False,
}


async def _find_project_by_name(client: CodeEngineClient, args: dict) -> list[types.TextContent]:
    try:
        project_name = args.get("project_name")
        resource_group_id = args.get("resource_group_id")

        logger.info(f"Finding project: {project_name}")
        if resource_group_id:
            logger.info(f"Filtering by resource group: {resource_group_id}")

        project = client.find_project_by_name(
            project_name=project_name,
            resource_group_id=resource_group_id,
        )

        if not project:
            rg_context = f" in resource group {resource_group_id}" if resource_group_id else ""
            return [types.TextContent(type="text", text=f"Project '{project_name}' not found{rg_context}.")]

        summary = f"**Found Project: {project.get('name')}**\n\n"
        summary += f"• **ID:** {project.get('id')}\n"
        summary += f"• **Region:** {project.get('region', 'Unknown')}\n"
        summary += f"• **Status:** {project.get('status', 'Unknown')}\n"
        summary += f"• **Resource Group ID:** {project.get('resource_group_id', 'Unknown')}\n"
        summary += f"• **Created:** {project.get('created_at', 'Unknown')}\n"

        raw = json.dumps(project, indent=2, default=str)
        return [types.TextContent(type="text", text=f"{summary}\n\n**Raw JSON Data:**\n```json\n{raw}\n```")]

    except CodeEngineError as e:
        return [types.TextContent(type="text", text=f"Code Engine API error: {e}")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Unexpected error: {e}")]


register(ToolDefinition(
    name="find_project_by_name",
    description="Find a Code Engine project by name, optionally filtered by resource group",
    input_schema=_FIND_PROJECT_SCHEMA,
    handler=_find_project_by_name,
))
