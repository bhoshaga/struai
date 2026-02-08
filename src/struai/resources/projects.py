"""Tier 2 projects resource."""

from __future__ import annotations

import asyncio
import time
from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING, BinaryIO, Dict, List, Optional, Tuple, Union

from .._exceptions import JobFailedError, TimeoutError
from ..models.entities import Entity, EntityListItem, Fact
from ..models.projects import (
    JobStatus,
    Project,
    ProjectDeleteResult,
    SheetAnnotations,
    SheetDeleteResult,
    SheetDetail,
    SheetIngestResponse,
    SheetResult,
    SheetSummary,
)
from ..models.search import SearchResponse
from .drawings import _compute_file_hash

if TYPE_CHECKING:
    from .._base import AsyncBaseClient, BaseClient

Uploadable = Union[str, Path, bytes, BinaryIO]
PreparedUpload = Tuple[dict, Optional[BinaryIO]]


# =============================================================================
# Job handles
# =============================================================================


class Job:
    """Handle for one async sheet-ingestion job (sync)."""

    def __init__(
        self,
        client: "BaseClient",
        project_id: str,
        job_id: str,
        page: Optional[int] = None,
    ):
        self._client = client
        self._project_id = project_id
        self._job_id = job_id
        self._page = page

    @property
    def id(self) -> str:
        return self._job_id

    @property
    def page(self) -> Optional[int]:
        return self._page

    def status(self) -> JobStatus:
        """Fetch current job status."""
        return self._client.get(
            f"/projects/{self._project_id}/jobs/{self._job_id}",
            cast_to=JobStatus,
        )

    def wait(self, timeout: float = 120, poll_interval: float = 2) -> SheetResult:
        """Wait for completion and return resulting sheet info."""
        start = time.time()
        while time.time() - start < timeout:
            status = self.status()
            if status.is_complete:
                if status.result is None:
                    return SheetResult()
                return status.result
            if status.is_failed:
                raise JobFailedError(
                    f"Job {self._job_id} failed: {status.error}",
                    job_id=self._job_id,
                    error=status.error or "Unknown error",
                )
            time.sleep(poll_interval)

        raise TimeoutError(f"Job {self._job_id} did not complete within {timeout}s")


class AsyncJob:
    """Handle for one async sheet-ingestion job (async)."""

    def __init__(
        self,
        client: "AsyncBaseClient",
        project_id: str,
        job_id: str,
        page: Optional[int] = None,
    ):
        self._client = client
        self._project_id = project_id
        self._job_id = job_id
        self._page = page

    @property
    def id(self) -> str:
        return self._job_id

    @property
    def page(self) -> Optional[int]:
        return self._page

    async def status(self) -> JobStatus:
        """Fetch current job status."""
        return await self._client.get(
            f"/projects/{self._project_id}/jobs/{self._job_id}",
            cast_to=JobStatus,
        )

    async def wait(self, timeout: float = 120, poll_interval: float = 2) -> SheetResult:
        """Wait for completion and return resulting sheet info."""
        start = time.time()
        while time.time() - start < timeout:
            status = await self.status()
            if status.is_complete:
                if status.result is None:
                    return SheetResult()
                return status.result
            if status.is_failed:
                raise JobFailedError(
                    f"Job {self._job_id} failed: {status.error}",
                    job_id=self._job_id,
                    error=status.error or "Unknown error",
                )
            await asyncio.sleep(poll_interval)

        raise TimeoutError(f"Job {self._job_id} did not complete within {timeout}s")


class JobBatch:
    """Batch of jobs returned by a multi-page sheet ingest request (sync)."""

    def __init__(self, jobs: List[Job]):
        self.jobs = jobs

    @property
    def ids(self) -> List[str]:
        return [job.id for job in self.jobs]

    def status_all(self) -> List[JobStatus]:
        return [job.status() for job in self.jobs]

    def wait_all(
        self,
        timeout_per_job: float = 120,
        poll_interval: float = 2,
    ) -> List[SheetResult]:
        return [job.wait(timeout=timeout_per_job, poll_interval=poll_interval) for job in self.jobs]


