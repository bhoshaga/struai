"""Common types shared across SDK models."""

from __future__ import annotations

from typing import Dict, List, Tuple, Union

from pydantic import BaseModel, ConfigDict

Point = Tuple[float, float]
BBox = Tuple[float, float, float, float]
JSONValue = Union[str, int, float, bool, None, Dict[str, "JSONValue"], List["JSONValue"]]


class SDKBaseModel(BaseModel):
    """Base model that tolerates forward-compatible extra fields."""

    model_config = ConfigDict(extra="allow")


class TextSpan(SDKBaseModel):
    """Text detected inside an annotation."""

    id: Union[int, str, None] = None
    text: str = ""


class Dimensions(SDKBaseModel):
    """Page dimensions in fitz coordinate space."""

    width: float = 0.0
    height: float = 0.0


class Circle(SDKBaseModel):
    """Circle geometry."""

    center: Point
    radius: float


class Line(SDKBaseModel):
    """Line segment."""

    start: Point
    end: Point
