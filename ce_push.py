#!/usr/bin/env python3
"""
Code Engine Build-Source Deployment CLI - Direct IBM Cloud CLI Wrapper

This script provides a command-line interface for deploying applications to IBM Cloud
Code Engine using the integrated --build-source option. It wraps the IBM Cloud CLI
to package local source code, build Docker images, and deploy applications in a single
operation.

FEATURES:
  - Deploys from local source directory (packages and uploads source)
  - Builds Docker image using Dockerfile in source directory
  - Deploys application with auto-scaling configuration
  - Stores images in IBM Container Registry
  - Supports project targeting and resource group filtering
  - Custom or auto-generated image names

REQUIREMENTS:
  - IBM Cloud CLI (ibmcloud) must be installed and authenticated
  - Code Engine CLI plugin (ce) must be installed
  - Valid IBM Cloud API key
  - Source directory must contain a Dockerfile
  - Target Code Engine project must exist

USAGE EXAMPLES:
  # Deploy with default project (rst-ce-dev)
  python3 ce_push.py --app-name myapp --port 9090

  # Deploy to specific project
  python3 ce_push.py --app-name myapp --port 8080 --project my-project

  # Deploy with custom image name
  python3 ce_push.py --app-name myapp --port 8080 --image myapp:v1 --namespace rtiffany

  # Deploy with resource group filtering
  python3 ce_push.py --app-name myapp --port 3000 --resource-group CDE

  # Deploy from specific directory
  cd examples/simple-go-app
  python3 ../../ce_push.py --app-name simple-go-app --port 8080

COMMAND-LINE ARGUMENTS:
  --app-name (required): Name of the application to create
  --port (default: 8080): Port the application listens on
  --project (default: rst-ce-dev): Code Engine project name or ID
  --region (default: us-south): IBM Cloud region
  --image: Custom image name (stored in private.us.icr.io/namespace/)
  --namespace: Registry namespace for custom image
  --resource-group: Resource group to filter/target projects

DEPLOYMENT PROCESS:
  1. Authenticates with IBM Cloud (if not already authenticated)
  2. Targets the specified Code Engine project
  3. Packages source files from current directory
  4. Uploads source to Code Engine
  5. Builds Docker image using Dockerfile
  6. Pushes image to IBM Container Registry
  7. Deploys application with specified configuration
  8. Returns application URL

OUTPUT:
  The script provides detailed logging of each step and returns:
  - Build status and progress
  - Generated or custom image name
  - Application deployment status
  - Public application URL

RELATED TOOLS:
  - MCP Server Tool: create_app_from_source (calls this script)
  - IBM Cloud CLI: ibmcloud ce app create --build-source
  - See TOOLS.md for comprehensive MCP tool documentation

TROUBLESHOOTING:
  If deployment fails, check:
  - IBM Cloud CLI is installed: ibmcloud --version
  - Code Engine plugin is installed: ibmcloud plugin list
  - Authenticated: ibmcloud login
  - Project exists: ibmcloud ce project list
  - Dockerfile exists in source directory
"""

