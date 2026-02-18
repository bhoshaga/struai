"""Tier 2: project, sheet ingest, and job models."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import Field

from .common import SDKBaseModel


class Project(SDKBaseModel):
    """Project metadata returned by /v1/projects and /v1/projects create."""

    id: str
    name: str
    description: Optional[str] = None
    created_at: Optional[datetime] = None


class ProjectListResponse(SDKBaseModel):
    """Response for GET /v1/projects."""

    projects: List[Project] = Field(default_factory=list)


class ProjectDeleteResult(SDKBaseModel):
    """Response for DELETE /v1/projects/{project_id}."""

    deleted: bool
    project_id: str
    projects_deleted: Optional[int] = None
    nodes_deleted: Optional[int] = None
    relationships_deleted: Optional[int] = None
    owner_mapping_deleted: Optional[bool] = None
    qdrant_deleted_points: Optional[int] = None


class SheetDeleteResult(SDKBaseModel):
    """Response for DELETE /v1/projects/{project_id}/sheets/{sheet_id}."""

    deleted: bool
    project_id: str
    sheet_id: str
    nodes_deleted: Optional[int] = None
    relationships_deleted_by_source_sheet: Optional[int] = None
    qdrant: Optional[Dict[str, Any]] = None


class JobSummary(SDKBaseModel):
    """Queued job descriptor from sheet ingest request."""

    job_id: str
    page: int


class SheetIngestResponse(SDKBaseModel):
    """Response for POST /v1/projects/{project_id}/sheets."""

    jobs: List[JobSummary] = Field(default_factory=list)


class SheetResult(SDKBaseModel):
    """Result section in a completed job."""

    sheet_id: Optional[str] = None
    entities_created: Optional[int] = None
    relationships_created: Optional[int] = None
    skipped: Optional[bool] = None


class JobStepTiming(SDKBaseModel):
    """Public timing payload for each step."""

    start_utc: Optional[str] = None
    end_utc: Optional[str] = None
    duration_ms: Optional[int] = None


class JobStepRef(SDKBaseModel):
    """Step metadata included in status_log entries."""

    key: str
    index: int
    total: int
    label: str


class JobStatusEvent(SDKBaseModel):
    """Single status log event."""

    seq: int
    event: str
    status: str
    at_utc: str
    message: Optional[str] = None
    step: Optional[JobStepRef] = None
    error: Optional[Dict[str, Any]] = None


class JobStatus(SDKBaseModel):
    """Current job status from GET /v1/projects/{project_id}/jobs/{job_id}."""

    job_id: str
    page: Optional[int] = None
    status: str
    created_at_utc: Optional[str] = None
    started_at_utc: Optional[str] = None
    completed_at_utc: Optional[str] = None
    current_step: Optional[str] = None
    step_timings: Dict[str, JobStepTiming] = Field(default_factory=dict)
    status_log: List[JobStatusEvent] = Field(default_factory=list)
    result: Optional[SheetResult] = None
    error: Optional[str] = None

    @property
    def is_complete(self) -> bool:
        return self.status == "complete"

    @property
    def is_failed(self) -> bool:
        return self.status == "failed"

    @property
    def is_running(self) -> bool:
        return self.status == "running"

    @property
    def is_queued(self) -> bool:
        return self.status == "queued"
