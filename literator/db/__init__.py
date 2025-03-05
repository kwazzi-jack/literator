"""Database module for Literator.

This module provides database models and handlers for managing academic papers,
authors, and keywords. It includes functionality for initializing the database,
saving and retrieving papers, and getting database statistics.

Models:
    Paper: Represents an academic paper with its metadata
    Author: Represents an author of academic papers
    Keyword: Represents keywords associated with papers
    PaperAuthorLink: Represents the many-to-many relationship between papers and authors

Functions:
    init_db: Initialize the database schema
    save_papers_to_db: Save paper records to the database
    get_stats: Retrieve statistics about the database contents
    get_papers_from_db: Query and retrieve papers from the database
"""

# Expose module
from literator.db.models import Paper, Author, Keyword, PaperAuthorLink
from literator.db.handler import (
    init_db,
    save_papers_to_db,
    get_stats,
    get_papers_from_db,
)

__all__ = [
    "Paper",
    "Author",
    "Keyword",
    "PaperAuthorLink",
    "init_db",
    "save_papers_to_db",
    "get_stats",
    "get_papers_from_db",
]
