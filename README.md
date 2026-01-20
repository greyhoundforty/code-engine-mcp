# IBM Code Engine MCP Server

A Model Context Protocol (MCP) server for IBM Cloud Code Engine. Enables natural language deployment and management of applications via Claude Desktop or Claude Code.

## Features

- **Natural language deployment** - "Deploy this app to Code Engine on port 8080"
- **Build from source** - Automatic packaging, building, and deployment
- **Complete management** - Projects, applications, builds, jobs, secrets
- **Secure by design** - API keys isolated in Docker container
- **22 MCP tools** - Full Code Engine API coverage

## Quick Start

### Prerequisites

- Docker Desktop
- IBM Cloud account with Code Engine access
- IBM Cloud API key ([create one](https://cloud.ibm.com/iam/apikeys))

### 1. Build the Docker Image

```bash
git clone https://github.com/greyhoundforty/code-engine-mcp
cd code-engine-mcp
docker build -t code-engine-mcp:latest .
```

### 2. Configure API Key

Create `~/.mcp.env`:
```bash
IBMCLOUD_API_KEY=your-api-key-here
```

Secure the file:
```bash
chmod 600 ~/.mcp.env
```

### 3. Configure Claude Desktop

Add to your Claude Desktop configuration:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "ibm-code-engine": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "--env-file", "/Users/your-username/.mcp.env",
        "code-engine-mcp:latest"
      ]
    }
  }
}
```

Replace `/Users/your-username/.mcp.env` with your actual path.

### 4. Restart Claude Desktop

The MCP server will be available for use.

## Usage

### Deploy from Source

Navigate to your project directory with a Dockerfile:

```
"Deploy this app to Code Engine on port 8080"
```

Claude will automatically:
1. Package your source code
2. Create a build run
3. Build the Docker image
4. Deploy to Code Engine
5. Return the endpoint URL

### Find Projects

```
"Find my Code Engine project named rst-ce-dev"
```

### List Applications

```
"List all applications in project dts-account-project"
```

### Get Application Details

```
"Show me details for app myapp"
```

### Scale Applications

```
"Scale myapp to minimum 2 instances"
```

## Available Tools

The MCP server provides **22 tools** across 6 categories for complete Code Engine management:

### Project Management (2 tools)
- `list_projects` - List all Code Engine projects
- `find_project_by_name` - Find project by name with optional resource group filter

### Application Management (7 tools)
- `list_applications` - List applications in a project
- `get_application` - Get application details
- `create_application` - Create app from pre-built image
- `update_application` - Update app configuration
- `create_app_from_source` - Deploy from source code (build + deploy)
- `list_app_revisions` - List application revisions
- `get_app_revision` - Get revision details

### Build Management (5 tools)
- `create_build` - Create build configuration
- `list_builds` - List build configurations
- `create_build_run` - Execute a build
- `get_build_run` - Get build run status
- `list_build_runs` - List build runs

### Job Management (4 tools)
- `list_jobs` - List batch jobs
- `get_job` - Get job details
- `list_job_runs` - List job runs
- `get_job_run` - Get job run details

### Domain Management (2 tools)
- `list_domain_mappings` - List custom domain mappings
- `get_domain_mapping` - Get domain mapping details

### Secret Management (2 tools)
- `list_secrets` - List secrets (data masked)
- `get_secret` - Get secret details (data masked)

All tools return formatted summaries and raw JSON for flexibility.

**📖 For detailed documentation of all tools including parameters, examples, and usage patterns, see [TOOLS.md](TOOLS.md)**

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `IBMCLOUD_API_KEY` | Yes | - | IBM Cloud API key |
| `IBMCLOUD_REGION` | No | `us-south` | IBM Cloud region |
| `LOG_LEVEL` | No | `INFO` | Logging level |

### Supported Regions

- `us-south` (Dallas)
- `us-east` (Washington DC)
- `eu-gb` (London)
- `eu-de` (Frankfurt)
- `jp-tok` (Tokyo)
- `au-syd` (Sydney)

## Security

- API keys loaded via Docker `--env-file` (never in command history)
- Container runs as non-root user
- Ephemeral containers (`--rm` flag)
- Secrets automatically masked in responses
- No credential caching

## Project Structure

```
code-engine-mcp/
├── ce_mcp_server_v3.py      # MCP server implementation (22 tools)
├── ce_push.py                # Build-source deployment CLI
├── utils.py                  # Code Engine SDK wrapper
├── Dockerfile                # Container definition
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── TOOLS.md                  # Detailed tool documentation
└── examples/
    ├── simple-flask-app/     # Example Flask application
    └── simple-go-app/        # Example Go application
```

## Development

### Run Server Locally

```bash
export IBMCLOUD_API_KEY=your-api-key
python ce_mcp_server_v3.py
```

### Rebuild Docker Image

```bash
docker build -t code-engine-mcp:latest .
```

### Test Connection

```bash
docker run -i --rm --env-file ~/.mcp.env code-engine-mcp:latest
```

The server should start and show initialization messages.

## Common Use Cases

### Deploy a Flask App

```
"Deploy this Flask app to Code Engine project dts-account-project on port 8080 with minimum 2 instances"
```

### Monitor Build Progress

```
"Show me the status of build run myapp-run-123"
```

### List All Resources

```
"List all applications in the CDE resource group"
```

### Update Application

```
"Update myapp to use 4G memory and 1 CPU"
```

## Troubleshooting

### MCP Server Not Available

1. Verify Docker is running: `docker ps`
2. Rebuild image: `docker build -t code-engine-mcp:latest .`
3. Restart Claude Desktop

### Authentication Failed

1. Check API key in `~/.mcp.env`
2. Verify API key is valid: `ibmcloud iam oauth-tokens`
3. Ensure file has correct permissions: `chmod 600 ~/.mcp.env`

### Project Not Found

1. List projects to see exact names: `ibmcloud ce project list`
2. Use exact project name in command

### Docker Permission Denied

Ensure Docker daemon is running and you have permissions to run Docker commands.

## Architecture

```
Claude Desktop/Code
      ↓
Natural Language Command
      ↓
MCP Server (Docker)
      ↓
IBM Code Engine API
      ↓
Your Application (deployed)
```

The MCP server translates natural language into Code Engine API calls, handling authentication, error handling, and response formatting.

## Additional Resources

- [IBM Code Engine Documentation](https://cloud.ibm.com/docs/codeengine)
- [Model Context Protocol](https://modelcontextprotocol.io)
- [Claude Desktop](https://claude.ai/download)

For detailed guides and examples, see the project wiki.

## License

MIT License - See LICENSE file for details

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

Ensure all tests pass and code follows existing style.
