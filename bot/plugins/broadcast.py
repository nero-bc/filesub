import os
import asyncio

from pyrogram import Client, filters
from pyrogram.errors import FloodWait, RPCError

from bot import BOT_ADMINS, PROTECT_CONTENT

BROADCASTING, succeeded, failed, total_users = False, 0, 0, 0


@Client.on_message(filters.command("broadcast") & filters.user(BOT_ADMINS))
async def broadcast(client, message):
    global BROADCASTING, succeeded, failed, total_users
    
    RUNNING_MESSAGE = "Broadcast is running, wait until the task is finished.\n\n**/status:** Show broadcast status."

    if not message.reply_to_message:
        if not BROADCASTING:
            await message.reply("Please reply to a message you want to broadcast.", quote=True)
            BROADCASTING, succeeded, failed, total_users = False, 0, 0, 0
        else:
            await message.reply(RUNNING_MESSAGE, quote=True)
            
        return
    else:
        if not BROADCASTING:
            BROADCASTING, succeeded, failed, total_users = True, 0, 0, 0
            broadcast_message = message.reply_to_message
        else:
            await message.reply(RUNNING_MESSAGE, quote=True)
            return

    process_message = await message.reply("Sending...", quote=True)
    
    with open("broadcast.txt", "w") as f:
        f.write(f"{message.chat.id}\n{process_message.id}")

    all_users = client.UserDB.all_users()
    total_users = len(all_users)
    
    for user_id in all_users:
        if not BROADCASTING:
            break
        
        if user_id in BOT_ADMINS:
            continue
        
        try:
            await broadcast_message.copy(user_id, protect_content=PROTECT_CONTENT)
            succeeded += 1
        except FloodWait as e:
            client.Logger.warning(e)
            await asyncio.sleep(e.value)
        except RPCError:
            client.UserDB.delete_user(user_id)
            failed += 1
    
        if (succeeded + failed) % 25 == 0:
            await process_message.edit(f"**Broadcast Running**\n - Sent: {succeeded}/{total_users}\n - Failed: {failed}\n\n**/cancel:** Cancel the process.")
    
    if not BROADCASTING:
        await message.reply(f"**Broadcast Aborted**\n - Sent: {succeeded}/{total_users}\n - Failed: {failed}", quote=True)
    else:
        await message.reply(f"**Broadcast Finished**\n - Succeeded: {succeeded}\n - Failed: {failed}", quote=True)
    
    BROADCASTING, succeeded, failed, total_users = False, 0, 0, 0
    
    if os.path.exists("broadcast.txt"):
        os.remove("broadcast.txt")

    await process_message.delete()


@Client.on_message(filters.command("status") & filters.user(BOT_ADMINS))
async def status(_, message):
    global BROADCASTING, succeeded, failed, total_users

    if not BROADCASTING:
        await message.reply("No broadcast is running.", quote=True)
    else:
        await message.reply(f"**Broadcast Status**\n - Sent: {succeeded}/{total_users}\n - Failed: {failed}", quote=True)


@Client.on_message(filters.command("cancel") & filters.user(BOT_ADMINS))
async def cancel(client, message):
    global BROADCASTING
    
    if not BROADCASTING:
        await message.reply("No broadcast is running.", quote=True)
    else:
        approval_message = await client.ask(
            text="Are you sure you want to cancel the broadcast process?\n\n**/yes** or **/no**",
            chat_id=message.chat.id
        )
        if approval_message.text and approval_message.text == "/yes":
            await approval_message.reply("Broadcast has been aborted.", quote=True)
            BROADCASTING = False
            if os.path.exists("broadcast.txt"):
                os.remove("broadcast.txt")
        elif approval_message.text and approval_message.text == "/no":
            await approval_message.reply("Broadcast cancellation is not approved.", quote=True)
        else:
            await approval_message.reply("The message is invalid.", quote=True)

    return
