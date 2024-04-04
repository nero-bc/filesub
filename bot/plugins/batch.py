from pyrogram import Client, filters
from pyrogram.helpers import ikb

from bot import ADMINS, CHANNEL_DB


@Client.on_message(filters.command("batch") & filters.private & filters.user(ADMINS))
async def batch(client, message):
    INVALID_MESSAGE = "Pesan tidak valid atau pesan yang diteruskan bukan dari CHANNEL_DB."
    first_message = await client.ask(text="Pesan awal: Teruskan pesan dari CHANNEL_DB.", chat_id=message.chat.id)
    if first_message.forward_from_chat and first_message.forward_from_chat.id == CHANNEL_DB:
        first_message_id = first_message.forward_from_message_id
    else:
        await first_message.reply(INVALID_MESSAGE, quote=True)
        return

    while True:
        last_message = await client.ask(text="Pesan akhir: Teruskan pesan dari CHANNEL_DB.", chat_id=message.chat.id)
        if last_message.forward_from_chat and last_message.forward_from_chat.id == CHANNEL_DB:
            last_message_id = last_message.forward_from_message_id
            break
        else:
            await last_message.reply(INVALID_MESSAGE, quote=True)
            return

    data = f"id-{first_message_id * abs(CHANNEL_DB)}-{last_message_id * abs(CHANNEL_DB)}"
    encoded_str = client.url.encode(data)
    
    generated_link = f"t.me/{client.username}?start={encoded_str}"
    reply_markup = ikb([[("Bagikan", f"t.me/share/url?url={generated_link}", "url")]])
    await last_message.reply(generated_link, reply_markup=reply_markup, quote=True, disable_web_page_preview=True)