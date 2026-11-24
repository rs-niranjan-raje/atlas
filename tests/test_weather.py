import asyncio
from types import SimpleNamespace

import httpx
import pytest

from atlas.tools.weather import ToolCallError, ask, get_weather


def weather_client(requests=None):
    """A fake Open-Meteo: finds Pune only, and records the requests it receives."""

    def handler(request):
        if requests is not None:
            requests.append(request)
        if "geocoding" in request.url.host:
            if request.url.params["name"] == "Pune":
                return httpx.Response(
                    200, json={"results": [{"name": "Pune", "latitude": 18.5, "longitude": 73.8}]}
                )
            return httpx.Response(200, json={})  # unknown city: no "results" key
        return httpx.Response(200, json={"current": {"temperature_2m": 27.5, "weather_code": 63}})

    return httpx.AsyncClient(transport=httpx.MockTransport(handler))


def model_asks(name, args):
    """A fake model response that asks us to call a function."""
    return SimpleNamespace(
        function_calls=[SimpleNamespace(name=name, args=args)],
        text=None,
        candidates=[SimpleNamespace(content="MODEL_REQUEST_TURN")],
    )


def model_says(text):
    """A fake model response with a plain text answer."""
    return SimpleNamespace(function_calls=None, text=text, candidates=[])


def fake_model(responses):
    """Return the responses one by one. Records how many items the history had each call."""
    queue = iter(responses)
    history_sizes = []

    async def generate(contents):
        history_sizes.append(len(contents))
        return next(queue)

    return generate, history_sizes


def test_function_request_is_run_and_result_sent_back():
    generate, sizes = fake_model(
        [model_asks("get_weather", {"city": "Pune"}), model_says("28C and clear in Pune.")]
    )
    answer = asyncio.run(ask("Weather in Pune?", generate, weather_client()))
    assert answer == "28C and clear in Pune."
    assert sizes == [1, 3]  # 2 calls; second has question + model request + function result


def test_function_result_is_in_the_second_call():
    sent = []

    async def generate(contents):
        sent.append(list(contents))
        return model_asks("get_weather", {"city": "Pune"}) if len(sent) == 1 else model_says("ok")

    asyncio.run(ask("Weather in Pune?", generate, weather_client()))
    result_part = sent[1][2].parts[0].function_response
    assert result_part.name == "get_weather"
    assert result_part.response == {"city": "Pune", "temp_c": 27.5, "sky": "rain"}


def test_no_function_needed_means_one_call():
    generate, sizes = fake_model([model_says("Hello!")])
    assert asyncio.run(ask("Hi", generate)) == "Hello!"
    assert sizes == [1]


def test_unknown_function_name_is_refused():
    generate, sizes = fake_model([model_asks("delete_everything", {})])
    with pytest.raises(ToolCallError):
        asyncio.run(ask("anything", generate))
    assert sizes == [1]  # we never went back to the model


@pytest.mark.parametrize("bad_args", [{}, {"city": "   "}, {"city": 123}])
def test_invalid_arguments_are_refused(bad_args):
    generate, _ = fake_model([model_asks("get_weather", bad_args)])
    with pytest.raises(ToolCallError):
        asyncio.run(ask("anything", generate))


def test_get_weather_returns_city_temperature_and_sky():
    result = asyncio.run(get_weather("Pune", weather_client()))
    assert result == {"city": "Pune", "temp_c": 27.5, "sky": "rain"}


def test_get_weather_sends_coordinates_to_the_forecast_request():
    requests = []
    asyncio.run(get_weather("Pune", weather_client(requests)))
    assert len(requests) == 2  # geocoding, then forecast
    assert requests[1].url.params["latitude"] == "18.5"
    assert requests[1].url.params["longitude"] == "73.8"


def test_unknown_city_returns_an_error_result_and_skips_the_forecast():
    requests = []
    result = asyncio.run(get_weather("Nowhereville", weather_client(requests)))
    assert "error" in result
    assert len(requests) == 1


def test_network_error_status_raises():
    client = httpx.AsyncClient(transport=httpx.MockTransport(lambda r: httpx.Response(503)))
    with pytest.raises(httpx.HTTPStatusError):
        asyncio.run(get_weather("Pune", client))
