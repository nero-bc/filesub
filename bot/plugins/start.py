import os
import subprocess

from pyrogram import Client, filters
from pyrogram.helpers import ikb
from pyrogram.errors import FloodWait, RPCError

from bot import ADMINS, CHANNEL_DB, FORCE_SUB_, PROTECT_CONTENT


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
            dynamic_buttons.append([("Coba Lagi", f"t.me/{client.username}?start={message.command[1]}", "url")])
        except Exception:
            pass

        return ikb(dynamic_buttons)


async def subscriber(client, message):
    user_id = message.from_user.id
    if user_id in ADMINS:
        return True

    for key, chat_id in FORCE_SUB_.items():
        try: 
            await client.get_chat_member(chat_id, user_id)
        except RPCError:
            return False

    return True


@Client.on_message(filters.command("start"))
async def start(client, message):
    START_MESSAGE = "**Bot aktif dan berfungsi. Bot ini dapat menyimpan pesan di kanal khusus, dan pengguna mengakses melalui bot.**"
    FORCE_MESSAGE = "**\n\nUntuk melihat pesan yang dibagikan oleh bot. Join terlebih dahulu, lalu tekan tombol Coba Lagi.**" 

    user_id = message.chat.id
    client.db.insert_user(user_id)

    reply_markup = buttons(client, message)
    if len(message.command) > 1:
        if not await subscriber(client, message):
            await message.reply(START_MESSAGE + FORCE_MESSAGE, reply_markup=reply_markup, quote=True)
            return
        else:
            encoded_str = message.command[1]
            decoded_str = client.url.decode(encoded_str)
            argument = decoded_str.split("-")
            message_ids = []
            if len(argument) == 3:
                start, end = int(int(argument[1]) / abs(CHANNEL_DB)), int(int(argument[2]) / abs(CHANNEL_DB))
                message_ids = range(start, end + 1) if start <= end else range(start, end - 1, -1)
            elif len(argument) == 2:
                message_ids.append(int(int(argument[1]) / abs(CHANNEL_DB)))

            msgs = await client.get_messages(CHANNEL_DB, message_ids)
            for msg in msgs:
                try:
                    await msg.copy(user_id, protect_content=PROTECT_CONTENT)
                except FloodWait as e:
                    await asyncio.sleep(e.value)
                    client.log.warning(f"START: FloodWait: Bot dijeda selama {e.value} detik.")
            return
    else:
        await message.reply(START_MESSAGE, reply_markup=reply_markup, quote=True)


@Client.on_message(filters.command("restart") & filters.user(ADMINS))
async def restart(client, message):
    REPO = "https://github.com/ugorwx/fsub"

    processing = await message.reply("Memulai ulang...", quote=True)
    
    if os.path.exists('log.txt'):
        os.remove('log.txt')
    
    client.log.info("Memulai ulang bot...")
    
    with open('restart.txt', 'w') as f:
        f.write(f"{message.chat.id}\n{processing.id}")

    if os.path.exists(".git"):
        client.log.info("Memperbarui repositori bot...")
        subprocess.run(["rm", "-fr", ".git"])
        update = subprocess.run(
            [
                f"git init -q; \
                git config --global user.email 'n/a'; \
                git config --global user.name 'n/a'; \
                git add .; \
                git commit -sm update -q; \
                git remote add origin {REPO}; \
                git fetch origin -q; \
                git reset --hard origin/debug -q"
            ],
            shell=True)
        if update.returncode == 0:
            client.log.info("Repositori bot berhasil diperbarui")
        else:
            client.log.warning("Repositori bot gagal diperbarui")
    
    client.log.info("Memperbarui dependencies bot...")
    subprocess.run(["pip", "install", "-Ur", "requirements.txt"])
    client.log.info("Dependencies bot berhasil diperbarui")
    subprocess.run(["python", "-m", "bot"])