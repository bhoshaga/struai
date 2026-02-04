"""Common types shared across models."""
from typing import Tuple

from pydantic import BaseModel

# Coordinate types
Point = Tuple[float, float]  # [x, y]
BBox = Tuple[float, float, float, float]  # [x1, y1, x2, y2]


class TextSpan(BaseModel):
    """Text detected inside an annotation."""

    id: int
    text: str


class Dimensions(BaseModel):
    """Page dimensions in pixels."""

    width: int
    height: int


class Circle(BaseModel):
    """Circle geometry."""

    center: Point
    radius: float


class Line(BaseModel):
    """Line segment."""

    start: Point
    end: Point
