import asyncio
import logging
import requests
import uvloop

from colab_leecher import bot

async def main():
    async with bot.colab_bot:
        logging.info("Colab Leecher Started!")
        await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        uvloop.install()
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped manually.")
