from __future__ import annotations

import json
import logging
import time
from typing import Any
from urllib import request

from src.config.settings import Settings

BASE_URL = "https://www.metaculus.com/api"
logger = logging.getLogger(__name__)


def _format_payload_for_api(question: dict, forecast: dict) -> dict:
    """Convert internal forecast format to Metaculus API format."""
    qtype = question.get("type", "binary")

    if qtype == "binary":
        return {"probability_yes": forecast.get("probability", 0.5)}

    if qtype in {"multiple_choice", "distribution"}:
        dist = forecast.get("distribution", [])
        return {"probability_yes_per_category": dist}

    if qtype in {"numeric", "discrete"}:
        p10 = forecast.get("p10", 0.1)
        p50 = forecast.get("p50", 0.5)
        p90 = forecast.get("p90", 0.9)
        return {"percentiles": [p10, p50, p90]}

    if qtype == "date":
        date_quantiles = forecast.get("date_quantiles", {})
        return {
            "p10": date_quantiles.get("p10", 0.1),
            "p50": date_quantiles.get("p50", 0.5),
            "p90": date_quantiles.get("p90", 0.9),
        }

    return forecast


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
            return self._request_json(f"{BASE_URL}/projects/{self.settings.tournament_id}/")
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
            url = (
                f"{BASE_URL}/posts/"
                f"?tournaments={self.settings.tournament_id}"
                f"&has_group=false"
                f"&order_by=-hotness"
                f"&forecast_type=all"
                f"&project={self.settings.tournament_id}"
                f"&statuses=open,upcoming"
                f"&include_description=true"
                f"&limit=100"
            )
            data = self._request_json(url)
            results = data.get("results", [])
            questions = []
            for post in results:
                question = post.get("question")
                if question:
                    question["post_id"] = post.get("id")
                    questions.append(question)
            return questions
        except Exception:
            if self.settings.dry_run:
                logger.warning("API request failed; falling back to fixture data (dry-run mode)")
                data = self._load_fixture("metaculus_questions.json")
                return data.get("results", data)
            raise

    def submit(self, question: dict, forecast: dict, reasoning: str) -> dict:
        """Submit a forecast using the official Metaculus API endpoint."""
        question_id = question.get("id")
        formatted_payload = _format_payload_for_api(question, forecast)
        body = [{"question": question_id, **formatted_payload}]
        return self._request_json(f"{BASE_URL}/questions/forecast/", method="POST", body=body)

    def post_comment(self, post_id: int, comment_text: str) -> dict:
        """Post a comment on a question page."""
        body = {
            "text": comment_text,
            "parent": None,
            "included_forecast": True,
            "is_private": True,
            "on_post": post_id,
        }
        return self._request_json(f"{BASE_URL}/comments/create/", method="POST", body=body)
