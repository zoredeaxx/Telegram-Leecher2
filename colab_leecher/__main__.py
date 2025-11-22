import logging
import os
import asyncio
from datetime import datetime
from asyncio import sleep, get_event_loop

from pyrogram import filters, idle
from pyrogram.client import Client
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.handlers import MessageHandler, CallbackQueryHandler

from . import API_ID, API_HASH, BOT_TOKEN, OWNER
from . import colab_bot

from .utility.handler import cancelTask
from .utility.variables import BOT, MSG, BotTimes, Paths
from .utility.task_manager import taskScheduler, task_starter
from .utility.helper import isLink, setThumbnail, message_deleter, send_settings


async def main():
    global colab_bot
    
    logging.info("Initializing bot client...")
    
    colab_bot = Client(
        "my_bot",
        api_id=API_ID,
        api_hash=API_HASH,
        bot_token=BOT_TOKEN
    )
    
    add_handlers()
    
    async with colab_bot:
        user_info = await colab_bot.get_me()
        logging.info(f"Bot started as {user_info.first_name} (@{user_info.username})")
        await idle()
        
    logging.info("Bot has been stopped.")


def add_handlers():
    colab_bot.add_handler(MessageHandler(start, filters.command("start") & filters.private))
    colab_bot.add_handler(MessageHandler(telegram_upload, filters.command("leech") & filters.private))
    colab_bot.add_handler(MessageHandler(drive_upload, filters.command("mirror") & filters.private))
    colab_bot.add_handler(MessageHandler(directory_upload, filters.command("dirleech") & filters.private))
    colab_bot.add_handler(MessageHandler(yt_upload, filters.command("ytleech") & filters.private))
    colab_bot.add_handler(MessageHandler(settings, filters.command("settings") & filters.private))
    colab_bot.add_handler(MessageHandler(custom_name, filters.command("setname") & filters.private))
    colab_bot.add_handler(MessageHandler(zip_pswd, filters.command("zipaswd") & filters.private))
    colab_bot.add_handler(MessageHandler(unzip_pswd, filters.command("unzipaswd") & filters.private))
    colab_bot.add_handler(MessageHandler(help_command, filters.command("help") & filters.private))
    colab_bot.add_handler(MessageHandler(setPrefix, filters.reply))
    colab_bot.add_handler(MessageHandler(handle_url, filters.create(isLink) & ~filters.photo))
    colab_bot.add_handler(MessageHandler(handle_image, filters.photo & filters.private))
    colab_bot.add_handler(CallbackQueryHandler(handle_options))


src_request_msg = None


async def start(client, message):
    await message.delete()
    text = "**Hey There, 👋🏼 It's Colab Leecher**\n\n◲ I am a Powerful File Transloading Bot 🚀\n◲ I can Transfer Files To Telegram or Your Google Drive From Various Sources 🦐"
    keyboard = InlineKeyboardMarkup(
        [[
            InlineKeyboardButton("Repository 🦄", url="https://github.com/XronTrix10/Telegram-Leecher"),
            InlineKeyboardButton("Support 💝", url="https://t.me/Colab_Leecher"),
        ]]
    )
    await message.reply_text(text, reply_markup=keyboard)


async def telegram_upload(client, message):
    global BOT, src_request_msg
    BOT.Mode.mode = "leech"
    BOT.Mode.ytdl = False
    text = "<b>⚡ Send Me DOWNLOAD LINK(s) 🔗»</b>\n\n🦀 Follow the below pattern\n\n<code>https//linktofile1.mp4\nhttps//linktofile2.mp4\n[Custom name space.mp4]\n{Password for zipping}\n(Password for unzip)</code>"
    src_request_msg = await task_starter(message, text)


async def drive_upload(client, message):
    global BOT, src_request_msg
    BOT.Mode.mode = "mirror"
    BOT.Mode.ytdl = False
    text = "<b>⚡ Send Me DOWNLOAD LINK(s) 🔗»</b>\n\n🦀 Follow the below pattern\n\n<code>https//linktofile1.mp4\nhttps//linktofile2.mp4\n[Custom name space.mp4]\n{Password for zipping}\n(Password for unzip)</code>"
    src_request_msg = await task_starter(message, text)


async def directory_upload(client, message):
    global BOT, src_request_msg
    BOT.Mode.mode = "dir-leech"
    BOT.Mode.ytdl = False
    text = "<b>⚡ Send Me FOLDER PATH 🔗»</b>\n\n🦀 Below is an example\n\n<code>/home/user/Downloads/bot</code>"
    src_request_msg = await task_starter(message, text)


async def yt_upload(client, message):
    global BOT, src_request_msg
    BOT.Mode.mode = "leech"
    BOT.Mode.ytdl = True
    text = "<b>⚡ Send YTDL DOWNLOAD LINK(s) 🔗»</b>\n\n🦀 Follow the below pattern\n\n<code>https//linktofile1.mp4\nhttps//linktofile2.mp4\n[Custom name space.mp4]\n{Password for zipping}</code>"
    src_request_msg = await task_starter(message, text)


