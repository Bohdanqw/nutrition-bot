import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import json
import httpx

# ================== ТОКЕН БОТА ==================
BOT_TOKEN = "8867065336:AAFI6Kf2pV0SbtR0gl933x-CgA0b4dz8Vtw"

# ================== GEMINI API КЛЮЧ ==================
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

# ================== AI АНАЛІЗ (Gemini) ==================

async def analyze_food(text: str):
    """Аналізує харчування через Gemini AI"""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{
            "parts": [{
                "text": f"Ти нутриціолог. Проаналізуй текст і поверни ТІЛЬКИ JSON (без markdown, без ```): {{\"protein\": число, \"fat\": число, \"carbs\": число, \"calories\": число, \"comment\": \"короткий коментар українською\"}}\n\nТекст: {text}"
            }]
        }]
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, json=data, timeout=30)
            result = response.json()
            content = result["candidates"][0]["content"]["parts"][0]["text"]
            # Очищаємо від markdown якщо є
            content = content.replace("```json", "").replace("```", "").strip()
            return json.loads(content)
        except Exception as e:
            return {"error": str(e)}

# ================== КОМАНДИ ==================

@dp.message(Command("start"))
async def start(message: types.Message):
    if message.from_user.id not in whitelist:
        await message.answer("❌ У вас немає доступу.")
        return
    await message.answer("👋 Привіт! Я Мій Харчобот.\n\nПросто пиши, що з'їв (наприклад: 2 яйця, 150г курки, рис)")

@dp.message(Command("add"))
async def add_user(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        user_id = int(message.text.split()[1])
        whitelist.add(user_id)
        save_whitelist()
        await message.answer(f"✅ Додано користувача {user_id}")
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
    await message.answer(f"👥 Всього користувачів: {len(whitelist)}\n{list(whitelist)}")

@dp.message()
async def handle_food(message: types.Message):
    if message.from_user.id not in whitelist:
        await message.answer("❌ У вас немає доступу.")
        return
    
    thinking = await message.answer("🤔 Аналізую через AI...")
    
    result = await analyze_food(message.text)
    
    await thinking.delete()
    
    if "error" in result:
        await message.answer(f"❌ Помилка: {result['error']}")
        return
    
    text = f"✅ **Аналіз харчування:**\n\n"
    text += f"🥚 **Білки:** {result.get('protein', 0)} г\n"
    text += f"🥑 **Жири:** {result.get('fat', 0)} г\n"
    text += f"🍚 **Вуглеводи:** {result.get('carbs', 0)} г\n"
    text += f"🔥 **Калорії:** {result.get('calories', 0)} ккал\n\n"
    
    if result.get('comment'):
        text += f"💬 {result['comment']}"
    
    await message.answer(text, parse_mode="Markdown")

async def main():
    print("🤖 Мій Харчобот з AI (Gemini) запущений!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
