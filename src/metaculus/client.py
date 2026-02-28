from __future__ import annotations

import json
import logging
import time
from typing import Any
from urllib import request

from src.config.settings import Settings

BASE_URL = "https://www.metaculus.com/api2"
logger = logging.getLogger(__name__)


class MetaculusClient:
    def __init__(self, settings: Settings):
        self.settings = settings

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.settings.metaculus_token:
            headers["Authorization"] = f"Token {self.settings.metaculus_token}"
        return headers

    def _request_json(self, url: str, method: str = "GET", body: dict[str, Any] | None = None) -> dict:
        payload = None if body is None else json.dumps(body).encode("utf-8")
        req = request.Request(url=url, method=method, headers=self._headers(), data=payload)
        for attempt in range(self.settings.retries):
            try:
                with request.urlopen(req, timeout=self.settings.timeout_seconds) as resp:
                    return json.loads(resp.read().decode("utf-8"))
            except Exception:
                if attempt == self.settings.retries - 1:
                    raise
                time.sleep(2**attempt)
        return {}

    def _load_fixture(self, filename: str) -> dict:
        path = self.settings.fixtures_dir / filename
        return json.loads(path.read_text(encoding="utf-8"))

    def tournament_meta(self) -> dict:
        if not self.settings.metaculus_token:
            return self._load_fixture("metaculus_tournament_32916.json")
        try:
            return self._request_json(f"{BASE_URL}/tournaments/{self.settings.tournament_id}/")
        except Exception:
            if self.settings.dry_run:
                logger.warning("API request failed; falling back to fixture data (dry-run mode)")
                return self._load_fixture("metaculus_tournament_32916.json")
            raise

    def questions(self) -> list[dict]:
        if not self.settings.metaculus_token:
            data = self._load_fixture("metaculus_questions.json")
            return data.get("results", data)
        try:
            data = self._request_json(
                f"{BASE_URL}/questions/?tournaments={self.settings.tournament_id}&limit=100"
            )
            return data.get("results", [])
        except Exception:
            if self.settings.dry_run:
                logger.warning("API request failed; falling back to fixture data (dry-run mode)")
                data = self._load_fixture("metaculus_questions.json")
                return data.get("results", data)
            raise

    def submit(self, question_id: int, forecast_payload: dict, reasoning: str) -> dict:
        body = {"prediction": forecast_payload, "comment": reasoning}
        return self._request_json(
            f"{BASE_URL}/questions/{question_id}/predict/", method="POST", body=body
        )
