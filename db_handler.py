import logging
from typing import List, Optional, Dict, Any

from sqlalchemy.exc import IntegrityError
from sqlalchemy import func as sqlalchemy_func
from sqlmodel import Session, SQLModel, create_engine, select, or_
from rich.console import Console

from models import Paper, PaperDB, AuthorDB, Keyword
from config import VAULT_PATH

# Configure logging
console = Console()
logger = logging.getLogger("litreview.db")

# Set up database
DB_PATH = VAULT_PATH / "papers.sqlite"
DB_URL = f"sqlite:///{DB_PATH}"

# Create engine
engine = create_engine(DB_URL, echo=False)


def init_db():
    """Initialize the database by creating all tables"""
    logger.info(f"Initializing database at {DB_PATH}")

    # Ensure the directory exists
    DB_PATH.parent.mkdir(exist_ok=True, parents=True)
    SQLModel.metadata.create_all(engine)
    logger.info("Database initialized")


def save_papers_to_db(papers: List[Paper]) -> int:
    """
    Save papers to the database, skipping duplicates based on DOI.

    Returns:
        Number of new papers added to the database.
    """
    added_count = 0
    skipped_count = 0

    with Session(engine) as session:
        for paper in papers:
            # Skip papers without DOI as we can't reliably check for duplicates
            if not paper.doi:
                skipped_count += 1
                continue

            # Check if the paper already exists
            existing_paper = session.exec(
                select(PaperDB).where(PaperDB.doi == paper.doi)
            ).first()

            if existing_paper:
                # Update citation count if necessary
                if paper.citations and (
                    not existing_paper.citations
                    or paper.citations > existing_paper.citations
                ):
                    existing_paper.citations = paper.citations
                    session.add(existing_paper)
                skipped_count += 1
                continue

            # Convert to database model and add
            paper_db = PaperDB.from_paper(paper)
            try:
                session.add(paper_db)
                session.commit()
                added_count += 1
            except IntegrityError:
                logger.warning(f"Issue adding paper: {paper.title}. Skipping...")
                session.rollback()
                skipped_count += 1

    logger.info(
        f"Added {added_count} new papers to the database. Skipped {skipped_count} papers..."
    )
    return added_count


def get_papers_from_db(
    query: Optional[str] = None,
    source: Optional[str] = None,
    start_year: Optional[int] = None,
    end_year: Optional[int] = None,
    limit: int = 100,
) -> List[Paper]:
    """
    Retrieve papers from the database with optional filtering.

    Args:
        query: Text search in title, abstract, or keywords
        source: Filter by source (e.g., 'scopus', 'arxiv')
        start_year: Filter papers published after this year
        end_year: Filter papers published before this year
        limit: Maximum number of results

    Returns:
        List of Paper objects
    """
    with Session(engine) as session:
        statement = select(PaperDB)

        # Apply filters
        if source:
            statement = statement.where(PaperDB.source == source)

        if start_year:
            statement = statement.where(
                or_(
                    PaperDB.publication_date is None,
                    PaperDB.publication_date >= f"{start_year}-01-01",
                )
            )

        if end_year:
            statement = statement.where(
                or_(
                    PaperDB.publication_date is None,
                    PaperDB.publication_date <= f"{end_year}-12-31",
                )
            )

        if query:
            query_term = f"%{query}%"
            statement = statement.where(
                or_(PaperDB.title.like(query_term), PaperDB.abstract.like(query_term))
            )

        statement = statement.limit(limit)
        results = session.exec(statement).all()

        # Convert to Paper objects
        papers = [result.to_paper() for result in results]

    return papers


def get_paper_count() -> int:
    """Get the total number of papers in the database"""
    with Session(engine) as session:
        return session.exec(select(PaperDB)).count()


def get_stats() -> Dict[str, Any]:
    """Get statistics about the database"""
    with Session(engine) as session:
        total_papers = session.exec(select(PaperDB)).count()
        total_authors = session.exec(select(AuthorDB)).count()

        # Count papers by source
        sources_query = select(
            PaperDB.source, sqlalchemy_func.count(PaperDB.id)
        ).group_by(PaperDB.source)
        sources = {source: count for source, count in session.exec(sources_query).all()}

        # Get the 10 most common keywords
        keywords_query = (
            select(
                Keyword.keyword, sqlalchemy_func.count(Keyword.keyword).label("count")
            )
            .group_by(Keyword.keyword)
            .order_by(sqlalchemy_func.count(Keyword.keyword).desc())
            .limit(10)
        )
        top_keywords = {kw: count for kw, count in session.exec(keywords_query).all()}

    return {
        "total_papers": total_papers,
        "total_authors": total_authors,
        "papers_by_source": sources,
        "top_keywords": top_keywords,
    }
