"""Tier 2: Projects, Sheets, Search API."""
import asyncio
import time
from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING, BinaryIO, Dict, List, Optional, Union

from .._exceptions import JobFailedError, TimeoutError
from ..models.entities import Entity, EntityListItem, Fact
from ..models.projects import JobStatus, Project, Sheet, SheetResult
from ..models.search import QueryResponse, SearchResponse

if TYPE_CHECKING:
    from .._base import AsyncBaseClient, BaseClient


# =============================================================================
# Job handles for async sheet ingestion
# =============================================================================


class Job:
    """Handle for an async sheet ingestion job (sync)."""

    def __init__(self, client: "BaseClient", project_id: str, job_id: str):
        self._client = client
        self._project_id = project_id
        self._job_id = job_id

    @property
    def id(self) -> str:
        return self._job_id

    def status(self) -> JobStatus:
        """Check current job status."""
        return self._client.get(
            f"/projects/{self._project_id}/jobs/{self._job_id}",
            cast_to=JobStatus,
        )

    def wait(
        self,
        timeout: float = 120,
        poll_interval: float = 2,
    ) -> SheetResult:
        """Wait for job completion.

        Args:
            timeout: Maximum seconds to wait
            poll_interval: Seconds between status checks

        Returns:
            SheetResult on success

        Raises:
            TimeoutError: If job doesn't complete in time
            JobFailedError: If job fails
        """
        start = time.time()
        while time.time() - start < timeout:
            status = self.status()

            if status.is_complete:
                return status.result  # type: ignore

            if status.is_failed:
                raise JobFailedError(
                    f"Job {self._job_id} failed: {status.error}",
                    job_id=self._job_id,
                    error=status.error or "Unknown error",
                )

            time.sleep(poll_interval)

        raise TimeoutError(f"Job {self._job_id} did not complete within {timeout}s")


class AsyncJob:
    """Handle for an async sheet ingestion job (async)."""

    def __init__(self, client: "AsyncBaseClient", project_id: str, job_id: str):
        self._client = client
        self._project_id = project_id
        self._job_id = job_id

    @property
    def id(self) -> str:
        return self._job_id

    async def status(self) -> JobStatus:
        """Check current job status."""
        return await self._client.get(
            f"/projects/{self._project_id}/jobs/{self._job_id}",
            cast_to=JobStatus,
        )

    async def wait(
        self,
        timeout: float = 120,
        poll_interval: float = 2,
    ) -> SheetResult:
        """Wait for job completion (async)."""
        start = time.time()
        while time.time() - start < timeout:
            status = await self.status()

            if status.is_complete:
                return status.result  # type: ignore

            if status.is_failed:
                raise JobFailedError(
                    f"Job {self._job_id} failed: {status.error}",
                    job_id=self._job_id,
                    error=status.error or "Unknown error",
                )

            await asyncio.sleep(poll_interval)

        raise TimeoutError(f"Job {self._job_id} did not complete within {timeout}s")


# =============================================================================
# Sheets resource
# =============================================================================


class Sheets:
    """Sheet ingestion API (sync)."""

    def __init__(self, client: "BaseClient", project_id: str):
        self._client = client
        self._project_id = project_id

    def add(
        self,
        file: Union[str, Path, bytes, BinaryIO],
        page: int,
        webhook_url: Optional[str] = None,
    ) -> Job:
        """Add a sheet to the project (async job).

        Args:
            file: PDF file
            page: Page number (1-indexed)
            webhook_url: Optional callback URL when complete

        Returns:
            Job handle for polling/waiting
        """
        files = self._prepare_file(file)
        data: Dict[str, str] = {"page": str(page)}
        if webhook_url:
            data["webhook_url"] = webhook_url

        response = self._client.post(
            f"/projects/{self._project_id}/sheets",
            files=files,
            data=data,
        )
        return Job(self._client, self._project_id, response["job_id"])

    def list(self, limit: int = 100) -> List[Sheet]:
        """List all sheets in project."""
        response = self._client.get(
            f"/projects/{self._project_id}/sheets",
            params={"limit": limit},
        )
        return [Sheet.model_validate(s) for s in response["sheets"]]

    def get(self, sheet_id: str) -> Sheet:
        """Get a sheet by ID."""
        return self._client.get(
            f"/projects/{self._project_id}/sheets/{sheet_id}",
            cast_to=Sheet,
        )

    def delete(self, sheet_id: str) -> None:
        """Remove a sheet from the project."""
        self._client.delete(f"/projects/{self._project_id}/sheets/{sheet_id}")

    def _prepare_file(self, file: Union[str, Path, bytes, BinaryIO]) -> dict:
        if isinstance(file, (str, Path)):
            path = Path(file)
            return {"file": (path.name, open(path, "rb"), "application/pdf")}
        elif isinstance(file, bytes):
            return {"file": ("document.pdf", file, "application/pdf")}
        else:
            name = getattr(file, "name", "document.pdf")
            if hasattr(name, "split"):
                name = Path(name).name
            return {"file": (name, file, "application/pdf")}


