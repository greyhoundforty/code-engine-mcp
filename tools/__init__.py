"""
Import all domain modules to trigger their register() calls.

Importing `tools` (or `from tools import registry`) is sufficient to
populate the registry with all 22 tools.
"""

from tools import applications, builds, domains, jobs, projects, secrets  # noqa: F401
