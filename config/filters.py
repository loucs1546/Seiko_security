# config/filters.py

# Liste à compléter par toi-même (ex: mots interdits, patterns, etc.)
MOTS_INTERDITS = set()

# Exemples (à remplacer ou compléter) :
MOTS_INTERDITS = {
    "connard",
    "conne",
    "pute",
    "salope",
    "enculé",
    "merde",
    "bordel",
    "putain",
    "fuck",
    "shit",
    "bitch",
    "asshole",
    "dick",
    "pénis",
    "vagin",
    "porn",
    "porno",
    "sex",
    "fuckyou",
    "bastard",
    "motherfucker",
    "nazi",
    "raciste",
    "homophobe",
    "sodomie",
    "masturbation",
    "cunnilingus",
    "fellation",
    "inceste",
    "violer",
    "viol",
    "merdal",
    "chiant",
    "batard",
    "salope",
    "garce",
    "fils de pute",
    "pute de luxe",
    "tarlouze",
    "tapette",
    "pd",
    "enculée",
    "gouine",
    "trou du cul",
    "gros con",
    "gros cul",
    "nique",
    "ta gueule",
    "nique ta mère",
    "nique le système",
    "putes",
    "casse-toi",
    "pute borgne",
    "salope de merde",
    "conasse",
    "connasses",
    "putain de merde",
    "cul",
    "bite",
    "chatte",
    "couilles",
    "sexe",
    "pornographie",
    "masturber",
    "orgie",
    "orgies",
    "striptease",
    "prostituée",
    "escort",
    "viols",
    "abusive",
    "abuse",
}


# === Mots ou domaines interdits dans les URL ===
MOTS_INTERDITS_URL = {
    "pornhub",
    "youporn",
    "xvideos",
    "xhamster",
    "redtube",
    "xnxx",
    "tube8",
    "spankwire",
    "porn.com",
    "fap",
    "brazzers",
    "naughtyamerica",
    "bangbros",
    "javhub",
    "eroprofile",
    "xart",
    "pornhd",
}

def est_contenu_suspect(contenu: str) -> bool:
    contenu_min = contenu.lower()
    for mot in MOTS_INTERDITS:
        if mot in contenu_min:
            return True
    if len(contenu) > 5:
        majuscules = sum(1 for c in contenu if c.isupper())
        if majuscules / len(contenu) > 0.7:
            return True
    if any(contenu.count(c) / len(contenu) > 0.6 for c in set(contenu)):
        return True
    return False

def est_url_suspecte(url: str) -> bool:
    url_min = url.lower()
    for mot in MOTS_INTERDITS_URL:
        if mot in url_min:
            return True
    return False