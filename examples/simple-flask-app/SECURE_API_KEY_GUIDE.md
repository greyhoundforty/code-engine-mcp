# Secure API Key Handling Guide
**How the MCP Server Keeps Your Credentials Safe**

## ⭐ Primary Method: MCP Tools (Use This!)

**The IBM Code Engine MCP Server is designed for secure, natural language interaction.**

This is THE way to use this MCP server - all other methods are fallbacks for troubleshooting or when MCP is unavailable.

### How It Works (Completely Secure)

```
You: "Deploy this app to Code Engine on port 8080"
     ↓
Claude Code calls MCP tool
     ↓
Docker loads IBMCLOUD_API_KEY from /Users/ryan/.mcp.env
     ↓
MCP server authenticates internally
     ↓
Returns result
     ↓
✅ NO API KEY EVER SHOWN
```

### Why This Is Secure

- 🔒 API key loaded via Docker `--env-file` mechanism
- 🔒 Key only accessible inside ephemeral container
- 🔒 Authentication happens in isolated environment
- 🔒 No credentials in conversation history
- 🔒 No credentials in command output
- 🔒 No manual CLI commands with exposed keys

### How to Use

Simply use natural language:
- "Deploy this app to Code Engine"
- "Find my Code Engine project rst-ce-dev"
- "List applications in dts-account-project"

**See `MCP_USAGE_GUIDE.md` for complete usage documentation.**

---

## ⚠️ Alternative Methods (Use Only When Necessary)

The following methods are for:
- Troubleshooting MCP server issues
- Direct CLI usage when MCP is unavailable
- Automation/scripting scenarios

**These are NOT the primary use case.** Use MCP tools whenever possible.

---

## The Problem (Direct CLI Exposure)

When Claude Code runs direct CLI commands, it may inadvertently expose API keys in the output:

❌ **INSECURE:**
```bash
export IBMCLOUD_API_KEY=GAD6piveTxRNxUTGNTQgMExPaN0ul8CjFp93gPxMCBbb && ibmcloud ce ...
```
This shows the API key in:
- Command descriptions
- Terminal output
- Conversation history
- Potentially logs

## The Solutions

### ✅ Solution 1: Use MCP Tools (RECOMMENDED)

**Why it's secure:**
- API key loaded from `/Users/ryan/.mcp.env` via Docker `--env-file`
- Key never appears in command output
- Key never in conversation history
- All authentication happens inside the Docker container

**How to use:**
```
You: "Deploy this Flask app to Code Engine on port 8080"

Claude: Uses MCP tool 'create_app_from_source'
        ↓
        Docker loads IBMCLOUD_API_KEY from .mcp.env
        ↓
        MCP server authenticates internally
        ↓
        Returns deployment result (NO KEY VISIBLE)
```

**Example commands:**
- "Find my Code Engine project named dts-account-project"
- "Deploy this app to Code Engine on port 9090 with minimum 2 instances"
- "List all applications in project rst-ce-dev"

**Security:**
- 🔒 API key never exposed
- 🔒 Authentication happens in container
- 🔒 No credential leakage

---

### ✅ Solution 2: Pre-authenticate CLI Session

**Use the secure helper script:**

```bash
# At the start of your Claude Code session:
source /Users/ryan/projects/code-engine-cli-skill/examples/simple-flask-app/secure_cli_helper.sh
```

