"""Bot Telegram de reconnaissance musicale (type Shazam) — 100% en français."""

import html
import logging
import os
import tempfile
import time

from telegram import Update
from telegram.constants import ChatAction, ParseMode
from telegram.error import BadRequest, Forbidden, TelegramError
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

import config
import db
import keyboards as kb
import recognizer
import strings as S

logger = logging.getLogger(__name__)

MEMBER_STATUSES = {'creator', 'administrator', 'member', 'restricted'}


# --------------------------------------------------------------------------
# utilitaires
# --------------------------------------------------------------------------

def is_admin(user_id: int) -> bool:
    return user_id in config.ADMINS


def esc(value) -> str:
    return html.escape(str(value if value is not None else '—'))


async def reply(update: Update, text: str, **kwargs):
    return await update.effective_message.reply_html(text, **kwargs)


async def _in_chat(context, chat_id: str, user_id: int) -> bool:
    """True si l'utilisateur est membre (ou si le chat n'est pas configuré)."""
    if not chat_id:
        return True
    try:
        member = await context.bot.get_chat_member(chat_id, user_id)
        return member.status in MEMBER_STATUSES
    except (BadRequest, Forbidden) as exc:
        logger.warning('Vérification adhésion impossible pour %s: %s', chat_id, exc)
        # le bot n'est pas admin du chat / chat introuvable : on ne bloque pas
        return True
    except TelegramError as exc:
        logger.warning('Erreur adhésion %s: %s', chat_id, exc)
        return True


async def has_joined(context, user_id: int) -> bool:
    if is_admin(user_id):
        return True
    return (
        await _in_chat(context, config.CHANNEL_ID, user_id)
        and await _in_chat(context, config.GROUP_ID, user_id)
    )


async def guard(update: Update, context) -> bool:
    """Contrôle bannissement + adhésion obligatoire. True = l'utilisateur peut continuer."""
    user = update.effective_user
    db.save_user(user)

    if db.is_banned(user.id):
        await reply(update, S.BANNED)
        return False

    if not await has_joined(context, user.id):
        await reply(
            update,
            S.MUST_JOIN.format(name=esc(user.first_name)),
            reply_markup=kb.must_join(),
        )
        return False

    return True


# --------------------------------------------------------------------------
# commandes
# --------------------------------------------------------------------------

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db.save_user(user)

    if db.is_banned(user.id):
        await reply(update, S.BANNED)
        return

    if not await has_joined(context, user.id):
        await reply(
            update,
            S.MUST_JOIN.format(name=esc(user.first_name)),
            reply_markup=kb.must_join(),
        )
        return

    await reply(
        update,
        S.START.format(name=esc(user.first_name), creator=esc(config.CREATOR_NAME)),
        reply_markup=kb.start_links(),
    )
    await update.effective_message.reply_text(
        '👇 Menu principal',
        reply_markup=kb.main_menu(is_admin(user.id)),
    )


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await guard(update, context):
        return
    await reply(update, S.HELP)


async def cmd_about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await guard(update, context):
        return
    await reply(
        update,
        S.ABOUT.format(
            creator=esc(config.CREATOR_NAME),
            channel=esc(config.CHANNEL_URL),
            group=esc(config.GROUP_URL),
        ),
        reply_markup=kb.start_links(),
    )


async def cmd_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await guard(update, context):
        return
    row = db.get_user(update.effective_user.id)
    since = time.strftime('%d/%m/%Y', time.localtime(row['joined_at'])) if row else '—'
    await reply(
        update,
        S.STATS.format(
            searches=row['searches'] if row else 0,
            found=row['found'] if row else 0,
            since=since,
        ),
    )


async def cmd_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await reply(update, S.ADMIN_ONLY)
        return
    stats = db.global_stats()
    await reply(update, S.ADMIN.format(**stats))


async def cmd_ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await reply(update, S.ADMIN_ONLY)
        return
    if not context.args or not context.args[0].lstrip('-').isdigit():
        await reply(update, 'Usage : <code>/ban 123456789</code>')
        return
    db.set_banned(int(context.args[0]), True)
    await reply(update, '🚫 Utilisateur banni.')


async def cmd_unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await reply(update, S.ADMIN_ONLY)
        return
    if not context.args or not context.args[0].lstrip('-').isdigit():
        await reply(update, 'Usage : <code>/unban 123456789</code>')
        return
    db.set_banned(int(context.args[0]), False)
    await reply(update, '✅ Utilisateur débanni.')


async def cmd_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await reply(update, S.ADMIN_ONLY)
        return
    text = ' '.join(context.args).strip()
    if not text:
        await reply(update, 'Usage : <code>/broadcast Ton message</code>')
        return

    sent = failed = 0
    for user_id in db.all_user_ids():
        try:
            await context.bot.send_message(user_id, text, parse_mode=ParseMode.HTML)
            sent += 1
        except TelegramError:
            failed += 1
    await reply(update, f'📣 Envoyé : <b>{sent}</b> · Échecs : <b>{failed}</b>')


# --------------------------------------------------------------------------
# adhesion obligatoire
# --------------------------------------------------------------------------

