#!/usr/bin/env python3
"""
Create a measure_time function with
integers n and max_delay as arguments
"""
import asyncio
import time

wait_n = __import__('1-concurrent_coroutines').wait_n


def measure_time(n: int, max_delay: int) -> float:
    """
    Measure the total execution time of
    wait_n and return the average time per task.
    """
    starting_time_period = time.time()
    asyncio.run(wait_n(n, max_delay))
    total_time = time.time() - starting_time_period
    return total_time / n