class AsyncJobBatch:
    """Batch of jobs returned by a multi-page sheet ingest request (async)."""

    def __init__(self, jobs: List[AsyncJob]):
        self.jobs = jobs

    @property
    def ids(self) -> List[str]:
        return [job.id for job in self.jobs]

    async def status_all(self) -> List[JobStatus]:
        return [await job.status() for job in self.jobs]

    async def wait_all(
        self,
        timeout_per_job: float = 120,
        poll_interval: float = 2,
    ) -> List[SheetResult]:
        return [
            await job.wait(timeout=timeout_per_job, poll_interval=poll_interval)
            for job in self.jobs
        ]


# =============================================================================
# Helpers
# =============================================================================


def _normalize_page_selector(page: Union[int, str]) -> str:
    if isinstance(page, int):
        return str(page)
    text = str(page).strip()
    if not text:
        raise ValueError("page is required")
    return text


def _prepare_file(file: Uploadable) -> PreparedUpload:
    if isinstance(file, (str, Path)):
        path = Path(file)
        handle = open(path, "rb")
        return {"file": (path.name, handle, "application/pdf")}, handle
    if isinstance(file, bytes):
        return {"file": ("document.pdf", file, "application/pdf")}, None

    name = getattr(file, "name", "document.pdf")
    if hasattr(name, "split"):
        name = Path(name).name
    return {"file": (name, file, "application/pdf")}, None


def _jobs_from_response(
    client: "BaseClient",
    project_id: str,
    payload: SheetIngestResponse,
) -> List[Job]:
    jobs: List[Job] = []
    for item in payload.jobs:
        jobs.append(Job(client, project_id, item.job_id, page=item.page))
    return jobs


def _async_jobs_from_response(
    client: "AsyncBaseClient", project_id: str, payload: SheetIngestResponse
) -> List[AsyncJob]:
    jobs: List[AsyncJob] = []
    for item in payload.jobs:
        jobs.append(AsyncJob(client, project_id, item.job_id, page=item.page))
    return jobs


# =============================================================================
# Sheets
# =============================================================================


class Sheets:
    """Sheet ingestion and retrieval API (sync)."""

    def __init__(self, client: "BaseClient", project_id: str):
        self._client = client
        self._project_id = project_id

    def add(
        self,
        file: Optional[Uploadable] = None,
        *,
        page: Union[int, str] = 1,
        file_hash: Optional[str] = None,
        source_description: Optional[str] = None,
        on_sheet_exists: Optional[str] = None,
        community_update_mode: Optional[str] = None,
        semantic_index_update_mode: Optional[str] = None,
    ) -> Union[Job, JobBatch]:
        """Queue sheet ingestion jobs.

        Args:
            file: PDF upload (omit when using file_hash)
            page: page selector (e.g. `12`, `"1,3,5-7"`, `"all"`)
            file_hash: cached PDF hash
            source_description: optional source descriptor stored with the job
            on_sheet_exists: one of `error|skip|rebuild`
            community_update_mode: one of `incremental|rebuild`
            semantic_index_update_mode: one of `incremental|rebuild`

        Returns:
            `Job` for single-page selectors or `JobBatch` for multi-page selectors.
        """
        if file is None and not file_hash:
            raise ValueError("Provide file or file_hash")
        if file is not None and file_hash:
            raise ValueError("Provide either file or file_hash, not both")

        if file is not None and file_hash is None:
            computed_hash = _compute_file_hash(file)
            try:
                cache = self._client.get(f"/drawings/cache/{computed_hash}")
                if cache.get("cached"):
                    file = None
                    file_hash = computed_hash
            except Exception:
                pass

        selector = _normalize_page_selector(page)
        data: Dict[str, str] = {"page": selector}
        if file_hash:
            data["file_hash"] = file_hash
        if source_description is not None:
            data["source_description"] = source_description
        if on_sheet_exists:
            data["on_sheet_exists"] = on_sheet_exists
        if community_update_mode:
            data["community_update_mode"] = community_update_mode
        if semantic_index_update_mode:
            data["semantic_index_update_mode"] = semantic_index_update_mode

        upload = None
        handle = None
        try:
            if file is not None:
                upload, handle = _prepare_file(file)

            response = self._client.post(
                f"/projects/{self._project_id}/sheets",
                files=upload,
                data=data,
                cast_to=SheetIngestResponse,
            )
        finally:
            if handle is not None:
                handle.close()

        jobs = _jobs_from_response(self._client, self._project_id, response)
        if len(jobs) == 1:
            return jobs[0]
        return JobBatch(jobs)

    def list(self, limit: Optional[int] = None) -> List[SheetSummary]:
        """List sheets in the project."""
        params = {"limit": limit} if limit is not None else None
        response = self._client.get(f"/projects/{self._project_id}/sheets", params=params)
        return [SheetSummary.model_validate(item) for item in response.get("sheets", [])]

    def get(self, sheet_id: str) -> SheetDetail:
        """Fetch sheet details."""
        return self._client.get(
            f"/projects/{self._project_id}/sheets/{sheet_id}",
            cast_to=SheetDetail,
        )

    def get_annotations(self, sheet_id: str) -> SheetAnnotations:
        """Fetch raw annotations for one sheet."""
        return self._client.get(
            f"/projects/{self._project_id}/sheets/{sheet_id}/annotations",
            cast_to=SheetAnnotations,
        )

    def delete(self, sheet_id: str) -> SheetDeleteResult:
        """Delete a sheet and return cleanup stats."""
        return self._client.delete(
            f"/projects/{self._project_id}/sheets/{sheet_id}",
            cast_to=SheetDeleteResult,
        )


