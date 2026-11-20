"""A search request that Atlas sends to a search tool."""

from typing import Annotated

from pydantic import AfterValidator, BaseModel, Field


def not_blank(value: str) -> str:
    """Check if the string is empty or only whitespace."""
    if not value.strip():
        raise ValueError("String cannot be empty or only whitespace.")
    return value


NotBlankStr = Annotated[str, AfterValidator(not_blank)]


class SearchQuery(BaseModel):
    """What to search for and how many results to return."""

    text: NotBlankStr
    max_results: int = Field(default=5, ge=1, le=20)
