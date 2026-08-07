from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

import config

BTN_IDENTIFY = '🎧 Identifier un son'
BTN_STATS = '📊 Mes stats'
BTN_HELP = '❓ Aide'
BTN_ABOUT = 'ℹ️ À propos'
BTN_ADMIN = '🛡 Admin'


def main_menu(is_admin: bool = False) -> ReplyKeyboardMarkup:
    rows = [
        [KeyboardButton(BTN_IDENTIFY)],
        [KeyboardButton(BTN_STATS), KeyboardButton(BTN_HELP)],
        [KeyboardButton(BTN_ABOUT)],
    ]
    if is_admin:
        rows.append([KeyboardButton(BTN_ADMIN)])
    return ReplyKeyboardMarkup(
        rows,
        resize_keyboard=True,
        input_field_placeholder='Envoie un audio ou une vidéo 🎵',
    )


def start_links() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton('👤 Contacter le créateur', url=config.CREATOR_URL)],
            [
                InlineKeyboardButton('📢 La chaîne', url=config.CHANNEL_URL),
                InlineKeyboardButton('💬 Le groupe', url=config.GROUP_URL),
            ],
        ]
    )


def must_join() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton('📢 Rejoindre la chaîne', url=config.CHANNEL_URL)],
            [InlineKeyboardButton('💬 Rejoindre le groupe', url=config.GROUP_URL)],
            [InlineKeyboardButton("✅ J'ai rejoint", callback_data='check_join')],
        ]
    )


def result_links(links: dict) -> InlineKeyboardMarkup | None:
    """links : {'label emoji': url}"""
    rows, current = [], []
    for label, url in links.items():
        if not url:
            continue
        current.append(InlineKeyboardButton(label, url=url))
        if len(current) == 2:
            rows.append(current)
            current = []
    if current:
        rows.append(current)
    if not rows:
        return None
    return InlineKeyboardMarkup(rows)
