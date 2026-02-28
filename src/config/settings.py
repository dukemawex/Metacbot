from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from src.config import constants


@dataclass(frozen=True)
class Settings:
    metaculus_token: str | None
    exa_api_key: str | None
    openrouter_api_key: str | None
    max_questions: int
    timeout_seconds: int
    retries: int
    cooldown_minutes: int
    min_prob: float
    max_prob: float
    tournament_id: int | str
    data_dir: Path
    fixtures_dir: Path

    @staticmethod
    def _parse_tournament_id(value: str) -> int | str:
        """Parse tournament ID - try as int first, fall back to string."""
        try:
            return int(value)
        except ValueError:
            return value

    @classmethod
    def from_env(cls) -> "Settings":
        base = Path(__file__).resolve().parents[2]
        return cls(
            metaculus_token=os.getenv("METACULUS_TOKEN"),
            exa_api_key=os.getenv("EXA_API_KEY"),
            openrouter_api_key=os.getenv("OPENROUTER_API_KEY"),
            max_questions=int(os.getenv("MAX_QUESTIONS", constants.DEFAULT_MAX_QUESTIONS)),
            timeout_seconds=int(os.getenv("TIMEOUT_SECONDS", constants.DEFAULT_TIMEOUT_SECONDS)),
            retries=int(os.getenv("RETRIES", constants.DEFAULT_RETRIES)),
            cooldown_minutes=int(os.getenv("COOLDOWN_MINUTES", constants.DEFAULT_COOLDOWN_MINUTES)),
            min_prob=float(os.getenv("MIN_PROB", constants.DEFAULT_MIN_PROB)),
            max_prob=float(os.getenv("MAX_PROB", constants.DEFAULT_MAX_PROB)),
            tournament_id=cls._parse_tournament_id(os.getenv("TOURNAMENT_ID", str(constants.TOURNAMENT_ID))),
            data_dir=base / "data",
            fixtures_dir=base / "tests" / "fixtures",
        )

    def preflight(self) -> tuple[bool, list[str]]:
        errors: list[str] = []
        if not self.metaculus_token:
            errors.append("METACULUS_TOKEN is required")
        if not self.exa_api_key:
            errors.append("EXA_API_KEY is required")
        if not self.openrouter_api_key:
            errors.append("OPENROUTER_API_KEY is required")
        return (len(errors) == 0, errors)
