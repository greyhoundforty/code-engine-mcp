# Overview

This is a guide to using the IBM Code Engine API with the Python SDK. These examples serve as a base for Claude to interact with the Code Engine service, allowing you to manage projects, applications, and revisions.

## Prerequisites

- Python 3.10 or later
- `ibm-code-engine-sdk` package installed

## Authentication

```python
from ibm_code_engine_sdk.code_engine_v2 import *
from ibm_cloud_sdk_core import ApiException
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

authenticator = IAMAuthenticator(apikey=ibmcloud_api_key)

service = CodeEngineV2(authenticator=authenticator)
service.set_service_url('https://api.'+REGION+'.codeengine.cloud.ibm.com/v2')
```

## List all projects

```python
all_results = []
pager = ProjectsPager(
    client=code_engine_service,
    limit=100,
)
while pager.has_next():
    next_page = pager.get_next()
    assert next_page is not None
    all_results.extend(next_page)

print(json.dumps(all_results, indent=2))
```

## List applications in a project

```python
all_results = []
pager = AppsPager(
    client=code_engine_service,
    project_id='PROJECT_ID',
    limit=100,
)
while pager.has_next():
    next_page = pager.get_next()
    assert next_page is not None
    all_results.extend(next_page)

print(json.dumps(all_results, indent=2))
```

## Get an application

```python
response = code_engine_service.get_app(
    project_id='PROJECT_ID',
    name='my-app',
)
app = response.get_result()

print(json.dumps(app, indent=2))
```

## List application revisions

```python
all_results = []
pager = AppRevisionsPager(
    client=code_engine_service,
    project_id='15314cc3-85b4-4338-903f-c28cdee6d005',
    app_name='my-app',
    limit=100,
)
while pager.has_next():
    next_page = pager.get_next()
    assert next_page is not None
    all_results.extend(next_page)

print(json.dumps(all_results, indent=2))
```

## Get an application revision

```python
response = code_engine_service.get_app_revision(
    project_id='15314cc3-85b4-4338-903f-c28cdee6d005',
    app_name='my-app',
    name='my-app-00001',
)
app_revision = response.get_result()

print(json.dumps(app_revision, indent=2))
```

## Update an application revision

```python
app_patch_model = {
  "image_reference": "icr.io/codeengine/hello"
}

response = code_engine_service.update_app(
    project_id='15314cc3-85b4-4338-903f-c28cdee6d005',
    name='my-app',
    if_match='testString',
    app=app_patch_model,
)
app = response.get_result()

print(json.dumps(app, indent=2))
```

## List all Domain mappings

```python
all_results = []
pager = DomainMappingsPager(
    client=code_engine_service,
    project_id='15314cc3-85b4-4338-903f-c28cdee6d005',
    limit=100,
)
while pager.has_next():
    next_page = pager.get_next()
    assert next_page is not None
    all_results.extend(next_page)

print(json.dumps(all_results, indent=2))
```

## Get a Domain mapping

```python
response = code_engine_service.get_domain_mapping(
    project_id='15314cc3-85b4-4338-903f-c28cdee6d005',
    name='www.example.com',
)
domain_mapping = response.get_result()

print(json.dumps(domain_mapping, indent=2))
```

## Create a Domain mapping

```python

component_ref_model = {
    'name': 'my-app-1',
    'resource_type': 'app_v2',
}

response = code_engine_service.create_domain_mapping(
    project_id='15314cc3-85b4-4338-903f-c28cdee6d005',
    component=component_ref_model,
    name='www.example.com',
    tls_secret='my-tls-secret',
)
domain_mapping = response.get_result()

print(json.dumps(domain_mapping, indent=2))
```

## List all Code Engine secrets

```python
all_results = []
pager = SecretsPager(
    client=code_engine_service,
    project_id='PROJECT_ID',
    limit=100,
)
while pager.has_next():
    next_page = pager.get_next()
    assert next_page is not None
    all_results.extend(next_page)

print(json.dumps(all_results, indent=2))
```

## Get a Code Engine secret

```python
response = code_engine_service.get_secret(
    project_id='PROJECT_ID',
    name='my-secret',


```

## Create a generic Code Engine secret

```python
secret_data = {
    "username": "my-username",
    "password": "my-password",
}

response = code_engine_service.create_secret(
    project_id='15314cc3-85b4-4338-903f-c28cdee6d005',
    format='generic',
    name='my-secret',
    data=secret_data
)
secret = response.get_result()

print(json.dumps(secret, indent=2))
```

## create a Code Engine TLS secret

```python
secret_data = {
    "tls.crt": tls_cert,
    "tls.key": tls_key,
}

response = code_engine_service.create_secret(
    project_id=project_id, format="tls", name=secret_name, data=secret_data
).get_result()
```

## Create a Code Engine Build from Dockerfile

```python
response = code_engine_service.create_build(
    project_id='15314cc3-85b4-4338-903f-c28cdee6d005',
    name='my-build',
    output_image='private.de.icr.io/icr_namespace/image-name',
    output_secret='ce-auto-icr-private-eu-de',
    strategy_type='dockerfile',
    source_type='git',
    source_url='https://github.com/IBM/CodeEngine'
)
build = response.get_result()

print(json.dumps(build, indent=2))
```

## create a Code Engine Build from Source

```python
response = code_engine_service.create_build(
    project_id='PROJECT_ID',
    name='my-build',
    output_image='private.us.icr.io/icr_namespace/image-name',
    output_secret='ce-auto-icr-private-us-south',
    strategy_type='dockerfile',
    source_type='local',
    source_context_dir='.',

)
build = response.get_result()

print(json.dumps(build, indent=2))
```