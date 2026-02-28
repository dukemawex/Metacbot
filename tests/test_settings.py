from src.config.settings import Settings


def test_from_env_uses_repo_relative_paths(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    settings = Settings.from_env()
    expected_root = settings.fixtures_dir.parent.parent
    assert settings.fixtures_dir == expected_root / "tests" / "fixtures"
    assert settings.data_dir == expected_root / "data"
