# IBM Code Engine MCP Server

A Model Context Protocol (MCP) server for interacting with IBM Code Engine resources. This server provides tools to list and inspect Code Engine projects, applications, revisions, domain mappings, and secrets.

## Available MCP Tools

This server provides **13 comprehensive tools** for IBM Code Engine management:

### Project Management
- **`list_projects`** - List all Code Engine projects in your account

### Application Management  
- **`list_applications`** - List applications in a specific project
- **`get_application`** - Get detailed application information
- **`list_app_revisions`** - List revisions for a specific application
- **`get_app_revision`** - Get detailed revision information

### Batch Job Management
- **`list_jobs`** - List batch jobs in a specific project
- **`get_job`** - Get detailed job information
- **`list_job_runs`** - List job runs for a specific job or all jobs in a project
- **`get_job_run`** - Get detailed job run information

### Domain Management
- **`list_domain_mappings`** - List domain mappings in a project
- **`get_domain_mapping`** - Get detailed domain mapping information

### Secret Management
- **`list_secrets`** - List secrets in a project (sensitive data automatically masked)
- **`get_secret`** - Get detailed secret information (sensitive data automatically masked)

All tools include comprehensive error handling and return both formatted summaries and raw JSON data for maximum flexibility.

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
   python ce_mcp_server_v3.py
   ```

## Usage

### Claude Desktop Integration

For use with Claude Desktop, build and configure the Docker container:

```bash
# Build the image
docker build -t code-engine-mcp:latest .
```

**Configure Claude Desktop:**

1. **Get your IBM Cloud API Key:**
   - Log into [IBM Cloud Console](https://cloud.ibm.com)
   - Navigate to "Manage" → "Access (IAM)" → "API keys"
   - Create a new API key with Code Engine access

2. **Create Environment File:**
   Create a `.mcp.env` file (recommended location: `~/.mcp.env`):
   ```bash
   IBMCLOUD_API_KEY=your-actual-api-key-here
   ```

3. **Add MCP Server Configuration:**
   
   **Option A: Using Environment File (Recommended)**
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

   **Option B: Direct API Key**
   ```json
   {
     "mcpServers": {
       "ibm-code-engine": {
         "command": "docker",
         "args": [
           "run", "-i", "--rm",
           "-e", "IBMCLOUD_API_KEY=your-actual-api-key-here",
           "-e", "LOG_LEVEL=INFO",
           "code-engine-mcp:latest"
         ]
       }
     }
   }
   ```

4. **Restart Claude Desktop** to load the new MCP server.

**Important:** 
- Replace `/Users/your-username/.mcp.env` with the actual path to your environment file
- The `${VARIABLE}` substitution syntax is not supported in Claude Desktop configurations
- Using an environment file (Option A) is more secure and easier to manage

### Development Mode

Run the server directly for development:
```bash
python ce_mcp_server_v3.py
```

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

For detailed troubleshooting steps and common issues, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

## License

[Your license here]

## Contributing

1. Fork the repository
2. Create a feature branch
3. Run quality checks: `mise run quality`
4. Submit a pull request