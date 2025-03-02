from abc import ABC, abstractmethod
import requests
from datetime import datetime
import logging
from typing import List, Dict, Any, Optional

from models import Paper, Author
from config import get_api_config

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


class ScopusClient(APIClient):
    """
    A client for interacting with the Scopus API to fetch academic papers.
    This class extends the APIClient base class and provides specific functionality
    for searching and retrieving papers from Scopus's database. It handles API
    authentication, request formatting, response parsing, and pagination.
    Attributes:
        headers (dict): HTTP headers including API key and accept type for JSON
        max_results_per_request (int): Maximum number of results per API request
        timeout (int): Request timeout in seconds
    Args:
        api_key (Optional[str]): API key for authentication. If not provided,
            will attempt to load from configuration
        api_url (Optional[str]): Base URL for API. If not provided,
            will attempt to load from configuration
    Raises:
        ValueError: If required API key or URL is not provided either through
            parameters or configuration
    Example:
        ```
        client = ScopusClient(api_key="your-api-key")
        papers = client.search("artificial intelligence", start_year=2020, max_results=100)
        ```
    """

    def __init__(self, api_key: Optional[str] = None, api_url: Optional[str] = None):
        # Initialize the Client class
        super().__init__(name="scopus", api_key=api_key, api_url=api_url)

        # Scopus related settings
        self.headers["X-ELS-APIKey"] = self.api_key
        self.headers["Accept"] = "application/json"

    def search(
        self,
        query: str,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
        max_results: int = 100,
    ) -> List[Paper]:
        """
        Search Scopus for papers matching the query.

        Args:
            query (str): The search query
            start_year (Optional[int], optional): Start year for filtering results. Defaults to None.
            end_year (Optional[int], optional): End year for filtering results. Defaults to None.
            max_results (int, optional): Maximum number of results to return. Defaults to 100.

        Returns:
            List[Paper]: A list of Paper objects matching the search criteria
        """
        params = {
            "query": query,
            "count": min(max_results, self.max_results_per_request),
            "start": 0,
            "view": "COMPLETE",  # Get complete record information
        }

        # Add date range if specified
        date_restrictions = []
        if start_year:
            date_restrictions.append(f"PUBYEAR > {start_year - 1}")
        if end_year:
            date_restrictions.append(f"PUBYEAR < {end_year + 1}")

        if date_restrictions:
            params["query"] += " AND " + " AND ".join(date_restrictions)

        all_papers = []
        total_fetched = 0

        try:
            while total_fetched < max_results:
                params["start"] = total_fetched

                logger.info(
                    f"Fetching results {total_fetched + 1}-{total_fetched + params['count']}..."
                )
                response = requests.get(
                    self.api_url,
                    headers=self.headers,
                    params=params,
                    timeout=self.timeout,
                )
                response.raise_for_status()

                data = response.json()

                # Check if there are results
                if (
                    "search-results" not in data
                    or "entry" not in data["search-results"]
                ):
                    logger.warning("No results found in Scopus response")
                    break

                entries = data["search-results"]["entry"]
                if not entries:
                    break

                # Parse results
                batch_papers = self.parse_results(entries)
                all_papers.extend(batch_papers)

                total_fetched += len(entries)

                # Check if we've reached the end
                if len(entries) < params["count"]:
                    break

            logger.info(f"Total papers fetched from Scopus: {len(all_papers)}")
            return all_papers

        except requests.RequestException as e:
            logger.error(f"Error fetching from Scopus API: {e}")
            return all_papers

    def parse_results(self, entries: List[Dict[str, Any]]) -> List[Paper]:
        """Parse Scopus API results into Paper objects."""
        papers = []

        for entry in entries:
            try:
                # Extract authors
                authors = []
                if "author" in entry:
                    author_list = entry["author"]
                    if isinstance(author_list, list):
                        for author_data in author_list:
                            name = author_data.get("authname", "")
                            affiliation = author_data.get("affilname", None)
                            authors.append(Author(name=name, affiliation=affiliation))
                    else:
                        # Single author
                        name = author_list.get("authname", "")
                        affiliation = author_list.get("affilname", None)
                        authors.append(Author(name=name, affiliation=affiliation))

                # Parse publication date
                pub_date = None
                if "prism:coverDate" in entry:
                    try:
                        pub_date = datetime.strptime(
                            entry["prism:coverDate"], "%Y-%m-%d"
                        )
                    except (ValueError, TypeError):
                        logger.error(
                            f"Error parsing publication date: {entry['prism:coverDate']}"
                        )
                        pub_date = None

                # Extract keywords
                keywords = []
                if "authkeywords" in entry and entry["authkeywords"]:
                    keywords = [
                        kw.strip()
                        for kw in entry["authkeywords"].split(",")
                        if kw.strip()
                    ]

                # Create Paper object using Pydantic model
                paper = Paper(
                    title=entry.get("dc:title", ""),
                    authors=authors,
                    abstract=entry.get("dc:description", None),
                    publication_date=pub_date,
                    journal=entry.get("prism:publicationName", None),
                    doi=entry.get("prism:doi", None),
                    url=entry.get("prism:url", None),
                    citations=int(entry.get("citedby-count", "0")),
                    keywords=keywords,
                    source="scopus",
                    source_id=entry.get("dc:identifier", None),
                    metadata={
                        "scopus_id": (
                            entry.get("dc:identifier", "").replace("SCOPUS_ID:", "")
                            if "dc:identifier" in entry
                            else None
                        ),
                        "eid": entry.get("eid", None),
                    },
                )

                # Extract author UUIDs
                paper.author_uuids = [author.uuid for author in authors]

                # Add paper UUIDs to authors
                for author in paper.authors:
                    author.paper_uuids.append(paper.uuid)

                papers.append(paper)
            except Exception as e:
                logger.error(f"Error parsing Scopus entry: {e}")
                continue

        return papers


def get_api_client(name: str) -> APIClient:
    """
    Get the API client for the specified name.

    Args:
        name: The name of the API client (e.g., 'scopus')

    Returns:
        An instance of the specified API client
    """
    if name == "scopus":
        return ScopusClient()
    else:
        raise ValueError(f"Unknown API client: {name}")
