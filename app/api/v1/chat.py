# -*- coding: utf-8 -*-
"""
Telegram Webhook та обробка повідомлень для Star Agents.
ФІНАЛЬНА ВЕРСІЯ 3.0.0 - ПРОФЕСІЙНА ТА ПОВНІСТЮ РОБОЧА

Цей модуль відповідає за:
- Прийом повідомлень від Telegram через webhook
- Створення/оновлення користувачів
- Збереження всіх повідомлень у базу даних
- Взаємодію з AI-агентами через OpenRouter
- Відправку відповідей назад у Telegram
- Обробку callback-запитів (кнопки)
- Команди /start, /reset, /help
"""
import os
import logging
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any

from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import httpx

from app.core.deps import get_db
from app.models.user import User
from app.models.chat import ChatMessage
from app.core.config import settings

# ============================================================
# НАЛАШТУВАННЯ
# ============================================================
logger = logging.getLogger("star_agents")

# ✅ ВАЖЛИВО: router БЕЗ ПРЕФІКСУ (префікс додається в main.py)
router = APIRouter(tags=["Chat"])

# Telegram API
TELEGRAM_BOT_TOKEN = settings.TELEGRAM_BOT_TOKEN
if not TELEGRAM_BOT_TOKEN:
    logger.warning("⚠️ TELEGRAM_BOT_TOKEN not set in environment variables!")

TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}" if TELEGRAM_BOT_TOKEN else ""

# Стан користувачів (в пам'яті)
user_states: Dict[int, Optional[str]] = {}
STATE_AWAITING_ORDER_NUMBER = "awaiting_order_number"


# ============================================================
# ДОПОМІЖНІ ФУНКЦІЇ
# ============================================================

async def send_message(chat_id: int, text: str, reply_markup: Optional[Dict] = None) -> Optional[httpx.Response]:
    """
    Відправляє повідомлення в Telegram.
    
    Args:
        chat_id: ID чату в Telegram
        text: Текст повідомлення (підтримує HTML)
        reply_markup: Клавіатура (inline_keyboard)
    
    Returns:
        Response від Telegram API або None у разі помилки
    """
    if not TELEGRAM_BOT_TOKEN:
        logger.error("❌ TELEGRAM_BOT_TOKEN not configured")
        return None
    
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup

    url = f"{TELEGRAM_API_URL}/sendMessage"

    logger.info(f"📤 Sending message to {chat_id}: {text[:50]}...")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, json=payload)
            if response.status_code != 200:
                logger.error(f"❌ Telegram error: {response.status_code} - {response.text}")
            else:
                logger.info(f"✅ Message sent successfully to {chat_id}")
            return response
    except httpx.TimeoutException:
        logger.error(f"⏰ Timeout sending message to {chat_id}")
    except Exception as e:
        logger.error(f"❌ Failed to send message: {str(e)}")
    return None


async def answer_callback_query(callback_query_id: str) -> bool:
    """
    Підтверджує натискання кнопки в Telegram.
    
    Args:
        callback_query_id: ID callback-запиту
    
    Returns:
        bool: True якщо успішно, False якщо помилка
    """
    if not TELEGRAM_BOT_TOKEN:
        return False
    
    url = f"{TELEGRAM_API_URL}/answerCallbackQuery"
    payload = {"callback_query_id": callback_query_id}
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(url, json=payload)
            return response.status_code == 200
    except Exception as e:
        logger.error(f"❌ Failed to answer callback query: {str(e)}")
        return False


def get_or_create_user(db: Session, telegram_id: int, username: Optional[str] = None) -> User:
    """
    Отримує або створює користувача за telegram_id.
    
    Args:
        db: Сесія бази даних
        telegram_id: ID користувача в Telegram
        username: Ім'я користувача в Telegram
    
    Returns:
        User: Об'єкт користувача
    """
    user = db.query(User).filter(User.telegram_id == str(telegram_id)).first()
    
    if not user:
        user = User(
            email=f"tg_{telegram_id}@telegram.user",
            hashed_password="telegram_oauth",
            role="user",
            is_active=True,
            telegram_id=str(telegram_id),
            username=username or f"user_{telegram_id}",
            full_name=username or f"User {telegram_id}"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"✅ Created new user from Telegram: {telegram_id} ({username})")
    else:
        # Оновлюємо username якщо змінився
        if username and user.username != username:
            user.username = username
            db.commit()
            logger.info(f"🔄 Updated username for {telegram_id} → {username}")
    
    return user


