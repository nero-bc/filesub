import asyncio

from pyrogram import Client, filters
from pyrogram.errors import FloodWait, MessageEmpty, UserNotParticipant
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from FSub import ADMINS, CHANNEL_DB, FORCE_SUB_, PROTECT_CONTENT, UserDB, StrTools


def FButton(client, message):
    if FORCE_SUB_:
        dynamic_button = []
        current_row = []
        for key in FORCE_SUB_.keys():
            current_row.append(InlineKeyboardButton(f"Join {key}", url=getattr(client, f"FORCE_SUB_{key}")))
            
            if len(current_row) == 3:
                dynamic_button.append(current_row)
                current_row = []
        
        if current_row:
            dynamic_button.append(current_row)
            
        try:
            dynamic_button.append([InlineKeyboardButton("Coba Lagi", url=f"t.me/{client.username}?start={message.command[1]}")])
        except: pass

        return dynamic_button


def FSubs(filter, client, update):
    user_id = update.from_user.id
    if user_id in ADMINS:
        return True
    for key, chat_id in FORCE_SUB_.items():
        try: client.get_chat_member(chat_id, user_id)
        except (UserNotParticipant, Exception):
            return False

    return True

isSubs = filters.create(FSubs)


START_STRING = "**Bot aktif dan berfungsi. Bot ini dapat menyimpan pesan di kanal khusus, dan pengguna mengakses melalui bot.**"
FSUB_STRING  = "**\n\nUntuk melihat pesan yang dibagikan oleh bot. Join terlebih dahulu, lalu tekan tombol Coba Lagi.**" 


@Client.on_message(filters.command("start") & filters.private & ~isSubs)
async def start_command_0(client, message):
    processing = await message.reply("...", quote=True)
    user_id = message.chat.id
    buttons = FButton(client, message)
    UserDB.add(user_id)
    if len(message.text) > 7:
        await processing.edit(START_STRING + FSUB_STRING, reply_markup=InlineKeyboardMarkup(buttons))
        return await message.delete()
    else:
        await processing.edit(START_STRING, reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_message(filters.command("start") & filters.private & isSubs)
async def start_command_1(client, message):
    processing = await message.reply("...", quote=True)
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
            except (MessageEmpty, Exception):
                pass
        await processing.delete() ; return await message.delete() 
    else:
        await processing.edit(START_STRING, reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_message(filters.command("restart") & filters.private & filters.user(ADMINS))
async def restart_command(client, message):
    import subprocess
    processing = await message.reply("Memulai ulang...", quote=True)
    with open('restart.txt', 'w') as f:
        f.write(f"{message.chat.id}\n{processing.id}")
    client.bot_logger.info("Memulai ulang bot...")
    subprocess.run(["python", "-m", "FSub"])