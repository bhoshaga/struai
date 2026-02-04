"""Tier 2: Project and Sheet models."""
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class Project(BaseModel):
    """Project container for sheets."""

    id: str
    name: str
    description: Optional[str] = None
    created_at: datetime
    sheets_count: int = 0
    entities_count: int = 0


class Sheet(BaseModel):
    """Sheet in a project."""

    id: str
    title: Optional[str] = None
    name: Optional[str] = None
    page: int
    width: int
    height: int
    created_at: datetime
    entities_count: int = 0


class StepStatus(str, Enum):
    """Status of a pipeline step."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETE = "complete"
    FAILED = "failed"


class JobStep(BaseModel):
    """Status of a single pipeline step."""

    status: StepStatus
    duration_ms: Optional[int] = None
    tokens: Optional[int] = None
    error: Optional[str] = None


class JobSteps(BaseModel):
    """All pipeline steps."""

    detection: JobStep
    enrichment: JobStep
    synthesis: JobStep
    graph: JobStep


class SheetResult(BaseModel):
    """Result of sheet ingestion."""

    sheet_id: str
    entities_created: int
    relationships_created: int


class JobStatus(BaseModel):
    """Current job status."""

    job_id: str
    status: str  # "processing", "complete", "failed"
    steps: JobSteps
    result: Optional[SheetResult] = None
    error: Optional[str] = None

    @property
    def is_complete(self) -> bool:
        return self.status == "complete"

    @property
    def is_failed(self) -> bool:
        return self.status == "failed"
