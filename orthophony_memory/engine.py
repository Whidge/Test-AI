"""Core game logic and scoring."""

from __future__ import annotations

import random
from typing import Iterable

from orthophony_memory.constants import COLORS, SHAPES
from orthophony_memory.models import SymbolCard


class MemoryGameEngine:
    """Generates rounds and applies scoring rules."""

    POINTS_CORRECT = 10
    POINTS_INCORRECT = -5
    POINTS_COMPLETION_BONUS = 20

    def __init__(self, rng: random.Random | None = None) -> None:
        self._rng = rng or random.Random()
        self._symbol_pool = self._build_symbol_pool()

    @property
    def symbol_pool(self) -> tuple[SymbolCard, ...]:
        return self._symbol_pool

    def create_round_sequence(self, sequence_length: int) -> list[SymbolCard]:
        if not 1 <= sequence_length <= len(self._symbol_pool):
            raise ValueError(
                f"sequence_length must be between 1 and {len(self._symbol_pool)}."
            )
        return self._rng.sample(self._symbol_pool, k=sequence_length)

    def shuffled_recall_pool(self) -> list[SymbolCard]:
        cards = list(self._symbol_pool)
        self._rng.shuffle(cards)
        return cards

    @classmethod
    def score_choice(
        cls,
        expected: SymbolCard,
        chosen: SymbolCard,
        is_final_choice: bool,
    ) -> tuple[bool, int]:
        if chosen == expected:
            points = cls.POINTS_CORRECT
            if is_final_choice:
                points += cls.POINTS_COMPLETION_BONUS
            return True, points
        return False, cls.POINTS_INCORRECT

    @staticmethod
    def sequence_labels(sequence: Iterable[SymbolCard]) -> str:
        return ", ".join(card.label for card in sequence)

    @staticmethod
    def _build_symbol_pool() -> tuple[SymbolCard, ...]:
        return tuple(
            SymbolCard(shape=shape, color_name=color_name, color_hex=color_hex)
            for shape in SHAPES
            for color_name, color_hex in COLORS.items()
        )

