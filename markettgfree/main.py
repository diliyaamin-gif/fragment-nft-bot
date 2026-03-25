import asyncio
import logging
import random
import aiosqlite
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from config import config
from database import Database
from handlers import router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def init_database():
    db = Database()
    await db.init_db()

    async with aiosqlite.connect("shop.db") as conn:
        async with conn.execute("SELECT COUNT(*) FROM nft_gifts") as cursor:
            count = await cursor.fetchone()

            if count[0] == 0:
                logger.info("Заполняем базу данных NFT подарками...")

                for name, data in config.NFT_GIFTS.items():
                    gift_id = await db.add_nft_gift(
                        name,
                        data['min_price'],
                        data['max_price'],
                        data['quantity']
                    )
                    await db.generate_nft_instances(gift_id)
                    logger.info(f"Добавлен NFT: {name} ({data['quantity']} шт.)")

                for num_data in config.ANONYMOUS_NUMBERS:
                    price = random.uniform(num_data['min_price'], num_data['max_price'])
                    await db.add_anonymous_number(num_data['number'], round(price, 2))

                for username_data in config.USERNAMES['4_letter']:
                    await db.add_username(username_data['username'], username_data['price'], "4 буквы")

                for username_data in config.USERNAMES['5_letter']:
                    await db.add_username(username_data['username'], username_data['price'], "5 букв")

                for username_data in config.USERNAMES['long']:
                    price = random.uniform(username_data['min_price'], username_data['max_price'])
                    await db.add_username(username_data['username'], round(price, 2), "Длинный")

                logger.info("База данных успешно заполнена!")

    return db


async def main():
    logger.info("Запуск Fragment NFT Shop бота...")

    bot = Bot(token=config.BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    await init_database()
    dp.include_router(router)

    await bot.set_my_commands([
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="help", description="Помощь"),
    ])

    logger.info("Бот успешно запущен!")

    try:
        await dp.start_polling(bot, skip_updates=True)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())