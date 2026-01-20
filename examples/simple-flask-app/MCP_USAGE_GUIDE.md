# IBM Code Engine MCP Server - Usage Guide
**The Natural Language Interface for Code Engine Deployments**

## Primary Usage: MCP Tools via Claude Code/Desktop

This MCP server was built specifically to enable natural language commands for Code Engine operations. **This is the intended and recommended way to use it.**

---

## 🎯 How It Works

```
You (natural language)
         ↓
    "Deploy this app to Code Engine on port 8080"
         ↓
Claude Code/Desktop (interprets intent)
         ↓
MCP Server (ibm-code-engine)
         ↓
    Docker Container
    • Loads IBMCLOUD_API_KEY from .mcp.env
    • Authenticates to IBM Cloud
    • Calls Code Engine API
         ↓
    Returns Result
    • ✅ No API key exposed
    • ✅ No manual CLI commands
    • ✅ Natural language response
```

---

## ✅ Setup (One-Time)

### 1. Verify .mcp.env File

**Location:** `/Users/ryan/.mcp.env`

```bash
# Check it exists and is secure
ls -la /Users/ryan/.mcp.env

# Should show:
# -rw------- (only you can read)
```

**Contents:**
```
IBMCLOUD_API_KEY=your-api-key-here
```

**Security:**
```bash
chmod 600 /Users/ryan/.mcp.env
```

---

### 2. Verify .mcp.json Configuration

**Location:** Your project directory (e.g., `examples/simple-flask-app/.mcp.json`)

```json
{
  "mcpServers": {
    "ibm-code-engine": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "--env-file", "/Users/ryan/.mcp.env",
        "code-engine-mcp:latest"
      ]
    }
  }
}
```

**Key points:**
- `--env-file` loads credentials securely
- `code-engine-mcp:latest` uses your updated Docker image
- API key NEVER appears in configuration

---

### 3. Verify Docker Image is Built

```bash
docker images code-engine-mcp:latest
```

**Expected:**
```
REPOSITORY        TAG       IMAGE ID       CREATED
code-engine-mcp   latest    db4045e68ed7   2026-01-20 10:26:52
```

If missing:
```bash
cd /Users/ryan/projects/code-engine-cli-skill
docker build -t code-engine-mcp:latest .
```

---

### 4. Restart Claude Desktop (if using Claude Desktop)

```bash
# Quit Claude Desktop completely
# Restart Claude Desktop
# MCP server will auto-start when needed
```

---

## 🚀 Using the MCP Server

### Available Natural Language Commands

#### 1. Find Projects

**Examples:**
```
"Find my Code Engine project named rst-ce-dev"
"Find the dts-account-project Code Engine project"
"Show me the project called jbmh"
```

**What happens:**
- Calls `find_project_by_name` MCP tool
- Returns project details (ID, region, status)
- No API key shown ✅

**Example response:**
```
**Found Project: rst-ce-dev**

• ID: 00c1079d-a49b-4a20-83cc-af83220f1b62
• Region: us-south
• Status: active
• Resource Group ID: ac83304b2fb6492e95995812da85b653
```

---

#### 2. Deploy Applications from Source

**Examples:**
```
"Deploy this app to Code Engine on port 8080"

"Create an application from this source code on port 9090 with minimum 2 instances"

"Build and push this Flask app to Code Engine project rst-ce-dev"

"Deploy this to dts-account-project on port 3000 with min scale 3"
```

**What happens:**
- Claude identifies deployment intent
- Finds project (if name given)
- Calls `create_app_from_source` MCP tool
- Packages source code
- Creates build run
- Deploys application
- Returns endpoint URL
- No API key shown ✅

**Example response:**
```
✅ Application 'simple-flask-app-demo' created successfully!

• Name: simple-flask-app-demo
• Project ID: d0a6c45d-8609-4e6a-b652-1075054ea8b1
• Status: Building
• 🌐 Endpoint: https://simple-flask-app-demo.xxx.codeengine.appdomain.cloud
• Port: 8080
• Scale: 2-10 instances
• Resources: 0.5 CPU, 4G memory

Note: Code Engine is packaging source, building Docker image, and deploying...
```

---

#### 3. List Projects

**Examples:**
```
"List all my Code Engine projects"
"Show me all Code Engine projects"
"What Code Engine projects do I have?"
```

**What happens:**
- Calls `list_projects` MCP tool
- Returns all projects in your account
- No API key shown ✅

---

#### 4. List Applications

