/**
 * StruAI JavaScript/TypeScript SDK.
 */

export interface StruAIOptions {
  apiKey: string;
  baseUrl?: string;
  timeout?: number;
}

export type Point = [number, number];
export type BBox = [number, number, number, number];
export type Uploadable = Blob | ArrayBuffer | ArrayBufferView | string;

export interface Dimensions {
  width: number;
  height: number;
}

export interface TextSpan {
  id?: string | number | null;
  text: string;
}

export interface Leader {
  id: string;
  bbox?: BBox | null;
  arrow_tip?: Point | null;
  text_bbox?: BBox | null;
  texts_inside: TextSpan[];
}

export interface SectionTag {
  id: string;
  bbox?: BBox | null;
  circle?: { center: Point; radius: number } | null;
  direction?: string | null;
  texts_inside: TextSpan[];
  section_line?: { start: Point; end: Point } | null;
}

export interface DetailTag {
  id: string;
  bbox?: BBox | null;
  circle?: { center: Point; radius: number } | null;
  texts_inside: TextSpan[];
  has_dashed_bbox?: boolean;
}

export interface RevisionTriangle {
  id: string;
  bbox?: BBox | null;
  vertices: Point[];
  text?: string | null;
}

export interface RevisionCloud {
  id: string;
  bbox?: BBox | null;
}

export interface Annotations {
  leaders: Leader[];
  section_tags: SectionTag[];
  detail_tags: DetailTag[];
  revision_triangles: RevisionTriangle[];
  revision_clouds: RevisionCloud[];
}

export interface TitleBlock {
  bounds?: BBox | null;
  viewport?: BBox | null;
}

export interface DrawingResult {
  id: string;
  page: number;
  dimensions: Dimensions;
  processing_ms: number;
  annotations: Annotations;
  titleblock?: TitleBlock | null;
}

export interface DrawingCacheStatus {
  cached: boolean;
  file_hash: string;
}

export interface DrawingDeleteResult {
  deleted: boolean;
  id: string;
}

export interface Project {
  id: string;
  name: string;
  description?: string | null;
  created_at?: string | null;
  sheet_count?: number;
  entity_count?: number;
  rel_count?: number;
  community_count?: number;
}

export interface ProjectDeleteResult {
  deleted: boolean;
  id: string;
}

export interface JobSummary {
  job_id: string;
  page: number;
}

export interface SheetIngestResponse {
  jobs: JobSummary[];
}

export interface SheetResult {
  sheet_id?: string;
  entities_created?: number;
  relationships_created?: number;
  skipped?: boolean;
  [key: string]: unknown;
}

export interface JobStatusEvent {
  seq: number;
  event: string;
  status: string;
  at_utc: string;
  message?: string;
  step?: {
    key: string;
    index: number;
    total: number;
    label: string;
  };
  error?: Record<string, unknown>;
}

export interface JobStatus {
  job_id: string;
  page?: number;
  status: 'queued' | 'running' | 'complete' | 'failed' | string;
  created_at_utc?: string | null;
  started_at_utc?: string | null;
  completed_at_utc?: string | null;
  current_step?: string | null;
  step_timings?: Record<string, { start_utc?: string; end_utc?: string; duration_ms?: number }>;
  status_log?: JobStatusEvent[];
  result?: SheetResult;
  error?: string;
}

export interface SheetSummary {
  id: string;
  sheet_uuid?: string | null;
  title?: string | null;
  revision?: string | null;
  page?: number | null;
  width?: number | null;
  height?: number | null;
  mention_count?: number;
  component_instance_count?: number;
  region_count?: number;
  created_at?: string | null;
}

export interface SheetRegion {
  id: string;
  type?: string;
  label?: string;
  category?: string;
  description?: string;
  bbox?: BBox | null;
}

export interface SheetMention {
  id: string;
  type?: string;
  label?: string;
  text?: string;
  description?: string;
  bbox?: BBox | null;
  region_id?: string;
  attributes?: unknown;
  provenance?: unknown;
}

