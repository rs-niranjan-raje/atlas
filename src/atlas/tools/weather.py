"""Function calling demo: the model asks for get_weather, our code validates and runs it."""

from collections.abc import Awaitable, Callable
from typing import Any

from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import ValidationError

from atlas.schemas.weather import WeatherArgs

MODEL = "gemini-3.5-flash-lite"

# What the model sees: a "menu" entry describing the function and its arguments.
WEATHER_TOOL = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="get_weather",
            description="Get the current weather for a city.",
            parameters_json_schema=WeatherArgs.model_json_schema(),
        )
    ]
)

# A function that takes the conversation so far and returns the model's response.
Generate = Callable[[list[Any]], Awaitable[Any]]


class ToolCallError(Exception):
    """The model asked for a function call we refuse to run."""


def get_weather(city: str) -> dict[str, Any]:
    """Fake weather lookup. Returns made-up data, no network."""
    return {"city": city, "temp_c": 28, "sky": "clear"}


async def call_gemini_with_tools(contents: list[Any], client: genai.Client | None = None) -> Any:
    """Send the conversation to Gemini, with get_weather offered as a tool."""
    if client is None:
        load_dotenv()
        client = genai.Client()
    return await client.aio.models.generate_content(
        model=MODEL,
        contents=contents,
        config=types.GenerateContentConfig(tools=[WEATHER_TOOL], temperature=0),
    )


async def ask(question: str, generate: Generate = call_gemini_with_tools) -> str:
    """Answer a question, running get_weather if the model asks for it.

    Normal case: 2 model calls (question -> function request, then function result -> answer).
    If the model needs no function, it answers in the first call.
    Raises ToolCallError for an unknown function name or invalid arguments.
    """
    contents: list[Any] = [types.Content(role="user", parts=[types.Part.from_text(text=question)])]
    response = await generate(contents)

    if not response.function_calls:
        return response.text  # the model answered directly

    call = response.function_calls[0]
    if call.name != "get_weather":  # 1. is this a function we know?
        raise ToolCallError(f"Model asked for an unknown function: {call.name!r}.")
    try:
        args = WeatherArgs.model_validate(call.args)  # 2. are the arguments valid?
    except ValidationError as error:
        raise ToolCallError("Model sent invalid arguments for get_weather.") from error
    result = get_weather(args.city)  # 3. only now WE run it

    # Send back the history: the question, the model's request, and our function result.
    contents.append(response.candidates[0].content)
    contents.append(
        types.Content(
            role="user",
            parts=[types.Part.from_function_response(name=call.name, response=result)],
        )
    )
    final = await generate(contents)
    return final.text
