import asyncio
from loguru import logger
from random import randint


async def sleep(sleep_from: int, sleep_to: int):
    delay = randint(sleep_from, sleep_to)
    logger.info(f"💤 Спим {delay} секунд...")
    for _ in range(delay):
        await asyncio.sleep(1)