export interface SheetComponentInstance {
  id: string;
  label?: string;
  family?: string;
  material?: string;
  discipline?: string;
  bbox?: BBox | null;
  region_id?: string;
  component_type_uuid?: string;
  resolution_state?: string;
  resolution_reason?: string;
}

export interface SheetReference {
  id: string;
  source_id?: string;
  target_sheet_id?: string;
  target_sheet_uuid?: string;
  target_unresolved?: boolean;
  fact?: string;
  target_detail?: string;
}

export interface SheetDetail {
  id: string;
  sheet_uuid?: string | null;
  title?: string | null;
  revision?: string | null;
  page?: number | null;
  width?: number | null;
  height?: number | null;
  regions: SheetRegion[];
  mentions: SheetMention[];
  component_instances: SheetComponentInstance[];
  references: SheetReference[];
}

export interface SheetAnnotations {
  sheet_id: string;
  page: number;
  dimensions: Dimensions;
  annotations: {
    leaders: Array<Record<string, unknown>>;
    section_tags: Array<Record<string, unknown>>;
    detail_tags: Array<Record<string, unknown>>;
    revision_triangles: Array<Record<string, unknown>>;
    revision_clouds: Array<Record<string, unknown>>;
    [key: string]: Array<Record<string, unknown>>;
  };
  titleblock?: Record<string, unknown> | null;
}

export interface SheetDeleteResult {
  deleted: boolean;
  sheet_id: string;
  cleanup?: {
    deleted_nodes?: number;
    deleted_fact_uuids?: string[];
    deleted_reference_uuids?: string[];
  };
  maintenance?: {
    community_mode?: string;
    semantic_index_mode?: string;
    communities_count?: number;
    semantic_points_upserted?: number;
    semantic_points_deleted?: number;
  };
}

export interface ConnectedEntity {
  id: string;
  type: string;
  label?: string;
  description?: string;
  sheet_id?: string;
  bbox?: BBox | null;
}

export interface GraphContext {
  connected_entities: ConnectedEntity[];
  relationships: Array<{ type?: string; fact?: string }>;
}

export interface EntitySearchHit {
  id: string;
  type: string;
  label?: string;
  description?: string;
  sheet_id?: string;
  bbox?: BBox | null;
  score: number;
  attributes?: Record<string, unknown>;
  graph_context?: GraphContext;
}

export interface FactSearchHit {
  id: string;
  predicate?: string;
  source?: string;
  target?: string;
  fact_text?: string;
  sheet_id?: string;
  score: number;
}

export interface CommunitySearchHit {
  id: string;
  name?: string;
  summary?: string;
  member_count?: number;
  score: number;
}

export interface SearchResponse {
  entities: EntitySearchHit[];
  facts: FactSearchHit[];
  communities: CommunitySearchHit[];
  search_ms: number;
}

export interface EntityListItem {
  id: string;
  type: string;
  label: string;
  description?: string;
  sheet_id?: string;
  bbox?: BBox | null;
  attributes?: unknown;
}

export interface EntityLocation {
  sheet_id: string;
  page?: number;
}

export interface EntityRelation {
  id: string;
  type: string;
  fact?: string;
  source_id?: string;
  target_id?: string;
  other_id?: string;
  other_label?: string;
  sheet_id?: string;
  valid_at?: string | null;
  invalid_at?: string | null;
  target_sheet_id?: string | null;
  target_unresolved?: boolean;
  target_sheet?: Record<string, unknown>;
}

export interface Entity {
  id: string;
  type: string;
  label: string;
  description?: string;
  sheet_id?: string;
  bbox?: BBox | null;
  attributes?: unknown;
  provenance?: unknown;
  outgoing: EntityRelation[];
  incoming: EntityRelation[];
  locations: EntityLocation[];
}

