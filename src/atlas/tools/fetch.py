"""Fetch a web page over HTTP, retrying on temporary errors."""

import asyncio

import httpx

MAX_ATTEMPTS = 3


async def fetch_page(url: str, client: httpx.AsyncClient | None = None) -> str:
    """Download a page and return its text.

    Retries up to 3 times on timeouts, connection errors and 5xx responses,
    waiting 1s, then 2s between tries. A 4xx response (like 404) is raised at once.
    Pass your own client to control the transport (tests use a fake server).
    """
    owns_client = client is None
    if client is None:
        client = httpx.AsyncClient(timeout=10.0)
    try:
        for attempt in range(MAX_ATTEMPTS):
            is_last = attempt == MAX_ATTEMPTS - 1
            try:
                response = await client.get(url)
                response.raise_for_status()
                return response.text
            except (httpx.TimeoutException, httpx.ConnectError):
                if is_last:
                    raise
            except httpx.HTTPStatusError as error:
                if error.response.status_code < 500 or is_last:
                    raise
            await asyncio.sleep(2**attempt)
        raise RuntimeError("unreachable")
    finally:
        if owns_client:
            await client.aclose()
