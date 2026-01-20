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
    
    def list_projects(self, limit: int = 100, resource_group_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all Code Engine projects, optionally filtered by resource group
        
        Args:
            limit: Maximum number of projects to return per page
            resource_group_id: Optional resource group ID to filter projects
            
        Returns:
            List of project dictionaries
        """
        try:
            all_results = []
            
            # Build pager kwargs
            pager_kwargs = {
                'client': self.service,
                'limit': limit,
            }
            
            # Add resource group filter if provided
            if resource_group_id:
                pager_kwargs['resource_group_id'] = resource_group_id
                logger.info(f"Filtering projects by resource group: {resource_group_id}")
            
            pager = ProjectsPager(**pager_kwargs)
            
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
    
    def create_application(
        self,
        project_id: str,
        app_name: str,
        image_reference: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a new Code Engine application
        
        Args:
            project_id: Code Engine project ID
            app_name: Name for the new application
            image_reference: Container image reference (e.g., 'icr.io/namespace/image:tag')
            **kwargs: Additional application configuration options including:
                - image_port: Port the app listens on (default: 8080)
                - managed_domain_mappings: Managed domain mapping visibility (default: 'local_public')
                - scale_min_instances: Minimum number of instances (default: 0)
                - scale_max_instances: Maximum number of instances (default: 10)
                - scale_cpu_limit: CPU limit (default: '1')
                - scale_memory_limit: Memory limit (default: '4G')
                - run_env_variables: List of environment variable dicts with 'name' and 'value'
                - run_service_account: Service account name (default: 'default')
                
        Returns:
            Application details dictionary
        """
        try:
            response = self.service.create_app(
                project_id=project_id,
                name=app_name,
                image_reference=image_reference,
                **kwargs
            )
            app = response.get_result()
            logger.info(f"Created application {app_name} in project {project_id}")
            return app
            
        except ApiException as e:
            logger.error(f"API error creating application: {e}")
            raise CodeEngineError(f"Failed to create application {app_name}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error creating application: {e}")
            raise CodeEngineError(f"Unexpected error: {e}")
    
    def update_application(
        self,
        project_id: str,
        app_name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Update an existing Code Engine application
        
        Args:
            project_id: Code Engine project ID
            app_name: Name of the application to update
            **kwargs: Application configuration options to update (same as create_application)
                
        Returns:
            Updated application details dictionary
        """
        try:
            response = self.service.update_app(
                project_id=project_id,
                name=app_name,
                **kwargs
            )
            app = response.get_result()
            logger.info(f"Updated application {app_name} in project {project_id}")
            return app
            
        except ApiException as e:
            logger.error(f"API error updating application: {e}")
            raise CodeEngineError(f"Failed to update application {app_name}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error updating application: {e}")
            raise CodeEngineError(f"Unexpected error: {e}")
    
    def create_build(
        self,
        project_id: str,
        build_name: str,
        output_image: str,
        output_secret: str,
        source_url: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a new build configuration
        
        Args:
            project_id: Code Engine project ID
            build_name: Name for the build configuration
            output_image: Output container image reference
            output_secret: Name of the secret for pushing to registry
            source_url: Git repository URL
            **kwargs: Additional build configuration including:
                - source_revision: Git branch/tag/commit (default: 'main')
                - source_context_dir: Directory in repo with source (default: root)
                - source_secret: Secret for accessing private repos
                - strategy_type: Build strategy ('dockerfile' or 'buildpacks')
                - strategy_spec_file: Path to Dockerfile if strategy_type is 'dockerfile'
                - strategy_size: Build resources ('small', 'medium', 'large', 'xlarge')
                - timeout: Build timeout in seconds (default: 600)
                
        Returns:
            Build configuration details dictionary
        """
        try:
            response = self.service.create_build(
                project_id=project_id,
                name=build_name,
                output_image=output_image,
                output_secret=output_secret,
                source_url=source_url,
                **kwargs
            )
            build = response.get_result()
            logger.info(f"Created build {build_name} in project {project_id}")
            return build
            
        except ApiException as e:
            logger.error(f"API error creating build: {e}")
            raise CodeEngineError(f"Failed to create build {build_name}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error creating build: {e}")
            raise CodeEngineError(f"Unexpected error: {e}")
    
    def create_build_run(
        self,
        project_id: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create and execute a build run
        
        Args:
            project_id: Code Engine project ID
            **kwargs: Build run configuration including:
                - build_name: Name of existing build config to use
                - name: Optional name for this build run
                - output_image: Override output image
                - output_secret: Override output secret
                - source_url: Override source URL
                - source_revision: Override source revision
                - timeout: Override timeout
                
        Returns:
            Build run details dictionary
        """
        try:
            response = self.service.create_build_run(
                project_id=project_id,
                **kwargs
            )
            build_run = response.get_result()
            logger.info(f"Created build run {build_run.get('name', 'unnamed')} in project {project_id}")
            return build_run
            
        except ApiException as e:
            logger.error(f"API error creating build run: {e}")
            raise CodeEngineError(f"Failed to create build run: {e}")
        except Exception as e:
            logger.error(f"Unexpected error creating build run: {e}")
            raise CodeEngineError(f"Unexpected error: {e}")
    
    def get_build(self, project_id: str, build_name: str) -> Dict[str, Any]:
        """
        Get details of a specific build configuration
        
        Args:
            project_id: Code Engine project ID
            build_name: Name of the build
            
        Returns:
            Build configuration details dictionary
        """
        try:
            response = self.service.get_build(
                project_id=project_id,
                name=build_name,
            )
            build = response.get_result()
            logger.info(f"Retrieved build {build_name} from project {project_id}")
            return build
            
        except ApiException as e:
            logger.error(f"API error getting build: {e}")
            raise CodeEngineError(f"Failed to get build {build_name}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error getting build: {e}")
            raise CodeEngineError(f"Unexpected error: {e}")
    
    def get_build_run(self, project_id: str, build_run_name: str) -> Dict[str, Any]:
        """
        Get details of a specific build run
        
        Args:
            project_id: Code Engine project ID
            build_run_name: Name of the build run
            
        Returns:
            Build run details dictionary
        """
        try:
            response = self.service.get_build_run(
                project_id=project_id,
                name=build_run_name,
            )
            build_run = response.get_result()
            logger.info(f"Retrieved build run {build_run_name} from project {project_id}")
            return build_run
            
        except ApiException as e:
            logger.error(f"API error getting build run: {e}")
            raise CodeEngineError(f"Failed to get build run {build_run_name}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error getting build run: {e}")
            raise CodeEngineError(f"Unexpected error: {e}")
    
    def list_builds(self, project_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        List build configurations in a project
        
        Args:
            project_id: Code Engine project ID
            limit: Maximum number of builds to return
            
        Returns:
            List of build configuration dictionaries
        """
        try:
            response = self.service.list_builds(
                project_id=project_id,
                limit=limit,
            )
            builds = response.get_result().get('builds', [])
            logger.info(f"Retrieved {len(builds)} builds for project {project_id}")
            return builds
            
        except ApiException as e:
            logger.error(f"API error listing builds: {e}")
            raise CodeEngineError(f"Failed to list builds: {e}")
        except Exception as e:
            logger.error(f"Unexpected error listing builds: {e}")
            raise CodeEngineError(f"Unexpected error: {e}")
    
    def list_build_runs(
        self,
        project_id: str,
        build_name: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        List build runs in a project
        
        Args:
            project_id: Code Engine project ID
            build_name: Optional build name to filter runs
            limit: Maximum number of build runs to return
            
        Returns:
            List of build run dictionaries
        """
        try:
            kwargs = {
                'project_id': project_id,
                'limit': limit
            }
            if build_name:
                kwargs['build_name'] = build_name
                
            response = self.service.list_build_runs(**kwargs)
            build_runs = response.get_result().get('build_runs', [])
            logger.info(f"Retrieved {len(build_runs)} build runs for project {project_id}")
            return build_runs
            
        except ApiException as e:
            logger.error(f"API error listing build runs: {e}")
            raise CodeEngineError(f"Failed to list build runs: {e}")
        except Exception as e:
            logger.error(f"Unexpected error listing build runs: {e}")
            raise CodeEngineError(f"Unexpected error: {e}")
    
    def find_project_by_name(self, project_name: str, resource_group_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Find a Code Engine project by name, optionally filtered by resource group.
        
        Args:
            project_name: Name of the project to find
            resource_group_id: Optional resource group ID to filter search
            
        Returns:
            Project dictionary if found, None otherwise
        """
        try:
            projects = self.list_projects(resource_group_id=resource_group_id)
            
            for project in projects:
                if project.get('name') == project_name:
                    logger.info(f"Found project '{project_name}': {project.get('id')}")
                    return project
            
            logger.warning(f"Project '{project_name}' not found")
            return None
            
        except CodeEngineError:
            raise
        except Exception as e:
            logger.error(f"Error finding project: {e}")
            raise CodeEngineError(f"Failed to find project '{project_name}': {e}")
    
    def get_resource_group_id_by_name(self, resource_group_name: str) -> Optional[str]:
        """
        Get resource group ID by name using ibmcloud CLI.
        
        Args:
            resource_group_name: Name of the resource group
            
        Returns:
            Resource group ID if found, None otherwise
            
        Note:
            This requires ibmcloud CLI to be installed and configured.
        """
        try:
            import subprocess
            import json
            
            # Use ibmcloud CLI to get resource group
            result = subprocess.run(
                ['ibmcloud', 'resource', 'groups', '--output', 'json'],
                capture_output=True,
                text=True,
                check=True
            )
            
            groups = json.loads(result.stdout)
            for group in groups.get('resources', []):
                if group.get('name') == resource_group_name:
                    rg_id = group.get('id')
                    logger.info(f"Found resource group '{resource_group_name}': {rg_id}")
                    return rg_id
            
            logger.warning(f"Resource group '{resource_group_name}' not found")
            return None
            
        except Exception as e:
            logger.error(f"Error getting resource group ID: {e}")
            return None

    def create_app_from_source(
        self,
        project_id: str,
        app_name: str,
        source_path: str = ".",
        port: int = 8080,
        image_name: Optional[str] = None,
        min_scale: int = 1,
        max_scale: int = 10,
        cpu_limit: str = "0.5",
        memory_limit: str = "4G"
    ) -> Dict[str, Any]:
        """
        Create a Code Engine application directly from local source code.
        
        This method combines build and application creation into a single operation.
        Code Engine automatically packages the source, creates a build run, pushes
        the image to the private registry, and deploys the application.
        
        Equivalent to: ibmcloud ce app create --name APP_NAME --build-source .
        
        Args:
            project_id: Code Engine project ID
            app_name: Name of the application to create
            source_path: Path to source code (default: ".")
            port: Port the application listens on (default: 8080)
            image_name: Optional custom image name (format: private.us.icr.io/namespace/image:tag)
                       If not provided, Code Engine generates one automatically
            min_scale: Minimum number of instances (default: 1)
            max_scale: Maximum number of instances (default: 10)
            cpu_limit: CPU limit per instance (default: "0.5")
            memory_limit: Memory limit per instance (default: "4G")
            
        Returns:
            Application details dictionary including endpoint URL
            
        Raises:
            CodeEngineError: If application creation fails
            
        Example:
            # Create app with auto-generated image name
            app = client.create_app_from_source(
                project_id="proj-123",
                app_name="my-app",
                source_path=".",
                port=9090
            )
            
            # Create app with custom registry image name
            app = client.create_app_from_source(
                project_id="proj-123",
                app_name="my-app",
                source_path=".",
                port=9090,
                image_name="private.us.icr.io/rtiffany/my-app:1"
            )
        """
        try:
            # Build request parameters for app creation with source
            # The SDK maps these to the Code Engine API create app endpoint
            app_create_params = {
                'project_id': project_id,
                'name': app_name,
                'port': port,
                'scale_min_instances': min_scale,
                'scale_max_instances': max_scale,
                'scale_cpu_limit': cpu_limit,
                'scale_memory_limit': memory_limit,
            }
            
            # If custom image name provided, set it
            # Otherwise, Code Engine will auto-generate using private registry
            if image_name:
                # Ensure image name has private. prefix for private registry
                if not image_name.startswith('private.'):
                    image_name = f'private.{image_name}'
                app_create_params['image_reference'] = image_name
            
            # Add build source - the SDK parameter name may vary
            # This triggers Code Engine's integrated build-from-source feature
            # Equivalent to ibmcloud ce app create --build-source <source_path>
            if hasattr(self.service, 'create_app'):
                # The SDK typically accepts build_source as a parameter
                app_create_params['build_source'] = source_path
            
            logger.info(f"Creating Code Engine application '{app_name}' from source: {source_path}")
            if image_name:
                logger.info(f"Using image: {image_name}")
            
            response = self.service.create_app(**app_create_params)
            app = response.get_result()
            
            logger.info(f"Application '{app_name}' created successfully")
            logger.info(f"Endpoint: {app.get('endpoint', 'Pending - build in progress')}")
            
            return app
            
        except ApiException as e:
            logger.error(f"API error creating application from source: {e}")
            raise CodeEngineError(f"Failed to create application '{app_name}' from source: {e}")
        except Exception as e:
            logger.error(f"Unexpected error creating application from source: {e}")
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