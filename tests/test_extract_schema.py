from datetime import date

import pytest
from pydantic import ValidationError

from atlas.schemas.extract import ActionItem, ExtractResult


def test_full_result_is_valid():
    result = ExtractResult(
        title="Sprint planning",
        entities=["Asha", "Atlas"],
        dates=["2026-11-27"],
        action_items=[{"task": "Write tests", "owner": "Asha", "due_date": "2026-11-27"}],
    )
    assert result.dates == [date(2026, 11, 27)]
    assert result.action_items[0].owner == "Asha"


def test_only_title_is_required():
    result = ExtractResult(title="Short note")
    assert result.entities == []
    assert result.dates == []
    assert result.action_items == []


def test_blank_title_is_rejected():
    with pytest.raises(ValidationError):
        ExtractResult(title="   ")


def test_title_over_200_chars_is_rejected():
    with pytest.raises(ValidationError):
        ExtractResult(title="x" * 201)


def test_vague_date_is_rejected():
    with pytest.raises(ValidationError):
        ExtractResult(title="Note", dates=["next Friday"])


def test_action_item_blank_task_is_rejected():
    with pytest.raises(ValidationError):
        ActionItem(task=" ")


def test_action_item_owner_and_due_date_are_optional():
    item = ActionItem(task="Send the report")
    assert item.owner is None
    assert item.due_date is None


def test_default_lists_are_not_shared_between_results():
    first = ExtractResult(title="A")
    first.entities.append("Asha")
    assert ExtractResult(title="B").entities == []
