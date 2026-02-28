from unittest.mock import patch
from urllib.error import HTTPError

import pytest

from src.config.settings import Settings
from src.llm.openrouter_client import OpenRouterClient
from src.research.exa_client import ExaClient


def _settings(live: bool = False) -> Settings:
    base = Settings.from_env()
    return Settings(
        metaculus_token="fake-token",
        exa_api_key="fake-exa-key",
        openrouter_api_key="fake-openrouter-key",
        live_mode=live,
        strict_open_window=base.strict_open_window,
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


def test_exa_search_falls_back_on_http_error_in_dry_run():
    settings = _settings(live=False)
    client = ExaClient(settings)

    with patch("src.research.exa_client.request.urlopen", side_effect=HTTPError(
        "http://example.com", 403, "Forbidden", {}, None
    )):
        result = client.search("test query")

    assert isinstance(result, list)


def test_exa_search_raises_in_live_mode():
    settings = _settings(live=True)
    client = ExaClient(settings)

    with patch("src.research.exa_client.request.urlopen", side_effect=HTTPError(
        "http://example.com", 403, "Forbidden", {}, None
    )):
        with pytest.raises(RuntimeError, match="Exa API request failed"):
            client.search("test query")


def test_openrouter_chat_json_falls_back_on_http_error_in_dry_run():
    settings = _settings(live=False)
    client = OpenRouterClient(settings)

    with patch("src.llm.openrouter_client.request.urlopen", side_effect=HTTPError(
        "http://example.com", 403, "Forbidden", {}, None
    )):
        result = client.chat_json("test prompt")

    assert isinstance(result, dict)
    assert "probability" in result


def test_openrouter_chat_json_raises_in_live_mode():
    settings = _settings(live=True)
    client = OpenRouterClient(settings)

    with patch("src.llm.openrouter_client.request.urlopen", side_effect=HTTPError(
        "http://example.com", 403, "Forbidden", {}, None
    )):
        with pytest.raises(RuntimeError, match="OpenRouter API request failed"):
            client.chat_json("test prompt")


def test_openrouter_chat_falls_back_on_http_error_in_dry_run():
    settings = _settings(live=False)
    client = OpenRouterClient(settings)

    with patch("src.llm.openrouter_client.request.urlopen", side_effect=HTTPError(
        "http://example.com", 403, "Forbidden", {}, None
    )):
        result = client.chat("test prompt")

    assert isinstance(result, str)


def test_openrouter_chat_raises_in_live_mode():
    settings = _settings(live=True)
    client = OpenRouterClient(settings)

    with patch("src.llm.openrouter_client.request.urlopen", side_effect=HTTPError(
        "http://example.com", 403, "Forbidden", {}, None
    )):
        with pytest.raises(RuntimeError, match="OpenRouter API request failed"):
            client.chat("test prompt")
