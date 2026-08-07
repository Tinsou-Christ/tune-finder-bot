import os


def _int_list(value: str):
    out = []
    for part in (value or '').replace(';', ',').split(','):
        part = part.strip()
        if part.lstrip('-').isdigit():
            out.append(int(part))
    return out


def _clean(value: str) -> str:
    return (value or '').strip()


BOT_TOKEN = _clean(os.environ.get('BOT_TOKEN'))
ADMINS = _int_list(os.environ.get('ADMINS', ''))

# reconnaissance musicale (https://audd.io/)
AUDD_API_TOKEN = _clean(os.environ.get('AUDD_API_TOKEN'))

# liens affiches sur /start
CREATOR_URL = _clean(os.environ.get('CREATOR_URL')) or 'https://t.me/Shadow_sekai'
CHANNEL_URL = _clean(os.environ.get('CHANNEL_URL')) or 'https://t.me/Shadow_sekai'
GROUP_URL = _clean(os.environ.get('GROUP_URL')) or 'https://t.me/Shadow_sekai'

CREATOR_NAME = _clean(os.environ.get('CREATOR_NAME')) or 'Shadow Sekai'

# adhesion obligatoire : @nom_de_la_chaine / @nom_du_groupe (ou -100...)
CHANNEL_ID = _clean(os.environ.get('CHANNEL_ID'))
GROUP_ID = _clean(os.environ.get('GROUP_ID'))

DB_PATH = os.environ.get('DB_PATH', os.path.join(os.path.dirname(__file__), 'bot.db'))
PORT = int(os.environ.get('PORT', '8080'))

# limites
MAX_FILE_MB = 20          # taille max telechargeable via l'API Bot
SAMPLE_SECONDS = 20       # duree de l'extrait analyse
RECOGNIZE_TIMEOUT = 60    # secondes
