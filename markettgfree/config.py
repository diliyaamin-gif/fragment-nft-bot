import os
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class Config:
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "8652446124:AAHWEQM5pNlyTbvMIM-eveF70znaBWDeXcM")
    ADMIN_ID: int = int(os.getenv("ADMIN_ID", "8607082207"))

    ITEMS_PER_PAGE: int = 6
    MIN_DEPOSIT_AMOUNT: float = 45.0
    MAX_DEPOSIT_AMOUNT: float = 20000.0

    # Криптокошельки
    WALLETS: Dict[str, str] = field(default_factory=lambda: {
            "TON": "UQBBd3G68MQe3f4cGkInTq0ZiiTcGWPVXhHQdBu-CKbh4ka0",
            "BTC": "bc1qstqqvf6vj4437yhrfx5felk8qnvepkn4ghakw4",
            "ETH": "0x79668a9Ba8f001D5ec5Ce173c7D490B75cFa24f5",
            "SOL": "6bb1QRvBaxQhqgqM76qTLgm6Wqvsif4PnnoSS31KXPYr",
            "TRX": "TKu4DpBxYSi4W4sUgTtjtUvVm3vxjrXGKR",
            "BNB": "0xC3B96101bD6533dC3242472B7C5Eb453fBCA9766"
        })

    # USDT кошельки по сетям
    USDT_WALLETS: Dict[str, str] = field(default_factory=lambda: {
            "TRC20": "TKu4DpBxYSi4W4sUgTtjtUvVm3vxjrXGKR",
            "ERC20": "0x79668a9Ba8f001D5ec5Ce173c7D490B75cFa24f5",
            "BEP20": "0xC3B96101bD6533dC3242472B7C5Eb453fBCA9766",
            "SOL": "6bb1QRvBaxQhqgqM76qTLgm6Wqvsif4PnnoSS31KXPYr",
            "TON": "UQBBd3G68MQe3f4cGkInTq0ZiiTcGWPVXhHQdBu-CKbh4ka0"
        })

    # Реальные фоны из Telegram Fragment
    BACKGROUNDS: List[str] = field(default_factory=lambda: [
            "Black", "Onyx Black", "Gunmetal", "Mustard", "Fire Engine",
            "Carmine", "Midnight Blue", "Mexican Pink", "Platinum", "Sapphire",
            "Purple", "Electric Indigo", "Neon Blue", "Jade Green", "Aquamarine",
            "Desert Sand", "Chestnut", "Grape", "Dark Lilac", "Moonstone",
            "Roman Silver", "Hunter Green", "Persimmon", "Satin Gold", "Fandango",
            "Pacific Cyan", "Pistachio", "Amber", "Ivory White", "Seal Brown",
            "Tomato", "Cobalt Blue", "Lemongrass", "Malachite", "Mint Green",
            "Raspberry", "Marine Blue", "Light Olive", "Electric Purple"
        ])

    # Реальные NFT подарки Telegram (названия и цены)
    NFT_GIFTS: Dict[str, Dict] = field(default_factory=lambda: {
            # Очень редкие (10-20 шт)
            "Heart Locket": {"min_price": 750, "max_price": 1500, "quantity": 15},
            "Plush Pepe": {"min_price": 500, "max_price": 1000, "quantity": 18},
            "Heroic Helmet": {"min_price": 400, "max_price": 800, "quantity": 20},
            "Mighty Arm": {"min_price": 350, "max_price": 700, "quantity": 22},
            "Ion Gem": {"min_price": 300, "max_price": 600, "quantity": 25},
            "Durov's Cap": {"min_price": 250, "max_price": 500, "quantity": 28},
            "Nail Bracelet": {"min_price": 200, "max_price": 400, "quantity": 30},
            "Perfume Bottle": {"min_price": 180, "max_price": 350, "quantity": 32},
            "Magic Potion": {"min_price": 150, "max_price": 300, "quantity": 35},
            "Mini Oscar": {"min_price": 120, "max_price": 250, "quantity": 38},

            # Редкие (40-60 шт)
            "Astral Shard": {"min_price": 100, "max_price": 200, "quantity": 40},
            "Artisan Brick": {"min_price": 90, "max_price": 180, "quantity": 42},
            "Gem Signet": {"min_price": 80, "max_price": 160, "quantity": 45},
            "Sharp Tongue": {"min_price": 70, "max_price": 140, "quantity": 48},
            "Bonded Ring": {"min_price": 60, "max_price": 120, "quantity": 50},
            "Electric Skull": {"min_price": 55, "max_price": 110, "quantity": 52},
            "Loot Bag": {"min_price": 50, "max_price": 100, "quantity": 55},
            "Kissed Frog": {"min_price": 45, "max_price": 90, "quantity": 58},

            # Средние (60-100 шт)
            "Neko Helmet": {"min_price": 40, "max_price": 80, "quantity": 60},
            "Signet Ring": {"min_price": 35, "max_price": 70, "quantity": 65},
            "Scared Cat": {"min_price": 30, "max_price": 60, "quantity": 70},
            "Skull Flower": {"min_price": 28, "max_price": 55, "quantity": 75},
            "Flying Broom": {"min_price": 25, "max_price": 50, "quantity": 80},
            "Trapped Heart": {"min_price": 22, "max_price": 45, "quantity": 85},
            "Crystal Ball": {"min_price": 20, "max_price": 40, "quantity": 90},
            "Voodoo Doll": {"min_price": 18, "max_price": 35, "quantity": 95},

            # Обычные (100-150 шт)
            "Love Candle": {"min_price": 15, "max_price": 30, "quantity": 100},
            "Love Potion": {"min_price": 14, "max_price": 28, "quantity": 105},
            "Diamond Ring": {"min_price": 13, "max_price": 26, "quantity": 110},
            "Cupid Charm": {"min_price": 12, "max_price": 24, "quantity": 115},
            "Top Hat": {"min_price": 11, "max_price": 22, "quantity": 120},
            "Record Player": {"min_price": 10, "max_price": 20, "quantity": 125},
            "Eternal Candle": {"min_price": 9, "max_price": 18, "quantity": 130},
            "Hanging Star": {"min_price": 8, "max_price": 16, "quantity": 135},

            # Много (150-250 шт)
            "Sakura Flower": {"min_price": 7, "max_price": 14, "quantity": 140},
            "Jelly Bunny": {"min_price": 6.5, "max_price": 13, "quantity": 145},
            "Spy Agaric": {"min_price": 6, "max_price": 12, "quantity": 150},
            "Snow Globe": {"min_price": 5.5, "max_price": 11, "quantity": 155},
            "Ginger Cookie": {"min_price": 5, "max_price": 10, "quantity": 160},
            "Hex Pot": {"min_price": 4.5, "max_price": 9, "quantity": 165},
            "Berry Box": {"min_price": 4, "max_price": 8, "quantity": 170},
            "Tama Gadget": {"min_price": 3.5, "max_price": 7, "quantity": 175},
            "Moon Pendant": {"min_price": 3, "max_price": 6, "quantity": 180},
            "Lunar Snake": {"min_price": 2.8, "max_price": 5.6, "quantity": 185},
            "Holiday Drink": {"min_price": 2.6, "max_price": 5.2, "quantity": 190},
            "Joyful Bundle": {"min_price": 2.4, "max_price": 4.8, "quantity": 195},
            "Restless Jar": {"min_price": 2.2, "max_price": 4.4, "quantity": 200},
            "Big Year": {"min_price": 2, "max_price": 4, "quantity": 210},
            "Light Sword": {"min_price": 2, "max_price": 4, "quantity": 220},
            "Jingle Bells": {"min_price": 2, "max_price": 4, "quantity": 230},
            "Easter Egg": {"min_price": 2, "max_price": 4, "quantity": 240},
            "Candy Cane": {"min_price": 2, "max_price": 4, "quantity": 250},
            "Lush Bouquet": {"min_price": 2, "max_price": 4, "quantity": 250},
            "Spiced Wine": {"min_price": 2, "max_price": 4, "quantity": 250},
            "Evil Eye": {"min_price": 2, "max_price": 4, "quantity": 250},
            "Ionic Dryer": {"min_price": 2, "max_price": 4, "quantity": 250},
            "Stellar Rocket": {"min_price": 2, "max_price": 4, "quantity": 250},
            "Snake Box": {"min_price": 2, "max_price": 4, "quantity": 250},
            "Jack-in-the-Box": {"min_price": 2, "max_price": 4, "quantity": 250},
            "Witch Hat": {"min_price": 2, "max_price": 4, "quantity": 250},
            "Pet Snake": {"min_price": 2, "max_price": 4, "quantity": 250},
            "Jester Hat": {"min_price": 2, "max_price": 4, "quantity": 250},
            "Party Sparkler": {"min_price": 2, "max_price": 4, "quantity": 250},
            "Star Notepad": {"min_price": 2, "max_price": 4, "quantity": 250},
            "Snow Mittens": {"min_price": 2, "max_price": 4, "quantity": 250}
        })

     # Анонимные номера
    ANONYMOUS_NUMBERS: List[Dict] = field(default_factory=lambda: [
            {"number": "+888 1045 1626", "min_price": 950, "max_price": 1250},
            {"number": "+888 1957 2852", "min_price": 950, "max_price": 1250},
            {"number": "+888 1285 1952", "min_price": 950, "max_price": 1250},
            {"number": "+888 9285 6825", "min_price": 950, "max_price": 1250},
            {"number": "+888 4573 3760", "min_price": 950, "max_price": 1250},
            {"number": "+888 1963 0836", "min_price": 950, "max_price": 1250},
            {"number": "+888 2962 2i62", "min_price": 950, "max_price": 1250},
            {"number": "+888 7334 2863", "min_price": 950, "max_price": 1250},
            {"number": "+888 2863 3862", "min_price": 950, "max_price": 1250},
            {"number": "+888 9832 5612", "min_price": 950, "max_price": 1250}
        ])

    # Юзернеймы
    USERNAMES: Dict[str, List[Dict]] = field(default_factory=lambda: {
            "4_letter": [
                {"username": "@vibe", "price": 550},
                {"username": "@drop", "price": 250},
                {"username": "@meta", "price": 300},
                {"username": "@moon", "price": 240},
                {"username": "@surf", "price": 920}
            ],
            "5_letter": [
                {"username": "@trade", "price": 210},
                {"username": "@coins", "price": 120},
                {"username": "@owner", "price": 120},
                {"username": "@crypt", "price": 150},
                {"username": "@alpha", "price": 150},
                {"username": "@power", "price": 145},
                {"username": "@money", "price": 175},
                {"username": "@block", "price": 180},
                {"username": "@chain", "price": 230},
                {"username": "@token", "price": 350}
            ],
            "long": [
                {"username": "@my_shop_nft", "min_price": 2, "max_price": 6},
                {"username": "@buy_and_sell_ton", "min_price": 2, "max_price": 6},
                {"username": "@crypto_wallet_ton", "min_price": 2, "max_price": 6},
                {"username": "@nft_gifts_shop", "min_price": 2, "max_price": 6},
                {"username": "@telegram_nft", "min_price": 2, "max_price": 6}
            ]
        })

config = Config()