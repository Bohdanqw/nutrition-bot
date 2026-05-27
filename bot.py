import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN, timeout=30)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "👋 Привіт! Я бот для підрахунку харчування.\n\n"
        "Просто напиши, що ти з'їв.\n"
        "Приклад: 3 яйця, 200г курки, 150г рису"
    )

@dp.message()
async def echo(message: types.Message):
    await message.answer(f"✅ Записано:\n{message.text}")

async def main():
    print("🤖 Бот запущений... Спроба підключення до Telegram")
    await dp.start_polling(bot, polling_timeout=60)

if __name__ == "__main__":
    asyncio.run(main())