from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import Optional

# Ініціалізація FastAPI
app = FastAPI(
    title="E-commerce Support Agent",
    description="Агент для автоматизації підтримки клієнтів у сфері e-commerce",
    version="1.0.0"
)

# Модель запиту від клієнта
class CustomerQuery(BaseModel):
    query: str
    customer_id: Optional[str] = None

# Головна сторінка (перевірка роботи)
@app.get("/")
def root():
    return {"message": "E-commerce Support Agent is running!"}

# Endpoint для відповіді клієнту
@app.post("/reply")
def reply_to_customer(request: CustomerQuery):
    """
    Приймає запит від клієнта та повертає відповідь.
    Поки що це базова заглушка, яку ми будемо розширювати.
    """
    # Тут пізніше буде інтеграція з Prom.ua, OLX, Telegram, НП
    response_text = f"Ваш запит: '{request.query}'. Агент відповість найближчим часом."
    return {
        "customer_id": request.customer_id,
        "response": response_text
    }

# Endpoint для перевірки статусу замовлення (заглушка)
@app.get("/order-status")
def order_status(order_id: str = Query(..., description="ID замовлення")):
    """
    Перевірка статусу замовлення.
    Поки що повертає тестову відповідь.
    """
    return {
        "order_id": order_id,
        "status": "В обробці",
        "message": "Замовлення знайдено, очікуйте оновлення статусу."
    }
