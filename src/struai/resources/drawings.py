"""Tier 1 drawings resource."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import TYPE_CHECKING, BinaryIO, Optional, Tuple, Union

from .._exceptions import NotFoundError
from ..models.drawings import DrawingCacheStatus, DrawingDeleteResult, DrawingResult

if TYPE_CHECKING:
    from .._base import AsyncBaseClient, BaseClient

Uploadable = Union[str, Path, bytes, BinaryIO]
PreparedUpload = Tuple[dict, Optional[BinaryIO]]


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


class Drawings:
    """Tier 1 raw detection API (sync)."""

    def __init__(self, client: "BaseClient"):
        self._client = client

    def analyze(
        self,
        file: Optional[Uploadable] = None,
        page: int = 1,
        file_hash: Optional[str] = None,
    ) -> DrawingResult:
        """Analyze one page via POST /v1/drawings."""
        if file is None and not file_hash:
            raise ValueError("Provide file or file_hash")
        if file is not None and file_hash:
            raise ValueError("Provide either file or file_hash, not both")

        if file is not None and file_hash is None:
            file_hash = self.compute_file_hash(file)
            if self._check_cache(file_hash):
                file = None

        upload = None
        handle = None
        try:
            if file is not None:
                upload, handle = _prepare_file(file)
            data = {"page": str(page)}
            if file_hash:
                data["file_hash"] = file_hash

            return self._client.post(
                "/drawings",
                files=upload,
                data=data,
                cast_to=DrawingResult,
            )
        finally:
            if handle is not None:
                handle.close()

    def check_cache(self, file_hash: str) -> DrawingCacheStatus:
        """Check PDF cache status for a file hash."""
        return self._client.get(f"/drawings/cache/{file_hash}", cast_to=DrawingCacheStatus)

    def get(self, drawing_id: str) -> DrawingResult:
        """Get drawing by ID."""
        return self._client.get(f"/drawings/{drawing_id}", cast_to=DrawingResult)

    def delete(self, drawing_id: str) -> DrawingDeleteResult:
        """Delete drawing by ID."""
        return self._client.delete(f"/drawings/{drawing_id}", cast_to=DrawingDeleteResult)

    def compute_file_hash(self, file: Uploadable) -> str:
        """Compute server-compatible file hash (sha256 first 16 chars)."""
        return _compute_file_hash(file)

    def _check_cache(self, file_hash: str) -> bool:
        try:
            status = self.check_cache(file_hash)
            return bool(status.cached)
        except NotFoundError:
            return False


class AsyncDrawings:
    """Tier 1 raw detection API (async)."""

    def __init__(self, client: "AsyncBaseClient"):
        self._client = client

    async def analyze(
        self,
        file: Optional[Uploadable] = None,
        page: int = 1,
        file_hash: Optional[str] = None,
    ) -> DrawingResult:
        """Analyze one page via POST /v1/drawings."""
        if file is None and not file_hash:
            raise ValueError("Provide file or file_hash")
        if file is not None and file_hash:
            raise ValueError("Provide either file or file_hash, not both")

        if file is not None and file_hash is None:
            file_hash = self.compute_file_hash(file)
            if await self._check_cache(file_hash):
                file = None

        upload = None
        handle = None
        try:
            if file is not None:
                upload, handle = _prepare_file(file)
            data = {"page": str(page)}
            if file_hash:
                data["file_hash"] = file_hash

            return await self._client.post(
                "/drawings",
                files=upload,
                data=data,
                cast_to=DrawingResult,
            )
        finally:
            if handle is not None:
                handle.close()

    async def check_cache(self, file_hash: str) -> DrawingCacheStatus:
        """Check PDF cache status for a file hash."""
        return await self._client.get(f"/drawings/cache/{file_hash}", cast_to=DrawingCacheStatus)

    async def get(self, drawing_id: str) -> DrawingResult:
        """Get drawing by ID."""
        return await self._client.get(f"/drawings/{drawing_id}", cast_to=DrawingResult)

    async def delete(self, drawing_id: str) -> DrawingDeleteResult:
        """Delete drawing by ID."""
        return await self._client.delete(f"/drawings/{drawing_id}", cast_to=DrawingDeleteResult)

    def compute_file_hash(self, file: Uploadable) -> str:
        """Compute server-compatible file hash (sha256 first 16 chars)."""
        return _compute_file_hash(file)

    async def _check_cache(self, file_hash: str) -> bool:
        try:
            status = await self.check_cache(file_hash)
            return bool(status.cached)
        except NotFoundError:
            return False


def _compute_file_hash(file: Uploadable) -> str:
    hasher = hashlib.sha256()

    if isinstance(file, (str, Path)):
        with open(file, "rb") as handle:
            for chunk in iter(lambda: handle.read(8192), b""):
                hasher.update(chunk)
        return hasher.hexdigest()[:16]

    if isinstance(file, bytes):
        hasher.update(file)
        return hasher.hexdigest()[:16]

    pos = None
    if hasattr(file, "tell"):
        try:
            pos = file.tell()
        except Exception:
            pos = None

    for chunk in iter(lambda: file.read(8192), b""):
        hasher.update(chunk)

    if pos is not None and hasattr(file, "seek"):
        try:
            file.seek(pos)
        except Exception:
            pass

    return hasher.hexdigest()[:16]
