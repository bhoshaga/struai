/**
 * StruAI JavaScript SDK - Drawing Analysis API client
 *
 * @example
 * ```typescript
 * import { StruAI } from 'struai';
 *
 * const client = new StruAI({ apiKey: 'sk-xxx' });
 *
 * // Tier 1: Raw detection
 * const result = await client.drawings.analyze('structural.pdf', { page: 4 });
 *
 * // Tier 2: Graph + Search
 * const project = await client.projects.create({ name: 'Building A' });
 * const job = await project.sheets.add('structural.pdf', { page: 4 });
 * await job.wait();
 * const results = await project.search('W12x26 beam connections');
 * ```
 */

export interface StruAIOptions {
  apiKey: string;
  baseUrl?: string;
  timeout?: number;
}

export interface Dimensions {
  width: number;
  height: number;
}

export interface TextSpan {
  id: number;
  text: string;
}

export interface Leader {
  id: string;
  bbox: [number, number, number, number];
  arrow_tip: [number, number];
  text_bbox: [number, number, number, number];
  texts_inside: TextSpan[];
}

export interface SectionTag {
  id: string;
  bbox: [number, number, number, number];
  circle: { center: [number, number]; radius: number };
  direction: string;
  texts_inside: TextSpan[];
  section_line?: { start: [number, number]; end: [number, number] };
}

export interface DetailTag {
  id: string;
  bbox: [number, number, number, number];
  circle: { center: [number, number]; radius: number };
  texts_inside: TextSpan[];
  has_dashed_bbox: boolean;
}

export interface RevisionTriangle {
  id: string;
  bbox: [number, number, number, number];
  vertices: [number, number][];
  text: string;
}

export interface RevisionCloud {
  id: string;
  bbox: [number, number, number, number];
}

export interface Annotations {
  leaders: Leader[];
  section_tags: SectionTag[];
  detail_tags: DetailTag[];
  revision_triangles: RevisionTriangle[];
  revision_clouds: RevisionCloud[];
}

export interface TitleBlock {
  bounds: [number, number, number, number];
  viewport: [number, number, number, number];
}

export interface DrawingResult {
  id: string;
  page: number;
  dimensions: Dimensions;
  processing_ms: number;
  annotations: Annotations;
  titleblock?: TitleBlock;
}

export interface Project {
  id: string;
  name: string;
  description?: string;
  created_at: string;
  sheets_count: number;
  entities_count: number;
}

export interface Sheet {
  id: string;
  title?: string;
  page: number;
  width: number;
  height: number;
  created_at: string;
  entities_count: number;
}

export interface SheetResult {
  sheet_id: string;
  entities_created: number;
  relationships_created: number;
}

export interface JobStatus {
  job_id: string;
  status: 'processing' | 'complete' | 'failed';
  steps: {
    detection: { status: string; duration_ms?: number };
    enrichment: { status: string; duration_ms?: number; tokens?: number };
    synthesis: { status: string; duration_ms?: number; tokens?: number };
    graph: { status: string; duration_ms?: number };
  };
  result?: SheetResult;
  error?: string;
}

export interface SearchHit {
  entity: {
    id: string;
    type: string;
    label: string;
    description?: string;
    sheet_id: string;
    bbox?: [number, number, number, number];
  };
  score: number;
  graph_context?: {
    connected_entities: Array<{ id: string; type: string; label: string }>;
    relationships: Array<{ type: string; fact: string }>;
  };
}

export interface SearchResponse {
  results: SearchHit[];
  search_ms: number;
}

export interface QueryResponse {
  answer: string;
  sources: Array<{
    entity_id: string;
    sheet_id: string;
    label: string;
    bbox?: [number, number, number, number];
  }>;
  confidence: number;
}

const DEFAULT_BASE_URL = 'https://api.stru.ai/v1';

class APIError extends Error {
  constructor(
    message: string,
    public statusCode?: number,
    public code?: string
  ) {
    super(message);
    this.name = 'APIError';
  }
}

class Drawings {
  constructor(private client: StruAI) {}

  async analyze(
    file: File | Blob | string,
    options: { page: number }
  ): Promise<DrawingResult> {
    const formData = new FormData();
    if (typeof file === 'string') {
      // file path - only works in Node.js
      throw new Error('File paths not supported in browser. Pass a File or Blob.');
    }
    formData.append('file', file);
    formData.append('page', options.page.toString());

    return this.client.request<DrawingResult>('/drawings', {
      method: 'POST',
      body: formData,
    });
  }

  async get(drawingId: string): Promise<DrawingResult> {
    return this.client.request<DrawingResult>(`/drawings/${drawingId}`);
  }

  async delete(drawingId: string): Promise<void> {
    await this.client.request(`/drawings/${drawingId}`, { method: 'DELETE' });
  }
}

class Job {
  constructor(
    private client: StruAI,
    private projectId: string,
    public readonly id: string
  ) {}

  async status(): Promise<JobStatus> {
    return this.client.request<JobStatus>(
      `/projects/${this.projectId}/jobs/${this.id}`
    );
  }

