# IBM Code Engine MCP Server
**Natural Language Interface for Code Engine Deployments**

## 🎯 What Is This?

This MCP server enables **natural language deployment** of applications to IBM Cloud Code Engine directly from Claude Code or Claude Desktop.

**Say what you want, Claude handles the deployment:**

```
You: "Deploy this Flask app to Code Engine on port 8080"

Claude: ✅ Deployed to https://your-app.codeengine.appdomain.cloud
```

No manual CLI commands. No exposed API keys. Just natural language.

---

## ✅ Quick Start (3 Steps)

### 1. Verify Setup

```bash
# Check Docker image exists
docker images code-engine-mcp:latest

# Check API key file exists and is secure
ls -la /Users/ryan/.mcp.env
# Should show: -rw------- (600 permissions)
```

### 2. Ensure .mcp.json in Your Project

Your project needs a `.mcp.json` file:

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

### 3. Use Natural Language

Open Claude Code in your project directory and say:

```
"Deploy this app to Code Engine on port 8080"
```

**That's it!** 🎉

---

## 💬 What You Can Say

### Deploy Applications
```
"Deploy this app to Code Engine on port 8080"
"Create an application from this source code on port 9090 with minimum 2 instances"
"Deploy to dts-account-project on port 3000"
```

### Find Projects
```
"Find my Code Engine project named rst-ce-dev"
"Show me the dts-account-project details"
```

### List Resources
```
"List all my Code Engine projects"
"Show me all applications in project rst-ce-dev"
"What apps are running in dts-account-project"
```

### Get Details
```
"Show me details for app simple-flask-app-demo"
"What's the status of my application"
"Get the endpoint URL for app myapp"
```

---

## 🔐 Security

**Your API key is NEVER exposed** when using MCP tools.

**How it works:**
1. API key stored in `/Users/ryan/.mcp.env` (secure file)
2. Docker loads key via `--env-file` flag
3. Authentication happens inside ephemeral container
4. Container destroyed after each operation
5. No credentials in conversation history

**Security checklist:**
- ✅ API key in `.mcp.env` with 600 permissions
- ✅ `.mcp.env` in `.gitignore` (never committed)
- ✅ Docker `--env-file` mechanism (secure loading)
- ✅ Ephemeral containers (no credential persistence)
- ✅ No API key in command output

---

## 📁 Project Structure

```
your-project/
├── .mcp.json              ← MCP server configuration
├── Dockerfile             ← Your app's Dockerfile
├── app.py                 ← Your application code
├── requirements.txt       ← Python dependencies
└── ...other files

/Users/ryan/.mcp.env       ← API key (secure, not in project)
```

---

## 🛠️ Available Tools (22 Total)

The MCP server provides 22 tools for Code Engine operations:

### Core Deployment (⭐ Most Used)
- **create_app_from_source** - Deploy from source code (NEW!)
- **find_project_by_name** - Find project by name (NEW!)
- **list_projects** - List all projects
- **list_applications** - List apps in project
- **get_application** - Get app details

### Application Management
- create_application
- update_application
- list_app_revisions
- get_app_revision

### Build Management
- create_build
- list_builds
- create_build_run
- get_build_run
- list_build_runs

### Job Management
- list_jobs
- get_job
- list_job_runs
- get_job_run

### Other
- list_domain_mappings
- get_domain_mapping
- list_secrets
- get_secret

---

## 📚 Documentation

**Start here:**
- **`MCP_USAGE_GUIDE.md`** - Complete usage guide with examples
- **`SECURE_API_KEY_GUIDE.md`** - Security best practices

**Implementation details:**
- **`IMPLEMENTATION_SUMMARY.md`** - What was implemented
- **`TESTING_CHECKLIST.md`** - Testing procedures
- **`NEXT_AGENT.md`** - Technical architecture

---

## 🎬 Complete Example

### Scenario: Deploy a New Flask App

**Starting point:** You have a Flask app with a Dockerfile

```bash
my-flask-app/
├── Dockerfile
├── app.py
└── requirements.txt
```

**Steps:**

1. **Navigate to your app:**
   ```bash
   cd ~/projects/my-flask-app
   ```

2. **Ensure .mcp.json exists** (create if needed):
   ```bash
   cp /path/to/example/.mcp.json .
   ```

