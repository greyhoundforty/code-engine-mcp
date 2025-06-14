#!/usr/bin/env python3
"""
Script to validate the JSON schemas in the MCP server
This will find any issues with JSON/Python syntax differences like true vs True
"""

import re
import sys
import ast

def check_file_for_json_booleans(filename):
    """Check a Python file for lowercase true/false that should be True/False"""
    with open(filename, 'r') as f:
        content = f.read()

    # Find potential dictionary literals that might contain 'true' or 'false'
    dict_pattern = r'{\s*[^{}]*?(true|false)[^{}]*?}'
    potential_issues = re.findall(dict_pattern, content, re.MULTILINE | re.DOTALL)

    if potential_issues:
        print(f"Found potential JSON boolean issues in {filename}:")

        # Find all occurrences of lowercase true/false outside of strings
        # This is a simplistic approach and might have false positives/negatives
        lines = content.split('\n')
        issues_found = False

        for i, line in enumerate(lines):
            # Skip comments
            if line.strip().startswith('#'):
                continue

            # Check for true/false not in quotes
            if re.search(r'[^"\']true[^"\']', line) or re.search(r'[^"\']false[^"\']', line):
                print(f"Line {i+1}: {line.strip()}")
                issues_found = True

        if not issues_found:
            print("  No specific issues identified (false positive)")

        return issues_found

    return False

def validate_schema_syntax(filename):
    """Try to parse the Python file and validate schema syntax"""
    try:
        with open(filename, 'r') as f:
            content = f.read()

        # Parse the Python code
        tree = ast.parse(content)
        print(tree)
        print(f"✓ {filename} parses successfully as Python")
        return True
    except SyntaxError as e:
        print(f"✗ Syntax error in {filename}: {e}")
        print(f"  Line {e.lineno}: {e.text}")
        return False

def find_and_extract_schemas(filename):
    """Find and extract JSON schemas from the Python file"""
    with open(filename, 'r') as f:
        content = f.read()

    # Try to find inputSchema dictionaries
    schema_pattern = r'inputSchema\s*=\s*({[^}]+})'
    schemas = re.findall(schema_pattern, content, re.MULTILINE | re.DOTALL)

    if not schemas:
        print(f"No schemas found in {filename}")
        return True

    print(f"Found {len(schemas)} schemas in {filename}")

    # For each schema, replace true/false with True/False and try to evaluate
    issues_found = False
    for i, schema in enumerate(schemas):
        # Replace JSON booleans with Python booleans
        fixed_schema = schema.replace('true', 'True').replace('false', 'False')

        try:
            # Try to evaluate the schema as a Python dictionary
            eval(fixed_schema)
            print(f"  Schema {i+1}: Valid after fixing booleans")
        except Exception as e:
            print(f"  Schema {i+1}: Invalid - {e}")
            issues_found = True

    return not issues_found

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validate_schemas.py <filename>")
        sys.exit(1)

    filename = sys.argv[1]

    json_issues = check_file_for_json_booleans(filename)
    syntax_ok = validate_schema_syntax(filename)
    schemas_ok = find_and_extract_schemas(filename)

    if json_issues or not syntax_ok or not schemas_ok:
        print("\nIssues found. Fix the JSON/Python boolean values (true → True, false → False)")
        sys.exit(1)
    else:
        print("\nNo issues found!")
        sys.exit(0)
