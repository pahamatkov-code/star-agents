# -*- coding: utf-8 -*-
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Завантажуємо ключ OpenRouter
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Ініціалізуємо OpenAI-клієнт для OpenRouter
client = OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1"
)

# Базовий промпт для інтернет-магазину
ECOMMERCE_BASE_PROMPT = """
Ти — AI-агент підтримки клієнтів інтернет-магазину.
Спілкуйся ТІЛЬКИ українською мовою.
Будь ввічливим, доброзичливим і професійним.
Відповідай коротко — 2–4 речення.
Не вигадуй інформацію. Якщо чогось не знаєш — уточни.

Загальна інформація:
- Доставка: Нова Пошта (2–3 дні), Укрпошта (3–5 днів)
- Повернення: протягом 14 днів після отримання
- Оплата: картка онлайн, накладений платіж
- Графік роботи підтримки: 9:00–18:00
"""

def build_system_prompt(agent_name: str, role: str = None, skills: str = None) -> str:
    prompt = f"Тебе звуть {agent_name}.\n"
    if role:
        prompt += f"Твоя роль: {role}.\n"
    if skills:
        prompt += f"Твої спеціалізації: {skills}.\n"
    prompt += ECOMMERCE_BASE_PROMPT
    return prompt


def ask_agent(
    message: str,
    agent_name: str,
    role: str = None,
    skills: str = None,
    history: list = None
) -> str:

    system_prompt = build_system_prompt(agent_name, role, skills)

    messages = [{"role": "system", "content": system_prompt}]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": message})

    try:
        response = client.chat.completions.create(
            model="qwen/qwen3.7-plus",
            extra_body={
                "models": [
                    "qwen/qwen3.7-plus",
                    "google/gemini-3.1-pro-preview"
                ],
                "route": "fallback"
            },
            messages=messages,
            max_tokens=300,
            temperature=0.4
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print("AI ERROR:", str(e))
        return (
            "Вибачте, зараз не можу відповісти. "
            "Схоже, виникла технічна затримка на сервері. "
            "Спробуйте, будь ласка, ще раз за хвилинку."
        )
