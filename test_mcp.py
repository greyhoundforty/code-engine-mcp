#!/usr/bin/env python3
import asyncio
import json
import sys

async def test_mcp_client():
    # Use specific tool and parameters
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "call_tool",
        "params": {
            "name": "list_secrets",
            "arguments": {
                "project_id": "d0a6c45d-8609-4e6a-b652-1075054ea8b1"
            }
        }
    }

    # Serialize the request
    request_str = json.dumps(request) + "\n"

    # Start the MCP server process
    proc = await asyncio.create_subprocess_exec(
        sys.executable, "/app/ce_mcp_server.py",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    # Send the request
    proc.stdin.write(request_str.encode())
    await proc.stdin.drain()

    # Read the response
    response = await proc.stdout.readline()
    response_data = json.loads(response.decode())

    # Print the response
    print(json.dumps(response_data, indent=2))

    # Clean up
    proc.terminate()
    await proc.wait()

if __name__ == "__main__":
    asyncio.run(test_mcp_client())
