"""
Tool registry base type.

A ToolDefinition groups together everything a single MCP tool needs:
its name, description, JSON schema, and async handler.  The handler
receives the injected CodeEngineClient and the raw arguments dict.
"""

from dataclasses import dataclass
from typing import Any, Awaitable, Callable

import mcp.types as types

from utils import CodeEngineClient

ToolHandler = Callable[
    [CodeEngineClient, dict[str, Any]],
    Awaitable[list[types.TextContent]],
]


@dataclass
class ToolDefinition:
    name: str
    description: str
    input_schema: dict[str, Any]
    handler: ToolHandler
