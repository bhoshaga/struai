# StruAI Python SDK

Official Python SDK for the StruAI Drawing Analysis API.

## Installation

```bash
pip install struai
```

## Quick Start

```python
from struai import StruAI

client = StruAI(api_key="sk-xxx")  # or set STRUAI_API_KEY env var

# Optional: override base URL (http://localhost:8000 or http://localhost:8000/v1)
client = StruAI(api_key="sk-xxx", base_url="http://localhost:8000")
```

## Tier 1: Raw Detection ($0.02/page)

Fast geometric detection. Returns annotations in ~1-2 seconds.

```python
# Analyze a PDF page
result = client.drawings.analyze("structural.pdf", page=4)

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
from struai import AsyncStruAI

async with AsyncStruAI(api_key="sk-xxx") as client:
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
