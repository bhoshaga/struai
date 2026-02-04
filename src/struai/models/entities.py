"""Entity and Relationship models."""
from typing import List, Optional

from pydantic import BaseModel


class EntityLocation(BaseModel):
    """Where an entity appears."""

    sheet_id: str
    sheet_title: Optional[str] = None
    page: int


class Fact(BaseModel):
    """Relationship between entities."""

    id: str
    fact: str
    edge_type: str
    source_id: str
    source_label: Optional[str] = None
    target_id: str
    target_label: Optional[str] = None


class Entity(BaseModel):
    """Full entity with relationships."""

    id: str
    type: str
    label: str
    description: Optional[str] = None
    group_id: str
    outgoing_facts: List[Fact] = []
    incoming_facts: List[Fact] = []
    locations: List[EntityLocation] = []
