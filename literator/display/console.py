"""Display functions for the litreview tool."""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from literator.utils.logging import get_logger
from literator.config import REQUESTS_DIR
from literator.db import init_db, Paper, Author

# Setup console for rich output
console = Console()
logger = get_logger(__name__)


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


def display_query_results(papers: List[Paper]):
    """Display query results in a nicely formatted table"""
    # Display results in a table
    table = Table(title="Search Results")
    table.add_column("Title")
    table.add_column("Year")
    table.add_column("Authors")
    table.add_column("Source")

    for paper in papers[:10]:  # Show first 10 papers
        pub_year = paper.publication_date.year if paper.publication_date else "Unknown"
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


def display_request_results(file: Optional[str] = None, count: int = 10):
    """View results from a recent API call"""
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
            results_dict: Dict[str, Any] = json.load(f)

        # Load results values
        query: str = results_dict.get("query", "Unknown")
        timestamp: Optional[str] = results_dict.get("timestamp")
        if timestamp:
            timestamp_str = datetime.strptime(timestamp, "%Y%m%d_%H%M%S")
            timestamp = timestamp_str.strftime("%Y-%m-%d %H:%M:%S")
        else:
            timestamp = "Unknown"
        start_year: str = results_dict.get("start_year", "N/A")
        end_year: str = results_dict.get("end_year", "N/A")
        source: str = results_dict.get("source", "Unknown")

        papers_list = results_dict.get("papers", [])
        papers: List[Paper] = [Paper(**paper_dict) for paper_dict in papers_list]

        # Display basic info with colors
        console.print(
            Panel(
                "\n".join(
                    [
                        f"[bold blue]Request file:[/bold blue] [cyan]{file_path}[/cyan]",
                        f"[bold blue]Total papers:[/bold blue] [green]{len(papers)}[/green]",
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

        for i, paper in enumerate(papers[:count]):
            # Extract data from the paper dict
            title = paper.title or "Unknown"

            # Get year from publication date
            year = "?"
            if paper.publication_date:
                pub_date = str(paper.publication_date)
                try:
                    year = pub_date.split("-")[0]  # Get year from YYYY-MM-DD
                except (IndexError, AttributeError):
                    pass

            # Format authors
            authors = "Unknown"
            paper_authors: List[Author] = paper.authors or []
            if paper_authors:
                author_names = [
                    author.name or "Unknown" for author in paper_authors[:2]
                ]
                authors = ", ".join(author_names)
                if len(paper_authors) > 2:
                    authors += " et al."

            # Format journal - don't truncate, let rich handle wrapping
            journal: str = paper.journal or "Unknown"

            # Format number
            row_num = str(i + 1)
            if len(row_num) > 3:
                row_num = row_num[-3:]

            table.add_row(row_num, title, year, authors, journal)

        console.print(table)

        if len(papers) > count:
            console.print(
                f"[dim italic](Showing {count} of {len(papers)} papers)[/dim italic]"
            )

    except Exception as e:
        logger.error(f"Error displaying results: {str(e)}")
        console.print(f"[red]Error displaying results: {str(e)}[/red]")
