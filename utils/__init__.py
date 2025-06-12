try:
    from .db_intraday import load_last_timestamp  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    def load_last_timestamp(*args, **kwargs):
        raise ImportError("pandas is required for load_last_timestamp")
