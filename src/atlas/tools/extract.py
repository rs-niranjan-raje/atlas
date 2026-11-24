"""Turn free text (a meeting note or an email) into a validated ExtractResult."""

from collections.abc import Awaitable, Callable

from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import ValidationError

from atlas.schemas.extract import ExtractResult

MODEL = "gemini-3.5-flash-lite"

# Stable text goes first and the changing email goes last, so prompt caching can help later.
SYSTEM_INSTRUCTION = (
    "You extract structured data from a meeting note or an email. "
    "Return a short title, the people, companies and places mentioned (entities), "
    "every date as YYYY-MM-DD, and each action item with its owner and due date if given. "
    "Use only what is in the text. If something is missing, leave it empty. Never guess."
)

# A function that takes the text and returns the model's raw JSON string.
Generate = Callable[[str], Awaitable[str]]


class ExtractionError(Exception):
    """The model could not give a valid result, even after one retry."""


def build_retry_prompt(text: str, bad_reply: str, error: ValidationError) -> str:
    """Build the second message: the original text, the wrong reply, and what was wrong."""
    return (
        f"{text}\n\n"
        f"Your previous reply was:\n{bad_reply}\n\n"
        f"It failed validation with this error:\n{error}\n\n"
        "Fix the problems and reply again with only the corrected JSON."
    )


async def call_gemini(text: str, client: genai.Client | None = None) -> str:
    """Send the text to Gemini and return its raw JSON reply."""
    if client is None:
        load_dotenv()
        client = genai.Client()  # reads GEMINI_API_KEY from the environment
    response = await client.aio.models.generate_content(
        model=MODEL,
        contents=text,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            response_mime_type="application/json",
            response_schema=ExtractResult,
            temperature=0,  # we want the same answer every time
        ),
    )
    return response.text


async def extract(text: str, generate: Generate = call_gemini) -> ExtractResult:
    """Extract structured data from text.

    `generate` is the model call. Tests pass a fake one, so they need no key or network.
    If the first reply fails validation, ask once more with the error fed back.
    Raises ExtractionError if the second reply fails too.
    """
    raw = await generate(text)
    try:
        return ExtractResult.model_validate_json(raw)
    except ValidationError as first_error:
        retry_prompt = build_retry_prompt(text, raw, first_error)

    raw = await generate(retry_prompt)  # the one and only retry
    try:
        return ExtractResult.model_validate_json(raw)
    except ValidationError as second_error:
        # Keep the message free of the user's text. The details stay on __cause__.
        raise ExtractionError(
            f"Model reply failed validation twice ({second_error.error_count()} errors)."
        ) from second_error
