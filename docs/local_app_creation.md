# Creating Code Engine Applications from Local Directories

This guide explains how to implement and use a tool for creating Code Engine applications from local directories using the MCP server.

## Background

IBM Code Engine supports creating applications from various sources:
- Container images in a registry
- Source code in a Git repository
- Local source code directories

The last option requires handling file uploads to Code Engine, which involves:
1. Packaging the local directory
2. Creating a buildpack-based application
3. Monitoring the build process

## Implementation Strategy

### 1. New Tool Definition

Add a new tool to the MCP server for creating applications from local directories:

```python
types.Tool(
    name="create_app_from_local",
    description="Create a Code Engine application from a local directory",
    inputSchema={
        "type": "object",
        "properties": {
            "project_id": {
                "type": "string",
                "description": "Code Engine project ID"
            },
            "app_name": {
                "type": "string",
                "description": "Name for the new application"
            },
            "directory_path": {
                "type": "string",
                "description": "Path to the local directory containing source code"
            },
            "memory": {
                "type": "string",
                "description": "Memory allocation (e.g., '2G')",
                "default": "2G"
            },
            "cpu": {
                "type": "string",
                "description": "CPU allocation (e.g., '1')",
                "default": "1"
            },
            "min_scale": {
                "type": "integer",
                "description": "Minimum number of instances",
                "default": 0
            },
            "max_scale": {
                "type": "integer",
                "description": "Maximum number of instances",
                "default": 10
            },
            "port": {
                "type": "integer",
                "description": "Port the application listens on",
                "default": 8080
            },
            "env_vars": {
                "type": "object",
                "description": "Environment variables for the application",
                "default": {}
            },
            "build_strategy": {
                "type": "string",
                "description": "Build strategy to use",
                "enum": ["dockerfile", "buildpacks"],
                "default": "dockerfile"
            },
            "wait_for_completion": {
                "type": "boolean",
                "description": "Wait for the build to complete",
                "default": true
            }
        },
        "required": ["project_id", "app_name", "directory_path"]
    }
)
```

### 2. File Processing Utility

Add a utility function to handle directory packaging:

```python
# In utils.py
import os
import tempfile
import tarfile
import time
from typing import Dict, Any, Optional

def package_directory(directory_path: str) -> str:
    """
    Package a local directory into a tarball for upload

    Args:
        directory_path: Path to the local directory

    Returns:
        Path to the created tarball
    """
    if not os.path.isdir(directory_path):
        raise ValueError(f"Directory not found: {directory_path}")

    # Create a temporary file for the tarball
    fd, tarball_path = tempfile.mkstemp(suffix='.tar.gz')
    os.close(fd)

    try:
        with tarfile.open(tarball_path, "w:gz") as tar:
            tar.add(directory_path, arcname=".")

        return tarball_path
    except Exception as e:
        # Clean up on error
        if os.path.exists(tarball_path):
            os.unlink(tarball_path)
        raise RuntimeError(f"Failed to package directory: {str(e)}")
```

### 3. Application Creation Function

Add a method to the `CodeEngineClient` class to handle application creation:

