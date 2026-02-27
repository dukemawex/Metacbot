def maybe_forecasting_tools() -> bool:
    try:
        import forecasting_tools  # type: ignore  # noqa: F401

        return True
    except Exception:
        return False
