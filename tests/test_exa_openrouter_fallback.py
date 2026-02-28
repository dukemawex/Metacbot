from unittest.mock import patch
from urllib.error import HTTPError

import pytest

from src.config.settings import Settings
from src.llm.openrouter_client import OpenRouterClient
from src.research.exa_client import ExaClient


def _settings(
    exa_api_key: str | None = "fake-exa-key",
    openrouter_api_key: str | None = "fake-openrouter-key",
) -> Settings:
    base = Settings.from_env()
    return Settings(
        metaculus_token="fake-token",
        exa_api_key=exa_api_key,
        openrouter_api_key=openrouter_api_key,
        max_questions=base.max_questions,
        timeout_seconds=base.timeout_seconds,
        retries=1,
        cooldown_minutes=base.cooldown_minutes,
        min_prob=base.min_prob,
        max_prob=base.max_prob,
        tournament_id=base.tournament_id,
        data_dir=base.data_dir,
        fixtures_dir=base.fixtures_dir,
    )


def test_exa_search_requires_api_key():
    settings = _settings(exa_api_key=None)
    client = ExaClient(settings)
    with pytest.raises(RuntimeError, match="EXA_API_KEY is required"):
        client.search("test query")


def test_exa_search_raises_on_http_error():
    settings = _settings()
    client = ExaClient(settings)

    with patch("src.research.exa_client.request.urlopen", side_effect=HTTPError(
        "http://example.com", 403, "Forbidden", {}, None
    )):
        with pytest.raises(RuntimeError, match="Exa API request failed"):
            client.search("test query")


def test_openrouter_chat_json_requires_api_key():
    settings = _settings(openrouter_api_key=None)
    client = OpenRouterClient(settings)
    with pytest.raises(RuntimeError, match="OPENROUTER_API_KEY is required"):
        client.chat_json("test prompt")


def test_openrouter_chat_json_raises_on_http_error():
    settings = _settings()
    client = OpenRouterClient(settings)

    with patch("src.llm.openrouter_client.request.urlopen", side_effect=HTTPError(
        "http://example.com", 403, "Forbidden", {}, None
    )):
        with pytest.raises(RuntimeError, match="OpenRouter API request failed"):
            client.chat_json("test prompt")


def test_openrouter_chat_requires_api_key():
    settings = _settings(openrouter_api_key=None)
    client = OpenRouterClient(settings)
    with pytest.raises(RuntimeError, match="OPENROUTER_API_KEY is required"):
        client.chat("test prompt")


def test_openrouter_chat_raises_on_http_error():
    settings = _settings()
    client = OpenRouterClient(settings)

    with patch("src.llm.openrouter_client.request.urlopen", side_effect=HTTPError(
        "http://example.com", 403, "Forbidden", {}, None
    )):
        with pytest.raises(RuntimeError, match="OpenRouter API request failed"):
            client.chat("test prompt")
