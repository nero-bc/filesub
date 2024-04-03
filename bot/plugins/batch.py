from pyrogram import Client, filters

from pyromod.helpers import ikb

from bot import BOT_ADMINS, DATABASE_CHANNEL


@Client.on_message(filters.command("batch") & filters.private & filters.user(BOT_ADMINS))
async def batch(client, message):
    INVALID_MESSAGE = "The message is invalid or the message being forwarded is not from the DATABASE CHANNEL."
    
    initial_message = await client.ask(
        text="**Initial Message:** Forward message from DATABASE_CHANNEL.", 
        chat_id=message.chat.id
    )
    if initial_message.forward_from_chat and initial_message.forward_from_chat.id == DATABASE_CHANNEL:
        initial_message_id = initial_message.forward_from_message_id
    else:
        await initial_message.reply(INVALID_MESSAGE, quote=True)
        return

    while True:
        last_message = await client.ask(
            text="**Last Message:** Forward message from DATABASE_CHANNEL.",
            chat_id=message.chat.id
        )
        if last_message.forward_from_chat and last_message.forward_from_chat.id == DATABASE_CHANNEL:
            last_message_id = last_message.forward_from_message_id
            break
        else:
            await last_message.reply(INVALID_MESSAGE, quote=True)
            return

    data = f"id-{initial_message_id * abs(DATABASE_CHANNEL)}-{last_message_id * abs(DATABASE_CHANNEL)}"
    encoded_str = client.URLSafe.encode(data)
    
    generated_link = f"t.me/{client.me.username}?start={encoded_str}"
    reply_markup = ikb([
        [("Share", f"t.me/share/url?url={generated_link}", "url")]
    ])

    await last_message.reply(
        generated_link,
        reply_markup=reply_markup,
        quote=True, 
        disable_web_page_preview=True
    )