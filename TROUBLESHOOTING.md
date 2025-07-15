# Troubleshooting Guide

## Quick Diagnosis

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

## MCP Library Issues

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

## Server Version Comparison

| Version | Description | Best For |
|---------|-------------|----------|
| `v3` | Minimal, no InitializationOptions | Newer MCP libraries |
| `v2` | Multiple startup methods | Compatibility testing |
| `v1` | Original implementation | Older MCP libraries |

## Docker Usage

```bash
# Use specific server version
docker run -e MCP_SERVER_FILE="ce_mcp_server_v3.py" your-image

# Check which server version container is using
docker run your-image env | grep MCP_SERVER_FILE

# Debug inside container
docker run -it --entrypoint=/bin/bash your-image
python test_mcp_imports.py
```

## Common Issues

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

7. **Claude Desktop not seeing tools**
   - Stop any running containers: `docker stop $(docker ps -q --filter ancestor=code-engine-mcp)`
   - Restart Claude Desktop completely
   - Verify configuration matches exactly
   - Try rebuilding with a new tag: `docker build -t code-engine-mcp:latest .`

## Getting Help

1. Run the test suite: `mise run test:all`
2. Check the logs for detailed error messages
3. Try the alternative server implementation
4. Verify your IBM Cloud permissions
5. Ensure your API key is valid and not expired