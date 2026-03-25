import random
import logging
from datetime import datetime
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import config
from database import Database
from keyboards import *

router = Router()
db = Database()
logger = logging.getLogger(__name__)


# Состояния FSM
class DepositStates(StatesGroup):
    waiting_for_currency = State()
    waiting_for_amount = State()
    waiting_for_screenshot = State()


class BuyNFTStates(StatesGroup):
    choosing_background = State()
    waiting_for_username = State()
    confirming = State()


class BuyNumberStates(StatesGroup):
    waiting_for_wallet = State()
    confirming = State()


class BuyUsernameStates(StatesGroup):
    waiting_for_target = State()
    confirming = State()


class AdminAddNFTStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_min_price = State()
    waiting_for_max_price = State()
    waiting_for_quantity = State()


class AdminAddBalanceStates(StatesGroup):
    waiting_for_user_id = State()
    waiting_for_amount = State()


# Тексты
TEXTS = {
    'ru': {
        'welcome': "🏦 **FRAGMENT NFT SHOP**\n\nДобро пожаловать в официальный магазин коллекционных NFT подарков Telegram.\n\n**Доступно к приобретению:**\n• 🎨 Эксклюзивные NFT подарки\n• 📱 Анонимные номера +888\n• 👤 Премиальные юзернеймы\n\n💰 Пополните баланс и начните коллекционировать уникальные цифровые активы.",
        'help': "📖 **СПРАВОЧНАЯ ИНФОРМАЦИЯ**\n\n**🛍️ МАГАЗИН**\nВыберите категорию для просмотра доступных товаров\n\n**👤 ПРОФИЛЬ**\nПросмотр баланса и личной информации\n\n**📦 МОИ ПОКУПКИ**\nИстория всех приобретенных активов\n\n**💰 ПОПОЛНЕНИЕ**\nПополнение баланса криптовалютой\n\n━━━━━━━━━━━━━━━━━━━━\n**🎁 О NFT ПОДАРКАХ**\n\nКаждый NFT подарок в Telegram имеет уникальные характеристики:\n• **Фон** — цветовое оформление (39 вариантов)\n• **Модель** — визуальный стиль (10+ вариантов)\n• **Узор** — декоративный элемент (15+ вариантов)\n\n✨ **ВАЖНО:** Модель и узор определяются **СЛУЧАЙНЫМ ОБРАЗОМ** при генерации подарка, что делает каждый экземпляр абсолютно уникальным, как в реальном Telegram.\n\n━━━━━━━━━━━━━━━━━━━━\n**🚚 ДОСТАВКА АКТИВОВ**\n\n• **NFT подарки** — доставка на указанный @username в течение 48 часов\n• **Юзернеймы** — передача на указанный @username в течение 48 часов\n• **Анонимные номера** — отправка на TON кошелек в течение 72 часов\n\nПо всем вопросам: @fragment_support",
        'profile': "👤 **ПРОФИЛЬ ПОЛЬЗОВАТЕЛЯ**\n\n🆔 **ID:** `{user_id}`\n💰 **БАЛАНС:** `{balance:.2f} USD`\n📅 **Регистрация:** {date}\n\n━━━━━━━━━━━━━━━━━━━━\nДля пополнения баланса используйте кнопку ниже.",
        'purchases': "📦 **ИСТОРИЯ ПОКУПОК**\n\n{items}\n━━━━━━━━━━━━━━━━━━━━\nВсего покупок: {total}",
        'purchase_item_nft': "🎨 **{name}**\n💰 {price} USD\n🎨 Фон: {background}\n📅 {date}\n🚚 Доставка: {delivery}",
        'purchase_item_username': "👤 **{name}**\n💰 {price} USD\n📅 {date}\n🚚 Передача на: {delivery}",
        'purchase_item_number': "📱 **{name}**\n💰 {price} USD\n📅 {date}\n🚚 Получение: {delivery}",
        'purchase_empty': "У вас пока нет покупок.\nПосетите магазин, чтобы приобрести уникальные NFT активы.",
        'deposit_choose_currency': "💰 **ВЫБОР ВАЛЮТЫ**\n\nВыберите криптовалюту для пополнения баланса:\n\n💎 TON — минимальная комиссия\n💵 USDT — стейблкоин (доступен в 5 сетях)\n₿ Bitcoin — основная криптовалюта\n⟠ Ethereum — смарт-контракты\n◎ Solana — высокая скорость\n\nМинимальная сумма: **${min}**\nМаксимальная сумма: **${max}**",
        'deposit_enter_amount': "💰 **ПОПОЛНЕНИЕ ЧЕРЕЗ {currency}**\n\nВведите сумму пополнения в USD:\n\n💡 Минимум: **${min}**\n💡 Максимум: **${max}**\n\nСредства будут зачислены после подтверждения транзакции администратором.",
        'deposit_min_error': "❌ **ОШИБКА**\n\nМинимальная сумма пополнения: **${min} USD**\n\nПожалуйста, введите корректную сумму:",
        'deposit_max_error': "❌ **ОШИБКА**\n\nМаксимальная сумма пополнения: **${max} USD**\n\nПожалуйста, введите корректную сумму:",
        'deposit_instruction': "💳 **ИНСТРУКЦИЯ ПО ОПЛАТЕ**\n\n1️⃣ Отправьте **{amount} {currency}** на указанный кошелек:\n\n`{wallet}`\n\n2️⃣ После отправки нажмите кнопку «Отправить чек» и прикрепите **СКРИНШОТ ТРАНЗАКЦИИ**\n\n⚠️ **ВАЖНО:**\n• Отправляйте ТОЛЬКО скриншот из кошелька/обменника\n• Убедитесь, что сумма соответствует указанной\n• Проверка занимает до 30 минут\n\n❌ Платежи без чека не обрабатываются",
        'insufficient_balance': "❌ **НЕДОСТАТОЧНО СРЕДСТВ**\n\nНеобходимо: **${price:.2f} USD**\nВаш баланс: **${balance:.2f} USD**\n\nПополните баланс и повторите попытку.",
        'purchase_success_nft': "✅ **ПОКУПКА ПОДТВЕРЖДЕНА**\n\n🎁 **{item}**\n💰 Сумма: **${price:.2f} USD**\n🎨 Фон: **{background}**\n\n━━━━━━━━━━━━━━━━━━━━\n**🚚 ИНФОРМАЦИЯ О ДОСТАВКЕ**\n\nАктив будет доставлен на указанный @username в течение **48 часов**.\n\nСпасибо за покупку!",
        'purchase_success_username': "✅ **ПОКУПКА ПОДТВЕРЖДЕНА**\n\n👤 **{item}**\n💰 Сумма: **${price:.2f} USD**\n\n━━━━━━━━━━━━━━━━━━━━\n**🚚 ИНФОРМАЦИЯ О ДОСТАВКЕ**\n\nЮзернейм будет передан на **{target}** в течение **48 часов**.\n\nСпасибо за покупку!",
        'purchase_success_number': "✅ **ПОКУПКА ПОДТВЕРЖДЕНА**\n\n📱 **{item}**\n💰 Сумма: **${price:.2f} USD**\n\n━━━━━━━━━━━━━━━━━━━━\n**🚚 ИНФОРМАЦИЯ О ДОСТАВКЕ**\n\nНомер будет отправлен на TON кошелек **{wallet}** в течение **72 часов**.\n\nСпасибо за покупку!",
        'item_sold': "❌ **ТОВАР ПРОДАН**\n\nДанный экземпляр уже приобретен другим пользователем.\nПожалуйста, выберите другой товар.",
        'payment_sent': "✅ **ЧЕК ОТПРАВЛЕН**\n\nВаш запрос на пополнение передан на обработку администратору.\n\n⏱ Ожидаемое время подтверждения: до 30 минут\n\nПосле подтверждения баланс будет автоматически пополнен.",
        'payment_confirmed': "✅ **БАЛАНС ПОПОЛНЕН**\n\n💰 Сумма: **+${amount:.2f} USD**\n💵 Новый баланс: **${balance:.2f} USD**\n\nСпасибо за доверие! Приятных покупок.",
        'payment_rejected': "❌ **ПЛАТЕЖ ОТКЛОНЕН**\n\nВаш запрос на пополнение не прошел верификацию.\n\nПричина: несоответствие чека или ошибка в сумме.\n\nID запроса: **{request_id}**\n\nДля уточнения деталей свяжитесь с поддержкой.",
        'admin_new_payment': "💰 **НОВЫЙ ЗАПРОС НА ПОПОЛНЕНИЕ**\n\n👤 Пользователь: `{user_id}`\n💵 Сумма: **${amount}**\n💎 Валюта: {currency}\n🔗 Сеть: {network}\n🏦 Кошелек: `{wallet}`\n\nПроверьте чек и подтвердите транзакцию.",
        'stats': "📊 **СТАТИСТИКА МАГАЗИНА**\n\n👥 Пользователей: **{users}**\n💰 Общий баланс: **${balance:.2f}**\n\n📈 **ПРОДАЖИ:**\n🎨 NFT подарков: **{nft_sold}**\n👤 Юзернеймов: **{usernames_sold}**\n📱 Анонимных номеров: **{numbers_sold}**\n\n💎 Всего продаж: **{total_sold}**",
        'nft_card': "🎁 **{name}**\n\n💰 Цена: **${price}**\n\n━━━━━━━━━━━━━━━━━━━━\n🎨 **ВЫБЕРИТЕ ФОН**\n\nПосле выбора фона, модель и узор будут определены **СЛУЧАЙНО**, как в реальном Telegram.",
        'ask_username': "👤 **УКАЖИТЕ ПОЛУЧАТЕЛЯ**\n\nВведите @username Telegram-аккаунта, на который будет доставлен NFT подарок:\n\n💡 Пример: @username\n\n⚠️ Убедитесь в правильности введенных данных — изменить будет невозможно.",
        'ask_wallet': "🏦 **УКАЖИТЕ КОШЕЛЕК**\n\nВведите TON кошелек для получения анонимного номера:\n\n💡 Пример: EQD...\n\n⚠️ Убедитесь в правильности адреса — средства будут отправлены на указанный кошелек.",
        'ask_target_username': "👤 **УКАЖИТЕ ПОЛУЧАТЕЛЯ**\n\nВведите @username, на который будет передан юзернейм:\n\n💡 Пример: @username\n\n⚠️ Убедитесь в правильности введенных данных — изменить будет невозможно.",
        'invalid_username': "❌ **НЕВЕРНЫЙ ФОРМАТ**\n\n@username должен начинаться с символа @ и содержать только латинские буквы, цифры и нижнее подчеркивание.\n\nПожалуйста, введите корректный username:",
        'invalid_wallet': "❌ **НЕВЕРНЫЙ ФОРМАТ**\n\nTON кошелек должен начинаться с EQD или UQD и содержать 48 символов.\n\nПожалуйста, введите корректный адрес кошелька:",
        'admin_added': "✅ **NFT ПОДАРОК ДОБАВЛЕН**\n\n📝 Название: **{name}**\n💰 Цена: **${min} - ${max}**\n📦 Количество: **{qty}** шт.\n\nПодарок доступен для покупки в магазине.",
        'balance_added': "✅ **БАЛАНС ПОПОЛНЕН**\n\n👤 Пользователь: `{user_id}`\n💰 Сумма: **+${amount}**\n💵 Новый баланс: **${balance}**",
        'admin_access_denied': "⛔ **ДОСТУП ЗАПРЕЩЕН**\n\nДанная команда доступна только администратору.",
        'random_attributes': "🎲 **Модель и узор будут определены случайно**\n\nКак в реальном Telegram, каждый подарок получает уникальную комбинацию характеристик."
    },
    'en': {
        'welcome': "🏦 **FRAGMENT NFT SHOP**\n\nWelcome to the official Telegram collectible NFT gifts store.\n\n**Available for purchase:**\n• 🎨 Exclusive NFT gifts\n• 📱 Anonymous +888 numbers\n• 👤 Premium usernames\n\n💰 Top up your balance and start collecting unique digital assets.",
        'help': "📖 **HELP INFORMATION**\n\n**🛍️ SHOP**\nSelect a category to view available items\n\n**👤 PROFILE**\nView balance and personal information\n\n**📦 MY PURCHASES**\nHistory of all purchased assets\n\n**💰 DEPOSIT**\nTop up balance with cryptocurrency\n\n━━━━━━━━━━━━━━━━━━━━\n**🎁 ABOUT NFT GIFTS**\n\nEach NFT gift in Telegram has unique characteristics:\n• **Background** — color design (39 options)\n• **Model** — visual style (10+ options)\n• **Pattern** — decorative element (15+ options)\n\n✨ **IMPORTANT:** Model and pattern are determined **RANDOMLY** when generating the gift, making each instance completely unique, just like in real Telegram.\n\n━━━━━━━━━━━━━━━━━━━━\n**🚚 ASSET DELIVERY**\n\n• **NFT gifts** — delivery to specified @username within 48 hours\n• **Usernames** — transfer to specified @username within 48 hours\n• **Anonymous numbers** — sent to TON wallet within 72 hours\n\nFor questions: @fragment_support",
        'profile': "👤 **USER PROFILE**\n\n🆔 **ID:** `{user_id}`\n💰 **BALANCE:** `{balance:.2f} USD`\n📅 **Registered:** {date}\n\n━━━━━━━━━━━━━━━━━━━━\nUse the button below to top up your balance.",
        'purchases': "📦 **PURCHASE HISTORY**\n\n{items}\n━━━━━━━━━━━━━━━━━━━━\nTotal purchases: {total}",
        'purchase_item_nft': "🎨 **{name}**\n💰 {price} USD\n🎨 Background: {background}\n📅 {date}\n🚚 Delivery: {delivery}",
        'purchase_item_username': "👤 **{name}**\n💰 {price} USD\n📅 {date}\n🚚 Transfer to: {delivery}",
        'purchase_item_number': "📱 **{name}**\n💰 {price} USD\n📅 {date}\n🚚 Receive at: {delivery}",
        'purchase_empty': "You have no purchases yet.\nVisit the store to purchase unique NFT assets.",
        'deposit_choose_currency': "💰 **SELECT CURRENCY**\n\nChoose cryptocurrency to top up your balance:\n\n💎 TON — low fees\n💵 USDT — stablecoin (available in 5 networks)\n₿ Bitcoin — main cryptocurrency\n⟠ Ethereum — smart contracts\n◎ Solana — high speed\n\nMinimum amount: **${min}**\nMaximum amount: **${max}**",
        'deposit_enter_amount': "💰 **DEPOSIT VIA {currency}**\n\nEnter deposit amount in USD:\n\n💡 Minimum: **${min}**\n💡 Maximum: **${max}**\n\nFunds will be credited after admin confirmation.",
        'deposit_min_error': "❌ **ERROR**\n\nMinimum deposit amount: **${min} USD**\n\nPlease enter a valid amount:",
        'deposit_max_error': "❌ **ERROR**\n\nMaximum deposit amount: **${max} USD**\n\nPlease enter a valid amount:",
        'deposit_instruction': "💳 **PAYMENT INSTRUCTIONS**\n\n1️⃣ Send **{amount} {currency}** to the following wallet:\n\n`{wallet}`\n\n2️⃣ After sending, click the «Send receipt» button and attach a **SCREENSHOT OF THE TRANSACTION**\n\n⚠️ **IMPORTANT:**\n• Send ONLY a screenshot from your wallet/exchange\n• Make sure the amount matches\n• Verification takes up to 30 minutes\n\n❌ Payments without a receipt are not processed",
        'insufficient_balance': "❌ **INSUFFICIENT FUNDS**\n\nRequired: **${price:.2f} USD**\nYour balance: **${balance:.2f} USD**\n\nTop up your balance and try again.",
        'purchase_success_nft': "✅ **PURCHASE CONFIRMED**\n\n🎁 **{item}**\n💰 Amount: **${price:.2f} USD**\n🎨 Background: **{background}**\n\n━━━━━━━━━━━━━━━━━━━━\n**🚚 DELIVERY INFORMATION**\n\nThe asset will be delivered to the specified @username within **48 hours**.\n\nThank you for your purchase!",
        'purchase_success_username': "✅ **PURCHASE CONFIRMED**\n\n👤 **{item}**\n💰 Amount: **${price:.2f} USD**\n\n━━━━━━━━━━━━━━━━━━━━\n**🚚 DELIVERY INFORMATION**\n\nThe username will be transferred to **{target}** within **48 hours**.\n\nThank you for your purchase!",
        'purchase_success_number': "✅ **PURCHASE CONFIRMED**\n\n📱 **{item}**\n💰 Amount: **${price:.2f} USD**\n\n━━━━━━━━━━━━━━━━━━━━\n**🚚 DELIVERY INFORMATION**\n\nThe number will be sent to TON wallet **{wallet}** within **72 hours**.\n\nThank you for your purchase!",
        'item_sold': "❌ **ITEM SOLD**\n\nThis instance has already been purchased by another user.\nPlease choose another item.",
        'payment_sent': "✅ **RECEIPT SENT**\n\nYour deposit request has been submitted for admin processing.\n\n⏱ Expected confirmation time: up to 30 minutes\n\nAfter confirmation, your balance will be automatically topped up.",
        'payment_confirmed': "✅ **BALANCE TOPPED UP**\n\n💰 Amount: **+${amount:.2f} USD**\n💵 New balance: **${balance:.2f} USD**\n\nThank you for your trust! Happy shopping.",
        'payment_rejected': "❌ **PAYMENT REJECTED**\n\nYour deposit request did not pass verification.\n\nReason: receipt mismatch or amount error.\n\nRequest ID: **{request_id}**\n\nFor details, contact support.",
        'admin_new_payment': "💰 **NEW DEPOSIT REQUEST**\n\n👤 User: `{user_id}`\n💵 Amount: **${amount}**\n💎 Currency: {currency}\n🔗 Network: {network}\n🏦 Wallet: `{wallet}`\n\nVerify the receipt and confirm the transaction.",
        'stats': "📊 **STORE STATISTICS**\n\n👥 Users: **{users}**\n💰 Total balance: **${balance:.2f}**\n\n📈 **SALES:**\n🎨 NFT gifts: **{nft_sold}**\n👤 Usernames: **{usernames_sold}**\n📱 Anonymous numbers: **{numbers_sold}**\n\n💎 Total sales: **{total_sold}**",
        'nft_card': "🎁 **{name}**\n\n💰 Price: **${price}**\n\n━━━━━━━━━━━━━━━━━━━━\n🎨 **SELECT BACKGROUND**\n\nAfter selecting the background, the model and pattern will be determined **RANDOMLY**, just like in real Telegram.",
        'ask_username': "👤 **SPECIFY RECIPIENT**\n\nEnter the @username of the Telegram account to which the NFT gift will be delivered:\n\n💡 Example: @username\n\n⚠️ Make sure the data is correct — it cannot be changed later.",
        'ask_wallet': "🏦 **SPECIFY WALLET**\n\nEnter the TON wallet to receive the anonymous number:\n\n💡 Example: EQD...\n\n⚠️ Make sure the address is correct — funds will be sent to this wallet.",
        'ask_target_username': "👤 **SPECIFY RECIPIENT**\n\nEnter the @username to which the username will be transferred:\n\n💡 Example: @username\n\n⚠️ Make sure the data is correct — it cannot be changed later.",
        'invalid_username': "❌ **INVALID FORMAT**\n\n@username must start with @ and contain only Latin letters, numbers, and underscores.\n\nPlease enter a valid username:",
        'invalid_wallet': "❌ **INVALID FORMAT**\n\nTON wallet must start with EQD or UQD and contain 48 characters.\n\nPlease enter a valid wallet address:",
        'admin_added': "✅ **NFT GIFT ADDED**\n\n📝 Name: **{name}**\n💰 Price: **${min} - ${max}**\n📦 Quantity: **{qty}** pcs.\n\nThe gift is now available for purchase.",
        'balance_added': "✅ **BALANCE TOPPED UP**\n\n👤 User: `{user_id}`\n💰 Amount: **+${amount}**\n💵 New balance: **${balance}**",
        'admin_access_denied': "⛔ **ACCESS DENIED**\n\nThis command is only available to the administrator.",
        'random_attributes': "🎲 **Model and pattern will be randomly determined**\n\nJust like in real Telegram, each gift receives a unique combination of characteristics."
    }
}


