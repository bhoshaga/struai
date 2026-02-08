# StruAI JavaScript SDK

Official JavaScript/TypeScript SDK for the StruAI Drawing Analysis API.

## Installation

```bash
npm install struai
```

## Environment

```bash
export STRUAI_API_KEY=your_api_key
# Optional: defaults to https://api.stru.ai (SDK appends /v1 automatically)
export STRUAI_BASE_URL=https://api.stru.ai
```

## Quick Start

```ts
import { StruAI } from 'struai';

const client = new StruAI({
  apiKey: process.env.STRUAI_API_KEY!,
  baseUrl: process.env.STRUAI_BASE_URL, // optional
  timeout: 60_000, // optional
});

const drawing = await client.drawings.analyze('/absolute/path/to/structural.pdf', { page: 12 });
const project = await client.projects.create({ name: 'Building A', description: 'Structural set' });
const jobOrBatch = await project.sheets.add(null, {
  page: 12,
  fileHash: await client.drawings.computeFileHash('/absolute/path/to/structural.pdf'),
});
```

## Real Workflow Examples

```bash
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

# Optional cleanup after full workflow
STRUAI_CLEANUP=1 node scripts/projects_workflow.mjs
```

See `scripts/README.md` for quick copy/paste commands.

## API Reference

### Client

- `new StruAI({ apiKey, baseUrl?, timeout? })`
- `client.drawings`
- `client.projects`

### Drawings (`client.drawings`)

- `analyze(file, { page, fileHash? }) -> Promise<DrawingResult>`
  - Pass either `file` or `fileHash`.
  - `file` can be a file path string, `Blob`, `ArrayBuffer`, or typed array.
- `checkCache(fileHash) -> Promise<DrawingCacheStatus>`
- `get(drawingId) -> Promise<DrawingResult>`
- `delete(drawingId) -> Promise<DrawingDeleteResult>`
- `computeFileHash(file) -> Promise<string>`

### Projects Top-Level (`client.projects`)

- `create({ name, description? }) -> Promise<ProjectInstance>`
- `list({ limit? }?) -> Promise<Project[]>`
- `get(projectId) -> Promise<ProjectInstance>`
- `delete(projectId) -> Promise<ProjectDeleteResult>`

### Project Instance (`project`)

Properties:

- `id`, `name`, `description`, `data`
- `sheets`, `entities`, `relationships`

Methods:

- `search(query, { limit?, channels?, includeGraphContext? }?) -> Promise<SearchResponse>`
- `delete() -> Promise<ProjectDeleteResult>`

### Sheets (`project.sheets`)

- `add(file, { page, fileHash?, sourceDescription?, onSheetExists?, communityUpdateMode?, semanticIndexUpdateMode? }) -> Promise<Job | JobBatch>`
  - `page` supports `12`, `'1,3,5-7'`, `'all'`
  - Pass either `file` or `fileHash`
- `list({ limit? }?) -> Promise<SheetSummary[]>`
- `get(sheetId) -> Promise<SheetDetail>`
- `getAnnotations(sheetId) -> Promise<SheetAnnotations>`
- `delete(sheetId) -> Promise<SheetDeleteResult>`

### Entities (`project.entities`)

- `list({ sheetId?, type?, family?, normalizedSpec?, regionUuid?, regionLabel?, noteNumber?, limit? }?) -> Promise<EntityListItem[]>`
- `get(entityId, { includeInvalid?, expandTarget? }?) -> Promise<Entity>`

### Relationships (`project.relationships`)

- `list({ sheetId?, sourceId?, targetId?, type?, includeInvalid?, invalidOnly?, orphanOnly?, limit? }?) -> Promise<Fact[]>`

### Jobs

`Job`:

- `id`, `page`
- `status() -> Promise<JobStatus>`
- `wait({ timeoutMs?, pollIntervalMs? }?) -> Promise<SheetResult>`

`JobBatch`:

- `jobs`, `ids`
- `statusAll() -> Promise<JobStatus[]>`
- `waitAll({ timeoutMs?, pollIntervalMs? }?) -> Promise<SheetResult[]>`

## Endpoint Coverage

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

## License

MIT
