from io import BytesIO
from unittest.mock import MagicMock, patch
from urllib.error import HTTPError

import pytest

from src.config.settings import Settings
from src.metaculus.client import MetaculusAPIError, MetaculusClient


def _settings_with_token(metaculus_token: str | None = "fake-token") -> Settings:
    base = Settings.from_env()
    return Settings(
        metaculus_token=metaculus_token,
        exa_api_key=base.exa_api_key,
        openrouter_api_key=base.openrouter_api_key,
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


def _mock_urlopen():
    response = MagicMock()
    response.read.return_value = b"{}"
    urlopen_mock = MagicMock()
    urlopen_mock.return_value.__enter__.return_value = response
    return urlopen_mock


def test_request_includes_standard_headers():
    settings = _settings_with_token("abc123")
    client = MetaculusClient(settings)
    with patch("src.metaculus.client.request.Request") as request_mock:
        with patch("src.metaculus.client.request.urlopen", _mock_urlopen()):
            client._request_json("http://example.com")
    headers = request_mock.call_args.kwargs["headers"]
    assert headers["Accept"] == "application/json"
    assert headers["User-Agent"].startswith("metacbot/")


def test_request_includes_authorization_token_header():
    settings = _settings_with_token("abc123")
    client = MetaculusClient(settings)
    with patch("src.metaculus.client.request.Request") as request_mock:
        with patch("src.metaculus.client.request.urlopen", _mock_urlopen()):
            client._request_json("http://example.com")
    headers = request_mock.call_args.kwargs["headers"]
    assert headers["Authorization"] == "Token abc123"


def test_request_preserves_prefixed_authorization_token():
    settings = _settings_with_token("Token abc123")
    client = MetaculusClient(settings)
    with patch("src.metaculus.client.request.Request") as request_mock:
        with patch("src.metaculus.client.request.urlopen", _mock_urlopen()):
            client._request_json("http://example.com")
    headers = request_mock.call_args.kwargs["headers"]
    assert headers["Authorization"] == "Token abc123"


def test_tournament_meta_allows_missing_token_for_public_projects():
    settings = _settings_with_token(metaculus_token=None)
    client = MetaculusClient(settings)
    with patch.object(client, "_request_json", return_value={"id": 123}) as request_mock:
        result = client.tournament_meta()
    assert result == {"id": 123}
    assert request_mock.called


def test_403_raises_actionable_error_with_token_and_visibility_hints():
    settings = _settings_with_token(metaculus_token=None)
    client = MetaculusClient(settings)

    error = HTTPError(
        "http://example.com",
        403,
        "Forbidden",
        hdrs={},
        fp=BytesIO(b'{"detail":"Auth required"}'),
    )

    with patch("src.metaculus.client.request.urlopen", side_effect=error):
        with pytest.raises(MetaculusAPIError) as exc:
            client._request_json("http://example.com")

    message = str(exc.value)
    assert "METACULUS_TOKEN" in message
    assert "METACULUS_API_KEY" in message
    assert "TOURNAMENT_ID" in message
    assert "Auth required" in message
