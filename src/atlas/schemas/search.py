"""A search request that Atlas sends to a search tool."""

from pydantic import BaseModel, Field

from atlas.schemas.common import NotBlankStr


class SearchQuery(BaseModel):
    """What to search for and how many results to return."""

    text: NotBlankStr
    max_results: int = Field(default=5, ge=1, le=20)
