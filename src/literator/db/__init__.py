# Expose classes
from literator.db.models import Paper, Author, Keyword, PaperAuthorLink

# Expose functions
from literator.db.handler import (
    init_db,
    save_papers_to_db,
    get_papers_from_db,
    get_paper_by_doi,
    get_paper_by_uuid,
    get_papers_by_author,
    get_papers_by_keyword,
    get_papers_by_journal,
    get_papers_by_year,
)