export interface Fact {
  id: string;
  type: string;
  fact?: string;
  source_id?: string;
  target_id?: string;
  sheet_id?: string;
  valid_at?: string | null;
  invalid_at?: string | null;
  target_sheet_id?: string | null;
  target_unresolved?: boolean;
}

const DEFAULT_BASE_URL = 'https://api.stru.ai';

function normalizeBaseUrl(raw: string): string {
  const trimmed = raw.replace(/\/$/, '');
  try {
    const parsed = new URL(trimmed);
    const path = parsed.pathname.replace(/\/$/, '');
    if (path === '' || path === '/') {
      parsed.pathname = '/v1';
      return parsed.toString().replace(/\/$/, '');
    }
    return trimmed;
  } catch {
    if (trimmed.endsWith('/v1')) {
      return trimmed;
    }
    return `${trimmed}/v1`;
  }
}

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

function delay(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function parsePageSelector(page: number | string): string {
  if (typeof page === 'number') {
    return String(page);
  }
  const text = page.trim();
  if (!text) {
    throw new Error('page is required');
  }
  return text;
}

function bufferToHex(buffer: ArrayBuffer): string {
  return Array.from(new Uint8Array(buffer))
    .map((b) => b.toString(16).padStart(2, '0'))
    .join('');
}

function toArrayBuffer(bytes: Uint8Array): ArrayBuffer {
  return bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength) as ArrayBuffer;
}

async function readUploadableBytes(file: Uploadable): Promise<Uint8Array> {
  if (typeof file === 'string') {
    const fs = await import('node:fs/promises');
    const data = await fs.readFile(file);
    return new Uint8Array(data.buffer, data.byteOffset, data.byteLength);
  }

  if (file instanceof ArrayBuffer) {
    return new Uint8Array(file);
  }

  if (ArrayBuffer.isView(file)) {
    return new Uint8Array(file.buffer, file.byteOffset, file.byteLength);
  }

  const blob = file as Blob;
  return new Uint8Array(await blob.arrayBuffer());
}

async function computeFileHash(file: Uploadable): Promise<string> {
  const bytes = await readUploadableBytes(file);

  if (globalThis.crypto?.subtle) {
    const digest = await globalThis.crypto.subtle.digest('SHA-256', toArrayBuffer(bytes));
    return bufferToHex(digest).slice(0, 16);
  }

  const crypto = await import('node:crypto');
  const hash = crypto.createHash('sha256').update(Buffer.from(bytes)).digest('hex');
  return hash.slice(0, 16);
}

async function uploadableToFormPart(file: Uploadable): Promise<{ blob: Blob; filename: string }> {
  if (typeof file === 'string') {
    const path = await import('node:path');
    const bytes = await readUploadableBytes(file);
    return {
      blob: new Blob([toArrayBuffer(bytes)], { type: 'application/pdf' }),
      filename: path.basename(file),
    };
  }

  if (file instanceof ArrayBuffer || ArrayBuffer.isView(file)) {
    const bytes = await readUploadableBytes(file);
    return {
      blob: new Blob([toArrayBuffer(bytes)], { type: 'application/pdf' }),
      filename: 'document.pdf',
    };
  }

  const blob = file as Blob;
  const name = (blob as File).name ?? 'document.pdf';
  return { blob, filename: name };
}

class Drawings {
  constructor(private client: StruAI) {}

  async analyze(
    file: Uploadable | null,
    options: { page: number; fileHash?: string }
  ): Promise<DrawingResult> {
    let fileHash = options.fileHash;

    if (fileHash && file) {
      throw new Error('Provide file or fileHash, not both.');
    }
    if (!fileHash && !file) {
      throw new Error('Provide file or fileHash.');
    }

    if (!fileHash && file) {
      const computedHash = await computeFileHash(file);
      const cache = await this.checkCache(computedHash);
      if (cache.cached) {
        fileHash = computedHash;
        file = null;
      }
    }

    const formData = new FormData();
    formData.append('page', String(options.page));
    if (fileHash) {
      formData.append('file_hash', fileHash);
    }
    if (file) {
      const part = await uploadableToFormPart(file);
      formData.append('file', part.blob, part.filename);
    }

    return this.client.request<DrawingResult>('/drawings', {
      method: 'POST',
      body: formData,
    });
  }

