# Expose module
from literator.api.base import APIClient
from literator.api.scopus import ScopusAPIClient
from literator.api.base import get_api_client

__all__ = ["APIClient", "ScopusAPIClient", "get_api_client"]
