import asyncio

from pyrogram import Client, filters
from pyrogram.errors import FloodWait, RPCError

from bot import ADMINS, PROTECT_CONTENT


@Client.on_message(filters.command("broadcast") & filters.user(ADMINS))
async def broadcast(client, message):
    if not message.reply_to_message:
        broadcast_ask = await client.ask(text="Silahkan kirim pesan yang ingin disiarkan.\n\n/cancel untuk membatalkan.", chat_id=message.chat.id)
        if broadcast_ask.text == "/cancel":
            await message.reply("Proses dibatalkan.")
            return
        else:
            broadcast_message = broadcast_ask
    else:
        broadcast_message = message.reply_to_message

    processing = await message.reply("Terkirim: ...", quote=True)

    client.log.info("Mengirim pesan siaran...")
    
    successful, unsuccessful = 0, 0
    total_users = len(client.db.all_users())
    
    async def edit_processing():
        while successful + unsuccessful < total_users:
            try:
                await asyncio.sleep(5)
                await processing.edit(f"Terkirim: {successful}/{total_users}")
                client.log.info(f"BROADCAST: Terkirim: {successful}/{total_users}")
            except FloodWait as e:
                await asyncio.sleep(e.value)
                client.log.warning(f"BROADCAST: FloodWait: Bot dijeda selama {e.value} detik")
            except RPCError:
                pass

    asyncio.create_task(edit_processing())
    
    for user_id in client.db.all_users():
        if user_id in ADMINS:
            continue
        try:
            await broadcast_message.copy(user_id, protect_content=PROTECT_CONTENT)
            successful += 1
        except FloodWait as e:
            await asyncio.sleep(e.value)
            client.log.warning(f"BROADCAST: FloodWait: Bot dijeda selama {e.value} detik")
        except RPCError:
            client.db.delete_user(user_id)
            unsuccessful += 1

    status_broadcast = f"#BROADCAST\n - Berhasil: {successful}\n - Gagal: {unsuccessful}"
    
    client.log.info("Pesan siaran telah dikirim")
    
    await message.reply(status_broadcast, quote=True)
    return await processing.delete()
