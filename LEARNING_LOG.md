# Learning log

One entry per module: what I built, what broke, what I learned, and where an AI assistant
helped or got things wrong.

## Module 0: Setup

- **Built:**
  - The Atlas repo, pushed to GitHub (first commit `5d17262`), with Python 3.12 managed by uv.
  - `scripts/check_gemini.py`: checks the Gemini key works without printing it.
  - Ran the `deep-search` sample from `D:\adk-samples` in `adk web`. It stands in for the missing "team's agent project".
- **Broke:**
  - uv failed with a certificate error on the company network. `UV_SYSTEM_CERTS=1` fixed it.
  - Full deep-search runs hit a 429 quota error on the free-tier key.
  - The sample forced Google Cloud login. I patched `app/__init__.py` in the sample clone (not in Atlas) to use the API key.
- **Learned:**
  - Two meanings of "model": the AI model (Gemini) vs a data model (Pydantic class).
  - An agent = model + instructions + tools.
  - Tool calling: the model only asks for the call. Our code validates and runs it.
  - The key lives in `.env`, which is git-ignored, and is never printed or committed.
- **AI assistant:** no mistakes logged for this module.

## Module 1: Python essentials

- **Built:**
  - Pydantic schemas: `Document`, `SearchQuery`, `SearchResult`, with a reusable `NotBlankStr` type.
  - `fetch_page`: async httpx download, 3 attempts, waits 1s then 2s. Retries timeouts, connect errors and 5xx. A 4xx fails at once.
  - `scripts/gather_demo.py`: 3 calls one by one took 3.0s, with `asyncio.gather` 1.0s.
  - 21 tests, 97% coverage on `schemas/` and `tools/`.
- **Broke:**
  - Used a name before defining it (ruff F821).
  - Two score tests expected an error for 0.0 and 1.0, but those values are valid. I changed them to assert they are accepted.
  - One test sent two bad values at once, so it could pass for the wrong reason. Now one rule per test.
- **Learned:**
  - A param or field is optional only if it has a default. `| None` and `Field(min_length=...)` do not make it optional.
  - `await` runs steps in order. `gather` overlaps the waits.
  - Mock the HTTP layer with `httpx.MockTransport`, and skip real sleeps by patching `asyncio.sleep`.
  - Coverage shows which lines no test runs. It does not show that the tests are good.
- **AI assistant:** see `AI_MISTAKES.md`.
