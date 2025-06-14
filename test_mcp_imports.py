#!/usr/bin/env python3
"""
Test script to verify MCP library imports and basic functionality
"""

import sys
import traceback

def test_mcp_imports():
    """Test all required MCP imports"""
    print("🔍 Testing MCP library imports...")
    
    try:
        print("  Testing basic mcp import...")
        import mcp
        print(f"  ✅ mcp version: {getattr(mcp, '__version__', 'unknown')}")
        
        print("  Testing mcp.types...")
        import mcp.types as types
        print(f"  ✅ mcp.types imported")
        
        print("  Testing mcp.server...")
        from mcp.server import Server
        print(f"  ✅ mcp.server.Server imported")
        
        print("  Testing mcp.server.stdio...")
        try:
            import mcp.server.stdio
            print(f"  ✅ mcp.server.stdio imported")
            
            # Test if stdio_server function exists
            if hasattr(mcp.server.stdio, 'stdio_server'):
                print(f"  ✅ stdio_server function found")
            else:
                print(f"  ❌ stdio_server function NOT found")
                print(f"  Available attributes: {dir(mcp.server.stdio)}")
                
        except ImportError as e:
            print(f"  ❌ mcp.server.stdio import failed: {e}")
            
            # Try alternative import
            try:
                print("  Trying alternative import...")
                from mcp.server.stdio import stdio_server
                print(f"  ✅ stdio_server imported directly")
            except ImportError as e2:
                print(f"  ❌ Direct stdio_server import failed: {e2}")
        
        print("  Testing types...")
        try:
            tool = types.Tool(
                name="test",
                description="test tool",
                inputSchema={"type": "object", "properties": {}}
            )
            print(f"  ✅ types.Tool works")
        except Exception as e:
            print(f"  ❌ types.Tool failed: {e}")
            
        try:
            content = types.TextContent(type="text", text="test")
            print(f"  ✅ types.TextContent works")
        except Exception as e:
            print(f"  ❌ types.TextContent failed: {e}")
            
        try:
            # Try different possible locations for InitializationOptions
            from mcp.server.models import InitializationOptions
            init_opts = InitializationOptions(
                server_name="test",
                server_version="1.0.0"
            )
            print(f"  ✅ InitializationOptions found in mcp.server.models")
        except ImportError:
            try:
                from mcp.server import InitializationOptions
                init_opts = InitializationOptions(
                    server_name="test",
                    server_version="1.0.0"
                )
                print(f"  ✅ InitializationOptions found in mcp.server")
            except ImportError:
                try:
                    # Try just running without InitializationOptions
                    print(f"  ⚠️  InitializationOptions not found - may not be required")
                except Exception as e:
                    print(f"  ❌ InitializationOptions failed: {e}")
        except Exception as e:
            print(f"  ❌ InitializationOptions failed: {e}")
            
        return True
        
    except Exception as e:
        print(f"❌ MCP import failed: {e}")
        print(f"Full traceback:\n{traceback.format_exc()}")
        return False

def test_server_creation():
    """Test basic server creation"""
    print("\n🏗️  Testing MCP server creation...")
    
    try:
        from mcp.server import Server
        
        server = Server("test-server")
        print("  ✅ Server created successfully")
        
        # Test decorators
        @server.list_tools()
        async def test_list_tools():
            return []
            
        @server.call_tool()
        async def test_call_tool(name: str, arguments: dict):
            return []
            
        print("  ✅ Server decorators work")
        return True
        
    except Exception as e:
        print(f"  ❌ Server creation failed: {e}")
        print(f"Full traceback:\n{traceback.format_exc()}")
        return False

def main():
    """Main test function"""
    print("🧪 MCP Library Test Suite")
    print("=" * 40)
    
    # Test imports
    import_success = test_mcp_imports()
    
    if not import_success:
        print("\n❌ Import tests failed. Cannot proceed with server tests.")
        sys.exit(1)
    
    # Test server creation
    server_success = test_server_creation()
    
    if import_success and server_success:
        print("\n🎉 All MCP tests passed!")
        print("\n💡 Suggested next steps:")
        print("  1. Check your ce_mcp_server.py imports")
        print("  2. Run: python ce_mcp_server.py")
        print("  3. Check for any remaining errors")
    else:
        print("\n❌ Some tests failed. Please check your MCP installation.")
        print("\n🔧 Try:")
        print("  pip install --upgrade mcp")
        print("  pip list | grep mcp")

if __name__ == "__main__":
    main()