# StruAI JavaScript SDK

Official JavaScript/TypeScript SDK for the StruAI Drawing Analysis API.

## Installation

```bash
npm install struai
```

## Quick Start

```ts
import { StruAI } from 'struai';

const client = new StruAI({ apiKey: process.env.STRUAI_API_KEY! });
// Optional local: new StruAI({ apiKey: 'windowseat', baseUrl: 'http://localhost:8000' })
```

## Tier 1: Drawings

```ts
const drawing = await client.drawings.analyze(fileBlob, { page: 12 });
const cache = await client.drawings.checkCache('abc123def4567890');
const same = await client.drawings.get(drawing.id);
await client.drawings.delete(drawing.id);
```

## Tier 2: Projects

```ts
const project = await client.projects.create({
  name: 'Building A',
  description: 'Structural set',
});

// Single page -> Job
const jobOrBatch = await project.sheets.add(fileBlob, { page: 12 });
if ('wait' in jobOrBatch) {
  await jobOrBatch.wait({ timeoutMs: 180_000 });
}

// Multi-page selector -> JobBatch
const batch = await project.sheets.add(null, { page: '1,3,5-7', fileHash: 'abc123def4567890' });
if ('waitAll' in batch) {
  await batch.waitAll({ timeoutMs: 300_000 });
}

const sheets = await project.sheets.list();
const details = await project.sheets.get(sheets[0].id);
const raw = await project.sheets.getAnnotations(sheets[0].id);
```

### Search

```ts
const search = await project.search('beam connection at grid A', {
  limit: 10,
  channels: ['entities', 'facts', 'communities'],
  includeGraphContext: true,
});

console.log(search.entities.length, search.facts.length, search.communities.length);
```

### Entities + Relationships

```ts
const entities = await project.entities.list({ limit: 20, type: 'component_instance' });
const entity = await project.entities.get(entities[0].id, { expandTarget: true });
const rels = await project.relationships.list({ limit: 20, includeInvalid: false });
```

## Local Smoke Test

```bash
npm run build
STRUAI_API_KEY=windowseat STRUAI_BASE_URL=http://localhost:8000 node scripts/smoke_local.mjs
```

## License

MIT
