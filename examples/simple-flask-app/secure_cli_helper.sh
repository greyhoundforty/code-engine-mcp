#!/bin/bash
# Secure CLI Helper - Never exposes API key in command history or output
# Usage: source secure_cli_helper.sh

# Load API key from .mcp.env securely
if [ -f "/Users/ryan/.mcp.env" ]; then
    # Read the API key without echoing it
    export IBMCLOUD_API_KEY=$(grep IBMCLOUD_API_KEY /Users/ryan/.mcp.env | cut -d '=' -f2)

    # Login to IBM Cloud (one-time per session)
    ibmcloud login --apikey "$IBMCLOUD_API_KEY" -r us-south -q > /dev/null 2>&1

    if [ $? -eq 0 ]; then
        echo "✅ Authenticated to IBM Cloud securely"
        echo "🔒 API key loaded from .mcp.env (not displayed)"

        # Unset the variable so it's not in the environment
        unset IBMCLOUD_API_KEY
    else
        echo "❌ Authentication failed"
        exit 1
    fi
else
    echo "❌ .mcp.env file not found at /Users/ryan/.mcp.env"
    exit 1
fi

# Now you can run ibmcloud commands without exposing the key:
# ibmcloud ce project list
# ibmcloud ce app create --name myapp --build-source . --port 8080
