# Expose module
from literator.db.models import Paper, Author, Keyword, PaperAuthorLink
from literator.db.handler import (
    init_db,
    save_papers_to_db,
    get_papers_from_db,
)

__all__ = [
    "Paper",
    "Author",
    "Keyword",
    "PaperAuthorLink",
    "init_db",
    "save_papers_to_db",
    "get_papers_from_db",
]