class AsyncSheets:
    """Sheet ingestion and retrieval API (async)."""

    def __init__(self, client: "AsyncBaseClient", project_id: str):
        self._client = client
        self._project_id = project_id

    async def add(
        self,
        file: Optional[Uploadable] = None,
        *,
        page: Union[int, str] = 1,
        file_hash: Optional[str] = None,
        source_description: Optional[str] = None,
        on_sheet_exists: Optional[str] = None,
        community_update_mode: Optional[str] = None,
        semantic_index_update_mode: Optional[str] = None,
    ) -> Union[AsyncJob, AsyncJobBatch]:
        """Queue sheet ingestion jobs."""
        if file is None and not file_hash:
            raise ValueError("Provide file or file_hash")
        if file is not None and file_hash:
            raise ValueError("Provide either file or file_hash, not both")

        if file is not None and file_hash is None:
            computed_hash = _compute_file_hash(file)
            try:
                cache = await self._client.get(f"/drawings/cache/{computed_hash}")
                if cache.get("cached"):
                    file = None
                    file_hash = computed_hash
            except Exception:
                pass

        selector = _normalize_page_selector(page)
        data: Dict[str, str] = {"page": selector}
        if file_hash:
            data["file_hash"] = file_hash
        if source_description is not None:
            data["source_description"] = source_description
        if on_sheet_exists:
            data["on_sheet_exists"] = on_sheet_exists
        if community_update_mode:
            data["community_update_mode"] = community_update_mode
        if semantic_index_update_mode:
            data["semantic_index_update_mode"] = semantic_index_update_mode

        upload = None
        handle = None
        try:
            if file is not None:
                upload, handle = _prepare_file(file)
            response = await self._client.post(
                f"/projects/{self._project_id}/sheets",
                files=upload,
                data=data,
                cast_to=SheetIngestResponse,
            )
        finally:
            if handle is not None:
                handle.close()

        jobs = _async_jobs_from_response(self._client, self._project_id, response)
        if len(jobs) == 1:
            return jobs[0]
        return AsyncJobBatch(jobs)

    async def list(self, limit: Optional[int] = None) -> List[SheetSummary]:
        """List sheets in the project."""
        params = {"limit": limit} if limit is not None else None
        response = await self._client.get(f"/projects/{self._project_id}/sheets", params=params)
        return [SheetSummary.model_validate(item) for item in response.get("sheets", [])]

    async def get(self, sheet_id: str) -> SheetDetail:
        """Fetch sheet details."""
        return await self._client.get(
            f"/projects/{self._project_id}/sheets/{sheet_id}",
            cast_to=SheetDetail,
        )

    async def get_annotations(self, sheet_id: str) -> SheetAnnotations:
        """Fetch raw annotations for one sheet."""
        return await self._client.get(
            f"/projects/{self._project_id}/sheets/{sheet_id}/annotations",
            cast_to=SheetAnnotations,
        )

    async def delete(self, sheet_id: str) -> SheetDeleteResult:
        """Delete a sheet and return cleanup stats."""
        return await self._client.delete(
            f"/projects/{self._project_id}/sheets/{sheet_id}",
            cast_to=SheetDeleteResult,
        )


