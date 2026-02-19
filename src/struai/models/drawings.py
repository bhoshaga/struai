"""Tier 1: raw drawing detection models."""

from __future__ import annotations

from typing import List, Optional

from pydantic import Field

from .common import BBox, Circle, Dimensions, Line, Point, SDKBaseModel, TextSpan


class Leader(SDKBaseModel):
    """Leader annotation with arrow and text."""

    id: str
    bbox: Optional[BBox] = None
    arrow_tip: Optional[Point] = None
    text_bbox: Optional[BBox] = None
    texts_inside: List[TextSpan] = Field(default_factory=list)


class SectionTag(SDKBaseModel):
    """Section cut tag."""

    id: str
    bbox: Optional[BBox] = None
    circle: Optional[Circle] = None
    direction: Optional[str] = None
    texts_inside: List[TextSpan] = Field(default_factory=list)
    section_line: Optional[Line] = None


class DetailTag(SDKBaseModel):
    """Detail callout tag."""

    id: str
    bbox: Optional[BBox] = None
    circle: Optional[Circle] = None
    texts_inside: List[TextSpan] = Field(default_factory=list)
    has_dashed_bbox: bool = False


class RevisionTriangle(SDKBaseModel):
    """Revision marker triangle."""

    id: str
    bbox: Optional[BBox] = None
    vertices: List[Point] = Field(default_factory=list)
    text: Optional[str] = None


class RevisionCloud(SDKBaseModel):
    """Revision cloud boundary."""

    id: str
    bbox: Optional[BBox] = None


class Annotations(SDKBaseModel):
    """All detected annotations."""

    leaders: List[Leader] = Field(default_factory=list)
    section_tags: List[SectionTag] = Field(default_factory=list)
    detail_tags: List[DetailTag] = Field(default_factory=list)
    revision_triangles: List[RevisionTriangle] = Field(default_factory=list)
    revision_clouds: List[RevisionCloud] = Field(default_factory=list)


class TitleBlock(SDKBaseModel):
    """Title block bounds and viewport."""

    bounds: Optional[BBox] = None
    viewport: Optional[BBox] = None


class DrawingResult(SDKBaseModel):
    """Result returned by POST /v1/drawings."""

    id: str
    page: int
    dimensions: Dimensions
    processing_ms: int
    annotations: Annotations
    titleblock: Optional[TitleBlock] = None


class DrawingCacheStatus(SDKBaseModel):
    """Result returned by GET /v1/drawings/cache/{file_hash}."""

    cached: bool
    file_hash: str
