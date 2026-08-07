"""Tous les textes du bot, en francais, avec emojis et mise en forme HTML."""

START = (
    "🎧 <b>Bienvenue {name} !</b> ✨\n\n"
    "Je suis ton <b>Shazam sur Telegram</b> 🎵\n"
    "Envoie-moi n'importe quoi qui contient de la musique :\n\n"
    "🎙 un <b>vocal</b>\n"
    "🎵 un <b>audio</b> / fichier MP3\n"
    "🎬 une <b>vidéo</b> ou une <b>note vidéo</b>\n"
    "🎞 un <b>GIF</b> sonore\n\n"
    "…et je te donne le <b>titre</b>, l'<b>artiste</b>, l'<b>album</b> et les liens d'écoute 🔎\n\n"
    "👤 <b>Créateur :</b> {creator}\n"
    "📢 <b>Chaîne officielle</b> · 💬 <b>Groupe officiel</b>\n\n"
    "👇 Utilise les boutons ci-dessous pour commencer."
)

HELP = (
    "❓ <b>Aide</b>\n\n"
    "1️⃣ Envoie un <b>vocal</b>, un <b>audio</b>, une <b>vidéo</b> ou un <b>GIF</b>\n"
    "2️⃣ J'extrais le son et je l'analyse 🔎\n"
    "3️⃣ Je te renvoie le <b>titre du son</b> avec les liens d'écoute 🎵\n\n"
    "💡 <b>Astuces</b>\n"
    "• 10 à 20 secondes de musique claire suffisent\n"
    "• Évite les bruits de fond trop forts 🔇\n"
    "• Fichier de <b>20 Mo maximum</b> (limite de Telegram)\n\n"
    "<b>Commandes</b>\n"
    "/start — menu principal\n"
    "/help — cette aide\n"
    "/about — infos sur le bot\n"
    "/stats — mes statistiques"
)

ABOUT = (
    "ℹ️ <b>À propos</b>\n\n"
    "🎵 <b>Bot de reconnaissance musicale</b>\n"
    "Il identifie n'importe quel son présent dans un audio ou une vidéo.\n\n"
    "👤 <b>Créateur :</b> {creator}\n"
    "📢 <b>Chaîne :</b> {channel}\n"
    "💬 <b>Groupe :</b> {group}\n\n"
    "🛠 Développé avec ❤️ en Python."
)

MUST_JOIN = (
    "🔒 <b>Accès réservé aux membres</b>\n\n"
    "Salut {name} 👋\n"
    "Pour utiliser le bot, tu dois d'abord rejoindre :\n\n"
    "📢 la <b>chaîne officielle</b>\n"
    "💬 le <b>groupe officiel</b>\n\n"
    "👇 Rejoins-les puis appuie sur <b>✅ J'ai rejoint</b>."
)

STILL_NOT_JOINED = "🚫 Tu n'as pas encore rejoint <b>la chaîne et le groupe</b>. Réessaie après 😉"
JOIN_OK = "✅ <b>Parfait, merci d'avoir rejoint !</b>\nTu peux maintenant utiliser le bot 🎉"

ASK_MEDIA = (
    "🎤 <b>Envoie-moi le son à identifier</b>\n\n"
    "Un vocal 🎙, un audio 🎵, une vidéo 🎬 ou un GIF 🎞 — je m'occupe du reste 🔎"
)

ANALYZING = "🔎 <b>Analyse en cours…</b>\n🎧 J'écoute attentivement, patiente quelques secondes ⏳"

NO_TOKEN = (
    "⚠️ <b>Service de reconnaissance non configuré</b>\n\n"
    "Réessaie dans quelques instants."
)

TOO_BIG = (
    "📦 <b>Fichier trop lourd</b>\n\n"
    "Telegram m'autorise seulement <b>{limit} Mo</b>.\n"
    "Envoie un extrait plus court ✂️"
)

NOT_MEDIA = (
    "🤔 Je ne vois pas de son ici.\n"
    "Envoie-moi un <b>vocal</b> 🎙, un <b>audio</b> 🎵, une <b>vidéo</b> 🎬 ou un <b>GIF</b> 🎞."
)

NOT_FOUND = (
    "😔 <b>Aucune correspondance trouvée</b>\n\n"
    "Essaie avec :\n"
    "• un extrait où la musique est plus <b>audible</b> 🔊\n"
    "• un passage <b>chanté</b> ou du refrain 🎶\n"
    "• moins de bruit autour 🔇"
)

ERROR = "💥 <b>Oups…</b> une erreur est survenue pendant l'analyse. Réessaie dans un instant 🙏"

RESULT = (
    "🎯 <b>Son identifié !</b>\n\n"
    "🎵 <b>Titre :</b> {title}\n"
    "👤 <b>Artiste :</b> {artist}\n"
    "💿 <b>Album :</b> {album}\n"
    "📅 <b>Sortie :</b> {release}\n"
    "🏷 <b>Label :</b> {label}"
)

STATS = (
    "📊 <b>Tes statistiques</b>\n\n"
    "🔎 Recherches : <b>{searches}</b>\n"
    "🎯 Sons trouvés : <b>{found}</b>\n"
    "📅 Membre depuis : <b>{since}</b>"
)

ADMIN = (
    "🛡 <b>Panneau admin</b>\n\n"
    "👥 Utilisateurs : <b>{users}</b>\n"
    "🔎 Recherches totales : <b>{searches}</b>\n"
    "🎯 Sons identifiés : <b>{found}</b>\n\n"
    "<b>Commandes</b>\n"
    "/broadcast &lt;message&gt; — message à tous\n"
    "/ban &lt;id&gt; · /unban &lt;id&gt;"
)

BANNED = "🚫 Tu es banni de ce bot."
ADMIN_ONLY = "🛡 Commande réservée aux administrateurs."
