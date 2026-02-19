/**
 * Local smoke test for StruAI JS SDK.
 *
 * Usage:
 *   npm run build
 *   STRUAI_API_KEY=YOUR_API_KEY STRUAI_BASE_URL=http://localhost:8000 \
 *     node scripts/smoke_local.mjs
 */
import { StruAI } from '../dist/index.mjs';

const baseUrl = process.env.STRUAI_BASE_URL ?? 'http://localhost:8000';
const apiKey = process.env.STRUAI_API_KEY;
if (!apiKey) {
  throw new Error('Missing STRUAI_API_KEY');
}

const client = new StruAI({ apiKey, baseUrl });

const projects = await client.projects.list();
let project;
let created = false;
if (projects.length > 0) {
  project = client.projects.open(projects[0].id, { name: projects[0].name });
} else {
  project = await client.projects.create({ name: 'Smoke Test Project' });
  created = true;
}

const topology = await project.docquery.sheetList();
const search = await project.docquery.search('beam', { limit: 3 });

console.log(
  `project=${project.id} sheet_nodes=${topology.totals.sheet_node_count ?? 0} ` +
    `mismatches=${topology.mismatch_warnings.length} search_count=${search.hits.length}`
);

if (created) {
  await project.delete();
}
