# Atlas: Progress

Course: Agentic AI Developer Program (Modules 0-11, Gemini + Google ADK).
Last updated: 2026-11-20.

## Status at a glance

| Module | Topic | Status |
|---|---|---|
| 0 | Setup | Done except the tag |
| 1 | Python essentials | Done except the tag |
| 2-11 | LLM basics, first agent, RAG, multi-agent, MCP/A2A, human-in-the-loop, guardrails, responsible AI, deployment, capstone | Not started |

## Module 0: Setup

Done:
- Repo created and pushed: first commit `5d17262` ("Module 0: Atlas skeleton") on `master`.
- `.env` created locally (never committed). Gemini key verified with `scripts/check_gemini.py`.
- Python 3.12 installed via uv (`UV_SYSTEM_CERTS=1` fixed the company-network certificate error).
- ADK samples cloned to `D:\adk-samples`. The `deep-search` sample:
  - dependencies installed with Python 3.12
  - its own test (`tests/test_runnability.py`) passes
  - runs in `adk web` and answers simple messages
  - full research runs hit a 429 quota error (personal free-tier key)

Local changes made to the sample clone only (not in Atlas):
- `app/__init__.py`: use the API key when set, instead of forcing Google Cloud login.
- `app/.env`: key added, `MODEL_NAME=gemini-3.5-flash-lite`.

Leftovers:
- [x] Find a learning buddy.
- [x] Write the Module 0 entry in `LEARNING_LOG.md`.
- [x] Update the tracker spreadsheet.
- [ ] Tag `module-0-done`.
- Skipped: "draw the deep-search flow" (decided not to do it).
- Skipped: "team's agent project" step (no such project exists).

## Module 1: Python essentials

Lab tasks:
1. [x] Pydantic models in `src/atlas/schemas/`: `Document`, `SearchQuery` (with `NotBlankStr`), `SearchResult`
2. [x] Async httpx client in `tools/fetch.py` with timeouts and retries
3. [x] `asyncio.gather` timing (`scripts/gather_demo.py`: 3.0s one by one, 1.0s with gather)
4. [x] Mocked tests (`tests/test_fetch.py`, `httpx.MockTransport`)
5. [x] AI edge-case tests and mistakes log
   - [x] Edge-case tests added, coverage checked
   - [x] `AI_MISTAKES.md` has 2 real rows (empty row 3 deleted)

Exit check:
- [x] At least 15 tests: 21
- [x] At least 80% coverage on `schemas/` and `tools/`: 97%
- [x] A validation-error test

Latest checks: 21 tests passed, `ruff check` clean.

Next: commit and tag `module-1-done` (only when asked).

## Uncommitted changes

`pyproject.toml`, `uv.lock`, `scripts/`, `src/atlas/schemas/` (document, result, search), `src/atlas/tools/fetch.py`,
`tests/` (document, result, search, fetch), `AI_MISTAKES.md`, `LEARNING_LOG.md` and this file.
Commit only when asked.

## Concepts learned so far

- uv ~ Maven, `pyproject.toml` ~ pom.xml, Ruff ~ Checkstyle, pytest ~ JUnit, pytest-cov ~ JaCoCo.
- Pydantic `BaseModel` + `Field(...)` ~ DTO + Bean Validation. `Field` does nothing without `BaseModel`.
- A param or field is optional only if it has a default.
- Two meanings of "model": the AI model (Gemini) vs a data model (Pydantic class).
- Tool calling: the model only asks for a tool call. Our code validates and runs it.
  The built-in `google_search` is different: Google runs the search inside the Gemini call.
- An agent = model + instructions + tools. Guardrails come in Modules 4, 5 and 8.
- async: `await` runs in order, `gather` overlaps waits, `asyncio.sleep` parks one task while `time.sleep` blocks the thread.
- Test one rule at a time. Valid edge values are asserted as accepted, not wrapped in `pytest.raises`.

## Open decisions

- Quota: a team key or Google Cloud project is needed to run deep-search fully.
- Optional: `uv add --dev pytest-cov` so the coverage command needs no `--with`.
