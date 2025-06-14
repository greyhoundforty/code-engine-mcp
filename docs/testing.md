# Testing Guide

This document provides guidance on setting up and running tests for the IBM Code Engine MCP Server project, with a particular focus on supporting the upcoming application creation features.

## Setting up pytest

### Installation

First, ensure you have pytest and related packages installed:

```bash
pip install pytest pytest-asyncio pytest-mock pytest-cov
```

Or add them to your requirements.txt and install:

```bash
# requirements-dev.txt
pytest==7.4.3
pytest-asyncio==0.23.2
pytest-mock==3.12.0
pytest-cov==4.1.0
```

### Project Structure

Organize tests in a directory structure that mirrors your main code:

```
project-root/
├── ce_mcp_server.py
├── utils.py
└── tests/
    ├── conftest.py            # Shared pytest fixtures
    ├── test_server.py         # Tests for MCP server functionality
    ├── test_utils.py          # Tests for utility functions
    └── test_app_creation/     # Tests for application creation features
        ├── conftest.py        # App-creation specific fixtures
        ├── test_basic.py      # Basic app creation tests
        └── test_advanced.py   # Advanced app creation tests
```

## Creating Test Fixtures

### Basic Fixtures

Create a `conftest.py` file with common fixtures:

```python
# tests/conftest.py
import pytest
import os
from unittest.mock import MagicMock

@pytest.fixture
def mock_ce_client():
    """Mock Code Engine client for testing"""
    client = MagicMock()
    # Set up mock return values
    client.list_projects.return_value = [
        {"id": "project1", "name": "test-project", "region": "us-south", "status": "active"},
    ]
    client.list_applications.return_value = [
        {"id": "app1", "name": "test-app", "status": "ready"}
    ]
    return client

@pytest.fixture
def mock_env_vars(monkeypatch):
    """Set mock environment variables for testing"""
    monkeypatch.setenv("IBMCLOUD_API_KEY", "mock-api-key")
    monkeypatch.setenv("IBMCLOUD_REGION", "us-south")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
```

### App Creation Fixtures

Create additional fixtures for application creation testing:

```python
# tests/test_app_creation/conftest.py
import pytest
from unittest.mock import MagicMock

@pytest.fixture
def mock_create_app_response():
    """Mock response for application creation"""
    return {
        "id": "new-app-id",
        "name": "new-test-app",
        "project_id": "project1",
        "status": "creating",
        "image_reference": "test-image:latest",
        "created_at": "2025-06-14T10:00:00Z"
    }

@pytest.fixture
def mock_ce_client_with_create(mock_ce_client):
    """Extend mock Code Engine client with create app capability"""
    mock_ce_client.create_application = MagicMock(
        return_value=mock_create_app_response()
    )
    return mock_ce_client
```

## Example Test Cases

### Basic Server Tests

```python
# tests/test_server.py
import pytest
import asyncio
import mcp.types as types
from ce_mcp_server import server, handle_call_tool
from unittest.mock import patch, MagicMock

@pytest.mark.asyncio
async def test_list_tools():
    """Test that the server lists tools correctly"""
    tools = await server.list_tools_handler()
    assert len(tools) >= 3  # At least the basic tools
    tool_names = [tool.name for tool in tools]
    assert "list_projects" in tool_names
    assert "list_applications" in tool_names
    assert "get_application" in tool_names

@pytest.mark.asyncio
@patch("ce_mcp_server.ce_client")
async def test_list_projects(mock_client, mock_ce_client):
    """Test list_projects tool call"""
    mock_client.return_value = mock_ce_client

    result = await handle_call_tool("list_projects", {"limit": 10})

    assert mock_ce_client.list_projects.called
    assert mock_ce_client.list_projects.call_args[1]["limit"] == 10
    assert len(result) == 1
    assert "Found" in result[0].text
```

### Future App Creation Tests

