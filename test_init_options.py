#!/usr/bin/env python3
"""
Test script to verify InitializationOptions works correctly
"""

import sys
import traceback

def test_initialization_options():
    """Test InitializationOptions creation with proper capabilities"""
    print("🔧 Testing InitializationOptions creation...")
    
    try:
        # Test 1: Try mcp.server.models
        try:
            from mcp.server.models import InitializationOptions
            init_opts = InitializationOptions(
                server_name="test-server",
                server_version="1.0.0",
                capabilities={}  # Required field
            )
            print("  ✅ InitializationOptions from mcp.server.models - SUCCESS")
            print(f"     Created: {init_opts}")
            return True
        except ImportError:
            print("  ❌ mcp.server.models.InitializationOptions not found")
        except Exception as e:
            print(f"  ❌ mcp.server.models.InitializationOptions failed: {e}")
        
        # Test 2: Try mcp.server
        try:
            from mcp.server import InitializationOptions
            init_opts = InitializationOptions(
                server_name="test-server",
                server_version="1.0.0",
                capabilities={}
            )
            print("  ✅ InitializationOptions from mcp.server - SUCCESS")
            print(f"     Created: {init_opts}")
            return True
        except ImportError:
            print("  ❌ mcp.server.InitializationOptions not found")
        except Exception as e:
            print(f"  ❌ mcp.server.InitializationOptions failed: {e}")
        
        # Test 3: Try mcp.types (shouldn't work but let's verify)
        try:
            import mcp.types as types
            if hasattr(types, 'InitializationOptions'):
                init_opts = types.InitializationOptions(
                    server_name="test-server",
                    server_version="1.0.0",
                    capabilities={}
                )
                print("  ✅ InitializationOptions from mcp.types - SUCCESS")
                print(f"     Created: {init_opts}")
                return True
            else:
                print("  ℹ️  InitializationOptions not in mcp.types (expected)")
        except Exception as e:
            print(f"  ❌ mcp.types.InitializationOptions failed: {e}")
        
        print("  ❌ Could not create InitializationOptions from any location")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        traceback.print_exc()
        return False

def test_server_run_signature():
    """Test what Server.run() expects"""
    print("\n🔍 Testing Server.run() signature...")
    
    try:
        from mcp.server import Server
        import inspect
        
        # Get the signature of Server.run
        signature = inspect.signature(Server.run)
        print(f"  📋 Server.run signature: {signature}")
        
        # Check parameters
        params = list(signature.parameters.keys())
        print(f"  📋 Parameters: {params}")
        
        # Check if initialization_options is required
        init_param = signature.parameters.get('initialization_options')
        if init_param:
            print(f"  📋 initialization_options parameter: {init_param}")
            if init_param.default == inspect.Parameter.empty:
                print("  ⚠️  initialization_options is REQUIRED (no default value)")
            else:
                print(f"  ℹ️  initialization_options has default: {init_param.default}")
        else:
            print("  ❌ initialization_options parameter not found")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error inspecting Server.run: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 InitializationOptions Fix Test")
    print("=" * 40)
    
    init_test = test_initialization_options()
    signature_test = test_server_run_signature()
    
    if init_test and signature_test:
        print("\n🎉 InitializationOptions tests passed!")
        print("\n💡 Next steps:")
        print("  1. Try running: python ce_mcp_server_v3.py")
        print("  2. If it works, rebuild Docker: mise run docker:build")
    else:
        print("\n❌ Some tests failed. The InitializationOptions issue may not be fully resolved.")

if __name__ == "__main__":
    main()