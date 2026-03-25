import aiosqlite
import random
from typing import Optional, List, Dict
from config import config


class Database:
    def __init__(self, db_path: str = "shop.db"):
        self.db_path = db_path

    async def init_db(self):
        async with aiosqlite.connect(self.db_path) as db:
            # Пользователи
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    balance REAL DEFAULT 0,
                    language TEXT DEFAULT 'ru',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # NFT подарки (типы)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS nft_gifts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    min_price REAL NOT NULL,
                    max_price REAL NOT NULL,
                    total_quantity INTEGER NOT NULL,
                    sold_quantity INTEGER DEFAULT 0
                )
            """)

            # Экземпляры NFT
            await db.execute("""
                CREATE TABLE IF NOT EXISTS nft_instances (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    gift_id INTEGER,
                    price REAL NOT NULL,
                    background TEXT DEFAULT 'Black',
                    is_sold BOOLEAN DEFAULT 0,
                    buyer_id INTEGER,
                    bought_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    delivery_info TEXT,
                    FOREIGN KEY (gift_id) REFERENCES nft_gifts(id)
                )
            """)

            # Анонимные номера
            await db.execute("""
                CREATE TABLE IF NOT EXISTS anonymous_numbers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    number TEXT NOT NULL,
                    price REAL NOT NULL,
                    is_sold BOOLEAN DEFAULT 0,
                    buyer_id INTEGER,
                    bought_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    wallet_address TEXT,
                    delivery_info TEXT
                )
            """)

            # Юзернеймы
            await db.execute("""
                CREATE TABLE IF NOT EXISTS usernames (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    price REAL NOT NULL,
                    category TEXT,
                    is_sold BOOLEAN DEFAULT 0,
                    buyer_id INTEGER,
                    bought_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    target_username TEXT,
                    delivery_info TEXT
                )
            """)

            # Платежи
            await db.execute("""
                CREATE TABLE IF NOT EXISTS payments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    amount REAL,
                    currency TEXT,
                    screenshot_id INTEGER,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            await db.commit()

    # === ПОЛЬЗОВАТЕЛИ ===
    async def add_user(self, user_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
            await db.commit()

    async def get_balance(self, user_id: int) -> float:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,)) as cursor:
                result = await cursor.fetchone()
                return result[0] if result else 0.0

    async def update_balance(self, user_id: int, amount: float):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, user_id))
            await db.commit()

    async def get_user_language(self, user_id: int) -> str:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT language FROM users WHERE user_id = ?", (user_id,)) as cursor:
                result = await cursor.fetchone()
                return result[0] if result else 'ru'

    async def set_user_language(self, user_id: int, language: str):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("UPDATE users SET language = ? WHERE user_id = ?", (language, user_id))
            await db.commit()

    # === NFT ===
    async def add_nft_gift(self, name: str, min_price: float, max_price: float, quantity: int) -> int:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "INSERT INTO nft_gifts (name, min_price, max_price, total_quantity) VALUES (?, ?, ?, ?)",
                (name, min_price, max_price, quantity)
            )
            await db.commit()
            return cursor.lastrowid

    async def generate_nft_instances(self, gift_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT * FROM nft_gifts WHERE id = ?", (gift_id,)) as cursor:
                gift = await cursor.fetchone()
                if not gift:
                    return

                _, name, min_price, max_price, total_qty, sold_qty = gift
                available = total_qty - sold_qty

                for _ in range(available):
                    price = round(random.uniform(min_price, max_price), 2)
                    background = random.choice(config.BACKGROUNDS)
                    await db.execute(
                        "INSERT INTO nft_instances (gift_id, price, background) VALUES (?, ?, ?)",
                        (gift_id, price, background)
                    )
                await db.commit()

    async def get_all_nft_gifts(self) -> List[Dict]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM nft_gifts WHERE total_quantity > sold_quantity") as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    async def get_nft_instances(self, gift_id: int) -> List[Dict]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM nft_instances WHERE gift_id = ? AND is_sold = 0",
                                  (gift_id,)) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    async def get_nft_instance(self, instance_id: int) -> Optional[Dict]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM nft_instances WHERE id = ? AND is_sold = 0", (instance_id,)) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None

    async def buy_nft(self, instance_id: int, buyer_id: int, price: float, delivery_info: str = None) -> bool:
        async with aiosqlite.connect(self.db_path) as db:
            try:
                await db.execute("BEGIN TRANSACTION")

                balance = await self.get_balance(buyer_id)
                if balance < price:
                    return False

                await db.execute("""
                    UPDATE nft_instances 
                    SET is_sold = 1, buyer_id = ?, delivery_info = ?, bought_at = CURRENT_TIMESTAMP 
                    WHERE id = ? AND is_sold = 0
                """, (buyer_id, delivery_info, instance_id))

                await db.execute("UPDATE users SET balance = balance - ? WHERE user_id = ?", (price, buyer_id))
                await db.execute("""
                    UPDATE nft_gifts SET sold_quantity = sold_quantity + 1 
                    WHERE id = (SELECT gift_id FROM nft_instances WHERE id = ?)
                """, (instance_id,))

                await db.commit()
                return True
            except:
                await db.rollback()
                return False

    # === АНОНИМНЫЕ НОМЕРА ===
    async def add_anonymous_number(self, number: str, price: float):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("INSERT INTO anonymous_numbers (number, price) VALUES (?, ?)", (number, price))
            await db.commit()

    async def get_available_numbers(self) -> List[Dict]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM anonymous_numbers WHERE is_sold = 0") as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    async def get_number(self, number_id: int) -> Optional[Dict]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM anonymous_numbers WHERE id = ? AND is_sold = 0",
                                  (number_id,)) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None

    async def buy_number(self, number_id: int, buyer_id: int, price: float, wallet_address: str = None) -> bool:
        async with aiosqlite.connect(self.db_path) as db:
            try:
                await db.execute("BEGIN TRANSACTION")

                balance = await self.get_balance(buyer_id)
                if balance < price:
                    return False

                await db.execute("""
                    UPDATE anonymous_numbers 
                    SET is_sold = 1, buyer_id = ?, wallet_address = ?, bought_at = CURRENT_TIMESTAMP 
                    WHERE id = ? AND is_sold = 0
                """, (buyer_id, wallet_address, number_id))

                await db.execute("UPDATE users SET balance = balance - ? WHERE user_id = ?", (price, buyer_id))

                await db.commit()
                return True
            except:
                await db.rollback()
                return False

    # === ЮЗЕРНЕЙМЫ ===
    async def add_username(self, username: str, price: float, category: str):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("INSERT INTO usernames (username, price, category) VALUES (?, ?, ?)",
                             (username, price, category))
            await db.commit()

    async def get_available_usernames(self, category: str = None) -> List[Dict]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            if category:
                query = "SELECT * FROM usernames WHERE is_sold = 0 AND category = ?"
                params = (category,)
            else:
                query = "SELECT * FROM usernames WHERE is_sold = 0"
                params = ()

            async with db.execute(query, params) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    async def get_username(self, username_id: int) -> Optional[Dict]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM usernames WHERE id = ? AND is_sold = 0", (username_id,)) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None

    async def buy_username(self, username_id: int, buyer_id: int, price: float, target_username: str = None) -> bool:
        async with aiosqlite.connect(self.db_path) as db:
            try:
                await db.execute("BEGIN TRANSACTION")

                balance = await self.get_balance(buyer_id)
                if balance < price:
                    return False

                await db.execute("""
                    UPDATE usernames 
                    SET is_sold = 1, buyer_id = ?, target_username = ?, bought_at = CURRENT_TIMESTAMP 
                    WHERE id = ? AND is_sold = 0
                """, (buyer_id, target_username, username_id))

                await db.execute("UPDATE users SET balance = balance - ? WHERE user_id = ?", (price, buyer_id))

                await db.commit()
                return True
            except:
                await db.rollback()
                return False

    # === ИСТОРИЯ ПОКУПОК ===
    async def get_user_purchases(self, user_id: int, limit: int = 20) -> List[Dict]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            purchases = []

            # NFT покупки
            async with db.execute("""
                SELECT 
                    n.id,
                    n.price,
                    n.background,
                    n.bought_at,
                    n.delivery_info,
                    g.name as item_name,
                    'nft' as type
                FROM nft_instances n
                JOIN nft_gifts g ON n.gift_id = g.id
                WHERE n.buyer_id = ? AND n.is_sold = 1
                ORDER BY n.bought_at DESC
                LIMIT ?
            """, (user_id, limit)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    purchases.append(dict(row))

            # Юзернеймы
            async with db.execute("""
                SELECT 
                    id,
                    username as item_name,
                    price,
                    bought_at,
                    target_username as delivery_info,
                    'username' as type
                FROM usernames
                WHERE buyer_id = ? AND is_sold = 1
                ORDER BY bought_at DESC
                LIMIT ?
            """, (user_id, limit - len(purchases))) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    purchases.append(dict(row))

            # Анонимные номера
            async with db.execute("""
                SELECT 
                    id,
                    number as item_name,
                    price,
                    bought_at,
                    wallet_address as delivery_info,
                    'number' as type
                FROM anonymous_numbers
                WHERE buyer_id = ? AND is_sold = 1
                ORDER BY bought_at DESC
                LIMIT ?
            """, (user_id, limit - len(purchases))) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    purchases.append(dict(row))

            purchases.sort(key=lambda x: x['bought_at'], reverse=True)
            return purchases[:limit]

    # === ПЛАТЕЖИ ===
    async def add_payment(self, user_id: int, amount: float, currency: str, screenshot_id: int) -> int:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "INSERT INTO payments (user_id, amount, currency, screenshot_id) VALUES (?, ?, ?, ?)",
                (user_id, amount, currency, screenshot_id)
            )
            await db.commit()
            return cursor.lastrowid

    async def get_payment(self, payment_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM payments WHERE id = ?", (payment_id,)) as cursor:
                return await cursor.fetchone()

    async def confirm_payment(self, payment_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("UPDATE payments SET status = 'confirmed' WHERE id = ?", (payment_id,))
            await db.commit()

    async def reject_payment(self, payment_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("UPDATE payments SET status = 'rejected' WHERE id = ?", (payment_id,))
            await db.commit()