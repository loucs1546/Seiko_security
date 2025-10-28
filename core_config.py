# core_config.py
import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))

CONFIG = {
    "security": {
        "anti_spam": False,
        "anti_raid": False,
        "anti_hack": False
    },
    "logs": {
        "messages": None,
        "vocal": None,
        "commands": None,
        "roles": None,
        "profile": None,
        "content": None,
        "sanctions": None,
        "moderation": None,
        "ticket": None,
        "securite": None
    }
}