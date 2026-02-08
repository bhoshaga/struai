# StruAI SDK (Python + JavaScript)

Official SDKs for the StruAI Drawing Analysis API.

- Python package: `struai` (PyPI)
- JavaScript package: `struai` (npm, in `js/`)

## Python Install

```bash
pip install struai
```

## JavaScript Install

```bash
npm install struai
```

## Quick Start (Python)

```python
import os
from struai import StruAI

client = StruAI(api_key=os.environ["STRUAI_API_KEY"])
# Optional: StruAI(api_key=..., base_url="http://localhost:8000")
```

## Tier 1: Drawings

```python
# Upload PDF + detect one page
result = client.drawings.analyze("structural.pdf", page=12)
print(result.id, result.processing_ms)

# Reuse cache by hash
file_hash = client.drawings.compute_file_hash("structural.pdf")
result = client.drawings.analyze(page=12, file_hash=file_hash)

# Cache probe / retrieval / deletion
cache = client.drawings.check_cache(file_hash)
again = client.drawings.get(result.id)
deleted = client.drawings.delete(result.id)
```

## Tier 2: Projects

```python
project = client.projects.create(name="Building A", description="Structural set")

# Ingest one page (returns Job)
job = project.sheets.add(page=12, file_hash=file_hash)
sheet_result = job.wait(timeout=180)

# Ingest many pages (returns JobBatch)
batch = project.sheets.add(page="1,3,5-7", file_hash=file_hash)
all_results = batch.wait_all(timeout_per_job=300)

# Sheet data
sheets = project.sheets.list()
sheet = project.sheets.get(sheet_result.sheet_id)
raw_annotations = project.sheets.get_annotations(sheet_result.sheet_id)
```

### Search

```python
search = project.search(
    query="beam connection at grid A",
    limit=10,
    channels=["entities", "facts", "communities"],
    include_graph_context=True,
)

print(len(search.entities), len(search.facts), len(search.communities))
```

### Entities + Relationships

```python
entities = project.entities.list(limit=20, type="component_instance")
entity = project.entities.get(entities[0].id, expand_target=True)

rels = project.relationships.list(limit=20, include_invalid=False)
```

## Async Python

```python
import os
from struai import AsyncStruAI

async with AsyncStruAI(api_key=os.environ["STRUAI_API_KEY"]) as client:
    file_hash = client.drawings.compute_file_hash("structural.pdf")
    result = await client.drawings.analyze(page=12, file_hash=file_hash)
    project = await client.projects.create(name="Async Project")
    job = await project.sheets.add(page=12, file_hash=file_hash)
    await job.wait(timeout=180)
```

## HTTP Endpoints Covered

Tier 1:
- `POST /v1/drawings`
- `GET /v1/drawings/{id}`
- `DELETE /v1/drawings/{id}`
- `GET /v1/drawings/cache/{file_hash}`

Tier 2:
- `POST /v1/projects`
- `GET /v1/projects`
- `GET /v1/projects/{id}`
- `DELETE /v1/projects/{id}`
- `POST /v1/projects/{project_id}/sheets`
- `GET /v1/projects/{project_id}/jobs/{job_id}`
- `GET /v1/projects/{project_id}/sheets`
- `GET /v1/projects/{project_id}/sheets/{sheet_id}`
- `GET /v1/projects/{project_id}/sheets/{sheet_id}/annotations`
- `DELETE /v1/projects/{project_id}/sheets/{sheet_id}`
- `POST /v1/projects/{project_id}/search`
- `GET /v1/projects/{project_id}/entities`
- `GET /v1/projects/{project_id}/entities/{entity_id}`
- `GET /v1/projects/{project_id}/relationships`

## Local Smoke Tests

- Python: `scripts/smoke_local.py`
- JavaScript: `js/scripts/smoke_local.mjs`

## License

MIT