```python
# In utils.py
def create_application_from_local(
    self,
    project_id: str,
    app_name: str,
    directory_path: str,
    memory: str = "2G",
    cpu: str = "1",
    min_scale: int = 0,
    max_scale: int = 10,
    port: int = 8080,
    env_vars: Dict[str, str] = None,
    build_strategy: str = "buildpacks",
    wait_for_completion: bool = True
) -> Dict[str, Any]:
    """
    Create a Code Engine application from a local directory

    Args:
        project_id: Code Engine project ID
        app_name: Name for the new application
        directory_path: Path to local directory containing source code
        memory: Memory allocation
        cpu: CPU allocation
        min_scale: Minimum number of instances
        max_scale: Maximum number of instances
        port: Port the application listens on
        env_vars: Environment variables for the application
        build_strategy: Build strategy to use
        wait_for_completion: Wait for the build to complete

    Returns:
        Application details dictionary
    """
    try:
        # Package the directory
        tarball_path = package_directory(directory_path)

        try:
            # Prepare environment variables
            environment_variables = []
            if env_vars:
                for key, value in env_vars.items():
                    environment_variables.append({
                        "key": key,
                        "value": value
                    })

            # Create the application
            response = self.service.create_app(
                project_id=project_id,
                name=app_name,
                image_port=port,
                image_reference=f"local-source-{app_name}",  # Placeholder
                run_env_variables=environment_variables,
                scale_min_instances=min_scale,
                scale_max_instances=max_scale,
                scale_cpu_limit=cpu,
                scale_memory_limit=memory
            )
            app = response.get_result()

            # Upload the source code
            with open(tarball_path, 'rb') as file:
                upload_response = self.service.create_app_source(
                    project_id=project_id,
                    app_name=app_name,
                    source_archive=file,
                    build_strategy=build_strategy
                )

            build_status = upload_response.get_result()

            # Optionally wait for the build to complete
            if wait_for_completion:
                build_id = build_status.get("id")
                while True:
                    build_response = self.service.get_app_build(
                        project_id=project_id,
                        app_name=app_name,
                        build_id=build_id
                    )
                    build_info = build_response.get_result()

                    status = build_info.get("status")
                    if status in ["succeeded", "failed", "cancelled"]:
                        break

                    # Wait before checking again
                    time.sleep(5)

                # Get updated application details
                response = self.service.get_app(
                    project_id=project_id,
                    name=app_name
                )
                app = response.get_result()

            return app

        finally:
            # Clean up the tarball
            if os.path.exists(tarball_path):
                os.unlink(tarball_path)

    except ApiException as e:
        logger.error(f"API error creating application: {e}")
        raise CodeEngineError(f"Failed to create application: {e}")
    except Exception as e:
        logger.error(f"Unexpected error creating application: {e}")
        raise CodeEngineError(f"Unexpected error: {e}")
```

### 4. Tool Handler Implementation

Implement the handler for the new tool:

```python
# In ce_mcp_server.py
async def handle_create_app_from_local(arguments: dict) -> list[types.TextContent]:
    """Handle create_app_from_local tool call"""
    try:
        # Extract required arguments
        project_id = arguments.get('project_id')
        app_name = arguments.get('app_name')
        directory_path = arguments.get('directory_path')

        # Extract optional arguments with defaults
        memory = arguments.get('memory', '2G')
        cpu = arguments.get('cpu', '1')
        min_scale = arguments.get('min_scale', 0)
        max_scale = arguments.get('max_scale', 10)
        port = arguments.get('port', 8080)
        env_vars = arguments.get('env_vars', {})
        build_strategy = arguments.get('build_strategy', 'buildpacks')
        wait_for_completion = arguments.get('wait_for_completion', True)

        # Validate required arguments
        if not project_id or not app_name or not directory_path:
            return [types.TextContent(
                type="text",
                text="Error: project_id, app_name, and directory_path are required"
            )]

        # Check if the directory exists
        if not os.path.isdir(directory_path):
            return [types.TextContent(
                type="text",
                text=f"Error: Directory not found: {directory_path}"
            )]

        # Create the application
        app = ce_client.create_application_from_local(
            project_id=project_id,
            app_name=app_name,
            directory_path=directory_path,
            memory=memory,
            cpu=cpu,
            min_scale=min_scale,
            max_scale=max_scale,
            port=port,
            env_vars=env_vars,
            build_strategy=build_strategy,
            wait_for_completion=wait_for_completion
        )

        # Format the response
        status = app.get('status', 'Unknown')
        build_status = "completed" if wait_for_completion else "in progress"

        summary = f"**Application '{app_name}' created from local directory**\n\n"
        summary += f"• Status: {status}\n"
        summary += f"• Build: {build_status}\n"

        if app.get('endpoint'):
            summary += f"• Endpoint: {app.get('endpoint')}\n"

        # Include raw JSON but mask sensitive data
        masked_app = app.copy()
        raw_json = json.dumps(masked_app, indent=2, default=str)

        return [
            types.TextContent(
                type="text",
                text=f"{summary}\n\n**Raw JSON Data:**\n```json\n{raw_json}\n```"
            )
        ]

    except CodeEngineError as e:
        return [types.TextContent(type="text", text=f"Code Engine API error: {str(e)}")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Unexpected error: {str(e)}")]
```

### 5. Update Tool Routing

Update the `handle_call_tool` function to route to the new handler:

