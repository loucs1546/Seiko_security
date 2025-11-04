# core_config.py
import os
from typing import Dict, Any

CONFIG: Dict[str, Any] = {
    "security": {
        "anti_spam": False,
        "anti_raid": False,
        "anti_hack": False
    },
    "logs": {}
}

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID", "0"))