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

# Tier 2: projects + docquery
project = client.projects.create(name="Building A", description="Structural set")
job = project.sheets.add(page=12, file_hash=client.drawings.compute_file_hash("structural.pdf"))
sheet = job.wait(timeout=180)

hits = project.docquery.search("beam connection", limit=5)
print(hits.count)
```

## Real Workflow Examples

Python examples (`/examples`):

```bash
# Drawings-only flow (hash, cache probe, analyze, get, optional delete)
python3 examples/test_prod_page12.py --pdf /absolute/path/to/structural.pdf --page 12

# Full projects + docquery workflow
python3 examples/test_prod_page12_full.py --pdf /absolute/path/to/structural.pdf --page 12

# Full workflow + crop demo
python3 examples/test_prod_page12_full.py \
  --pdf /absolute/path/to/structural.pdf --page 12 \
  --crop-image /absolute/path/to/page_context.png \
  --crop-output /absolute/path/to/crop.png

# Optional cleanup after full workflow
python3 examples/test_prod_page12_full.py --pdf /absolute/path/to/structural.pdf --cleanup

# Async workflow
python3 examples/async_projects_workflow.py --pdf /absolute/path/to/structural.pdf --page 12
```

Page-12 cookbook with all 10 operations (including `cypher` and `crop`):
- `examples/PAGE12_COOKBOOK.md`

JavaScript examples (`/js/scripts`):

```bash
cd js
npm install
npm run build

# Drawings-only flow
STRUAI_API_KEY=... STRUAI_BASE_URL=https://api.stru.ai \
STRUAI_PDF=/absolute/path/to/structural.pdf STRUAI_PAGE=12 \
node scripts/drawings_quickstart.mjs

# Full projects + docquery workflow
STRUAI_API_KEY=... STRUAI_BASE_URL=https://api.stru.ai \
STRUAI_PDF=/absolute/path/to/structural.pdf STRUAI_PAGE=12 \
node scripts/projects_workflow.mjs

# Full workflow + crop demo
STRUAI_API_KEY=... STRUAI_BASE_URL=https://api.stru.ai \
STRUAI_PDF=/absolute/path/to/structural.pdf STRUAI_PAGE=12 \
STRUAI_CROP_IMAGE=/absolute/path/to/page_context.png \
STRUAI_CROP_OUTPUT=/absolute/path/to/crop.png \
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
- `list() -> list[Project]`
- `open(project_id, name=None, description=None) -> ProjectInstance`
- `delete(project_id) -> ProjectDeleteResult`

### Project Instance (`project`)

Properties:

- `id`, `name`, `description`, `data`
- `sheets`, `docquery`

Methods:

- `delete() -> ProjectDeleteResult`

### Sheets (`project.sheets`)

- `add(file=None, page=1|"1,3,5-7"|"all", file_hash=None, source_description=None, on_sheet_exists=None, community_update_mode=None, semantic_index_update_mode=None) -> Job | JobBatch`
- `delete(sheet_id) -> SheetDeleteResult`
- `job(job_id, page=None) -> Job`

### DocQuery (`project.docquery`)

- `node_get(uuid) -> DocQueryNodeGetResult`
- `sheet_entities(sheet_id, entity_type=None, limit=200) -> DocQuerySheetEntitiesResult`
- `search(query, index="entity_search", limit=20) -> DocQuerySearchResult`
- `neighbors(uuid, direction="both", relationship_type=None, limit=50) -> DocQueryNeighborsResult`
- `cypher(query, params=None, max_rows=500) -> DocQueryCypherResult`
- `sheet_summary(sheet_id, orphan_limit=10) -> DocQuerySheetSummaryResult`
- `sheet_list() -> DocQuerySheetListResult`
- `reference_resolve(uuid, limit=100) -> DocQueryReferenceResolveResult`
- `crop(output, uuid=None, bbox=None, image=None, page_hash=None, scale=None, scale_x=None, scale_y=None, auto_scale=False, pad=0, clamp=True) -> DocQueryCropResult`

CLI parity: `project-list` maps to `client.projects.list()`, and the remaining 9 commands map to `project.docquery.*`, for full 10-command parity.

Python cypher + crop example:

```python
project = client.projects.open("proj_86c0f02e")
rows = project.docquery.cypher(
    "MATCH (n:Entity {project_id:$project_id}) RETURN count(n) AS total",
    params={},
    max_rows=1,
)

crop = project.docquery.crop(
    uuid="entity-uuid-here",
    image="/absolute/path/to/page_context.png",
    output="/absolute/path/to/crop.png",
)
print(rows.records[0]["total"], crop.output_image["path"])
```

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
- `DELETE /v1/projects/{project_id}`
- `POST /v1/projects/{project_id}/sheets`
- `DELETE /v1/projects/{project_id}/sheets/{sheet_id}`
- `GET /v1/projects/{project_id}/jobs/{job_id}`
- `GET /v1/projects/{project_id}/docquery/node-get`
- `GET /v1/projects/{project_id}/docquery/sheet-entities`
- `GET /v1/projects/{project_id}/docquery/search`
- `GET /v1/projects/{project_id}/docquery/neighbors`
- `POST /v1/projects/{project_id}/docquery/cypher`

## JavaScript Reference

See `js/README.md` for complete JS method signatures and usage patterns.

## License

MIT
