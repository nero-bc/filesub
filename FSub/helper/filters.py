from pyrogram.errors import UserNotParticipant
from FSub import ADMINS, FORCE_SUB_


def fsub_subscriber(filter, client, update):
    user_id = update.from_user.id
    if user_id in ADMINS:
        return True
    for key, chat_id in FORCE_SUB_.items():
        try: client.get_chat_member(chat_id, user_id)
        except UserNotParticipant: return False
        except Exception: return False
    
    return True