# =============================================================================
# Entities
# =============================================================================


class Entities:
    """Entity retrieval API (sync)."""

    def __init__(self, client: "BaseClient", project_id: str):
        self._client = client
        self._project_id = project_id

    def list(
        self,
        *,
        sheet_id: Optional[str] = None,
        type: Optional[str] = None,
        family: Optional[str] = None,
        normalized_spec: Optional[str] = None,
        region_uuid: Optional[str] = None,
        region_label: Optional[str] = None,
        note_number: Optional[str] = None,
        limit: int = 200,
    ) -> List[EntityListItem]:
        """List entities with optional filters."""
        params: Dict[str, Union[str, int]] = {"limit": limit}
        if sheet_id:
            params["sheet_id"] = sheet_id
        if type:
            params["type"] = type
        if family:
            params["family"] = family
        if normalized_spec:
            params["normalized_spec"] = normalized_spec
        if region_uuid:
            params["region_uuid"] = region_uuid
        if region_label:
            params["region_label"] = region_label
        if note_number:
            params["note_number"] = note_number

        response = self._client.get(
            f"/projects/{self._project_id}/entities",
            params=params,
        )
        return [EntityListItem.model_validate(item) for item in response.get("entities", [])]

    def get(
        self,
        entity_id: str,
        *,
        include_invalid: bool = False,
        expand_target: bool = False,
    ) -> Entity:
        """Get one entity with full relation context."""
        params: Dict[str, Union[str, bool]] = {
            "include_invalid": include_invalid,
            "expand_target": expand_target,
        }
        return self._client.get(
            f"/projects/{self._project_id}/entities/{entity_id}",
            params=params,
            cast_to=Entity,
        )


class AsyncEntities:
    """Entity retrieval API (async)."""

    def __init__(self, client: "AsyncBaseClient", project_id: str):
        self._client = client
        self._project_id = project_id

    async def list(
        self,
        *,
        sheet_id: Optional[str] = None,
        type: Optional[str] = None,
        family: Optional[str] = None,
        normalized_spec: Optional[str] = None,
        region_uuid: Optional[str] = None,
        region_label: Optional[str] = None,
        note_number: Optional[str] = None,
        limit: int = 200,
    ) -> List[EntityListItem]:
        """List entities with optional filters."""
        params: Dict[str, Union[str, int]] = {"limit": limit}
        if sheet_id:
            params["sheet_id"] = sheet_id
        if type:
            params["type"] = type
        if family:
            params["family"] = family
        if normalized_spec:
            params["normalized_spec"] = normalized_spec
        if region_uuid:
            params["region_uuid"] = region_uuid
        if region_label:
            params["region_label"] = region_label
        if note_number:
            params["note_number"] = note_number

        response = await self._client.get(
            f"/projects/{self._project_id}/entities",
            params=params,
        )
        return [EntityListItem.model_validate(item) for item in response.get("entities", [])]

    async def get(
        self,
        entity_id: str,
        *,
        include_invalid: bool = False,
        expand_target: bool = False,
    ) -> Entity:
        """Get one entity with full relation context."""
        params: Dict[str, Union[str, bool]] = {
            "include_invalid": include_invalid,
            "expand_target": expand_target,
        }
        return await self._client.get(
            f"/projects/{self._project_id}/entities/{entity_id}",
            params=params,
            cast_to=Entity,
        )


