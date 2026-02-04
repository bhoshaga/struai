"""Tier 1: Raw Detection API."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import TYPE_CHECKING, BinaryIO, Optional, Union

from .._exceptions import NotFoundError
from ..models.drawings import DrawingResult

if TYPE_CHECKING:
    from .._base import AsyncBaseClient, BaseClient


class Drawings:
    """Tier 1: Raw detection API (sync)."""

    def __init__(self, client: "BaseClient"):
        self._client = client

    def analyze(
        self,
        file: Optional[Union[str, Path, bytes, BinaryIO]] = None,
        page: int = 1,
        file_hash: Optional[str] = None,
    ) -> DrawingResult:
        """Analyze a PDF page for annotations.

        Args:
            file: PDF file path, bytes, or file-like object (omit if using file_hash)
            page: Page number (1-indexed)
            file_hash: Hash of previously cached PDF (optional, skips upload)

        Returns:
            DrawingResult with detected annotations

        Example:
            >>> result = client.drawings.analyze("structural.pdf", page=4)
            >>> for leader in result.annotations.leaders:
            ...     print(leader.texts_inside[0].text)
        """
        if file is None and not file_hash:
            raise ValueError("Provide file or file_hash")
        if file is not None and file_hash:
            raise ValueError("Provide either file or file_hash, not both")

        if file is not None and file_hash is None:
            file_hash = self.compute_file_hash(file)
            if self._check_cache(file_hash):
                file = None

        files = self._prepare_file(file) if file is not None else None
        data = {"page": str(page)}
        if file_hash:
            data["file_hash"] = file_hash
        return self._client.post(
            "/drawings",
            files=files,
            data=data,
            cast_to=DrawingResult,
        )

    def get(self, drawing_id: str) -> DrawingResult:
        """Retrieve a previously processed drawing.

        Args:
            drawing_id: Drawing ID (e.g., "drw_7f8a9b2c")
        """
        return self._client.get(f"/drawings/{drawing_id}", cast_to=DrawingResult)

    def delete(self, drawing_id: str) -> None:
        """Delete a drawing result.

        Args:
            drawing_id: Drawing ID to delete
        """
        self._client.delete(f"/drawings/{drawing_id}")

    def _prepare_file(self, file: Union[str, Path, bytes, BinaryIO]) -> dict:
        """Prepare file for upload."""
        if isinstance(file, (str, Path)):
            path = Path(file)
            return {"file": (path.name, open(path, "rb"), "application/pdf")}
        elif isinstance(file, bytes):
            return {"file": ("document.pdf", file, "application/pdf")}
        else:
            # File-like object
            name = getattr(file, "name", "document.pdf")
            if hasattr(name, "split"):
                name = Path(name).name
            return {"file": (name, file, "application/pdf")}

    def compute_file_hash(self, file: Union[str, Path, bytes, BinaryIO]) -> str:
        """Compute SHA256 hash (first 16 chars) matching server cache key."""
        return _compute_file_hash(file)

    def _check_cache(self, file_hash: str) -> bool:
        try:
            resp = self._client.get(f"/drawings/cache/{file_hash}")
            return bool(resp.get("cached"))
        except NotFoundError:
            return False


class AsyncDrawings:
    """Tier 1: Raw detection API (async)."""

    def __init__(self, client: "AsyncBaseClient"):
        self._client = client

    async def analyze(
        self,
        file: Optional[Union[str, Path, bytes, BinaryIO]] = None,
        page: int = 1,
        file_hash: Optional[str] = None,
    ) -> DrawingResult:
        """Analyze a PDF page for annotations (async).

        Args:
            file: PDF file path, bytes, or file-like object (omit if using file_hash)
            page: Page number (1-indexed)
            file_hash: Hash of previously cached PDF (optional, skips upload)

        Returns:
            DrawingResult with detected annotations
        """
        if file is None and not file_hash:
            raise ValueError("Provide file or file_hash")
        if file is not None and file_hash:
            raise ValueError("Provide either file or file_hash, not both")

        if file is not None and file_hash is None:
            file_hash = self.compute_file_hash(file)
            if await self._check_cache_async(file_hash):
                file = None

        files = self._prepare_file(file) if file is not None else None
        data = {"page": str(page)}
        if file_hash:
            data["file_hash"] = file_hash
        return await self._client.post(
            "/drawings",
            files=files,
            data=data,
            cast_to=DrawingResult,
        )

    async def get(self, drawing_id: str) -> DrawingResult:
        """Retrieve a previously processed drawing (async)."""
        return await self._client.get(f"/drawings/{drawing_id}", cast_to=DrawingResult)

    async def delete(self, drawing_id: str) -> None:
        """Delete a drawing result (async)."""
        await self._client.delete(f"/drawings/{drawing_id}")

    def _prepare_file(self, file: Union[str, Path, bytes, BinaryIO]) -> dict:
        """Prepare file for upload."""
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

    def compute_file_hash(self, file: Union[str, Path, bytes, BinaryIO]) -> str:
        """Compute SHA256 hash (first 16 chars) matching server cache key."""
        return _compute_file_hash(file)

    async def _check_cache_async(self, file_hash: str) -> bool:
        try:
            resp = await self._client.get(f"/drawings/cache/{file_hash}")
            return bool(resp.get("cached"))
        except NotFoundError:
            return False


def _compute_file_hash(file: Union[str, Path, bytes, BinaryIO]) -> str:
    hasher = hashlib.sha256()
    if isinstance(file, (str, Path)):
        with open(file, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hasher.update(chunk)
        return hasher.hexdigest()[:16]
    if isinstance(file, bytes):
        hasher.update(file)
        return hasher.hexdigest()[:16]

    # File-like object
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
