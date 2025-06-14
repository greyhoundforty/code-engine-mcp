# Pre-commit Hooks Guide

This guide provides instructions for setting up pre-commit hooks in the IBM Code Engine MCP Server project, focusing on pylint for code quality and secret scanning for security.

## What are Pre-commit Hooks?

Pre-commit hooks are scripts that run automatically before each git commit to ensure code quality, prevent secrets from being committed, and maintain consistent formatting. They help catch issues early in the development process.

## Installation

### 1. Install pre-commit

First, install the pre-commit package:

```bash
pip install pre-commit
```

Or add it to your development requirements:

```bash
# requirements-dev.txt
pre-commit==3.5.0
```

### 2. Create a pre-commit configuration file

Create a `.pre-commit-config.yaml` file in the root of your repository:

```yaml
# .pre-commit-config.yaml
repos:
-   repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
    -   id: trailing-whitespace
    -   id: end-of-file-fixer
    -   id: check-yaml
    -   id: check-added-large-files
    -   id: check-json
    -   id: debug-statements

-   repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.1.5
    hooks:
    -   id: ruff
        args: [--fix, --exit-non-zero-on-fix]

-   repo: https://github.com/pycqa/pylint
    rev: v3.0.1
    hooks:
    -   id: pylint
        name: pylint
        entry: pylint
        language: system
        types: [python]
        args: [
            "--rcfile=.pylintrc",  # Use your pylint config file
            "--disable=C0111",     # Missing docstring
            "--disable=C0103",     # Invalid name
            "--disable=C0330",     # Wrong hanging indentation
            "--disable=C0326",     # Bad whitespace
        ]

-   repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.1
    hooks:
    -   id: gitleaks

-   repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
    -   id: detect-secrets
        args: ['--baseline', '.secrets.baseline']

-   repo: local
    hooks:
    -   id: pytest-check
        name: pytest-check
        entry: pytest
        language: system
        pass_filenames: false
        always_run: true
        args: [
            "tests/",
            "-xvs"
        ]
```

### 3. Create a pylint configuration file

Create a `.pylintrc` file in the root of your repository:

```ini
[MASTER]
ignore=CVS
ignore-patterns=
persistent=yes
load-plugins=
jobs=1
unsafe-load-any-extension=no
extension-pkg-whitelist=

[MESSAGES CONTROL]
disable=
    C0111, # missing docstring
    C0103, # invalid name
    C0330, # wrong hanging indentation
    C0326, # bad whitespace
    W0511, # fixme
    R0903, # too few public methods
    R0913, # too many arguments
    R0914, # too many local variables
    R0915, # too many statements
    R1705, # unnecessary else after return
    W0212, # access to a protected member
    W0703, # broad except
    W1201, # specify string format arguments as logging function parameters
    W1202  # use % formatting in logging functions

[REPORTS]
output-format=text
reports=yes
evaluation=10.0 - ((float(5 * error + warning + refactor + convention) / statement) * 10)

[BASIC]
good-names=i,j,k,ex,Run,_,id
bad-names=foo,bar,baz,toto,tutu,tata
name-group=
include-naming-hint=no
function-rgx=[a-z_][a-z0-9_]{2,30}$
function-name-hint=[a-z_][a-z0-9_]{2,30}$
variable-rgx=[a-z_][a-z0-9_]{2,30}$
variable-name-hint=[a-z_][a-z0-9_]{2,30}$
const-rgx=(([A-Z_][A-Z0-9_]*)|(__.*__))$
const-name-hint=(([A-Z_][A-Z0-9_]*)|(__.*__))$
attr-rgx=[a-z_][a-z0-9_]{2,30}$
attr-name-hint=[a-z_][a-z0-9_]{2,30}$
argument-rgx=[a-z_][a-z0-9_]{2,30}$
argument-name-hint=[a-z_][a-z0-9_]{2,30}$
class-rgx=[A-Z_][a-zA-Z0-9]+$
class-name-hint=[A-Z_][a-zA-Z0-9]+$
inlinevar-rgx=[A-Za-z_][A-Za-z0-9_]*$
inlinevar-name-hint=[A-Za-z_][A-Za-z0-9_]*$
no-docstring-rgx=^_
docstring-min-length=-1

[FORMAT]
max-line-length=100
ignore-long-lines=^\s*(# )?<?https?://\S+>?$
single-line-if-stmt=no
no-space-check=trailing-comma,dict-separator
max-module-lines=1000
indent-string='    '
indent-after-paren=4
expected-line-ending-format=

[SIMILARITIES]
min-similarity-lines=4
ignore-comments=yes
ignore-docstrings=yes
ignore-imports=yes

[TYPECHECK]
ignore-mixin-members=yes
ignored-classes=SQLObject
unsafe-load-any-extension=yes
generated-members=REQUEST,acl_users,aq_parent

[VARIABLES]
init-import=no
dummy-variables-rgx=_$|dummy
additional-builtins=
callbacks=cb_,_cb

[DESIGN]
max-args=5
ignored-argument-names=_.*
max-locals=15
max-returns=6
max-branches=12
max-statements=50
max-parents=7
max-attributes=7
min-public-methods=2
max-public-methods=20

[CLASSES]
ignore-iface-methods=isImplementedBy,deferred,extends,names,namesAndDescriptions,queryDescriptionFor,getBases,getDescriptionFor,getDoc,getName,getTaggedValue,getTaggedValueTags,isEqualOrExtendedBy,setTaggedValue,isImplementedByInstancesOf,adaptWith,is_implemented_by
defining-attr-methods=__init__,__new__,setUp
valid-classmethod-first-arg=cls
valid-metaclass-classmethod-first-arg=mcs

[IMPORTS]
deprecated-modules=regsub,TERMIOS,Bastion,rexec
import-graph=
ext-import-graph=
int-import-graph=

[EXCEPTIONS]
overgeneral-exceptions=Exception
```