  async checkCache(fileHash: string): Promise<DrawingCacheStatus> {
    return this.client.request<DrawingCacheStatus>(`/drawings/cache/${fileHash}`);
  }

  async get(drawingId: string): Promise<DrawingResult> {
    return this.client.request<DrawingResult>(`/drawings/${drawingId}`);
  }

  async delete(drawingId: string): Promise<DrawingDeleteResult> {
    return this.client.request<DrawingDeleteResult>(`/drawings/${drawingId}`, {
      method: 'DELETE',
    });
  }

  async computeFileHash(file: Uploadable): Promise<string> {
    return computeFileHash(file);
  }
}

class Job {
  constructor(
    private client: StruAI,
    private projectId: string,
    public readonly id: string,
    public readonly page?: number
  ) {}

  async status(): Promise<JobStatus> {
    return this.client.request<JobStatus>(`/projects/${this.projectId}/jobs/${this.id}`);
  }

  async wait(options?: { timeoutMs?: number; pollIntervalMs?: number }): Promise<SheetResult> {
    const timeoutMs = options?.timeoutMs ?? 120_000;
    const pollIntervalMs = options?.pollIntervalMs ?? 2_000;
    const start = Date.now();

    while (Date.now() - start < timeoutMs) {
      const status = await this.status();
      if (status.status === 'complete') {
        return status.result ?? {};
      }
      if (status.status === 'failed') {
        throw new APIError(`Job ${this.id} failed: ${status.error}`);
      }
      await delay(pollIntervalMs);
    }

    throw new APIError(`Job ${this.id} did not complete within ${timeoutMs}ms`);
  }
}

class JobBatch {
  constructor(public readonly jobs: Job[]) {}

  get ids(): string[] {
    return this.jobs.map((job) => job.id);
  }

  async statusAll(): Promise<JobStatus[]> {
    return Promise.all(this.jobs.map((job) => job.status()));
  }

  async waitAll(options?: { timeoutMs?: number; pollIntervalMs?: number }): Promise<SheetResult[]> {
    return Promise.all(this.jobs.map((job) => job.wait(options)));
  }
}

class Sheets {
  constructor(
    private client: StruAI,
    private projectId: string
  ) {}

  async add(
    file: Uploadable | null,
    options: {
      page: number | string;
      fileHash?: string;
      sourceDescription?: string;
      onSheetExists?: 'error' | 'skip' | 'rebuild';
      communityUpdateMode?: 'incremental' | 'rebuild';
      semanticIndexUpdateMode?: 'incremental' | 'rebuild';
    }
  ): Promise<Job | JobBatch> {
    let fileHash = options.fileHash;

    if (fileHash && file) {
      throw new Error('Provide file or fileHash, not both.');
    }
    if (!fileHash && !file) {
      throw new Error('Provide file or fileHash.');
    }

    if (!fileHash && file) {
      const computedHash = await computeFileHash(file);
      try {
        const cache = await this.client.request<DrawingCacheStatus>(`/drawings/cache/${computedHash}`);
        if (cache.cached) {
          file = null;
          fileHash = computedHash;
        }
      } catch {
        // Fail open: continue with upload
      }
    }

    const formData = new FormData();
    formData.append('page', parsePageSelector(options.page));
    if (fileHash) {
      formData.append('file_hash', fileHash);
    }
    if (options.sourceDescription !== undefined) {
      formData.append('source_description', options.sourceDescription);
    }
    if (options.onSheetExists) {
      formData.append('on_sheet_exists', options.onSheetExists);
    }
    if (options.communityUpdateMode) {
      formData.append('community_update_mode', options.communityUpdateMode);
    }
    if (options.semanticIndexUpdateMode) {
      formData.append('semantic_index_update_mode', options.semanticIndexUpdateMode);
    }
    if (file) {
      const part = await uploadableToFormPart(file);
      formData.append('file', part.blob, part.filename);
    }

    const response = await this.client.request<SheetIngestResponse>(`/projects/${this.projectId}/sheets`, {
      method: 'POST',
      body: formData,
    });

    const jobs = (response.jobs ?? []).map(
      (item) => new Job(this.client, this.projectId, item.job_id, item.page)
    );
    if (jobs.length === 1) {
      return jobs[0];
    }
    return new JobBatch(jobs);
  }