3. **Open Claude Code:**
   ```bash
   claude-code .
   ```

4. **Deploy with natural language:**
   ```
   "Deploy this Flask app to Code Engine project dts-account-project on port 8080 with minimum 2 instances"
   ```

5. **Claude automatically:**
   - Finds the project "dts-account-project"
   - Gets the project ID
   - Packages your source code
   - Creates a build run
   - Builds the Docker image
   - Deploys with 2 minimum instances
   - Returns the endpoint URL

6. **Verify deployment:**
   ```
   "Show me the application details"
   ```

**Result:**
```
✅ Application deployed successfully!

• Name: my-flask-app
• Project: dts-account-project
• URL: https://my-flask-app.xxx.codeengine.appdomain.cloud
• Status: Running
• Instances: 2
```

**No API key ever shown. No manual commands. Just works.** ✅

---

## ⚠️ Troubleshooting

### "MCP server not available"

```bash
# Rebuild Docker image
cd /Users/ryan/projects/code-engine-cli-skill
docker build -t code-engine-mcp:latest .

# Restart Claude Desktop
```

### "Authentication failed"

```bash
# Verify API key file
cat /Users/ryan/.mcp.env
# Should show: IBMCLOUD_API_KEY=...

# Test API key
export IBMCLOUD_API_KEY=$(cat /Users/ryan/.mcp.env | cut -d'=' -f2)
ibmcloud iam oauth-tokens
```

### "Project not found"

```bash
# List exact project names
ibmcloud ce project list

# Use exact name:
"Find project named dts-account-project"
```

---

## 🚀 Why Use This?

### Traditional Way (Manual CLI)
```bash
export IBMCLOUD_API_KEY=...                    # ❌ Exposes key
ibmcloud ce project select --name myproject
ibmcloud ce app create \
  --name myapp \
  --build-source . \
  --port 8080 \
  --min-scale 2 \
  --max-scale 10 \
  --cpu 0.5 \
  --memory 4G
# Wait for build...
# Copy endpoint URL manually
```

### MCP Server Way (Natural Language)
```
"Deploy this app to Code Engine project myproject on port 8080 with min scale 2"

✅ Done. Endpoint: https://myapp.xxx.codeengine.appdomain.cloud
```

**Benefits:**
- 🎯 One natural language command vs 5+ CLI commands
- 🔒 No API key exposure
- ⚡ Automatic project lookup
- 🤖 Claude handles all the details
- ✅ Clean, simple interface

---

## 🎓 Learning More

### For End Users
1. Read `MCP_USAGE_GUIDE.md` - Complete usage guide
2. Try the examples in this README
3. See `TESTING_CHECKLIST.md` for testing

### For Developers
1. Review `IMPLEMENTATION_SUMMARY.md` - What's implemented
2. Check `NEXT_AGENT.md` - Technical architecture
3. Examine `ce_mcp_server_v3.py` - Server implementation
4. Review `utils.py` - Code Engine SDK wrapper

---

## 📝 Requirements

- Docker Desktop running
- IBM Cloud account with Code Engine access
- IBM Cloud API key (stored in `/Users/ryan/.mcp.env`)
- Claude Code or Claude Desktop
- Project with Dockerfile

---

## 🎉 Success Metrics

**You know it's working when:**

✅ You say "Deploy this app" and it deploys
✅ No API key appears in any output
✅ No manual CLI commands needed
✅ You get back a working endpoint URL
✅ Your app is running in Code Engine

**That's the goal. Simple, secure, effective.**

---

## 📞 Getting Help

**Documentation:**
- `MCP_USAGE_GUIDE.md` - How to use the MCP server
- `SECURE_API_KEY_GUIDE.md` - Security details
- `TESTING_CHECKLIST.md` - Testing procedures

**Common Issues:**
- Docker not running → Start Docker Desktop
- API key missing → Create `/Users/ryan/.mcp.env`
- Old Docker image → Rebuild with `docker build`
- Project not found → Use exact project name

---

## 🏁 TL;DR

**One command to deploy:**
```
"Deploy this app to Code Engine on port 8080"
```

**That's it. No API keys. No manual CLI. Just works.** 🚀

**Start with `MCP_USAGE_GUIDE.md` for complete documentation.**