def get_text(lang: str, key: str, **kwargs):
    text = TEXTS.get(lang, TEXTS['ru']).get(key, key)
    return text.format(**kwargs) if kwargs else text


# === СТАРТ ===
@router.message(Command("start"))
async def cmd_start(message: Message):
    user_id = message.from_user.id
    await db.add_user(user_id)

    await message.answer(
        "🌐 Выберите язык / Choose language:",
        reply_markup=get_language_keyboard()
    )


@router.callback_query(F.data.startswith("lang_"))
async def set_language(callback: CallbackQuery):
    lang = callback.data.split("_")[1]
    user_id = callback.from_user.id

    await db.set_user_language(user_id, lang)

    is_admin = (user_id == config.ADMIN_ID)
    await callback.message.delete()
    await callback.message.answer(
        get_text(lang, 'welcome'),
        reply_markup=get_main_menu(is_admin, lang),
        parse_mode="Markdown"
    )
    await callback.answer()


# === HELP ===
@router.message(Command("help"))
async def cmd_help(message: Message):
    user_id = message.from_user.id
    lang = await db.get_user_language(user_id)

    await message.answer(
        get_text(lang, 'help'),
        parse_mode="Markdown"
    )


# === АДМИН-ПАНЕЛЬ ===
@router.message(Command("admin"))
async def cmd_admin(message: Message):
    user_id = message.from_user.id

    if user_id != config.ADMIN_ID:
        lang = await db.get_user_language(user_id)
        await message.answer(get_text(lang, 'admin_access_denied'))
        return

    lang = await db.get_user_language(user_id)
    await message.answer(
        "⚙️ **АДМИН-ПАНЕЛЬ**" if lang == 'ru' else "⚙️ **ADMIN PANEL**",
        reply_markup=get_admin_panel(lang),
        parse_mode="Markdown"
    )


