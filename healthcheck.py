import sys
import subprocess

try:
    # Basic import test
    import ce_mcp_server
    import utils
    print("Health check passed: All modules import successfully")
    sys.exit(0)
except Exception as e:
    print(f"Health check failed: {e}")
    sys.exit(1)
EOF
