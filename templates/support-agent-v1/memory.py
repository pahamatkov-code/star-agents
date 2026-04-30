# memory.py - Контекстна пам'ять для Smart Support UA Pro

from typing import List, Dict
from datetime import datetime

class ConversationMemory:
    def __init__(self, max_messages: int = 10):
        self.history: List[Dict] = []
        self.max_messages = max_messages

    def add_message(self, role: str, content: str, customer_name: str = None):
        """Додає повідомлення в історію"""
        message = {
            "timestamp": datetime.now().strftime("%H:%M"),
            "role": role,
            "content": content,
            "customer_name": customer_name
        }
        self.history.append(message)
        
        # Обмежуємо розмір історії
        if len(self.history) > self.max_messages:
            self.history.pop(0)

    def get_history(self) -> List[Dict]:
        """Повертає історію розмови"""
        return self.history

    def get_formatted_history(self) -> str:
        """Повертає історію у зручному форматі для промпту"""
        if not self.history:
            return "Це перше повідомлення від клієнта."
        
        formatted = "Історія розмови:\n"
        for msg in self.history:
            formatted += f"[{msg['timestamp']}] {msg['role']}: {msg['content']}\n"
        return formatted

    def clear(self):
        """Очищає історію"""
        self.history = []


# Глобальний об'єкт пам'яті (для одного клієнта на сесію)
conversation_memory = ConversationMemory()