import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import sharp from 'sharp';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { Job, JobBatch, StruAI } from '../src/index';

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
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
          command: 'search',
          input: { project_id: 'proj_1', query: 'beam', index: 'entity_search', limit: 5 },
          hits: [{ node: { properties: { uuid: 'node_1' } }, score: 0.88 }],
          count: 1,
          summary: {},
        })
      );

    vi.stubGlobal('fetch', fetchMock);

    const client = new StruAI({ apiKey: 'k', baseUrl: 'http://localhost:8000' });
    const project = await client.projects.create({ name: 'Project 1' });

    const result = await project.docquery.search('beam', { limit: 5 });
    expect(result.count).toBe(1);
    expect(result.hits[0].score).toBe(0.88);
    expect((result.hits[0].node as any).properties.uuid).toBe('node_1');
  });

  it('builds sheetSummary from docquery cypher calls', async () => {
    const cypher = (records: Array<Record<string, unknown>>) =>
      jsonResponse({
        ok: true,
        command: 'cypher',
        input: {},
        records,
        record_count: records.length,
        truncated: false,
        summary: {},
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

  it('crops an image region in bbox mode', async () => {
    const tmpDir = await fs.mkdtemp(path.join(os.tmpdir(), 'struai-crop-'));
    const sourcePath = path.join(tmpDir, 'source.png');
    const outputPath = path.join(tmpDir, 'crop.png');
    await sharp({
      create: {
        width: 120,
        height: 80,
        channels: 3,
        background: { r: 255, g: 255, b: 255 },
      },
    })
      .png()
      .toFile(sourcePath);

    const client = new StruAI({ apiKey: 'k', baseUrl: 'http://localhost:8000' });
    const project = client.projects.open('proj_1');
    const result = await project.docquery.crop({
      image: sourcePath,
      output: outputPath,
      bbox: [10, 15, 50, 45],
    });

    expect(result.command).toBe('crop');
    expect(result.output_image.width).toBe(40);
    expect(result.output_image.height).toBe(30);
    await expect(fs.stat(outputPath)).resolves.toBeDefined();
  });
});