```python
@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """Handle tool calls for Code Engine operations"""
    global ce_client

    try:
        # Ensure we have a client
        if ce_client is None:
            logger.error("Code Engine client not initialized")
            return [types.TextContent(
                type="text",
                text="Error: Code Engine client not initialized. Please check your IBM Cloud API key."
            )]

        # Route to appropriate handler
        if name == "list_projects":
            return await handle_list_projects(arguments)
        elif name == "list_applications":
            return await handle_list_applications(arguments)
        elif name == "get_application":
            return await handle_get_application(arguments)
        elif name == "create_app_from_local":
            return await handle_create_app_from_local(arguments)
        # Add other handlers here
        else:
            return [types.TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )]

    except Exception as e:
        logger.error(f"Error handling tool call {name}: {e}")
        return [types.TextContent(
            type="text",
            text=f"Error executing {name}: {str(e)}"
        )]
```

## Usage Example

To create an application from a local directory:

```python
# Call the tool with appropriate arguments
result = await handle_call_tool("create_app_from_local", {
    "project_id": "your-project-id",
    "app_name": "my-local-app",
    "directory_path": "/path/to/your/app",
    "memory": "2G",
    "cpu": "1",
    "min_scale": 0,
    "max_scale": 10,
    "port": 8080,
    "env_vars": {
        "DEBUG": "true",
        "NODE_ENV": "production"
    },
    "build_strategy": "buildpacks",
    "wait_for_completion": True
})
```

## Limitations and Considerations

1. **Directory Size**: Large directories may take time to package and upload. Consider implementing progress tracking for large uploads.

2. **File Selection**: The current implementation packages the entire directory. If you need more granular file selection:
   - Add a `file_patterns` parameter (e.g., `["**/*.js", "**/*.json", "!node_modules/**"]`)
   - Use the `pathlib` library with `glob` patterns to filter files during packaging

3. **Security**: Ensure that:
   - The MCP server has appropriate filesystem access permissions
   - Large file uploads are monitored and limited to prevent resource exhaustion
   - Source code is scanned for sensitive information before upload

4. **Build Status**: For long-running builds, consider implementing a separate tool to check build status

5. **Error Handling**: Implement robust error handling, especially for network issues during file upload

## Advanced Implementation: Selective File Upload

For more granular file selection, you can enhance the `package_directory` function:

```python
import fnmatch
from pathlib import Path

def package_directory(
    directory_path: str,
    include_patterns: List[str] = None,
    exclude_patterns: List[str] = None
) -> str:
    """
    Package a local directory with file filtering

    Args:
        directory_path: Path to the local directory
        include_patterns: List of glob patterns to include
        exclude_patterns: List of glob patterns to exclude

    Returns:
        Path to the created tarball
    """
    if not os.path.isdir(directory_path):
        raise ValueError(f"Directory not found: {directory_path}")

    # Default patterns
    include_patterns = include_patterns or ["**/*"]
    exclude_patterns = exclude_patterns or []

    # Create a temporary file for the tarball
    fd, tarball_path = tempfile.mkstemp(suffix='.tar.gz')
    os.close(fd)

    try:
        with tarfile.open(tarball_path, "w:gz") as tar:
            # Walk the directory tree
            for root, dirs, files in os.walk(directory_path):
                for file in files:
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, directory_path)

                    # Check if file should be included
                    include_file = any(fnmatch.fnmatch(rel_path, pattern) for pattern in include_patterns)

                    # Check if file should be excluded
                    exclude_file = any(fnmatch.fnmatch(rel_path, pattern) for pattern in exclude_patterns)

                    if include_file and not exclude_file:
                        tar.add(full_path, arcname=rel_path)

        return tarball_path
    except Exception as e:
        # Clean up on error
        if os.path.exists(tarball_path):
            os.unlink(tarball_path)
        raise RuntimeError(f"Failed to package directory: {str(e)}")
```

You can then update the tool schema to include these pattern parameters:

```python
"file_include_patterns": {
    "type": "array",
    "description": "Glob patterns for files to include",
    "items": {"type": "string"},
    "default": ["**/*"]
},
"file_exclude_patterns": {
    "type": "array",
    "description": "Glob patterns for files to exclude",
    "items": {"type": "string"},
    "default": ["node_modules/**", ".git/**"]
}
```

This allows for more precise control over which files are included in the application.
