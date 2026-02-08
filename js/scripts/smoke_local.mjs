/**
 * Local smoke test for StruAI JS SDK.
 *
 * Usage:
 *   npm run build
 *   STRUAI_API_KEY=windowseat STRUAI_BASE_URL=http://localhost:8000 \
 *     node scripts/smoke_local.mjs
 */
import { StruAI } from '../dist/index.mjs';

const baseUrl = process.env.STRUAI_BASE_URL ?? 'http://localhost:8000';
const apiKey = process.env.STRUAI_API_KEY ?? 'windowseat';

const client = new StruAI({ apiKey, baseUrl });

const projects = await client.projects.list({ limit: 1 });
let project;
let created = false;
if (projects.length > 0) {
  project = await client.projects.get(projects[0].id);
} else {
  project = await client.projects.create({ name: 'Smoke Test Project' });
  created = true;
}

const entities = await project.entities.list({ limit: 1 });
const relationships = await project.relationships.list({ limit: 1 });
const search = await project.search('beam', { limit: 3 });

console.log(
  `project=${project.id} entities=${entities.length} relationships=${relationships.length} ` +
    `search_entities=${search.entities.length} search_facts=${search.facts.length}`
);

if (created) {
  await project.delete();
}
