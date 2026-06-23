# -*- coding: utf-8 -*-
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import httpx
import os
import asyncio

from app.services.ai_service import ask_agent

router = APIRouter()

# Telegram API
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

# Стан користувачів
user_states = {}

STATE_AWAITING_ORDER_NUMBER = "awaiting_order_number"


# ---------------------- Intent Detection ----------------------

def detect_intent(text: str):
    t = text.lower()

    if any(x in t for x in ["скільки", "ціна", "коштує"]):
        return "payment"

    if "де" in t and "замов" in t:
        return "order_status"

    if "достав" in t:
        return "delivery"

    if "поверн" in t:
        return "returns"

    if "гарант" in t:
        return "warranty"

    if "менедж" in t:
        return "manager"

    return None


# ---------------------- Відправка повідомлень ----------------------

async def send_message(chat_id: int, text: str, reply_markup=None):
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"   # HTML безпечніший за Markdown
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup

    url = f"{TELEGRAM_API_URL}/sendMessage"

    # Логування
    print(">>> SENDING TO:", url)
    print(">>> PAYLOAD:", payload)

    async with httpx.AsyncClient(timeout=10) as client_http:
        response = await client_http.post(url, json=payload)

        # Логування відповіді Telegram
        print(">>> TELEGRAM RESPONSE:", response.status_code, response.text)

        return response


# ---------------------- Головне меню ----------------------

def main_menu():
    return {
        "inline_keyboard": [
            [
                {"text": "📦 Статус замовлення", "callback_data": "order_status"},
                {"text": "💳 Оплата", "callback_data": "payment"},
            ],
            [
                {"text": "🚚 Доставка", "callback_data": "delivery"},
                {"text": "🔄 Повернення", "callback_data": "returns"},
            ],
            [
                {"text": "🛠️ Гарантія", "callback_data": "warranty"},
                {"text": "👩‍💼 Менеджер", "callback_data": "manager"},
            ],
        ]
    }


# ---------------------- Обробка callback-кнопок ----------------------

async def handle_callback(callback, chat_id, user_id):
    data = callback["data"]

    if data == "order_status":
        user_states[user_id] = STATE_AWAITING_ORDER_NUMBER
        await send_message(chat_id, "Вкажіть, будь ласка, номер вашого замовлення:")
        return

    responses = {
        "payment": "💳 <b>Оплата</b>\nДоступні способи: картка, Google Pay, Apple Pay.",
        "delivery": "🚚 <b>Доставка</b>\nНадсилаємо Новою Поштою по всій Україні.",
        "returns": "🔄 <b>Повернення</b>\nПовернення можливе протягом 14 днів.",
        "warranty": "🛠️ <b>Гарантія</b>\nГарантія 12 місяців на всі товари.",
        "manager": "👩‍💼 <b>Менеджер</b>\nОчікуйте, будь ласка. Менеджер скоро відповість."
    }

    if data in responses:
        await send_message(chat_id, responses[data], main_menu())
        return


# ---------------------- Обробка текстових повідомлень ----------------------

async def handle_text_message(text, chat_id, user_id):
    state = user_states.get(user_id)

    # Очікуємо номер замовлення
    if state == STATE_AWAITING_ORDER_NUMBER:
        order_number = text.strip()
        track_suffix = order_number[-4:] if len(order_number) >= 4 else order_number

        reply = (
            f"<b>Статус замовлення</b>\n"
            f"Ваше замовлення №<b>{order_number}</b> відправлено Новою Поштою.\n"
            f"Трек-номер: <code>204509{track_suffix}</code>\n"
            f"Перевірити: https://track.novaposhta.ua/"
        )

        user_states[user_id] = None
        await send_message(chat_id, reply, main_menu())
        return

    # Намір → кнопка
    intent = detect_intent(text)
    if intent:
        await handle_callback({"data": intent}, chat_id, user_id)
        return

    # AI-відповідь
    loop = asyncio.get_event_loop()
    ai_answer = await loop.run_in_executor(
        None,
        lambda: ask_agent(
            message=text,
            agent_name="StarAgent"
        )
    )

    print(">>> AI ANSWER:", ai_answer)

    await send_message(chat_id, ai_answer, main_menu())


# ---------------------- Webhook ----------------------

@router.post("/chat/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()

    # Callback-кнопки
    if "callback_query" in data:
        callback = data["callback_query"]
        chat_id = callback["message"]["chat"]["id"]
        user_id = callback["from"]["id"]

        await handle_callback(callback, chat_id, user_id)
        return JSONResponse({"ok": True})

    # Текстові повідомлення
    if "message" in data:
        message = data["message"]
        chat_id = message["chat"]["id"]
        user_id = message["from"]["id"]
        text = message.get("text", "")

        await handle_text_message(text, chat_id, user_id)
        return JSONResponse({"ok": True})

    return JSONResponse({"ok": True})