# =============================================================================
# Relationships
# =============================================================================


class Relationships:
    """Relationship retrieval API (sync)."""

    def __init__(self, client: "BaseClient", project_id: str):
        self._client = client
        self._project_id = project_id

    def list(
        self,
        *,
        sheet_id: Optional[str] = None,
        source_id: Optional[str] = None,
        target_id: Optional[str] = None,
        type: Optional[str] = None,
        include_invalid: bool = False,
        invalid_only: bool = False,
        orphan_only: bool = False,
        limit: int = 200,
    ) -> List[Fact]:
        """List relationships with optional filters."""
        params: Dict[str, Union[str, int, bool]] = {
            "limit": limit,
            "include_invalid": include_invalid,
            "invalid_only": invalid_only,
            "orphan_only": orphan_only,
        }
        if sheet_id:
            params["sheet_id"] = sheet_id
        if source_id:
            params["source_id"] = source_id
        if target_id:
            params["target_id"] = target_id
        if type:
            params["type"] = type

        response = self._client.get(
            f"/projects/{self._project_id}/relationships",
            params=params,
        )
        return [Fact.model_validate(item) for item in response.get("relationships", [])]


class AsyncRelationships:
    """Relationship retrieval API (async)."""

    def __init__(self, client: "AsyncBaseClient", project_id: str):
        self._client = client
        self._project_id = project_id

    async def list(
        self,
        *,
        sheet_id: Optional[str] = None,
        source_id: Optional[str] = None,
        target_id: Optional[str] = None,
        type: Optional[str] = None,
        include_invalid: bool = False,
        invalid_only: bool = False,
        orphan_only: bool = False,
        limit: int = 200,
    ) -> List[Fact]:
        """List relationships with optional filters."""
        params: Dict[str, Union[str, int, bool]] = {
            "limit": limit,
            "include_invalid": include_invalid,
            "invalid_only": invalid_only,
            "orphan_only": orphan_only,
        }
        if sheet_id:
            params["sheet_id"] = sheet_id
        if source_id:
            params["source_id"] = source_id
        if target_id:
            params["target_id"] = target_id
        if type:
            params["type"] = type

        response = await self._client.get(
            f"/projects/{self._project_id}/relationships",
            params=params,
        )
        return [Fact.model_validate(item) for item in response.get("relationships", [])]


# =============================================================================
# Project instance
# =============================================================================


class ProjectInstance:
    """Project handle with nested resources (sync)."""

    def __init__(self, client: "BaseClient", project: Project):
        self._client = client
        self._project = project

    @property
    def id(self) -> str:
        return self._project.id

    @property
    def name(self) -> str:
        return self._project.name

    @property
    def description(self) -> Optional[str]:
        return self._project.description

    @property
    def data(self) -> Project:
        """Raw project model data."""
        return self._project

    @cached_property
    def sheets(self) -> Sheets:
        return Sheets(self._client, self.id)

    @cached_property
    def entities(self) -> Entities:
        return Entities(self._client, self.id)

    @cached_property
    def relationships(self) -> Relationships:
        return Relationships(self._client, self.id)

    def search(
        self,
        query: str,
        *,
        limit: int = 10,
        channels: Optional[List[str]] = None,
        include_graph_context: bool = True,
    ) -> SearchResponse:
        """Search entities, facts, and communities in the project."""
        body: Dict[str, Union[str, int, bool, List[str]]] = {
            "query": query,
            "limit": limit,
            "include_graph_context": include_graph_context,
        }
        if channels is not None:
            body["channels"] = channels

        return self._client.post(
            f"/projects/{self.id}/search",
            json=body,
            cast_to=SearchResponse,
        )

    def delete(self) -> ProjectDeleteResult:
        """Delete this project."""
        return self._client.delete(f"/projects/{self.id}", cast_to=ProjectDeleteResult)


