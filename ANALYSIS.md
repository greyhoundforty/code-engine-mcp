# Architecture Analysis: IBM Code Engine MCP Server

> **Scope:** `ce_mcp_server_v3.py`, `utils.py`, `ce_push.py`, `tests/`, `Dockerfile`
> **Focus:** Abstraction levels, design patterns, structural concerns, and improvement opportunities

---

## 1. Executive Summary

The codebase is a functional MCP server exposing 22 IBM Code Engine tools. The implementation is clear, works, and is well-documented. However, several structural patterns create friction as the codebase grows: a monolithic dispatch chain, schema definitions duplicated across the tool-list and handlers, inconsistent response formatting patterns, a global mutable client, and a test suite that targets a deleted file. The sections below detail each concern with concrete evidence and propose targeted structural improvements.

---

## 2. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│  ce_mcp_server_v3.py  (~1480 lines)                             │
│                                                                  │
│  handle_list_tools()     ←── 22 inline Tool() definitions       │
│  handle_call_tool()      ←── 22-branch if/elif chain            │
│  handle_<tool_name>()    ←── one function per tool              │
│                                                                  │
│  Global:  ce_client: Optional[CodeEngineClient]                 │
└─────────────────────────────────────────────────────────────────┘
            │ calls
            ▼
┌─────────────────────────────────────────────────────────────────┐
│  utils.py  (~1178 lines)                                        │
│                                                                  │
│  CodeEngineClient        ←── wraps ibm_code_engine_sdk          │
│  create_code_engine_client()                                     │
│  format_*_summary()      ←── 4 ad-hoc formatter functions       │
│  mask_sensitive_data()                                           │
└─────────────────────────────────────────────────────────────────┘
            │ calls
            ▼
┌─────────────────────────────────────────────────────────────────┐
│  ibm_code_engine_sdk  (third-party)                             │
└─────────────────────────────────────────────────────────────────┘

ce_push.py  ←── standalone CLI; not called by the MCP server
```

---

## 3. Pros and Cons of Current Implementation

| Dimension | Pros | Cons |
|-----------|------|------|
| **Readability** | Each `handle_*` function is self-contained and easy to trace | File is ~1480 lines; finding a specific tool requires scrolling past 700 lines of schema definitions |
| **Correctness** | Consistent try/except around every handler; `CodeEngineError` surfaces cleanly | `handle_call_tool` catches `Exception` broadly at the outer level *and* each inner handler catches it again — double-try pattern creates silent swallowing risk |
| **Abstraction** | `CodeEngineClient` cleanly wraps the SDK; `create_code_engine_client()` centralizes auth | Response formatting is mixed: some tools use `format_*_summary()` helpers in `utils.py`, others inline identical loops directly in the handler |
| **Extensibility** | Adding a new tool requires edits in three places: `handle_list_tools()`, `handle_call_tool()` dispatch, and a new `handle_*()` function | The 22-branch `if/elif` chain in `handle_call_tool()` will grow linearly with each new tool |
| **State management** | Auth is ephemeral (no caching, no token storage) | `ce_client` is a module-level global mutated inside `async main()`, making unit tests fragile and preventing multi-region or multi-tenancy without restart |
| **Security** | `mask_sensitive_data()` is applied explicitly; non-root container; `--env-file` auth | `get_resource_group_id_by_name()` shells out to `ibmcloud` CLI via `subprocess` — a side-channel with no sanitization |
| **Testing** | Tests cover the three core read operations with proper mocking | `tests/test_server.py` imports `ce_mcp_server` (v1) then `ce_mcp_server_v2`, but the actual file is `ce_mcp_server_v3.py` — all tests are **skipped** at runtime |
| **Dependency hygiene** | Pinned versions in `requirements.txt` | Dev tools (`pylint`, `pre-commit`, `detect-secrets`, `pytest`, `isort`) are in the same `requirements.txt` as production dependencies — inflates the Docker image |
| **Build/deploy duality** | `ce_push.py` provides a clean standalone CLI | `ce_push.py` is not integrated with the MCP server (`create_app_from_source` calls the SDK directly, not `ce_push.py`) — two divergent paths for the same operation |
| **Schema definition** | Schemas are explicit and MCP-compliant | Schema constraints (`minimum`, `maximum`, `default`) are defined in `handle_list_tools()` but *not enforced* in the handlers — defaults are re-specified manually in every handler with `.get('limit', 100)` |

---

## 4. Key Structural Issues

### 4.1 Triple-Site Tool Registration

Every new tool requires simultaneous edits in three disconnected locations:

```python
# Site 1: handle_list_tools() — schema definition (~line 109)
types.Tool(name="list_applications", inputSchema={...})

