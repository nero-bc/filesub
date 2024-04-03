import os
import logging
import uvloop
import base64

from pymongo import MongoClient

from pyromod import Client

from pyrogram.types import BotCommand
from pyrogram.enums import ParseMode

logging.basicConfig(level=logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
LOGGER = logging.getLogger("FSub")

API_ID    = int(os.environ.get("API_ID", 2040))
API_HASH  = os.environ.get("API_HASH", "b18441a1ff607e10a989891a5462e627")
BOT_TOKEN = os.getenv("BOT_TOKEN")


DATABASE_NAME = BOT_TOKEN.split(":", 1)[0]
DATABASE_URL  = os.getenv("DATABASE_URL")

CHANNEL_DB = int(os.getenv("CHANNEL_DB"))

ADMINS = [int(i) for i in os.getenv("ADMINS").split()]

FORCE_SUB_TOTAL = 1
FORCE_SUB_      = {}
while True:
    key   = f"FORCE_SUB_{FORCE_SUB_TOTAL}"
    value = os.environ.get(key)
    if value is None:
        break
    FORCE_SUB_[FORCE_SUB_TOTAL] = int(value)
    FORCE_SUB_TOTAL += 1

PROTECT_CONTENT = eval(os.environ.get("PROTECT_CONTENT", "True"))


class UserDB:
    def __init__(self, database_url, database_name):
        self.dbclient = MongoClient(database_url)
        self.database = self.dbclient[database_name]
        self.user_data = self.database['users']

    def add(self, user_id: int):
        if not self.user_data.find_one({'_id': user_id}):
            self.user_data.insert_one({'_id': user_id})
            LOGGER.info(f"{user_id} ditambahkan ke database.")
        else:
            return None

    def all(self):
        users = self.user_data.find()
        user_id = [user['_id'] for user in users]
        return user_id

    def delete(self, user_id: int):
        self.user_data.delete_one({'_id': user_id})
        LOGGER.info(f"{user_id} dihapus dari database.")

UserDB = UserDB(DATABASE_URL, DATABASE_NAME)


class StrTools:
    def __init__(self):
        pass

    def encoder(self, string):
        string_bytes = string.encode("ascii")
        base64_bytes = base64.urlsafe_b64encode(string_bytes)
        base64_string = (base64_bytes.decode("ascii")).strip("=")
        return base64_string

    def decoder(self, base64_string):
        base64_string = base64_string.strip("=")
        base64_bytes = (base64_string + "=" * (-len(base64_string) % 4)).encode("ascii")
        string_bytes = base64.urlsafe_b64decode(base64_bytes)
        decode_string = string_bytes.decode("ascii")
        return decode_string

StrTools = StrTools()


class FSub(Client):
    def __init__(self):
        super().__init__(
            name       = "Bot",
            api_id     = API_ID, 
            api_hash   = API_HASH,
            bot_token  = BOT_TOKEN,
            in_memory  = True,
            parse_mode = ParseMode.MARKDOWN,
            plugins    = dict(root="FSub/plugins"))

    async def start(self):
        uvloop.install()
        try:
            await super().start()
            get_bot_profile = await self.get_me()
            self.bot_logger = LOGGER
            self.username   = get_bot_profile.username
            self.bot_logger.info(f"Memulai bot: @{self.username} (ID: {get_bot_profile.id})")
        except Exception as e:
            LOGGER.error(e)
            exit()
        
        try:
            self.bot_logger.info("Menyetel perintah bot...")
            await self.set_bot_commands([
                BotCommand("start", "Mulai bot"),
                BotCommand("ping", "Periksa latensi bot"),
                BotCommand("batch", "[Admin] Pesan massal"),
                BotCommand("broadcast", "[Admin] Kirim pesan siaran"),
                BotCommand("users", "[Admin] Periksa jumlah pengguna bot"),
                BotCommand("restart", "[Admin] Mulai ulang bot")])
            self.bot_logger.info("Perintah bot berhasil disetel.")
        except Exception as e:
            self.bot_logger.error(e)
            pass

        for key, chat_id in FORCE_SUB_.items():
            try:
                self.bot_logger.info(f"Memeriksa akses bot di FORCE_SUB_{key}...")
                get_chat    = await self.get_chat(chat_id)
                invite_link = get_chat.invite_link
                if not invite_link:
                    await self.export_chat_invite_link(chat_id)
                    invite_link = get_chat.invite_link
                setattr(self, f"FORCE_SUB_{key}", invite_link)
                self.bot_logger.info(f"FORCE_SUB_{key} terdeteksi: {get_chat.title} (ID: {get_chat.id})")
            except Exception as e:
                self.bot_logger.error(e)
                self.bot_logger.error(f"@{self.username} tidak memiliki akses mengundang pengguna dengan tautan di FORCE_SUB_{key}. Pastikan FORCE_SUB_{key} diisi dengan benar dan bot menjadi admin serta diberi akses mengundang pengguna dengan tautan.")
                exit()

        try:
            self.bot_logger.info("Memeriksa akses bot di CHANNEL_DB...")
            hello_world = await self.send_message(CHANNEL_DB, "Hello World!") ; await hello_world.delete()
            get_chat    = await self.get_chat(CHANNEL_DB)
            self.bot_logger.info(f"CHANNEL_DB terdeteksi: {get_chat.title} (ID: {get_chat.id})")
        except Exception as e:
            self.bot_logger.error(e)
            self.bot_logger.error(f"@{self.username} tidak memiliki akses/tidak berhasil mengirim pesan di CHANNEL_DB. Pastikan CHANNEL_DB diisi dengan benar dan bot menjadi admin serta diberi akses mengirim pesan.")
            exit()
        
        if os.path.exists('restart.txt'):
            with open('restart.txt', 'r') as f:
                chat_id    = int(f.readline().strip())
                message_id = int(f.readline().strip())
                await self.edit_message_text(chat_id, message_id, "Bot dimulai ulang.")
            
            os.remove('restart.txt')

        self.bot_logger.info("Bot berhasil diaktifkan!")
    
    async def stop(self, *args):
        await super().stop()
        self.bot_logger.warning("Bot telah berhenti!")
    
FSub = FSub()