class AsyncSheets:
    """Sheet ingestion API (async)."""

    def __init__(self, client: "AsyncBaseClient", project_id: str):
        self._client = client
        self._project_id = project_id

    async def add(
        self,
        file: Union[str, Path, bytes, BinaryIO],
        page: int,
        webhook_url: Optional[str] = None,
    ) -> AsyncJob:
        """Add a sheet to the project (async job)."""
        files = self._prepare_file(file)
        data: Dict[str, str] = {"page": str(page)}
        if webhook_url:
            data["webhook_url"] = webhook_url

        response = await self._client.post(
            f"/projects/{self._project_id}/sheets",
            files=files,
            data=data,
        )
        return AsyncJob(self._client, self._project_id, response["job_id"])

    async def list(self, limit: int = 100) -> List[Sheet]:
        """List all sheets in project."""
        response = await self._client.get(
            f"/projects/{self._project_id}/sheets",
            params={"limit": limit},
        )
        return [Sheet.model_validate(s) for s in response["sheets"]]

    async def get(self, sheet_id: str) -> Sheet:
        """Get a sheet by ID."""
        return await self._client.get(
            f"/projects/{self._project_id}/sheets/{sheet_id}",
            cast_to=Sheet,
        )

    async def delete(self, sheet_id: str) -> None:
        """Remove a sheet from the project."""
        await self._client.delete(f"/projects/{self._project_id}/sheets/{sheet_id}")

    def _prepare_file(self, file: Union[str, Path, bytes, BinaryIO]) -> dict:
        if isinstance(file, (str, Path)):
            path = Path(file)
            return {"file": (path.name, open(path, "rb"), "application/pdf")}
        elif isinstance(file, bytes):
            return {"file": ("document.pdf", file, "application/pdf")}
        else:
            name = getattr(file, "name", "document.pdf")
            if hasattr(name, "split"):
                name = Path(name).name
            return {"file": (name, file, "application/pdf")}


# =============================================================================
# Entities resource
# =============================================================================


class Entities:
    """Entity retrieval API (sync)."""

    def __init__(self, client: "BaseClient", project_id: str):
        self._client = client
        self._project_id = project_id

    def list(
        self,
        sheet_id: Optional[str] = None,
        type: Optional[str] = None,
        limit: int = 100,
    ) -> List[EntityListItem]:
        """List entities in project."""
        params: Dict[str, Union[str, int]] = {"limit": limit}
        if sheet_id:
            params["sheet_id"] = sheet_id
        if type:
            params["type"] = type

        response = self._client.get(
            f"/projects/{self._project_id}/entities",
            params=params,
        )
        return [EntityListItem.model_validate(e) for e in response["entities"]]

    def get(self, entity_id: str) -> Entity:
        """Get entity with all relationships."""
        return self._client.get(
            f"/projects/{self._project_id}/entities/{entity_id}",
            cast_to=Entity,
        )


class AsyncEntities:
    """Entity retrieval API (async)."""

    def __init__(self, client: "AsyncBaseClient", project_id: str):
        self._client = client
        self._project_id = project_id

    async def list(
        self,
        sheet_id: Optional[str] = None,
        type: Optional[str] = None,
        limit: int = 100,
    ) -> List[EntityListItem]:
        """List entities in project."""
        params: Dict[str, Union[str, int]] = {"limit": limit}
        if sheet_id:
            params["sheet_id"] = sheet_id
        if type:
            params["type"] = type

        response = await self._client.get(
            f"/projects/{self._project_id}/entities",
            params=params,
        )
        return [EntityListItem.model_validate(e) for e in response["entities"]]

    async def get(self, entity_id: str) -> Entity:
        """Get entity with all relationships."""
        return await self._client.get(
            f"/projects/{self._project_id}/entities/{entity_id}",
            cast_to=Entity,
        )


# =============================================================================
# Relationships resource
# =============================================================================


class Relationships:
    """Relationship retrieval API (sync)."""

    def __init__(self, client: "BaseClient", project_id: str):
        self._client = client
        self._project_id = project_id

    def list(
        self,
        source_id: Optional[str] = None,
        target_id: Optional[str] = None,
        type: Optional[str] = None,
        limit: int = 100,
    ) -> List[Fact]:
        """List relationships in project."""
        params: Dict[str, Union[str, int]] = {"limit": limit}
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
        return [Fact.model_validate(r) for r in response["relationships"]]


class AsyncRelationships:
    """Relationship retrieval API (async)."""

    def __init__(self, client: "AsyncBaseClient", project_id: str):
        self._client = client
        self._project_id = project_id

    async def list(
        self,
        source_id: Optional[str] = None,
        target_id: Optional[str] = None,
        type: Optional[str] = None,
        limit: int = 100,
    ) -> List[Fact]:
        """List relationships in project."""
        params: Dict[str, Union[str, int]] = {"limit": limit}
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
        return [Fact.model_validate(r) for r in response["relationships"]]


# =============================================================================
# ProjectInstance - bound to a specific project
# =============================================================================


