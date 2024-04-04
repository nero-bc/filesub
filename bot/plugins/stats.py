import time

from pyrogram import Client, filters

from bot import ADMINS


@Client.on_message(filters.command("ping"))
async def ping(_, message):
    start_time = time.time()
    processing = await message.reply("...", quote=True)
    result_time = time.time() - start_time
    await processing.edit(f"Latensi: {result_time * 1000:.3f} ms")


@Client.on_message(filters.command("users") & filters.user(ADMINS))
async def users(client, message):
    processing = await message.reply("...", quote=True)
    total_users = len(client.db.all_users())
    await processing.edit(f"{total_users} pengguna")


@Client.on_message(filters.command("log") & filters.user(ADMINS))
async def log(_, message):
    await message.reply_document("log.txt", quote=True)
