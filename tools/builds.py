"""Build management tools (5): create, list, create_run, get_run, list_runs."""

import json

import mcp.types as types

from tools.base import ToolDefinition
from tools.registry import register
from utils import CodeEngineClient, CodeEngineError, format_builds_summary, format_build_runs_summary

_PROJECT_ID = {"type": "string", "description": "Code Engine project ID"}
_LIMIT = {"type": "integer", "description": "Maximum number to return (default: 100)", "default": 100, "minimum": 1, "maximum": 200}

# ---------------------------------------------------------------------------
# create_build
# ---------------------------------------------------------------------------

async def _create_build(client: CodeEngineClient, args: dict) -> list[types.TextContent]:
    try:
        optional_keys = ["source_revision", "source_context_dir", "strategy_type",
                         "strategy_spec_file", "strategy_size"]
        kwargs = {k: args[k] for k in optional_keys if k in args}
        build = client.create_build(
            project_id=args["project_id"],
            build_name=args["build_name"],
            output_image=args["output_image"],
            output_secret=args["output_secret"],
            source_url=args["source_url"],
            **kwargs,
        )
        raw = json.dumps(build, indent=2, default=str)
        return [types.TextContent(type="text", text=f"**Build configuration {args['build_name']} created successfully!**\n\n```json\n{raw}\n```")]
    except CodeEngineError as e:
        return [types.TextContent(type="text", text=f"Code Engine API error: {e}")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Unexpected error: {e}")]


register(ToolDefinition(
    name="create_build",
    description="Create a new build configuration for building container images from source",
    input_schema={
        "type": "object",
        "properties": {
            "project_id": _PROJECT_ID,
            "build_name": {"type": "string", "description": "Name for the build configuration"},
            "output_image": {"type": "string", "description": "Output container image reference (e.g., 'icr.io/namespace/image:tag')"},
            "output_secret": {"type": "string", "description": "Name of secret for pushing to container registry"},
            "source_url": {"type": "string", "description": "Git repository URL containing source code"},
            "source_revision": {"type": "string", "description": "Git branch, tag, or commit (default: 'main')", "default": "main"},
            "source_context_dir": {"type": "string", "description": "Directory in repo containing source (default: root)"},
            "strategy_type": {"type": "string", "description": "Build strategy: 'dockerfile' or 'buildpacks' (default: 'dockerfile')", "default": "dockerfile"},
            "strategy_spec_file": {"type": "string", "description": "Path to Dockerfile (default: './Dockerfile')", "default": "./Dockerfile"},
            "strategy_size": {"type": "string", "description": "Build resources: 'small', 'medium', 'large', 'xlarge' (default: 'medium')", "default": "medium"},
        },
        "required": ["project_id", "build_name", "output_image", "output_secret", "source_url"],
        "additionalProperties": False,
    },
    handler=_create_build,
))

# ---------------------------------------------------------------------------
# list_builds
# ---------------------------------------------------------------------------

async def _list_builds(client: CodeEngineClient, args: dict) -> list[types.TextContent]:
    try:
        builds = client.list_builds(project_id=args["project_id"], limit=args.get("limit", 100))
        summary = format_builds_summary(builds, project_id=args["project_id"])
        raw = json.dumps(builds, indent=2, default=str)
        return [types.TextContent(type="text", text=f"{summary}\n\n**Raw JSON Data:**\n```json\n{raw}\n```")]
    except CodeEngineError as e:
        return [types.TextContent(type="text", text=f"Code Engine API error: {e}")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Unexpected error: {e}")]


register(ToolDefinition(
    name="list_builds",
    description="List all build configurations in a project",
    input_schema={
        "type": "object",
        "properties": {"project_id": _PROJECT_ID, "limit": _LIMIT},
        "required": ["project_id"],
        "additionalProperties": False,
    },
    handler=_list_builds,
))

# ---------------------------------------------------------------------------
# create_build_run
# ---------------------------------------------------------------------------

async def _create_build_run(client: CodeEngineClient, args: dict) -> list[types.TextContent]:
    try:
        kwargs: dict = {"build_name": args["build_name"]}
        if "name" in args:
            kwargs["name"] = args["name"]
        build_run = client.create_build_run(project_id=args["project_id"], **kwargs)
        run_name = build_run.get("name", "unnamed")
        status = build_run.get("status", "unknown")
        raw = json.dumps(build_run, indent=2, default=str)
        return [types.TextContent(
            type="text",
            text=(
                f"**Build run {run_name} started!**\n\n"
                f"Status: {status}\n\n"
                f"Use `get_build_run` with name '{run_name}' to check progress.\n\n"
                f"```json\n{raw}\n```"
            ),
        )]
    except CodeEngineError as e:
        return [types.TextContent(type="text", text=f"Code Engine API error: {e}")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Unexpected error: {e}")]


register(ToolDefinition(
    name="create_build_run",
    description="Execute a build to create a container image from source code",
    input_schema={
        "type": "object",
        "properties": {
            "project_id": _PROJECT_ID,
            "build_name": {"type": "string", "description": "Name of existing build configuration to execute"},
            "name": {"type": "string", "description": "Optional name for this build run"},
        },
        "required": ["project_id", "build_name"],
        "additionalProperties": False,
    },
    handler=_create_build_run,
))

# ---------------------------------------------------------------------------
# get_build_run
# ---------------------------------------------------------------------------

async def _get_build_run(client: CodeEngineClient, args: dict) -> list[types.TextContent]:
    try:
        build_run = client.get_build_run(project_id=args["project_id"], build_run_name=args["build_run_name"])
        status = build_run.get("status", "unknown")
        status_details = build_run.get("status_details", {})

        summary = f"**Build Run: {args['build_run_name']}**\n\nStatus: **{status}**\n"
        if status_details:
            if "completion_time" in status_details:
                summary += f"Completed: {status_details['completion_time']}\n"
            if "start_time" in status_details:
                summary += f"Started: {status_details['start_time']}\n"
            if "reason" in status_details:
                summary += f"Reason: {status_details['reason']}\n"
        summary += f"\nOutput Image: {build_run.get('output_image', 'N/A')}\n"

        raw = json.dumps(build_run, indent=2, default=str)
        return [types.TextContent(type="text", text=f"{summary}\n\n**Full Details:**\n```json\n{raw}\n```")]
    except CodeEngineError as e:
        return [types.TextContent(type="text", text=f"Code Engine API error: {e}")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Unexpected error: {e}")]


register(ToolDefinition(
    name="get_build_run",
    description="Get the status and details of a build run",
    input_schema={
        "type": "object",
        "properties": {
            "project_id": _PROJECT_ID,
            "build_run_name": {"type": "string", "description": "Name of the build run"},
        },
        "required": ["project_id", "build_run_name"],
        "additionalProperties": False,
    },
    handler=_get_build_run,
))

# ---------------------------------------------------------------------------
# list_build_runs
# ---------------------------------------------------------------------------

async def _list_build_runs(client: CodeEngineClient, args: dict) -> list[types.TextContent]:
    try:
        build_runs = client.list_build_runs(
            project_id=args["project_id"],
            build_name=args.get("build_name"),
            limit=args.get("limit", 100),
        )
        summary = format_build_runs_summary(
            build_runs,
            build_name=args.get("build_name") or "",
            project_id=args["project_id"],
        )
        raw = json.dumps(build_runs, indent=2, default=str)
        return [types.TextContent(type="text", text=f"{summary}\n\n**Raw JSON Data:**\n```json\n{raw}\n```")]
    except CodeEngineError as e:
        return [types.TextContent(type="text", text=f"Code Engine API error: {e}")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Unexpected error: {e}")]


register(ToolDefinition(
    name="list_build_runs",
    description="List build runs in a project, optionally filtered by build name",
    input_schema={
        "type": "object",
        "properties": {
            "project_id": _PROJECT_ID,
            "build_name": {"type": "string", "description": "Optional: filter by build configuration name"},
            "limit": _LIMIT,
        },
        "required": ["project_id"],
        "additionalProperties": False,
    },
    handler=_list_build_runs,
))
