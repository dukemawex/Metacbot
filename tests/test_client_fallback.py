from unittest.mock import patch
from urllib.error import HTTPError

import pytest

from src.config.settings import Settings
from src.metaculus.client import MetaculusClient


def _settings_with_token(live: bool = False, metaculus_token: str | None = "fake-token") -> Settings:
    base = Settings.from_env()
    # frozen dataclass – rebuild with overrides
    return Settings(
        metaculus_token=metaculus_token,
        exa_api_key=base.exa_api_key,
        openrouter_api_key=base.openrouter_api_key,
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


def test_tournament_meta_requires_token():
    settings = _settings_with_token(metaculus_token=None)
    client = MetaculusClient(settings)
    with pytest.raises(RuntimeError, match="METACULUS_TOKEN is required"):
        client.tournament_meta()


def test_questions_requires_token():
    settings = _settings_with_token(metaculus_token=None)
    client = MetaculusClient(settings)
    with pytest.raises(RuntimeError, match="METACULUS_TOKEN is required"):
        client.questions()


def test_tournament_meta_raises_in_live_mode():
    settings = _settings_with_token(live=True)
    client = MetaculusClient(settings)

    with patch.object(client, "_request_json", side_effect=HTTPError(
        "http://example.com", 403, "Forbidden", {}, None
    )):
        with pytest.raises(HTTPError):
            client.tournament_meta()


def test_questions_raises_in_live_mode():
    settings = _settings_with_token(live=True)
    client = MetaculusClient(settings)

    with patch.object(client, "_request_json", side_effect=HTTPError(
        "http://example.com", 403, "Forbidden", {}, None
    )):
        with pytest.raises(HTTPError):
            client.questions()
