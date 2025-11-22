import asyncio
import logging
from colab_leecher import colab_bot

async def main():
    async with colab_bot:
        from . import bot
        logging.info("Colab Leecher Started!")
        await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped.")
