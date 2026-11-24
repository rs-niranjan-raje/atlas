import asyncio
from datetime import date
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from atlas.tools.extract import (
    MODEL,
    SYSTEM_INSTRUCTION,
    ExtractionError,
    call_gemini,
    extract,
)

GOOD_JSON = (
    '{"title": "Sprint planning", "entities": ["Asha"], "dates": ["2026-11-27"], '
    '"action_items": [{"task": "Write tests", "owner": "Asha", "due_date": "2026-11-27"}]}'
)


def fake_generate(reply):
    """Build a fake model call that returns `reply` and records what it was sent."""
    seen = []

    async def generate(text):
        seen.append(text)
        return reply

    return generate, seen


def test_good_reply_becomes_a_validated_object():
    generate, seen = fake_generate(GOOD_JSON)
    result = asyncio.run(extract("Asha will write tests by Friday.", generate))
    assert result.title == "Sprint planning"
    assert result.dates == [date(2026, 11, 27)]
    assert result.action_items[0].owner == "Asha"
    assert seen == ["Asha will write tests by Friday."]


def fake_generate_sequence(replies):
    """Like fake_generate, but returns the replies one by one (first call, second call...)."""
    seen = []
    queue = iter(replies)

    async def generate(text):
        seen.append(text)
        return next(queue)

    return generate, seen


BAD_DATE_JSON = '{"title": "Note", "dates": ["next Friday"]}'


def test_good_first_reply_makes_one_call():
    generate, seen = fake_generate_sequence([GOOD_JSON])
    asyncio.run(extract("anything", generate))
    assert len(seen) == 1


def test_bad_then_good_reply_retries_once_and_succeeds():
    generate, seen = fake_generate_sequence([BAD_DATE_JSON, GOOD_JSON])
    result = asyncio.run(extract("Asha writes tests.", generate))
    assert result.title == "Sprint planning"
    assert len(seen) == 2


def test_retry_prompt_contains_text_bad_reply_and_error():
    generate, seen = fake_generate_sequence([BAD_DATE_JSON, GOOD_JSON])
    asyncio.run(extract("Asha writes tests.", generate))
    retry_prompt = seen[1]
    assert "Asha writes tests." in retry_prompt  # the original text
    assert BAD_DATE_JSON in retry_prompt  # what the model said
    assert "dates.0" in retry_prompt  # which field was wrong (from the Pydantic error)


def test_two_bad_replies_raise_extraction_error_after_exactly_two_calls():
    generate, seen = fake_generate_sequence([BAD_DATE_JSON, BAD_DATE_JSON, GOOD_JSON])
    with pytest.raises(ExtractionError):
        asyncio.run(extract("anything", generate))
    assert len(seen) == 2  # never a third call


def test_non_json_replies_also_raise_extraction_error():
    generate, _ = fake_generate_sequence(["Sure! Here is your JSON:", "Sorry, I cannot."])
    with pytest.raises(ExtractionError):
        asyncio.run(extract("anything", generate))


def test_extraction_error_message_does_not_contain_the_users_text():
    generate, _ = fake_generate_sequence([BAD_DATE_JSON, BAD_DATE_JSON])
    with pytest.raises(ExtractionError) as info:
        asyncio.run(extract("secret meeting note", generate))
    assert "secret meeting note" not in str(info.value)
    assert isinstance(info.value.__cause__, ValidationError)


def test_call_gemini_sends_schema_and_zero_temperature():
    calls = []

    async def generate_content(**kwargs):
        calls.append(kwargs)
        return SimpleNamespace(text=GOOD_JSON)

    fake_client = SimpleNamespace(
        aio=SimpleNamespace(models=SimpleNamespace(generate_content=generate_content))
    )

    assert asyncio.run(call_gemini("some email", fake_client)) == GOOD_JSON
    sent = calls[0]
    assert sent["model"] == MODEL
    assert sent["contents"] == "some email"
    assert sent["config"].temperature == 0
    assert sent["config"].response_mime_type == "application/json"
    assert sent["config"].system_instruction == SYSTEM_INSTRUCTION
