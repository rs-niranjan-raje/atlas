"""The structured result Atlas pulls out of free text (a meeting note or an email)."""

from datetime import date

from pydantic import BaseModel, Field

from atlas.schemas.common import NotBlankStr


class ActionItem(BaseModel):
    """One thing someone needs to do."""

    task: NotBlankStr
    owner: str | None = None
    due_date: date | None = None


class ExtractResult(BaseModel):
    """Everything extracted from one piece of text. Only the title is required."""

    title: NotBlankStr = Field(max_length=200)
    entities: list[str] = Field(default_factory=list)
    dates: list[date] = Field(default_factory=list)
    action_items: list[ActionItem] = Field(default_factory=list)