  async list(options?: { limit?: number }): Promise<SheetSummary[]> {
    const params = new URLSearchParams();
    if (options?.limit !== undefined) {
      params.set('limit', String(options.limit));
    }
    const query = params.toString();
    const response = await this.client.request<{ sheets: SheetSummary[] }>(
      query
        ? `/projects/${this.projectId}/sheets?${query}`
        : `/projects/${this.projectId}/sheets`
    );
    return response.sheets ?? [];
  }

  async get(sheetId: string): Promise<SheetDetail> {
    return this.client.request<SheetDetail>(`/projects/${this.projectId}/sheets/${sheetId}`);
  }

  async getAnnotations(sheetId: string): Promise<SheetAnnotations> {
    return this.client.request<SheetAnnotations>(
      `/projects/${this.projectId}/sheets/${sheetId}/annotations`
    );
  }

  async delete(sheetId: string): Promise<SheetDeleteResult> {
    return this.client.request<SheetDeleteResult>(`/projects/${this.projectId}/sheets/${sheetId}`, {
      method: 'DELETE',
    });
  }
}

class Entities {
  constructor(
    private client: StruAI,
    private projectId: string
  ) {}

  async list(options?: {
    sheetId?: string;
    type?: string;
    family?: string;
    normalizedSpec?: string;
    regionUuid?: string;
    regionLabel?: string;
    noteNumber?: string;
    limit?: number;
  }): Promise<EntityListItem[]> {
    const params = new URLSearchParams();
    if (options?.limit !== undefined) params.set('limit', String(options.limit));
    if (options?.sheetId) params.set('sheet_id', options.sheetId);
    if (options?.type) params.set('type', options.type);
    if (options?.family) params.set('family', options.family);
    if (options?.normalizedSpec) params.set('normalized_spec', options.normalizedSpec);
    if (options?.regionUuid) params.set('region_uuid', options.regionUuid);
    if (options?.regionLabel) params.set('region_label', options.regionLabel);
    if (options?.noteNumber) params.set('note_number', options.noteNumber);

    const query = params.toString();
    const response = await this.client.request<{ entities: EntityListItem[] }>(
      query
        ? `/projects/${this.projectId}/entities?${query}`
        : `/projects/${this.projectId}/entities`
    );
    return response.entities ?? [];
  }

  async get(entityId: string, options?: { includeInvalid?: boolean; expandTarget?: boolean }): Promise<Entity> {
    const params = new URLSearchParams();
    if (options?.includeInvalid !== undefined) {
      params.set('include_invalid', String(options.includeInvalid));
    }
    if (options?.expandTarget !== undefined) {
      params.set('expand_target', String(options.expandTarget));
    }
    const query = params.toString();
    return this.client.request<Entity>(
      query
        ? `/projects/${this.projectId}/entities/${entityId}?${query}`
        : `/projects/${this.projectId}/entities/${entityId}`
    );
  }
}

class Relationships {
  constructor(
    private client: StruAI,
    private projectId: string
  ) {}

