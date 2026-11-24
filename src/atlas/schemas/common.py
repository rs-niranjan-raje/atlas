"""Small reusable types shared by several schemas."""

from typing import Annotated

from pydantic import AfterValidator


def not_blank(value: str) -> str:
    """Reject a string that is empty or only whitespace."""
    if not value.strip():
        raise ValueError("String cannot be empty or only whitespace.")
    return value


NotBlankStr = Annotated[str, AfterValidator(not_blank)]
