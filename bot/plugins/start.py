import subprocess
import asyncio

from pyrogram import Client, filters
from pyrogram.errors import FloodWait, RPCError

from pyromod.helpers import ikb

from bot import BOT_ADMINS, DATABASE_CHANNEL, FORCE_SUB_, PROTECT_CONTENT


@Client.on_message(filters.command("start"))
async def start(client, message):
    START_MESSAGE = "**The bot is up and running. These bots can store messages in custom channels, and users access them through the bot.**"
    FORCE_MESSAGE = "**\n\nTo view messages shared by bots. Join first, then press the Try Again button.**" 

    user_id = message.from_user.id
    client.UserDB.insert_user(user_id)
    
    reply_markup = buttons(client, message)
    if len(message.command) > 1:
        if not await subscriber(client, message):
            await message.reply(START_MESSAGE + FORCE_MESSAGE, reply_markup=reply_markup, quote=True)
            return
        else:
            encoded_str = message.command[1]
            decoded_str = client.URLSafe.decode(encoded_str)
            argument = decoded_str.split("-")
            message_ids = []
            if len(argument) == 3:
                start, end = int(int(argument[1]) / abs(DATABASE_CHANNEL)), int(int(argument[2]) / abs(DATABASE_CHANNEL))
                message_ids = range(start, end + 1) if start <= end else range(start, end - 1, -1)
            elif len(argument) == 2:
                message_ids.append(int(int(argument[1]) / abs(DATABASE_CHANNEL)))

            msgs = await client.get_messages(DATABASE_CHANNEL, message_ids)
            for msg in msgs:
                try:
                    await msg.copy(user_id, protect_content=PROTECT_CONTENT)
                except FloodWait as e:
                    client.Logger.warning(e)
                    await asyncio.sleep(e.value)
            return
    else:
        await message.reply(START_MESSAGE, reply_markup=reply_markup, quote=True)


@Client.on_message(filters.command("restart") & filters.user(BOT_ADMINS))
async def restart(client, message):
    process_message = await message.reply("Restarting...", quote=True)
    
    with open("restart.txt", "w") as f:
        f.write(f"{message.chat.id}\n{process_message.id}")
    
    subprocess.run(["python", "-m", "bot"])


def buttons(client, message):
    if FORCE_SUB_:
        dynamic_buttons = []
        current_rows = []
        for key in FORCE_SUB_.keys():
            current_rows.append((f"Join {key}", getattr(client, f"FORCE_SUB_{key}"), "url"))
            
            if len(current_rows) == 3:
                dynamic_buttons.append(current_rows)
                current_rows = []
        
        if current_rows:
            dynamic_buttons.append(current_rows)
            
        try:
            dynamic_buttons.append(
                [("Try Again", f"t.me/{client.me.username}?start={message.command[1]}", "url")]
            )
        except Exception:
            pass

        return ikb(dynamic_buttons)


async def subscriber(client, message):
    user_id = message.from_user.id
    if user_id in BOT_ADMINS:
        return True

    for key, chat_id in FORCE_SUB_.items():
        try: 
            await client.get_chat_member(chat_id, user_id)
        except RPCError:
            return False

    return True