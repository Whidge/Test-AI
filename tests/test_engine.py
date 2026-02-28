"""Unit tests for memory game logic."""

from __future__ import annotations

import random
import unittest

from orthophony_memory.engine import MemoryGameEngine
from orthophony_memory.models import RoundConfig


class MemoryGameEngineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = MemoryGameEngine(rng=random.Random(42))

    def test_symbol_pool_contains_16_unique_cards(self) -> None:
        pool = self.engine.symbol_pool
        self.assertEqual(len(pool), 16)
        self.assertEqual(len(set(pool)), 16)

    def test_create_round_sequence_has_requested_unique_length(self) -> None:
        sequence = self.engine.create_round_sequence(8)
        self.assertEqual(len(sequence), 8)
        self.assertEqual(len(set(sequence)), 8)

    def test_score_choice_correct_non_final(self) -> None:
        card = self.engine.symbol_pool[0]
        is_correct, points = self.engine.score_choice(
            expected=card,
            chosen=card,
            is_final_choice=False,
        )
        self.assertTrue(is_correct)
        self.assertEqual(points, MemoryGameEngine.POINTS_CORRECT)

    def test_score_choice_correct_final_includes_bonus(self) -> None:
        card = self.engine.symbol_pool[0]
        is_correct, points = self.engine.score_choice(
            expected=card,
            chosen=card,
            is_final_choice=True,
        )
        self.assertTrue(is_correct)
        self.assertEqual(
            points,
            MemoryGameEngine.POINTS_CORRECT
            + MemoryGameEngine.POINTS_COMPLETION_BONUS,
        )

    def test_score_choice_incorrect(self) -> None:
        expected = self.engine.symbol_pool[0]
        chosen = self.engine.symbol_pool[1]
        is_correct, points = self.engine.score_choice(
            expected=expected,
            chosen=chosen,
            is_final_choice=False,
        )
        self.assertFalse(is_correct)
        self.assertEqual(points, MemoryGameEngine.POINTS_INCORRECT)


class RoundConfigTests(unittest.TestCase):
    def test_round_config_rejects_invalid_length(self) -> None:
        with self.assertRaises(ValueError):
            RoundConfig(sequence_length=0, display_seconds=1)

    def test_round_config_rejects_non_positive_display_time(self) -> None:
        with self.assertRaises(ValueError):
            RoundConfig(sequence_length=4, display_seconds=0)


if __name__ == "__main__":
    unittest.main()

