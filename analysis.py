import asyncio
import aiosqlite
import json
from datetime import datetime, timedelta
import random
from typing import Dict, List, Optional

DB_PATH = "trainer_data.db"

# ==================== БАЗА ДАНИХ ====================
async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS clients (
                user_id INTEGER PRIMARY KEY,
                name TEXT,
                age INTEGER,
                gender TEXT,
                weight REAL,
                height REAL,
                activity_level REAL,
                goal TEXT,
                connected_apps TEXT DEFAULT '[]'
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS daily_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                date TEXT,
                calories REAL,
                protein REAL,
                carbs REAL,
                fat REAL,
                steps INTEGER,
                source_app TEXT
            )
        """)
        await db.commit()

# ==================== РОЗРАХУНКИ ====================
def calculate_macros(age: int, weight: float, height: float, gender: str, 
                     activity: float, goal: str) -> Dict:
    if gender == "male":
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
    
    tdee = bmr * activity
    
    if goal == "lose":
        calories = tdee * 0.8
        protein = weight * 2.4
    elif goal == "gain":
        calories = tdee * 1.15
        protein = weight * 2.0
    else:
        calories = tdee
        protein = weight * 2.0
    
    fat = weight * 0.9
    carbs = (calories - (protein * 4 + fat * 9)) / 4
    
    return {
        "calories": round(calories),
        "protein": round(protein, 1),
        "carbs": round(carbs, 1),
        "fat": round(fat, 1)
    }

def recommend_products(macros: Dict, current_protein: float = 0) -> List[Dict]:
    products = []
    deficit = macros["protein"] - current_protein
    
    if deficit > 20:
        products.append({
            "name": "Протеїн Whey 1 кг",
            "daily": f"{round(deficit * 0.6)} г",
            "monthly": f"{round(deficit * 0.6 * 30 / 1000, 1)} кг",
            "reason": "Дефіцит протеїну"
        })
    
    if macros["calories"] > 2600:
        products.append({
            "name": "Креатин 300 г",
            "daily": "5 г",
            "monthly": "150 г",
            "reason": "Для сили та маси"
        })
    
    return products

# ==================== АНАЛІЗ З ДОДАТКІВ ====================
async def analyze_client_data(user_id: int, app_name: str = "MyFitnessPal") -> Dict:
    # Тут буде логіка аналізу (поки спрощена)
    return {
        "app": app_name,
        "avg_protein": 95,
        "recommendation": "Потрібно додати протеїн",
        "products": recommend_products({"protein": 160, "calories": 2800}, 95)
    }

# ==================== ТЕСТ ====================
if __name__ == "__main__":
    print("✅ Файл analysis.py готовий!")
    print("Тепер можеш імпортувати його в свій bot.py")
