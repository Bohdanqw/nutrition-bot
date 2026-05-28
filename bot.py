import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import json
import httpx
from datetime import datetime, date

BOT_TOKEN = "8867065336:AAFI6Kf2pV0SbtR0gl933x-CgA0b4dz8Vtw"
GEMINI_API_KEY = "твій_gemini_ключ_сюди"  # ←←← ВСТАВ КЛЮЧ!

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

ADMIN_ID = 488630121
WHITELIST_FILE = "whitelist.json"
HISTORY_FILE = "history.json"
NORM_FILE = "norm.json"

# Завантаження whitelist
try:
    with open(WHITELIST_FILE, "r", encoding="utf-8") as f:
        whitelist = set(json.load(f))
except:
    whitelist = {ADMIN_ID}

def save_whitelist():
    with open(WHITELIST_FILE, "w", encoding="utf-8") as f:
        json.dump(list(whitelist), f)

# ================== ІСТОРІЯ ==================

def load_history():
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def add_to_history(user_id: int, text: str, analysis: dict):
    history = load_history()
    today = str(date.today())
    
    if today not in history:
        history[today] = {}
    
    if str(user_id) not in history[today]:
        history[today][str(user_id)] = []
    
    history[today][str(user_id)].append({
        "time": datetime.now().strftime("%H:%M"),
        "text": text,
        "analysis": analysis
    })
    
    save_history(history)

def get_today_stats(user_id: int):
    history = load_history()
    today = str(date.today())
    
    if today not in history or str(user_id) not in history[today]:
        return None
    
    entries = history[today][str(user_id)]
    
    total_protein = sum(e["analysis"].get("protein", 0) for e in entries)
    total_fat = sum(e["analysis"].get("fat", 0) for e in entries)
    total_carbs = sum(e["analysis"].get("carbs", 0) for e in entries)
    total_calories = sum(e["analysis"].get("calories", 0) for e in entries)
    
    return {
        "protein": round(total_protein, 1),
        "fat": round(total_fat, 1),
        "carbs": round(total_carbs, 1),
        "calories": round(total_calories)
    }

# ================== ДЕННА НОРМА ==================

def load_norm():
    try:
        with open(NORM_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_norm(norm):
    with open(NORM_FILE, "w", encoding="utf-8") as f:
        json.dump(norm, f)

def get_user_norm(user_id: int):
    norm = load_norm()
    return norm.get(str(user_id), 2000)  # За замовчуванням 2000
