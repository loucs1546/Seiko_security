# core_config.py
import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))

# Configuration dynamique (remplace LOG_CHANNELS)
CONFIG = {
    "security": {
        "anti_spam": False,
        "anti_hack": False,
        "anti_raid": False
    },
    "logs": {
        "messages": None,
        "vocal": None,
        "commands": None,
        "roles": None,
        "profile": None,
        "content": None,
        "sanctions": None
    }
}