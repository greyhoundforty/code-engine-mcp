# IBM Code Engine MCP Server - Available Tools

This document provides comprehensive documentation for all tools available in the IBM Code Engine MCP Server. These tools enable Claude Code and Claude Desktop to interact with IBM Cloud Code Engine services.

## Table of Contents

- [Project Management](#project-management) (2 tools)
- [Application Management](#application-management) (7 tools)
- [Build Management](#build-management) (5 tools)
- [Job Management](#job-management) (4 tools)
- [Domain Management](#domain-management) (2 tools)
- [Secret Management](#secret-management) (2 tools)
- [Configmap Management](#configmap-management) (5 tools)
- [Function Management](#function-management) (6 tools)
- [Service Binding Management](#service-binding-management) (4 tools)

---

## Project Management

### `list_projects`

List all IBM Code Engine projects in your account.

**Parameters:**
- `limit` (integer, optional): Maximum number of projects to return
  - Default: 100
  - Minimum: 1
  - Maximum: 200

**Example:**
```
"List all Code Engine projects"
"Show me my Code Engine projects"
```

**Returns:**
- Formatted summary of projects with names, IDs, regions, and status
- Raw JSON data for programmatic access

---

### `find_project_by_name`

Find a specific Code Engine project by name, with optional resource group filtering.

**Parameters:**
- `project_name` (string, **required**): Name of the project to find
- `resource_group_id` (string, optional): Resource group ID to filter search

**Example:**
```
"Find project named rst-ce-dev"
"Find project myapp in resource group CDE"
```

**Returns:**
- Project details including ID, name, region, resource group
- Error message if project not found

---

## Application Management

### `list_applications`

List all applications in a specific Code Engine project.

**Parameters:**
- `project_id` (string, **required**): Code Engine project ID
- `limit` (integer, optional): Maximum number of applications to return
  - Default: 100
  - Minimum: 1
  - Maximum: 200

**Example:**
```
"List applications in project abc123"
"Show me all apps in rst-ce-dev"
```

**Returns:**
- Formatted summary with app names, images, status, URLs
- Scaling configuration and resource limits
- Raw JSON data

---

### `get_application`

Get detailed information about a specific application.

**Parameters:**
- `project_id` (string, **required**): Code Engine project ID
- `app_name` (string, **required**): Name of the application

**Example:**
```
"Get details for app myapp in project abc123"
"Show me the configuration for simple-go-app"
```

**Returns:**
- Complete application configuration
- Current status and health
- Endpoint URLs
- Scaling settings (min/max instances, CPU, memory)
- Image reference and port
- Environment variables and secrets

---

### `list_app_revisions`

List all revisions for a specific application (deployment history).

**Parameters:**
- `project_id` (string, **required**): Code Engine project ID
- `app_name` (string, **required**): Name of the application
- `limit` (integer, optional): Maximum number of revisions to return
  - Default: 100
  - Minimum: 1
  - Maximum: 200

**Example:**
```
"Show revisions for myapp"
"List deployment history for simple-go-app"
```

**Returns:**
- List of revisions with timestamps
- Configuration changes per revision
- Active/inactive status

---

### `get_app_revision`

Get detailed information about a specific application revision.

**Parameters:**
- `project_id` (string, **required**): Code Engine project ID
- `app_name` (string, **required**): Name of the application
- `revision_name` (string, **required**): Name of the revision

**Example:**
```
"Get details for revision myapp-00001"
```

**Returns:**
- Complete revision configuration
- Creation timestamp
- Image reference used in this revision
- Resource allocations

---

### `create_application`

Create a new Code Engine application from a pre-built container image.

**Parameters:**
- `project_id` (string, **required**): Code Engine project ID
- `app_name` (string, **required**): Name for the new application
- `image_reference` (string, **required**): Container image reference (e.g., 'icr.io/namespace/image:tag')
- `image_port` (integer, optional): Port the application listens on (default: 8080)
- `scale_min_instances` (integer, optional): Minimum number of instances (default: 0)
- `scale_max_instances` (integer, optional): Maximum number of instances (default: 10)
- `scale_cpu_limit` (string, optional): CPU limit per instance (default: '1')
  - Examples: '0.5', '1', '2'
- `scale_memory_limit` (string, optional): Memory limit per instance (default: '4G')
  - Examples: '2G', '4G', '8G'
- `managed_domain_mappings` (string, optional): Domain visibility (default: 'local_public')
  - Options: 'local_public', 'local_private', 'local'

**Example:**
```
"Create app myapp from image icr.io/namespace/myapp:v1"
"Deploy nginx from nginx:latest with 2GB memory and port 80"
```

**Returns:**
- Application creation status
- Application URL
- Configuration summary

---

### `update_application`

Update an existing Code Engine application's configuration.

**Parameters:**
- `project_id` (string, **required**): Code Engine project ID
- `app_name` (string, **required**): Name of the application to update
- `image_reference` (string, optional): New container image reference
- `scale_min_instances` (integer, optional): New minimum instances
- `scale_max_instances` (integer, optional): New maximum instances
- `scale_cpu_limit` (string, optional): New CPU limit
- `scale_memory_limit` (string, optional): New memory limit

**Example:**
```
"Update myapp to use new image myapp:v2"
"Scale myapp to minimum 2 instances"
"Update myapp memory to 8G"
```

**Returns:**
- Update status
- New configuration details
- Updated application URL

---

### `create_app_from_source`

Deploy an application from local source code using Code Engine's integrated build-source feature. This tool packages your source code, builds a Docker image, and deploys it automatically in a single operation.

**Parameters:**
- `project_id` (string, **required**): Code Engine project ID
- `app_name` (string, **required**): Name of the application to create
- `source_path` (string, optional): Path to source code directory (default: '.')
- `port` (integer, optional): Port the application listens on (default: 8080)
  - Minimum: 1
  - Maximum: 65535
- `image_name` (string, optional): Custom image name (e.g., 'private.us.icr.io/namespace/image:tag')
  - If not provided, Code Engine auto-generates a name
- `min_scale` (integer, optional): Minimum number of instances (default: 1)
  - Minimum: 0
  - Maximum: 100
- `max_scale` (integer, optional): Maximum number of instances (default: 10)
  - Minimum: 1
  - Maximum: 100
- `cpu_limit` (string, optional): CPU limit per instance (default: '0.5')
- `memory_limit` (string, optional): Memory limit per instance (default: '4G')

**Example:**
```
"Deploy the Go app in examples/simple-go-app to rst-ce-dev"
"Create app myflask from ./flask-app on port 5000"
"Deploy current directory as myapp with 2GB memory"
```

**Returns:**
- Build status and progress
- Generated image name
- Application deployment status
- Application URL
- Complete configuration

**Requirements:**
- Source directory must contain a Dockerfile
- IBM Cloud CLI must be installed and authenticated
- Code Engine CLI plugin must be installed

---

## Build Management

### `create_build`

Create a new build configuration for building container images from Git source code.

**Parameters:**
- `project_id` (string, **required**): Code Engine project ID
- `build_name` (string, **required**): Name for the build configuration
- `output_image` (string, **required**): Output container image reference (e.g., 'icr.io/namespace/image:tag')
- `output_secret` (string, **required**): Name of secret for pushing to container registry
- `source_url` (string, **required**): Git repository URL containing source code
- `source_revision` (string, optional): Git branch, tag, or commit (default: 'main')
- `source_context_dir` (string, optional): Directory in repo containing source (default: root)
- `strategy_type` (string, optional): Build strategy (default: 'dockerfile')
  - Options: 'dockerfile', 'buildpacks'
- `strategy_spec_file` (string, optional): Path to Dockerfile (default: './Dockerfile')
- `strategy_size` (string, optional): Build resources (default: 'medium')
  - Options: 'small', 'medium', 'large', 'xlarge'

**Example:**
```
"Create build mybuild from https://github.com/user/repo.git"
"Create build config for myapp with buildpacks strategy"
```

**Returns:**
- Build configuration status
- Configuration details
- Build ID

---

### `list_builds`

List all build configurations in a project.

**Parameters:**
- `project_id` (string, **required**): Code Engine project ID
- `limit` (integer, optional): Maximum number of builds to return (default: 100)

**Example:**
```
"List builds in project abc123"
"Show me all build configurations"
```

**Returns:**
- List of build configurations with names, sources, and output images
- Build strategy and settings

---

### `create_build_run`

Execute a build to create a container image from source code.

**Parameters:**
- `project_id` (string, **required**): Code Engine project ID
- `build_name` (string, **required**): Name of existing build configuration to execute
- `name` (string, optional): Optional name for this build run

**Example:**
```
"Run build mybuild"
"Execute build configuration myapp-build"
```

**Returns:**
- Build run status
- Build run name
- Progress updates

---

### `get_build_run`

Get the status and details of a specific build run.

**Parameters:**
- `project_id` (string, **required**): Code Engine project ID
- `build_run_name` (string, **required**): Name of the build run

**Example:**
```
"Check status of build run mybuild-run-123"
"Get details for build mybuild-run-260120"
```

**Returns:**
- Build run status (pending/running/succeeded/failed)
- Build logs summary
- Output image reference
- Start and completion times
- Error messages if failed

---

### `list_build_runs`

List build runs in a project, optionally filtered by build configuration name.

**Parameters:**
- `project_id` (string, **required**): Code Engine project ID
- `build_name` (string, optional): Filter by build configuration name
- `limit` (integer, optional): Maximum number of build runs to return (default: 100)

**Example:**
```
"List all build runs in project abc123"
"Show build runs for mybuild"
```

**Returns:**
- List of build runs with status and timestamps
- Build configuration names
- Output images

---

## Job Management

### `list_jobs`

List all batch jobs in a specific Code Engine project.

**Parameters:**
- `project_id` (string, **required**): Code Engine project ID
- `limit` (integer, optional): Maximum number of jobs to return (default: 100)

**Example:**
```
"List jobs in project abc123"
"Show me all batch jobs"
```

**Returns:**
- List of jobs with names and configurations
- Resource allocations
- Job run modes

---

### `get_job`

Get detailed information about a specific batch job.

**Parameters:**
- `project_id` (string, **required**): Code Engine project ID
- `job_name` (string, **required**): Name of the job

**Example:**
```
"Get details for job myjob"
"Show configuration for batch-processor"
```

**Returns:**
- Complete job configuration
- Image reference
- Resource limits (CPU, memory)
- Environment variables
- Retry settings

---

### `list_job_runs`

List job runs for a specific job or all jobs in a project.

**Parameters:**
- `project_id` (string, **required**): Code Engine project ID
- `job_name` (string, optional): Optional job name to filter runs
- `limit` (integer, optional): Maximum number of job runs to return (default: 100)

**Example:**
```
"List job runs in project abc123"
"Show runs for job myjob"
```

**Returns:**
- List of job runs with status
- Start and completion times
- Exit codes
- Resource usage

---

### `get_job_run`

Get detailed information about a specific job run.

**Parameters:**
- `project_id` (string, **required**): Code Engine project ID
- `job_run_name` (string, **required**): Name of the job run

**Example:**
```
"Get details for job run myjob-run-123"
"Check status of batch-run-260120"
```

**Returns:**
- Job run status (pending/running/succeeded/failed)
- Execution details
- Logs summary
- Resource consumption
- Exit code

---

## Domain Management

### `list_domain_mappings`

List all custom domain mappings in a specific Code Engine project.

**Parameters:**
- `project_id` (string, **required**): Code Engine project ID
- `limit` (integer, optional): Maximum number of domain mappings to return (default: 100)

**Example:**
```
"List domain mappings in project abc123"
"Show custom domains"
```

**Returns:**
- List of domain mappings
- Target applications
- TLS certificate status

---

### `get_domain_mapping`

Get detailed information about a specific domain mapping.

**Parameters:**
- `project_id` (string, **required**): Code Engine project ID
- `domain_name` (string, **required**): Name of the domain mapping

**Example:**
```
"Get details for domain myapp.example.com"
```

**Returns:**
- Domain configuration
- Target application
- TLS/SSL certificate details
- CNAME records required

---

## Secret Management

### `list_secrets`

List all secrets in a specific Code Engine project. Sensitive data is automatically masked for security.

**Parameters:**
- `project_id` (string, **required**): Code Engine project ID
- `limit` (integer, optional): Maximum number of secrets to return (default: 100)

**Example:**
```
"List secrets in project abc123"
"Show me all secrets"
```

**Returns:**
- List of secret names and types
- Creation timestamps
- Number of keys per secret
- **Note:** Actual secret values are masked (e.g., "********")

---

### `get_secret`

Get detailed information about a specific secret. Sensitive data is automatically masked for security.

**Parameters:**
- `project_id` (string, **required**): Code Engine project ID
- `secret_name` (string, **required**): Name of the secret

**Example:**
```
"Get details for secret api-keys"
```

**Returns:**
- Secret metadata
- Keys contained in the secret
- **Note:** Actual secret values are masked (e.g., "********")
- Creation and update timestamps

---

## Tool Response Format

All tools return responses in a consistent format:

### Text Summary
A human-readable formatted summary of the results, including:
- Key information highlighted
- Status indicators
- URLs and endpoints
- Error messages if applicable

### Raw JSON
Complete JSON data from the Code Engine API for programmatic access and detailed inspection.

## Security Features

- **Automatic Secret Masking**: All secret values are masked in responses
- **No Credential Caching**: API keys are loaded fresh for each operation
- **Non-root Container**: MCP server runs as non-root user
- **Ephemeral Containers**: Docker containers are removed after execution (`--rm` flag)
- **Environment-based Auth**: API keys loaded via `--env-file` (never in command history)

## Configuration Requirements

To use these tools, you need:

1. **IBM Cloud API Key** (`IBMCLOUD_API_KEY` environment variable)
2. **IBM Cloud Region** (`IBMCLOUD_REGION`, default: `us-south`)
   - Supported regions: `us-south`, `us-east`, `eu-gb`, `eu-de`, `jp-tok`, `au-syd`
3. **MCP Server Running** via Docker or locally

See the main [README.md](README.md) for setup instructions.

## Common Usage Patterns

### Deploying from Source (Recommended)
```
1. "Find project rst-ce-dev"
2. "Deploy the app in examples/simple-go-app to rst-ce-dev"
```

### Deploying from Pre-built Image
```
1. "List my Code Engine projects"
2. "Create app myapp from image icr.io/namespace/myapp:v1 in project abc123"
```

### Building from Git
```
1. "Create build mybuild from https://github.com/user/repo.git outputting to icr.io/namespace/myapp:latest"
2. "Run build mybuild"
3. "Check status of build run mybuild-run-123"
4. "Create app myapp from image icr.io/namespace/myapp:latest"
```

### Monitoring and Scaling
```
1. "Show me all apps in project abc123"
2. "Get details for app myapp"
3. "Scale myapp to minimum 2 instances"
```

## Error Handling

All tools provide clear error messages when:
- Required parameters are missing
- Projects or resources are not found
- API authentication fails
- IBM Cloud API returns errors
- Build or deployment operations fail

Error responses include:
- Error type and code
- Descriptive error message
- Suggested corrective actions
- Relevant IBM Cloud documentation links

## Additional Resources

- [IBM Cloud Code Engine Documentation](https://cloud.ibm.com/docs/codeengine)
- [Code Engine CLI Reference](https://cloud.ibm.com/docs/codeengine?topic=codeengine-cli)
- [IBM Container Registry](https://cloud.ibm.com/docs/Registry)
- [Example Applications](examples/)

---

## Configmap Management

### `list_config_maps`

List all configmaps in a Code Engine project.

**Parameters:**
- `project_id` (string, **required**): Code Engine project ID
- `limit` (integer, optional): Maximum number to return. Default: 100

**Example:**
```
"List configmaps in project abc123"
"Show all configmaps in my project"
```

**Returns:**
- Formatted summary of configmaps with names, key counts, and creation dates
- Raw JSON data

---

### `get_config_map`

Get all key-value pairs in a specific configmap.

**Parameters:**
- `project_id` (string, **required**): Code Engine project ID
- `name` (string, **required**): Configmap name

**Example:**
```
"Get configmap app-config in project abc123"
"Show me the values in my-configmap"
```

**Returns:**
- Full configmap details including all key-value pairs

---

### `create_config_map`

Create a new configmap in a Code Engine project.

**Parameters:**
- `project_id` (string, **required**): Code Engine project ID
- `name` (string, **required**): Configmap name (must be unique within the project)
- `data` (object, optional): Key-value pairs to store (all values must be strings)

**Example:**
```
"Create configmap app-config with HOST=db.example.com and PORT=5432"
"Create an empty configmap named feature-flags"
```

**Returns:**
- Created configmap details

---

### `update_config_map`

Replace all key-value pairs in a configmap (full replacement). Any keys not included in `data` will be removed.

**Parameters:**
- `project_id` (string, **required**): Code Engine project ID
- `name` (string, **required**): Configmap name
- `data` (object, optional): New key-value pairs (replaces all existing entries)

**Example:**
```
"Update configmap app-config with new values HOST=prod.example.com PORT=5432"
"Replace all keys in my-configmap with {DEBUG: false}"
```

**Returns:**
- Updated configmap details

---

### `delete_config_map`

Delete a configmap from a Code Engine project.

**Parameters:**
- `project_id` (string, **required**): Code Engine project ID
- `name` (string, **required**): Configmap name

**Example:**
```
"Delete configmap app-config from project abc123"
```

**Returns:**
- Confirmation message

---

## Function Management

### `list_functions`

List all serverless functions in a Code Engine project.

**Parameters:**
- `project_id` (string, **required**): Code Engine project ID
- `limit` (integer, optional): Maximum number to return. Default: 100

**Example:**
```
"List functions in project abc123"
"Show all serverless functions"
```

**Returns:**
- Formatted summary with function names, runtimes, status, and endpoints
- Raw JSON data

---

### `get_function`

Get details of a specific serverless function.

**Parameters:**
- `project_id` (string, **required**): Code Engine project ID
- `name` (string, **required**): Function name

**Example:**
```
"Get function my-handler in project abc123"
```

**Returns:**
- Full function details including runtime, endpoint, scaling config, environment variables

---

### `create_function`

Create a new serverless function. Use `list_function_runtimes` to see available runtime values.

**Parameters:**
- `project_id` (string, **required**): Code Engine project ID
- `name` (string, **required**): Function name (unique within project)
- `code_reference` (string, **required**): Container registry image reference or inline code bundle data URL
- `runtime` (string, **required**): Managed runtime identifier (e.g. `nodejs-20`, `python-3.11`)
- `scale_cpu_limit` (string, optional): CPU limit, e.g. `"0.25"`, `"0.5"`, `"1"`. Default: `"0.25"`
- `scale_memory_limit` (string, optional): Memory limit, e.g. `"256M"`, `"512M"`, `"1G"`. Default: `"1G"`
- `scale_max_execution_time` (integer, optional): Max execution time in seconds (max 120). Default: 60
- `managed_domain_mappings` (string, optional): Endpoint visibility: `"local"`, `"local_public"`, or `"local_private"`
- `run_env_variables` (array, optional): Environment variables as `[{name, value}]` objects

**Example:**
```
"Create a Node.js 20 function named my-handler with image icr.io/ns/fn:latest"
"Deploy a Python 3.11 function with 512M memory and 30-second timeout"
```

**Returns:**
- Created function details including endpoint URL

---

### `update_function`

Update configuration of an existing serverless function. Automatically handles ETag concurrency control.

**Parameters:**
- `project_id` (string, **required**): Code Engine project ID
- `name` (string, **required**): Function name
- `runtime` (string, optional): New runtime identifier
- `code_reference` (string, optional): New code reference
- `scale_cpu_limit` (string, optional): New CPU limit
- `scale_memory_limit` (string, optional): New memory limit
- `scale_max_execution_time` (integer, optional): New max execution time in seconds
- `managed_domain_mappings` (string, optional): New endpoint visibility
- `run_env_variables` (array, optional): New environment variables

**Example:**
```
"Update function my-handler to use nodejs-22 runtime"
"Increase memory for my-handler to 512M"
```

**Returns:**
- Updated function details

---

### `delete_function`

Delete a serverless function from a Code Engine project.

**Parameters:**
- `project_id` (string, **required**): Code Engine project ID
- `name` (string, **required**): Function name

**Example:**
```
"Delete function my-handler from project abc123"
```

**Returns:**
- Confirmation message

---

### `list_function_runtimes`

List all available managed runtimes for Code Engine functions. No parameters required.

**Example:**
```
"What function runtimes are available?"
"List available Code Engine function runtimes"
```

**Returns:**
- List of available runtime identifiers (e.g. `nodejs-20`, `nodejs-22`, `nodejs-24`, `python-3.11`, `python-3.13`)

---

## Service Binding Management

### `list_bindings`

List all service bindings in a Code Engine project.

**Parameters:**
- `project_id` (string, **required**): Code Engine project ID
- `limit` (integer, optional): Maximum number to return. Default: 100

**Example:**
```
"List service bindings in project abc123"
"Show all bindings in my project"
```

**Returns:**
- Formatted summary with binding IDs, bound component, prefix, and status
- Raw JSON data

---

### `get_binding`

Get details of a specific service binding.

**Parameters:**
- `project_id` (string, **required**): Code Engine project ID
- `binding_id` (string, **required**): Service binding ID (from `list_bindings`)

**Example:**
```
"Get binding bind-abc in project abc123"
```

**Returns:**
- Full binding details including component, prefix, secret name, and status

---

### `create_binding`

Bind an IBM Cloud service instance to a Code Engine app, job, or function. The service credentials are injected as environment variables with the specified prefix. Requires an existing service credential secret in the project.

**Parameters:**
- `project_id` (string, **required**): Code Engine project ID
- `component_name` (string, **required**): Name of the app, job, or function to bind to
- `component_resource_type` (string, **required**): Resource type — `"app_v2"`, `"job_v2"`, or `"function_v2"`
- `prefix` (string, **required**): Environment variable prefix (e.g. `"COS"` → variables like `COS_APIKEY`, `COS_URL`)
- `secret_name` (string, **required**): Name of the existing service credential secret in the project

**Example:**
```
"Bind COS service to app my-app using secret cos-credentials with prefix COS"
"Create a service binding for job my-job to use the Watson NLU service"
```

**Returns:**
- Created binding details including binding ID

---

### `delete_binding`

Delete a service binding from a Code Engine project.

**Parameters:**
- `project_id` (string, **required**): Code Engine project ID
- `binding_id` (string, **required**): Service binding ID

**Example:**
```
"Delete binding bind-abc from project abc123"
```

**Returns:**
- Confirmation message
