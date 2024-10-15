#!/usr/bin/env python3
"""
This module defines a coroutine `async_comprehension`
that collects 10 random numbers using an async
comprehension over async_generator.
"""
from typing import List
from importlib import import_module as information

async_generator = information('0-async_generator').async_generator


async def async_comprehension() -> List[float]:
    """
    Coroutine to collect 10 random numbers using an async
    comprehension over async_generator, then return them.
    """
    return [num async for num in async_generator()]
