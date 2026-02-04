# StruAI JavaScript SDK

Official JavaScript/TypeScript SDK for the StruAI Drawing Analysis API.

See the [main README](../README.md) for Python examples.

## Installation

```bash
npm install struai
```

## Quick Start

Get an API key from `stru.ai` and set `STRUAI_API_KEY`.

```typescript
import { StruAI } from 'struai';

// Get an API key from stru.ai and set STRUAI_API_KEY
const client = new StruAI({ apiKey: process.env.STRUAI_API_KEY! });

// Optional: override base URL (http://localhost:8000 or http://localhost:8000/v1)
const local = new StruAI({ apiKey: process.env.STRUAI_API_KEY!, baseUrl: 'http://localhost:8000' });
```

## Tier 1: Raw Detection ($0.02/page)

```typescript
// Analyze a PDF page
const result = await client.drawings.analyze(file, { page: 4 });

// Or reuse cached PDFs by hash (skips upload)
const resultFromCache = await client.drawings.analyze(null, { page: 4, fileHash: "abc123def4567890" });

console.log(`Processed in ${result.processing_ms}ms`);

for (const leader of result.annotations.leaders) {
  const texts = leader.texts_inside.map(t => t.text).join(', ');
  console.log(`Leader: ${texts}`);
}
```

## Tier 2: Graph + Search ($0.15/page)

```typescript
// Create project
const project = await client.projects.create({
  name: 'Building A Structural',
  description: '96-page structural drawing set'
});

// Add sheet (async processing)
const job = await project.sheets.add(file, { page: 4 });

// Or reuse cached PDFs by hash (skips upload)
const cachedJob = await project.sheets.add(null, { page: 4, fileHash: "abc123def4567890" });
const result = await job.wait({ timeout: 120000 });
console.log(`Created ${result.entities_created} entities`);

// Semantic search
const results = await project.search('W12x26 beam connections', {
  limit: 10,
  includeGraphContext: true
});

for (const hit of results.results) {
  console.log(`${hit.entity.label}: ${hit.score}`);
}

// Natural language query
const answer = await project.query('What beams connect to column C3?');
console.log(answer.answer);

// Browse entities
const entities = await project.entities.list({ type: 'Component', limit: 50 });
const entity = await project.entities.get('ent_abc123');
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
- `POST /v1/projects/{project_id}/sheets` — multipart form with `file` **or** `file_hash`, plus `page`
- `GET /v1/projects/{project_id}/jobs/{job_id}`
- `GET /v1/projects/{project_id}/sheets`
- `GET /v1/projects/{project_id}/sheets/{sheet_id}`
- `DELETE /v1/projects/{project_id}/sheets/{sheet_id}`
- `POST /v1/projects/{project_id}/search`
- `POST /v1/projects/{project_id}/query`
- `GET /v1/projects/{project_id}/entities`
- `GET /v1/projects/{project_id}/entities/{entity_id}`
- `GET /v1/projects/{project_id}/relationships`

## License

MIT
