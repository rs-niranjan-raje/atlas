from pydantic import BaseModel, Field

from atlas.schemas.document import Document


class SearchResult(BaseModel):
    """A search result returned by Atlas."""

    document: Document
    score: float = Field(ge=0.0, le=1.0)  # score is between 0 and 1
