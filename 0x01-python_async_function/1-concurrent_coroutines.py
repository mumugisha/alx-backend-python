#!/usr/bin/env python3
"""
Import wait_random from the previous Python
file that you’ve written and write an async
routine called wait_n.
"""
import asyncio
from typing import List

wait_random = __import__('0-basic_async_syntax').wait_random


async def wait_n(n: int, max_delay: int) -> List[float]:
    """
    Async routine that takes in 2 int arguments
    and returns the list of delays.
    """
    waiting_time_period = await asyncio.gather(
        *tuple(map(lambda _: wait_random(max_delay), range(n)))
    )
    return sorted(waiting_time_period)