# Site 2: handle_call_tool() — dispatch branch (~line 719)
elif name == "list_applications":
    return await handle_list_applications(arguments)

# Site 3: standalone handler function (~line 796)
async def handle_list_applications(arguments: dict) -> list[types.TextContent]:
    ...
```

A missed edit at any one site produces a tool that is either registered but uncallable, callable but unregistered, or silently routes to the wrong handler.

---

### 4.2 Inconsistent Formatter Pattern

Only 4 of 22 tools use the shared `format_*_summary()` helpers in `utils.py`. The remaining tools inline ad-hoc formatting loops that are structurally identical but not shared:

```python
# utils.py — shared helper (consistent, tested)
def format_apps_summary(apps): ...

# ce_mcp_server_v3.py — handle_list_builds() (~line 1278)
# Identical loop pattern, inlined instead of extracted
for build in builds:
    formatted_summary += f"• **{build.get('name', 'Unknown')}**\n"
    formatted_summary += f"  Output: {build.get('output_image', 'Unknown')}\n"
    ...
```

This means that changes to the display format for builds, build-runs, domain mappings, app revisions, and secrets must be made in the server file rather than in the utilities layer.

---

### 4.3 Global Mutable Client

```python
# Module level — mutable global
ce_client: Optional[CodeEngineClient] = None

async def main():
    global ce_client           # mutated here
    ce_client = create_code_engine_client(...)
```

All 22 handler functions read `ce_client` as a free variable. This pattern:
- Makes isolated unit tests impossible without `patch("ce_mcp_server_v3.ce_client", ...)`
- Prevents instantiating the server in a context where two clients (e.g., two regions) are needed
- Makes the initialization order implicit and hard to enforce

---

### 4.4 Dead Test Suite

```python
# tests/test_server.py line 17
try:
    from ce_mcp_server import server, handle_call_tool      # v1 — deleted
except ImportError:
    try:
        from ce_mcp_server_v2 import server, handle_call_tool  # v2 — deleted
    except ImportError:
        pytest.skip("Server module could not be imported", allow_module_level=True)
```

The current server file is `ce_mcp_server_v3.py`. Both fallback imports fail, causing `pytest.skip()` to fire at module level. Running `pytest` produces no failures (which looks like a pass) but executes zero assertions.

---

### 4.5 Requirements Bloat

The single `requirements.txt` ships production and dev dependencies together into the Docker image:

```
# Production (needed at runtime)
mcp==1.9.4
ibm-code-engine-sdk==4.20.0
ibm-cloud-sdk-core==3.24.2
pydantic==2.11.5

# Dev-only (never needed at runtime)
pylint==3.3.7
pytest==8.4.0
pre-commit==4.2.0
detect-secrets==1.5.0
isort==6.0.1
```

---

## 5. Proposed Better Architecture

The core insight is that each MCP tool is a self-contained unit: it has a schema, a handler, and (optionally) a formatter. Making that relationship explicit eliminates the triple-site registration problem and yields a naturally extensible structure.

### 5.1 Tool Registry Pattern

Instead of three disconnected sites, a single `ToolDefinition` dataclass co-locates everything a tool needs:

```python
# tools/base.py
from dataclasses import dataclass
from typing import Any, Callable, Awaitable
import mcp.types as types

@dataclass
class ToolDefinition:
    name: str
    description: str
    input_schema: dict
    handler: Callable[..., Awaitable[list[types.TextContent]]]

# tools/registry.py
_registry: dict[str, ToolDefinition] = {}

def register(tool: ToolDefinition) -> ToolDefinition:
    _registry[tool.name] = tool
    return tool

def get_all() -> list[types.Tool]:
    return [
        types.Tool(name=t.name, description=t.description, inputSchema=t.input_schema)
        for t in _registry.values()
    ]

async def dispatch(name: str, arguments: dict, client) -> list[types.TextContent]:
    if name not in _registry:
        return [types.TextContent(type="text", text=f"Unknown tool: {name}")]
    return await _registry[name].handler(client, arguments)
```

### 5.2 Per-Domain Tool Modules

Each resource category lives in its own module; registration is the only side effect on import:

```python
# tools/applications.py
from .registry import register, ToolDefinition
from utils import CodeEngineClient, CodeEngineError, format_apps_summary
import mcp.types as types, json

_LIST_SCHEMA = {
    "type": "object",
    "properties": {
        "project_id": {"type": "string", "description": "Code Engine project ID"},
        "limit": {"type": "integer", "default": 100, "minimum": 1, "maximum": 200},
    },
    "required": ["project_id"],
    "additionalProperties": False,
}

