# Simple Go Test App

A minimal Go application for testing IBM Code Engine MCP Server deployment workflows.

## Local Testing

```bash
# Run locally
go run main.go
```

Visit http://localhost:8080 to see the app running.

## Test with Docker

```bash
# Build the image
docker build -t test-go-app:latest .

# Run locally
docker run -p 8080:8080 test-go-app:latest
```

## Deploy to Code Engine

Use the IBM Code Engine MCP Server from Claude Desktop or Claude Code to deploy this app. See the parent README for detailed instructions.

## Features

- Retro CRT-style UI matching the McElroy Entertainment System aesthetic
- Health check endpoint at `/health`
- JSON API endpoint at `/api/info`
- Environment information display
- Real-time hostname and timestamp
