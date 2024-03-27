import asyncio

from pyrogram import Client, filters
from pyrogram.errors import FloodWait, MessageEmpty
from pyrogram.types import Message, InlineKeyboardMarkup

from FSub import ADMINS, CHANNEL_DB, PROTECT_CONTENT, UserDB, FButton, isSubs, StrTools


START_STRING = "**Bot aktif dan berfungsi. Bot ini dapat menyimpan pesan di kanal khusus, dan pengguna mengakses melalui bot.**"
FSUB_STRING  = "**\n\nUntuk melihat pesan yang dibagikan oleh bot. Join terlebih dahulu, lalu tekan tombol Coba Lagi.**" 

@Client.on_message(filters.command("start") & filters.private & ~isSubs)
async def start_command_0(client, message):
    processing = await message.reply("...", quote=True)
    await asyncio.sleep(0.25)
    user_id = message.chat.id
    buttons = FButton(client, message)
    UserDB.add(user_id)
    if len(message.text) > 7:
        await processing.edit(START_STRING + FSUB_STRING, reply_markup=InlineKeyboardMarkup(buttons))
        return await message.delete()
    else:
        return await processing.edit(START_STRING, reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_message(filters.command("start") & filters.private & isSubs)
async def start_command_1(client, message):
    processing = await message.reply("...", quote=True)
    await asyncio.sleep(0.25)
    user_id = message.chat.id
    buttons = FButton(client, message)
    UserDB.add(user_id)
    text = message.text
    if len(text) > 7:
        base64_string = text.split(" ", 1)[1]
        string   = StrTools.decoder(base64_string)
        argument = string.split("-")
        if len(argument) == 3:
            start = int(int(argument[1]) / abs(CHANNEL_DB))
            end   = int(int(argument[2]) / abs(CHANNEL_DB))
            if start <= end:
                message_ids = range(start, end + 1)
            else:
                message_ids = []
                i = start
                while True:
                    message_ids.append(i)
                    i -= 1
                    if i < end:
                        break
        elif len(argument) == 2:
            message_ids = [int(int(argument[1]) / abs(CHANNEL_DB))]

        msgs = await client.get_messages(CHANNEL_DB, message_ids)
        for msg in msgs:
            try:
                await msg.copy(user_id, protect_content=PROTECT_CONTENT)
                await asyncio.sleep(0.25)
            except FloodWait as e:
                await asyncio.sleep(e.value)
            except MessageEmpty:
                pass
        await message.delete() ; return await processing.delete()
    else:
        return await processing.edit(START_STRING, reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_message(filters.command("restart") & filters.private & filters.user(ADMINS))
async def restart_command(client, message):
    import subprocess
    processing = await message.reply("Memulai ulang...", quote=True)
    with open('restart.txt', 'w') as f:
        f.write(f"{message.chat.id}\n{processing.id}")
    client.bot_logger.info("Memulai ulang bot...")
    subprocess.run(["python", "-m", "FSub"])