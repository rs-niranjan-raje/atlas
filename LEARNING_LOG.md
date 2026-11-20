# Learning log

One entry per module: what I built, what broke, what I learned, and where an AI assistant
helped or got things wrong.

## Module 0: Setup

- **Built:**
- **Broke:**
- **Learned:**
- **AI assistant:**

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
