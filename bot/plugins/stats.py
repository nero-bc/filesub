import os
import time

from pyrogram import Client, filters

from bot import BOT_ADMINS


@Client.on_message(filters.command("ping"))
async def ping(_, message):
    start_time = time.time()
    processing = await message.reply("...", quote=True)
    result_time = time.time() - start_time
    await processing.edit(f"Latency: {result_time * 1000:.3f} ms")


@Client.on_message(filters.command("users") & filters.user(BOT_ADMINS))
async def users(client, message):
    processing = await message.reply("...", quote=True)
    total_users = len(client.UserDB.all_users())
    await processing.edit(f"{total_users} users")


@Client.on_message(filters.command("log") & filters.user(BOT_ADMINS))
async def log(_, message):
    if os.path.exists("log.txt"):
        await message.reply_document("log.txt", quote=True)
        os.remove("log.txt")
    else:
        await message.reply("Currently no logs exist.", quote=True)
