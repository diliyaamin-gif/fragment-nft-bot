from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List, Dict
from config import config


def get_main_menu(is_admin: bool = False, lang: str = 'ru') -> InlineKeyboardMarkup:
    texts = {
        'ru': {'shop': '🛍️ Магазин NFT', 'profile': '👤 Профиль', 'purchases': '📦 Мои покупки',
               'deposit': '💰 Пополнить баланс', 'admin': '⚙️ Админ-панель'},
        'en': {'shop': '🛍️ NFT Shop', 'profile': '👤 Profile', 'purchases': '📦 My Purchases', 'deposit': '💰 Deposit',
               'admin': '⚙️ Admin Panel'}
    }
    t = texts.get(lang, texts['ru'])

    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=t['shop'], callback_data="shop_menu"))
    builder.row(InlineKeyboardButton(text=t['profile'], callback_data="profile"))
    builder.row(InlineKeyboardButton(text=t['purchases'], callback_data="my_purchases"))
    builder.row(InlineKeyboardButton(text=t['deposit'], callback_data="deposit"))

    if is_admin:
        builder.row(InlineKeyboardButton(text=t['admin'], callback_data="admin_panel"))

    return builder.as_markup()


def get_shop_menu(lang: str = 'ru') -> InlineKeyboardMarkup:
    texts = {
        'ru': {'nft': '🎨 NFT Подарки', 'numbers': '📱 Анонимные номера (+888)', 'usernames': '👤 NFT Юзернеймы',
               'back': '🔙 Назад'},
        'en': {'nft': '🎨 NFT Gifts', 'numbers': '📱 Anonymous Numbers (+888)', 'usernames': '👤 NFT Usernames',
               'back': '🔙 Back'}
    }
    t = texts.get(lang, texts['ru'])

    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=t['nft'], callback_data="category_nft"))
    builder.row(InlineKeyboardButton(text=t['numbers'], callback_data="category_numbers"))
    builder.row(InlineKeyboardButton(text=t['usernames'], callback_data="category_usernames"))
    builder.row(InlineKeyboardButton(text=t['back'], callback_data="back_to_main"))
    return builder.as_markup()


def get_nft_list_keyboard(gifts: List[Dict], page: int = 0, items_per_page: int = 6,
                          lang: str = 'ru') -> InlineKeyboardMarkup:
    texts = {
        'ru': {'back': '🔙 Назад в магазин', 'prev': '⬅️ Назад', 'next': '➡️ Вперед'},
        'en': {'back': '🔙 Back to shop', 'prev': '⬅️ Prev', 'next': '➡️ Next'}
    }
    t = texts.get(lang, texts['ru'])

    builder = InlineKeyboardBuilder()

    start = page * items_per_page
    end = start + items_per_page
    page_gifts = gifts[start:end]

    for gift in page_gifts:
        builder.row(InlineKeyboardButton(
            text=f"🎁 {gift['name']} (${gift['min_price']} - ${gift['max_price']})",
            callback_data=f"gift_{gift['id']}"
        ))

    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(text=t['prev'], callback_data=f"nft_page_{page - 1}"))
    if end < len(gifts):
        nav_buttons.append(InlineKeyboardButton(text=t['next'], callback_data=f"nft_page_{page + 1}"))

    if nav_buttons:
        builder.row(*nav_buttons)

    builder.row(InlineKeyboardButton(text=t['back'], callback_data="back_to_shop"))
    return builder.as_markup()


def get_background_keyboard(lang: str = 'ru') -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for i, bg in enumerate(config.BACKGROUNDS[:20]):
        builder.row(InlineKeyboardButton(text=f"🎨 {bg}", callback_data=f"bg_{i}"))

    builder.row(InlineKeyboardButton(
        text="🎲 Случайный фон" if lang == 'ru' else "🎲 Random background",
        callback_data="bg_random"
    ))

    builder.row(InlineKeyboardButton(
        text="🔙 Назад" if lang == 'ru' else "🔙 Back",
        callback_data="back_to_gift_list"
    ))

    return builder.as_markup()


def get_delivery_info_keyboard(item_type: str, lang: str = 'ru') -> InlineKeyboardMarkup:
    texts = {
        'ru': {
            'nft': "Введите @username для получения подарка:",
            'username': "Введите @username, на который нужно передать юзернейм:",
            'number': "Введите TON кошелек для получения номера:"
        },
        'en': {
            'nft': "Enter @username to receive the gift:",
            'username': "Enter @username to transfer the username to:",
            'number': "Enter TON wallet to receive the number:"
        }
    }

    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="❌ Отмена" if lang == 'ru' else "❌ Cancel",
        callback_data="cancel_delivery"
    ))
    return builder.as_markup()


