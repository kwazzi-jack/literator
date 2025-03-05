"""Command line interface for the litreview tool."""

import click

from literator.utils.logging import setup_logging
from literator.core import fetch_papers, query_database
from literator.display import display_stats
from literator.db import init_db


@click.group()
@click.option("--debug", is_flag=True, help="Enable debug logging")
@click.pass_context
def main(ctx, debug):
    """Literature review management tool."""
    # Initialize logging early
    logger = setup_logging(debug=debug)

    # Store debug setting in context for subcommands
    ctx.ensure_object(dict)
    ctx.obj["DEBUG"] = debug
    ctx.obj["LOGGER"] = logger


# Fetch command group
@main.group(name="fetch")
@click.pass_context
def fetch_cli(ctx):
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
    """Fetch papers from Scopus API"""
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
@click.option(
    "--file", type=str, help="Specific results file to view (defaults to most recent)"
)
@click.option("--count", type=int, default=10, help="Number of papers to display")
def fetch_results_command(file: str, count: int):
    """View results from a recent Scopus API call"""
    # display_results(file, count)


# Papers command group
@main.group(name="papers")
@click.pass_context
def papers_cli(ctx):
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
    query_database(
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


if __name__ == "__main__":
    main()
