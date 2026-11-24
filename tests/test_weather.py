import asyncio
from types import SimpleNamespace

import pytest

from atlas.tools.weather import ToolCallError, ask, get_weather


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
    answer = asyncio.run(ask("Weather in Pune?", generate))
    assert answer == "28C and clear in Pune."
    assert sizes == [1, 3]  # 2 calls; second has question + model request + function result


def test_function_result_is_in_the_second_call():
    sent = []

    async def generate(contents):
        sent.append(list(contents))
        return model_asks("get_weather", {"city": "Pune"}) if len(sent) == 1 else model_says("ok")

    asyncio.run(ask("Weather in Pune?", generate))
    result_part = sent[1][2].parts[0].function_response
    assert result_part.name == "get_weather"
    assert result_part.response["city"] == "Pune"


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


def test_get_weather_returns_fake_data():
    assert get_weather("Pune")["city"] == "Pune"