async def settings(client, message):
    if message.chat.id == OWNER:
        await message.delete()
        await send_settings(client, message, message.id, True)


async def setPrefix(client, message):
    global BOT
    if BOT.State.prefix:
        BOT.Setting.prefix = message.text
        BOT.State.prefix = False
        await send_settings(client, message, message.reply_to_message_id, False)
        await message.delete()
    elif BOT.State.suffix:
        BOT.Setting.suffix = message.text
        BOT.State.suffix = False
        await send_settings(client, message, message.reply_to_message_id, False)
        await message.delete()


async def handle_url(client, message):
    global BOT, src_request_msg
    BOT.Options.custom_name = ""
    BOT.Options.zip_pswd = ""
    BOT.Options.unzip_pswd = ""
    if src_request_msg:
        await src_request_msg.delete()
        src_request_msg = None
    if not BOT.State.task_going and BOT.State.started:
        temp_source = message.text.splitlines()
        for _ in range(3):
            if temp_source[-1].startswith("["):
                BOT.Options.custom_name = temp_source[-1][1:-1]
                temp_source.pop()
            elif temp_source[-1].startswith("{"):
                BOT.Options.zip_pswd = temp_source[-1][1:-1]
                temp_source.pop()
            elif temp_source[-1].startswith("("):
                BOT.Options.unzip_pswd = temp_source[-1][1:-1]
                temp_source.pop()
            else:
                break
        BOT.SOURCE = temp_source
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Regular", callback_data="normal")],
            [InlineKeyboardButton("Compress", callback_data="zip"), InlineKeyboardButton("Extract", callback_data="unzip")],
            [InlineKeyboardButton("UnDoubleZip", callback_data="undzip")]
        ])
        await message.reply_text(
            text=f"<b>🐹 Select Type of {BOT.Mode.mode.capitalize()} You Want » </b>\n\nRegular:<i> Normal file upload</i>\nCompress:<i> Zip file upload</i>\nExtract:<i> extract before upload</i>\nUnDoubleZip:<i> Unzip then compress</i>",
            reply_markup=keyboard,
            quote=True,
        )
    elif BOT.State.started:
        await message.delete()
        await message.reply_text("<i>I am Already Working ! Please Wait Until I finish 😣!!</i>")


async def handle_options(client, callback_query):
    global BOT, MSG
    data = callback_query.data
    if data in ["normal", "zip", "unzip", "undzip", "ytdl-true", "ytdl-false"]:
        if data in ["normal", "zip", "unzip", "undzip"]:
            BOT.Mode.type = data
        else:
            BOT.Mode.ytdl = data == "ytdl-true"
        
        await callback_query.message.delete()
        await client.delete_messages(
            chat_id=callback_query.message.chat.id,
            message_ids=callback_query.message.reply_to_message_id,
        )
        MSG.status_msg = await client.send_message(
            chat_id=OWNER,
            text="#STARTING_TASK\n\n**Starting your task in a few Seconds...🦐**",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Cancel ❌", callback_data="cancel")]])
        )
        BOT.State.task_going = True
        BOT.State.started = False
        BotTimes.start_time = datetime.now()
        loop = get_event_loop()
        BOT.TASK = loop.create_task(taskScheduler(client))
        await BOT.TASK
        BOT.State.task_going = False
    elif data == "video":
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Convert", callback_data="convert-true"), InlineKeyboardButton("Don't Convert", callback_data="convert-false")],
            [InlineKeyboardButton("To » Mp4", callback_data="mp4"), InlineKeyboardButton("To » Mkv", callback_data="mkv")],
            [InlineKeyboardButton("High Quality", callback_data="q-High"), InlineKeyboardButton("Low Quality", callback_data="q-Low")],
            [InlineKeyboardButton("Back ⏎", callback_data="back")]
        ])
        await callback_query.message.edit_text(
            f"CHOOSE YOUR DESIRED OPTION ⚙️ »\n\n╭⌬ CONVERT » <code>{BOT.Setting.convert_video}</code>\n├⌬ OUTPUT FORMAT » <code>{BOT.Options.video_out}</code>\n╰⌬ OUTPUT QUALITY » <code>{BOT.Setting.convert_quality}</code>",
            reply_markup=keyboard,
        )
    elif data == "caption":
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Monospace", callback_data="code-Monospace"), InlineKeyboardButton("Bold", callback_data="b-Bold")],
            [InlineKeyboardButton("Italic", callback_data="i-Italic"), InlineKeyboardButton("Underlined", callback_data="u-Underlined")],
            [InlineKeyboardButton("Regular", callback_data="p-Regular")]
        ])
        await callback_query.message.edit_text(
            "CHOOSE YOUR CAPTION FONT STYLE »\n\n⌬ <code>Monospace</code>\n⌬ Regular\n⌬ <b>Bold</b>\n⌬ <i>Italic</i>\n⌬ <u>Underlined</u>",
            reply_markup=keyboard,
        )
    elif data == "thumb":
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Delete Thumbnail", callback_data="del-thumb")],
            [InlineKeyboardButton("Go Back ⏎", callback_data="back")]
        ])
        thmb_ = "None" if not BOT.Setting.thumbnail else "Exists"
        await callback_query.message.edit_text(
            f"CHOOSE YOUR THUMBNAIL SETTINGS »\n\n⌬ Thumbnail » {thmb_}\n⌬ Send an Image to set as Your Thumbnail",
            reply_markup=keyboard,
        )
    elif data == "del-thumb":
        if BOT.Setting.thumbnail and os.path.exists(Paths.THMB_PATH):
            os.remove(Paths.THMB_PATH)
        BOT.Setting.thumbnail = False
        await send_settings(client, callback_query.message, callback_query.message.id, False)
    elif data == "set-prefix":
        await callback_query.message.edit_text("Send a Text to Set as PREFIX by REPLYING THIS MESSAGE »")
        BOT.State.prefix = True
    elif data == "set-suffix":
        await callback_query.message.edit_text("Send a Text to Set as SUFFIX by REPLYING THIS MESSAGE »")
        BOT.State.suffix = True
    elif data.startswith(("code-", "p-", "b-", "i-", "u-")):
        res = data.split("-")
        BOT.Options.caption = res[0]
        BOT.Setting.caption = res[1]
        await send_settings(client, callback_query.message, callback_query.message.id, False)
    elif data.startswith(("convert-", "q-", "mp4", "mkv")):
        if data.startswith("convert-"):
            BOT.Options.convert_video = data == "convert-true"
            BOT.Setting.convert_video = "Yes" if BOT.Options.convert_video else "No"
        elif data.startswith("q-"):
            BOT.Setting.convert_quality = data.split("-")[-1]
            BOT.Options.convert_quality = BOT.Setting.convert_quality == "High"
        else:
            BOT.Options.video_out = data
        await send_settings(client, callback_query.message, callback_query.message.id, False)
    elif data in ["media", "document"]:
        BOT.Options.stream_upload = data == "media"
        BOT.Setting.stream_upload = "Media" if BOT.Options.stream_upload else "Document"
        await send_settings(client, callback_query.message, callback_query.message.id, False)
    elif data == "close":
        await callback_query.message.delete()
    elif data == "back":
        await send_settings(client, callback_query.message, callback_query.message.id, False)
    elif data == "cancel":
        await cancelTask("User Cancelled !")


