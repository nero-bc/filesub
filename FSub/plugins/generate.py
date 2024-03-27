import asyncio

from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from FSub import ADMINS, CHANNEL_DB, StrTools


@Client.on_message(filters.private & filters.user(ADMINS) & ~filters.command(["start", "ping", "batch", "broadcast", "users", "restart"]))
async def generate_command(client, message):
    generate = await message.reply("...", quote=True)
    await asyncio.sleep(0.25)
    copied   = await message.copy(chat_id=CHANNEL_DB, disable_notification=True)
    
    converted_id   = copied.id * abs(CHANNEL_DB)
    text_string    = f"get-{converted_id}"
    base64_string  = StrTools.encoder(text_string)
    generated_link = f"t.me/{client.username}?start={base64_string}"
    share_button   = InlineKeyboardMarkup([[InlineKeyboardButton("Bagikan", url=f't.me/share/url?url={generated_link}')]])
    return await generate.edit(generated_link, reply_markup=share_button, disable_web_page_preview=True)