from typing import Any, Dict
from app.services.ai_service import ask_agent

# Твій старий промпт — перенесений 1:1
SYSTEM_PROMPT = """
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

class EcommerceSupportAgent:
    """
    E-commerce агент з твоїм стилем, правилами і логікою.
    Працює через OpenRouter (AI Service).
    """

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        user_message = payload.get("message", "")

        # Викликаємо AI-сервіс
        reply = ask_agent(
            message=user_message,
            agent_name="E-commerce Support Agent",
            role="Підтримка інтернет-магазину",
            skills="відповіді на запитання про доставку, оплату, повернення, статус замовлення"
        )

        return {
            "agent": "ecommerce_support",
            "reply": reply
        }

def create_ecommerce_support_agent() -> EcommerceSupportAgent:
    return EcommerceSupportAgent()