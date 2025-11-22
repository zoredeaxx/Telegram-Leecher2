# colab_leecher/__main__.py

import asyncio
import logging
import requests
import uvloop
from pyrogram import Client, filters

# Import your configuration and the handler functions
from colab_leecher import API_ID, API_HASH, BOT_TOKEN
from colab_leecher.bot import (
    start,
    telegram_upload,
    drive_upload,
    directory_upload,
    yt_upload,
    settings_cmd,
    setPrefix,
    handle_url,
    handle_options,
    handle_image,
    custom_name,
    zip_pswd,
    unzip_pswd,
    help_command
)
from colab_leecher.utility.helper import isLink

async def main():
    app = Client(
        "my_bot",
        api_id=API_ID,
        api_hash=API_HASH,
        bot_token=BOT_TOKEN
    )

    app.add_handler(filters.command("start") & filters.private)(start)
    app.add_handler(filters.command("tgupload") & filters.private)(telegram_upload)
    app.add_handler(filters.command("gdupload") & filters.private)(drive_upload)
    app.add_handler(filters.command("dirupload") & filters.private)(directory_upload)
    app.add_handler(filters.command("ytupload") & filters.private)(yt_upload)
    app.add_handler(filters.command("settings") & filters.private)(settings_cmd)
    app.add_handler(filters.reply)(setPrefix)
    app.add_handler(filters.create(isLink) & ~filters.photo)(handle_url)
    app.add_handler(filters.photo & filters.private)(handle_image)
    app.add_handler(filters.command("setname") & filters.private)(custom_name)
    app.add_handler(filters.command("zipaswd") & filters.private)(zip_pswd)
    app.add_handler(filters.command("unzipaswd") & filters.private)(unzip_pswd)
    app.add_handler(filters.command("help") & filters.private)(help_command)
    
    # The callback query handler is special and is added directly
    app.add_handler(handle_options)

    # --- RUN THE BOT ---
    async with app:
        logging.info("Colab Leecher Started!")
        await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        uvloop.install()
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped manually.")
