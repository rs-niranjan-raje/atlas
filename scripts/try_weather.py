"""Try function calling against the real Gemini API. Run: uv run python scripts/try_weather.py"""

import asyncio
import time

from atlas.tools.weather import MODEL, ask


async def main() -> None:
    start = time.perf_counter()
    answer = await ask("What is the weather in Pune right now?")
    seconds = time.perf_counter() - start
    print(f"Model: {MODEL}  ({seconds:.1f}s)")
    print(answer)


if __name__ == "__main__":
    asyncio.run(main())
