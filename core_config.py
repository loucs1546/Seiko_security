import os
from typing import Dict, Any

# Configuration par défaut
CONFIG: Dict[str, Any] = {
    "security": {
        "anti_spam": False,
        "anti_hack": False,
        "anti_raid": False
    },
    "logs": {}
}

# Chargement du token et guild ID
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
if not DISCORD_TOKEN:
    raise RuntimeError("DISCORD_TOKEN manquant dans les variables d'environnement")

try:
    GUILD_ID = int(os.getenv("GUILD_ID", "0"))
except ValueError:
    raise RuntimeError("GUILD_ID invalide dans les variables d'environnement")

def save_config():
    """Sauvegarde la configuration (à implémenter selon besoin)"""
    pass

def load_config():
    """Charge la configuration (à implémenter selon besoin)"""
    pass