# StruAI SDK (Python + JavaScript)

Official SDKs for the StruAI Drawing Analysis API.

- Python package: `struai` (PyPI)
- JavaScript package: `struai` (npm, source in `js/`)

## Install

```bash
pip install struai
npm install struai
```

## Environment

```bash
export STRUAI_API_KEY=your_api_key
# Optional: defaults to https://api.stru.ai (SDK appends /v1 automatically)
export STRUAI_BASE_URL=https://api.stru.ai
```

## Python Quick Start

```python
import os
from struai import StruAI

client = StruAI(api_key=os.environ["STRUAI_API_KEY"])

# Tier 1: drawings
result = client.drawings.analyze("structural.pdf", page=12)
print(result.id, result.processing_ms)

# Tier 2: projects
project = client.projects.create(name="Building A", description="Structural set")
job = project.sheets.add(page=12, file_hash=client.drawings.compute_file_hash("structural.pdf"))
sheet = job.wait(timeout=180)

search = project.search("beam connection", limit=5)
print(len(search.entities), len(search.facts), len(search.communities))
```

## Real Workflow Examples

Python examples (`/examples`):

```bash
# Drawings-only flow (hash, cache probe, analyze, get, optional delete)
python3 examples/test_prod_page12.py --pdf /absolute/path/to/structural.pdf --page 12

# Full projects workflow (create/list/get project, ingest, poll, search, entities, relationships)
python3 examples/test_prod_page12_full.py --pdf /absolute/path/to/structural.pdf --page 12

# Optional cleanup after full workflow
python3 examples/test_prod_page12_full.py --pdf /absolute/path/to/structural.pdf --cleanup

# Async workflow
python3 examples/async_projects_workflow.py --pdf /absolute/path/to/structural.pdf --page 12
```

JavaScript examples (`/js/scripts`):

```bash
cd js
npm install
npm run build

# Drawings-only flow
STRUAI_API_KEY=... STRUAI_BASE_URL=http://localhost:8000 \
STRUAI_PDF=/absolute/path/to/structural.pdf STRUAI_PAGE=12 \
node scripts/drawings_quickstart.mjs

# Full projects workflow
STRUAI_API_KEY=... STRUAI_BASE_URL=http://localhost:8000 \
STRUAI_PDF=/absolute/path/to/structural.pdf STRUAI_PAGE=12 \
node scripts/projects_workflow.mjs
```

## Python API Reference

Async API (`AsyncStruAI`) mirrors the same resource shape and method names; use `await`.

### Client

- `StruAI(api_key=None, base_url="https://api.stru.ai", timeout=60, max_retries=2)`
- `AsyncStruAI(api_key=None, base_url="https://api.stru.ai", timeout=60, max_retries=2)`
- `client.drawings`
- `client.projects`

### Drawings (`client.drawings`)

- `analyze(file=None, page=1, file_hash=None) -> DrawingResult`
- `check_cache(file_hash) -> DrawingCacheStatus`
- `get(drawing_id) -> DrawingResult`
- `delete(drawing_id) -> DrawingDeleteResult`
- `compute_file_hash(file) -> str`

### Projects Top-Level (`client.projects`)

- `create(name, description=None) -> ProjectInstance`
- `list(limit=None) -> list[Project]`
- `get(project_id) -> ProjectInstance`
- `delete(project_id) -> ProjectDeleteResult`

### Project Instance (`project`)

Properties:

- `id`, `name`, `description`, `data`
- `sheets`, `entities`, `relationships`

Methods:

- `search(query, limit=10, channels=None, include_graph_context=True) -> SearchResponse`
- `delete() -> ProjectDeleteResult`

### Sheets (`project.sheets`)

- `add(file=None, page=1|"1,3,5-7"|"all", file_hash=None, source_description=None, on_sheet_exists=None, community_update_mode=None, semantic_index_update_mode=None) -> Job | JobBatch`
- `list(limit=None) -> list[SheetSummary]`
- `get(sheet_id) -> SheetDetail`
- `get_annotations(sheet_id) -> SheetAnnotations`
- `delete(sheet_id) -> SheetDeleteResult`

### Entities (`project.entities`)

- `list(sheet_id=None, type=None, family=None, normalized_spec=None, region_uuid=None, region_label=None, note_number=None, limit=200) -> list[EntityListItem]`
- `get(entity_id, include_invalid=False, expand_target=False) -> Entity`

### Relationships (`project.relationships`)

- `list(sheet_id=None, source_id=None, target_id=None, type=None, include_invalid=False, invalid_only=False, orphan_only=False, limit=200) -> list[Fact]`

### Jobs

`Job` (single-page ingest result):

- `id`, `page`
- `status() -> JobStatus`
- `wait(timeout=120, poll_interval=2) -> SheetResult`

`JobBatch` (multi-page ingest result):

- `jobs`, `ids`
- `status_all() -> list[JobStatus]`
- `wait_all(timeout_per_job=120, poll_interval=2) -> list[SheetResult]`

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

## JavaScript Reference

See `js/README.md` for complete JS method signatures and usage patterns.

## License

MIT
