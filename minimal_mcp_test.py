#!/usr/bin/env python3
"""
Minimal MCP server test to understand the correct API
"""

import asyncio
import sys
import traceback

async def test_minimal_server():
    """Test minimal MCP server setup"""
    try:
        print("Testing minimal MCP server...")
        
        # Import what we need
        from mcp.server import Server
        import mcp.types as types
        
        # Create server
        server = Server("test-server")
        
        # Add a simple tool
        @server.list_tools()
        async def handle_list_tools():
            return [
                types.Tool(
                    name="test_tool",
                    description="A test tool",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                )
            ]
        
        @server.call_tool()
        async def handle_call_tool(name: str, arguments: dict):
            return [
                types.TextContent(
                    type="text", 
                    text=f"Called tool: {name} with args: {arguments}"
                )
            ]
        
        print("✅ Server setup complete")
        
        # Try to get the stdio server
        try:
            # Method 1: Try direct import
            from mcp.server.stdio import stdio_server
            print("✅ stdio_server imported directly")
            return True
        except ImportError:
            try:
                # Method 2: Try from module
                import mcp.server.stdio
                stdio_server = mcp.server.stdio.stdio_server
                print("✅ stdio_server found in module")
                return True
            except (ImportError, AttributeError):
                try:
                    # Method 3: Check if it's a different name
                    import mcp.server.stdio
                    print(f"Available in mcp.server.stdio: {dir(mcp.server.stdio)}")
                    return False
                except ImportError:
                    print("❌ mcp.server.stdio not available at all")
                    return False
                    
    except Exception as e:
        print(f"❌ Error: {e}")
        traceback.print_exc()
        return False

async def main():
    success = await test_minimal_server()
    if success:
        print("🎉 Minimal MCP test passed!")
    else:
        print("❌ Minimal MCP test failed!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())