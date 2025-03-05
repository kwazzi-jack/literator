from datetime import datetime, timezone


def get_timestamp() -> str:
    """Get the current timestamp in a format suitable for filenames."""
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