# === ГЛАВНОЕ МЕНЮ ===
@router.callback_query(F.data == "back_to_main")
async def back_to_main(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang = await db.get_user_language(user_id)
    is_admin = (user_id == config.ADMIN_ID)

    await callback.message.edit_text(
        get_text(lang, 'welcome'),
        reply_markup=get_main_menu(is_admin, lang),
        parse_mode="Markdown"
    )
    await callback.answer()


# === ПРОФИЛЬ ===
@router.callback_query(F.data == "profile")
async def show_profile(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang = await db.get_user_language(user_id)
    balance = await db.get_balance(user_id)

    await callback.message.edit_text(
        get_text(lang, 'profile', user_id=user_id, balance=balance, date=datetime.now().strftime('%d.%m.%Y')),
        reply_markup=get_main_menu(user_id == config.ADMIN_ID, lang),
        parse_mode="Markdown"
    )
    await callback.answer()


# === МОИ ПОКУПКИ ===
@router.callback_query(F.data == "my_purchases")
async def show_purchases(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang = await db.get_user_language(user_id)

    purchases = await db.get_user_purchases(user_id, 20)

    if not purchases:
        text = get_text(lang, 'purchase_empty')
    else:
        items_text = []
        for p in purchases:
            date = datetime.strptime(p['bought_at'], '%Y-%m-%d %H:%M:%S').strftime('%d.%m.%Y %H:%M')

            if p['type'] == 'nft':
                delivery = p.get('delivery_info', '@username')
                items_text.append(get_text(lang, 'purchase_item_nft',
                                           name=p['item_name'], price=p['price'],
                                           background=p.get('background', 'Black'),
                                           date=date, delivery=delivery))
            elif p['type'] == 'username':
                delivery = p.get('delivery_info', '@username')
                items_text.append(get_text(lang, 'purchase_item_username',
                                           name=p['item_name'], price=p['price'], date=date, delivery=delivery))
            else:
                delivery = p.get('delivery_info', 'TON wallet')
                items_text.append(get_text(lang, 'purchase_item_number',
                                           name=p['item_name'], price=p['price'], date=date, delivery=delivery))

        text = get_text(lang, 'purchases', items='\n\n━━━━━━━━━━━━━━━━━━━━\n\n'.join(items_text), total=len(purchases))

    await callback.message.edit_text(
        text,
        reply_markup=get_main_menu(user_id == config.ADMIN_ID, lang),
        parse_mode="Markdown"
    )
    await callback.answer()


# === МАГАЗИН ===
@router.callback_query(F.data == "shop_menu")
async def shop_menu(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang = await db.get_user_language(user_id)

    await callback.message.edit_text(
        "🛍️ **КАТАЛОГ**\n\nВыберите категорию для просмотра доступных активов:" if lang == 'ru' else "🛍️ **CATALOG**\n\nSelect a category to view available assets:",
        reply_markup=get_shop_menu(lang),
        parse_mode="Markdown"
    )
    await callback.answer()


# === NFT КАТЕГОРИЯ ===
@router.callback_query(F.data == "category_nft")
async def category_nft(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang = await db.get_user_language(user_id)

    gifts = await db.get_all_nft_gifts()

    if not gifts:
        await callback.message.edit_text(
            "😔 Временно отсутствуют NFT подарки." if lang == 'ru' else "😔 NFT gifts temporarily unavailable.",
            reply_markup=get_shop_menu(lang)
        )
        await callback.answer()
        return

    await callback.message.edit_text(
        "🎨 **NFT ПОДАРКИ**\n\nДоступные коллекции:" if lang == 'ru' else "🎨 **NFT GIFTS**\n\nAvailable collections:",
        reply_markup=get_nft_list_keyboard(gifts, 0, config.ITEMS_PER_PAGE, lang),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("gift_"))
async def show_gift_instances(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = await db.get_user_language(user_id)
    gift_id = int(callback.data.split("_")[1])

    instances = await db.get_nft_instances(gift_id)

    if not instances:
        await callback.answer(get_text(lang, 'item_sold'), show_alert=True)
        return

    instance = instances[0]
    gift_info = await db.get_all_nft_gifts()
    gift_name = next((g['name'] for g in gift_info if g['id'] == gift_id), "Unknown")

    await state.update_data(
        instance_id=instance['id'],
        gift_name=gift_name,
        price=instance['price'],
        gift_id=gift_id
    )
    await state.set_state(BuyNFTStates.choosing_background)

    text = get_text(lang, 'nft_card', name=gift_name, price=instance['price'])

    await callback.message.edit_text(
        text,
        reply_markup=get_background_keyboard(lang),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(BuyNFTStates.choosing_background, F.data.startswith("bg_"))
async def choose_background(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = await db.get_user_language(user_id)
    background_index = int(callback.data.split("_")[1])
    background = config.BACKGROUNDS[background_index]

    await state.update_data(selected_background=background)
    await state.set_state(BuyNFTStates.waiting_for_username)

    await callback.message.edit_text(
        get_text(lang, 'ask_username'),
        reply_markup=get_cancel_keyboard(lang),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(BuyNFTStates.choosing_background, F.data == "bg_random")
async def random_background(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = await db.get_user_language(user_id)
    background = random.choice(config.BACKGROUNDS)

    await state.update_data(selected_background=background)
    await state.set_state(BuyNFTStates.waiting_for_username)

    await callback.message.edit_text(
        get_text(lang, 'ask_username'),
        reply_markup=get_cancel_keyboard(lang),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.message(BuyNFTStates.waiting_for_username)
async def process_nft_username(message: Message, state: FSMContext):
    user_id = message.from_user.id
    lang = await db.get_user_language(user_id)
    username = message.text.strip()

    if not username.startswith('@') or len(username) < 2:
        await message.answer(get_text(lang, 'invalid_username'), reply_markup=get_cancel_keyboard(lang))
        return

    await state.update_data(target_username=username)
    data = await state.get_data()

    text = get_text(lang, 'purchase_success_nft',
                    item=data['gift_name'],
                    price=data['price'],
                    background=data['selected_background'])

    await message.answer(
        text,
        reply_markup=get_confirm_purchase_keyboard(lang),
        parse_mode="Markdown"
    )
    await state.set_state(BuyNFTStates.confirming)


@router.callback_query(BuyNFTStates.confirming, F.data == "confirm_purchase")
async def confirm_nft_purchase(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = await db.get_user_language(user_id)
    data = await state.get_data()

    instance_id = data['instance_id']
    gift_name = data['gift_name']
    price = data['price']
    background = data['selected_background']
    target_username = data['target_username']

    instance = await db.get_nft_instance(instance_id)

    if not instance:
        await callback.answer(get_text(lang, 'item_sold'), show_alert=True)
        await state.clear()
        await category_nft(callback)
        return

    balance = await db.get_balance(user_id)

    if balance < price:
        await callback.answer(
            get_text(lang, 'insufficient_balance', price=price, balance=balance),
            show_alert=True
        )
        await state.clear()
        return

    success = await db.buy_nft(instance_id, user_id, price, target_username)

    if success:
        new_balance = await db.get_balance(user_id)
        await callback.answer("✅ Покупка подтверждена!" if lang == 'ru' else "✅ Purchase confirmed!", show_alert=True)

        text = get_text(lang, 'purchase_success_nft',
                        item=gift_name, price=price, background=background)

        await callback.message.edit_text(
            text,
            reply_markup=get_main_menu(user_id == config.ADMIN_ID, lang),
            parse_mode="Markdown"
        )
    else:
        await callback.answer("❌ Ошибка при покупке" if lang == 'ru' else "❌ Purchase error", show_alert=True)

    await state.clear()


# === АНОНИМНЫЕ НОМЕРА ===
@router.callback_query(F.data == "category_numbers")
async def category_numbers(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang = await db.get_user_language(user_id)

    numbers = await db.get_available_numbers()

    if not numbers:
        await callback.message.edit_text(
            "😔 Анонимные номера временно отсутствуют." if lang == 'ru' else "😔 Anonymous numbers temporarily unavailable.",
            reply_markup=get_shop_menu(lang)
        )
        await callback.answer()
        return

    await callback.message.edit_text(
        "📱 **АНОНИМНЫЕ НОМЕРА (+888)**\n\nДоступные номера:" if lang == 'ru' else "📱 **ANONYMOUS NUMBERS (+888)**\n\nAvailable numbers:",
        reply_markup=get_numbers_keyboard(numbers, 0, config.ITEMS_PER_PAGE, lang),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("number_"))
async def show_number(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = await db.get_user_language(user_id)
    number_id = int(callback.data.split("_")[1])

    number = await db.get_number(number_id)

    if not number:
        await callback.answer(get_text(lang, 'item_sold'), show_alert=True)
        await category_numbers(callback)
        return

    await state.update_data(
        number_id=number['id'],
        number=number['number'],
        price=number['price']
    )
    await state.set_state(BuyNumberStates.waiting_for_wallet)

    await callback.message.edit_text(
        get_text(lang, 'ask_wallet'),
        reply_markup=get_cancel_keyboard(lang),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.message(BuyNumberStates.waiting_for_wallet)
async def process_number_wallet(message: Message, state: FSMContext):
    user_id = message.from_user.id
    lang = await db.get_user_language(user_id)
    wallet = message.text.strip()

    if not wallet.startswith(('EQD', 'UQD')) or len(wallet) != 48:
        await message.answer(get_text(lang, 'invalid_wallet'), reply_markup=get_cancel_keyboard(lang))
        return

    await state.update_data(wallet_address=wallet)
    data = await state.get_data()

    text = get_text(lang, 'purchase_success_number',
                    item=data['number'],
                    price=data['price'],
                    wallet=wallet)

    await message.answer(
        text,
        reply_markup=get_confirm_purchase_keyboard(lang),
        parse_mode="Markdown"
    )
    await state.set_state(BuyNumberStates.confirming)


@router.callback_query(BuyNumberStates.confirming, F.data == "confirm_purchase")
async def confirm_number_purchase(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = await db.get_user_language(user_id)
    data = await state.get_data()

    number_id = data['number_id']
    number = data['number']
    price = data['price']
    wallet = data['wallet_address']

    number_obj = await db.get_number(number_id)

    if not number_obj:
        await callback.answer(get_text(lang, 'item_sold'), show_alert=True)
        await state.clear()
        await category_numbers(callback)
        return

    balance = await db.get_balance(user_id)

    if balance < price:
        await callback.answer(
            get_text(lang, 'insufficient_balance', price=price, balance=balance),
            show_alert=True
        )
        await state.clear()
        return

    success = await db.buy_number(number_id, user_id, price, wallet)

    if success:
        new_balance = await db.get_balance(user_id)
        await callback.answer("✅ Покупка подтверждена!" if lang == 'ru' else "✅ Purchase confirmed!", show_alert=True)

        text = get_text(lang, 'purchase_success_number',
                        item=number, price=price, wallet=wallet)

        await callback.message.edit_text(
            text,
            reply_markup=get_main_menu(user_id == config.ADMIN_ID, lang),
            parse_mode="Markdown"
        )
    else:
        await callback.answer("❌ Ошибка при покупке" if lang == 'ru' else "❌ Purchase error", show_alert=True)

    await state.clear()


# === ЮЗЕРНЕЙМЫ ===
@router.callback_query(F.data == "category_usernames")
async def category_usernames(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang = await db.get_user_language(user_id)

    usernames = await db.get_available_usernames()

    if not usernames:
        await callback.message.edit_text(
            "😔 Юзернеймы временно отсутствуют." if lang == 'ru' else "😔 Usernames temporarily unavailable.",
            reply_markup=get_shop_menu(lang)
        )
        await callback.answer()
        return

    await callback.message.edit_text(
        "👤 **NFT ЮЗЕРНЕЙМЫ**\n\nДоступные имена:" if lang == 'ru' else "👤 **NFT USERNAMES**\n\nAvailable names:",
        reply_markup=get_usernames_keyboard(usernames, 0, config.ITEMS_PER_PAGE, lang),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("username_"))
async def show_username(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = await db.get_user_language(user_id)
    username_id = int(callback.data.split("_")[1])

    username_obj = await db.get_username(username_id)

    if not username_obj:
        await callback.answer(get_text(lang, 'item_sold'), show_alert=True)
        await category_usernames(callback)
        return

    await state.update_data(
        username_id=username_obj['id'],
        username=username_obj['username'],
        price=username_obj['price']
    )
    await state.set_state(BuyUsernameStates.waiting_for_target)

    await callback.message.edit_text(
        get_text(lang, 'ask_target_username'),
        reply_markup=get_cancel_keyboard(lang),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.message(BuyUsernameStates.waiting_for_target)
async def process_username_target(message: Message, state: FSMContext):
    user_id = message.from_user.id
    lang = await db.get_user_language(user_id)
    target = message.text.strip()

    if not target.startswith('@') or len(target) < 2:
        await message.answer(get_text(lang, 'invalid_username'), reply_markup=get_cancel_keyboard(lang))
        return

    await state.update_data(target_username=target)
    data = await state.get_data()

    text = get_text(lang, 'purchase_success_username',
                    item=data['username'],
                    price=data['price'],
                    target=target)

    await message.answer(
        text,
        reply_markup=get_confirm_purchase_keyboard(lang),
        parse_mode="Markdown"
    )
    await state.set_state(BuyUsernameStates.confirming)


@router.callback_query(BuyUsernameStates.confirming, F.data == "confirm_purchase")
async def confirm_username_purchase(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = await db.get_user_language(user_id)
    data = await state.get_data()

    username_id = data['username_id']
    username = data['username']
    price = data['price']
    target = data['target_username']

    username_obj = await db.get_username(username_id)

    if not username_obj:
        await callback.answer(get_text(lang, 'item_sold'), show_alert=True)
        await state.clear()
        await category_usernames(callback)
        return

    balance = await db.get_balance(user_id)

    if balance < price:
        await callback.answer(
            get_text(lang, 'insufficient_balance', price=price, balance=balance),
            show_alert=True
        )
        await state.clear()
        return

    success = await db.buy_username(username_id, user_id, price, target)

    if success:
        new_balance = await db.get_balance(user_id)
        await callback.answer("✅ Покупка подтверждена!" if lang == 'ru' else "✅ Purchase confirmed!", show_alert=True)

        text = get_text(lang, 'purchase_success_username',
                        item=username, price=price, target=target)

        await callback.message.edit_text(
            text,
            reply_markup=get_main_menu(user_id == config.ADMIN_ID, lang),
            parse_mode="Markdown"
        )
    else:
        await callback.answer("❌ Ошибка при покупке" if lang == 'ru' else "❌ Purchase error", show_alert=True)

    await state.clear()


# === ПОПОЛНЕНИЕ БАЛАНСА ===
@router.callback_query(F.data == "deposit")
async def deposit_start(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = await db.get_user_language(user_id)

    await state.set_state(DepositStates.waiting_for_currency)
    await callback.message.edit_text(
        get_text(lang, 'deposit_choose_currency', min=config.MIN_DEPOSIT_AMOUNT, max=config.MAX_DEPOSIT_AMOUNT),
        reply_markup=get_deposit_currency_keyboard(lang),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(DepositStates.waiting_for_currency, F.data.startswith("deposit_"))
async def deposit_currency_selected(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = await db.get_user_language(user_id)
    currency = callback.data.split("_")[1]

    if currency == 'USDT':
        await state.update_data(currency=currency)
        await callback.message.edit_text(
            "💵 **ВЫБЕРИТЕ СЕТЬ USDT**" if lang == 'ru' else "💵 **SELECT USDT NETWORK**",
            reply_markup=get_usdt_network_keyboard(lang),
            parse_mode="Markdown"
        )
    else:
        wallet = config.WALLETS.get(currency, "Кошелек не указан")
        network = {'TON': 'TON', 'BTC': 'Bitcoin', 'ETH': 'Ethereum', 'SOL': 'Solana', 'TRX': 'Tron', 'BNB': 'BSC'}.get(
            currency, currency)

        await state.update_data(currency=currency, wallet=wallet, network=network)
        await state.set_state(DepositStates.waiting_for_amount)

        await callback.message.edit_text(
            get_text(lang, 'deposit_enter_amount', currency=currency, min=config.MIN_DEPOSIT_AMOUNT,
                     max=config.MAX_DEPOSIT_AMOUNT),
            reply_markup=get_cancel_keyboard(lang),
            parse_mode="Markdown"
        )

    await callback.answer()


@router.callback_query(DepositStates.waiting_for_currency, F.data.startswith("usdt_"))
async def deposit_usdt_selected(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = await db.get_user_language(user_id)
    network = callback.data.split("_")[1]

    wallet = config.USDT_WALLETS.get(network, "Кошелек не указан")

    await state.update_data(currency=f"USDT ({network})", wallet=wallet, network=network)
    await state.set_state(DepositStates.waiting_for_amount)

    await callback.message.edit_text(
        get_text(lang, 'deposit_enter_amount', currency=f"USDT ({network})", min=config.MIN_DEPOSIT_AMOUNT,
                 max=config.MAX_DEPOSIT_AMOUNT),
        reply_markup=get_cancel_keyboard(lang),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.message(DepositStates.waiting_for_amount)
async def deposit_amount(message: Message, state: FSMContext):
    user_id = message.from_user.id
    lang = await db.get_user_language(user_id)
    data = await state.get_data()

    try:
        amount = float(message.text)
        if amount < config.MIN_DEPOSIT_AMOUNT:
            await message.answer(get_text(lang, 'deposit_min_error', min=config.MIN_DEPOSIT_AMOUNT),
                                 reply_markup=get_cancel_keyboard(lang))
            return
        if amount > config.MAX_DEPOSIT_AMOUNT:
            await message.answer(get_text(lang, 'deposit_max_error', max=config.MAX_DEPOSIT_AMOUNT),
                                 reply_markup=get_cancel_keyboard(lang))
            return

        await state.update_data(amount=amount)
        await state.set_state(DepositStates.waiting_for_screenshot)

        currency = data.get('currency', 'TON')
        wallet = data.get('wallet', config.WALLETS.get(currency, "Кошелек не указан"))

        await message.answer(
            get_text(lang, 'deposit_instruction', amount=amount, currency=currency, wallet=wallet),
            reply_markup=get_cancel_keyboard(lang),
            parse_mode="Markdown"
        )
    except ValueError:
        await message.answer(
            "❌ Введите корректную сумму:" if lang == 'ru' else "❌ Enter a valid amount:",
            reply_markup=get_cancel_keyboard(lang)
        )


@router.message(DepositStates.waiting_for_screenshot, F.photo)
async def deposit_screenshot(message: Message, state: FSMContext, bot: Bot):
    user_id = message.from_user.id
    lang = await db.get_user_language(user_id)
    data = await state.get_data()

    amount = data.get('amount', 0)
    currency = data.get('currency', 'TON')
    wallet = data.get('wallet', '')
    network = data.get('network', '')

    payment_id = await db.add_payment(user_id, amount, currency, message.message_id)

    await bot.send_photo(
        config.ADMIN_ID,
        photo=message.photo[-1].file_id,
        caption=get_text('ru', 'admin_new_payment', user_id=user_id, amount=amount, currency=currency, network=network,
                         wallet=wallet),
        reply_markup=get_payment_confirm_keyboard(payment_id, amount, 'ru'),
        parse_mode="Markdown"
    )

    await message.answer(
        get_text(lang, 'payment_sent'),
        reply_markup=get_main_menu(user_id == config.ADMIN_ID, lang),
        parse_mode="Markdown"
    )
    await state.clear()


# === АДМИН-ПАНЕЛЬ ===
@router.callback_query(F.data == "admin_panel")
async def admin_panel_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    if user_id != config.ADMIN_ID:
        await callback.answer("⛔ Доступ запрещен!", show_alert=True)
        return

    lang = await db.get_user_language(user_id)
    await callback.message.edit_text(
        "⚙️ **АДМИН-ПАНЕЛЬ**" if lang == 'ru' else "⚙️ **ADMIN PANEL**",
        reply_markup=get_admin_panel(lang),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data == "admin_add_nft")
async def admin_add_nft(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != config.ADMIN_ID:
        await callback.answer("⛔ Доступ запрещен!", show_alert=True)
        return

    lang = await db.get_user_language(callback.from_user.id)
    await state.set_state(AdminAddNFTStates.waiting_for_name)
    await callback.message.edit_text(
        "➕ **Добавление NFT подарка**\n\nВведите название подарка:" if lang == 'ru' else "➕ **Add NFT gift**\n\nEnter gift name:",
        reply_markup=get_cancel_keyboard(lang),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.message(AdminAddNFTStates.waiting_for_name)
async def admin_add_nft_name(message: Message, state: FSMContext):
    if message.from_user.id != config.ADMIN_ID:
        return

    lang = await db.get_user_language(message.from_user.id)
    await state.update_data(name=message.text)
    await state.set_state(AdminAddNFTStates.waiting_for_min_price)

    await message.answer(
        f"📝 Название: {message.text}\n\nВведите минимальную цену (USD):" if lang == 'ru' else f"📝 Name: {message.text}\n\nEnter minimum price (USD):",
        reply_markup=get_cancel_keyboard(lang)
    )


@router.message(AdminAddNFTStates.waiting_for_min_price)
async def admin_add_nft_min_price(message: Message, state: FSMContext):
    if message.from_user.id != config.ADMIN_ID:
        return

    lang = await db.get_user_language(message.from_user.id)
    try:
        min_price = float(message.text)
        await state.update_data(min_price=min_price)
        await state.set_state(AdminAddNFTStates.waiting_for_max_price)

        await message.answer(
            f"💰 Минимальная цена: ${min_price}\n\nВведите максимальную цену (USD):" if lang == 'ru' else f"💰 Minimum price: ${min_price}\n\nEnter maximum price (USD):",
            reply_markup=get_cancel_keyboard(lang)
        )
    except ValueError:
        await message.answer("❌ Введите корректное число:" if lang == 'ru' else "❌ Enter a valid number:")


@router.message(AdminAddNFTStates.waiting_for_max_price)
async def admin_add_nft_max_price(message: Message, state: FSMContext):
    if message.from_user.id != config.ADMIN_ID:
        return

    lang = await db.get_user_language(message.from_user.id)
    try:
        max_price = float(message.text)
        data = await state.get_data()

        if max_price <= data['min_price']:
            await message.answer(
                "❌ Максимальная цена должна быть больше минимальной!\nВведите максимальную цену еще раз:" if lang == 'ru' else "❌ Maximum price must be greater than minimum!\nEnter maximum price again:"
            )
            return

        await state.update_data(max_price=max_price)
        await state.set_state(AdminAddNFTStates.waiting_for_quantity)

        await message.answer(
            f"💰 Ценовой диапазон: ${data['min_price']} - ${max_price}\n\nВведите количество экземпляров:" if lang == 'ru' else f"💰 Price range: ${data['min_price']} - ${max_price}\n\nEnter quantity:",
            reply_markup=get_cancel_keyboard(lang)
        )
    except ValueError:
        await message.answer("❌ Введите корректное число:" if lang == 'ru' else "❌ Enter a valid number:")


@router.message(AdminAddNFTStates.waiting_for_quantity)
async def admin_add_nft_quantity(message: Message, state: FSMContext):
    if message.from_user.id != config.ADMIN_ID:
        return

    lang = await db.get_user_language(message.from_user.id)
    try:
        quantity = int(message.text)
        if quantity <= 0:
            await message.answer(
                "❌ Количество должно быть положительным!" if lang == 'ru' else "❌ Quantity must be positive!")
            return

        data = await state.get_data()

        gift_id = await db.add_nft_gift(
            data['name'],
            data['min_price'],
            data['max_price'],
            quantity
        )

        await db.generate_nft_instances(gift_id)

        await message.answer(
            get_text(lang, 'admin_added', name=data['name'], min=data['min_price'], max=data['max_price'],
                     qty=quantity),
            reply_markup=get_main_menu(True, lang),
            parse_mode="Markdown"
        )

        await state.clear()

    except ValueError:
        await message.answer("❌ Введите корректное число:" if lang == 'ru' else "❌ Enter a valid number:")


@router.callback_query(F.data == "admin_add_balance")
async def admin_add_balance(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != config.ADMIN_ID:
        await callback.answer("⛔ Доступ запрещен!", show_alert=True)
        return

    lang = await db.get_user_language(callback.from_user.id)
    await state.set_state(AdminAddBalanceStates.waiting_for_user_id)
    await callback.message.edit_text(
        "💰 **Пополнение баланса пользователя**\n\nВведите Telegram ID пользователя:" if lang == 'ru' else "💰 **Top up user balance**\n\nEnter user Telegram ID:",
        reply_markup=get_cancel_keyboard(lang),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.message(AdminAddBalanceStates.waiting_for_user_id)
async def admin_add_balance_user_id(message: Message, state: FSMContext):
    if message.from_user.id != config.ADMIN_ID:
        return

    lang = await db.get_user_language(message.from_user.id)
    try:
        user_id = int(message.text)
        await state.update_data(target_user_id=user_id)
        await state.set_state(AdminAddBalanceStates.waiting_for_amount)

        await message.answer(
            f"👤 Пользователь: {user_id}\n\nВведите сумму пополнения (USD):" if lang == 'ru' else f"👤 User: {user_id}\n\nEnter deposit amount (USD):",
            reply_markup=get_cancel_keyboard(lang)
        )
    except ValueError:
        await message.answer("❌ Введите корректный ID пользователя:" if lang == 'ru' else "❌ Enter a valid user ID:")


@router.message(AdminAddBalanceStates.waiting_for_amount)
async def admin_add_balance_amount(message: Message, state: FSMContext, bot: Bot):
    if message.from_user.id != config.ADMIN_ID:
        return

    lang = await db.get_user_language(message.from_user.id)
    try:
        amount = float(message.text)
        data = await state.get_data()
        target_user_id = data['target_user_id']

        await db.update_balance(target_user_id, amount)
        new_balance = await db.get_balance(target_user_id)

        user_lang = await db.get_user_language(target_user_id)

        try:
            await bot.send_message(
                target_user_id,
                get_text(user_lang, 'payment_confirmed', amount=amount, balance=new_balance),
                parse_mode="Markdown"
            )
        except:
            pass

        await message.answer(
            get_text(lang, 'balance_added', user_id=target_user_id, amount=amount, balance=new_balance),
            reply_markup=get_main_menu(True, lang),
            parse_mode="Markdown"
        )

        await state.clear()

    except ValueError:
        await message.answer("❌ Введите корректную сумму:" if lang == 'ru' else "❌ Enter a valid amount:")


@router.callback_query(F.data == "admin_stats")
async def admin_stats(callback: CallbackQuery):
    if callback.from_user.id != config.ADMIN_ID:
        await callback.answer("⛔ Доступ запрещен!", show_alert=True)
        return

    lang = await db.get_user_language(callback.from_user.id)

    async with aiosqlite.connect("shop.db") as conn:
        async with conn.execute("SELECT COUNT(*) FROM users") as cursor:
            users_count = (await cursor.fetchone())[0]

        async with conn.execute("SELECT SUM(balance) FROM users") as cursor:
            total_balance = (await cursor.fetchone())[0] or 0

        async with conn.execute("SELECT COUNT(*) FROM nft_instances WHERE is_sold = 1") as cursor:
            nft_sold = (await cursor.fetchone())[0]

        async with conn.execute("SELECT COUNT(*) FROM usernames WHERE is_sold = 1") as cursor:
            usernames_sold = (await cursor.fetchone())[0]

        async with conn.execute("SELECT COUNT(*) FROM anonymous_numbers WHERE is_sold = 1") as cursor:
            numbers_sold = (await cursor.fetchone())[0]

    await callback.message.edit_text(
        get_text(lang, 'stats', users=users_count, balance=total_balance, nft_sold=nft_sold,
                 usernames_sold=usernames_sold, numbers_sold=numbers_sold,
                 total_sold=nft_sold + usernames_sold + numbers_sold),
        reply_markup=get_admin_panel(lang),
        parse_mode="Markdown"
    )
    await callback.answer()


# === ПОДТВЕРЖДЕНИЕ ПЛАТЕЖЕЙ ===
@router.callback_query(F.data.startswith("confirm_payment_"))
async def confirm_payment(callback: CallbackQuery, bot: Bot):
    if callback.from_user.id != config.ADMIN_ID:
        await callback.answer("⛔ Доступ запрещен!", show_alert=True)
        return

    payment_id = int(callback.data.split("_")[2])
    payment = await db.get_payment(payment_id)

    if not payment or payment['status'] != 'pending':
        await callback.answer("❌ Платеж уже обработан!", show_alert=True)
        return

    await db.update_balance(payment['user_id'], payment['amount'])
    await db.confirm_payment(payment_id)

    user_lang = await db.get_user_language(payment['user_id'])
    new_balance = await db.get_balance(payment['user_id'])

    try:
        await bot.send_message(
            payment['user_id'],
            get_text(user_lang, 'payment_confirmed', amount=payment['amount'], balance=new_balance),
            parse_mode="Markdown"
        )
    except:
        pass

    await callback.message.edit_caption(
        f"{callback.message.caption}\n\n✅ **ПОДТВЕРЖДЕНО**\n🕐 {datetime.now().strftime('%d.%m.%Y %H:%M')}",
        parse_mode="Markdown"
    )
    await callback.answer("✅ Платеж подтвержден!")


@router.callback_query(F.data.startswith("reject_payment_"))
async def reject_payment(callback: CallbackQuery, bot: Bot):
    if callback.from_user.id != config.ADMIN_ID:
        await callback.answer("⛔ Доступ запрещен!", show_alert=True)
        return

    payment_id = int(callback.data.split("_")[2])
    payment = await db.get_payment(payment_id)

    if not payment or payment['status'] != 'pending':
        await callback.answer("❌ Платеж уже обработан!", show_alert=True)
        return

    await db.reject_payment(payment_id)

    user_lang = await db.get_user_language(payment['user_id'])

    try:
        await bot.send_message(
            payment['user_id'],
            get_text(user_lang, 'payment_rejected', request_id=payment_id),
            parse_mode="Markdown"
        )
    except:
        pass

    await callback.message.edit_caption(
        f"{callback.message.caption}\n\n❌ **ОТКЛОНЕНО**\n🕐 {datetime.now().strftime('%d.%m.%Y %H:%M')}",
        parse_mode="Markdown"
    )
    await callback.answer("❌ Платеж отклонен!")


# === НАВИГАЦИЯ ===
@router.callback_query(F.data == "back_to_shop")
async def back_to_shop(callback: CallbackQuery):
    await shop_menu(callback)


@router.callback_query(F.data == "back_to_gift_list")
async def back_to_gift_list(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await category_nft(callback)


@router.callback_query(F.data == "back_to_numbers")
async def back_to_numbers(callback: CallbackQuery):
    await category_numbers(callback)


@router.callback_query(F.data == "back_to_usernames")
async def back_to_usernames(callback: CallbackQuery):
    await category_usernames(callback)


@router.callback_query(F.data == "cancel_purchase")
async def cancel_purchase(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = await db.get_user_language(user_id)
    await state.clear()
    await category_nft(callback)


@router.callback_query(F.data == "cancel_delivery")
async def cancel_delivery(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = await db.get_user_language(user_id)
    await state.clear()
    await shop_menu(callback)


@router.callback_query(F.data.startswith("nft_page_"))
async def nft_pagination(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang = await db.get_user_language(user_id)
    page = int(callback.data.split("_")[2])

    gifts = await db.get_all_nft_gifts()
    await callback.message.edit_reply_markup(
        reply_markup=get_nft_list_keyboard(gifts, page, config.ITEMS_PER_PAGE, lang)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("numbers_page_"))
async def numbers_pagination(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang = await db.get_user_language(user_id)
    page = int(callback.data.split("_")[2])

    numbers = await db.get_available_numbers()
    await callback.message.edit_reply_markup(
        reply_markup=get_numbers_keyboard(numbers, page, config.ITEMS_PER_PAGE, lang)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("usernames_page_"))
async def usernames_pagination(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang = await db.get_user_language(user_id)
    page = int(callback.data.split("_")[2])

    usernames = await db.get_available_usernames()
    await callback.message.edit_reply_markup(
        reply_markup=get_usernames_keyboard(usernames, page, config.ITEMS_PER_PAGE, lang)
    )
    await callback.answer()


@router.callback_query(F.data == "cancel_action")
async def cancel_action(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = await db.get_user_language(user_id)
    await state.clear()

    await callback.message.edit_text(
        "✅ Действие отменено" if lang == 'ru' else "✅ Action cancelled",
        reply_markup=get_main_menu(user_id == config.ADMIN_ID, lang)
    )
    await callback.answer()