# AI Mistakes Log

Things the AI assistant got wrong while building Atlas, and how I caught them.
Add one row per mistake. Be specific. Keep it short.

| # | Module | What the AI got wrong | How I caught it | Fix / lesson |
|---|--------|-----------------------|-----------------|--------------|
| 1 | 1 | The "user 1/2/3 arrives" diagram made it look like all responses are sent together. | I asked "does the response wait until every task finishes?" | Each task answers when it finishes. `gather` waits only inside one request. |
| 2 | 1 | PROGRESS.md was left out of date after tasks were finished. | I noticed it still listed finished tasks as to-do. | Update the progress file at the end of every task. |

## How to fill a row

- **What the AI got wrong:** the claim, code or advice that was incorrect or misleading.
- **How I caught it:** a failing test, ruff, running the code, or a question that exposed it.
- **Fix / lesson:** what I changed, and what I will check next time.

## Rule of thumb

AI output is a draft. I run it, test it, and understand it before I keep it.
