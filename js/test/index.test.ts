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
});
