"""Literature review management tool."""

__version__ = "0.1.0"

# Setup logging and configuration
from literator.utils import setup_logging
from literator.config import Config

setup_logging()

# Expose specific common objects
# Ruff disabled: Forcing setup of logging and config first
from literator.db.models import Paper, Author, Keyword  # noqa: E402
from literator.api import get_api_client  # noqa: E402

__all__ = ["Config", "Paper", "Author", "Keyword", "get_api_client"]
