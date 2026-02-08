/**
 * Full Tier 1 + Tier 2 workflow example.
 *
 * Usage:
 *   npm run build
 *   STRUAI_API_KEY=... STRUAI_BASE_URL=http://localhost:8000 \
 *   STRUAI_PDF=/absolute/path/to/structural.pdf STRUAI_PAGE=12 \
 *   node scripts/projects_workflow.mjs
 *
 * Optional cleanup:
 *   STRUAI_CLEANUP=1 node scripts/projects_workflow.mjs
 */

import fs from 'node:fs/promises';
import path from 'node:path';
import { StruAI } from '../dist/index.mjs';

const apiKey = process.env.STRUAI_API_KEY;
const baseUrl = process.env.STRUAI_BASE_URL ?? 'https://api.stru.ai';
const pdfPath = process.env.STRUAI_PDF;
const page = Number(process.env.STRUAI_PAGE ?? '12');
const query = process.env.STRUAI_QUERY ?? 'beam connection';
const cleanup = process.env.STRUAI_CLEANUP === '1';
const timeoutMs = Number(process.env.STRUAI_TIMEOUT_MS ?? '240000');
const pollIntervalMs = Number(process.env.STRUAI_POLL_INTERVAL_MS ?? '2000');

if (!apiKey) {
  console.error('Missing STRUAI_API_KEY');
  process.exit(1);
}
if (!pdfPath) {
  console.error('Missing STRUAI_PDF');
  process.exit(1);
}

try {
  await fs.access(pdfPath);
} catch {
  console.error(`PDF not found: ${pdfPath}`);
  process.exit(1);
}

const client = new StruAI({ apiKey, baseUrl });

console.log('== Tier 1: Drawings ==');
const fileHash = await client.drawings.computeFileHash(pdfPath);
const cache = await client.drawings.checkCache(fileHash);
console.log(`file_hash=${fileHash} cached=${cache.cached}`);

const drawing = cache.cached
  ? await client.drawings.analyze(null, { page, fileHash })
  : await client.drawings.analyze(pdfPath, { page });
console.log(`drawing_id=${drawing.id} page=${drawing.page} processing_ms=${drawing.processing_ms}`);

console.log('\n== Tier 2: Projects ==');
const project = await client.projects.create({
  name: `JS SDK Workflow ${Date.now()}`,
  description: `Created from ${path.basename(pdfPath)} page ${page}`,
});
console.log(`project_created id=${project.id} name=${project.name}`);

const projects = await client.projects.list({ limit: 5 });
console.log(`projects_list_count=${projects.length}`);

const fetchedProject = await client.projects.get(project.id);
console.log(`project_get id=${fetchedProject.id} description=${fetchedProject.description ?? ''}`);

const jobOrBatch = cache.cached
  ? await project.sheets.add(null, {
      page,
      fileHash,
      sourceDescription: `${path.basename(pdfPath)} page ${page}`,
      onSheetExists: 'skip',
      communityUpdateMode: 'incremental',
      semanticIndexUpdateMode: 'incremental',
    })
  : await project.sheets.add(pdfPath, {
      page,
      sourceDescription: `${path.basename(pdfPath)} page ${page}`,
      onSheetExists: 'skip',
      communityUpdateMode: 'incremental',
      semanticIndexUpdateMode: 'incremental',
    });

let sheetResult;
if ('waitAll' in jobOrBatch) {
  const statuses = await jobOrBatch.statusAll();
  console.log(`initial_batch_statuses=${statuses.map((s) => `${s.job_id}:${s.status}`).join(',')}`);
  const results = await jobOrBatch.waitAll({ timeoutMs, pollIntervalMs });
  sheetResult = results.find((item) => item.sheet_id) ?? results[0];
} else {
  const status = await jobOrBatch.status();
  console.log(`initial_job_status job_id=${status.job_id} status=${status.status}`);
  sheetResult = await jobOrBatch.wait({ timeoutMs, pollIntervalMs });
}

console.log(
  `sheet_result sheet_id=${sheetResult.sheet_id ?? ''} ` +
    `entities_created=${sheetResult.entities_created ?? 0} ` +
    `relationships_created=${sheetResult.relationships_created ?? 0}`
);

const sheets = await project.sheets.list({ limit: 10 });
console.log(`sheets_list_count=${sheets.length}`);

const targetSheetId = sheetResult.sheet_id;
if (targetSheetId) {
  const sheet = await project.sheets.get(targetSheetId);
  console.log(`sheet_get id=${sheet.id} page=${sheet.page ?? ''} regions=${sheet.regions.length}`);

  const annotations = await project.sheets.getAnnotations(targetSheetId);
  console.log(
    `sheet_annotations leaders=${(annotations.annotations.leaders ?? []).length} ` +
      `section_tags=${(annotations.annotations.section_tags ?? []).length}`
  );
}

const search = await project.search(query, {
  limit: 5,
  channels: ['entities', 'facts', 'communities'],
  includeGraphContext: true,
});
console.log(
  `search entities=${search.entities.length} facts=${search.facts.length} ` +
    `communities=${search.communities.length} search_ms=${search.search_ms}`
);

const entities = await project.entities.list({ limit: 5, type: 'component_instance' });
console.log(`entities_list_count=${entities.length}`);
if (entities.length > 0) {
  const entity = await project.entities.get(entities[0].id, {
    includeInvalid: false,
    expandTarget: true,
  });
  console.log(`entity_get id=${entity.id} label=${entity.label} outgoing=${entity.outgoing.length}`);
}

const relationships = await project.relationships.list({ limit: 5, includeInvalid: false });
console.log(`relationships_list_count=${relationships.length}`);

if (cleanup) {
  if (targetSheetId) {
    const deletedSheet = await project.sheets.delete(targetSheetId);
    console.log(`sheet_deleted=${deletedSheet.deleted} sheet_id=${deletedSheet.sheet_id}`);
  }
  const deletedProject = await fetchedProject.delete();
  console.log(`project_deleted=${deletedProject.deleted} project_id=${deletedProject.id}`);
} else {
  console.log(`kept_project_id=${project.id}`);
}
