import logging

from src.config.settings import Settings
from src.execution.runner import run_once
from src.metaculus.client import MetaculusAPIError

logger = logging.getLogger(__name__)


def main() -> int:
    settings = Settings.from_env()
    try:
        return run_once(settings)
    except MetaculusAPIError as err:
        logger.error("%s", err)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
