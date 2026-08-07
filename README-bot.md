> Ce dépôt contient le bot Telegram (Python). Le `Dockerfile` est à la racine, pas dans un sous-dossier.

# 🎧 Bot de reconnaissance musicale (type Shazam)

Envoie un **vocal**, un **audio**, une **vidéo**, une **note vidéo** ou un **GIF** : le bot extrait le son, l'analyse et renvoie le **titre**, l'**artiste**, l'**album**, la **date de sortie**, le **label**, la **pochette** et les **liens d'écoute** (Spotify, Apple Music, Deezer).

## ✨ Fonctionnalités

- 🎵 Reconnaissance du son dans un audio **ou** une vidéo (extraction via ffmpeg)
- 🖼 Pochette de l'album + boutons Spotify / Apple Music / Deezer
- 🔒 **Adhésion obligatoire** : sans avoir rejoint la **chaîne** *et* le **groupe**, impossible d'utiliser le bot (bouton « ✅ J'ai rejoint »)
- 🔗 `/start` affiche les infos du **créateur**, de la **chaîne** et du **groupe**
- ⌨️ Menu clavier + boutons inline, tout en français avec emojis
- 📊 Statistiques par utilisateur (`/stats`)
- 🛡 Admin : `/admin`, `/broadcast`, `/ban`, `/unban`

## ⚙️ Variables d'environnement

| Variable | Description |
|---|---|
| `BOT_TOKEN` | token donné par [@BotFather](https://t.me/BotFather) |
| `AUDD_API_TOKEN` | clé API de [audd.io](https://audd.io/) (reconnaissance musicale) |
| `ADMINS` | IDs Telegram des admins, séparés par des virgules |
| `CREATOR_NAME` | nom affiché du créateur |
| `CREATOR_URL` | lien du créateur (bouton `/start`) |
| `CHANNEL_URL` | lien d'invitation de la chaîne |
| `GROUP_URL` | lien d'invitation du groupe |
| `CHANNEL_ID` | `@nom_chaine` ou `-100…` — utilisé pour vérifier l'adhésion |
| `GROUP_ID` | `@nom_groupe` ou `-100…` — utilisé pour vérifier l'adhésion |
| `DB_PATH` | chemin SQLite (ex. `/var/data/bot.db`) |

> ⚠️ Le bot doit être **administrateur** de la chaîne et du groupe pour pouvoir vérifier l'adhésion. Si `CHANNEL_ID`/`GROUP_ID` sont vides, la vérification est désactivée.

## 🐳 Lancer avec Docker

```bash
docker build -t shazam-bot .
docker run \
  -e BOT_TOKEN=xxx \
  -e AUDD_API_TOKEN=yyy \
  -e ADMINS=123456789 \
  -e CHANNEL_ID=@ma_chaine \
  -e GROUP_ID=@mon_groupe \
  -p 8080:8080 shazam-bot
```

## 🚀 Déploiement sur Render

1. Pousse le dépôt sur GitHub.
2. Render : **New → Web Service → Docker** (ou « Blueprint » avec `render.yaml`).
3. Renseigne les variables ci-dessus.

Le service expose un petit serveur HTTP sur `$PORT` pour le health check.

## 💻 Sans Docker (nécessite `ffmpeg`)

```bash
pip install -r requirements.txt
BOT_TOKEN=xxx AUDD_API_TOKEN=yyy python main.py
```
