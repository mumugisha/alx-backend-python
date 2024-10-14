#!/usr/bin/env python3
"""
Write an asynchronous coroutine that
takes in an integer argument and waits for a random delay.
"""
import asyncio
import random


async def wait_random(max_delay: int = 10) -> float:
    """
    Waits for a random delay between 0 and max_delay seconds
    and eventually returns the delay time.
    """
    waiting_time_period = random.random() * max_delay
    await asyncio.sleep(waiting_time_period)
    return waiting_time_period
