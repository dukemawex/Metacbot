from src.config.settings import Settings
from src.execution.runner import run_once


def main() -> int:
    settings = Settings.from_env()
    return run_once(settings)


if __name__ == "__main__":
    raise SystemExit(main())
