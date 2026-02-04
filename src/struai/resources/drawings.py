"""Tier 1: Raw Detection API."""
from pathlib import Path
from typing import TYPE_CHECKING, BinaryIO, Union

from ..models.drawings import DrawingResult

if TYPE_CHECKING:
    from .._base import AsyncBaseClient, BaseClient


class Drawings:
    """Tier 1: Raw detection API (sync)."""

    def __init__(self, client: "BaseClient"):
        self._client = client

    def analyze(
        self,
        file: Union[str, Path, bytes, BinaryIO],
        page: int,
    ) -> DrawingResult:
        """Analyze a PDF page for annotations.

        Args:
            file: PDF file path, bytes, or file-like object
            page: Page number (1-indexed)

        Returns:
            DrawingResult with detected annotations

        Example:
            >>> result = client.drawings.analyze("structural.pdf", page=4)
            >>> for leader in result.annotations.leaders:
            ...     print(leader.texts_inside[0].text)
        """
        files = self._prepare_file(file)
        return self._client.post(
            "/drawings",
            files=files,
            data={"page": str(page)},
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


class AsyncDrawings:
    """Tier 1: Raw detection API (async)."""

    def __init__(self, client: "AsyncBaseClient"):
        self._client = client

    async def analyze(
        self,
        file: Union[str, Path, bytes, BinaryIO],
        page: int,
    ) -> DrawingResult:
        """Analyze a PDF page for annotations (async).

        Args:
            file: PDF file path, bytes, or file-like object
            page: Page number (1-indexed)

        Returns:
            DrawingResult with detected annotations
        """
        files = self._prepare_file(file)
        return await self._client.post(
            "/drawings",
            files=files,
            data={"page": str(page)},
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
