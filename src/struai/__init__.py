"""StruAI Python SDK - Drawing Analysis API client.

Example:
    >>> import os
    >>> from struai import StruAI
    >>>
    >>> client = StruAI(api_key=os.environ["STRUAI_API_KEY"])
    >>>
    >>> # Tier 1: Raw detection ($0.02/page)
    >>> result = client.drawings.analyze("plans.pdf", page=4)
    >>> for leader in result.annotations.leaders:
    ...     print(leader.texts_inside[0].text)
    >>>
    >>> # Tier 2: Graph + Search ($0.15/page)
    >>> project = client.projects.create("Building A")
    >>> job = project.sheets.add("plans.pdf", page=4)
    >>> job.wait()
    >>> results = project.search("W12x26 beam connections")
"""

from ._client import AsyncStruAI, StruAI
from ._exceptions import (
    APIError,
    AuthenticationError,
    ConnectionError,
    InternalServerError,
    JobFailedError,
    NotFoundError,
    PermissionDeniedError,
    RateLimitError,
    StruAIError,
    TimeoutError,
    ValidationError,
)
from ._version import __version__

# Re-export commonly used models
from .models import (
    Annotations,
    BBox,
    DetailTag,
    Dimensions,
    # Tier 1 - Drawings
    DrawingResult,
    # Entities
    Entity,
    EntityListItem,
    EntityRelation,
    Fact,
    JobStatus,
    Leader,
    # Common
    Point,
    # Tier 2 - Projects
    Project,
    QueryResponse,
    RevisionCloud,
    RevisionTriangle,
    SearchHit,
    # Search
    SearchResponse,
    SectionTag,
    Sheet,
    SheetResult,
    TextSpan,
    TitleBlock,
)

__all__ = [
    # Version
    "__version__",
    # Clients
    "StruAI",
    "AsyncStruAI",
    # Exceptions
    "StruAIError",
    "APIError",
    "AuthenticationError",
    "PermissionDeniedError",
    "NotFoundError",
    "ValidationError",
    "RateLimitError",
    "InternalServerError",
    "TimeoutError",
    "ConnectionError",
    "JobFailedError",
    # Models - Common
    "Point",
    "BBox",
    "TextSpan",
    "Dimensions",
    # Models - Tier 1
    "DrawingResult",
    "Annotations",
    "Leader",
    "SectionTag",
    "DetailTag",
    "RevisionTriangle",
    "RevisionCloud",
    "TitleBlock",
    # Models - Tier 2
    "Project",
    "Sheet",
    "JobStatus",
    "SheetResult",
    "SearchResponse",
    "SearchHit",
    "QueryResponse",
    "Entity",
    "EntityListItem",
    "EntityRelation",
    "Fact",
]