class ProjectInstance:
    """A project with access to nested resources (sync)."""

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

    @cached_property
    def sheets(self) -> Sheets:
        """Sheet ingestion API."""
        return Sheets(self._client, self.id)

    @cached_property
    def entities(self) -> Entities:
        """Entity retrieval API."""
        return Entities(self._client, self.id)

    @cached_property
    def relationships(self) -> Relationships:
        """Relationship retrieval API."""
        return Relationships(self._client, self.id)

    def search(
        self,
        query: str,
        limit: int = 10,
        filters: Optional[Dict] = None,
        include_graph_context: bool = True,
    ) -> SearchResponse:
        """Semantic search across project.

        Args:
            query: Search query text
            limit: Max results to return
            filters: Optional filters (sheet_id, entity_type)
            include_graph_context: Include related entities

        Returns:
            SearchResponse with results
        """
        body: Dict = {
            "query": query,
            "limit": limit,
            "include_graph_context": include_graph_context,
        }
        if filters:
            body["filters"] = filters

        return self._client.post(
            f"/projects/{self.id}/search",
            json=body,
            cast_to=SearchResponse,
        )

    def query(self, question: str) -> QueryResponse:
        """Ask a natural language question.

        Args:
            question: Question in natural language

        Returns:
            QueryResponse with answer and sources
        """
        return self._client.post(
            f"/projects/{self.id}/query",
            json={"question": question},
            cast_to=QueryResponse,
        )

    def delete(self) -> None:
        """Delete this project and all its data."""
        self._client.delete(f"/projects/{self.id}")


class AsyncProjectInstance:
    """A project with access to nested resources (async)."""

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

    @cached_property
    def sheets(self) -> AsyncSheets:
        """Sheet ingestion API."""
        return AsyncSheets(self._client, self.id)

    @cached_property
    def entities(self) -> AsyncEntities:
        """Entity retrieval API."""
        return AsyncEntities(self._client, self.id)

    @cached_property
    def relationships(self) -> AsyncRelationships:
        """Relationship retrieval API."""
        return AsyncRelationships(self._client, self.id)

    async def search(
        self,
        query: str,
        limit: int = 10,
        filters: Optional[Dict] = None,
        include_graph_context: bool = True,
    ) -> SearchResponse:
        """Semantic search across project (async)."""
        body: Dict = {
            "query": query,
            "limit": limit,
            "include_graph_context": include_graph_context,
        }
        if filters:
            body["filters"] = filters

        return await self._client.post(
            f"/projects/{self.id}/search",
            json=body,
            cast_to=SearchResponse,
        )

    async def query(self, question: str) -> QueryResponse:
        """Ask a natural language question (async)."""
        return await self._client.post(
            f"/projects/{self.id}/query",
            json={"question": question},
            cast_to=QueryResponse,
        )

    async def delete(self) -> None:
        """Delete this project and all its data."""
        await self._client.delete(f"/projects/{self.id}")


# =============================================================================
# Projects resource (top-level)
# =============================================================================


class Projects:
    """Tier 2: Project management API (sync)."""

    def __init__(self, client: "BaseClient"):
        self._client = client

    def create(
        self,
        name: str,
        description: Optional[str] = None,
    ) -> ProjectInstance:
        """Create a new project.

        Args:
            name: Project name
            description: Optional description

        Returns:
            ProjectInstance with access to sheets, search, etc.
        """
        data = self._client.post(
            "/projects",
            json={"name": name, "description": description},
            cast_to=Project,
        )
        return ProjectInstance(self._client, data)

    def list(self, limit: int = 100) -> List[Project]:
        """List all projects."""
        response = self._client.get("/projects", params={"limit": limit})
        return [Project.model_validate(p) for p in response["projects"]]

    def get(self, project_id: str) -> ProjectInstance:
        """Get a project by ID."""
        data = self._client.get(f"/projects/{project_id}", cast_to=Project)
        return ProjectInstance(self._client, data)

    def delete(self, project_id: str) -> None:
        """Delete a project and all its data."""
        self._client.delete(f"/projects/{project_id}")


class AsyncProjects:
    """Tier 2: Project management API (async)."""

    def __init__(self, client: "AsyncBaseClient"):
        self._client = client

    async def create(
        self,
        name: str,
        description: Optional[str] = None,
    ) -> AsyncProjectInstance:
        """Create a new project (async)."""
        data = await self._client.post(
            "/projects",
            json={"name": name, "description": description},
            cast_to=Project,
        )
        return AsyncProjectInstance(self._client, data)

    async def list(self, limit: int = 100) -> List[Project]:
        """List all projects (async)."""
        response = await self._client.get("/projects", params={"limit": limit})
        return [Project.model_validate(p) for p in response["projects"]]

    async def get(self, project_id: str) -> AsyncProjectInstance:
        """Get a project by ID (async)."""
        data = await self._client.get(f"/projects/{project_id}", cast_to=Project)
        return AsyncProjectInstance(self._client, data)

    async def delete(self, project_id: str) -> None:
        """Delete a project and all its data (async)."""
        await self._client.delete(f"/projects/{project_id}")
