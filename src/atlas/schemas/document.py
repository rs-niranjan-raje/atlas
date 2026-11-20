"""A document that Atlas can search and cite."""

from pydantic import BaseModel, Field, HttpUrl


class Document(BaseModel):
    """One source document (a web page, a PDF, a note)."""

    id: str = Field(min_length=1)
    title: str = Field(min_length=1, max_length=300)
    text: str
    url: HttpUrl | None = None  # optional; must be a valid URL if given