  async wait(options?: { timeout?: number; pollInterval?: number }): Promise<SheetResult> {
    const timeout = options?.timeout ?? 120000;
    const pollInterval = options?.pollInterval ?? 2000;
    const start = Date.now();

    while (Date.now() - start < timeout) {
      const status = await this.status();
      if (status.status === 'complete' && status.result) {
        return status.result;
      }
      if (status.status === 'failed') {
        throw new APIError(`Job ${this.id} failed: ${status.error}`);
      }
      await new Promise((r) => setTimeout(r, pollInterval));
    }
    throw new APIError(`Job ${this.id} did not complete within ${timeout}ms`);
  }
}

class Sheets {
  constructor(
    private client: StruAI,
    private projectId: string
  ) {}

  async add(
    file: File | Blob,
    options: { page: number; webhookUrl?: string }
  ): Promise<Job> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('page', options.page.toString());
    if (options.webhookUrl) {
      formData.append('webhook_url', options.webhookUrl);
    }

    const response = await this.client.request<{ job_id: string }>(
      `/projects/${this.projectId}/sheets`,
      { method: 'POST', body: formData }
    );
    return new Job(this.client, this.projectId, response.job_id);
  }

  async list(options?: { limit?: number }): Promise<Sheet[]> {
    const params = new URLSearchParams();
    if (options?.limit) params.set('limit', options.limit.toString());
    const response = await this.client.request<{ sheets: Sheet[] }>(
      `/projects/${this.projectId}/sheets?${params}`
    );
    return response.sheets;
  }

  async get(sheetId: string): Promise<Sheet> {
    return this.client.request<Sheet>(
      `/projects/${this.projectId}/sheets/${sheetId}`
    );
  }

  async delete(sheetId: string): Promise<void> {
    await this.client.request(`/projects/${this.projectId}/sheets/${sheetId}`, {
      method: 'DELETE',
    });
  }
}

class ProjectInstance {
  public readonly sheets: Sheets;

  constructor(
    private client: StruAI,
    private project: Project
  ) {
    this.sheets = new Sheets(client, project.id);
  }

  get id() {
    return this.project.id;
  }
  get name() {
    return this.project.name;
  }

  async search(
    query: string,
    options?: {
      limit?: number;
      filters?: { sheet_id?: string; entity_type?: string[] };
      includeGraphContext?: boolean;
    }
  ): Promise<SearchResponse> {
    return this.client.request<SearchResponse>(`/projects/${this.id}/search`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query,
        limit: options?.limit ?? 10,
        filters: options?.filters,
        include_graph_context: options?.includeGraphContext ?? true,
      }),
    });
  }

  async query(question: string): Promise<QueryResponse> {
    return this.client.request<QueryResponse>(`/projects/${this.id}/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question }),
    });
  }

  async delete(): Promise<void> {
    await this.client.request(`/projects/${this.id}`, { method: 'DELETE' });
  }
}

class Projects {
  constructor(private client: StruAI) {}

  async create(options: {
    name: string;
    description?: string;
  }): Promise<ProjectInstance> {
    const project = await this.client.request<Project>('/projects', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(options),
    });
    return new ProjectInstance(this.client, project);
  }

  async list(options?: { limit?: number }): Promise<Project[]> {
    const params = new URLSearchParams();
    if (options?.limit) params.set('limit', options.limit.toString());
    const response = await this.client.request<{ projects: Project[] }>(
      `/projects?${params}`
    );
    return response.projects;
  }

  async get(projectId: string): Promise<ProjectInstance> {
    const project = await this.client.request<Project>(`/projects/${projectId}`);
    return new ProjectInstance(this.client, project);
  }

  async delete(projectId: string): Promise<void> {
    await this.client.request(`/projects/${projectId}`, { method: 'DELETE' });
  }
}

export class StruAI {
  private apiKey: string;
  private baseUrl: string;
  private timeout: number;

  public readonly drawings: Drawings;
  public readonly projects: Projects;

  constructor(options: StruAIOptions) {
    this.apiKey = options.apiKey;
    this.baseUrl = (options.baseUrl ?? DEFAULT_BASE_URL).replace(/\/$/, '');
    this.timeout = options.timeout ?? 60000;

    this.drawings = new Drawings(this);
    this.projects = new Projects(this);
  }

  async request<T>(path: string, init?: RequestInit): Promise<T> {
    const url = `${this.baseUrl}${path}`;
    const headers = new Headers(init?.headers);
    headers.set('Authorization', `Bearer ${this.apiKey}`);

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);

    try {
      const response = await fetch(url, {
        ...init,
        headers,
        signal: controller.signal,
      });

      if (!response.ok) {
        let message = response.statusText;
        try {
          const body = await response.json();
          message = body.error?.message ?? message;
        } catch {}
        throw new APIError(message, response.status);
      }

      if (response.status === 204) {
        return undefined as T;
      }

      return response.json();
    } finally {
      clearTimeout(timeoutId);
    }
  }
}

export { APIError };
export default StruAI;
