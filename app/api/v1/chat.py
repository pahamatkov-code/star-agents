from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/chat", tags=["chat"])

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str


# === SIMPLE IN-MEMORY DIALOG HISTORY ===
dialog_history: list[dict] = []


# === RULE-BASED LOGIC WITH HISTORY ===
def generate_reply(message: str) -> str:
    text = message.lower()

    # 1) Якщо користувач вже питав про замовлення
    if any("замовлення" in m.get("user", "").lower() for m in dialog_history):
        if "номер" in text or "ттн" in text:
            return "Дякую! Ми оновили статус. Ваше замовлення вже на відділенні."

    # 2) Де замовлення
    if any(word in text for word in [
        "де моє замовлення", "де заказ", "статус замовлення", "статус заказа"
    ]):
        return "Ваше замовлення зараз у Новій Пошті. Номер ТТН: 123."

    # 3) Повернення товару
    if any(word in text for word in [
        "повернення", "вернуть", "повернути товар", "рефанд"
    ]):
        return "Для оформлення повернення, будь ласка, вкажіть номер замовлення."

    # 4) Доставка
    if any(word in text for word in [
        "доставка", "скільки їде", "коли приїде", "когда приедет"
    ]):
        return "Доставка займає 1–2 дні по Україні. Після відправки ви отримаєте ТТН."

    # 5) Оплата
    if any(word in text for word in [
        "оплата", "як оплатити", "оплатить", "способи оплати"
    ]):
        return "Оплата доступна карткою, Google Pay, Apple Pay або післяплатою."

    # 6) Привітання
    if any(word in text for word in [
        "привіт", "добрий", "здравствуйте", "хай"
    ]):
        return "Вітаю! Чим можу допомогти?"

    # 7) За замовчуванням
    return "Дякую за звернення! Наш менеджер скоро відповість."


# === MAIN CHAT ENDPOINT ===
@router.post("/", response_model=ChatResponse)
def chat_endpoint(payload: ChatRequest):
    user_message = payload.message

    # Додаємо в історію
    dialog_history.append({"user": user_message})

    # Генеруємо відповідь
    reply = generate_reply(user_message)

    # Додаємо відповідь у історію
    dialog_history.append({"agent": reply})

    return ChatResponse(reply=reply)


# === RESET DIALOG HISTORY ===
@router.post("/reset")
def reset_dialog():
    dialog_history.clear()
    return {"status": "ok", "message": "Історію діалогу очищено."}
