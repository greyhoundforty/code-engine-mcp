"""
Utility functions for IBM Code Engine MCP Server
Handles authentication, client setup, and resource operations
"""

import json
import logging
import os
from typing import List, Dict, Any, Optional
from ibm_code_engine_sdk.code_engine_v2 import (
    CodeEngineV2,
    ProjectsPager,
    AppsPager,
    AppRevisionsPager,
    DomainMappingsPager,
    SecretsPager
)
from ibm_cloud_sdk_core import ApiException
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

# Set up logging
logger = logging.getLogger(__name__)

class CodeEngineError(Exception):
    """Custom exception for Code Engine operations"""
    pass

class CodeEngineClient:
    """Wrapper class for IBM Code Engine operations"""
    
    def __init__(self, api_key: str, region: str = "us-south"):
        """
        Initialize Code Engine client
        
        Args:
            api_key: IBM Cloud API key
            region: IBM Cloud region (default: us-south)
        """
        self.api_key = api_key
        self.region = region
        self.service = None
        self._setup_client()
    
    def _setup_client(self):
        """Set up the Code Engine service client"""
        try:
            authenticator = IAMAuthenticator(apikey=self.api_key)
            self.service = CodeEngineV2(authenticator=authenticator)
            service_url = f'https://api.{self.region}.codeengine.cloud.ibm.com/v2'
            self.service.set_service_url(service_url)
            logger.info(f"Code Engine client initialized for region: {self.region}")
        except Exception as e:
            raise CodeEngineError(f"Failed to initialize Code Engine client: {str(e)}")
    
    def list_projects(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        List all Code Engine projects
        
        Args:
            limit: Maximum number of projects to return per page
            
        Returns:
            List of project dictionaries
        """
        try:
            all_results = []
            pager = ProjectsPager(
                client=self.service,
                limit=limit,
            )
            
            while pager.has_next():
                next_page = pager.get_next()
                if next_page is not None:
                    all_results.extend(next_page)
            
            logger.info(f"Retrieved {len(all_results)} projects")
            return all_results
            
        except ApiException as e:
            logger.error(f"API error listing projects: {e}")
            raise CodeEngineError(f"Failed to list projects: {e}")
        except Exception as e:
            logger.error(f"Unexpected error listing projects: {e}")
            raise CodeEngineError(f"Unexpected error: {e}")
    
    def list_applications(self, project_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        List applications in a specific project
        
        Args:
            project_id: Code Engine project ID
            limit: Maximum number of apps to return per page
            
        Returns:
            List of application dictionaries
        """
        try:
            all_results = []
            pager = AppsPager(
                client=self.service,
                project_id=project_id,
                limit=limit,
            )
            
            while pager.has_next():
                next_page = pager.get_next()
                if next_page is not None:
                    all_results.extend(next_page)
            
            logger.info(f"Retrieved {len(all_results)} applications for project {project_id}")
            return all_results
            
        except ApiException as e:
            logger.error(f"API error listing applications: {e}")
            raise CodeEngineError(f"Failed to list applications: {e}")
        except Exception as e:
            logger.error(f"Unexpected error listing applications: {e}")
            raise CodeEngineError(f"Unexpected error: {e}")
    
    def get_application(self, project_id: str, app_name: str) -> Dict[str, Any]:
        """
        Get details of a specific application
        
        Args:
            project_id: Code Engine project ID
            app_name: Name of the application
            
        Returns:
            Application details dictionary
        """
        try:
            response = self.service.get_app(
                project_id=project_id,
                name=app_name,
            )
            app = response.get_result()
            logger.info(f"Retrieved application {app_name} from project {project_id}")
            return app
            
        except ApiException as e:
            logger.error(f"API error getting application: {e}")
            raise CodeEngineError(f"Failed to get application {app_name}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error getting application: {e}")
            raise CodeEngineError(f"Unexpected error: {e}")
    
    def list_app_revisions(self, project_id: str, app_name: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        List revisions for a specific application
        
        Args:
            project_id: Code Engine project ID
            app_name: Name of the application
            limit: Maximum number of revisions to return per page
            
        Returns:
            List of application revision dictionaries
        """
        try:
            all_results = []
            pager = AppRevisionsPager(
                client=self.service,
                project_id=project_id,
                app_name=app_name,
                limit=limit,
            )
            
            while pager.has_next():
                next_page = pager.get_next()
                if next_page is not None:
                    all_results.extend(next_page)
            
            logger.info(f"Retrieved {len(all_results)} revisions for app {app_name}")
            return all_results
            
        except ApiException as e:
            logger.error(f"API error listing app revisions: {e}")
            raise CodeEngineError(f"Failed to list app revisions: {e}")
        except Exception as e:
            logger.error(f"Unexpected error listing app revisions: {e}")
            raise CodeEngineError(f"Unexpected error: {e}")
    
    def get_app_revision(self, project_id: str, app_name: str, revision_name: str) -> Dict[str, Any]:
        """
        Get details of a specific application revision
        
        Args:
            project_id: Code Engine project ID
            app_name: Name of the application
            revision_name: Name of the revision
            
        Returns:
            Application revision details dictionary
        """
        try:
            response = self.service.get_app_revision(
                project_id=project_id,
                app_name=app_name,
                name=revision_name,
            )
            app_revision = response.get_result()
            logger.info(f"Retrieved revision {revision_name} for app {app_name}")
            return app_revision
            
        except ApiException as e:
            logger.error(f"API error getting app revision: {e}")
            raise CodeEngineError(f"Failed to get app revision {revision_name}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error getting app revision: {e}")
            raise CodeEngineError(f"Unexpected error: {e}")
    
    def list_domain_mappings(self, project_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        List domain mappings in a specific project
        
        Args:
            project_id: Code Engine project ID
            limit: Maximum number of domain mappings to return per page
            
        Returns:
            List of domain mapping dictionaries
        """
        try:
            all_results = []
            pager = DomainMappingsPager(
                client=self.service,
                project_id=project_id,
                limit=limit,
            )
            
            while pager.has_next():
                next_page = pager.get_next()
                if next_page is not None:
                    all_results.extend(next_page)
            
            logger.info(f"Retrieved {len(all_results)} domain mappings for project {project_id}")
            return all_results
            
        except ApiException as e:
            logger.error(f"API error listing domain mappings: {e}")
            raise CodeEngineError(f"Failed to list domain mappings: {e}")
        except Exception as e:
            logger.error(f"Unexpected error listing domain mappings: {e}")
            raise CodeEngineError(f"Unexpected error: {e}")
    
    def get_domain_mapping(self, project_id: str, domain_name: str) -> Dict[str, Any]:
        """
        Get details of a specific domain mapping
        
        Args:
            project_id: Code Engine project ID
            domain_name: Name of the domain mapping
            
        Returns:
            Domain mapping details dictionary
        """
        try:
            response = self.service.get_domain_mapping(
                project_id=project_id,
                name=domain_name,
            )
            domain_mapping = response.get_result()
            logger.info(f"Retrieved domain mapping {domain_name} from project {project_id}")
            return domain_mapping
            
        except ApiException as e:
            logger.error(f"API error getting domain mapping: {e}")
            raise CodeEngineError(f"Failed to get domain mapping {domain_name}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error getting domain mapping: {e}")
            raise CodeEngineError(f"Unexpected error: {e}")
    
    def list_secrets(self, project_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        List secrets in a specific project
        
        Args:
            project_id: Code Engine project ID
            limit: Maximum number of secrets to return per page
            
        Returns:
            List of secret dictionaries
        """
        try:
            all_results = []
            pager = SecretsPager(
                client=self.service,
                project_id=project_id,
                limit=limit,
            )
            
            while pager.has_next():
                next_page = pager.get_next()
                if next_page is not None:
                    all_results.extend(next_page)
            
            logger.info(f"Retrieved {len(all_results)} secrets for project {project_id}")
            return all_results
            
        except ApiException as e:
            logger.error(f"API error listing secrets: {e}")
            raise CodeEngineError(f"Failed to list secrets: {e}")
        except Exception as e:
            logger.error(f"Unexpected error listing secrets: {e}")
            raise CodeEngineError(f"Unexpected error: {e}")
    
    def get_secret(self, project_id: str, secret_name: str) -> Dict[str, Any]:
        """
        Get details of a specific secret
        
        Args:
            project_id: Code Engine project ID
            secret_name: Name of the secret
            
        Returns:
            Secret details dictionary
        """
        try:
            response = self.service.get_secret(
                project_id=project_id,
                name=secret_name,
            )
            secret = response.get_result()
            logger.info(f"Retrieved secret {secret_name} from project {project_id}")
            return secret
            
        except ApiException as e:
            logger.error(f"API error getting secret: {e}")
            raise CodeEngineError(f"Failed to get secret {secret_name}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error getting secret: {e}")
            raise CodeEngineError(f"Unexpected error: {e}")


def create_code_engine_client(api_key: Optional[str] = None, region: str = "us-south") -> CodeEngineClient:
    """
    Create and return a Code Engine client
    
    Args:
        api_key: IBM Cloud API key (if not provided, will use IBMCLOUD_API_KEY env var)
        region: IBM Cloud region
        
    Returns:
        CodeEngineClient instance
        
    Raises:
        CodeEngineError: If API key is not provided or client creation fails
    """
    if api_key is None:
        api_key = os.getenv('IBMCLOUD_API_KEY')
    
    if not api_key:
        raise CodeEngineError("IBM Cloud API key not provided. Set IBMCLOUD_API_KEY environment variable or pass api_key parameter.")
    
    return CodeEngineClient(api_key, region)


def format_project_summary(projects: List[Dict[str, Any]]) -> str:
    """
    Format projects list for display
    
    Args:
        projects: List of project dictionaries
        
    Returns:
        Formatted string representation
    """
    if not projects:
        return "No projects found."
    
    summary = f"Found {len(projects)} Code Engine projects:\n\n"
    for project in projects:
        summary += f"• **{project.get('name', 'Unknown')}** ({project.get('id', 'No ID')})\n"
        summary += f"  Region: {project.get('region', 'Unknown')}\n"
        summary += f"  Status: {project.get('status', 'Unknown')}\n"
        summary += f"  Created: {project.get('created_at', 'Unknown')}\n\n"
    
    return summary


def format_apps_summary(apps: List[Dict[str, Any]], project_name: str = "") -> str:
    """
    Format applications list for display
    
    Args:
        apps: List of application dictionaries
        project_name: Name of the project (optional)
        
    Returns:
        Formatted string representation
    """
    if not apps:
        project_info = f" in project {project_name}" if project_name else ""
        return f"No applications found{project_info}."
    
    project_info = f" in project {project_name}" if project_name else ""
    summary = f"Found {len(apps)} applications{project_info}:\n\n"
    
    for app in apps:
        summary += f"• **{app.get('name', 'Unknown')}**\n"
        summary += f"  Status: {app.get('status', 'Unknown')}\n"
        summary += f"  Image: {app.get('image_reference', 'Unknown')}\n"
        summary += f"  Created: {app.get('created_at', 'Unknown')}\n"
        if app.get('endpoint'):
            summary += f"  Endpoint: {app.get('endpoint')}\n"
        summary += "\n"
    
    return summary