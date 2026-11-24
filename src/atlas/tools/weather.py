"""Function calling demo: the model asks for get_weather, our code validates and runs it."""

import ssl
from collections.abc import Awaitable, Callable
from typing import Any

import httpx
import truststore
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


GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

# WMO weather codes (used by Open-Meteo) grouped into plain words.
SKY_BY_CODE = {
    0: "clear", 1: "mostly clear", 2: "partly cloudy", 3: "overcast",
    45: "fog", 48: "fog", 51: "light drizzle", 53: "drizzle", 55: "heavy drizzle",
    61: "light rain", 63: "rain", 65: "heavy rain", 71: "light snow", 73: "snow",
    75: "heavy snow", 80: "rain showers", 81: "rain showers", 82: "heavy rain showers",
    95: "thunderstorm", 96: "thunderstorm with hail", 99: "thunderstorm with hail",
}  # fmt: skip


async def get_weather(city: str, client: httpx.AsyncClient | None = None) -> dict[str, Any]:
    """Look up the current weather for a city with Open-Meteo (free, no key).

    Two requests: city name -> latitude/longitude, then coordinates -> current weather.
    An unknown city returns {"error": ...} so the model can tell the user.
    Network problems raise httpx.HTTPError.
    """
    if client is None:
        # Trust the operating system's certificates (needed behind a company proxy).
        context = truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        async with httpx.AsyncClient(timeout=10, verify=context) as own_client:
            return await get_weather(city, own_client)

    geo = await client.get(GEOCODING_URL, params={"name": city, "count": 1})
    geo.raise_for_status()
    places = geo.json().get("results")
    if not places:
        return {"error": f"City not found: {city}"}
    place = places[0]

    forecast = await client.get(
        FORECAST_URL,
        params={
            "latitude": place["latitude"],
            "longitude": place["longitude"],
            "current": "temperature_2m,weather_code",
        },
    )
    forecast.raise_for_status()
    current = forecast.json()["current"]
    return {
        "city": place["name"],
        "temp_c": current["temperature_2m"],
        "sky": SKY_BY_CODE.get(current["weather_code"], "unknown"),
    }


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


async def ask(
    question: str,
    generate: Generate = call_gemini_with_tools,
    http_client: httpx.AsyncClient | None = None,
) -> str:
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
    result = await get_weather(args.city, http_client)  # 3. only now WE run it

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
