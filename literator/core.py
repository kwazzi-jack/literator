"""Core functionality for the litreview tool."""

import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Literal, Optional

from rich.console import Console
from rich.logging import RichHandler

from literator.api import APIClient, get_api_client
from .config import REQUESTS_DIR
from literator.db import (
    get_papers_from_db,
    init_db,
    save_papers_to_db,
)
from literator.db import Paper

# Configure logging with Rich
console = Console()
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(console=console, rich_tracebacks=True)],
)
logger = logging.getLogger("litreview")


# Fallback logging configuration if Rich is not available
def setup_basic_logging():
    """Setup basic logging if Rich logging fails"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    return logging.getLogger("litreview")


def get_timestamp() -> str:
    """Get the current timestamp in a format suitable for filenames."""
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def save_json(
    papers: List[Paper],
    query: str,
    timestamp: str,
    source: Literal["scopus"],
    start_year: Optional[int] = None,
    end_year: Optional[int] = None,
):
    """Save papers to a JSON file."""
    # Convert Pydantic models to dictionaries
    papers_dict = []
    for paper in papers:
        try:
            # Handle both Pydantic models and dataclasses
            if hasattr(paper, "dict"):
                paper_dict = paper.model_dump()
            else:
                from dataclasses import asdict

                paper_dict = asdict(paper)

            # Convert datetime to string for JSON serialization
            if paper_dict.get("publication_date"):
                paper_dict["publication_date"] = paper_dict[
                    "publication_date"
                ].strftime("%Y-%m-%d")
            papers_dict.append(paper_dict)
        except Exception as e:
            logger.error(f"Error processing paper for JSON: {str(e)}")

    # Construct outer dictionary
    results_dict = {
        "papers": papers_dict,
        "count": len(papers_dict),
        "query": query,
        "timestamp": timestamp,
        "start_year": start_year,
        "end_year": end_year,
        "source": source,
    }

    # Construct output path
    output_path = REQUESTS_DIR / f"{source}_{timestamp}.json"

    # Create directory if it doesn't exist
    output_path.parent.mkdir(exist_ok=True, parents=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results_dict, f, ensure_ascii=False, indent=4)

    logger.info(f"Saved {len(papers)} papers to {output_path}")


def fetch_papers(
    client_name: Literal["scopus"],
    query: str,
    start_year: Optional[int] = None,
    end_year: Optional[int] = None,
    max_results: int = 100,
    save_to_db: bool = True,
    save_to_json: bool = True,
) -> List[Paper]:
    """
    Fetch papers from Scopus API.

    Args:
        client_name: The API client to use
        query: Search query
        start_year: Optional start year for filtering
        end_year: Optional end year for filtering
        max_results: Maximum number of results to fetch
        save_to_db: Whether to save results to the database
        save_to_json: Whether to save results to JSON file

    Returns:
        List of Paper objects
    """
    logger.info(f"Searching for: {query}")
    logger.info(f"Year range: {start_year or 'any'} to {end_year or 'any'}")

    # Get relevant API client
    client: APIClient = get_api_client(client_name)
    logger.info(f"Using {client_name} API client")

    # Get timestamp
    timestamp = get_timestamp()
    logger.info(f"Timestamp: {timestamp}")

    # Initialize Scopus client
    try:
        # Search Scopus
        papers = client.search(
            query=query,
            start_year=start_year,
            end_year=end_year,
            max_results=max_results,
        )

        logger.info(f"Found {len(papers)} papers")

        # Save results to database if requested
        if save_to_db:
            try:
                init_db()  # Ensure database is initialized
                added_count = save_papers_to_db(papers)
                logger.info(f"Added {added_count} new papers to the database")
            except Exception as e:
                logger.error(f"Error saving to database: {str(e)}")

        # Save results to JSON if output file is specified
        if save_to_json:
            try:
                save_json(
                    papers,
                    query,
                    timestamp,
                    client.name,
                    start_year,
                    end_year,
                )
                logger.info("Saved results to JSON file")
            except Exception as e:
                logger.error(f"Error saving to JSON: {str(e)}")

        return papers

    except Exception as e:
        logger.exception(f"Error during paper fetching: {str(e)}")
        return []


def query_database(
    query: str = None,
    source: Optional[Literal["scopus"]] = None,
    start_year: Optional[int] = None,
    end_year: Optional[int] = None,
    limit: int = 100,
    print_results: bool = True,
) -> List[Paper]:
    """
    Query the database for papers

    Args:
        query: Search term for titles, abstracts, or keywords
        source: Filter by source (e.g., scopus, arxiv)
        start_year: Start year for filtering results
        end_year: End year for filtering results
        limit: Maximum number of results to return
        print_results: Whether to print results to console

    Returns:
        List of Paper objects
    """
    try:
        papers = get_papers_from_db(query, source, start_year, end_year, limit)
        logger.info(f"Found {len(papers)} papers in database")

        if print_results:
            from literator.display import display_query_results

            display_query_results(papers)

        return papers

    except Exception as e:
        logger.error(f"Error querying database: {str(e)}")
        return []
