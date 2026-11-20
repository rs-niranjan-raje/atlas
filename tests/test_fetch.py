import asyncio

import httpx
import pytest

from atlas.tools.fetch import fetch_page


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch):
    """Skip the real waiting between retries so tests run fast."""

    async def fake_sleep(seconds):
        pass

    monkeypatch.setattr(asyncio, "sleep", fake_sleep)


def make_client(responses):
    """Build a client whose fake server returns the given status codes in order.

    Returns (client, calls) where calls is a list that records each request.
    """
    calls = []
    codes = iter(responses)

    def handler(request):
        calls.append(request)
        item = next(codes)
        if isinstance(item, Exception):  # simulate a network failure
            raise item
        return httpx.Response(item, text="page text")

    return httpx.AsyncClient(transport=httpx.MockTransport(handler)), calls


async def run_fetch(responses):
    client, calls = make_client(responses)
    async with client:
        try:
            return await fetch_page("https://example.com", client), calls
        except httpx.HTTPError as error:  # base class of status, timeout, connect errors
            return error, calls


def test_good_response_returns_text():
    result, calls = asyncio.run(run_fetch([200]))
    assert result == "page text"
    assert len(calls) == 1


def test_404_raises_without_retry():
    result, calls = asyncio.run(run_fetch([404]))
    assert isinstance(result, httpx.HTTPStatusError)
    assert len(calls) == 1


def test_503_then_200_succeeds_after_retry():
    result, calls = asyncio.run(run_fetch([503, 200]))
    assert result == "page text"
    assert len(calls) == 2


def test_three_503s_raise():
    result, calls = asyncio.run(run_fetch([503, 503, 503]))
    assert isinstance(result, httpx.HTTPStatusError)
    assert len(calls) == 3


def test_timeouts_then_success_retries():
    timeout = httpx.ConnectTimeout("too slow")
    result, calls = asyncio.run(run_fetch([timeout, timeout, 200]))
    assert result == "page text"
    assert len(calls) == 3


def test_connect_error_every_time_raises():
    error = httpx.ConnectError("refused")
    result, calls = asyncio.run(run_fetch([error, error, error]))
    assert isinstance(result, httpx.ConnectError)
    assert len(calls) == 3


def test_own_client_is_created_and_closed(monkeypatch):
    real_client = httpx.AsyncClient
    created = []

    def fake_client(**kwargs):
        client = real_client(
            transport=httpx.MockTransport(lambda request: httpx.Response(200, text="ok")),
            **kwargs,
        )
        created.append(client)
        return client

    monkeypatch.setattr(httpx, "AsyncClient", fake_client)

    assert asyncio.run(fetch_page("https://example.com")) == "ok"
    assert created[0].is_closed  # we created it, so we must close it
