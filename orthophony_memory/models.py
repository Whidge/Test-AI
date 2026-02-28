"""Domain models for the memory test."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SymbolCard:
    """A unique shape-color symbol."""

    shape: str
    color_name: str
    color_hex: str

    @property
    def label(self) -> str:
        return f"{self.color_name} {self.shape}"


@dataclass(frozen=True, slots=True)
class RoundConfig:
    """Round parameters selected by the therapist/user."""

    sequence_length: int
    display_seconds: float

    def __post_init__(self) -> None:
        if not 1 <= self.sequence_length <= 16:
            raise ValueError("sequence_length must be between 1 and 16.")
        if self.display_seconds <= 0:
            raise ValueError("display_seconds must be greater than 0.")

    @property
    def display_milliseconds(self) -> int:
        return int(self.display_seconds * 1000)

