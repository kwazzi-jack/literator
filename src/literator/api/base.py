from abc import ABC, abstractmethod
import logging
from typing import List, Dict, Any, Literal, Optional

from literator.config import get_api_config
from literator.db.models import Paper

logger = logging.getLogger(__name__)


class APIClient(ABC):
    """Abstract base class for API clients used in literature review.

    This class provides a foundation for implementing API clients that interact with
    various academic paper databases and search services. It handles common initialization
    tasks such as setting up API keys, URLs, and other configuration parameters.

    Attributes:
        name (str): Name identifier for the API client
        api_key (str): Authentication key for API access
        api_url (str): Base URL for API endpoints
        timeout (int): Request timeout in seconds
        max_results_per_request (int): Maximum number of results per API request
        headers (dict): HTTP headers for API requests

    Args:
        name (str): Name identifier for the API client
        api_key (Optional[str]): API key for authentication. If not provided,
            will attempt to load from configuration
        api_url (Optional[str]): Base URL for API. If not provided,
            will attempt to load from configuration

    Raises:
        ValueError: If required API key or URL is not provided either through
            parameters or configuration

    Example:
        ```python
        class GoogleScholarAPI(APIClient):
            def __init__(self):
                super().__init__("google_scholar")
        ```
    """

    def __init__(
        self, name: str, api_key: Optional[str] = None, api_url: Optional[str] = None
    ):
        self.name = name
        capt_name = self.name.capitalize()
        logger.info(f"Initializing {capt_name} API client...")

        # Get API configuration based on name
        config = get_api_config()[self.name]

        # Look for API Key
        self.api_key = api_key or config["api_key"]
        if not self.api_key:
            err_msg = f"API key is required for {capt_name}. Set it in your .env file."
            logger.error(err_msg)
            raise ValueError(err_msg)
        else:
            logger.debug(f"API key found for {capt_name}")

        # Look for API URL
        self.api_url = api_url or config.get("api_url")
        if not self.api_url:
            raise ValueError(
                f"API URL is required for {capt_name}. Set it in your .env file."
            )
        else:
            logger.debug(f"API URL found for {capt_name}")

        # Fetch other settings
        self.timeout = config["timeout"]
        self.max_results_per_request = config["max_results_per_request"]
        logger.debug(f"Timeout: {self.timeout}")
        logger.debug(f"Max results per request: {self.max_results_per_request}")
        self.headers = {}

    @abstractmethod
    def search(self, query: str) -> List[Paper]:
        pass

    @abstractmethod
    def parse_results(self, entries: List[Dict[str, Any]]) -> List[Paper]:
        pass


def get_api_client(name: Literal["scopus"]) -> APIClient:
    """
    Get the API client for the specified name.

    Args:
        name: The name of the API client (e.g., 'scopus')

    Returns:
        An instance of the specified API client
    """

    if name == "scopus":
        # Conditional import to avoid circular import
        from literator.api.scopus import ScopusAPIClient

        return ScopusAPIClient()
    else:
        raise ValueError(f"Unknown API client: {name}")
