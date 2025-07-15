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
    SecretsPager,
    JobsPager,
    JobRunsPager
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
    
    def list_jobs(self, project_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        List batch jobs in a specific project
        
        Args:
            project_id: Code Engine project ID
            limit: Maximum number of jobs to return per page
            
        Returns:
            List of job dictionaries
        """
        try:
            all_results = []
            pager = JobsPager(
                client=self.service,
                project_id=project_id,
                limit=limit,
            )
            
            while pager.has_next():
                next_page = pager.get_next()
                if next_page is not None:
                    all_results.extend(next_page)
            
            logger.info(f"Retrieved {len(all_results)} jobs for project {project_id}")
            return all_results
            
        except ApiException as e:
            logger.error(f"API error listing jobs: {e}")
            raise CodeEngineError(f"Failed to list jobs: {e}")
        except Exception as e:
            logger.error(f"Unexpected error listing jobs: {e}")
            raise CodeEngineError(f"Unexpected error: {e}")
    
    def get_job(self, project_id: str, job_name: str) -> Dict[str, Any]:
        """
        Get details of a specific batch job
        
        Args:
            project_id: Code Engine project ID
            job_name: Name of the job
            
        Returns:
            Job details dictionary
        """
        try:
            response = self.service.get_job(
                project_id=project_id,
                name=job_name,
            )
            job = response.get_result()
            logger.info(f"Retrieved job {job_name} from project {project_id}")
            return job
            
        except ApiException as e:
            logger.error(f"API error getting job: {e}")
            raise CodeEngineError(f"Failed to get job {job_name}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error getting job: {e}")
            raise CodeEngineError(f"Unexpected error: {e}")
    
    def list_job_runs(self, project_id: str, job_name: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        List job runs in a specific project, optionally filtered by job name
        
        Args:
            project_id: Code Engine project ID
            job_name: Optional job name to filter runs
            limit: Maximum number of job runs to return per page
            
        Returns:
            List of job run dictionaries
        """
        try:
            all_results = []
            pager = JobRunsPager(
                client=self.service,
                project_id=project_id,
                job_name=job_name,
                limit=limit,
            )
            
            while pager.has_next():
                next_page = pager.get_next()
                if next_page is not None:
                    all_results.extend(next_page)
            
            job_info = f" for job {job_name}" if job_name else ""
            logger.info(f"Retrieved {len(all_results)} job runs{job_info} in project {project_id}")
            return all_results
            
        except ApiException as e:
            logger.error(f"API error listing job runs: {e}")
            raise CodeEngineError(f"Failed to list job runs: {e}")
        except Exception as e:
            logger.error(f"Unexpected error listing job runs: {e}")
            raise CodeEngineError(f"Unexpected error: {e}")
    
    def get_job_run(self, project_id: str, job_run_name: str) -> Dict[str, Any]:
        """
        Get details of a specific job run
        
        Args:
            project_id: Code Engine project ID
            job_run_name: Name of the job run
            
        Returns:
            Job run details dictionary
        """
        try:
            response = self.service.get_job_run(
                project_id=project_id,
                name=job_run_name,
            )
            job_run = response.get_result()
            logger.info(f"Retrieved job run {job_run_name} from project {project_id}")
            return job_run
            
        except ApiException as e:
            logger.error(f"API error getting job run: {e}")
            raise CodeEngineError(f"Failed to get job run {job_run_name}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error getting job run: {e}")
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


def format_jobs_summary(jobs: List[Dict[str, Any]], project_name: str = "") -> str:
    """
    Format jobs list for display
    
    Args:
        jobs: List of job dictionaries
        project_name: Name of the project (optional)
        
    Returns:
        Formatted string representation
    """
    if not jobs:
        project_info = f" in project {project_name}" if project_name else ""
        return f"No batch jobs found{project_info}."
    
    project_info = f" in project {project_name}" if project_name else ""
    summary = f"Found {len(jobs)} batch jobs{project_info}:\n\n"
    
    for job in jobs:
        summary += f"• **{job.get('name', 'Unknown')}**\n"
        summary += f"  Status: {job.get('status', 'Unknown')}\n"
        summary += f"  Image: {job.get('image_reference', 'Unknown')}\n"
        summary += f"  Created: {job.get('created_at', 'Unknown')}\n"
        if job.get('resource_type'):
            summary += f"  Resource Type: {job.get('resource_type')}\n"
        if job.get('scale_array_spec'):
            array_spec = job.get('scale_array_spec', {})
            if isinstance(array_spec, dict):
                summary += f"  Array Spec: {array_spec.get('array_size', 'N/A')} instances\n"
            else:
                # Handle case where scale_array_spec is a string or other type
                summary += f"  Array Spec: {array_spec}\n"
        summary += "\n"
    
    return summary


def format_job_runs_summary(job_runs: List[Dict[str, Any]], project_name: str = "", job_name: str = "") -> str:
    """
    Format job runs list for display
    
    Args:
        job_runs: List of job run dictionaries
        project_name: Name of the project (optional)
        job_name: Name of the job (optional)
        
    Returns:
        Formatted string representation
    """
    if not job_runs:
        context_info = ""
        if job_name and project_name:
            context_info = f" for job {job_name} in project {project_name}"
        elif job_name:
            context_info = f" for job {job_name}"
        elif project_name:
            context_info = f" in project {project_name}"
        return f"No job runs found{context_info}."
    
    context_info = ""
    if job_name and project_name:
        context_info = f" for job {job_name} in project {project_name}"
    elif job_name:
        context_info = f" for job {job_name}"
    elif project_name:
        context_info = f" in project {project_name}"
    
    summary = f"Found {len(job_runs)} job runs{context_info}:\n\n"
    
    for run in job_runs:
        summary += f"• **{run.get('name', 'Unknown')}**\n"
        summary += f"  Status: {run.get('status', 'Unknown')}\n"
        summary += f"  Job: {run.get('job_name', 'Unknown')}\n"
        summary += f"  Created: {run.get('created_at', 'Unknown')}\n"
        if run.get('completion_time'):
            summary += f"  Completed: {run.get('completion_time')}\n"
        if run.get('status_details'):
            details = run.get('status_details', {})
            if details.get('completion_time'):
                summary += f"  Completion Time: {details.get('completion_time')}\n"
            if details.get('failed'):
                summary += f"  Failed Instances: {details.get('failed')}\n"
            if details.get('succeeded'):
                summary += f"  Succeeded Instances: {details.get('succeeded')}\n"
        summary += "\n"
    
    return summary


def mask_sensitive_data(secret_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Mask sensitive data in secrets
    
    Args:
        secret_data: Secret data dictionary
        
    Returns:
        Dictionary with sensitive values masked
    """
    masked_data = secret_data.copy()
    
    # Mask the actual secret data
    if 'data' in masked_data and isinstance(masked_data['data'], dict):
        masked_data['data'] = {
            key: "***MASKED***" for key in masked_data['data'].keys()
        }
    
    return masked_data