# core_config.py
import os

def load_dotenv(dotenv_filename: str = ".env") -> None:
    """
    Lit un fichier .env simple et place les variables dans os.environ si elles ne sont pas déjà définies.
    Format attendu : KEY=VALUE, supporte les valeurs entre quotes et ignore les commentaires.
    """
    project_root = os.path.dirname(__file__)
    path = os.path.join(project_root, dotenv_filename)
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, val = line.split("=", 1)
            key = key.strip()
            val = val.strip()
            if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                val = val[1:-1]
            # Ne pas écraser les variables d'environnement existantes
            os.environ.setdefault(key, val)

# Charger .env local si présent
load_dotenv()

# Lecture et validation des variables
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
if not DISCORD_TOKEN:
    raise RuntimeError(
        "DISCORD_TOKEN non défini. Crée un fichier .env à la racine du projet ou exporte la variable d'environnement."
    )

_GUILD_ID_RAW = os.getenv("GUILD_ID")
if _GUILD_ID_RAW is None or _GUILD_ID_RAW == "":
    GUILD_ID = None
else:
    try:
        GUILD_ID = int(_GUILD_ID_RAW)
    except ValueError:
        raise RuntimeError(f"GUILD_ID invalide : '{_GUILD_ID_RAW}' doit être un entier.")

# Fournir une CONFIG minimale si absent
CONFIG = globals().get("CONFIG", {"logs": {}})