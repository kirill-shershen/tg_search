import asyncio

from config.telegram import BOT_RECONNECT_TIMER_MIN


async def run_pooling():
    while True:
        await asyncio.sleep(BOT_RECONNECT_TIMER_MIN)
