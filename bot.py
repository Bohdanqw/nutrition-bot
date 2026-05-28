import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import json
import httpx
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = "AIzaSyBhV82mPHjcLVw34N-nFrWEJmLHsnKdDYM"
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

# ================== AI АНАЛІЗ ==================

async def analyze_food(text: str):
    if not GEMINI_API_KEY or GEMINI_API_KEY == "твій_gemini_ключ_сюди":
        return {"protein": 0, "fat": 0, "carbs": 0, "calories": 0, "comment": "AI не налаштовано (встав ключ)"}
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{
            "parts": [{
                "text": f"Ти нутриціолог. Проаналізуй текст і поверни ТІЛЬКИ JSON: {{\"protein\": число, \"fat\": число, \"carbs\": число, \"calories\": число, \"comment\": \"короткий коментар українською\"}}\n\nТекст: {text}"
            }]
        }]
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, json=data, timeout=30)
            result = response.json()
            content = result["candidates"][0]["content"]["parts"][0]["text"]
            content = content.replace("```json", "").replace("```", "").strip()
            return json.loads(content)
        except:
            return {"protein": 0, "fat": 0, "carbs": 0, "calories": 0, "comment": "Помилка AI"}

@dp.message(Command("start"))
async def start(message: types.Message):
    if message.from_user.id not in whitelist:
        await message.answer("❌ У вас немає доступу.")
        return
    await message.answer("👋 Привіт! Я Мій Харчобот.\n\nПросто пиши, що з'їв (наприклад: 2 яйця, 150г курки)")

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
    
    thinking = await message.answer("🤔 Аналізую...")
    
    analysis = await analyze_food(message.text)
    
    await thinking.delete()
    
    text = f"✅ **Аналіз:** {message.text}\n\n"
    text += f"🥚 Білки: {analysis.get('protein', 0)} г\n"
    text += f"🥑 Жири: {analysis.get('fat', 0)} г\n"
    text += f"🍚 Вуглеводи: {analysis.get('carbs', 0)} г\n"
    text += f"🔥 Калорії: {analysis.get('calories', 0)} ккал"
    
    if analysis.get('comment'):
        text += f"\n\n💬 {analysis['comment']}"
    
    await message.answer(text, parse_mode="Markdown")

async def main():
    print("🤖 Мій Харчобот з AI запущений!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
