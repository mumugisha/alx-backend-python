#!/usr/bin/env python3

import asyncio

module = __import__('1-async_comprehension')
async_comprehension = module.async_comprehension


async def main():
    print(await async_comprehension())

asyncio.run(main())