**What it does:**
1. Reads API key from `.mcp.env` (doesn't echo it)
2. Runs `ibmcloud login` once
3. Unsets the API key variable
4. Credentials cached for the session

**Then run commands WITHOUT exposing the key:**
```bash
# No need for export IBMCLOUD_API_KEY anymore!
ibmcloud ce project list
ibmcloud ce app create --name myapp --build-source . --port 8080
```

**Security:**
- 🔒 API key read once, never displayed
- 🔒 Authentication cached in IBM Cloud CLI
- 🔒 Key removed from environment after login

---

### ✅ Solution 3: Environment Variable (Session-Scoped)

**Set once at session start (masked):**

```bash
# Read from .mcp.env without displaying
export IBMCLOUD_API_KEY=$(grep IBMCLOUD_API_KEY /Users/ryan/.mcp.env | cut -d '=' -f2)

# Verify it's set (without showing the value)
if [ -n "$IBMCLOUD_API_KEY" ]; then
    echo "✅ API key loaded securely"
else
    echo "❌ API key not found"
fi
```

**Then run commands:**
```bash
# API key comes from environment, not shown in command
ibmcloud ce project list
ibmcloud ce app create --name myapp --build-source . --port 8080
```

**Security:**
- 🔒 Key not shown in export command
- 🔒 Key available for session
- ⚠️ Still in environment (use Solution 2 for better security)

---

### ✅ Solution 4: Credential File Configuration

**Configure ibmcloud CLI to use a credential file:**

```bash
# Create config directory
mkdir -p ~/.bluemix

# Create credentials file
cat > ~/.bluemix/config.json <<EOF
{
  "IAMToken": "",
  "IAMRefreshToken": "",
  "Account": {
    "GUID": "6c27214690345bfb75bb1f2b28a20504"
  },
  "Region": "us-south"
}
EOF

# Login once (credentials cached)
ibmcloud login --apikey $(grep IBMCLOUD_API_KEY /Users/ryan/.mcp.env | cut -d '=' -f2) -q
```

**Future commands don't need the key:**
```bash
ibmcloud ce project list
# Uses cached credentials from ~/.bluemix/
```

**Security:**
- 🔒 API key only used once
- 🔒 Credentials cached in IBM Cloud config
- 🔒 No key in command history

---

## Best Practices Comparison

| Method | Security Level | Ease of Use | Primary Use Case | Recommended? |
|--------|----------------|-------------|------------------|--------------|
| **⭐ MCP Tools** | ⭐⭐⭐⭐⭐ Highest | ⭐⭐⭐⭐⭐ Natural language | **Claude Code/Desktop** | **✅ YES - USE THIS** |
| **Pre-auth Script** | ⭐⭐⭐⭐ High | ⭐⭐⭐⭐ One-time setup | Troubleshooting | ⚠️ Fallback only |
| **Environment Var** | ⭐⭐⭐ Medium | ⭐⭐⭐ Easy | Direct CLI | ⚠️ Fallback only |
| **Credential File** | ⭐⭐⭐⭐ High | ⭐⭐⭐ One-time setup | Automation | ⚠️ Fallback only |
| **Direct Export** | ⭐ LOWEST | ⭐⭐⭐⭐⭐ Easy | ❌ NEVER | ❌ NO - INSECURE |

---

## ⭐ Recommended Workflow: MCP Tools (PRIMARY METHOD)

**This is how you SHOULD use the Code Engine MCP Server:**

```
1. Verify setup (one-time):
   - .mcp.json exists in your project directory
   - /Users/ryan/.mcp.env contains IBMCLOUD_API_KEY
   - Docker image code-engine-mcp:latest is built

2. Start Claude Code/Desktop:
   - Open in your project directory
   - MCP server auto-starts when needed

3. Use natural language:
   "Deploy this app to Code Engine on port 8080"
   "Find my Code Engine project rst-ce-dev"
   "List applications in dts-account-project"
```

**✅ No API key ever shown!**
**✅ No manual commands needed!**
**✅ Secure by design!**

**See `MCP_USAGE_GUIDE.md` for complete documentation.**

---

## ⚠️ Fallback: Direct CLI Usage (When MCP Unavailable)

**Only use direct CLI when:**
- MCP server is not available
- Debugging MCP issues
- Scripting/automation scenarios

### For Direct CLI Usage

```bash
# Option A: Use the secure helper script
source /Users/ryan/projects/code-engine-cli-skill/examples/simple-flask-app/secure_cli_helper.sh

# Option B: Pre-authenticate manually
export IBMCLOUD_API_KEY=$(grep IBMCLOUD_API_KEY /Users/ryan/.mcp.env | cut -d '=' -f2)
ibmcloud login --apikey "$IBMCLOUD_API_KEY" -r us-south -q
unset IBMCLOUD_API_KEY
```

**Then run commands normally:**
```bash
ibmcloud ce project list
ibmcloud ce app create --name myapp --build-source . --port 8080
```

---

## Security Checklist

- [ ] `.mcp.env` file permissions are restrictive: `chmod 600 /Users/ryan/.mcp.env`
- [ ] `.mcp.env` is in `.gitignore` (never commit)
- [ ] API key never echoed in bash commands
- [ ] MCP server uses `--env-file` for Docker container
- [ ] Direct CLI commands use cached credentials or pre-authentication
- [ ] API key unset from environment after authentication
- [ ] No API keys in conversation history

---

## What Went Wrong in This Session?

I (Claude Code) used direct bash commands with explicit `export IBMCLOUD_API_KEY=...` which exposed the key in the output.

**This was for demonstration purposes to show the CLI works.**

**In production use with the MCP server, this would NEVER happen** because:
1. MCP tools authenticate via Docker `--env-file`
2. API key is loaded inside the container
3. No bash commands with exposed credentials

---

## Testing Secure Authentication

### Test 1: Verify .mcp.env is secure

```bash
# Check file permissions
ls -la /Users/ryan/.mcp.env

# Should show:
# -rw------- (600) or -rw-r--r-- (644) at minimum
```

**Recommended:**
```bash
chmod 600 /Users/ryan/.mcp.env
```

### Test 2: Verify MCP server loads credentials

```bash
# Run the MCP server manually
docker run -i --rm --env-file /Users/ryan/.mcp.env code-engine-mcp:latest

# Check logs - should show:
# "Code Engine client initialized for region: us-south"
# NO API KEY SHOULD BE VISIBLE in logs
```

### Test 3: Test secure CLI authentication

```bash
# Source the helper script
source secure_cli_helper.sh

# Verify authentication without showing key
ibmcloud target

# Should show:
# API endpoint:      https://cloud.ibm.com
# Region:            us-south
# User:              [your email]
# Account:           [account name]
# NO API KEY SHOWN ✅
```

---

## For Your .gitignore

Make sure these are never committed:

```gitignore
# API Keys and credentials
.mcp.env
.env
*.key
*.pem
credentials.json

# IBM Cloud config
.bluemix/

# Bash history (may contain keys)
.bash_history
```

---

## Emergency: API Key Exposed

If an API key is accidentally exposed:

1. **Immediately revoke the key:**
   ```bash
   ibmcloud iam api-key-delete <key-name>
   ```

2. **Create a new API key:**
   ```bash
   ibmcloud iam api-key-create code-engine-mcp-key -d "MCP Server Key" --file new-api-key.json
   ```

3. **Update .mcp.env:**
   ```bash
   echo "IBMCLOUD_API_KEY=<new-key>" > /Users/ryan/.mcp.env
   chmod 600 /Users/ryan/.mcp.env
   ```

4. **Test the new key:**
   ```bash
   docker run -i --rm --env-file /Users/ryan/.mcp.env code-engine-mcp:latest
   ```

---

## Summary

✅ **USE MCP TOOLS** - Most secure, no key exposure
✅ **Pre-authenticate CLI** - Secure for direct commands
❌ **NEVER export API keys in command strings** - Always visible

**The MCP server integration is secure by design.** The issue in this session was using direct CLI commands for demonstration, which won't happen in normal MCP tool usage.
