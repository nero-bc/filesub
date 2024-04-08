import os
import logging
import asyncio
import uvloop
import base64

from pymongo import MongoClient

from pyrogram import Client, idle
from pyrogram.types import BotCommand
from pyrogram.enums import ParseMode
from pyrogram.errors import RPCError

logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("log.txt"), logging.StreamHandler()],
    level=logging.INFO)


LOGGER = logging.getLogger("BOT")

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_DB = int(os.getenv("CHANNEL_DB"))

ADMINS = [int(i) for i in os.getenv("ADMINS").split()]

FORCE_SUB_TOTAL = 1
FORCE_SUB_ = {}
while True:
    key = f"FORCE_SUB_{FORCE_SUB_TOTAL}"
    value = os.environ.get(key)
    if value is None:
        break
    FORCE_SUB_[FORCE_SUB_TOTAL] = int(value)
    FORCE_SUB_TOTAL += 1

PROTECT_CONTENT = eval(os.environ.get("PROTECT_CONTENT", "True"))

DATABASE_NAME = BOT_TOKEN.split(":", 1)[0]
DATABASE_URL = os.getenv("DATABASE_URL")

BOT_COMMANDS = [
    BotCommand("start", "Mulai bot"),
    BotCommand("ping", "Periksa latensi bot"),
    BotCommand("batch", "[Admin] Pesan massal"),
    BotCommand("broadcast", "[Admin] Kirim pesan siaran"),
    BotCommand("users", "[Admin] Periksa jumlah pengguna bot"),
    BotCommand("log", "[Admin] Periksa log bot"),
    BotCommand("restart", "[Admin] Mulai ulang bot")]

COMMANDS = [command.command for command in BOT_COMMANDS]


class UserDB:
    def __init__(self, database_url, database_name):
        self.dbclient = MongoClient(database_url)
        self.database = self.dbclient[database_name]
        self.user_data = self.database['users']

    def insert_user(self, user_id: int):
        if not self.user_data.find_one({'_id': user_id}):
            self.user_data.insert_one({'_id': user_id})
            LOGGER.info(f"{user_id} ditambahkan ke database")

    def all_users(self):
        users = self.user_data.find()
        user_id = [user['_id'] for user in users]
        return user_id

    def delete_user(self, user_id: int):
        self.user_data.delete_one({'_id': user_id})
        LOGGER.info(f"{user_id} dihapus dari database")


class URLSafe:
    @staticmethod
    def encode(data):
        encoded_bytes = base64.urlsafe_b64encode(data.encode('utf-8'))
        encoded_str = str(encoded_bytes, 'utf-8').rstrip("=")
        return encoded_str

    @staticmethod
    def decode(data):
        padding_factor = (4 - len(data) % 4) % 4
        data += "=" * padding_factor
        decoded_bytes = base64.urlsafe_b64decode(data)
        decoded_str = str(decoded_bytes, 'utf-8')
        return decoded_str


class Bot(Client):
    def __init__(self):
        super().__init__(
            name = "bot",
            api_id = 2040,
            api_hash = "b18441a1ff607e10a989891a5462e627",
            bot_token = BOT_TOKEN,
            in_memory = True,
            parse_mode = ParseMode.MARKDOWN,
            plugins=dict(root="bot/plugins"))
    
    uvloop.install()

    async def start(self):
        LOGGER.info("Memeriksa kredensial bot...")
        try:
            await super().start()
            LOGGER.info("Bot telah dimulai")
            self.log = LOGGER
            self.db = UserDB(DATABASE_URL, DATABASE_NAME)
            self.url = URLSafe()
            self.username = self.me.username
            self.log.info("Mengatur perintah bot...")
            await self.set_bot_commands(BOT_COMMANDS)
            self.log.info("Perintah bot telah diatur")
        except RPCError as e:
            LOGGER.error(e)
            exit()

        self.log.info("CHANNEL_DB: Memeriksa akses bot...")
        try:
            hello_world = await self.send_message(CHANNEL_DB, "Hello World!")
            await hello_world.delete()
            self.log.info("CHANNEL_DB: Bot telah diberi akses")
        except RPCError as e:
            self.log.error(f"CHANNEL_DB: {e}")
            pass
        
        for key, chat_id in FORCE_SUB_.items():
            try:
                self.log.info(f"FORCE_SUB_{key}: Memeriksa akses bot...")
                get_chat = await self.get_chat(chat_id)
                setattr(self, f"FORCE_SUB_{key}", get_chat.invite_link)
                self.log.info(f"FORCE_SUB_{key}: Bot telah diberi akses")
            except RPCError as e:
                self.log.error(f"FORCE_SUB_{key}: {FORCE_SUB_[key]}: {e}")
                pass
        
        if os.path.exists('restart.txt'):
            with open('restart.txt', 'r') as f:
                chat_id = int(f.readline().strip())
                message_id = int(f.readline().strip())
                await self.edit_message_text(chat_id, message_id, "Bot dimulai ulang.")
            
            os.remove('restart.txt')

        self.log.info(f"@{self.username} berhasil diaktifkan")

        await idle()

    async def stop(self, *args):
        await super().stop()
        LOGGER.warning("Bot telah dihentikan")
        exit()

fsub = Bot()
