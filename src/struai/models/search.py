"""Project search models."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import Field

from .common import BBox, SDKBaseModel


class ConnectedEntity(SDKBaseModel):
    """Connected entity included in graph context."""

    id: str
    type: str
    label: Optional[str] = None
    description: Optional[str] = None
    sheet_id: Optional[str] = None
    bbox: Optional[BBox] = None


class RelationshipSummary(SDKBaseModel):
    """Relationship included in graph context."""

    type: Optional[str] = None
    fact: Optional[str] = None


class GraphContext(SDKBaseModel):
    """Graph context attached to an entity search hit."""

    connected_entities: List[ConnectedEntity] = Field(default_factory=list)
    relationships: List[RelationshipSummary] = Field(default_factory=list)


class EntitySearchHit(SDKBaseModel):
    """Entity hit from /projects/{id}/search."""

    id: str
    type: str
    label: Optional[str] = None
    description: Optional[str] = None
    sheet_id: Optional[str] = None
    bbox: Optional[BBox] = None
    score: float
    attributes: Optional[Dict[str, Any]] = None
    graph_context: Optional[GraphContext] = None


class FactSearchHit(SDKBaseModel):
    """Fact hit from /projects/{id}/search."""

    id: str
    predicate: Optional[str] = None
    source: Optional[str] = None
    target: Optional[str] = None
    fact_text: Optional[str] = None
    sheet_id: Optional[str] = None
    score: float


class CommunitySearchHit(SDKBaseModel):
    """Community hit from /projects/{id}/search."""

    id: str
    name: Optional[str] = None
    summary: Optional[str] = None
    member_count: Optional[int] = None
    score: float


class SearchResponse(SDKBaseModel):
    """Response payload from POST /projects/{id}/search."""

    entities: List[EntitySearchHit] = Field(default_factory=list)
    facts: List[FactSearchHit] = Field(default_factory=list)
    communities: List[CommunitySearchHit] = Field(default_factory=list)
    search_ms: int