import argparse
import os
import sys
import logging
import subprocess
import json
from typing import Optional
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CodeEngineBuildSourceDeployer:
    """
    Handles Code Engine application deployment using integrated build-source.
    
    Supports:
    - Resource group filtering for project discovery
    - Project targeting before deployment
    - Auto-generated or custom image names in private registry
    """

    def __init__(
        self,
        app_name: str,
        port: int = 8080,
        project: str = "rst-ce-dev",
        region: str = "us-south",
        image_name: Optional[str] = None,
        namespace: Optional[str] = None,
        resource_group: Optional[str] = None,
    ):
        """
        Initialize the Code Engine Build-Source deployer.
        
        Args:
            app_name: Name of the application
            port: Port the application listens on (default: 8080)
            project: Code Engine project name or ID (default: rst-ce-dev)
            region: IBM Cloud region (default: us-south)
            image_name: Optional custom image name (without private. prefix)
            namespace: Optional registry namespace for image (default: auto-generated)
            resource_group: Optional resource group to filter projects
        """
        self.app_name = app_name
        self.port = port
        self.project = project
        self.region = region
        self.source_dir = Path.cwd()
        self.api_key = os.getenv("IBMCLOUD_API_KEY")
        self.resource_group = resource_group
        
        # Construct image name if provided
        self.image_name = None
        if image_name:
            # Ensure private. prefix
            if not image_name.startswith('private.us.icr.io'):
                if namespace:
                    self.image_name = f"private.us.icr.io/{namespace}/{image_name}:latest"
                else:
                    self.image_name = f"private.us.icr.io/{image_name}:latest"
            else:
                self.image_name = image_name
        
        self._validate_setup()
        self._print_banner()

    def _validate_setup(self):
        """Validate required setup before deployment."""
        # Check Dockerfile exists
        if not (self.source_dir / "Dockerfile").exists():
            logger.error(f"❌ Dockerfile not found in {self.source_dir}")
            sys.exit(1)
        
        # Check ibmcloud CLI available
        import shutil
        if not shutil.which("ibmcloud"):
            logger.error("❌ ibmcloud CLI not found. Please install: https://cloud.ibm.com/docs/cli")
            sys.exit(1)
        
        # Check API key
        if not self.api_key:
            logger.error("❌ IBMCLOUD_API_KEY environment variable not set")
            sys.exit(1)

    def _print_banner(self):
        """Print deployment banner with configuration."""
        print("\n" + "="*70)
        print("🚀 Code Engine Build-Source Deployment")
        print("="*70)
        print(f"📱 App Name:       {self.app_name}")
        print(f"🔌 Port:           {self.port}")
        print(f"📦 Project:        {self.project}")
        print(f"🌍 Region:         {self.region}")
        if self.resource_group:
            print(f"👥 Resource Group: {self.resource_group}")
        print(f"📂 Source Path:    {self.source_dir}")
        if self.image_name:
            print(f"🖼️  Image:          {self.image_name}")
        else:
            print(f"🖼️  Image:          (auto-generated by Code Engine)")
        print("="*70 + "\n")

    def _run_command(self, cmd: list, description: str = "") -> bool:
        """
        Execute a shell command and return success/failure.
        
        Args:
            cmd: Command as list of strings
            description: Human-readable description
            
        Returns:
            True if successful, False otherwise
        """
        if description:
            logger.info(f"⏳ {description}...")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
            )
            
            if result.returncode == 0:
                if description:
                    logger.info(f"✅ {description}")
                return True
            else:
                logger.error(f"❌ Command failed: {' '.join(cmd)}")
                if result.stderr:
                    logger.error(f"   Error: {result.stderr}")
                if result.stdout:
                    logger.info(f"   Output: {result.stdout}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error executing command: {e}")
            return False

    def get_project_id(self) -> Optional[str]:
        """
        Resolve project name to project ID, optionally filtering by resource group.
        
        Returns:
            Project ID if found, None otherwise
        """
        try:
            # Build command to list projects
            cmd = [
                "ibmcloud",
                "ce",
                "project",
                "list",
                "--output", "json",
            ]
            
            logger.info(f"⏳ Resolving project '{self.project}'...")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
            )
            
            if result.returncode != 0:
                logger.error(f"❌ Failed to list projects:")
                logger.error(result.stderr)
                return None
            
            projects = json.loads(result.stdout)
            
            for project in projects.get('projects', []):
                if project.get('name') == self.project or project.get('id') == self.project:
                    project_id = project.get('id')
                    logger.info(f"✅ Found project '{self.project}': {project_id}")
                    return project_id
            
            logger.error(f"❌ Project '{self.project}' not found")
            return None
            
        except json.JSONDecodeError:
            logger.error("❌ Failed to parse project list output")
            return None
        except Exception as e:
            logger.error(f"❌ Error resolving project: {e}")
            return None

    def target_project(self) -> bool:
        """
        Target the Code Engine project in the CLI context.
        
        Returns:
            True if successful, False otherwise
        """
        cmd = [
            "ibmcloud",
            "ce",
            "project",
            "select",
            "--name", self.project,
        ]
        
        return self._run_command(
            cmd,
            description=f"Targeting Code Engine project '{self.project}'"
        )

    def deploy(self) -> bool:
        """
        Execute deployment using Code Engine build-source feature.
        
        Returns:
            True if deployment successful, False otherwise
        """
        # Step 1: Target the project
        if not self.target_project():
            return False
        
        # Step 2: Create the application
        try:
            # Build the ibmcloud ce app create command
            # The project context is already set via project select
            cmd_parts = [
                "ibmcloud",
                "ce",
                "app",
                "create",
                "--name", self.app_name,
                "--build-source", str(self.source_dir),
                "--port", str(self.port),
                "--min-scale", "1",
                "--max-scale", "10",
                "--force",  # Overwrite if exists
            ]
            
            # Add custom image name if provided
            if self.image_name:
                cmd_parts.extend(["--image", self.image_name])
            
            logger.info(f"⏳ Creating application '{self.app_name}'...")
            logger.info(f"   Command: {' '.join(cmd_parts)}")
            
            result = subprocess.run(
                cmd_parts,
                capture_output=True,
                text=True,
            )
            
            if result.returncode != 0:
                logger.error(f"❌ Deployment failed:")
                logger.error(result.stderr)
                return False
            
            # Parse output for endpoint URL
            output = result.stdout
            logger.info(output)
            
            # Extract endpoint URL from output if available
            for line in output.split('\n'):
                if 'https://' in line and 'codeengine.appdomain.cloud' in line:
                    endpoint = line.strip()
                    logger.info(f"\n✅ Application deployed successfully!")
                    logger.info(f"🌐 Endpoint: {endpoint}\n")
                    return True
            
            logger.info(f"\n✅ Application created successfully!")
            logger.info(f"⏳ Build and deployment in progress...")
            logger.info(f"   Run: ibmcloud ce app get --name {self.app_name}")
            logger.info(f"   To check status and get the endpoint URL.\n")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error during deployment: {e}")
            return False


