"""Tier 2: project, sheet, and job models."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import Field

from .common import BBox, Dimensions, SDKBaseModel
from .drawings import TitleBlock


class Project(SDKBaseModel):
    """Project metadata."""

    id: str
    name: str
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    sheet_count: Optional[int] = None
    entity_count: Optional[int] = None
    rel_count: Optional[int] = None
    community_count: Optional[int] = None


class ProjectListResponse(SDKBaseModel):
    """Response for GET /v1/projects."""

    projects: List[Project] = Field(default_factory=list)


class ProjectDeleteResult(SDKBaseModel):
    """Response for DELETE /v1/projects/{id}."""

    deleted: bool
    id: str


class SheetSummary(SDKBaseModel):
    """Summary from GET /v1/projects/{id}/sheets."""

    id: str
    sheet_uuid: Optional[str] = None
    title: Optional[str] = None
    revision: Optional[str] = None
    page: Optional[int] = None
    width: Optional[float] = None
    height: Optional[float] = None
    mention_count: Optional[int] = None
    component_instance_count: Optional[int] = None
    region_count: Optional[int] = None
    created_at: Optional[datetime] = None


class SheetListResponse(SDKBaseModel):
    """Response for GET /v1/projects/{id}/sheets."""

    project_id: str
    sheets: List[SheetSummary] = Field(default_factory=list)


class SheetRegion(SDKBaseModel):
    """Region listed in sheet detail."""

    id: str
    type: Optional[str] = None
    label: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    bbox: Optional[BBox] = None


class SheetMention(SDKBaseModel):
    """Mention listed in sheet detail."""

    id: str
    type: Optional[str] = None
    label: Optional[str] = None
    text: Optional[str] = None
    description: Optional[str] = None
    bbox: Optional[BBox] = None
    region_id: Optional[str] = None
    attributes: Optional[Union[Dict[str, Any], List[Any], str]] = None
    provenance: Optional[Union[Dict[str, Any], List[Any], str]] = None


class SheetComponentInstance(SDKBaseModel):
    """Component instance listed in sheet detail."""

    id: str
    label: Optional[str] = None
    family: Optional[str] = None
    material: Optional[str] = None
    discipline: Optional[str] = None
    bbox: Optional[BBox] = None
    region_id: Optional[str] = None
    component_type_uuid: Optional[str] = None
    resolution_state: Optional[str] = None
    resolution_reason: Optional[str] = None


class SheetReference(SDKBaseModel):
    """Reference listed in sheet detail."""

    id: str
    source_id: Optional[str] = None
    target_sheet_id: Optional[str] = None
    target_sheet_uuid: Optional[str] = None
    target_unresolved: Optional[bool] = None
    fact: Optional[str] = None
    target_detail: Optional[str] = None


class SheetDetail(SDKBaseModel):
    """Detailed sheet payload from GET /v1/projects/{id}/sheets/{sheet_id}."""

    id: str
    sheet_uuid: Optional[str] = None
    title: Optional[str] = None
    revision: Optional[str] = None
    page: Optional[int] = None
    width: Optional[float] = None
    height: Optional[float] = None
    regions: List[SheetRegion] = Field(default_factory=list)
    mentions: List[SheetMention] = Field(default_factory=list)
    component_instances: List[SheetComponentInstance] = Field(default_factory=list)
    references: List[SheetReference] = Field(default_factory=list)


class SheetAnnotations(SDKBaseModel):
    """Raw annotations for a sheet."""

    sheet_id: str
    page: int
    dimensions: Dimensions
    annotations: Dict[str, List[Dict[str, Any]]] = Field(default_factory=dict)
    titleblock: Optional[TitleBlock] = None


class SheetDeleteCleanup(SDKBaseModel):
    """Cleanup section from sheet deletion response."""

    deleted_nodes: int = 0
    deleted_fact_uuids: List[str] = Field(default_factory=list)
    deleted_reference_uuids: List[str] = Field(default_factory=list)


class SheetDeleteMaintenance(SDKBaseModel):
    """Maintenance section from sheet deletion response."""

    community_mode: Optional[str] = None
    semantic_index_mode: Optional[str] = None
    communities_count: Optional[int] = None
    semantic_points_upserted: Optional[int] = None
    semantic_points_deleted: Optional[int] = None


class SheetDeleteResult(SDKBaseModel):
    """Response for DELETE /v1/projects/{id}/sheets/{sheet_id}."""

    deleted: bool
    sheet_id: str
    cleanup: Optional[SheetDeleteCleanup] = None
    maintenance: Optional[SheetDeleteMaintenance] = None


class JobSummary(SDKBaseModel):
    """Queued job descriptor from sheet ingest request."""

    job_id: str
    page: int


class SheetIngestResponse(SDKBaseModel):
    """Response for POST /v1/projects/{id}/sheets."""

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
    """Current job status from GET /v1/projects/{id}/jobs/{job_id}."""

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
