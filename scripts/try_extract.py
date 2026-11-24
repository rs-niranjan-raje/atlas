"""Try extract() against the real Gemini API. Run: uv run python scripts/try_extract.py"""

import asyncio
import time

from atlas.tools.extract import MODEL, extract

# Made-up note. Never paste real customer or personal data here.
SAMPLE = """Sprint planning, 20 Nov 2026.
Present: Asha, Ravi, and Meera from the Pune team.
Asha will finish the search tests by 27 Nov 2026.
Ravi to ask Acme Corp for the API quota increase, no date set.
Next review meeting on 4 Dec 2026."""


async def main() -> None:
    start = time.perf_counter()
    result = await extract(SAMPLE)
    seconds = time.perf_counter() - start
    print(f"Model: {MODEL}  ({seconds:.1f}s)")
    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    asyncio.run(main())
