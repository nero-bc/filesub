from pyrogram import Client, filters
from pyrogram.types import Message

from pyromod.helpers import ikb

from FSub import ADMINS, CHANNEL_DB, StrTools


MESSAGE_INVALID = "Pesan tidak valid atau pesan yang diteruskan bukan dari CHANNEL_DB."

@Client.on_message(filters.command("batch") & filters.private & filters.user(ADMINS))
async def batch_command(client, message):
    first_message = await client.ask(text="Pesan awal: Teruskan pesan dari CHANNEL_DB.", chat_id=message.chat.id)
    if first_message.forward_from_chat and first_message.forward_from_chat.id == CHANNEL_DB:
        first_message_id = first_message.forward_from_message_id
        await first_message.sent_message.delete()
    else:
        return await first_message.reply(MESSAGE_INVALID, quote=True)

    while True:
        second_message = await client.ask(text="Pesan akhir: Teruskan pesan dari CHANNEL_DB.", chat_id=message.chat.id)
        if second_message.forward_from_chat and second_message.forward_from_chat.id == CHANNEL_DB:
            second_message_id = second_message.forward_from_message_id
            await second_message.sent_message.delete()
            break
        else:
            return await second_message.reply(MESSAGE_INVALID, quote=True)

    text_string = f"get-{first_message_id * abs(CHANNEL_DB)}-{second_message_id * abs(CHANNEL_DB)}"
    base64_string = StrTools.encoder(text_string)
    generated_link = f"t.me/{client.username}?start={base64_string}"
    share_button = ikb([[("Bagikan", f"t.me/share/url?url={generated_link}", "url")]])
    return await second_message.reply(generated_link, reply_markup=share_button, quote=True, disable_web_page_preview=True)