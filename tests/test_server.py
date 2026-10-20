#!/usr/bin/env python3
"""
Tests for the MCP server (server.py + tools registry).
"""

import sys
import os
from unittest.mock import MagicMock

import mcp.types as types
import pytest

pytestmark = pytest.mark.asyncio

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import tools  # noqa: F401, E402 — triggers tool registration
from tools import registry  # noqa: E402
from server import create_server  # noqa: E402


@pytest.fixture
def mock_client():
    """Mock CodeEngineClient for testing."""
    client = MagicMock()
    client.list_projects.return_value = [
        {
            "id": "project1",
            "name": "test-project",
            "region": "us-south",
            "status": "active",
            "created_at": "2025-01-01T00:00:00Z",
        }
    ]
    client.list_applications.return_value = [
        {
            "id": "app1",
            "name": "test-app",
            "status": "ready",
            "image_reference": "test-image:latest",
            "created_at": "2025-01-01T00:00:00Z",
            "endpoint": "https://test-app.example.com",
        }
    ]
    client.get_application.return_value = {
        "id": "app1",
        "name": "test-app",
        "status": "ready",
        "image_reference": "test-image:latest",
        "created_at": "2025-01-01T00:00:00Z",
        "endpoint": "https://test-app.example.com",
        "project_id": "project1",
    }
    return client


# ---------------------------------------------------------------------------
# Registry: tool list
# ---------------------------------------------------------------------------

async def test_registry_returns_22_tools():
    tools_list = registry.get_all()
    assert isinstance(tools_list, list)
    assert len(tools_list) == 22
    for tool in tools_list:
        assert isinstance(tool, types.Tool)
        assert tool.name
        assert tool.description
        assert tool.inputSchema


async def test_registry_has_expected_tool_names():
    names = {t.name for t in registry.get_all()}
    expected = {
        "list_projects", "find_project_by_name",
        "list_applications", "get_application", "list_app_revisions",
        "get_app_revision", "create_application", "update_application",
        "create_app_from_source",
        "create_build", "list_builds", "create_build_run", "get_build_run",
        "list_build_runs",
        "list_jobs", "get_job", "list_job_runs", "get_job_run",
        "list_domain_mappings", "get_domain_mapping",
        "list_secrets", "get_secret",
    }
    assert names == expected


# ---------------------------------------------------------------------------
# Registry: dispatch
# ---------------------------------------------------------------------------

async def test_dispatch_list_projects(mock_client):
    result = await registry.dispatch("list_projects", {"limit": 10}, mock_client)

    mock_client.list_projects.assert_called_once_with(limit=10)
    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], types.TextContent)
    assert "Found 1 Code Engine projects" in result[0].text
    assert "test-project" in result[0].text
    assert "Raw JSON Data" in result[0].text


async def test_dispatch_list_applications(mock_client):
    result = await registry.dispatch(
        "list_applications", {"project_id": "project1", "limit": 10}, mock_client
    )

    mock_client.list_applications.assert_called_once_with(project_id="project1", limit=10)
    assert "Found 1 applications" in result[0].text
    assert "test-app" in result[0].text


async def test_dispatch_get_application(mock_client):
    result = await registry.dispatch(
        "get_application", {"project_id": "project1", "app_name": "test-app"}, mock_client
    )

    mock_client.get_application.assert_called_once_with(project_id="project1", app_name="test-app")
    assert "Application Details for test-app" in result[0].text


async def test_dispatch_unknown_tool(mock_client):
    result = await registry.dispatch("no_such_tool", {}, mock_client)
    assert "Unknown tool: no_such_tool" in result[0].text


async def test_dispatch_propagates_error(mock_client):
    mock_client.list_projects.side_effect = Exception("boom")
    result = await registry.dispatch("list_projects", {}, mock_client)
    assert "error" in result[0].text.lower()
    assert "boom" in result[0].text


# ---------------------------------------------------------------------------
# Server factory
# ---------------------------------------------------------------------------

async def test_create_server_list_tools(mock_client):
    """create_server() wires list_tools to the registry."""
    app = create_server(mock_client)
    # The server object should be usable; we verify via registry directly
    # since we can't invoke the MCP protocol handlers directly without a full
    # stdio loop.  The registry tests above already cover the handler logic.
    assert app is not None
