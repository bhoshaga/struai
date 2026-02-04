"""StruAI Python SDK - Drawing Analysis API client.

Example:
    >>> from struai import StruAI
    >>>
    >>> client = StruAI(api_key="sk-xxx")
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

from ._version import __version__
from ._client import StruAI, AsyncStruAI
from ._exceptions import (
    StruAIError,
    APIError,
    AuthenticationError,
    PermissionDeniedError,
    NotFoundError,
    ValidationError,
    RateLimitError,
    InternalServerError,
    TimeoutError,
    ConnectionError,
    JobFailedError,
)

# Re-export commonly used models
from .models import (
    # Common
    Point,
    BBox,
    TextSpan,
    Dimensions,
    # Tier 1 - Drawings
    DrawingResult,
    Annotations,
    Leader,
    SectionTag,
    DetailTag,
    RevisionTriangle,
    RevisionCloud,
    TitleBlock,
    # Tier 2 - Projects
    Project,
    Sheet,
    JobStatus,
    SheetResult,
    # Search
    SearchResponse,
    SearchHit,
    QueryResponse,
    # Entities
    Entity,
    Fact,
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
    "Fact",
]