  async list(options?: {
    sheetId?: string;
    sourceId?: string;
    targetId?: string;
    type?: string;
    includeInvalid?: boolean;
    invalidOnly?: boolean;
    orphanOnly?: boolean;
    limit?: number;
  }): Promise<Fact[]> {
    const params = new URLSearchParams();
    if (options?.limit !== undefined) params.set('limit', String(options.limit));
    if (options?.sheetId) params.set('sheet_id', options.sheetId);
    if (options?.sourceId) params.set('source_id', options.sourceId);
    if (options?.targetId) params.set('target_id', options.targetId);
    if (options?.type) params.set('type', options.type);
    if (options?.includeInvalid !== undefined) params.set('include_invalid', String(options.includeInvalid));
    if (options?.invalidOnly !== undefined) params.set('invalid_only', String(options.invalidOnly));
    if (options?.orphanOnly !== undefined) params.set('orphan_only', String(options.orphanOnly));

    const query = params.toString();
    const response = await this.client.request<{ relationships: Fact[] }>(
      query
        ? `/projects/${this.projectId}/relationships?${query}`
        : `/projects/${this.projectId}/relationships`
    );
    return response.relationships ?? [];
  }
}

class ProjectInstance {
  public readonly sheets: Sheets;
  public readonly entities: Entities;
  public readonly relationships: Relationships;

  constructor(
    private client: StruAI,
    private project: Project
  ) {
    this.sheets = new Sheets(client, project.id);
    this.entities = new Entities(client, project.id);
    this.relationships = new Relationships(client, project.id);
  }

  get id(): string {
    return this.project.id;
  }

  get name(): string {
    return this.project.name;
  }

  get description(): string | null | undefined {
    return this.project.description;
  }

  get data(): Project {
    return this.project;
  }

  async search(
    query: string,
    options?: {
      limit?: number;
      channels?: Array<'entities' | 'facts' | 'communities'>;
      includeGraphContext?: boolean;
    }
  ): Promise<SearchResponse> {
    return this.client.request<SearchResponse>(`/projects/${this.id}/search`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query,
        limit: options?.limit ?? 10,
        channels: options?.channels,
        include_graph_context: options?.includeGraphContext ?? true,
      }),
    });
  }

  async delete(): Promise<ProjectDeleteResult> {
    return this.client.request<ProjectDeleteResult>(`/projects/${this.id}`, { method: 'DELETE' });
  }
}

class Projects {
  constructor(private client: StruAI) {}

  async create(options: { name: string; description?: string }): Promise<ProjectInstance> {
    const project = await this.client.request<Project>('/projects', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(options),
    });
    return new ProjectInstance(this.client, project);
  }

  async list(options?: { limit?: number }): Promise<Project[]> {
    const params = new URLSearchParams();
    if (options?.limit !== undefined) params.set('limit', String(options.limit));
    const query = params.toString();

    const response = await this.client.request<{ projects: Project[] }>(
      query ? `/projects?${query}` : '/projects'
    );
    return response.projects ?? [];
  }

  async get(projectId: string): Promise<ProjectInstance> {
    const project = await this.client.request<Project>(`/projects/${projectId}`);
    return new ProjectInstance(this.client, project);
  }

  async delete(projectId: string): Promise<ProjectDeleteResult> {
    return this.client.request<ProjectDeleteResult>(`/projects/${projectId}`, { method: 'DELETE' });
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
    this.baseUrl = normalizeBaseUrl(options.baseUrl ?? DEFAULT_BASE_URL);
    this.timeout = options.timeout ?? 60_000;

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
        let code: string | undefined;
        try {
          const body = await response.json();
          message = body?.error?.message ?? message;
          code = body?.error?.code;
        } catch {
          // fall through
        }
        throw new APIError(message, response.status, code);
      }

      if (response.status === 204) {
        return undefined as T;
      }

      const text = await response.text();
      if (!text) {
        return undefined as T;
      }
      return JSON.parse(text) as T;
    } finally {
      clearTimeout(timeoutId);
    }
  }
}

export { APIError, Job, JobBatch, ProjectInstance, Projects, Drawings, Sheets, Entities, Relationships };
export default StruAI;
