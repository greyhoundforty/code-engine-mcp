#!/usr/bin/env python3
"""
Tests for the MCP server functionality
"""

import pytest
import mcp.types as types
from unittest.mock import patch, MagicMock
import sys
import os

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the server module - adjust the import if you renamed the file
try:
    from ce_mcp_server import server, handle_call_tool
except ImportError:
    try:
        from ce_mcp_server_v2 import server, handle_call_tool
    except ImportError:
        pytest.skip("Server module could not be imported", allow_module_level=True)

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

@pytest.mark.asyncio
async def test_list_tools():
    """Test that the server lists tools correctly"""
    # Get the list_tools handler directly
    list_tools_handler = None
    for handler in server._handlers:
        if handler.__name__ == "list_tools":
            list_tools_handler = handler
            break

    assert list_tools_handler is not None, "list_tools handler not found"

    # Call the handler
    tools = await list_tools_handler()

    # Verify the result
    assert isinstance(tools, list)
    assert len(tools) >= 3, "Should have at least 3 tools"

    # Check tool properties
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

@pytest.mark.asyncio
async def test_call_tool_list_projects(mock_ce_client):
    """Test list_projects tool call"""
    # Mock the ce_client global variable
    with patch("ce_mcp_server.ce_client", mock_ce_client):
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

@pytest.mark.asyncio
async def test_call_tool_list_applications(mock_ce_client):
    """Test list_applications tool call"""
    # Mock the ce_client global variable
    with patch("ce_mcp_server.ce_client", mock_ce_client):
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

@pytest.mark.asyncio
async def test_call_tool_get_application(mock_ce_client):
    """Test get_application tool call"""
    # Mock the ce_client global variable
    with patch("ce_mcp_server.ce_client", mock_ce_client):
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
        assert "Application: test-app" in result[0].text
        assert "Status: ready" in result[0].text
        assert "Raw JSON Data" in result[0].text

@pytest.mark.asyncio
async def test_call_tool_unknown():
    """Test calling an unknown tool"""
    result = await handle_call_tool("unknown_tool", {})

    # Verify the response
    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], types.TextContent)
    assert result[0].type == "text"
    assert "Unknown tool: unknown_tool" in result[0].text

@pytest.mark.asyncio
async def test_call_tool_error(mock_ce_client):
    """Test error handling in tool call"""
    # Mock the ce_client global variable to raise an exception
    mock_ce_client.list_projects.side_effect = Exception("Test error")

    with patch("ce_mcp_server.ce_client", mock_ce_client):
        # Call the handler
        result = await handle_call_tool("list_projects", {"limit": 10})

        # Verify the response contains the error
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], types.TextContent)
        assert result[0].type == "text"
        assert "Error" in result[0].text
        assert "Test error" in result[0].text