async def _list_applications(client: CodeEngineClient, args: dict):
    try:
        apps = client.list_applications(
            project_id=args["project_id"],
            limit=args.get("limit", 100),
        )
        summary = format_apps_summary(apps)
        raw = json.dumps(apps, indent=2, default=str)
        return [types.TextContent(type="text", text=f"{summary}\n\n**Raw JSON:**\n```json\n{raw}\n```")]
    except CodeEngineError as e:
        return [types.TextContent(type="text", text=f"Code Engine API error: {e}")]

register(ToolDefinition(
    name="list_applications",
    description="List applications in a specific Code Engine project",
    input_schema=_LIST_SCHEMA,
    handler=_list_applications,
))
```

### 5.3 Dependency-Injected Client

Pass `client` explicitly to handlers; the global is gone:

```python
# server.py
from mcp.server import Server
import mcp.types as types
from tools import registry
from utils import create_code_engine_client, CodeEngineClient

def create_server(client: CodeEngineClient) -> Server:
    server = Server("ibm-code-engine-mcp")

    @server.list_tools()
    async def list_tools():
        return registry.get_all()

    @server.call_tool()
    async def call_tool(name: str, arguments: dict):
        return await registry.dispatch(name, arguments, client)

    return server

async def main():
    client = create_code_engine_client()
    app = create_server(client)
    from mcp.server.stdio import stdio_server
    from mcp.server import InitializationOptions
    async with stdio_server() as (r, w):
        await app.run(r, w, InitializationOptions(
            server_name="ibm-code-engine-mcp",
            server_version="1.0.0",
            capabilities={},
        ))
```

### 5.4 Split Requirements

```
# requirements/base.txt  — production deps only
mcp==1.9.4
ibm-code-engine-sdk==4.20.0
ibm-cloud-sdk-core==3.24.2
ibm-platform-services==0.66.2
pydantic==2.11.5
python-dotenv==1.1.0

# requirements/dev.txt
-r base.txt
pylint==3.3.7
pytest==8.4.0
pytest-asyncio==0.24.0
pre-commit==4.2.0
detect-secrets==1.5.0
```

```dockerfile
# Dockerfile — only install base
COPY requirements/base.txt requirements.txt
RUN pip install --user --no-cache-dir -r requirements.txt
```

### 5.5 Proposed Directory Structure

```
code-engine-mcp/
├── server.py                  # MCP wiring only (~40 lines)
├── utils.py                   # CodeEngineClient + formatters
├── tools/
│   ├── __init__.py            # imports all modules to trigger registration
│   ├── base.py                # ToolDefinition dataclass
│   ├── registry.py            # register(), get_all(), dispatch()
│   ├── projects.py            # list_projects, find_project_by_name
│   ├── applications.py        # list, get, create, update, revisions
│   ├── builds.py              # create, list, run, get_run
│   ├── jobs.py                # list, get, runs
│   ├── domains.py             # list, get
│   └── secrets.py             # list, get (with masking)
├── requirements/
│   ├── base.txt
│   └── dev.txt
├── tests/
│   ├── conftest.py            # shared fixtures, correct imports
│   ├── test_projects.py
│   ├── test_applications.py
│   └── test_registry.py      # dispatch / unknown-tool behaviour
├── ce_push.py                 # standalone CLI (unchanged)
├── Dockerfile
└── healthcheck.py
```

---

## 6. Targeted Quick Wins (Low Risk)

These changes can be made without the full restructure and immediately improve correctness:

| # | Fix | File | Effort |
|---|-----|------|--------|
| 1 | Fix the import in `tests/test_server.py` to target `ce_mcp_server_v3` | `tests/test_server.py:17` | 2 lines |
| 2 | Split `requirements.txt` into `base.txt` / `dev.txt`; update `Dockerfile` | `requirements.txt`, `Dockerfile` | ~15 min |
| 3 | Extract `format_builds_summary()`, `format_build_runs_summary()`, `format_domain_mappings_summary()` into `utils.py` to match existing `format_apps_summary()` pattern | `utils.py`, `ce_mcp_server_v3.py` | ~30 min |
| 4 | Remove the double-exception-catch in `handle_call_tool` — the outer try/except and each inner handler both catch `Exception`, masking which layer actually raised | `ce_mcp_server_v3.py:767` | 5 min |
| 5 | Replace `global ce_client` mutation in `main()` with a parameter passed through `create_server(client)` | `ce_mcp_server_v3.py:1444` | ~20 min |

---

## 7. Summary

The current implementation is coherent and correct for its scope. The primary structural debt is the **triple-site tool registration** pattern, which scales poorly and already has one live consequence (the dead test suite targeting the wrong module name). The global client and inconsistent formatting pattern are secondary concerns that compound as the tool count grows. The proposed tool-registry pattern resolves all three by making each tool a single first-class object that self-registers, carries its own schema, and receives the client via injection rather than global lookup.