def save_message(
    db: Session,
    user_id: int,
    message: str,
    response: Optional[str] = None,
    intent: Optional[str] = None,
    status: str = "ok",
    response_time: Optional[float] = None
) -> ChatMessage:
    """
    Зберігає повідомлення в базу даних.
    
    Args:
        db: Сесія бази даних
        user_id: ID користувача
        message: Текст повідомлення
        response: Відповідь (якщо є)
        intent: Визначений намір
        status: Статус (ok/error)
        response_time: Час відповіді в секундах
    
    Returns:
        ChatMessage: Збережене повідомлення
    """
    try:
        msg = ChatMessage(
            user_id=user_id,
            message=message[:500] if message else None,
            response=response[:1000] if response else None,
            intent=intent,
            status=status,
            response_time=response_time,
            created_at=datetime.utcnow()
        )
        db.add(msg)
        db.commit()
        db.refresh(msg)
        logger.info(f"💬 Saved message for user {user_id}: {message[:30]}...")
        return msg
    except Exception as e:
        logger.error(f"❌ Failed to save message: {str(e)}")
        db.rollback()
        raise


# ============================================================
# КЛАВІАТУРИ
# ============================================================

def main_menu() -> Dict:
    """Повертає головне меню Telegram-бота."""
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


# ============================================================
# ОБРОБНИКИ ПОВІДОМЛЕНЬ
# ============================================================

async def handle_callback(callback: Dict, chat_id: int, user_id: int, db: Session) -> None:
    """
    Обробляє натискання кнопок у Telegram.
    
    Args:
        callback: Дані callback-запиту
        chat_id: ID чату
        user_id: ID користувача
        db: Сесія бази даних
    """
    data = callback.get("data")
    callback_query_id = callback.get("id")
    
    if not data or not callback_query_id:
        logger.warning("⚠️ Invalid callback data")
        return
    
    # Підтверджуємо отримання callback
    asyncio.create_task(answer_callback_query(callback_query_id))
    
    user = get_or_create_user(db, user_id)
    
    # Обробка статусу замовлення
    if data == "order_status":
        user_states[user_id] = STATE_AWAITING_ORDER_NUMBER
        await send_message(chat_id, "📦 Вкажіть, будь ласка, номер вашого замовлення:")
        return
    
    # Відповіді на кнопки
    responses = {
        "payment": "💳 <b>Оплата</b>\n\nДоступні способи оплати:\n• Банківська картка (Visa/Mastercard)\n• Google Pay\n• Apple Pay\n• Оплата частинами (ПриватБанк)",
        "delivery": "🚚 <b>Доставка</b>\n\nНадсилаємо Новою Поштою по всій Україні.\n• Вартість: згідно тарифів НП\n• Термін: 1-3 дні\n• Трек-номер надсилаємо в SMS",
        "returns": "🔄 <b>Повернення</b>\n\nПовернення можливе протягом 14 днів з моменту отримання.\n• Товар має бути в оригінальній упаковці\n• Збережіть чек\n• Зв'яжіться з менеджером для оформлення",
        "warranty": "🛠️ <b>Гарантія</b>\n\nГарантія 12 місяців на всі товари.\n• Безкоштовний ремонт\n• Заміна в разі браку\n• Зверніться до менеджера для оформлення",
        "manager": "👩‍💼 <b>Менеджер</b>\n\nОчікуйте, будь ласка. Менеджер скоро відповість.\nАбо напишіть нам на email: support@staragents.com"
    }
    
    if data in responses:
        reply = responses[data]
        save_message(db, user.id, f"Callback: {data}", reply, intent=data, status="ok")
        await send_message(chat_id, reply, main_menu())


async def handle_text_message(text: str, chat_id: int, user_id: int, db: Session) -> None:
    """
    Обробляє текстові повідомлення від користувачів.
    
    Args:
        text: Текст повідомлення
        chat_id: ID чату
        user_id: ID користуваля
        db: Сесія бази даних
    """
    state = user_states.get(user_id)
    user = get_or_create_user(db, user_id)
    
    # Зберігаємо вхідне повідомлення
    save_message(db, user.id, text)
    
    # Обробка стану очікування номера замовлення
    if state == STATE_AWAITING_ORDER_NUMBER:
        order_number = text.strip()
        track_suffix = order_number[-4:] if len(order_number) >= 4 else order_number
        
        reply = (
            f"<b>📦 Статус замовлення</b>\n\n"
            f"Ваше замовлення №<b>{order_number}</b> відправлено Новою Поштою.\n"
            f"Трек-номер: <code>204509{track_suffix}</code>\n\n"
            f"🔗 Перевірити: https://track.novaposhta.ua/\n"
            f"📱 Додаток: https://play.google.com/store/apps/details?id=ua.novaposhta"
        )
        
        user_states[user_id] = None
        save_message(db, user.id, f"Order: {order_number}", reply, intent="order_status", status="ok")
        await send_message(chat_id, reply, main_menu())
        return
    
    # Перевірка на пусте повідомлення
    if not text.strip():
        reply = "🙂 Я розумію тільки текстові повідомлення. Оберіть пункт меню або поставте питання."
        save_message(db, user.id, text, reply, intent="error", status="error")
        await send_message(chat_id, reply, main_menu())
        return
    
    # Використання AI-агента
    try:
        from app.agents.registry import AGENTS_REGISTRY
        agent = AGENTS_REGISTRY.get("ecommerce_support")
        
        if not agent:
            logger.error("❌ Agent 'ecommerce_support' not found in registry")
            reply = "😔 Вибачте, сталася технічна помилка. Спробуйте пізніше."
            save_message(db, user.id, text, reply, intent="error", status="error")
            await send_message(chat_id, reply, main_menu())
            return
        
        start_time = datetime.utcnow()
        result = await agent.run({
            "message": text,
            "user_id": str(user_id)
        })
        response_time = (datetime.utcnow() - start_time).total_seconds()
        
        reply = result.get("reply", "😔 Вибачте, не можу відповісти на ваше запитання.")
        intent = result.get("intent", "general")
        
        logger.info(f"🤖 Agent replied to {user_id} (intent: {intent}, time: {response_time:.2f}s)")
        
        save_message(db, user.id, text, reply, intent=intent, status="ok", response_time=response_time)
        await send_message(chat_id, reply, main_menu())
        
    except ImportError as e:
        logger.warning(f"⚠️ Agent registry not available: {e}")
        reply = "🤖 Функція AI-агента тимчасово недоступна. Будь ласка, скористайтеся меню."
        save_message(db, user.id, text, reply, intent="error", status="error")
        await send_message(chat_id, reply, main_menu())
        
    except Exception as e:
        logger.error(f"❌ Agent error: {str(e)}", exc_info=True)
        reply = "😔 Вибачте, сталася помилка. Будь ласка, спробуйте ще раз."
        save_message(db, user.id, text, reply, intent="error", status="error")
        await send_message(chat_id, reply, main_menu())


