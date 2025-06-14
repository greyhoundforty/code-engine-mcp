#!/usr/bin/env python3
"""
Simple test script for IBM Code Engine MCP Server
Tests the Code Engine client functionality
"""

import os
import sys
import logging
from utils import create_code_engine_client, CodeEngineError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_code_engine_client():
    """Test Code Engine client functionality"""
    try:
        # Check for API key
        api_key = os.getenv('IBMCLOUD_API_KEY')
        if not api_key:
            print("❌ ERROR: IBMCLOUD_API_KEY environment variable not set")
            print("Please set it with: export IBMCLOUD_API_KEY='your-api-key'")
            return False
        
        # Test client creation
        print("🔧 Testing Code Engine client creation...")
        client = create_code_engine_client()
        print("✅ Code Engine client created successfully")
        
        # Test listing projects
        print("📋 Testing project listing...")
        projects = client.list_projects(limit=10)
        print(f"✅ Found {len(projects)} projects")
        
        if projects:
            print("\n📝 Project Summary:")
            for i, project in enumerate(projects[:3], 1):  # Show first 3 projects
                print(f"  {i}. {project.get('name', 'Unknown')} ({project.get('id', 'No ID')})")
                print(f"     Region: {project.get('region', 'Unknown')}")
                print(f"     Status: {project.get('status', 'Unknown')}")
            
            if len(projects) > 3:
                print(f"  ... and {len(projects) - 3} more projects")
            
            # Test listing applications in first project
            first_project_id = projects[0].get('id')
            if first_project_id:
                print(f"\n🚀 Testing application listing for project: {first_project_id}")
                apps = client.list_applications(project_id=first_project_id, limit=5)
                print(f"✅ Found {len(apps)} applications")
                
                if apps:
                    print("\n📝 Application Summary:")
                    for i, app in enumerate(apps[:2], 1):  # Show first 2 apps
                        print(f"  {i}. {app.get('name', 'Unknown')}")
                        print(f"     Status: {app.get('status', 'Unknown')}")
                        print(f"     Image: {app.get('image_reference', 'Unknown')}")
                else:
                    print("   No applications found in this project")
        else:
            print("   No projects found in your account")
        
        print("\n🎉 All tests completed successfully!")
        return True
        
    except CodeEngineError as e:
        print(f"❌ Code Engine API error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_environment():
    """Test environment setup"""
    print("🔍 Checking environment setup...")
    
    # Check Python version
    python_version = sys.version_info
    print(f"   Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version < (3, 10):
        print("   ⚠️  Warning: Python 3.10+ recommended")
    else:
        print("   ✅ Python version OK")
    
    # Check required modules
    required_modules = [
        'ibm_code_engine_sdk',
        'ibm_cloud_sdk_core',
        'mcp.server',
        'mcp.types'
    ]
    
    missing_modules = []
    for module in required_modules:
        try:
            __import__(module)
            print(f"   ✅ {module} installed")
        except ImportError:
            print(f"   ❌ {module} NOT installed")
            missing_modules.append(module)
    
    if missing_modules:
        print(f"\n❌ Missing modules: {', '.join(missing_modules)}")
        print("   Install with: mise run uv:reqs")
        return False
    
    # Check environment variables
    env_vars = ['IBMCLOUD_API_KEY']
    for var in env_vars:
        if os.getenv(var):
            print(f"   ✅ {var} is set")
        else:
            print(f"   ❌ {var} is NOT set")
            return False
    
    print("✅ Environment setup complete")
    return True

if __name__ == "__main__":
    print("🧪 IBM Code Engine MCP Server Test Suite")
    print("=" * 50)
    
    # Test environment first
    if not test_environment():
        print("\n❌ Environment tests failed. Please fix issues before continuing.")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    
    # Test Code Engine client
    if test_code_engine_client():
        print("\n🎉 All tests passed! Your Code Engine MCP server is ready to use.")
        print("\n💡 Next steps:")
        print("   1. Build Docker image: mise run docker:build")
        print("   2. Run MCP server: mise run docker:run")
        print("   3. Check logs: mise run docker:logs")
    else:
        print("\n❌ Code Engine tests failed. Please check your configuration.")
        sys.exit(1)