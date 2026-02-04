"""Entity and Relationship models."""
from typing import List, Optional

from pydantic import BaseModel

from .common import BBox


class EntityLocation(BaseModel):
    """Where an entity appears."""

    sheet_id: str
    sheet_title: Optional[str] = None
    page: Optional[int] = None


class EntityRelation(BaseModel):
    """Relationship entry on an entity detail response."""

    uuid: str
    type: str
    fact: str
    source_id: Optional[str] = None
    source_label: Optional[str] = None
    target_id: Optional[str] = None
    target_label: Optional[str] = None


class Fact(BaseModel):
    """Relationship between entities (list endpoint)."""

    id: str
    type: str
    fact: str
    source_id: str
    target_id: str
    source_label: Optional[str] = None
    target_label: Optional[str] = None


class EntityListItem(BaseModel):
    """Entity summary from list endpoint."""

    id: str
    type: str
    label: str
    description: Optional[str] = None
    sheet_id: Optional[str] = None
    bbox: Optional[BBox] = None
    attributes: Optional[str] = None


class Entity(BaseModel):
    """Full entity with relationships."""

    id: str
    type: str
    label: str
    description: Optional[str] = None
    outgoing: List[EntityRelation] = []
    incoming: List[EntityRelation] = []
    locations: List[EntityLocation] = []
