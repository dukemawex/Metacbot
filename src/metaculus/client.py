from __future__ import annotations

import json
import logging
import time
from typing import Any
from urllib import request
from urllib.error import HTTPError, URLError

from src.config.settings import Settings

BASE_URL = "https://www.metaculus.com/api"
BASE_URL_V2 = "https://www.metaculus.com/api2"
ERROR_BODY_LIMIT = 2048
logger = logging.getLogger(__name__)

# Default percentile values for forecasts
DEFAULT_P10 = 0.1
DEFAULT_P50 = 0.5
DEFAULT_P90 = 0.9


class MetaculusAPIError(RuntimeError):
    """Raised when the Metaculus API returns an actionable error."""

    def __init__(self, message: str, http_status: int | None = None, url: str | None = None):
        super().__init__(message)
        self.http_status = http_status
        self.url = url


def _format_payload_for_api(question: dict, forecast: dict) -> dict:
    """Convert internal forecast format to Metaculus API format."""
    qtype = question.get("type", "binary")

    if qtype == "binary":
        return {"probability_yes": forecast.get("probability", 0.5)}

    if qtype in {"multiple_choice", "distribution"}:
        dist = forecast.get("distribution", [])
        return {"probability_yes_per_category": dist}

    if qtype in {"numeric", "discrete"}:
        p10 = forecast.get("p10", DEFAULT_P10)
        p50 = forecast.get("p50", DEFAULT_P50)
        p90 = forecast.get("p90", DEFAULT_P90)
        return {"percentiles": [p10, p50, p90]}

    if qtype == "date":
        date_quantiles = forecast.get("date_quantiles", {})
        return {
            "p10": date_quantiles.get("p10", DEFAULT_P10),
            "p50": date_quantiles.get("p50", DEFAULT_P50),
            "p90": date_quantiles.get("p90", DEFAULT_P90),
        }

    return forecast


class MetaculusClient:
    def __init__(self, settings: Settings):
        self.settings = settings

    def _headers(self) -> dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "metacbot/1.0 (+https://github.com/metacbot)",
        }
        if self.settings.metaculus_token:
            token = self.settings.metaculus_token.strip()
            if not token.startswith(("Token ", "Bearer ")):
                token = f"Token {token}"
            headers["Authorization"] = token
        return headers

    @staticmethod
    def _truncate_error_body(body: bytes | str | None) -> str:
        if body is None:
            return ""
        if isinstance(body, bytes):
            text = body.decode("utf-8", errors="replace")
        else:
            text = body
        text = text.strip()
        if not text:
            return ""
        if len(text) > ERROR_BODY_LIMIT:
            return f"{text[:ERROR_BODY_LIMIT]}..."
        return text

    def _raise_actionable_http_error(self, err: HTTPError, url: str) -> None:
        response_text = ""
        if err.fp is not None:
            try:
                response_text = self._truncate_error_body(err.read())
            except Exception:
                response_text = ""

        if err.code in {401, 403}:
            token_hint = (
                "Authentication token is missing. Set METACULUS_TOKEN (or METACULUS_API_KEY)."
                if not self.settings.metaculus_token
                else "Provided token may be invalid or missing required scope."
            )
            visibility_hint = (
                f"Verify TOURNAMENT_ID={self.settings.tournament_id} is correct and visible to this account."
            )
            body_hint = f" Response body: {response_text}" if response_text else ""
            raise MetaculusAPIError(
                f"Metaculus API request failed with HTTP {err.code} for {url}. "
                f"{token_hint} {visibility_hint}{body_hint}",
                http_status=err.code,
                url=url,
            ) from err

        body_hint = f" Response body: {response_text}" if response_text else ""
        raise MetaculusAPIError(
            f"Metaculus API request failed with HTTP {err.code} for {url}.{body_hint}",
            http_status=err.code,
            url=url,
        ) from err

    def _request_json(self, url: str, method: str = "GET", body: dict[str, Any] | list[dict[str, Any]] | None = None) -> dict:
        payload = None if body is None else json.dumps(body).encode("utf-8")
        req = request.Request(url=url, method=method, headers=self._headers(), data=payload)
        for attempt in range(self.settings.retries):
            try:
                with request.urlopen(req, timeout=self.settings.timeout_seconds) as resp:
                    return json.loads(resp.read().decode("utf-8"))
            except HTTPError as err:
                if err.code in {401, 403, 429} or attempt == self.settings.retries - 1:
                    self._raise_actionable_http_error(err, url)
                time.sleep(2**attempt)
            except URLError as err:
                if attempt == self.settings.retries - 1:
                    raise MetaculusAPIError(f"Metaculus API request failed for {url}: {err}") from err
                time.sleep(2**attempt)
        raise MetaculusAPIError(f"Metaculus API request exhausted retries for {url}")

    def _load_fixture(self, filename: str) -> dict:
        path = self.settings.fixtures_dir / filename
        return json.loads(path.read_text(encoding="utf-8"))

    def _tournament_meta_urls(self) -> list[str]:
        tournament_id = self.settings.tournament_id
        tournament_id_str = str(tournament_id)
        urls = [
            f"{BASE_URL_V2}/projects/{tournament_id_str}/",
            f"{BASE_URL}/projects/{tournament_id_str}/",
            f"{BASE_URL_V2}/tournaments/{tournament_id_str}/",
            f"{BASE_URL}/tournaments/{tournament_id_str}/",
        ]
        if isinstance(tournament_id, int):
            urls.extend(
                [
                    f"{BASE_URL_V2}/posts/{tournament_id}/",
                    f"{BASE_URL}/posts/{tournament_id}/",
                ]
            )
        return urls

    def tournament_meta(self) -> dict:
        urls = self._tournament_meta_urls()
        tried_urls: list[str] = []
        for url in urls:
            try:
                data = self._request_json(url)
                if tried_urls:
                    logger.info(
                        "Tournament metadata fetch succeeded after fallback. tournament_id=%s successful_endpoint=%s tried_endpoints=%s",
                        self.settings.tournament_id,
                        url,
                        [*tried_urls, url],
                    )
                return data
            except MetaculusAPIError as err:
                tried_urls.append(url)
                if err.http_status == 404:
                    logger.warning(
                        "Resource not found: the id may be wrong or endpoint mismatched (project vs tournament). tournament_id=%s endpoint=%s tried_endpoints=%s",
                        self.settings.tournament_id,
                        url,
                        tried_urls,
                    )
                    continue
                raise
        raise MetaculusAPIError(
            "Metaculus tournament metadata lookup failed: Resource not found: the id may be wrong "
            "or endpoint mismatched (project vs tournament). "
            f"tournament_id={self.settings.tournament_id} tried_endpoints={tried_urls}"
        )

    def questions(self) -> list[dict]:
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
