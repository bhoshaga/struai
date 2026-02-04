# StruAI JavaScript SDK

Official JavaScript/TypeScript SDK for the StruAI Drawing Analysis API.

See the [main README](../README.md) for Python examples.

## Installation

```bash
npm install struai
```

## Quick Start

```typescript
import { StruAI } from 'struai';

const client = new StruAI({ apiKey: 'sk-xxx' });

// Optional: override base URL (http://localhost:8000 or http://localhost:8000/v1)
const local = new StruAI({ apiKey: 'sk-xxx', baseUrl: 'http://localhost:8000' });
```

## Tier 1: Raw Detection ($0.02/page)

```typescript
// Analyze a PDF page
const result = await client.drawings.analyze(file, { page: 4 });

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

## License

MIT
