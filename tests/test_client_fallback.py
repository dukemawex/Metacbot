from unittest.mock import patch
from urllib.error import HTTPError

from src.config.settings import Settings
from src.metaculus.client import MetaculusClient


def _make_settings(token: str | None, live: bool) -> Settings:
    return Settings.from_env()._replace(metaculus_token=token, live_mode=live)


def _settings_with_token(live: bool = False) -> Settings:
    base = Settings.from_env()
    # frozen dataclass – rebuild with overrides
    return Settings(
        metaculus_token="fake-token",
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


def test_tournament_meta_falls_back_on_http_error_in_dry_run():
    settings = _settings_with_token(live=False)
    client = MetaculusClient(settings)

    with patch.object(client, "_request_json", side_effect=HTTPError(
        "http://example.com", 403, "Forbidden", {}, None
    )):
        result = client.tournament_meta()

    assert isinstance(result, dict)
    assert "id" in result or "name" in result or len(result) > 0


def test_questions_falls_back_on_http_error_in_dry_run():
    settings = _settings_with_token(live=False)
    client = MetaculusClient(settings)

    with patch.object(client, "_request_json", side_effect=HTTPError(
        "http://example.com", 403, "Forbidden", {}, None
    )):
        result = client.questions()

    assert isinstance(result, list)


def test_tournament_meta_raises_in_live_mode():
    settings = _settings_with_token(live=True)
    client = MetaculusClient(settings)

    with patch.object(client, "_request_json", side_effect=HTTPError(
        "http://example.com", 403, "Forbidden", {}, None
    )):
        try:
            client.tournament_meta()
            assert False, "Expected HTTPError"
        except HTTPError:
            pass


def test_questions_raises_in_live_mode():
    settings = _settings_with_token(live=True)
    client = MetaculusClient(settings)

    with patch.object(client, "_request_json", side_effect=HTTPError(
        "http://example.com", 403, "Forbidden", {}, None
    )):
        try:
            client.questions()
            assert False, "Expected HTTPError"
        except HTTPError:
            pass
