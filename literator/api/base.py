from abc import ABC, abstractmethod
from datetime import datetime
from typing import Iterable, Iterator, List, Dict, Any, Literal, Optional, Union

from literator.config import get_api_config
from literator.db.models import Paper
from literator.utils import get_logger, format_phrase, str_to_datetime

logger = get_logger(__name__)


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


class APIQuery:
    def __init__(self):
        self.terms: List[str] = []
        self.constraints: List[str] = []
        self.inclusions: List[str] = []
        self.exclusion: List[str] = []
        self.before_date: Optional[datetime] = None
        self.after_year: Optional[datetime] = None

    def add_term(self, term: str, exact: bool = False):
        """
        Adds a search term to the list of terms.
        Args:
            term (str): The search term to be added.
            exact (bool, optional): If True, the term will be treated as an exact phrase match.
                Defaults to False.
        Example:
            >>> searcher.add_term("machine learning")  # Adds flexible match term
            >>> searcher.add_term("deep learning", exact=True)  # Adds exact match term
        """
        phrase = format_phrase(term, exact)
        if phrase not in self.terms:
            self.terms.append(phrase)

    def add_terms(
        self,
        terms: Iterator[str],
        exact: Union[bool, Iterable[bool]] = False,
    ):
        """
        Add multiple search terms to the search criteria.
        Parameters
        ----------
        terms : Iterator[str]
            A collection of search terms to add.
        terms : Union[bool, Iterable[bool]], optional
            Either a single boolean value applied to all terms, or a list of boolean values
            indicating whether each corresponding term should be matched exactly.
            If a single boolean is provided, it will be applied to all terms.
            Defaults to False.
        Examples
        --------
        >>> searcher.add_terms(['term1', 'term2'], exact=True)  # Both terms exact match
        >>> searcher.add_terms(['term1', 'term2'], exact=[True, False])  # First term exact, second fuzzy
        """
        # Exact is a single boolean
        if isinstance(exact, bool):
            for term in terms:
                self.add_term(term, exact)

        # Exact is a collection of booleans
        elif isinstance(exact, Iterable):
            for term, ex in zip(terms, exact):
                self.add_term(term, ex)

    def add_inclusion(self, term: str, exact: bool = False):
        """Add a term to the inclusion list.

        Args:
            term (str): The term to be added to the inclusion list.
            exact (bool, optional): If True, the term will be treated as an exact phrase match.
                Defaults to False.
        Example:
            >>> searcher.add_inclusion("term1")  # Adds term1 to inclusions
            >>> searcher.add_inclusion("term2", exact=True)  # Adds term2 as exact match
        """
        phrase = format_phrase(term, exact)
        if phrase not in self.inclusions:
            self.inclusions.append(phrase)

    def add_inclusions(
        self, terms: Iterable[str], exact: Union[bool, Iterable[bool]] = False
    ):
        """Add multiple terms to the inclusion list.

        Args:
            terms (Iterable[str]): A collection of terms to be added to the inclusion list.
            exact (Union[bool, Iterable[bool]], optional): Either a single boolean value applied
                to all terms, or a list of boolean values indicating whether each corresponding
                term should be matched exactly. Defaults to False.
        Example:
            >>> searcher.add_inclusions(["term1", "term2"], exact=True)  # Both terms exact match
            >>> searcher.add_inclusions(["term1", "term2"], exact=[True, False])  # First term exact, second fuzzy
        """
        if isinstance(exact, bool):
            for term in terms:
                self.add_inclusion(term, exact)
        elif isinstance(exact, Iterable):
            for term, ex in zip(terms, exact):
                self.add_inclusion(term, ex)

    def add_exclusion(self, term: str, exact: bool = False):
        """Add a term to the exclusion list.

        Args:
            term (str): The term to be added to the exclusion list.
            exact (bool, optional): If True, the term will be treated as an exact phrase match.
                Defaults to False.
        Example:
            >>> searcher.add_exclusion("term1")  # Adds term1 to exclusions
            >>> searcher.add_exclusion("term2", exact=True)  # Adds term2 as exact match
        """
        phrase = format_phrase(term, exact)
        if phrase not in self.exclusion:
            self.exclusion.append(phrase)

    def add_exclusions(
        self, terms: Iterable[str], exact: Union[bool, Iterable[bool]] = False
    ):
        """Add multiple terms to the exclusion list.

        Args:
            terms (Iterable[str]): A collection of terms to be added to the exclusion list.
            exact (Union[bool, Iterable[bool]], optional): Either a single boolean value applied
                to all terms, or a list of boolean values indicating whether each corresponding
                term should be matched exactly. Defaults to False.
        Example:
            >>> searcher.add_exclusions(["term1", "term2"], exact=True)  # Both terms exact match
            >>> searcher.add_exclusions(["term1", "term2"], exact=[True, False])  # First term exact, second fuzzy
        """
        if isinstance(exact, bool):
            for term in terms:
                self.add_exclusion(term, exact)
        elif isinstance(exact, Iterable):
            for term, ex in zip(terms, exact):
                self.add_exclusion(term, ex)

    def add_constraint(self, constraint: str):
        """Add a constraint to the query.

        Args:
            constraint (str): The constraint to be added.
        Example:
            >>> searcher.add_constraint("year > 2020")  # Adds a year constraint
        """
        phrase = format_phrase(constraint, exact=True)
        if phrase not in self.constraints:
            self.constraints.append(phrase)

    def before(self, date: Union[int, str, datetime]):
        """Set the start year for the query.

        Args:
            date (int): The starting year for the query.
        Example:
            >>> searcher.before(2020)  # Sets start year to 2020
        """
        # Date is year, set to 1st
        if isinstance(date, int):
            self.before_date = datetime(year=date, month=1, day=1)

        # Date is string, convert to datetime
        elif isinstance(date, str):
            self.before_date = str_to_datetime(date)

        # Date is datetime
        elif isinstance(date, datetime):
            self.before_date = date

        # Date is none
        elif date is None:
            self.before_date = None

        # Date is other
        else:
            msg = f"Invalid date format {type(date)}. Expected int, str, or datetime."
            logger.error(msg)
            raise ValueError(msg)

    def after(self, date: Optional[Union[int, str, datetime]] = None):
        """Set the end year for the query.

        Args:
            date (Optional[Union[int, str, datetime]]): The ending year for the query.
            If int, interpreted as year (set to January 1st).
            If str, parsed to datetime. If datetime, used directly.
            If None, no date filtering.
        Example:
            >>> searcher.after(2020)  # Sets end year to 2020
        """


        # Date is year, set to 1st
        if isinstance(date, int):
            self.after_date = datetime(year=date, month=1, day=1)

        # Date is string, convert to datetime
        elif isinstance(date, str):
            self.after_date = str_to_datetime(date)

        # Date is datetime
        elif isinstance(date, datetime):
            self.after_date = date

        # Date is none
        elif date is None:
            self.after_date = None

        # Date is other
        else:
            msg = f"Invalid date format {type(date)}. Expected int, str, or datetime."
            logger.error(msg)
            raise ValueError(msg)

    def add_constraints(self, constraints: Iterable[str]):
        """Add multiple constraints to the query.

        Args:
            constraints (Iterable[str]): A collection of constraints to be added.
        Example:
            >>> searcher.add_constraints(["year > 2020", "author = 'Smith'"])  # Adds multiple constraints
        """
        for constraint in constraints:
            self.add_constraint(constraint)

    def remove_term(self, term: str):
        """Remove a term from the query.

        Args:
            term (str): The term to be removed from the query.
        Example:
            >>> searcher.remove_term("machine learning")  # Removes flexible match term
            >>> searcher.remove_term("deep learning")  # Removes exact match term
        """

        # Get exact form
        exact_term = format_phrase(term, exact=True)

        # Remove term from terms
        if term in self.terms:
            self.terms.remove(term)

        # Remove exact term from terms
        elif exact_term in self.terms:
            self.terms.remove(exact_term)

    def remove_terms(self, terms: Iterable[str]):
        """Remove all terms in the list from the query.

        Args:
            terms (Iterable[str]): A collection of terms to be removed from the query.
        Example:
            >>> searcher.remove_terms(["term1", "term2"])  # Removes both terms
            >>> searcher.remove_terms(["term3"])  # Removes term3
        """
        for term in terms:
            self.remove_term(term)

    def remove_inclusion(self, term: str):
        """Remove a term from the inclusion list.

        Args:
            term (str): The term to be removed from the inclusion list.
        Example:
            >>> searcher.remove_inclusion("term1")  # Removes term1 from inclusions
        """
        # Get exact form
        exact_term = format_phrase(term, exact=True)

        # Remove term from inclusions
        if term in self.inclusions:
            self.inclusions.remove(term)

        # Remove exact term from inclusions
        elif exact_term in self.inclusions:
            self.inclusions.remove(exact_term)

    def remove_inclusions(self, terms: Iterable[str]):
        """Remove all terms in the list from the inclusion list.

        Args:
            terms (Iterable[str]): A collection of terms to be removed from the inclusion list.
        Example:
            >>> searcher.remove_inclusions(["term1", "term2"])  # Removes both terms
            >>> searcher.remove_inclusions(["term3"])  # Removes term3
        """
        for term in terms:
            self.remove_inclusion(term)

    def remove_exclusion(self, term: str):
        """Remove a term from the exclusion list.

        Args:
            term (str): The term to be removed from the exclusion list.
        Example:
            >>> searcher.remove_exclusion("term1")  # Removes term1 from exclusions
        """
        # Get exact form
        exact_term = format_phrase(term, exact=True)

        # Remove term from exclusions
        if term in self.exclusion:
            self.exclusion.remove(term)

        # Remove exact term from exclusions
        elif exact_term in self.exclusion:
            self.exclusion.remove(exact_term)

    def remove_exclusions(self, terms: Iterable[str]):
        """Remove all terms in the collection from the exclusion list.

        Args:
            terms (Iterable[str]): A collection of terms to be removed from the exclusion list.
        Example:
            >>> searcher.remove_exclusions(["term1", "term2"])  # Removes both terms
            >>> searcher.remove_exclusions(["term3"])  # Removes term3
        """
        for term in terms:
            self.remove_exclusion(term)

    def remove_constraint(self, constraint: str):
        """Remove a constraint from the query.

        Args:
            constraint (str): The constraint to be removed.
        Example:
            >>> searcher.remove_constraint("year > 2020")  # Removes year constraint
        """
        if constraint in self.constraints:
            self.constraints.remove(constraint)

    def remove_constraints(self, constraints: Iterable[str]):
        """Remove all constraints in the list from the query.

        Args:
            constraints (Iterable[str]): A collection of constraints to be removed.
        Example:
            >>> searcher.remove_constraints(["year > 2020", "author = 'Smith'"])  # Removes both constraints
        """
        for constraint in constraints:
            self.remove_constraint(constraint)

    def remove(self, terms: Union[str, Iterable[str]]):
        """Remove a term or collection of terms from the query.

        Args:
            term (str | List[str]): A single term or a list of terms to be removed.
        Example:
            >>> searcher.remove("term1")  # Removes single term
            >>> searcher.remove(["term2", "term3"])  # Removes multiple terms
        """

        # Single term to remove
        if isinstance(terms, str):
            self.remove_term(terms)
            self.remove_inclusion(terms)
            self.remove_exclusion(terms)

        # Multiple terms to remove
        elif isinstance(terms, Iterable):
            self.remove_terms(terms)
            self.remove_inclusions(terms)
            self.remove_exclusions(terms)


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
