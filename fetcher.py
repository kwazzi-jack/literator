import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any

import click
from rich.console import Console
from rich.logging import RichHandler
from rich.table import Table

from models import Paper
from scopus_client import ScopusClient
from config import VAULT_PATH, RESULTS_DIR
from db_handler import (
    init_db,
    save_papers_to_db,
    get_papers_from_db,
    get_paper_count,
    get_stats,
)

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


def save_results(papers: List[Paper], output_path: Path):
    """Save papers to a JSON file."""
    # Convert Pydantic models to dictionaries
    papers_dict = []
    for paper in papers:
        try:
            # Handle both Pydantic models and dataclasses
            if hasattr(paper, "dict"):
                paper_dict = paper.dict()
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

    # Create directory if it doesn't exist
    output_path.parent.mkdir(exist_ok=True, parents=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(papers_dict, f, ensure_ascii=False, indent=2)

    logger.info(f"Saved {len(papers)} papers to {output_path}")


def fetch_papers(
    query: str,
    start_year: Optional[int] = None,
    end_year: Optional[int] = None,
    max_results: int = 100,
    output_file: Optional[Path] = None,
    use_vault: bool = False,
    save_to_db: bool = True,
) -> List[Paper]:
    """
    Fetch papers from Scopus API.

    Args:
        query: Search query
        start_year: Optional start year for filtering
        end_year: Optional end year for filtering
        max_results: Maximum number of results to fetch
        output_file: File to save results to
        use_vault: Whether to save results to vault storage
        save_to_db: Whether to save results to the database

    Returns:
        List of Paper objects
    """
    logger.info(f"Searching for: {query}")
    logger.info(f"Year range: {start_year or 'any'} to {end_year or 'any'}")

    # Initialize Scopus client
    try:
        scopus_client = ScopusClient()

        # Search Scopus
        papers = scopus_client.search(
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
                total_papers = get_paper_count()
                logger.info(f"Database now contains {total_papers} papers")
            except Exception as e:
                logger.error(f"Error saving to database: {str(e)}")

        # Save results to JSON if output file is specified
        if output_file:
            save_results(papers, output_file)

        # Save to vault if requested
        if use_vault:
            # Make sure vault directory exists
            VAULT_PATH.mkdir(exist_ok=True, parents=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            query_slug = query.replace(" ", "_").replace("/", "_")[:50]
            vault_file = VAULT_PATH / f"scopus_{query_slug}_{timestamp}.json"
            save_results(papers, vault_file)
            logger.info(f"Also saved results to vault: {vault_file}")

        return papers

    except Exception as e:
        logger.exception(f"Error during paper fetching: {str(e)}")
        return []


def display_stats():
    """Display statistics about the database"""
    try:
        init_db()  # Ensure database is initialized
        stats = get_stats()

        console.print("\n[bold blue]Database Statistics[/bold blue]")
        console.print(f"Total papers: {stats['total_papers']}")
        console.print(f"Total authors: {stats['total_authors']}")

        # Display papers by source in a table
        table = Table(title="Papers by Source")
        table.add_column("Source")
        table.add_column("Count")

        for source, count in stats["papers_by_source"].items():
            table.add_row(source, str(count))

        console.print(table)

        # Display top keywords
        console.print("\n[bold]Top Keywords:[/bold]")
        for kw, count in stats["top_keywords"].items():
            console.print(f"  {kw}: {count}")

    except Exception as e:
        logger.error(f"Error getting statistics: {str(e)}")


def query_database(
    query: str = None,
    source: str = None,
    start_year: Optional[int] = None,
    end_year: Optional[int] = None,
    limit: int = 100,
    output_file: Optional[str] = None,
):
    """Query the database for papers"""
    try:
        papers = get_papers_from_db(query, source, start_year, end_year, limit)
        logger.info(f"Found {len(papers)} papers in database")

        # Display results in a table
        table = Table(title="Search Results")
        table.add_column("Title")
        table.add_column("Year")
        table.add_column("Authors")
        table.add_column("Source")

        for paper in papers[:10]:  # Show first 10 papers
            pub_year = (
                paper.publication_date.year if paper.publication_date else "Unknown"
            )
            authors = ", ".join([a.name for a in paper.authors[:3]])
            if len(paper.authors) > 3:
                authors += " et al."
            table.add_row(
                paper.title[:50] + "..." if len(paper.title) > 50 else paper.title,
                str(pub_year),
                authors,
                paper.source,
            )

        console.print(table)

        if len(papers) > 10:
            console.print(f"[italic](Showing 10 of {len(papers)} results)[/italic]")

        # Save to file if requested
        if output_file:
            save_results(papers, Path(output_file))

    except Exception as e:
        logger.error(f"Error querying database: {str(e)}")


def simple_fetch(
    query: str,
    start_year: Optional[int] = None,
    end_year: Optional[int] = None,
    max_results: int = 100,
    output_file: Optional[str] = None,
) -> List[Paper]:
    """
    Simplified version of fetch_papers for direct script usage.
    Does not use database or vault features.

    Args:
        query: Search query
        start_year: Optional start year for filtering
        end_year: Optional end year for filtering
        max_results: Maximum number of results to fetch
        output_file: File to save results to
    """
    output_path = Path(output_file) if output_file else None
    return fetch_papers(
        query=query,
        start_year=start_year,
        end_year=end_year,
        max_results=max_results,
        output_file=output_path,
        use_vault=False,
        save_to_db=False,
    )


# Click commands


@click.group()
def cli():
    """Fetch and manage papers for literature review"""
    pass


@cli.command("fetch")
@click.option("--query", required=True, help="Search query")
@click.option("--start-year", type=int, help="Start year for filtering results")
@click.option("--end-year", type=int, help="End year for filtering results")
@click.option(
    "--max-results", type=int, default=100, help="Maximum number of results to fetch"
)
@click.option("--output", type=str, help="Output file path (JSON)")
@click.option("--use-vault", is_flag=True, help="Save results to vault storage")
@click.option("--no-db", is_flag=True, help="Don't save results to the database")
def fetch_command(query, start_year, end_year, max_results, output, use_vault, no_db):
    """Fetch papers from APIs"""
    # Generate default output filename if none provided
    output_file = None
    if output:
        output_file = Path(output)
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        query_slug = query.replace(" ", "_").replace("/", "_")[:50]
        output_file = RESULTS_DIR / f"scopus_{query_slug}_{timestamp}.json"

    # Fetch papers
    fetch_papers(
        query=query,
        start_year=start_year,
        end_year=end_year,
        max_results=max_results,
        output_file=output_file,
        use_vault=use_vault,
        save_to_db=not no_db,
    )


@cli.command("query")
@click.option("--query", help="Search term for titles, abstracts, or keywords")
@click.option("--source", help="Filter by source (e.g., scopus, arxiv)")
@click.option("--start-year", type=int, help="Start year for filtering results")
@click.option("--end-year", type=int, help="End year for filtering results")
@click.option("--limit", type=int, default=100, help="Maximum number of results")
@click.option("--output", help="Output file path (JSON)")
def query_command(query, source, start_year, end_year, limit, output):
    """Query the database for papers"""
    query_database(
        query=query,
        source=source,
        start_year=start_year,
        end_year=end_year,
        limit=limit,
        output_file=output,
    )


@cli.command("stats")
def stats_command():
    """Display database statistics"""
    display_stats()


@cli.command("simple")
@click.option("--query", required=True, help="Search query")
@click.option("--start-year", type=int, help="Start year for filtering results")
@click.option("--end-year", type=int, help="End year for filtering results")
@click.option(
    "--max-results", type=int, default=100, help="Maximum number of results to fetch"
)
@click.option("--output", help="Output file path (JSON)")
def simple_command(query, start_year, end_year, max_results, output):
    """Simple paper fetch without database/vault features"""
    # Generate default output filename if none provided
    if not output:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        query_slug = query.replace(" ", "_").replace("/", "_")[:50]
        output = f"{RESULTS_DIR}/scopus_{query_slug}_{timestamp}.json"

    # Simple fetch (mimicking old fetch_papers.py behavior)
    simple_fetch(
        query=query,
        start_year=start_year,
        end_year=end_year,
        max_results=max_results,
        output_file=output,
    )


def main():
    """Main entry point for the CLI"""
    try:
        cli()
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.exception(f"Unexpected error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