**Examples:**
```
"List applications in project rst-ce-dev"
"Show me all apps in dts-account-project"
"What apps are running in project 00c1079d-a49b-4a20-83cc-af83220f1b62"
```

**What happens:**
- Calls `list_applications` MCP tool
- Returns all apps in specified project
- No API key shown ✅

---

#### 5. Get Application Details

**Examples:**
```
"Show me details for app simple-flask-mcp-test"
"Get application simple-flask-app-demo in project dts-account-project"
"What's the status of my app named test-app"
```

**What happens:**
- Calls `get_application` MCP tool
- Returns detailed app info (status, endpoint, instances)
- No API key shown ✅

---

#### 6. Build Operations

**Examples:**
```
"Create a build for this source code outputting to private.us.icr.io/rtiffany/myapp:v1"
"Start a build run for build-config myapp-build"
"Show me the status of build run myapp-build-run-123"
```

**What happens:**
- Calls build-related MCP tools
- Manages Code Engine build configurations
- No API key shown ✅

---

#### 7. Job Operations

**Examples:**
```
"List all jobs in project rst-ce-dev"
"Show me job runs for job data-processor"
"Get details for job run batch-job-run-456"
```

**What happens:**
- Calls job-related MCP tools
- Manages Code Engine batch jobs
- No API key shown ✅

---

## 🔐 Security Features

### Why MCP Tools Are Secure

1. **API Key Never in Commands**
   - Loaded via Docker `--env-file`
   - Only accessible inside container
   - Not in conversation history

2. **Authentication is Internal**
   - Happens inside Docker container
   - Code Engine SDK handles it
   - No credentials in output

3. **No Manual CLI Commands**
   - Claude interprets intent
   - Calls MCP tools directly
   - Returns formatted results

4. **Minimal Exposure Surface**
   - Only MCP server has access
   - Container is ephemeral (`--rm`)
   - No credential caching on host

---

## 📋 Complete Example Workflow

### Scenario: Deploy a New Flask App

**Step 1:** Navigate to your app directory
```bash
cd /Users/ryan/projects/my-flask-app
```

**Step 2:** Ensure .mcp.json exists or is in parent directory
```bash
ls .mcp.json
# or
ls ../.mcp.json
```

**Step 3:** Open Claude Code in this directory

**Step 4:** Use natural language
```
"Deploy this Flask app to Code Engine project dts-account-project on port 8080 with minimum 2 instances"
```

**Step 5:** Claude Code automatically:
1. Finds project "dts-account-project" → gets ID
2. Creates app from current directory source
3. Sets port to 8080
4. Sets min_scale to 2
5. Returns deployment status and endpoint

**Step 6:** Verify deployment
```
"Show me the application details"
```

**Result:** App deployed, running, and accessible - **no API key ever shown** ✅

---

## 🛠️ All Available MCP Tools (22 Total)

### Project Management (2 tools)
1. **list_projects** - List all Code Engine projects
2. **find_project_by_name** ⭐ NEW - Find project by name

### Application Management (5 tools)
3. **list_applications** - List apps in a project
4. **get_application** - Get app details
5. **create_application** - Create app from pre-built image
6. **update_application** - Update app configuration
7. **create_app_from_source** ⭐ NEW - Deploy from source code

### Application Revisions (2 tools)
8. **list_app_revisions** - List app revisions
9. **get_app_revision** - Get revision details

### Build Management (5 tools)
10. **create_build** - Create build configuration
11. **list_builds** - List build configs
12. **create_build_run** - Execute a build
13. **get_build_run** - Get build run status
14. **list_build_runs** - List build runs

### Job Management (4 tools)
15. **list_jobs** - List batch jobs
16. **get_job** - Get job details
17. **list_job_runs** - List job runs
18. **get_job_run** - Get job run details

### Domain Mappings (2 tools)
19. **list_domain_mappings** - List custom domains
20. **get_domain_mapping** - Get domain details

### Secrets Management (2 tools)
21. **list_secrets** - List secrets (masked)
22. **get_secret** - Get secret details (masked)

---

## ⚠️ When NOT to Use MCP Tools

### Use Direct CLI Instead If:

1. **MCP server is not available**
   - Docker not running
   - Image not built
   - .mcp.env missing

2. **Debugging MCP server issues**
   - Testing API connectivity
   - Verifying credentials
   - Troubleshooting build problems

3. **Scripting/Automation**
   - CI/CD pipelines
   - Automated deployments
   - Cron jobs

