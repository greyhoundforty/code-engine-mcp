"""Job management tools (4): list_jobs, get_job, list_job_runs, get_job_run."""

import json

import mcp.types as types

from tools.base import ToolDefinition
from tools.registry import register
from utils import CodeEngineClient, CodeEngineError, format_jobs_summary, format_job_runs_summary

_PROJECT_ID = {"type": "string", "description": "Code Engine project ID"}
_LIMIT = {"type": "integer", "description": "Maximum number to return (default: 100)", "default": 100, "minimum": 1, "maximum": 200}

# ---------------------------------------------------------------------------
# list_jobs
# ---------------------------------------------------------------------------

async def _list_jobs(client: CodeEngineClient, args: dict) -> list[types.TextContent]:
    try:
        jobs = client.list_jobs(project_id=args["project_id"], limit=args.get("limit", 100))
        summary = format_jobs_summary(jobs)
        raw = json.dumps(jobs, indent=2, default=str)
        return [types.TextContent(type="text", text=f"{summary}\n\n**Raw JSON Data:**\n```json\n{raw}\n```")]
    except CodeEngineError as e:
        return [types.TextContent(type="text", text=f"Code Engine API error: {e}")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Unexpected error: {e}")]


register(ToolDefinition(
    name="list_jobs",
    description="List batch jobs in a specific Code Engine project",
    input_schema={
        "type": "object",
        "properties": {"project_id": _PROJECT_ID, "limit": _LIMIT},
        "required": ["project_id"],
        "additionalProperties": False,
    },
    handler=_list_jobs,
))

# ---------------------------------------------------------------------------
# get_job
# ---------------------------------------------------------------------------

async def _get_job(client: CodeEngineClient, args: dict) -> list[types.TextContent]:
    try:
        job = client.get_job(project_id=args["project_id"], job_name=args["job_name"])
        raw = json.dumps(job, indent=2, default=str)
        return [types.TextContent(type="text", text=f"**Job Details for {args['job_name']}:**\n```json\n{raw}\n```")]
    except CodeEngineError as e:
        return [types.TextContent(type="text", text=f"Code Engine API error: {e}")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Unexpected error: {e}")]


register(ToolDefinition(
    name="get_job",
    description="Get detailed information about a specific batch job",
    input_schema={
        "type": "object",
        "properties": {
            "project_id": _PROJECT_ID,
            "job_name": {"type": "string", "description": "Name of the job"},
        },
        "required": ["project_id", "job_name"],
        "additionalProperties": False,
    },
    handler=_get_job,
))

# ---------------------------------------------------------------------------
# list_job_runs
# ---------------------------------------------------------------------------

async def _list_job_runs(client: CodeEngineClient, args: dict) -> list[types.TextContent]:
    try:
        job_runs = client.list_job_runs(
            project_id=args["project_id"],
            job_name=args.get("job_name"),
            limit=args.get("limit", 100),
        )
        summary = format_job_runs_summary(job_runs, job_name=args.get("job_name") or "")
        raw = json.dumps(job_runs, indent=2, default=str)
        return [types.TextContent(type="text", text=f"{summary}\n\n**Raw JSON Data:**\n```json\n{raw}\n```")]
    except CodeEngineError as e:
        return [types.TextContent(type="text", text=f"Code Engine API error: {e}")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Unexpected error: {e}")]


register(ToolDefinition(
    name="list_job_runs",
    description="List job runs for a specific job or all jobs in a project",
    input_schema={
        "type": "object",
        "properties": {
            "project_id": _PROJECT_ID,
            "job_name": {"type": "string", "description": "Optional job name to filter runs (if not provided, lists all job runs)"},
            "limit": _LIMIT,
        },
        "required": ["project_id"],
        "additionalProperties": False,
    },
    handler=_list_job_runs,
))

# ---------------------------------------------------------------------------
# get_job_run
# ---------------------------------------------------------------------------

async def _get_job_run(client: CodeEngineClient, args: dict) -> list[types.TextContent]:
    try:
        job_run = client.get_job_run(project_id=args["project_id"], job_run_name=args["job_run_name"])
        raw = json.dumps(job_run, indent=2, default=str)
        return [types.TextContent(type="text", text=f"**Job Run Details for {args['job_run_name']}:**\n```json\n{raw}\n```")]
    except CodeEngineError as e:
        return [types.TextContent(type="text", text=f"Code Engine API error: {e}")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Unexpected error: {e}")]


register(ToolDefinition(
    name="get_job_run",
    description="Get detailed information about a specific job run",
    input_schema={
        "type": "object",
        "properties": {
            "project_id": _PROJECT_ID,
            "job_run_name": {"type": "string", "description": "Name of the job run"},
        },
        "required": ["project_id", "job_run_name"],
        "additionalProperties": False,
    },
    handler=_get_job_run,
))
