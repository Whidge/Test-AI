"""Static configuration for game symbols and visuals."""

from __future__ import annotations

from typing import Final

SHAPES: Final[tuple[str, ...]] = ("circle", "triangle", "square", "rectangle")

COLORS: Final[dict[str, str]] = {
    "red": "#E74C3C",
    "blue": "#3498DB",
    "green": "#2ECC71",
    "yellow": "#F1C40F",
}

RECALL_GRID_COLUMNS: Final[int] = 4
DEFAULT_SEQUENCE_LENGTH: Final[int] = 6
DEFAULT_DISPLAY_SECONDS: Final[float] = 1.5

