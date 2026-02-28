from src.config.settings import Settings


def test_from_env_uses_repo_relative_paths(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    settings = Settings.from_env()
    assert settings.fixtures_dir.exists()
    assert settings.data_dir.parent == settings.fixtures_dir.parent.parent
