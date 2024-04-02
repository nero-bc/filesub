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
    await processing.edit(f"Latensi: {result_time * 1000:.3f} ms")


@Client.on_message(filters.command("users") & filters.private & filters.user(ADMINS))
async def users_command(_, message):
    processing  = await message.reply("...", quote=True)
    total_users = len(UserDB.all())
    await processing.edit(f"{total_users} pengguna")