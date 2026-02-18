"""DocQuery traversal models."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import Field

from .common import SDKBaseModel


class DocQuerySummaryCounters(SDKBaseModel):
    nodes_created: Optional[int] = None
    nodes_deleted: Optional[int] = None
    relationships_created: Optional[int] = None
    relationships_deleted: Optional[int] = None
    properties_set: Optional[int] = None
    labels_added: Optional[int] = None
    labels_removed: Optional[int] = None
    indexes_added: Optional[int] = None
    indexes_removed: Optional[int] = None
    constraints_added: Optional[int] = None
    constraints_removed: Optional[int] = None
    system_updates: Optional[int] = None
    contains_updates: Optional[bool] = None


class DocQuerySummary(SDKBaseModel):
    database: Optional[str] = None
    query_type: Optional[str] = None
    result_available_after_ms: Optional[int] = None
    result_consumed_after_ms: Optional[int] = None
    counters: Optional[DocQuerySummaryCounters] = None


class DocQuerySearchHit(SDKBaseModel):
    node: Optional[Dict[str, Any]] = None
    score: Optional[float] = None


class DocQueryNeighbor(SDKBaseModel):
    direction: Optional[str] = None
    relationship: Optional[Dict[str, Any]] = None
    neighbor_node: Optional[Dict[str, Any]] = None


class DocQueryNodeGetResult(SDKBaseModel):
    ok: bool
    command: str
    input: Dict[str, Any] = Field(default_factory=dict)
    found: bool
    node: Optional[Dict[str, Any]] = None
    summary: Optional[DocQuerySummary] = None


class DocQuerySheetEntitiesResult(SDKBaseModel):
    ok: bool
    command: str
    input: Dict[str, Any] = Field(default_factory=dict)
    entities: List[Dict[str, Any]] = Field(default_factory=list)
    count: int = 0
    summary: Optional[DocQuerySummary] = None


class DocQuerySearchResult(SDKBaseModel):
    ok: bool
    command: str
    input: Dict[str, Any] = Field(default_factory=dict)
    hits: List[DocQuerySearchHit] = Field(default_factory=list)
    count: int = 0
    summary: Optional[DocQuerySummary] = None


class DocQueryNeighborsResult(SDKBaseModel):
    ok: bool
    command: str
    input: Dict[str, Any] = Field(default_factory=dict)
    neighbors: List[DocQueryNeighbor] = Field(default_factory=list)
    count: int = 0
    summary: Optional[DocQuerySummary] = None


class DocQueryCypherResult(SDKBaseModel):
    ok: bool
    command: str
    input: Dict[str, Any] = Field(default_factory=dict)
    records: List[Dict[str, Any]] = Field(default_factory=list)
    record_count: int = 0
    truncated: bool = False
    summary: Optional[DocQuerySummary] = None


class DocQuerySheetSummaryResult(SDKBaseModel):
    ok: bool
    command: str
    input: Dict[str, Any] = Field(default_factory=dict)
    sheet_node: Optional[Dict[str, Any]] = None
    node_label_counts: List[Dict[str, Any]] = Field(default_factory=list)
    relationship_counts: List[Dict[str, Any]] = Field(default_factory=list)
    reachability: Dict[str, Any] = Field(default_factory=dict)
    orphan_examples: List[Dict[str, Any]] = Field(default_factory=list)
    warnings: List[Dict[str, Any]] = Field(default_factory=list)


class DocQuerySheetListResult(SDKBaseModel):
    ok: bool
    command: str
    input: Dict[str, Any] = Field(default_factory=dict)
    sheet_nodes: List[Dict[str, Any]] = Field(default_factory=list)
    entity_sheet_inventory: List[Dict[str, Any]] = Field(default_factory=list)
    totals: Dict[str, Any] = Field(default_factory=dict)
    mismatch_warnings: List[Dict[str, Any]] = Field(default_factory=list)


class DocQueryReferenceResolveResult(SDKBaseModel):
    ok: bool
    command: str
    input: Dict[str, Any] = Field(default_factory=dict)
    found: bool = False
    source: Optional[Dict[str, Any]] = None
    resolved_references: List[Dict[str, Any]] = Field(default_factory=list)
    count: int = 0
    warnings: List[Dict[str, Any]] = Field(default_factory=list)
