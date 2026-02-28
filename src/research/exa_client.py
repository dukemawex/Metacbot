from __future__ import annotations

import json
import logging
import time
from typing import Any
from urllib import request
from urllib.error import HTTPError, URLError

from src.config.settings import Settings

logger = logging.getLogger(__name__)

# Default search parameters aligned with official template
DEFAULT_NUM_RESULTS = 10
DEFAULT_SEARCH_TYPE = "neural"


class ExaClient:
    """Client for Exa AI search API following official Metaculus template patterns."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self._base_url = "https://api.exa.ai/search"

    def _load_fixture(self) -> list[dict]:
        """Load fixture data for offline/dry-run mode."""
        fixture = self.settings.fixtures_dir / "exa_results.json"
        try:
            data = json.loads(fixture.read_text(encoding="utf-8"))
            return data.get("results", [])
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.warning("Failed to load Exa fixture: %s", e)
            return []

    def _build_headers(self) -> dict[str, str]:
        """Build request headers for Exa API."""
        headers = {"Content-Type": "application/json"}
        if self.settings.exa_api_key:
            headers["x-api-key"] = self.settings.exa_api_key
        return headers

    def _build_request_body(
        self,
        query: str,
        num_results: int = DEFAULT_NUM_RESULTS,
        search_type: str = DEFAULT_SEARCH_TYPE,
        include_highlights: bool = True,
        include_text: bool = True,
    ) -> bytes:
        """Build the request body for the Exa search API."""
        body: dict[str, Any] = {
            "query": query,
            "numResults": num_results,
            "type": search_type,
        }

        # Include contents options for richer results
        contents: dict[str, Any] = {}
        if include_highlights:
            contents["highlights"] = {"numSentences": 3}
        if include_text:
            contents["text"] = {"maxCharacters": 1000}

        if contents:
            body["contents"] = contents

        return json.dumps(body).encode("utf-8")

    def _parse_results(self, response_data: dict) -> list[dict]:
        """Parse and normalize search results."""
        results = response_data.get("results", [])
        normalized = []
        for result in results:
            normalized.append({
                "title": result.get("title", "Untitled"),
                "url": result.get("url", ""),
                "text": result.get("text", ""),
                "highlights": result.get("highlights", []),
                "score": result.get("score", 0.0),
                "publishedDate": result.get("publishedDate"),
                "author": result.get("author"),
            })
        return normalized

    def search(
        self,
        query: str,
        num_results: int = DEFAULT_NUM_RESULTS,
        search_type: str = DEFAULT_SEARCH_TYPE,
    ) -> list[dict]:
        """
        Search for information using Exa's neural search.

        Args:
            query: The search query
            num_results: Number of results to return (default: 10)
            search_type: Type of search - 'neural' or 'keyword' (default: 'neural')

        Returns:
            List of search results with title, url, text, highlights, and score
        """
        if not self.settings.exa_api_key:
            raise RuntimeError("EXA_API_KEY is required for Exa API requests")

        body = self._build_request_body(query, num_results, search_type)
        req = request.Request(
            self._base_url,
            method="POST",
            data=body,
            headers=self._build_headers(),
        )

        last_error: Exception | None = None
        for attempt in range(self.settings.retries):
            try:
                with request.urlopen(req, timeout=self.settings.timeout_seconds) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    return self._parse_results(data)
            except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as e:
                last_error = e
                logger.debug("Exa search attempt %d failed: %s", attempt + 1, e)
                if attempt < self.settings.retries - 1:
                    time.sleep(2**attempt)

        # All retries failed
        raise RuntimeError(f"Exa API request failed after {self.settings.retries} attempts") from last_error

    def search_with_highlights(self, query: str, num_results: int = DEFAULT_NUM_RESULTS) -> list[dict]:
        """
        Search and return results with highlighted relevant passages.

        This is similar to the forecasting-tools ExaSearcher.invoke_for_highlights_in_relevance_order.
        Results are explicitly sorted by score to ensure consistent ordering regardless of API behavior.
        """
        results = self.search(query, num_results)
        return sorted(results, key=lambda x: x.get("score", 0), reverse=True)
