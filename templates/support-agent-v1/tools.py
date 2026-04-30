# tools.py - Smart Support UA Pro
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Optional, Dict
import json
from datetime import datetime

class CheckFAQTool(BaseTool):
    name: str = "check_faq"
    description: str = "Перевіряє базу знань FAQ і повертає найбільш релевантну відповідь"

    def _run(self, query: str) -> str:
        """Пошук у базі FAQ"""
        faq_database = {
            "доставка": "Доставка здійснюється Новою Поштою. Стандартний термін — 1-3 робочі дні. Вартість від 70 грн залежно від області.",
            "оплата": "Ми приймаємо оплату на карту ПриватБанку, Apple Pay, Google Pay та післяплату при доставці.",
            "повернення": "Повернення товару можливе протягом 14 днів з моменту отримання при збереженні товарного вигляду та упаковки.",
            "гарантія": "Гарантія на товари від 6 до 24 місяців залежно від категорії.",
            "статус замовлення": "Щоб перевірити статус, назвіть номер замовлення, і я відразу перевірю.",
            "скарга": "Вибачте, що виникла проблема. Будь ласка, опишіть детальніше, і я допоможу вирішити її максимально швидко."
        }

        query_lower = query.lower()
        for keyword, answer in faq_database.items():
            if keyword in query_lower:
                return answer

        return "На жаль, не знайшов точної відповіді в FAQ. Я можу передати ваше питання менеджеру для швидкого вирішення."


class GetOrderStatusTool(BaseTool):
    name: str = "get_order_status"
    description: str = "Отримує актуальний статус замовлення за його номером"

    class ArgsSchema(BaseModel):
        order_id: str = Field(..., description="Номер замовлення клієнта")

    def _run(self, order_id: str) -> str:
        # Заглушка. У реальному проєкті тут буде API інтеграція з Prom.ua або твоєю CRM
        statuses = {
            "12345": "Замовлення №12345 знаходиться в статусі 'В дорозі'. Очікувана доставка — завтра до 18:00.",
            "67890": "Замовлення №67890 успішно доставлено вчора. Дякуємо за покупку!",
            "11111": "Замовлення №11111 ще обробляється на складі. Очікуємо відправку сьогодні."
        }
        
        if order_id in statuses:
            return statuses[order_id]
        else:
            return f"Замовлення з номером {order_id} не знайдено. Будь ласка, перевірте правильність номера або надайте додаткову інформацію."


class SaveLeadTool(BaseTool):
    name: str = "save_lead"
    description: str = "Зберігає контактну інформацію клієнта та ключові деталі для подальшої роботи менеджера"

    class ArgsSchema(BaseModel):
        customer_name: str = Field(..., description="Ім'я клієнта")
        phone: Optional[str] = Field(None, description="Телефон клієнта")
        email: Optional[str] = Field(None, description="Email клієнта")
        note: Optional[str] = Field(None, description="Додаткова інформація або суть запиту")
        priority: Optional[str] = Field("medium", description="Пріоритет: low, medium, high")

    def _run(self, customer_name: str, phone: Optional[str] = None, 
             email: Optional[str] = None, note: Optional[str] = None, 
             priority: str = "medium") -> str:
        
        lead_data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "customer_name": customer_name,
            "phone": phone,
            "email": email,
            "note": note,
            "priority": priority,
            "source": "Smart Support UA Pro"
        }
        
        # Тут у реальному проєкті буде запис у Google Sheets, CRM або базу даних
        print(f"[LEAD SAVED] {lead_data}")
        
        return f"Інформація про клієнта {customer_name} успішно збережена. Менеджер зв'яжеться з вами найближчим часом."


# Експортуємо інструменти
available_tools = {
    "check_faq": CheckFAQTool(),
    "get_order_status": GetOrderStatusTool(),
    "save_lead": SaveLeadTool(),
}