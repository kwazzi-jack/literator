import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime, timezone
from dataclasses import asdict
from typing import Dict, Literal, Optional, List

import click
from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.table import Table

from models import Paper
from api_clients import APIClient, get_api_client
from config import VAULT_PATH, REQUESTS_DIR
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


def get_timestamp() -> str:
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
                total_papers = get_paper_count()
                logger.info(f"Database now contains {total_papers} papers")
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
    source: Optional[Literal["scopus"]] = None,
    start_year: Optional[int] = None,
    end_year: Optional[int] = None,
    limit: int = 100,
    print_results: bool = True,
) -> List[Paper]:
    """Query the database for papers"""
    try:
        papers = get_papers_from_db(query, source, start_year, end_year, limit)
        logger.info(f"Found {len(papers)} papers in database")

        if print_results:
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

    except Exception as e:
        logger.error(f"Error querying database: {str(e)}")


# Click commands
@click.group(name="fetch")
def fetch_cli():
    """Fetch and manage papers for literature review"""
    pass


@fetch_cli.command("scopus")
@click.option("--query", type=str, required=True, help="Search query")
@click.option("--start-year", type=int, help="Start year for filtering results")
@click.option("--end-year", type=int, help="End year for filtering results")
@click.option(
    "--max-results", type=int, default=100, help="Maximum number of results to fetch"
)
@click.option("--no-db", is_flag=True, help="Don't save results to the database")
@click.option("--no-json", is_flag=True, help="Don't save results to the json")
def fetch_scopus_command(
    query: str,
    start_year: int,
    end_year: int,
    max_results: int,
    no_db: bool,
    no_json: bool,
):
    """Fetch papers from APIs"""

    # Fetch papers
    fetch_papers(
        client_name="scopus",
        query=query,
        start_year=start_year,
        end_year=end_year,
        max_results=max_results,
        save_to_db=not no_db,
        save_to_json=not no_json,
    )


@fetch_cli.command("results")
@click.option("--file", help="Specific results file to view (defaults to most recent)")
@click.option("--count", type=int, default=10, help="Number of papers to display")
def fetch_results_command(file, count):
    """View results from a recent Scopus API call"""
    try:
        # Find the most recent results file if not specified
        if not file:
            if not REQUESTS_DIR.exists():
                console.print("[yellow]No requests directory found.[/yellow]")
                return

            files = list(REQUESTS_DIR.glob("scopus_*.json"))
            if not files:
                console.print("[yellow]No recent search results found.[/yellow]")
                return

            # Sort by modification time, newest first
            files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            file = str(files[0])

        # Convert to Path if string
        if isinstance(file, str):
            file_path = Path(file)
        else:
            file_path = file

        if not file_path.exists():
            console.print(f"[red]File not found: {file_path}[/red]")
            return

        # Read the JSON file
        with open(file_path, "r", encoding="utf-8") as f:
            results_dict: Dict[str, str] = json.load(f)

        # Load results values
        query = results_dict.get("query", "Unknown")
        timestamp = results_dict.get("timestamp")
        if timestamp:
            timestamp_str = datetime.strptime(timestamp, "%Y%m%d_%H%M%S")
            timestamp = timestamp_str.strftime("%Y-%m-%d %H:%M:%S")
        else:
            timestamp = "Unknown"
        start_year = results_dict.get("start_year")
        end_year = results_dict.get("end_year")
        source = results_dict.get("source", "Unknown")
        papers_dict = results_dict.get("papers", {})

        # Display basic info with colors
        console.print(
            Panel(
                "\n".join(
                    [
                        f"[bold blue]Request file:[/bold blue] [cyan]{file_path}[/cyan]",
                        f"[bold blue]Total papers:[/bold blue] [green]{len(papers_dict)}[/green]",
                        f"[bold blue]Query:[/bold blue] '[yellow]{query}[/yellow]'",
                        f"[bold blue]Timestamp:[/bold blue] [magenta]{timestamp}[/magenta]",
                        f"[bold blue]Source:[/bold blue] [yellow]{source.capitalize()}[/yellow]",
                        f"[bold blue]Start year:[/bold blue] [green]{start_year}[/green]",
                        f"[bold blue]End year:[/bold blue] [green]{end_year}[/green]",
                    ]
                ),
                title="Request Summary",
                border_style="bright_blue",
            )
        )

        # Show papers in a table with improved styling and word wrap
        table = Table(
            title="Papers Summary",
            title_style="bold blue",
            header_style="bold cyan",
            border_style="bright_blue",
            show_lines=True,  # Add lines between rows for better readability
        )
        table.add_column("#", style="magenta", width=3, justify="right")
        table.add_column("Title", style="bright_white", width=40, overflow="fold")
        table.add_column("Year", style="green", width=6, justify="center")
        table.add_column("Authors", width=30, style="yellow")
        table.add_column("Journal", width=30, style="blue", overflow="fold")

        for i, paper in enumerate(papers_dict[:count]):

            # Extract data from the paper dict
            title = paper.get("title", "Unknown")

            # Get year from publication date
            year = "?"
            if pub_date := paper.get("publication_date"):
                try:
                    year = pub_date.split("-")[0]  # Get year from YYYY-MM-DD
                except (IndexError, AttributeError):
                    pass

            # Format authors
            authors = "Unknown"
            if paper_authors := paper.get("authors", []):
                author_names = [a.get("name", "Unknown") for a in paper_authors[:2]]
                authors = ", ".join(author_names)
                if len(paper_authors) > 2:
                    authors += " et al."

            # Format journal - don't truncate, let rich handle wrapping
            journal = paper.get("journal", "Unknown")

            # Format number
            row_num = str(i + 1)
            if len(row_num) > 3:
                row_num = row_num[-3:]

            table.add_row(row_num, title, year, authors, journal)

        console.print(table)

        if len(papers_dict) > count:
            console.print(
                f"[dim italic](Showing {count} of {len(papers_dict)} papers)[/dim italic]"
            )

    except Exception as e:
        logger.error(f"Error displaying results: {str(e)}")
        console.print(f"[red]Error displaying results: {str(e)}[/red]")


@click.group(name="papers")
def papers_cli():
    """Manage papers in the database"""
    pass


@papers_cli.command("init_db")
def init_command():
    """Initialize the database"""
    init_db()


@papers_cli.command("query")
@click.option("--query", help="Search term for titles, abstracts, or keywords")
@click.option("--source", help="Filter by source (e.g., scopus, arxiv)")
@click.option("--start-year", type=int, help="Start year for filtering results")
@click.option("--end-year", type=int, help="End year for filtering results")
@click.option("--limit", type=int, default=100, help="Maximum number of results")
@click.option("--print-results", is_flag=True, help="Print results to console")
def query_command(query, source, start_year, end_year, limit, print_results):
    """Query the database for papers"""
    papers: List[Paper] = query_database(
        query=query,
        source=source,
        start_year=start_year,
        end_year=end_year,
        limit=limit,
        print_results=print_results,
    )


@papers_cli.command("stats")
def stats_command():
    """Display database statistics"""
    display_stats()
