import time
import asyncio

from pyrogram import Client, filters
from pyrogram.types import Message

from FSub import ADMINS, UserDB


@Client.on_message(filters.command("ping") & filters.private)
async def ping_command(_, message):
    start_time  = time.time()
    processing  = await message.reply("...", quote=True)
    result_time = time.time() - start_time
    await asyncio.sleep(0.25)
    return await processing.edit(f"Latensi: {result_time * 1000:.3f} ms")


@Client.on_message(filters.command("users") & filters.private & filters.user(ADMINS))
async def users_command(_, message):
    processing = await message.reply("...", quote=True)
    await asyncio.sleep(0.25)
    return await processing.edit(f"{len(UserDB.all())} pengguna")