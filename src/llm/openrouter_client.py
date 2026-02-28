from __future__ import annotations

import json
import logging
import time
from typing import Any
from urllib import request
from urllib.error import HTTPError, URLError

from src.config.settings import Settings

logger = logging.getLogger(__name__)

_OFFLINE_FALLBACK: dict = {"summary": "Offline mode fallback", "probability": 0.5, "confidence": 0.2}

# Default model - can be overridden via settings
DEFAULT_MODEL = "openai/gpt-4o-mini"


class OpenRouterClient:
    """Client for OpenRouter API following official Metaculus template patterns."""

    def __init__(self, settings: Settings, model: str | None = None, temperature: float = 0.3):
        self.settings = settings
        self.model = model or DEFAULT_MODEL
        self.temperature = temperature
        self._base_url = "https://openrouter.ai/api/v1/chat/completions"

    def _build_headers(self) -> dict[str, str]:
        """Build request headers for OpenRouter API."""
        headers = {
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/metaculus/metac-bot-template",
        }
        if self.settings.openrouter_api_key:
            headers["Authorization"] = f"Bearer {self.settings.openrouter_api_key}"
        return headers

    def _build_request_body(
        self,
        prompt: str,
        system_prompt: str | None = None,
        response_format: dict[str, Any] | None = None,
    ) -> bytes:
        """Build the request body for the API call."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        body: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
        }
        if response_format:
            body["response_format"] = response_format

        return json.dumps(body).encode("utf-8")

    def _parse_response(self, response_data: dict) -> str:
        """Extract content from API response."""
        try:
            return response_data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as e:
            raise ValueError(f"Unexpected response format: {e}") from e

    def chat(
        self,
        prompt: str,
        system_prompt: str | None = None,
    ) -> str:
        """Make a chat completion request and return raw text."""
        if not self.settings.openrouter_api_key:
            logger.debug("No OpenRouter API key; returning offline fallback")
            return _OFFLINE_FALLBACK.get("summary", "Offline mode fallback")

        body = self._build_request_body(prompt, system_prompt)
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
                    return self._parse_response(data)
            except (HTTPError, URLError, TimeoutError, json.JSONDecodeError, ValueError) as e:
                last_error = e
                logger.debug("OpenRouter attempt %d failed: %s", attempt + 1, e)
                if attempt < self.settings.retries - 1:
                    time.sleep(2**attempt)

        # All retries failed
        if self.settings.dry_run:
            logger.warning("OpenRouter API request failed; falling back to offline mode (dry-run)")
            return _OFFLINE_FALLBACK.get("summary", "Offline mode fallback")
        raise RuntimeError(f"OpenRouter API request failed after {self.settings.retries} attempts") from last_error

    def chat_json(self, prompt: str, system_prompt: str | None = None) -> dict:
        """Make a chat completion request and return parsed JSON."""
        if not self.settings.openrouter_api_key:
            logger.debug("No OpenRouter API key; returning offline fallback")
            return dict(_OFFLINE_FALLBACK)

        body = self._build_request_body(
            prompt,
            system_prompt,
            response_format={"type": "json_object"},
        )
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
                    content = self._parse_response(data)
                    return json.loads(content)
            except (HTTPError, URLError, TimeoutError, json.JSONDecodeError, ValueError) as e:
                last_error = e
                logger.debug("OpenRouter attempt %d failed: %s", attempt + 1, e)
                if attempt < self.settings.retries - 1:
                    time.sleep(2**attempt)

        # All retries failed
        if self.settings.dry_run:
            logger.warning("OpenRouter API request failed; falling back to offline mode (dry-run)")
            return dict(_OFFLINE_FALLBACK)
        raise RuntimeError(f"OpenRouter API request failed after {self.settings.retries} attempts") from last_error