async def handle_image(client, message):
    msg = await message.reply_text("<i>Trying To Save Thumbnail...</i>")
    success = await setThumbnail(message)
    if success:
        await msg.edit_text("**Thumbnail Successfully Changed ✅**")
        await message.delete()
    else:
        await msg.edit_text("🥲 **Couldn't Set Thumbnail, Please Try Again !**", quote=True)
    await sleep(15)
    await message_deleter(message, msg)


async def custom_name(client, message):
    global BOT
    if len(message.command) != 2:
        msg = await message.reply_text("Send\n/setname <code>custom_fileame.extension</code>\nTo Set Custom File Name 📛", quote=True)
    else:
        BOT.Options.custom_name = message.command[1]
        msg = await message.reply_text("Custom Name Has Been Successfully Set !", quote=True)
    await sleep(15)
    await message_deleter(message, msg)


async def zip_pswd(client, message):
    global BOT
    if len(message.command) != 2:
        msg = await message.reply_text("Send\n/zipaswd <code>password</code>\nTo Set Password for Output Zip File. 🔐", quote=True)
    else:
        BOT.Options.zip_pswd = message.command[1]
        msg = await message.reply_text("Zip Password Has Been Successfully Set !", quote=True)
    await sleep(15)
    await message_deleter(message, msg)


async def unzip_pswd(client, message):
    global BOT
    if len(message.command) != 2:
        msg = await message.reply_text("Send\n/unzipaswd <code>password</code>\nTo Set Password for Extracting Archives. 🔓", quote=True)
    else:
        BOT.Options.unzip_pswd = message.command[1]
        msg = await message.reply_text("Unzip Password Has Been Successfully Set !", quote=True)
    await sleep(15)
    await message_deleter(message, msg)


async def help_command(client, message):
    msg = await message.reply_text(
        "Send /start To Check If I am alive 🤨\n\nSend /leech, /mirror etc. and follow prompts to start transloading 🚀\n\nSend /settings to edit bot settings ⚙️\n\nSend /setname To Set Custom File Name 📛\n\nSend /zipaswd To Set Password For Zip File 🔐\n\nSend /unzipaswd To Set Password to Extract Archives 🔓\n\n⚠️ **You can ALWAYS SEND an image To Set it as THUMBNAIL for your files 🌄**",
        quote=True,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Instructions 📖", url="https://github.com/XronTrix10/Telegram-Leecher/wiki/INSTRUCTIONS")],
            [InlineKeyboardButton("Channel 📣", url="https://t.me/Colab_Leecher"), InlineKeyboardButton("Group 💬", url="https://t.me/Colab_Leecher_Discuss")]
        ])
    )
    await sleep(15)
    await message_deleter(message, msg)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped.")
