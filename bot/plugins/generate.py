from pyrogram import Client, filters

from pyromod.helpers import ikb

from bot import BOT_ADMINS, DATABASE_CHANNEL, LIST_COMMANDS


@Client.on_message(~filters.command(LIST_COMMANDS) & filters.private & filters.user(BOT_ADMINS))
async def generate(client, message):
    copied_message = await message.copy(chat_id=DATABASE_CHANNEL, disable_notification=True)
    
    data = f"id-{copied_message.id * abs(DATABASE_CHANNEL)}"
    encoded_str = client.URLSafe.encode(data)
    
    generated_link = f"t.me/{client.me.username}?start={encoded_str}"
    reply_markup = ikb([
        [("Share", f"t.me/share/url?url={generated_link}", "url")]
    ])
    
    await message.reply(
        generated_link,
        reply_markup=reply_markup,
        quote=True,
        disable_web_page_preview=True
    )