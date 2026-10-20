"""
Tool registry.

Domain modules call register() at import time.  The server calls
get_all() to expose the tool list and dispatch() to route calls.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import mcp.types as types

from tools.base import ToolDefinition

if TYPE_CHECKING:
    from utils import CodeEngineClient

_registry: dict[str, ToolDefinition] = {}


def register(tool: ToolDefinition) -> None:
    """Register a tool definition.  Called once per tool at import time."""
    if tool.name in _registry:
        raise ValueError(f"Tool '{tool.name}' is already registered")
    _registry[tool.name] = tool


def get_all() -> list[types.Tool]:
    """Return MCP Tool objects for every registered tool."""
    return [
        types.Tool(
            name=t.name,
            description=t.description,
            inputSchema=t.input_schema,
        )
        for t in _registry.values()
    ]


async def dispatch(
    name: str,
    arguments: dict[str, Any],
    client: "CodeEngineClient",
) -> list[types.TextContent]:
    """Route a tool call to its registered handler."""
    if name not in _registry:
        return [types.TextContent(type="text", text=f"Unknown tool: {name}")]
    return await _registry[name].handler(client, arguments)