### 4. Initialize secret scanning baseline

For `detect-secrets`, you need to create a baseline file:

```bash
detect-secrets scan > .secrets.baseline
```

### 5. Install the pre-commit hooks

Install the hooks into your git repository:

```bash
pre-commit install
```

## Usage

Once installed, pre-commit hooks will run automatically whenever you attempt to commit changes. If any hook fails, the commit will be aborted, allowing you to fix the issues before trying again.

### Manual Running

You can also run the hooks manually:

```bash
# Run all hooks on all files
pre-commit run --all-files

# Run a specific hook
pre-commit run pylint --all-files
pre-commit run detect-secrets --all-files
```

### Skipping Hooks

In rare cases, you may need to skip hooks for a specific commit:

```bash
git commit -m "Your message" --no-verify
```

⚠️ **Warning**: Only skip hooks when absolutely necessary. Using `--no-verify` bypasses all checks and may lead to committing secrets or low-quality code.

## Secret Scanning Customization

### Detect-secrets

You can customize the `detect-secrets` configuration in the `.secrets.baseline` file:

```bash
# Update baseline with new rules
detect-secrets scan --update .secrets.baseline

# Add specific exceptions (e.g., for test files)
detect-secrets scan --exclude-files 'tests/fixtures/.*' > .secrets.baseline
```

### Gitleaks

Gitleaks can be customized by creating a `.gitleaks.toml` file:

```toml
# .gitleaks.toml
title = "Gitleaks Config"

[[rules]]
id = "ibm-api-key"
description = "IBM Cloud API Key"
regex = '''(?i)(?:ibm)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\s|']|[\s|"]){0,3}(?:=|>|:=|\|\|:|<=|=>|:)(?:'|\"|\s|=|\x60){0,5}([a-zA-Z0-9]{44})(?:['|\"|\n|\r|\s|\x60|;]|$)'''
secretGroup = 1
entropy = 3.5
```

## Adding to CI/CD Pipeline

For continuous integration, add pre-commit to your CI workflow:

### GitHub Actions Example

Create a file `.github/workflows/pre-commit.yml`:

```yaml
name: Pre-commit checks

on:
  push:
    branches: [ main, master ]
  pull_request:
    branches: [ main, master ]

jobs:
  pre-commit:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install pre-commit
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    - name: Run pre-commit
      run: pre-commit run --all-files
```

## Integration with mise

Add pre-commit tasks to your `.mise.toml` file:

```toml
[tasks.precommit-install]
description = "Install pre-commit hooks"
run = "pre-commit install"

[tasks.precommit-run]
description = "Run all pre-commit hooks"
alias = "pc"
run = "pre-commit run --all-files"

[tasks.precommit-update]
description = "Update pre-commit hooks"
run = "pre-commit autoupdate"

[tasks.lint]
description = "Run pylint"
run = "pylint ce_mcp_server.py utils.py tests/"
```

## Best Practices

1. **Run hooks frequently** - Don't wait until commit time to run checks
2. **Keep hooks fast** - Optimize hooks to run quickly to avoid disrupting workflow
3. **Update regularly** - Keep hooks updated to catch new issues
4. **Educate team members** - Ensure everyone understands why hooks are important
5. **Document exceptions** - If certain patterns trigger false positives, document why they're allowed

## Troubleshooting

### Common Issues

- **Hooks taking too long**: Consider excluding large files or using more targeted hooks
- **False positives in secret detection**: Update your baseline file or add specific exclusions
- **Inconsistent behavior**: Ensure all developers use the same pre-commit version
- **Hook not running**: Verify hooks are installed with `pre-commit install`

### Getting Help

If you're having issues with specific hooks:

```bash
pre-commit run --verbose [hook-id]
```

This will show detailed output about what's happening during hook execution.
