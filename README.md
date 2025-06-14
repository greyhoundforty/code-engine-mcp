# IBM Code Engine MCP Server

A Model Context Protocol (MCP) server for interacting with IBM Code Engine resources. This server provides tools to list and inspect Code Engine projects, applications, revisions, domain mappings, and secrets.

## Features

**Iteration 1** focuses on read-only operations:
- ✅ List all Code Engine projects
- ✅ List applications in a project
- ✅ Get application details
- ✅ List application revisions
- ✅ Get revision details
- ✅ List domain mappings
- ✅ Get domain mapping details
- ✅ List secrets (with masked sensitive data)
- ✅ Get secret details (with masked sensitive data)

**Future iterations** will add:
- 🚧 Create applications and secrets
- 🚧 Update application configurations
- 🚧 Manage builds and deployments

## Prerequisites

- Python 3.10 or later
- [mise](https://github.com/jdx/mise) task runner
- IBM Cloud account with Code Engine access
- IBM Cloud API key with Code Engine permissions

## Setup

1. **Clone and setup environment:**
   ```bash
   git clone <your-repo>
   cd <project-directory>
   mise install
   ```

2. **Install dependencies:**
   ```bash
   mise run uv:reqs
   ```

3. **Set your IBM Cloud API key:**
   ```bash
   export IBMCLOUD_API_KEY="your-api-key-here"
   ```

4. **Test the setup:**
   ```bash
   # Test MCP library imports
   mise run test:mcp
   
   # Test InitializationOptions fix
   mise run test:init
   
   # Test Code Engine connectivity
   mise run test:client
   
   # Test all server versions
   mise run test:servers
   
   # Run complete test suite
   mise run test:all
   ```

5. **Run the server:**
   ```bash
   # Auto-detect and run best server version
   mise run run:best
   
   # Or manually test specific versions
   python ce_mcp_server_v3.py
   ```

## Usage

### Choosing the Right Server Version

The project includes three server implementations to handle MCP library compatibility:

1. **`ce_mcp_server_v3.py`** - Minimal implementation (recommended first try)
2. **`ce_mcp_server_v2.py`** - Alternative with multiple startup methods
3. **`ce_mcp_server.py`** - Original implementation

Run `mise run test:servers` to see which versions work with your MCP library.

### Development Mode

Run the server directly in development:
```bash
# Try the minimal server first
python ce_mcp_server_v3.py

# Or test all versions to see which works
mise run test:servers
```

### Docker Mode

Build and run in Docker (defaults to minimal v3 server):
```bash
# Build the image
mise run docker:build

# Run with default server (v3)
mise run docker:run

# Or specify a different server version
docker run -e MCP_SERVER_FILE="ce_mcp_server_v2.py" -e IBMCLOUD_API_KEY="$IBMCLOUD_API_KEY" your-image

# Check logs
mise run docker:logs

# Stop the container
mise run docker:stop
```

## Available Tools

The MCP server provides the following tools:

### Project Management
- `list_projects` - List all Code Engine projects
- Parameters: `limit` (optional, default: 100)

### Application Management
- `list_applications` - List applications in a project
- `get_application` - Get detailed application information
- `list_app_revisions` - List revisions for an application
- `get_app_revision` - Get detailed revision information

### Domain Management
- `list_domain_mappings` - List domain mappings in a project
- `get_domain_mapping` - Get detailed domain mapping information

### Secret Management
- `list_secrets` - List secrets in a project (sensitive data masked)
- `get_secret` - Get detailed secret information (sensitive data masked)

## Configuration

### Environment Variables

- `IBMCLOUD_API_KEY` - **Required** - Your IBM Cloud API key
- `IBMCLOUD_REGION` - Optional - IBM Cloud region (default: us-south)
- `LOG_LEVEL` - Optional - Logging level (default: INFO)

### Supported Regions

- `us-south` (default)
- `us-east`
- `eu-gb`
- `eu-de`
- `jp-tok`
- `au-syd`

## Development Tasks

| Command | Description |
|---------|-------------|
| `mise run dev` | Setup development environment |
| `mise run test:all` | Run complete test suite |
| `mise run test:mcp` | Test MCP library compatibility |
| `mise run test:init` | Test InitializationOptions fix |
| `mise run test:client` | Test Code Engine connectivity |
| `mise run test:servers` | Test all server versions |
| `mise run run:best` | Auto-run best working server |
| `mise run quality` | Run all code quality checks |
| `mise run format` | Format code with black |
| `mise run lint` | Run flake8 linting |
| `mise run docker:build` | Build Docker image |
| `mise run docker:run` | Run container |
| `mise run clean` | Clean up artifacts |

## Project Structure

```
├── ce_mcp_server.py        # Original MCP server implementation
├── ce_mcp_server_v2.py     # Alternative server with multiple startup methods  
├── ce_mcp_server_v3.py     # Minimal server (recommended)
├── utils.py                # IBM Code Engine SDK utilities
├── test_ce_client.py       # Test script for Code Engine connectivity
├── test_mcp_imports.py     # Test script for MCP library compatibility
├── minimal_mcp_test.py     # Minimal MCP server test
├── requirements.txt        # Python dependencies
├── Dockerfile             # Container configuration
├── mise.toml              # Task runner configuration
└── README.md              # This file
```

## Error Handling

The server includes comprehensive error handling:
- IBM Cloud API authentication errors
- Network connectivity issues
- Invalid project/resource IDs
- Rate limiting and quota errors

All errors are logged and returned as user-friendly messages.

## Security Notes

- Sensitive data in secrets is automatically masked in responses
- API keys are never logged or exposed
- Container runs as non-root user
- No sensitive data is cached or persisted

## Troubleshooting

## Troubleshooting

### Quick Diagnosis

Run the diagnostic test suite to identify issues:

```bash
# Complete diagnostic suite  
mise run test:all

# Test InitializationOptions specifically
mise run test:init

# Just test MCP library compatibility
mise run test:mcp

# Test all server versions
mise run test:servers

# Test Code Engine connectivity
mise run test:client

# Auto-run best working server
mise run run:best
```

### MCP Library Issues

**InitializationOptions Missing `capabilities` Field:**
```
1 validation error for InitializationOptions
capabilities
  Field required [type=missing, input_value={'server_name': 'test', 'server_version': '1.0.0'}, input_type=dict]
```
**Solution:** ✅ **FIXED** - All servers now include the required `capabilities={}` field.

**Server.run() Missing Required Argument:**
```
TypeError: Server.run() missing 1 required positional argument: 'initialization_options'
```
**Solution:** ✅ **FIXED** - All servers now properly create and pass `InitializationOptions`.

**TaskGroup Errors:**
```
ExceptionGroup: unhandled errors in a TaskGroup (1 sub-exception)
```
**Solution:** This was caused by the InitializationOptions issues above. Should now be resolved.

### Server Version Comparison

| Version | Description | Best For |
|---------|-------------|----------|
| `v3` | Minimal, no InitializationOptions | Newer MCP libraries |
| `v2` | Multiple startup methods | Compatibility testing |
| `v1` | Original implementation | Older MCP libraries |

### Docker Usage

```bash
# Use specific server version
docker run -e MCP_SERVER_FILE="ce_mcp_server_v3.py" your-image

# Check which server version container is using
docker run your-image env | grep MCP_SERVER_FILE

# Debug inside container
docker run -it --entrypoint=/bin/bash your-image
python test_mcp_imports.py
```

### Common Issues

1. **"Code Engine client not initialized"**
   - Check that `IBMCLOUD_API_KEY` is set
   - Verify your API key has Code Engine permissions

2. **"'Server' object has no attribute 'stdio_server'"**
   - MCP library version issue
   - Try: `pip install --upgrade mcp`
   - Use the alternative server: `ce_mcp_server_v2.py`

3. **"unhandled errors in a TaskGroup"**
   - Check the logs for the underlying exception
   - Try the alternative server implementation
   - Verify all imports work: `mise run test:mcp`

4. **"API error: 403 Forbidden"**
   - Your API key may lack Code Engine access
   - Check your IBM Cloud IAM permissions

5. **"No projects found"**
   - You may not have any Code Engine projects
   - Try creating a project in the IBM Cloud console

6. **Container fails to start**
   - Check logs with `mise run docker:logs`
   - Verify environment variables are set
   - Try different server: `docker run -e MCP_SERVER_FILE="ce_mcp_server_v2.py" ...`

### Getting Help

1. Run the test suite: `mise run test:all`
2. Check the logs for detailed error messages
3. Try the alternative server implementation
4. Verify your IBM Cloud permissions
5. Ensure your API key is valid and not expired

## License

[Your license here]

## Contributing

1. Fork the repository
2. Create a feature branch
3. Run quality checks: `mise run quality`
4. Submit a pull request