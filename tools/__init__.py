"""
Import all domain modules to trigger their register() calls.

Importing `tools` (or `from tools import registry`) is sufficient to
populate the registry with all 37 tools.
"""

from tools import (  # noqa: F401
    applications,
    bindings,
    builds,
    configmaps,
    domains,
    functions,
    jobs,
    projects,
    secrets,
)