async def on_check_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user

    if await has_joined(context, user.id):
        await query.answer('✅ Vérifié !')
        await query.edit_message_text(S.JOIN_OK, parse_mode=ParseMode.HTML)
        await context.bot.send_message(
            user.id,
            S.START.format(name=esc(user.first_name), creator=esc(config.CREATOR_NAME)),
            parse_mode=ParseMode.HTML,
            reply_markup=kb.start_links(),
        )
        await context.bot.send_message(
            user.id,
            '👇 Menu principal',
            reply_markup=kb.main_menu(is_admin(user.id)),
        )
    else:
        await query.answer("🚫 Tu n'as pas encore rejoint les deux !", show_alert=True)
        await context.bot.send_message(user.id, S.STILL_NOT_JOINED, parse_mode=ParseMode.HTML)


# --------------------------------------------------------------------------
# reconnaissance musicale
# --------------------------------------------------------------------------

def extract_media(message):
    """renvoie (file_id, taille, suffixe) ou None."""
    if message.voice:
        return message.voice.file_id, message.voice.file_size, '.ogg'
    if message.audio:
        return message.audio.file_id, message.audio.file_size, '.mp3'
    if message.video:
        return message.video.file_id, message.video.file_size, '.mp4'
    if message.video_note:
        return message.video_note.file_id, message.video_note.file_size, '.mp4'
    if message.animation:
        return message.animation.file_id, message.animation.file_size, '.mp4'
    if message.document:
        mime = message.document.mime_type or ''
        if mime.startswith('audio/') or mime.startswith('video/'):
            return message.document.file_id, message.document.file_size, '.bin'
    return None


async def on_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await guard(update, context):
        return

    message = update.effective_message
    media = extract_media(message)
    if not media:
        await reply(update, S.NOT_MEDIA)
        return

    file_id, size, suffix = media
    if size and size > config.MAX_FILE_MB * 1024 * 1024:
        await reply(update, S.TOO_BIG.format(limit=config.MAX_FILE_MB))
        return

    if not config.AUDD_API_TOKEN:
        await reply(update, S.NO_TOKEN)
        return

    user_id = update.effective_user.id
    db.add_search(user_id)

    status = await reply(update, S.ANALYZING)
    await context.bot.send_chat_action(message.chat_id, ChatAction.TYPING)

    path = os.path.join(tempfile.gettempdir(), f'media_{user_id}_{int(time.time())}{suffix}')
    try:
        tg_file = await context.bot.get_file(file_id)
        await tg_file.download_to_drive(path)

        info = await recognizer.recognize(path)
    except recognizer.RecognizeError as exc:
        logger.error('Reconnaissance échouée : %s', exc)
        await status.edit_text(S.ERROR, parse_mode=ParseMode.HTML)
        return
    except TelegramError as exc:
        logger.error('Téléchargement échoué : %s', exc)
        await status.edit_text(S.TOO_BIG.format(limit=config.MAX_FILE_MB), parse_mode=ParseMode.HTML)
        return
    except Exception:
        logger.exception('Erreur inattendue')
        await status.edit_text(S.ERROR, parse_mode=ParseMode.HTML)
        return
    finally:
        try:
            os.remove(path)
        except OSError:
            pass

    if not info:
        await status.edit_text(S.NOT_FOUND, parse_mode=ParseMode.HTML)
        return

    db.add_match(user_id, info['title'], info['artist'])

    text = S.RESULT.format(
        title=esc(info['title']),
        artist=esc(info['artist']),
        album=esc(info['album']),
        release=esc(info['release']),
        label=esc(info['label']),
    )
    markup = kb.result_links(info['links'])

    await status.delete()
    if info.get('cover'):
        try:
            await message.reply_photo(
                info['cover'],
                caption=text,
                parse_mode=ParseMode.HTML,
                reply_markup=markup,
            )
            return
        except TelegramError:
            pass
    await message.reply_html(text, reply_markup=markup)


# --------------------------------------------------------------------------
# boutons du clavier
# --------------------------------------------------------------------------

async def on_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await guard(update, context):
        return

    text = (update.effective_message.text or '').strip()
    if text == kb.BTN_IDENTIFY:
        await reply(update, S.ASK_MEDIA)
    elif text == kb.BTN_HELP:
        await cmd_help(update, context)
    elif text == kb.BTN_ABOUT:
        await cmd_about(update, context)
    elif text == kb.BTN_STATS:
        await cmd_stats(update, context)
    elif text == kb.BTN_ADMIN:
        await cmd_admin(update, context)
    else:
        await reply(update, S.NOT_MEDIA)


async def on_error(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error('Erreur non gérée', exc_info=context.error)


# --------------------------------------------------------------------------
# application
# --------------------------------------------------------------------------

def build_application() -> Application:
    db.init()

    application = Application.builder().token(config.BOT_TOKEN).build()

    application.add_handler(CommandHandler('start', cmd_start))
    application.add_handler(CommandHandler('help', cmd_help))
    application.add_handler(CommandHandler('about', cmd_about))
    application.add_handler(CommandHandler('stats', cmd_stats))
    application.add_handler(CommandHandler('admin', cmd_admin))
    application.add_handler(CommandHandler('ban', cmd_ban))
    application.add_handler(CommandHandler('unban', cmd_unban))
    application.add_handler(CommandHandler('broadcast', cmd_broadcast))

    application.add_handler(CallbackQueryHandler(on_check_join, pattern=r'^check_join$'))

    media_filter = (
        filters.VOICE
        | filters.AUDIO
        | filters.VIDEO
        | filters.VIDEO_NOTE
        | filters.ANIMATION
        | filters.Document.AUDIO
        | filters.Document.VIDEO
    )
    application.add_handler(MessageHandler(media_filter, on_media))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_text))

    application.add_error_handler(on_error)
    return application