def main():
    """Parse arguments and execute deployment."""
    parser = argparse.ArgumentParser(
        description="Deploy to IBM Cloud Code Engine using integrated build-source",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Deploy with default project (rst-ce-dev)
  %(prog)s --app-name myapp --port 9090
  
  # Deploy to specific project
  %(prog)s --app-name myapp --port 8080 --project my-project
  
  # Deploy with custom image name
  %(prog)s --app-name myapp --port 8080 --image myapp:v1 --namespace rtiffany
  
  # Deploy with resource group filtering
  %(prog)s --app-name myapp --port 3000 --resource-group CDE
        """,
    )
    
    parser.add_argument(
        "--app-name",
        required=True,
        help="Name of the application",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Port the application listens on (default: 8080)",
    )
    parser.add_argument(
        "--project",
        default="rst-ce-dev",
        help="Code Engine project name or ID (default: rst-ce-dev)",
    )
    parser.add_argument(
        "--region",
        default="us-south",
        help="IBM Cloud region (default: us-south)",
    )
    parser.add_argument(
        "--image",
        default=None,
        help="Custom image name (e.g., myapp:1). Stored in private.us.icr.io/namespace/",
    )
    parser.add_argument(
        "--namespace",
        default=None,
        help="Registry namespace for image (e.g., rtiffany). Used with --image flag.",
    )
    parser.add_argument(
        "--resource-group",
        default=None,
        help="Resource group to filter/target projects",
    )
    
    args = parser.parse_args()
    
    # Create deployer and execute
    deployer = CodeEngineBuildSourceDeployer(
        app_name=args.app_name,
        port=args.port,
        project=args.project,
        region=args.region,
        image_name=args.image,
        namespace=args.namespace,
        resource_group=args.resource_group,
    )
    
    # Execute deployment
    success = deployer.deploy()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
