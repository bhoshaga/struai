import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { Job, JobBatch, StruAI } from '../src/index';

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  });
}

function pngResponse(bytes: Uint8Array, status = 200): Response {
  return new Response(bytes, {
    status,
    headers: { 'Content-Type': 'image/png' },
  });
}

describe('StruAI JS SDK', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('normalizes baseUrl by appending /v1', () => {
    const client = new StruAI({ apiKey: 'k', baseUrl: 'http://localhost:8000' });
    expect((client as any).baseUrl).toBe('http://localhost:8000/v1');
  });

  it('opens a project handle without a network lookup', () => {
    const client = new StruAI({ apiKey: 'k', baseUrl: 'http://localhost:8000' });
    const project = client.projects.open('proj_123', { name: 'Test Project' });
    expect(project.id).toBe('proj_123');
    expect(project.name).toBe('Test Project');
  });

  it('returns Job for single-page ingest and JobBatch for multi-page ingest', async () => {
    const fetchMock = vi
      .fn<Parameters<typeof fetch>, ReturnType<typeof fetch>>()
      .mockResolvedValueOnce(jsonResponse({ id: 'proj_1', name: 'Project 1' }))
      .mockResolvedValueOnce(jsonResponse({ jobs: [{ job_id: 'job_1', page: 1 }] }))
      .mockResolvedValueOnce(
        jsonResponse({
          jobs: [
            { job_id: 'job_2', page: 1 },
            { job_id: 'job_3', page: 2 },
          ],
        })
      );

    vi.stubGlobal('fetch', fetchMock);

    const client = new StruAI({ apiKey: 'k', baseUrl: 'http://localhost:8000' });
    const project = await client.projects.create({ name: 'Project 1' });

    const single = await project.sheets.add(null, { page: 1, fileHash: 'abc123def4567890' });
    expect(single).toBeInstanceOf(Job);

    const multi = await project.sheets.add(null, { page: '1,2', fileHash: 'abc123def4567890' });
    expect(multi).toBeInstanceOf(JobBatch);
    expect((multi as JobBatch).ids).toEqual(['job_2', 'job_3']);
  });

  it('parses docquery search payload', async () => {
    const fetchMock = vi
      .fn<Parameters<typeof fetch>, ReturnType<typeof fetch>>()
      .mockResolvedValueOnce(jsonResponse({ id: 'proj_1', name: 'Project 1' }))
      .mockResolvedValueOnce(
        jsonResponse({
          ok: true,
          hits: [{ node: { properties: { uuid: 'node_1' } }, score: 0.88 }],
        })
      );

    vi.stubGlobal('fetch', fetchMock);

    const client = new StruAI({ apiKey: 'k', baseUrl: 'http://localhost:8000' });
    const project = await client.projects.create({ name: 'Project 1' });

    const result = await project.docquery.search('beam', { limit: 5 });
    expect(result.hits.length).toBe(1);
    expect(result.hits[0].score).toBe(0.88);
    expect((result.hits[0].node as any).properties.uuid).toBe('node_1');
    expect(fetchMock).toHaveBeenLastCalledWith(
      'http://localhost:8000/v1/projects/proj_1/search?query=beam&index=entity_search&limit=5',
      expect.any(Object)
    );
  });

  it('builds sheetSummary from docquery cypher calls', async () => {
    const cypher = (records: Array<Record<string, unknown>>) =>
      jsonResponse({
        ok: true,
        records,
      });

    const fetchMock = vi
      .fn<Parameters<typeof fetch>, ReturnType<typeof fetch>>()
      .mockResolvedValueOnce(jsonResponse({ id: 'proj_1', name: 'Project 1' }))
      .mockResolvedValueOnce(cypher([]))
      .mockResolvedValueOnce(cypher([{ label: 'Callout', count: 2 }]))
      .mockResolvedValueOnce(cypher([{ rel_type: 'REFERENCES', count: 5 }]))
      .mockResolvedValueOnce(
        cypher([
          {
            has_sheet_node: false,
            sheet_node_count: 0,
            non_sheet_total: 3,
            reachable_non_sheet: 1,
          },
        ])
      )
      .mockResolvedValueOnce(cypher([{ uuid: 'u1', labels: ['Callout'], category: 'callout', name: 'A' }]));

    vi.stubGlobal('fetch', fetchMock);

    const client = new StruAI({ apiKey: 'k', baseUrl: 'http://localhost:8000' });
    const project = await client.projects.create({ name: 'Project 1' });

    const summary = await project.docquery.sheetSummary('S111', { orphanLimit: 5 });
    expect(summary.command).toBe('sheet-summary');
    expect(summary.reachability.unreachable_non_sheet).toBe(2);
    expect(summary.warnings.map((w) => w.type)).toContain('missing_sheet_node');
    expect(summary.orphan_examples.length).toBe(1);
  });

  it('crops via server endpoint and writes png output', async () => {
    const tmpDir = await fs.mkdtemp(path.join(os.tmpdir(), 'struai-crop-'));
    const outputPath = path.join(tmpDir, 'crop.png');
    const bodyBytes = new Uint8Array([137, 80, 78, 71, 1, 2, 3, 4]);
    const fetchMock = vi
      .fn<Parameters<typeof fetch>, ReturnType<typeof fetch>>()
      .mockResolvedValueOnce(pngResponse(bodyBytes));

    vi.stubGlobal('fetch', fetchMock);

    const client = new StruAI({ apiKey: 'k', baseUrl: 'http://localhost:8000' });
    const project = client.projects.open('proj_1');
    const result = await project.docquery.crop({
      output: outputPath,
      bbox: [10, 15, 50, 45],
      pageHash: 'page_hash_1',
    });

    expect(result.ok).toBe(true);
    expect(result.output_path).toBe(outputPath);
    expect(result.bytes_written).toBe(bodyBytes.length);
    expect(result.content_type).toContain('image/png');

    const written = await fs.readFile(outputPath);
    expect(written.length).toBe(bodyBytes.length);
    expect(fetchMock).toHaveBeenCalledTimes(1);
    const [url, init] = fetchMock.mock.calls[0];
    expect(url).toBe('http://localhost:8000/v1/projects/proj_1/crop');
    expect((init as RequestInit).method).toBe('POST');
    expect((init as RequestInit).body).toBe(
      JSON.stringify({ bbox: [10, 15, 50, 45], page_hash: 'page_hash_1' })
    );
  });
});
