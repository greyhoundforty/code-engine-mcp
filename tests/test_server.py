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
    client.list_config_maps.return_value = [
        {"name": "my-cm", "data": {"HOST": "db.example.com"}, "created_at": "2025-01-01T00:00:00Z"},
    ]
    client.get_config_map.return_value = {
        "name": "my-cm", "data": {"HOST": "db.example.com"}, "created_at": "2025-01-01T00:00:00Z",
    }
    client.create_config_map.return_value = {
        "name": "new-cm", "data": {"KEY": "val"}, "created_at": "2025-01-01T00:00:00Z",
    }
    client.replace_config_map.return_value = {
        "name": "my-cm", "data": {"HOST": "new-host"}, "created_at": "2025-01-01T00:00:00Z",
    }
    client.list_functions.return_value = [
        {
            "name": "my-fn", "runtime": "nodejs-20", "status": "ready",
            "endpoint": "https://my-fn.example.com", "created_at": "2025-01-01T00:00:00Z",
        }
    ]
    client.get_function.return_value = {
        "name": "my-fn", "runtime": "nodejs-20", "status": "ready",
        "endpoint": "https://my-fn.example.com", "created_at": "2025-01-01T00:00:00Z",
    }
    client.list_function_runtimes.return_value = [
        {"name": "nodejs-20"}, {"name": "nodejs-22"}, {"name": "python-3.11"},
    ]
    client.list_bindings.return_value = [
        {
            "id": "bind-abc",
            "component": {"name": "my-app", "resource_type": "app_v2"},
            "prefix": "COS",
            "secret_name": "cos-secret",  # pragma: allowlist secret
            "status": "active",
        }
    ]
    client.get_binding.return_value = {
        "id": "bind-abc",
        "component": {"name": "my-app", "resource_type": "app_v2"},
        "prefix": "COS",
        "secret_name": "cos-secret",  # pragma: allowlist secret
        "status": "active",
    }
    return client


# ---------------------------------------------------------------------------
# Registry: tool list
# ---------------------------------------------------------------------------

async def test_registry_returns_37_tools():
    tools_list = registry.get_all()
    assert isinstance(tools_list, list)
    assert len(tools_list) == 37
    for tool in tools_list:
        assert isinstance(tool, types.Tool)
        assert tool.name
        assert tool.description
        assert tool.inputSchema


async def test_registry_has_expected_tool_names():
    names = {t.name for t in registry.get_all()}
    expected = {
        # projects
        "list_projects", "find_project_by_name",
        # applications
        "list_applications", "get_application", "list_app_revisions",
        "get_app_revision", "create_application", "update_application",
        "create_app_from_source",
        # builds
        "create_build", "list_builds", "create_build_run", "get_build_run",
        "list_build_runs",
        # jobs
        "list_jobs", "get_job", "list_job_runs", "get_job_run",
        # domains
        "list_domain_mappings", "get_domain_mapping",
        # secrets
        "list_secrets", "get_secret",
        # configmaps
        "list_config_maps", "get_config_map", "create_config_map",
        "update_config_map", "delete_config_map",
        # functions
        "list_functions", "get_function", "create_function",
        "update_function", "delete_function", "list_function_runtimes",
        # service bindings
        "list_bindings", "get_binding", "create_binding", "delete_binding",
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


# ---------------------------------------------------------------------------
# Dispatch: configmaps
# ---------------------------------------------------------------------------

async def test_dispatch_list_config_maps(mock_client):
    result = await registry.dispatch("list_config_maps", {"project_id": "project1"}, mock_client)
    mock_client.list_config_maps.assert_called_once_with(project_id="project1", limit=100)
    assert "1 configmap" in result[0].text
    assert "my-cm" in result[0].text


async def test_dispatch_get_config_map(mock_client):
    result = await registry.dispatch("get_config_map", {"project_id": "project1", "name": "my-cm"}, mock_client)
    mock_client.get_config_map.assert_called_once_with(project_id="project1", name="my-cm")
    assert "my-cm" in result[0].text


async def test_dispatch_create_config_map(mock_client):
    result = await registry.dispatch(
        "create_config_map",
        {"project_id": "project1", "name": "new-cm", "data": {"KEY": "val"}},
        mock_client,
    )
    mock_client.create_config_map.assert_called_once_with(
        project_id="project1", name="new-cm", data={"KEY": "val"}
    )
    assert "new-cm" in result[0].text


async def test_dispatch_update_config_map(mock_client):
    result = await registry.dispatch(
        "update_config_map",
        {"project_id": "project1", "name": "my-cm", "data": {"HOST": "new-host"}},
        mock_client,
    )
    mock_client.replace_config_map.assert_called_once_with(
        project_id="project1", name="my-cm", data={"HOST": "new-host"}
    )
    assert "my-cm" in result[0].text


async def test_dispatch_delete_config_map(mock_client):
    result = await registry.dispatch("delete_config_map", {"project_id": "project1", "name": "my-cm"}, mock_client)
    mock_client.delete_config_map.assert_called_once_with(project_id="project1", name="my-cm")
    assert "deleted" in result[0].text.lower()


# ---------------------------------------------------------------------------
# Dispatch: functions
# ---------------------------------------------------------------------------

async def test_dispatch_list_functions(mock_client):
    result = await registry.dispatch("list_functions", {"project_id": "project1"}, mock_client)
    mock_client.list_functions.assert_called_once_with(project_id="project1", limit=100)
    assert "1 function" in result[0].text
    assert "my-fn" in result[0].text


async def test_dispatch_get_function(mock_client):
    result = await registry.dispatch("get_function", {"project_id": "project1", "name": "my-fn"}, mock_client)
    mock_client.get_function.assert_called_once_with(project_id="project1", name="my-fn")
    assert "my-fn" in result[0].text


async def test_dispatch_list_function_runtimes(mock_client):
    result = await registry.dispatch("list_function_runtimes", {}, mock_client)
    mock_client.list_function_runtimes.assert_called_once()
    assert "nodejs-20" in result[0].text
    assert "python-3.11" in result[0].text


# ---------------------------------------------------------------------------
# Dispatch: service bindings
# ---------------------------------------------------------------------------

async def test_dispatch_list_bindings(mock_client):
    result = await registry.dispatch("list_bindings", {"project_id": "project1"}, mock_client)
    mock_client.list_bindings.assert_called_once_with(project_id="project1", limit=100)
    assert "1 service binding" in result[0].text
    assert "bind-abc" in result[0].text


async def test_dispatch_get_binding(mock_client):
    result = await registry.dispatch("get_binding", {"project_id": "project1", "binding_id": "bind-abc"}, mock_client)
    mock_client.get_binding.assert_called_once_with(project_id="project1", binding_id="bind-abc")
    assert "bind-abc" in result[0].text


async def test_dispatch_delete_binding(mock_client):
    result = await registry.dispatch("delete_binding", {"project_id": "project1", "binding_id": "bind-abc"}, mock_client)
    mock_client.delete_binding.assert_called_once_with(project_id="project1", binding_id="bind-abc")
    assert "deleted" in result[0].text.lower()