def get_confirm_purchase_keyboard(lang: str = 'ru') -> InlineKeyboardMarkup:
    texts = {
        'ru': {'confirm': '✅ Подтвердить покупку', 'cancel': '❌ Отмена'},
        'en': {'confirm': '✅ Confirm purchase', 'cancel': '❌ Cancel'}
    }
    t = texts.get(lang, texts['ru'])

    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=t['confirm'], callback_data="confirm_purchase"))
    builder.row(InlineKeyboardButton(text=t['cancel'], callback_data="cancel_purchase"))
    return builder.as_markup()


def get_numbers_keyboard(numbers: List[Dict], page: int = 0, items_per_page: int = 6,
                         lang: str = 'ru') -> InlineKeyboardMarkup:
    texts = {
        'ru': {'back': '🔙 Назад в магазин', 'prev': '⬅️ Назад', 'next': '➡️ Вперед'},
        'en': {'back': '🔙 Back to shop', 'prev': '⬅️ Prev', 'next': '➡️ Next'}
    }
    t = texts.get(lang, texts['ru'])

    builder = InlineKeyboardBuilder()

    start = page * items_per_page
    end = start + items_per_page
    page_numbers = numbers[start:end]

    for number in page_numbers:
        builder.row(InlineKeyboardButton(
            text=f"📱 {number['number']} - ${number['price']}",
            callback_data=f"number_{number['id']}"
        ))

    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(text=t['prev'], callback_data=f"numbers_page_{page - 1}"))
    if end < len(numbers):
        nav_buttons.append(InlineKeyboardButton(text=t['next'], callback_data=f"numbers_page_{page + 1}"))

    if nav_buttons:
        builder.row(*nav_buttons)

    builder.row(InlineKeyboardButton(text=t['back'], callback_data="back_to_shop"))
    return builder.as_markup()


def get_number_keyboard(number_id: int, price: float, lang: str = 'ru') -> InlineKeyboardMarkup:
    texts = {
        'ru': {'buy': f'💰 Купить за ${price}', 'back': '🔙 Назад к списку'},
        'en': {'buy': f'💰 Buy for ${price}', 'back': '🔙 Back to list'}
    }
    t = texts.get(lang, texts['ru'])

    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=t['buy'], callback_data=f"buy_number_{number_id}"))
    builder.row(InlineKeyboardButton(text=t['back'], callback_data="back_to_numbers"))
    return builder.as_markup()


def get_usernames_keyboard(usernames: List[Dict], page: int = 0, items_per_page: int = 6,
                           lang: str = 'ru') -> InlineKeyboardMarkup:
    texts = {
        'ru': {'back': '🔙 Назад в магазин', 'prev': '⬅️ Назад', 'next': '➡️ Вперед'},
        'en': {'back': '🔙 Back to shop', 'prev': '⬅️ Prev', 'next': '➡️ Next'}
    }
    t = texts.get(lang, texts['ru'])

    builder = InlineKeyboardBuilder()

    start = page * items_per_page
    end = start + items_per_page
    page_usernames = usernames[start:end]

    for username in page_usernames:
        builder.row(InlineKeyboardButton(
            text=f"👤 {username['username']} - ${username['price']}",
            callback_data=f"username_{username['id']}"
        ))

    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(text=t['prev'], callback_data=f"usernames_page_{page - 1}"))
    if end < len(usernames):
        nav_buttons.append(InlineKeyboardButton(text=t['next'], callback_data=f"usernames_page_{page + 1}"))

    if nav_buttons:
        builder.row(*nav_buttons)

    builder.row(InlineKeyboardButton(text=t['back'], callback_data="back_to_shop"))
    return builder.as_markup()


def get_username_keyboard(username_id: int, price: float, lang: str = 'ru') -> InlineKeyboardMarkup:
    texts = {
        'ru': {'buy': f'💰 Купить за ${price}', 'back': '🔙 Назад к списку'},
        'en': {'buy': f'💰 Buy for ${price}', 'back': '🔙 Back to list'}
    }
    t = texts.get(lang, texts['ru'])

    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=t['buy'], callback_data=f"buy_username_{username_id}"))
    builder.row(InlineKeyboardButton(text=t['back'], callback_data="back_to_usernames"))
    return builder.as_markup()


