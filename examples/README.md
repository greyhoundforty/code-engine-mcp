# Code Engine MCP Server - Example Applications

This directory contains example applications for testing deployment to IBM Code Engine via the MCP server.

## Available Examples

### 1. Simple Flask App (Python)
- **Location**: `simple-flask-app/`
- **Language**: Python 3.12
- **Framework**: Flask
- **Features**:
  - Retro CRT-style web interface
  - Health check endpoint (`/health`)
  - JSON API endpoint (`/api/info`)
  - Environment and hostname display
  - Gunicorn production server

### 2. Simple Go App (Go)
- **Location**: `simple-go-app/`
- **Language**: Go 1.21
- **Framework**: Standard library `net/http`
- **Features**:
  - Matching retro CRT-style interface
  - Health check endpoint (`/health`)
  - JSON API endpoint (`/api/info`)
  - Environment and hostname display
  - Multi-stage Docker build

## Visual Design

Both apps share a consistent retro aesthetic inspired by 1970s-1980s CRT terminals:
- **Dark teal gradient background** (#0a2e2e to #1a4a4a)
- **Bright cyan text** (#00ffcc)
- **Hot pink accent borders** (#ff1493)
- **Monospace typography** (Courier New)
- **Animated glow effects**
- **Pulsing status indicators**

See [COLOR_SCHEME.md](./COLOR_SCHEME.md) for detailed color palette and design specifications.

## Testing Locally

### Python App
```bash
cd simple-flask-app
pip install -r requirements.txt
python app.py
# Visit http://localhost:8080
```

### Go App
```bash
cd simple-go-app
go run main.go
# Visit http://localhost:8080
```

## Docker Testing

### Python App
```bash
cd simple-flask-app
docker build -t test-flask-app:latest .
docker run -p 8080:8080 test-flask-app:latest
```

### Go App
```bash
cd simple-go-app
docker build -t test-go-app:latest .
docker run -p 8080:8080 test-go-app:latest
```

## Deploying to Code Engine

Use the IBM Code Engine MCP Server from Claude Desktop or Claude Code to deploy these apps:

1. Navigate to the app directory in your conversation
2. Use the MCP tools to create a Code Engine application
3. Deploy from local source or build from the Dockerfile

See the main repository README for detailed MCP server setup and deployment instructions.

## Common Endpoints

All example apps provide these endpoints:

- **`/`** - Web interface with visual feedback
- **`/health`** - Health check (returns `{"status": "healthy"}`)
- **`/api/info`** - JSON info about the app (version, environment, hostname, timestamp)

## Environment Variables

All apps support these environment variables:

- **`PORT`** - Server port (default: 8080)
- **`ENVIRONMENT`** - Environment name (default: "development")

## Next Steps

- Deploy to Code Engine using the MCP server
- Customize the apps for your use case
- Use as templates for new applications
- Test Code Engine features (scaling, revisions, etc.)
