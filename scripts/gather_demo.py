"""Demo: running waits one by one vs together with asyncio.gather."""

import asyncio
import time


async def slow_task(name: str) -> str:
    """Pretend to wait on the network for 1 second."""
    await asyncio.sleep(1)
    return name


async def one_by_one(names: list[str]) -> list[str]:
    results = []
    for name in names:
        results.append(await slow_task(name))  # wait for each before starting the next
    return results


async def together(names: list[str]) -> list[str]:
    # start all tasks at once; the waits overlap
    return await asyncio.gather(*(slow_task(n) for n in names))


async def main() -> None:
    names = ["a", "b", "c"]

    start = time.perf_counter()  # stopwatch
    await one_by_one(names)
    print(f"one by one: {time.perf_counter() - start:.1f}s")

    start = time.perf_counter()
    await together(names)
    print(f"gather:     {time.perf_counter() - start:.1f}s")


if __name__ == "__main__":
    asyncio.run(main())
