import os
import sys
import logging
import uvloop
import base64

from pymongo import MongoClient

from pyromod import Client

from pyrogram.types import BotCommand
from pyrogram.enums import ParseMode
from pyrogram.errors import RPCError

logging.basicConfig(
    handlers=[logging.FileHandler("log.txt"), logging.StreamHandler()],
    level=logging.INFO
)


Logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_CHANNEL = int(os.getenv("DATABASE_CHANNEL"))

BOT_ADMINS = [int(i) for i in os.getenv("BOT_ADMINS").split()]

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

MONGODB_NAME = BOT_TOKEN.split(":", 1)[0]
MONGODB_URL = os.environ.get("MONGODB_URL", "mongodb://root:passwd@mongo")

BOT_COMMANDS = [
    BotCommand("start", "Start bot"),
    BotCommand("ping", "Bot latency"),
    BotCommand("batch", "Batch message"),
    BotCommand("broadcast", "Broadcast message"),
    BotCommand("cancel", "Cancel broadcast"),
    BotCommand("status", "Broadcast status"),
    BotCommand("users", "Bot users"),
    BotCommand("log", "Bot logs"),
    BotCommand("restart", "Restart bot")
]

LIST_COMMANDS = [command.command for command in BOT_COMMANDS]


class UserDB:
    def __init__(self, database_url, database_name):
        self.dbclient = MongoClient(database_url)
        self.database = self.dbclient[database_name]
        self.user_data = self.database["users"]

    def insert_user(self, user_id: int):
        if not self.user_data.find_one({"_id": user_id}):
            self.user_data.insert_one({"_id": user_id})

    def all_users(self):
        users = self.user_data.find()
        user_id = [user["_id"] for user in users]
        return user_id

    def delete_user(self, user_id: int):
        self.user_data.delete_one({"_id": user_id})

UserDB = UserDB(MONGODB_URL, MONGODB_NAME)


class URLSafe:
    @staticmethod
    def encode(data):
        encoded_bytes = base64.urlsafe_b64encode(data.encode("utf-8"))
        encoded_str = str(encoded_bytes, "utf-8").rstrip("=")
        return encoded_str

    @staticmethod
    def decode(data):
        padding_factor = (4 - len(data) % 4) % 4
        data += "=" * padding_factor
        decoded_bytes = base64.urlsafe_b64decode(data)
        decoded_str = str(decoded_bytes, "utf-8")
        return decoded_str

URLSafe = URLSafe()


class Bot(Client):
    def __init__(self):
        super().__init__(
            name = "Bot",
            api_id = 2040,
            api_hash = "b18441a1ff607e10a989891a5462e627",
            bot_token = BOT_TOKEN,
            in_memory = True,
            parse_mode = ParseMode.MARKDOWN,
            plugins = dict(root = "bot/plugins")
        )
        

    async def start(self):
        if os.path.exists(".git"):
            os.system("git fetch origin -q; git reset --hard origin/debug -q")

        try:
            uvloop.install()
            await super().start()
        except RPCError as e:
            Logger.error(e)
            sys.exit(1)

        self.Logger = Logger
        self.UserDB = UserDB
        self.URLSafe = URLSafe
    
        await self.set_bot_commands(BOT_COMMANDS)

        try:
            hello_world = await self.send_message(DATABASE_CHANNEL, "Hello World!")
            await hello_world.delete()
        except RPCError as e:
            self.Logger.error(f"DATABASE_CHANNEL: {e}")
            sys.exit(1)
            
        
        for key, chat_id in FORCE_SUB_.items():
            try:
                get_chat = await self.get_chat(chat_id)
                setattr(self, f"FORCE_SUB_{key}", get_chat.invite_link)
            except RPCError as e:
                self.Logger.error(f"FORCE_SUB_{key}: {e}")
                sys.exit(1)
        
        if os.path.exists("restart.txt"):
            with open("restart.txt", "r") as f:
                chat_id = int(f.readline().strip())
                message_id = int(f.readline().strip())
                await self.edit_message_text(
                    chat_id=chat_id,
                    message_id=message_id,
                    text="Bot has been restarted."
                )
            os.remove("restart.txt")

        if os.path.exists("broadcast.txt"):
            with open("broadcast.txt", "r") as f:
                chat_id = int(f.readline().strip())
                message_id = int(f.readline().strip())
                await self.send_message(
                    chat_id=chat_id,
                    text="Bot restarted, broadcast has been stopped.",
                    reply_to_message_id=message_id
                )
            os.remove("broadcast.txt")

    async def stop(self, *args):
        await super().stop()
        sys.exit()

Bot = Bot()
