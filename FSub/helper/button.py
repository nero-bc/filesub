from pyrogram.types import InlineKeyboardButton
from FSub import FORCE_SUB_


def fsub_button(client, message):
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