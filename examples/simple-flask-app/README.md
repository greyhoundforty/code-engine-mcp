# Simple Flask Test App

A minimal Flask application for testing IBM Code Engine MCP Server deployment workflows.

## Local Testing

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
python app.py
```

Visit http://localhost:8080 to see the app running.

## Test with Docker

```bash
# Build the image
docker build -t test-flask-app:latest .

# Run locally
docker run -p 8080:8080 test-flask-app:latest
```

## Deploy to Code Engine

Use the IBM Code Engine MCP Server from Claude Desktop or Claude Code to deploy this app. See the parent README for detailed instructions.
