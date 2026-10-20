#!/usr/bin/env python3
"""
Tests for the MCP server functionality
"""

import pytest
import mcp.types as types
from unittest.mock import patch, MagicMock
import sys
import os

pytestmark = pytest.mark.asyncio

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the server module
from ce_mcp_server_v3 import handle_call_tool, handle_list_tools  # noqa: E402

@pytest.fixture
def mock_ce_client():
    """Mock Code Engine client for testing"""
    client = MagicMock()
    # Set up mock return values
    client.list_projects.return_value = [
        {
            "id": "project1",
            "name": "test-project",
            "region": "us-south",
            "status": "active",
            "created_at": "2025-01-01T00:00:00Z"
        },
    ]
    client.list_applications.return_value = [
        {
            "id": "app1",
            "name": "test-app",
            "status": "ready",
            "image_reference": "test-image:latest",
            "created_at": "2025-01-01T00:00:00Z",
            "endpoint": "https://test-app.example.com"
        }
    ]
    client.get_application.return_value = {
        "id": "app1",
        "name": "test-app",
        "status": "ready",
        "image_reference": "test-image:latest",
        "created_at": "2025-01-01T00:00:00Z",
        "endpoint": "https://test-app.example.com",
        "project_id": "project1"
    }
    return client

async def test_list_tools():
    """Test that the server lists tools correctly"""
    # Call the list_tools handler via the registered handler
    tools = await handle_list_tools()

    # Verify the result
    assert isinstance(tools, list)
    assert len(tools) == 22, "Should have exactly 22 tools"

    # Check tool names
    tool_names = [tool.name for tool in tools]
    assert "list_projects" in tool_names
    assert "list_applications" in tool_names
    assert "get_application" in tool_names

    # Verify all tools have required properties
    for tool in tools:
        assert isinstance(tool, types.Tool)
        assert tool.name
        assert tool.description
        assert tool.inputSchema

async def test_call_tool_list_projects(mock_ce_client):
    """Test list_projects tool call"""
    # Mock the ce_client global variable
    with patch("ce_mcp_server_v3.ce_client", mock_ce_client):
        # Call the handler
        result = await handle_call_tool("list_projects", {"limit": 10})

        # Verify the client was called correctly
        mock_ce_client.list_projects.assert_called_once()
        assert mock_ce_client.list_projects.call_args[1]["limit"] == 10

        # Verify the response
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], types.TextContent)
        assert result[0].type == "text"
        assert "Found 1 Code Engine projects" in result[0].text
        assert "test-project" in result[0].text
        assert "Raw JSON Data" in result[0].text

async def test_call_tool_list_applications(mock_ce_client):
    """Test list_applications tool call"""
    # Mock the ce_client global variable
    with patch("ce_mcp_server_v3.ce_client", mock_ce_client):
        # Call the handler
        result = await handle_call_tool("list_applications", {
            "project_id": "project1",
            "limit": 10
        })

        # Verify the client was called correctly
        mock_ce_client.list_applications.assert_called_once()
        assert mock_ce_client.list_applications.call_args[1]["project_id"] == "project1"
        assert mock_ce_client.list_applications.call_args[1]["limit"] == 10

        # Verify the response
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], types.TextContent)
        assert result[0].type == "text"
        assert "Found 1 applications" in result[0].text
        assert "test-app" in result[0].text
        assert "Raw JSON Data" in result[0].text

async def test_call_tool_get_application(mock_ce_client):
    """Test get_application tool call"""
    # Mock the ce_client global variable
    with patch("ce_mcp_server_v3.ce_client", mock_ce_client):
        # Call the handler
        result = await handle_call_tool("get_application", {
            "project_id": "project1",
            "app_name": "test-app"
        })

        # Verify the client was called correctly
        mock_ce_client.get_application.assert_called_once()
        assert mock_ce_client.get_application.call_args[1]["project_id"] == "project1"
        assert mock_ce_client.get_application.call_args[1]["app_name"] == "test-app"

        # Verify the response
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], types.TextContent)
        assert result[0].type == "text"
        assert "Application Details for test-app" in result[0].text
        assert "Raw JSON Data" not in result[0].text  # get returns JSON directly

async def test_call_tool_unknown(mock_ce_client):
    """Test calling an unknown tool"""
    with patch("ce_mcp_server_v3.ce_client", mock_ce_client):
        result = await handle_call_tool("unknown_tool", {})

    # Verify the response
    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], types.TextContent)
    assert result[0].type == "text"
    assert "Unknown tool: unknown_tool" in result[0].text

async def test_call_tool_error(mock_ce_client):
    """Test error handling in tool call"""
    # Mock the ce_client global variable to raise an exception
    mock_ce_client.list_projects.side_effect = Exception("Test error")

    with patch("ce_mcp_server_v3.ce_client", mock_ce_client):
        # Call the handler
        result = await handle_call_tool("list_projects", {"limit": 10})

        # Verify the response contains the error
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], types.TextContent)
        assert result[0].type == "text"
        assert "error" in result[0].text.lower()
        assert "Test error" in result[0].text
