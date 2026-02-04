"""StruAI models."""
from .common import BBox, Dimensions, Point, TextSpan
from .drawings import (
    Annotations,
    DetailTag,
    DrawingResult,
    Leader,
    RevisionCloud,
    RevisionTriangle,
    SectionTag,
    TitleBlock,
)
from .entities import Entity, EntityListItem, EntityLocation, EntityRelation, Fact
from .projects import JobStatus, JobStep, Project, Sheet, SheetResult
from .search import (
    EntitySummary,
    GraphContext,
    QueryResponse,
    QuerySource,
    RelationshipSummary,
    SearchFilters,
    SearchHit,
    SearchResponse,
)

__all__ = [
    # Common
    "Point",
    "BBox",
    "TextSpan",
    "Dimensions",
    # Drawings (Tier 1)
    "DrawingResult",
    "Annotations",
    "Leader",
    "SectionTag",
    "DetailTag",
    "RevisionTriangle",
    "RevisionCloud",
    "TitleBlock",
    # Projects (Tier 2)
    "Project",
    "Sheet",
    "JobStatus",
    "JobStep",
    "SheetResult",
    # Search
    "SearchFilters",
    "SearchHit",
    "SearchResponse",
    "EntitySummary",
    "GraphContext",
    "RelationshipSummary",
    "QueryResponse",
    "QuerySource",
    # Entities
    "Entity",
    "EntityListItem",
    "EntityLocation",
    "EntityRelation",
    "Fact",
]
