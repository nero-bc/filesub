import asyncio

from pyromod.helpers import ikb

from pyrogram import Client, filters
from pyrogram.errors import FloodWait, MessageEmpty, UserNotParticipant
from pyrogram.types import Message

from FSub import ADMINS, CHANNEL_DB, FORCE_SUB_, PROTECT_CONTENT, UserDB, StrTools


def FButton(client, message):
    if FORCE_SUB_:
        dynamic_button = []
        current_row = []
        for key in FORCE_SUB_.keys():
            current_row.append((f"Join {key}", getattr(client, f"FORCE_SUB_{key}"), "url"))
            
            if len(current_row) == 3:
                dynamic_button.append(current_row)
                current_row = []
        
        if current_row:
            dynamic_button.append(current_row)
            
        try:
            dynamic_button.append([("Coba Lagi", f"t.me/{client.username}?start={message.command[1]}", "url")])
        except:
            pass

        return ikb(dynamic_button)


async def is_subscriber(client, message):
    user_id = message.chat.id
    if user_id in ADMINS:
        return True

    for key, chat_id in FORCE_SUB_.items():
        try: 
            await client.get_chat_member(chat_id, user_id)
        except(UserNotParticipant, Exception):
            return False
    
    return True


START_STRING = "**Bot aktif dan berfungsi. Bot ini dapat menyimpan pesan di kanal khusus, dan pengguna mengakses melalui bot.**"
FSUB_STRING = "**\n\nUntuk melihat pesan yang dibagikan oleh bot. Join terlebih dahulu, lalu tekan tombol Coba Lagi.**" 

@Client.on_message(filters.command("start") & filters.private)
async def start_command(client, message):
    processing = await message.reply("...", quote=True)
    user_id = message.chat.id
    buttons = FButton(client, message)
    UserDB.add(user_id)
    text = message.text
    if len(text) > 7:
        if not await is_subscriber(client, message):
            await processing.edit(START_STRING + FSUB_STRING, reply_markup=buttons)
            return await message.delete()
        else:
            base64_string = text.split(" ", 1)[1]
            string = StrTools.decoder(base64_string)
            argument = string.split("-")
            message_ids = []
            if len(argument) == 3:
                start = int(int(argument[1]) / abs(CHANNEL_DB))
                end = int(int(argument[2]) / abs(CHANNEL_DB))
                message_ids = range(start, end + 1) if start <= end else range(start, end - 1, -1)
            elif len(argument) == 2:
                message_ids.append(int(int(argument[1]) / abs(CHANNEL_DB)))

            msgs = await client.get_messages(CHANNEL_DB, message_ids)
            for msg in msgs:
                try:
                    await msg.copy(user_id, protect_content=PROTECT_CONTENT)
                    await asyncio.sleep(0.25)
                except FloodWait as e:
                    await asyncio.sleep(e.value)
                except (MessageEmpty, Exception):
                    pass
            await processing.delete()
            return await message.delete() 
    else:
        await processing.edit(START_STRING, reply_markup=buttons)


@Client.on_message(filters.command("restart") & filters.private & filters.user(ADMINS))
async def restart_command(client, message):
    import subprocess
    processing = await message.reply("Memulai ulang...", quote=True)
    with open('restart.txt', 'w') as f:
        f.write(f"{message.chat.id}\n{processing.id}")
    client.bot_logger.info("Memulai ulang bot...")
    subprocess.run(["python", "-m", "FSub"])