**For these cases, use the secure CLI helper:**
```bash
source /Users/ryan/projects/code-engine-cli-skill/examples/simple-flask-app/secure_cli_helper.sh
```

See `SECURE_API_KEY_GUIDE.md` for details.

---

## 🧪 Testing Your MCP Setup

### Test 1: Verify MCP Server Responds

**Say to Claude Code:**
```
"List all my Code Engine projects"
```

**Expected:** List of projects returned, no errors

✅ **Pass:** MCP server is working
❌ **Fail:** Check Docker image, .mcp.env, restart Claude Desktop

---

### Test 2: Find a Specific Project

**Say to Claude Code:**
```
"Find my Code Engine project named rst-ce-dev"
```

**Expected:**
```
**Found Project: rst-ce-dev**
• ID: 00c1079d-a49b-4a20-83cc-af83220f1b62
...
```

✅ **Pass:** find_project_by_name tool working
❌ **Fail:** Check project name, verify it exists

---

### Test 3: Deploy from Source

**Prerequisites:**
- In a directory with a Dockerfile
- Simple application code

**Say to Claude Code:**
```
"Deploy this app to Code Engine on port 8080"
```

**Expected:**
```
✅ Application created successfully!
• Endpoint: https://...codeengine.appdomain.cloud
```

✅ **Pass:** create_app_from_source tool working
❌ **Fail:** Check Dockerfile exists, verify project selection

---

## 🔧 Troubleshooting

### "MCP server not available"

**Cause:** Docker container not starting

**Fix:**
```bash
# Check Docker is running
docker ps

# Rebuild image
cd /Users/ryan/projects/code-engine-cli-skill
docker build -t code-engine-mcp:latest .

# Test manually
docker run -i --rm --env-file /Users/ryan/.mcp.env code-engine-mcp:latest
```

---

### "Authentication failed"

**Cause:** API key missing or invalid

**Fix:**
```bash
# Check .mcp.env exists
cat /Users/ryan/.mcp.env

# Should show:
# IBMCLOUD_API_KEY=...

# Test API key works
export IBMCLOUD_API_KEY=$(grep IBMCLOUD_API_KEY /Users/ryan/.mcp.env | cut -d '=' -f2)
ibmcloud iam oauth-tokens
```

---

### "Unknown tool: create_app_from_source"

**Cause:** Old Docker image without new tools

**Fix:**
```bash
# Rebuild with latest code
cd /Users/ryan/projects/code-engine-cli-skill
docker build --no-cache -t code-engine-mcp:latest .

# Restart Claude Desktop
```

---

### "Project not found"

**Cause:** Project name doesn't match exactly

**Fix:**
```bash
# List exact project names
ibmcloud ce project list

# Use exact name in command:
"Find project named dts-account-project"
# NOT: "Find project dts account"
```

---

## 📚 Additional Resources

- **IMPLEMENTATION_SUMMARY.md** - What was implemented
- **TESTING_CHECKLIST.md** - Complete testing procedures
- **SECURE_API_KEY_GUIDE.md** - Security best practices
- **NEXT_AGENT.md** - Technical implementation details

---

## 🎯 Quick Reference

### Most Common Commands

```
1. "Find my Code Engine project rst-ce-dev"
   → Gets project details

2. "Deploy this app to Code Engine on port 8080"
   → Deploys from current directory

3. "List applications in project rst-ce-dev"
   → Shows all apps

4. "Show me details for app myapp"
   → Gets app status and endpoint

5. "Deploy to dts-account-project on port 9090 with min scale 2"
   → Full deployment with scaling
```

---

## ✅ Best Practices

1. **Always use natural language first**
   - Let Claude interpret your intent
   - MCP tools handle the complexity

2. **Be specific with project names**
   - Use exact project names
   - Claude will find the project ID

3. **Include requirements in one command**
   - Port number
   - Min/max scale
   - Project name
   - All in natural language

4. **Let the MCP server handle authentication**
   - Never export API keys manually
   - Trust the Docker env-file mechanism

5. **Verify deployments with follow-up questions**
   - "Show me the app status"
   - "What's the endpoint URL?"
   - Natural conversation flow

---

## 🚀 Summary

**The IBM Code Engine MCP Server is designed for natural language interaction with Code Engine.**

✅ Say what you want, Claude Code handles the rest
✅ No manual CLI commands needed
✅ No API keys exposed
✅ Secure by design
✅ Simple and intuitive

**This is how it's meant to be used.** 🎉
