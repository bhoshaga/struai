"""Tier 1: Raw Detection models."""
from typing import List, Optional

from pydantic import BaseModel

from .common import BBox, Circle, Dimensions, Line, Point, TextSpan


class Leader(BaseModel):
    """Leader annotation with arrow and text."""

    id: str
    bbox: BBox
    arrow_tip: Point
    text_bbox: BBox
    texts_inside: List[TextSpan]


class SectionTag(BaseModel):
    """Section cut tag."""

    id: str
    bbox: BBox
    circle: Circle
    direction: str  # "left", "right", "up", "down"
    texts_inside: List[TextSpan]
    section_line: Optional[Line] = None


class DetailTag(BaseModel):
    """Detail callout tag."""

    id: str
    bbox: BBox
    circle: Circle
    texts_inside: List[TextSpan]
    has_dashed_bbox: bool = False


class RevisionTriangle(BaseModel):
    """Revision marker triangle."""

    id: str
    bbox: BBox
    vertices: List[Point]
    text: str


class RevisionCloud(BaseModel):
    """Revision cloud boundary."""

    id: str
    bbox: BBox


class Annotations(BaseModel):
    """All detected annotations."""

    leaders: List[Leader] = []
    section_tags: List[SectionTag] = []
    detail_tags: List[DetailTag] = []
    revision_triangles: List[RevisionTriangle] = []
    revision_clouds: List[RevisionCloud] = []


class TitleBlock(BaseModel):
    """Title block detection."""

    bounds: BBox
    viewport: BBox  # Drawing area excluding title block


class DrawingResult(BaseModel):
    """Result from Tier 1 raw detection."""

    id: str
    page: int
    dimensions: Dimensions
    processing_ms: int
    annotations: Annotations
    titleblock: Optional[TitleBlock] = None
