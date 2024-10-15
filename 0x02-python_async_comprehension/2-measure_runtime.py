#!/usr/bin/env python3
"""
Import async_comprehension from the
previous file and write a measure_runtime
coroutine that will execute async_comprehension
"""
import asyncio
import time
from importlib import import_module as use

async_comprehension = use('1-async_comprehension').async_comprehension


async def measure_runtime() -> float:
    """
    measure_runtime should measure the total
    runtime and return it. The total runtime
    should be roughly 10 seconds.
    """
    starting_time = time.time()
    await asyncio.gather(*(async_comprehension() for _ in range(4)))
    return time.time() - starting_time
