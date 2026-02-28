"""Persistence helpers for score tracking."""

from __future__ import annotations

import json
from pathlib import Path


class BestScoreStore:
    """Stores the best round score on disk."""

    def __init__(self, score_file: Path | None = None) -> None:
        self._score_file = score_file or Path.home() / ".orthophony_memory_score.json"

    def load(self) -> int:
        if not self._score_file.exists():
            return 0
        try:
            payload = json.loads(self._score_file.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return 0
        raw_score = payload.get("best_round_score", 0)
        return raw_score if isinstance(raw_score, int) and raw_score >= 0 else 0

    def save_if_higher(self, score: int) -> int:
        current_best = self.load()
        if score <= current_best:
            return current_best
        payload = {"best_round_score": score}
        try:
            self._score_file.write_text(
                json.dumps(payload, indent=2),
                encoding="utf-8",
            )
        except OSError:
            return current_best
        return score

