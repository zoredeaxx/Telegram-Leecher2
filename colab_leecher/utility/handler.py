# copyright 2023 © Xron Trix | https://github.com/Xrontrix10

import os
import shutil
import logging
import pathlib
from asyncio import sleep
from time import time
from natsort import natsorted
from datetime import datetime
from os import makedirs, path as ospath

# 'colab_bot' is removed from this import
from colab_leecher import OWNER

from colab_leecher.uploader.telegram import upload_file
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from colab_leecher.utility.variables import (
    BOT,
    MSG,
    BotTimes,
    Messages,
    Paths,
    Transfer,
    TaskError,
)
from colab_leecher.utility.converters import (
    archive,
    extract,
    videoConverter,
    sizeChecker,
)
from colab_leecher.utility.helper import (
    fileType,
    getSize,
    getTime,
    keyboard,
    shortFileName,
    sizeUnit,
    sysINFO,
)


async def Leech(folder_path: str, remove: bool):
    global BOT, BotTimes, Messages, Paths, Transfer
    files = [str(p) for p in pathlib.Path(folder_path).glob("**/*") if p.is_file()]
    for f in natsorted(files):
        file_path = ospath.join(folder_path, f)
        if BOT.Options.convert_video and fileType(file_path) == "video":
            file_path = await videoConverter(file_path)

    Transfer.total_down_size = getSize(folder_path)
    files = [str(p) for p in pathlib.Path(folder_path).glob("**/*") if p.is_file()]
    for f in natsorted(files):
        file_path = ospath.join(folder_path, f)
        leech = await sizeChecker(file_path, remove)

        if leech:
            if ospath.exists(file_path) and remove:
                os.remove(file_path)
            dir_list = natsorted(os.listdir(Paths.temp_zpath))
            count = 1
            for dir_path in dir_list:
                short_path = ospath.join(Paths.temp_zpath, dir_path)
                file_name = ospath.basename(short_path)
                new_path = shortFileName(short_path)
                os.rename(short_path, new_path)
                BotTimes.current_time = time()
                Messages.status_head = f"<b>📤 UPLOADING SPLIT » {count} OF {len(dir_list)} Files</b>\n\n<code>{file_name}</code>\n"
                try:
                    MSG.status_msg = await MSG.status_msg.edit_text(
                        text=Messages.task_msg + Messages.status_head + "\n⏳ __Starting.....__" + sysINFO(),
                        reply_markup=keyboard(),
                    )
                except Exception as d:
                    logging.info(d)
                await upload_file(new_path, file_name)
                Transfer.up_bytes.append(os.stat(new_path).st_size)
                count += 1
            shutil.rmtree(Paths.temp_zpath)
        else:
            if not ospath.exists(Paths.temp_files_dir):
                makedirs(Paths.temp_files_dir)
            if not remove:
                file_path = shutil.copy(file_path, Paths.temp_files_dir)
            file_name = ospath.basename(file_path)
            new_path = shortFileName(file_path)
            os.rename(file_path, new_path)
            BotTimes.current_time = time()
            Messages.status_head = f"<b>📤 UPLOADING » </b>\n\n<code>{file_name}</code>\n"
            try:
                MSG.status_msg = await MSG.status_msg.edit_text(
                    text=Messages.task_msg + Messages.status_head + "\n⏳ __Starting.....__" + sysINFO(),
                    reply_markup=keyboard(),
                )
            except Exception as d:
                logging.error(f"Error updating status bar: {d}")
            file_size = os.stat(new_path).st_size
            await upload_file(new_path, file_name)
            Transfer.up_bytes.append(file_size)
            if remove:
                if ospath.exists(new_path):
                    os.remove(new_path)
            else:
                if ospath.exists(Paths.temp_files_dir):
                    shutil.rmtree(Paths.temp_files_dir)

    if remove and ospath.exists(folder_path):
        shutil.rmtree(folder_path)
    if ospath.exists(Paths.thumbnail_ytdl):
        shutil.rmtree(Paths.thumbnail_ytdl)
    if ospath.exists(Paths.temp_files_dir):
        shutil.rmtree(Paths.temp_files_dir)


async def Zip_Handler(down_path: str, is_split: bool, remove: bool):
    global BOT, Messages, MSG, Transfer
    Messages.status_head = f"<b>🔐 ZIPPING » </b>\n\n<code>{Messages.download_name}</code>\n"
    try:
        MSG.status_msg = await MSG.status_msg.edit_text(
            text=Messages.task_msg + Messages.status_head + sysINFO(),
            reply_markup=keyboard(),
        )
    except Exception as e2:
        logging.error(f"Problem in ZipLeech !{e2}")
    logging.info("\nNow ZIPPING the folder...")
    BotTimes.current_time = time()
    if not ospath.exists(Paths.temp_zpath):
        makedirs(Paths.temp_zpath)
    await archive(down_path, is_split, remove)
    await sleep(2)
    Transfer.total_down_size = getSize(Paths.temp_zpath)
    if remove and ospath.exists(down_path):
        shutil.rmtree(down_path)


