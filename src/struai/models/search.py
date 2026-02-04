"""Search and Query models."""
from typing import List, Optional

from pydantic import BaseModel

from .common import BBox


class SearchFilters(BaseModel):
    """Filters for search."""

    sheet_id: Optional[str] = None
    entity_type: Optional[List[str]] = None


class EntitySummary(BaseModel):
    """Brief entity info in search results."""

    id: str
    type: str
    label: str
    description: Optional[str] = None
    sheet_id: str
    bbox: Optional[BBox] = None


class RelationshipSummary(BaseModel):
    """Brief relationship info."""

    type: str
    fact: str


class GraphContext(BaseModel):
    """Graph context for a search result."""

    connected_entities: List[EntitySummary]
    relationships: List[RelationshipSummary]


class SearchHit(BaseModel):
    """Single search result."""

    entity: EntitySummary
    score: float
    graph_context: Optional[GraphContext] = None


class SearchResponse(BaseModel):
    """Search response."""

    results: List[SearchHit]
    search_ms: int


class QuerySource(BaseModel):
    """Source citation for query answer."""

    entity_id: str
    sheet_id: str
    label: str
    bbox: Optional[BBox] = None


class QueryResponse(BaseModel):
    """Natural language query response."""

    answer: str
    sources: List[QuerySource]
    confidence: float
