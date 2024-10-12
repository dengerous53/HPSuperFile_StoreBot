import asyncio
from configs import Config
from pyrogram import Client
from pyrogram.types import Message
from pyrogram.errors import FloodWait, MessageDeleteForbidden
from handlers.helpers import str_to_b64
import logging

logging.basicConfig(level=logging.INFO)

async def reply_forward(message: Message, file_id: int):
    try:
        reply = await message.reply_text(
            f"**Files will be Deleted After 01 min ⏰**",
            disable_web_page_preview=True,
            quote=True
        )
        return reply
    except FloodWait as e:
        logging.warning(f"FloodWait: {e}")
        await asyncio.sleep(e.value)
        return await reply_forward(message, file_id)
    except Exception as e:
        logging.error(f"Error: {e}")

async def media_forward(bot: Client, user_id: int, file_id: int):
    try:
        if Config.FORWARD_AS_COPY is True:
            return await bot.copy_message(
                chat_id=user_id,
                from_chat_id=Config.DB_CHANNEL,
                message_id=file_id
            )
        elif Config.FORWARD_AS_COPY is False:
            return await bot.forward_messages(
                chat_id=user_id,
                from_chat_id=Config.DB_CHANNEL,
                message_ids=file_id
            )
    except FloodWait as e:
        logging.warning(f"FloodWait: {e}")
        await asyncio.sleep(e.value)
        return media_forward(bot, user_id, file_id)
    except Exception as e:
        logging.error(f"Error: {e}")

async def send_media_and_reply(bot: Client, user_id: int, file_id: int):
    try:
        sent_message = await media_forward(bot, user_id, file_id)
        reply_message = await reply_forward(sent_message, file_id)
        reply_message_text = "**File Deleted By @Moviesss4ers 🏆**"
        asyncio.create_task(delete_after_delay(reply_message, sent_message, 60, reply_message_text))
    except Exception as e:
        logging.error(f"Error: {e}")

async def delete_after_delay(message, file_message, delay, reply_message_text):
    try:
        await asyncio.sleep(delay)
        await file_message.delete()
        if message:
            try:
                await message.edit_text(reply_message_text)
            except MessageDeleteForbidden:
                logging.warning("Message deletion forbidden")
        else:
            logging.warning("Message not found")
    except Exception as e:
        logging.error(f"Error: {e}")