class AsyncProjectInstance:
    """Project handle with nested resources (async)."""

    def __init__(self, client: "AsyncBaseClient", project: Project):
        self._client = client
        self._project = project

    @property
    def id(self) -> str:
        return self._project.id

    @property
    def name(self) -> str:
        return self._project.name

    @property
    def description(self) -> Optional[str]:
        return self._project.description

    @property
    def data(self) -> Project:
        """Raw project model data."""
        return self._project

    @cached_property
    def sheets(self) -> AsyncSheets:
        return AsyncSheets(self._client, self.id)

    @cached_property
    def entities(self) -> AsyncEntities:
        return AsyncEntities(self._client, self.id)

    @cached_property
    def relationships(self) -> AsyncRelationships:
        return AsyncRelationships(self._client, self.id)

    async def search(
        self,
        query: str,
        *,
        limit: int = 10,
        channels: Optional[List[str]] = None,
        include_graph_context: bool = True,
    ) -> SearchResponse:
        """Search entities, facts, and communities in the project."""
        body: Dict[str, Union[str, int, bool, List[str]]] = {
            "query": query,
            "limit": limit,
            "include_graph_context": include_graph_context,
        }
        if channels is not None:
            body["channels"] = channels

        return await self._client.post(
            f"/projects/{self.id}/search",
            json=body,
            cast_to=SearchResponse,
        )

    async def delete(self) -> ProjectDeleteResult:
        """Delete this project."""
        return await self._client.delete(f"/projects/{self.id}", cast_to=ProjectDeleteResult)


# =============================================================================
# Projects top-level
# =============================================================================


class Projects:
    """Top-level project API (sync)."""

    def __init__(self, client: "BaseClient"):
        self._client = client

    def create(self, name: str, description: Optional[str] = None) -> ProjectInstance:
        """Create a project."""
        project = self._client.post(
            "/projects",
            json={"name": name, "description": description},
            cast_to=Project,
        )
        return ProjectInstance(self._client, project)

    def list(self, limit: Optional[int] = None) -> List[Project]:
        """List projects available to the API key."""
        params = {"limit": limit} if limit is not None else None
        response = self._client.get("/projects", params=params)
        return [Project.model_validate(item) for item in response.get("projects", [])]

    def get(self, project_id: str) -> ProjectInstance:
        """Get one project."""
        project = self._client.get(f"/projects/{project_id}", cast_to=Project)
        return ProjectInstance(self._client, project)

    def delete(self, project_id: str) -> ProjectDeleteResult:
        """Delete one project."""
        return self._client.delete(f"/projects/{project_id}", cast_to=ProjectDeleteResult)


class AsyncProjects:
    """Top-level project API (async)."""

    def __init__(self, client: "AsyncBaseClient"):
        self._client = client

    async def create(self, name: str, description: Optional[str] = None) -> AsyncProjectInstance:
        """Create a project."""
        project = await self._client.post(
            "/projects",
            json={"name": name, "description": description},
            cast_to=Project,
        )
        return AsyncProjectInstance(self._client, project)

    async def list(self, limit: Optional[int] = None) -> List[Project]:
        """List projects available to the API key."""
        params = {"limit": limit} if limit is not None else None
        response = await self._client.get("/projects", params=params)
        return [Project.model_validate(item) for item in response.get("projects", [])]

    async def get(self, project_id: str) -> AsyncProjectInstance:
        """Get one project."""
        project = await self._client.get(f"/projects/{project_id}", cast_to=Project)
        return AsyncProjectInstance(self._client, project)

    async def delete(self, project_id: str) -> ProjectDeleteResult:
        """Delete one project."""
        return await self._client.delete(f"/projects/{project_id}", cast_to=ProjectDeleteResult)


__all__ = [
    "Projects",
    "AsyncProjects",
    "ProjectInstance",
    "AsyncProjectInstance",
    "Sheets",
    "AsyncSheets",
    "Entities",
    "AsyncEntities",
    "Relationships",
    "AsyncRelationships",
    "Job",
    "AsyncJob",
    "JobBatch",
    "AsyncJobBatch",
]