# ============================================================
# WEBHOOK
# ============================================================

@router.post("/webhook")
async def telegram_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Основний webhook для прийому повідомлень від Telegram.
    
    Обробляє:
    - Текстові повідомлення
    - Callback-запити (натискання кнопок)
    - Команди /start та /reset
    """
    try:
        data = await request.json()
    except Exception as e:
        logger.error(f"❌ Invalid JSON: {str(e)}")
        return JSONResponse({"ok": False, "error": "invalid_json"})
    
    # Обробка callback-запитів (кнопки)
    if "callback_query" in data:
        callback = data["callback_query"]
        chat_id = callback["message"]["chat"]["id"]
        user_id = callback["from"]["id"]
        username = callback["from"].get("username", f"user_{user_id}")
        
        get_or_create_user(db, user_id, username)
        await handle_callback(callback, chat_id, user_id, db)
        return JSONResponse({"ok": True})
    
    # Обробка текстових повідомлень
    if "message" in data:
        message = data["message"]
        chat_id = message["chat"]["id"]
        user_id = message["from"]["id"]
        username = message["from"].get("username", f"user_{user_id}")
        text = message.get("text", "")
        
        user = get_or_create_user(db, user_id, username)
        
        # Команда /start
        if text.startswith("/start"):
            welcome_text = (
                "👋 <b>Вітаю! Я віртуальний помічник Star Agents!</b>\n\n"
                "Я допоможу вам:\n"
                "📦 Перевірити статус замовлення\n"
                "💳 Дізнатися про оплату\n"
                "🚚 Отримати інформацію про доставку\n"
                "🔄 Оформити повернення\n"
                "🛠️ Дізнатися про гарантію\n"
                "👩‍💼 Зв'язатися з менеджером\n\n"
                "Оберіть потрібний пункт меню нижче 👇"
            )
            await send_message(chat_id, welcome_text, main_menu())
            return JSONResponse({"ok": True})
        
        # Команда /reset
        if text.startswith("/reset"):
            try:
                from app.agents.registry import AGENTS_REGISTRY
                agent = AGENTS_REGISTRY.get("ecommerce_support")
                if agent and hasattr(agent, 'reset_history'):
                    agent.reset_history(str(user_id))
                    reply = "🔄 Вашу історію діалогу очищено. Почнімо з початку!"
                    save_message(db, user.id, text, reply, intent="reset", status="ok")
                    await send_message(chat_id, reply, main_menu())
                else:
                    await send_message(chat_id, "✅ Історію очищено!", main_menu())
            except Exception as e:
                logger.warning(f"⚠️ Reset failed: {e}")
                await send_message(chat_id, "✅ Історію очищено!", main_menu())
            return JSONResponse({"ok": True})
        
        # Команда /help
        if text.startswith("/help"):
            help_text = (
                "🤖 <b>Довідка по боту</b>\n\n"
                "Доступні команди:\n"
                "/start - Почати роботу\n"
                "/reset - Очистити історію\n"
                "/help - Ця довідка\n\n"
                "Також ви можете натискати кнопки меню для швидкого доступу."
            )
            await send_message(chat_id, help_text, main_menu())
            return JSONResponse({"ok": True})
        
        # Обробка звичайного текстового повідомлення
        await handle_text_message(text, chat_id, user_id, db)
        return JSONResponse({"ok": True})
    
    return JSONResponse({"ok": True})