```python
# tests/test_app_creation/test_basic.py
import pytest
import asyncio
from unittest.mock import patch, MagicMock

@pytest.mark.asyncio
@patch("ce_mcp_server.ce_client")
async def test_create_application_basic(mock_client, mock_ce_client_with_create):
    """Test basic application creation"""
    mock_client.return_value = mock_ce_client_with_create

    # Assuming you'll implement a create_application tool
    result = await handle_call_tool("create_application", {
        "project_id": "project1",
        "name": "new-test-app",
        "image": "test-image:latest"
    })

    # Verify the client was called correctly
    mock_ce_client_with_create.create_application.assert_called_once()
    call_args = mock_ce_client_with_create.create_application.call_args[1]
    assert call_args["project_id"] == "project1"
    assert call_args["name"] == "new-test-app"
    assert call_args["image_reference"] == "test-image:latest"

    # Verify the response was formatted correctly
    assert len(result) == 1
    assert "new-test-app" in result[0].text
    assert "creating" in result[0].text
```

## Running Tests

### Basic Test Commands

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_server.py

# Run specific test
pytest tests/test_server.py::test_list_tools

# Run tests with coverage report
pytest --cov=. --cov-report=term --cov-report=html
```

### Adding Tests to Mise Tasks

Add testing tasks to your `.mise.toml` file:

```toml
[tasks.test]
description = "Run all tests"
run = "pytest -v"

[tasks."test:unit"]
description = "Run unit tests only"
run = "pytest tests/test_server.py tests/test_utils.py -v"

[tasks."test:app-creation"]
description = "Run app creation tests"
run = "pytest tests/test_app_creation -v"

[tasks."test:coverage"]
description = "Run tests with coverage"
run = "pytest --cov=. --cov-report=term --cov-report=html"
```

## Testing Application Creation Features

When implementing application creation features, consider the following test scenarios:

1. **Basic app creation** - Test creating an application with minimal required parameters
2. **Parameter validation** - Test validation of required and optional parameters
3. **Error handling** - Test handling of API errors, invalid inputs, etc.
4. **App configuration** - Test setting various configuration options (memory, CPU, env vars)
5. **Wait for ready** - Test the ability to wait for an application to become ready
6. **Idempotency** - Test that creating an app with the same name is handled correctly

## Mocking IBM Cloud SDK

For effective testing without actual IBM Cloud calls, mock the SDK responses:

```python
# Example of mocking an IBM Code Engine SDK method
def test_create_application_sdk_interaction(mocker):
    # Mock the SDK response
    mock_response = mocker.MagicMock()
    mock_response.get_result.return_value = {
        "id": "app-id-123",
        "name": "test-app",
        "status": "creating"
    }

    # Mock the SDK method
    mock_create_app = mocker.patch(
        "ibm_code_engine_sdk.code_engine_v2.CodeEngineV2.create_app",
        return_value=mock_response
    )

    # Test your code that uses the SDK
    # ...

    # Verify the SDK was called correctly
    mock_create_app.assert_called_once()
```

## Integration Testing (Optional)

For more thorough testing, consider setting up integration tests with a test IBM Cloud account:

1. Create a separate test account/project in IBM Cloud
2. Use environment variables to control whether to run integration tests
3. Only run integration tests in secure environments (not in public CI)

```python
# Example of an integration test
@pytest.mark.integration
@pytest.mark.skipif(not os.getenv("RUN_INTEGRATION_TESTS"), reason="Integration tests disabled")
def test_integration_create_application():
    # This will make actual IBM Cloud API calls
    from utils import create_code_engine_client
    client = create_code_engine_client()

    # Create a test application
    result = client.create_application(
        project_id=os.getenv("TEST_PROJECT_ID"),
        name=f"test-app-{uuid.uuid4().hex[:8]}",  # Unique name
        image_reference="python:3.9-slim"
    )

    # Verify the result
    assert result["status"] in ["creating", "ready"]

    # Clean up (delete the application)
    client.delete_application(
        project_id=os.getenv("TEST_PROJECT_ID"),
        name=result["name"]
    )
```
