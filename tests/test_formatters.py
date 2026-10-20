#!/usr/bin/env python3
"""
Tests for utils.py formatter functions
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils import (  # noqa: E402
    format_project_summary,
    format_apps_summary,
    format_app_revisions_summary,
    format_domain_mappings_summary,
    format_secrets_summary,
    format_builds_summary,
    format_build_runs_summary,
    format_jobs_summary,
    format_job_runs_summary,
    mask_sensitive_data,
    format_config_maps_summary,
    format_functions_summary,
    format_bindings_summary,
)

# ---------------------------------------------------------------------------
# Shared fixtures (plain dicts — no pytest fixtures needed here)
# ---------------------------------------------------------------------------

PROJECTS = [
    {"id": "p1", "name": "my-project", "region": "us-south", "status": "active", "created_at": "2025-01-01T00:00:00Z"},
]

APPS = [
    {"name": "my-app", "status": "ready", "image_reference": "nginx:latest", "created_at": "2025-01-01T00:00:00Z", "endpoint": "https://my-app.example.com"},
]

REVISIONS = [
    {"name": "my-app-00001", "status": "ready", "created_at": "2025-01-01T00:00:00Z", "scale_config": {"min_scale": 1, "max_scale": 5}},
    {"name": "my-app-00002", "status": "ready", "created_at": "2025-01-02T00:00:00Z"},
]

DOMAIN_MAPPINGS = [
    {"name": "app.example.com", "status": "ready", "created_at": "2025-01-01T00:00:00Z", "target": {"type": "app", "name": "my-app"}},
]

SECRETS = [
    {"name": "my-secret", "format": "generic", "created_at": "2025-01-01T00:00:00Z", "data": {"API_KEY": "***MASKED***", "DB_PASS": "***MASKED***"}},
]

BUILDS = [
    {"name": "my-build", "output_image": "icr.io/ns/app:latest", "source_url": "https://github.com/user/repo", "strategy_type": "dockerfile", "created_at": "2025-01-01T00:00:00Z"},
]

BUILD_RUNS = [
    {"name": "my-build-run-001", "status": "succeeded", "build_name": "my-build", "created_at": "2025-01-01T00:00:00Z", "output_image": "icr.io/ns/app:latest"},
    {"name": "my-build-run-002", "status": "running", "build_name": "my-build", "created_at": "2025-01-02T00:00:00Z"},
]

JOBS = [
    {"name": "my-job", "status": "ready", "image_reference": "batch:latest", "created_at": "2025-01-01T00:00:00Z"},
]

JOB_RUNS = [
    {"name": "my-job-run-001", "status": "succeeded", "job_name": "my-job", "created_at": "2025-01-01T00:00:00Z", "completion_time": "2025-01-01T01:00:00Z"},
]


# ---------------------------------------------------------------------------
# format_project_summary
# ---------------------------------------------------------------------------

def test_format_project_summary_with_data():
    result = format_project_summary(PROJECTS)
    assert "Found 1 Code Engine projects" in result
    assert "my-project" in result
    assert "us-south" in result
    assert "active" in result


def test_format_project_summary_empty():
    assert format_project_summary([]) == "No projects found."


# ---------------------------------------------------------------------------
# format_apps_summary
# ---------------------------------------------------------------------------

def test_format_apps_summary_with_data():
    result = format_apps_summary(APPS)
    assert "Found 1 applications" in result
    assert "my-app" in result
    assert "nginx:latest" in result
    assert "https://my-app.example.com" in result


def test_format_apps_summary_empty():
    result = format_apps_summary([])
    assert "No applications found" in result


def test_format_apps_summary_with_project_name():
    result = format_apps_summary(APPS, project_name="my-project")
    assert "in project my-project" in result


# ---------------------------------------------------------------------------
# format_app_revisions_summary
# ---------------------------------------------------------------------------

def test_format_app_revisions_summary_with_data():
    result = format_app_revisions_summary(REVISIONS, app_name="my-app")
    assert "Found 2 revisions for application my-app" in result
    assert "my-app-00001" in result
    assert "my-app-00002" in result
    # First revision has scale_config
    assert "Scale: 1-5 instances" in result


def test_format_app_revisions_summary_empty():
    result = format_app_revisions_summary([], app_name="my-app", project_id="p1")
    assert "No revisions found" in result
    assert "my-app" in result
    assert "p1" in result


def test_format_app_revisions_summary_no_scale_config():
    revisions = [{"name": "rev-1", "status": "ready", "created_at": "2025-01-01T00:00:00Z"}]
    result = format_app_revisions_summary(revisions, app_name="my-app")
    assert "rev-1" in result
    assert "Scale:" not in result


# ---------------------------------------------------------------------------
# format_domain_mappings_summary
# ---------------------------------------------------------------------------

def test_format_domain_mappings_summary_with_data():
    result = format_domain_mappings_summary(DOMAIN_MAPPINGS, project_id="p1")
    assert "Found 1 domain mappings in project p1" in result
    assert "app.example.com" in result
    assert "Target: app - my-app" in result


def test_format_domain_mappings_summary_empty():
    result = format_domain_mappings_summary([], project_id="p1")
    assert "No domain mappings found in project p1" in result


def test_format_domain_mappings_summary_no_target():
    mappings = [{"name": "example.com", "status": "ready", "created_at": "2025-01-01T00:00:00Z"}]
    result = format_domain_mappings_summary(mappings)
    assert "example.com" in result
    assert "Target:" not in result


# ---------------------------------------------------------------------------
# format_secrets_summary
# ---------------------------------------------------------------------------

def test_format_secrets_summary_with_data():
    result = format_secrets_summary(SECRETS, project_id="p1")
    assert "Found 1 secrets in project p1" in result
    assert "my-secret" in result
    assert "generic" in result
    assert "API_KEY" in result
    assert "DB_PASS" in result


def test_format_secrets_summary_empty():
    result = format_secrets_summary([], project_id="p1")
    assert "No secrets found in project p1" in result


def test_format_secrets_summary_no_data_keys():
    secrets = [{"name": "empty-secret", "format": "generic", "created_at": "2025-01-01T00:00:00Z"}]
    result = format_secrets_summary(secrets)
    assert "empty-secret" in result
    assert "Keys:" not in result


# ---------------------------------------------------------------------------
# format_builds_summary
# ---------------------------------------------------------------------------

def test_format_builds_summary_with_data():
    result = format_builds_summary(BUILDS, project_id="p1")
    assert "Found 1 build configurations in project p1" in result
    assert "my-build" in result
    assert "icr.io/ns/app:latest" in result
    assert "https://github.com/user/repo" in result
    assert "dockerfile" in result


def test_format_builds_summary_empty():
    result = format_builds_summary([], project_id="p1")
    assert "No build configurations found in project p1" in result


# ---------------------------------------------------------------------------
# format_build_runs_summary
# ---------------------------------------------------------------------------

def test_format_build_runs_summary_with_data():
    result = format_build_runs_summary(BUILD_RUNS, build_name="my-build", project_id="p1")
    assert "Found 2 build runs for build 'my-build' in project p1" in result
    assert "my-build-run-001" in result
    assert "succeeded" in result
    assert "icr.io/ns/app:latest" in result
    # Second run has no output_image
    assert "my-build-run-002" in result


def test_format_build_runs_summary_empty():
    result = format_build_runs_summary([], build_name="my-build", project_id="p1")
    assert "No build runs found for build 'my-build' in project p1" in result


def test_format_build_runs_summary_no_filter():
    result = format_build_runs_summary(BUILD_RUNS, project_id="p1")
    assert "Found 2 build runs in project p1" in result
    # No build name context when not filtered
    assert "for build" not in result


# ---------------------------------------------------------------------------
# format_jobs_summary
# ---------------------------------------------------------------------------

def test_format_jobs_summary_with_data():
    result = format_jobs_summary(JOBS)
    assert "Found 1 batch jobs" in result
    assert "my-job" in result


def test_format_jobs_summary_empty():
    result = format_jobs_summary([])
    assert "No batch jobs found" in result


# ---------------------------------------------------------------------------
# format_job_runs_summary
# ---------------------------------------------------------------------------

def test_format_job_runs_summary_with_data():
    result = format_job_runs_summary(JOB_RUNS, job_name="my-job")
    assert "Found 1 job runs for job my-job" in result
    assert "my-job-run-001" in result
    assert "succeeded" in result


def test_format_job_runs_summary_empty():
    result = format_job_runs_summary([], job_name="my-job")
    assert "No job runs found for job my-job" in result


# ---------------------------------------------------------------------------
# mask_sensitive_data
# ---------------------------------------------------------------------------

def test_mask_sensitive_data_masks_values():
    secret = {"name": "my-secret", "data": {"KEY": "plaintext-value", "PASS": "another-value"}}
    result = mask_sensitive_data(secret)
    assert result["data"]["KEY"] == "***MASKED***"
    assert result["data"]["PASS"] == "***MASKED***"
    # Name is not masked
    assert result["name"] == "my-secret"


def test_mask_sensitive_data_no_data_field():
    secret = {"name": "my-secret", "format": "generic"}
    result = mask_sensitive_data(secret)
    assert result == secret


def test_mask_sensitive_data_does_not_mutate_original():
    secret = {"name": "my-secret", "data": {"KEY": "original-value"}}
    mask_sensitive_data(secret)
    assert secret["data"]["KEY"] == "original-value"


# ---------------------------------------------------------------------------
# format_config_maps_summary
# ---------------------------------------------------------------------------

def test_format_config_maps_summary_with_data():
    cms = [
        {"name": "my-cm", "data": {"HOST": "db.example.com", "PORT": "5432"}, "created_at": "2025-01-01"},
    ]
    result = format_config_maps_summary(cms, project_id="proj1")
    assert "1 configmap" in result
    assert "my-cm" in result
    assert "HOST" in result
    assert "PORT" in result
    assert "proj1" in result


def test_format_config_maps_summary_empty():
    result = format_config_maps_summary([], project_id="proj1")
    assert "No configmaps" in result
    assert "proj1" in result


def test_format_config_maps_summary_no_data_field():
    cms = [{"name": "empty-cm", "created_at": "2025-01-01"}]
    result = format_config_maps_summary(cms)
    assert "empty-cm" in result
    assert "(empty)" in result


# ---------------------------------------------------------------------------
# format_functions_summary
# ---------------------------------------------------------------------------

def test_format_functions_summary_with_data():
    functions = [
        {
            "name": "my-fn",
            "runtime": "nodejs-20",
            "status": "ready",
            "endpoint": "https://my-fn.example.com",
            "created_at": "2025-01-01",
        }
    ]
    result = format_functions_summary(functions, project_id="proj1")
    assert "1 function" in result
    assert "my-fn" in result
    assert "nodejs-20" in result
    assert "ready" in result
    assert "https://my-fn.example.com" in result


def test_format_functions_summary_empty():
    result = format_functions_summary([], project_id="proj1")
    assert "No functions" in result
    assert "proj1" in result


def test_format_functions_summary_no_endpoint():
    functions = [{"name": "fn-no-ep", "runtime": "python-3.11", "status": "ready", "created_at": "2025-01-01"}]
    result = format_functions_summary(functions)
    assert "fn-no-ep" in result
    assert "python-3.11" in result


# ---------------------------------------------------------------------------
# format_bindings_summary
# ---------------------------------------------------------------------------

def test_format_bindings_summary_with_data():
    bindings = [
        {
            "id": "binding-abc",
            "component": {"name": "my-app", "resource_type": "app_v2"},
            "prefix": "COS",
            "secret_name": "my-cos-secret",  # pragma: allowlist secret
            "status": "active",
        }
    ]
    result = format_bindings_summary(bindings, project_id="proj1")
    assert "1 service binding" in result
    assert "binding-abc" in result
    assert "my-app" in result
    assert "app_v2" in result
    assert "COS" in result
    assert "my-cos-secret" in result


def test_format_bindings_summary_empty():
    result = format_bindings_summary([], project_id="proj1")
    assert "No service bindings" in result
    assert "proj1" in result