async def Unzip_Handler(down_path: str, remove: bool):
    global MSG, Messages
    Messages.status_head = f"\n<b>📂 EXTRACTING » </b>\n\n<code>{Messages.download_name}</code>\n"
    MSG.status_msg = await MSG.status_msg.edit_text(
        text=Messages.task_msg + Messages.status_head + "\n⏳ __Starting.....__" + sysINFO(),
        reply_markup=keyboard(),
    )
    filenames = [str(p) for p in pathlib.Path(down_path).glob("**/*") if p.is_file()]
    for f in natsorted(filenames):
        short_path = ospath.join(down_path, f)
        if not ospath.exists(Paths.temp_unzip_path):
            makedirs(Paths.temp_unzip_path)
        filename = ospath.basename(f).lower()
        _, ext = ospath.splitext(filename)
        try:
            if ospath.exists(short_path):
                if ext in [".7z", ".gz", ".zip", ".rar", ".001", ".tar", ".z01"]:
                    await extract(short_path, remove)
                else:
                    shutil.copy(short_path, Paths.temp_unzip_path)
        except Exception as e5:
            logging.error(f"UZLeech Launcher Exception: {e5}")
    if remove:
        shutil.rmtree(down_path)


async def cancelTask(bot_client, Reason: str):
    text = f"#TASK_STOPPED\n\n**╭🔗 Source » **__[Here]({Messages.src_link})__\n**├🦄 Mode » **__{BOT.Mode.mode.capitalize()}__\n**├🤔 Reason » **__{Reason}__\n**╰🍃 Spent Time » **__{getTime((datetime.now() - BotTimes.start_time).seconds)}__"
    if BOT.State.task_going:
        try:
            if BOT.TASK:
                BOT.TASK.cancel()
            if ospath.exists(Paths.WORK_PATH):
                shutil.rmtree(Paths.WORK_PATH)
        except Exception as e:
            logging.error(f"Error during task cancellation: {e}")
        finally:
            BOT.State.task_going = False
            if MSG.status_msg:
                await MSG.status_msg.delete()
            await bot_client.send_message(
                chat_id=OWNER,
                text=text,
                reply_markup=InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton("Channel 📣", url="https://t.me/Colab_Leecher"),
                        InlineKeyboardButton("Group 💬", url="https://t.me/Colab_Leecher_Discuss"),
                    ],
                ]),
            )


async def SendLogs(bot_client, is_leech: bool):
    global Transfer, Messages, BOT, MSG, TaskError
    
    if TaskError.state:
        final_text = f"<b>#ERROR: Task failed!</b>\n\n<b>Reason:</b> <code>{TaskError.text}</code>"
    else:
        file_count_text = f"├<b>☘️ File Count » </b><code>{len(Transfer.sent_file)} Files</code>\n" if is_leech else ""
        size = sizeUnit(sum(Transfer.up_bytes)) if is_leech else sizeUnit(Transfer.total_down_size)
        
        final_text = (
            f"\n\n<b>#{(BOT.Mode.mode).upper()}_COMPLETE 🔥</b>\n\n"
            f"╭<b>📛 Name » </b><code>{Messages.download_name}</code>\n"
            f"├<b>📦 Size » </b><code>{size}</code>\n"
            f"{file_count_text}"
            f"╰<b>🍃 Saved Time »</b> <code>{getTime((datetime.now() - BotTimes.start_time).seconds)}</code>"
        )

    try:
        await MSG.status_msg.edit_text(
            text=Messages.task_msg + final_text,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Git Repo 🪲", url="https://github.com/XronTrix10/Telegram-Leecher")],
                [
                    InlineKeyboardButton("Channel 📣", url="https://t.me/Colab_Leecher"),
                    InlineKeyboardButton("Group 💬", url="https://t.me/Colab_Leecher_Discuss"),
                ],
            ]),
        )
    except Exception as e:
        logging.error(f"Could not edit final status message: {e}")

    if is_leech and not TaskError.state and Transfer.sent_file:
        try:
            log_header = f"<b>☘️ File Count:</b>  <code>{len(Transfer.sent_file)}</code>\n\n<b>📜 Logs:</b>"
            log_body = ""
            log_messages = []
            for i, sent_file_message in enumerate(Transfer.sent_file):
                file_link = f"https://t.me/c/{Messages.link_p}/{sent_file_message.id}"
                fileName = Transfer.sent_file_names[i]
                file_line = f"\n({str(i+1).zfill(2)}) <a href='{file_link}'>{fileName}</a>"
                if len(log_header + log_body + file_line) > 4096:
                    log_messages.append(log_header + log_body)
                    log_body = file_line
                else:
                    log_body += file_line
            log_messages.append(log_header + log_body)

            log_message_to_reply = MSG.status_msg
            for log_part in log_messages:
                log_message_to_reply = await log_message_to_reply.reply_text(text=log_part, quote=True)
        except Exception as e:
            logging.error(f"Error Sending file logs: {e}")
            await MSG.status_msg.reply_text(text=f"<b>Error Sending logs » </b><i>{e}</i>")

    BOT.State.started = False
    BOT.State.task_going = False
    TaskError.state = False
    TaskError.text = ""