def get_deposit_currency_keyboard(lang: str = 'ru') -> InlineKeyboardMarkup:
    texts = {
        'ru': {'ton': '💎 TON', 'usdt': '💵 USDT', 'btc': '₿ Bitcoin', 'eth': '⟠ Ethereum', 'sol': '◎ Solana',
               'back': '🔙 Назад'},
        'en': {'ton': '💎 TON', 'usdt': '💵 USDT', 'btc': '₿ Bitcoin', 'eth': '⟠ Ethereum', 'sol': '◎ Solana',
               'back': '🔙 Back'}
    }
    t = texts.get(lang, texts['ru'])

    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=t['ton'], callback_data="deposit_TON"))
    builder.row(InlineKeyboardButton(text=t['usdt'], callback_data="deposit_USDT"))
    builder.row(InlineKeyboardButton(text=t['btc'], callback_data="deposit_BTC"))
    builder.row(InlineKeyboardButton(text=t['eth'], callback_data="deposit_ETH"))
    builder.row(InlineKeyboardButton(text=t['sol'], callback_data="deposit_SOL"))
    builder.row(InlineKeyboardButton(text=t['back'], callback_data="back_to_main"))
    return builder.as_markup()


def get_usdt_network_keyboard(lang: str = 'ru') -> InlineKeyboardMarkup:
    texts = {
        'ru': {
            'trc20': '💵 USDT (TRC20) - Tron',
            'erc20': '💵 USDT (ERC20) - Ethereum',
            'bep20': '💵 USDT (BEP20) - BSC',
            'sol': '💵 USDT (SOL) - Solana',
            'ton': '💵 USDT (TON) - TON',
            'back': '🔙 Назад'
        },
        'en': {
            'trc20': '💵 USDT (TRC20) - Tron',
            'erc20': '💵 USDT (ERC20) - Ethereum',
            'bep20': '💵 USDT (BEP20) - BSC',
            'sol': '💵 USDT (SOL) - Solana',
            'ton': '💵 USDT (TON) - TON',
            'back': '🔙 Back'
        }
    }
    t = texts.get(lang, texts['ru'])

    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=t['trc20'], callback_data="usdt_TRC20"))
    builder.row(InlineKeyboardButton(text=t['erc20'], callback_data="usdt_ERC20"))
    builder.row(InlineKeyboardButton(text=t['bep20'], callback_data="usdt_BEP20"))
    builder.row(InlineKeyboardButton(text=t['sol'], callback_data="usdt_SOL"))
    builder.row(InlineKeyboardButton(text=t['ton'], callback_data="usdt_TON"))
    builder.row(InlineKeyboardButton(text=t['back'], callback_data="deposit"))
    return builder.as_markup()


def get_language_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
        InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")
    )
    return builder.as_markup()


def get_cancel_keyboard(lang: str = 'ru') -> InlineKeyboardMarkup:
    texts = {'ru': '❌ Отмена', 'en': '❌ Cancel'}
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=texts.get(lang, texts['ru']), callback_data="cancel_action"))
    return builder.as_markup()


def get_admin_panel(lang: str = 'ru') -> InlineKeyboardMarkup:
    texts = {
        'ru': {'add_nft': '➕ Добавить NFT', 'add_balance': '💰 Пополнить баланс', 'stats': '📊 Статистика',
               'back': '🔙 Назад'},
        'en': {'add_nft': '➕ Add NFT', 'add_balance': '💰 Add Balance', 'stats': '📊 Statistics', 'back': '🔙 Back'}
    }
    t = texts.get(lang, texts['ru'])

    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=t['add_nft'], callback_data="admin_add_nft"))
    builder.row(InlineKeyboardButton(text=t['add_balance'], callback_data="admin_add_balance"))
    builder.row(InlineKeyboardButton(text=t['stats'], callback_data="admin_stats"))
    builder.row(InlineKeyboardButton(text=t['back'], callback_data="back_to_main"))
    return builder.as_markup()


def get_payment_confirm_keyboard(payment_id: int, amount: float, lang: str = 'ru') -> InlineKeyboardMarkup:
    texts = {
        'ru': {'confirm': f'✅ Подтвердить (${amount})', 'reject': '❌ Отклонить'},
        'en': {'confirm': f'✅ Confirm (${amount})', 'reject': '❌ Reject'}
    }
    t = texts.get(lang, texts['ru'])

    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=t['confirm'], callback_data=f"confirm_payment_{payment_id}"),
        InlineKeyboardButton(text=t['reject'], callback_data=f"reject_payment_{payment_id}")
    )
    return builder.as_markup()