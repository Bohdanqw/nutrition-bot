import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import json
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

ADMIN_ID = 488630121
WHITELIST_FILE = "whitelist.json"

# Завантаження whitelist
try:
    with open(WHITELIST_FILE, "r", encoding="utf-8") as f:
        whitelist = set(json.load(f))
except:
    whitelist = {ADMIN_ID}

def save_whitelist():
    with open(WHITELIST_FILE, "w", encoding="utf-8") as f:
        json.dump(list(whitelist), f)

@dp.message(Command("start"))
async def start(message: types.Message):
    if message.from_user.id not in whitelist:
        await message.answer("❌ У вас немає доступу.")
        return
    await message.answer("👋 Привіт! Я Мій Харчобот.\n\nПросто пиши, що з'їв.")

@dp.message(Command("add"))
async def add_user(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        user_id = int(message.text.split()[1])
        whitelist.add(user_id)
        save_whitelist()
        await message.answer(f"✅ Додано {user_id}")
    except:
        await message.answer("Використання: /add 123456789")

@dp.message(Command("remove"))
async def remove_user(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        user_id = int(message.text.split()[1])
        if user_id != ADMIN_ID:
            whitelist.discard(user_id)
            save_whitelist()
            await message.answer(f"❌ Видалено {user_id}")
    except:
        await message.answer("Використання: /remove 123456789")

@dp.message(Command("users"))
async def list_users(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    await message.answer(f"👥 Всього: {len(whitelist)}\n{list(whitelist)}")

@dp.message()
async def handle_food(message: types.Message):
    if message.from_user.id not in whitelist:
        await message.answer("❌ Немає доступу.")
        return
    await message.answer(f"✅ Записано:\n{message.text}")

async def main():
    print("🤖 Мій Харчобот запущений!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
