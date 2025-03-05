from datetime import datetime, timezone


def get_timestamp(pattern: str = "%Y%m%d_%H%M%S") -> str:
    """Get the current timestamp in a format suitable for filenames."""
    return datetime.now(timezone.utc).strftime(pattern)


def str_to_datetime(timestamp: str, pattern: str = "%Y%m%d_%H%M%S") -> datetime:
    return datetime.strptime(timestamp, pattern)
