# Use specific Python version with security updates
FROM python:3.12-slim-bookworm

# Set labels for better metadata
LABEL maintainer="ryantiffany@fastmail.com"
LABEL description="IBM Code Engine MCP Server"
LABEL version="1.0.0"

# Set working directory
WORKDIR /app

# Install system dependencies in a single layer
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libc6-dev \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user early
RUN useradd -m -u 1000 mcpuser \
    && mkdir -p /app \
    && chown -R mcpuser:mcpuser /app

# Switch to non-root user for dependency installation
USER mcpuser

# Set up Python path and virtual environment
ENV PATH="/home/mcpuser/.local/bin:$PATH"
ENV PYTHONPATH="/app:$PYTHONPATH"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Copy requirements first for better caching
COPY --chown=mcpuser:mcpuser requirements.txt .

# Install Python dependencies as non-root user
RUN pip install --user --no-cache-dir -r requirements.txt

# Copy application code
COPY --chown=mcpuser:mcpuser ce_mcp_server.py .
COPY --chown=mcpuser:mcpuser utils.py .
COPY --chown=mcpuser:mcpuser ce_mcp_server_v2.py .

# Add health check script
COPY --chown=mcpuser:mcpuser healthcheck.py . 

# Set environment variables
ENV MCP_SERVER_NAME="ibm-code-engine-mcp"
ENV LOG_LEVEL="INFO"
ENV MCP_SERVER_FILE="ce_mcp_server_v2.py"

# Add health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python /app/healthcheck.py

# The MCP server uses stdio, so we don't expose ports
# Use exec form for better signal handling
# Allow override of server file via environment variable
ENTRYPOINT ["sh", "-c", "python -u ${MCP_SERVER_FILE}"]

# Add signal handlers for graceful shutdown
STOPSIGNAL SIGTERM


