import asyncio

from pyrogram import Client, filters
from pyrogram.helpers import ikb

from bot import ADMINS, CHANNEL_DB, COMMANDS


@Client.on_message(~filters.command(COMMANDS) & filters.private & filters.user(ADMINS))
async def generate(client, message):
    copied = await message.copy(chat_id=CHANNEL_DB, disable_notification=True)
    
    data = f"id-{copied.id * abs(CHANNEL_DB)}"
    encoded_str = client.url.encode(data)
    
    generated_link = f"t.me/{client.username}?start={encoded_str}"
    reply_markup = ikb([[("Bagikan", f"t.me/share/url?url={generated_link}", "url")]])
    await message.reply(generated_link, reply_markup=reply_markup, quote=True, disable_web_page_preview=True)