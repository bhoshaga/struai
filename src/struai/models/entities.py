"""Entity and relationship models."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

from pydantic import Field

from .common import BBox, SDKBaseModel


class EntityLocation(SDKBaseModel):
    """Sheet location for an entity."""

    sheet_id: str
    page: Optional[int] = None


class EntityRelation(SDKBaseModel):
    """Relationship row returned in entity detail payload."""

    id: str
    type: str
    fact: Optional[str] = None
    source_id: Optional[str] = None
    target_id: Optional[str] = None
    other_id: Optional[str] = None
    other_label: Optional[str] = None
    sheet_id: Optional[str] = None
    valid_at: Optional[str] = None
    invalid_at: Optional[str] = None
    target_sheet_id: Optional[str] = None
    target_unresolved: Optional[bool] = None
    target_sheet: Optional[Dict[str, Any]] = None


class Fact(SDKBaseModel):
    """Relationship entry from /projects/{id}/relationships."""

    id: str
    type: str
    fact: Optional[str] = None
    source_id: Optional[str] = None
    target_id: Optional[str] = None
    sheet_id: Optional[str] = None
    valid_at: Optional[str] = None
    invalid_at: Optional[str] = None
    target_sheet_id: Optional[str] = None
    target_unresolved: Optional[bool] = None


class EntityListItem(SDKBaseModel):
    """Entity summary from /projects/{id}/entities."""

    id: str
    type: str
    label: str
    description: Optional[str] = None
    sheet_id: Optional[str] = None
    bbox: Optional[BBox] = None
    attributes: Optional[Union[Dict[str, Any], List[Any], str]] = None


class Entity(SDKBaseModel):
    """Full entity payload from /projects/{id}/entities/{entity_id}."""

    id: str
    type: str
    label: str
    description: Optional[str] = None
    sheet_id: Optional[str] = None
    bbox: Optional[BBox] = None
    attributes: Optional[Union[Dict[str, Any], List[Any], str]] = None
    provenance: Optional[Union[Dict[str, Any], List[Any], str]] = None
    outgoing: List[EntityRelation] = Field(default_factory=list)
    incoming: List[EntityRelation] = Field(default_factory=list)
    locations: List[EntityLocation] = Field(default_factory=list)


class EntityListResponse(SDKBaseModel):
    """Response envelope for /projects/{id}/entities."""

    project_id: str
    entities: List[EntityListItem] = Field(default_factory=list)


class RelationshipListResponse(SDKBaseModel):
    """Response envelope for /projects/{id}/relationships."""

    project_id: str
    relationships: List[Fact] = Field(default_factory=list)
