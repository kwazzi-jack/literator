from datetime import datetime, timezone

SQUOTE = "'"
DQUOTE = '"'
SPACE = " "
COMMA = ","


def get_timestamp(pattern: str = "%Y%m%d_%H%M%S") -> str:
    """Get the current timestamp in a format suitable for filenames."""
    return datetime.now(timezone.utc).strftime(pattern)


def str_to_datetime(timestamp: str, pattern: str = "%Y%m%d_%H%M%S") -> datetime:
    return datetime.strptime(timestamp, pattern)


def format_phrase(value: str, exact: bool = False) -> str:
    strip_val = value.strip()
    wrapped = (strip_val.startswith(SQUOTE) and strip_val.endswith(SQUOTE)) or (
        strip_val.startswith(DQUOTE) and strip_val.endswith(DQUOTE)
    )
    if not wrapped and (exact or SPACE in value or COMMA in value):
        return f'"{strip_val}"'
    else:
        return strip_val
