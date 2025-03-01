from datetime import datetime
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field, validator
from sqlmodel import Field as SQLField, SQLModel, Relationship


class Author(BaseModel):
    name: str
    affiliation: Optional[str] = None
    orcid: Optional[str] = None


class AuthorDB(SQLModel, table=True):
    """SQLModel version of Author for database storage"""
    id: Optional[int] = SQLField(primary_key=True)
    name: str
    affiliation: Optional[str] = None
    orcid: Optional[str] = None
    paper_id: Optional[int] = SQLField(foreign_key="paperdb.id")
    paper: Optional["PaperDB"] = Relationship(back_populates="authors")


class Keyword(SQLModel, table=True):
    """Keywords associated with papers"""
    id: Optional[int] = SQLField(primary_key=True)
    keyword: str
    paper_id: Optional[int] = SQLField(foreign_key="paperdb.id")
    paper: Optional["PaperDB"] = Relationship(back_populates="keyword_objects")


class Paper(BaseModel):
    """Pydantic model for paper data"""
    title: str
    authors: List[Author]
    abstract: Optional[str] = None
    publication_date: Optional[datetime] = None
    journal: Optional[str] = None
    doi: Optional[str] = None
    url: Optional[str] = None
    citations: Optional[int] = None
    keywords: List[str] = Field(default_factory=list)
    source: str = ""  # e.g., 'scopus', 'arxiv', etc.
    source_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)  # For storing source-specific data

    class Config:
        arbitrary_types_allowed = True

    @validator('doi')
    def doi_must_be_valid(cls, v):
        """Simple validation for DOI format"""
        if v is not None and not v.startswith('10.'):
            raise ValueError('DOI must start with 10.')
        return v

    def __str__(self):
        return f"{self.title} ({len(self.authors)} authors, {self.publication_date})"


class PaperDB(SQLModel, table=True):
    """SQLModel version of Paper for database storage"""
    id: Optional[int] = SQLField(primary_key=True)
    title: str
    abstract: Optional[str] = None
    publication_date: Optional[datetime] = None
    journal: Optional[str] = None
    doi: Optional[str] = SQLField(default=None, unique=True, index=True)
    url: Optional[str] = None
    citations: Optional[int] = None
    source: str = ""
    source_id: Optional[str] = None
    metadata_json: Optional[str] = None

    # Relationships
    authors: List[AuthorDB] = Relationship(back_populates="paper")
    keyword_objects: List[Keyword] = Relationship(back_populates="paper")

    @property
    def keywords(self) -> List[str]:
        return [k.keyword for k in self.keyword_objects]

    @classmethod
    def from_paper(cls, paper: Paper) -> "PaperDB":
        """Convert a Paper to PaperDB"""
        import json

        # Create PaperDB instance
        paper_db = cls(
            title=paper.title,
            abstract=paper.abstract,
            publication_date=paper.publication_date,
            journal=paper.journal,
            doi=paper.doi,
            url=paper.url,
            citations=paper.citations,
            source=paper.source,
            source_id=paper.source_id,
            metadata_json=json.dumps(paper.metadata) if paper.metadata else None
        )

        # Add authors
        paper_db.authors = [
            AuthorDB(
                name=author.name,
                affiliation=author.affiliation,
                orcid=author.orcid
            )
            for author in paper.authors
        ]

        # Add keywords
        paper_db.keyword_objects = [
            Keyword(keyword=keyword)
            for keyword in paper.keywords
        ]

        return paper_db

    def to_paper(self) -> Paper:
        """Convert PaperDB to Paper"""
        import json

        # Convert authors
        authors = [
            Author(
                name=author.name,
                affiliation=author.affiliation,
                orcid=author.orcid
            )
            for author in self.authors
        ]

        # Extract metadata
        metadata = {}
        if self.metadata_json:
            try:
                metadata = json.loads(self.metadata_json)
            except json.JSONDecodeError:
                pass

        # Create Paper instance
        return Paper(
            title=self.title,
            authors=authors,
            abstract=self.abstract,
            publication_date=self.publication_date,
            journal=self.journal,
            doi=self.doi,
            url=self.url,
            citations=self.citations,
            keywords=self.keywords,
            source=self.source,
            source_id=self.source_id,
            metadata=metadata
        )
