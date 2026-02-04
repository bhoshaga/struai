# StruAI Python SDK

Official Python SDK for the StruAI Drawing Analysis API.

## Installation

```bash
pip install struai
```

## Quick Start

Get an API key from `stru.ai` and set it as an environment variable:

```bash
export STRUAI_API_KEY="YOUR_API_KEY"
```

```python
import os
from struai import StruAI

client = StruAI(api_key=os.environ["STRUAI_API_KEY"])

# Optional: override base URL (http://localhost:8000 or http://localhost:8000/v1)
client = StruAI(api_key=os.environ["STRUAI_API_KEY"], base_url="http://localhost:8000")
```

## Tier 1: Raw Detection ($0.02/page)

Fast geometric detection. Returns annotations in ~1-2 seconds.

```python
# Analyze a PDF page
result = client.drawings.analyze("structural.pdf", page=4)

# Or reuse cached PDFs by hash (skips upload)
file_hash = client.drawings.compute_file_hash("structural.pdf")
result = client.drawings.analyze(page=4, file_hash=file_hash)

print(f"Processed in {result.processing_ms}ms")
print(f"Page size: {result.dimensions.width}x{result.dimensions.height}")

# Access detected annotations
for leader in result.annotations.leaders:
    texts = [t.text for t in leader.texts_inside]
    print(f"Leader at {leader.arrow_tip}: {', '.join(texts)}")

for tag in result.annotations.section_tags:
    label = tag.texts_inside[0].text
    print(f"Section {label}, direction: {tag.direction}")

# Retrieve/delete previous results
drawing = client.drawings.get("drw_7f8a9b2c")
client.drawings.delete("drw_7f8a9b2c")
```

## HTTP Endpoints (Reference)

All endpoints are under `/v1`. Use `Authorization: Bearer <API_KEY>`.

Tier 1 (raw detection):
- `POST /v1/drawings` — multipart form with `file` (PDF) **or** `file_hash`, plus `page` (1-indexed)
- `GET /v1/drawings/{id}`
- `DELETE /v1/drawings/{id}`

Tier 2 (graph + search):
- `POST /v1/projects`
- `GET /v1/projects`
- `GET /v1/projects/{id}`
- `DELETE /v1/projects/{id}`
- `POST /v1/projects/{project_id}/sheets` — multipart form with `file` + `page`
- `GET /v1/projects/{project_id}/jobs/{job_id}`
- `GET /v1/projects/{project_id}/sheets`
- `GET /v1/projects/{project_id}/sheets/{sheet_id}`
- `DELETE /v1/projects/{project_id}/sheets/{sheet_id}`
- `POST /v1/projects/{project_id}/search`
- `POST /v1/projects/{project_id}/query`
- `GET /v1/projects/{project_id}/entities`
- `GET /v1/projects/{project_id}/entities/{entity_id}`
- `GET /v1/projects/{project_id}/relationships`

Example (raw detection):

```bash
curl -X POST "https://api.stru.ai/v1/drawings" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -F "file=@structural.pdf" \
  -F "page=4"

curl -X POST "https://api.stru.ai/v1/drawings" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -F "file_hash=abc123def4567890" \
  -F "page=4"
```

Example (project sheet ingestion):

```bash
curl -X POST "https://api.stru.ai/v1/projects/{project_id}/sheets" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -F "file=@structural.pdf" \
  -F "page=4"
```

## Tier 2: Graph + Search ($0.15/page)

Full pipeline: detection → LLM enrichment → knowledge graph → semantic search.

```python
# Create a project
project = client.projects.create(
    name="Building A Structural",
    description="96-page structural drawing set"
)

# Add sheets (async processing)
job = project.sheets.add("structural.pdf", page=4)
result = job.wait(timeout=120)  # Blocks until complete
print(f"Created {result.entities_created} entities")

# Semantic search
results = project.search(
    query="W12x26 beam connections at grid A",
    limit=10,
    include_graph_context=True
)

for hit in results.results:
    print(f"{hit.entity.label}: {hit.score:.2f}")
    if hit.graph_context:
        for rel in hit.graph_context.relationships:
            print(f"  - {rel.type}: {rel.fact}")

# Natural language query
answer = project.query("What beams connect to column C3?")
print(answer.answer)
print(f"Confidence: {answer.confidence:.0%}")

# Browse entities
entities = project.entities.list(type="Component", limit=50)
entity = project.entities.get("ent_abc123")
```

## Async Support

```python
import os
from struai import AsyncStruAI

async with AsyncStruAI(api_key=os.environ["STRUAI_API_KEY"]) as client:
    # Tier 1
    result = await client.drawings.analyze("structural.pdf", page=4)

    # Tier 2
    project = await client.projects.create(name="Building A")
    job = await project.sheets.add("structural.pdf", page=4)
    result = await job.wait(timeout=120)
    results = await project.search("W12x26 beam connections")
```

## Error Handling

```python
from struai import StruAI, AuthenticationError, RateLimitError, NotFoundError

try:
    result = client.drawings.analyze("plans.pdf", page=99)
except AuthenticationError:
    print("Invalid API key")
except RateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after}s")
except NotFoundError:
    print("Resource not found")
```

## License

MIT
