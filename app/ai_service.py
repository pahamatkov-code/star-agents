# -*- coding: utf-8 -*-
import anthropic
import os
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

ECOMMERCE_BASE_PROMPT = """
Ти — AI-агент підтримки клієнтів інтернет-магазину.
Спілкуйся ТІЛЬКИ українською мовою.
Будь ввічливим, корисним і конкретним.
Відповідай коротко — максимум 3-4 речення.

Загальна інформація:
- Доставка: Нова Пошта (2-3 дні), Укрпошта (3-5 днів)
- Повернення: протягом 14 днів після отримання
- Оплата: картка онлайн, накладений платіж
- Робочі години підтримки: 9:00-18:00
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

    messages = history or []
    messages.append({"role": "user", "content": message})

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=500,
        system=system_prompt,
        messages=messages
    )

    return response.content[0].text