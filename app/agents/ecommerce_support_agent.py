from typing import Any, Dict, List
from app.services.llm_service import LLMService
import logging
import datetime
import asyncio
import json
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
# STAR AGENT — АВТОМАТИЗОВАНА ПІДТРИМКА

## 1. ІДЕНТИЧНІСТЬ
Ти — **StarAgent**, головний консультант інтернет‑магазину «Star Agents».
Ти — обличчя бренду: створюєш довіру, даруєш впевненість і вирішуєш питання клієнтів так, щоб вони після кожної розмови відчували спокій і захищеність.

## 2. КОМУНІКАЦІЙНІ ПРИНЦИПИ
- **Мова:** тільки українська, чиста й літературна.
- **Тон:** ввічливий, впевнений, доброзичливий, але без надмірної фамільярності.
- **Стиль:** відповідай чітко, структуровано, по суті. Оптимальна довжина — 2–4 речення.
- **Адаптивність:** відчувай настрій клієнта. Якщо він жартує чи пише з емодзі — підтримай легкий тон. Якщо він стурбований — будь максимально серйозним і емпатичним.
- **Заборона:** ніколи не кажи «я не знаю». Завжди пропонуй рішення або наступний крок. Якщо даних немає — скеруй до менеджера.
- **Мета:** кожна відповідь має залишати клієнта з відчуттям впевненості, що його питання вирішується.

## 3. ПРАВИЛА МАГАЗИНУ
- **Доставка:**
  - Нова Пошта: 2–3 дні
  - Укрпошта: 3–5 днів
  - Кур'єр: 1–2 дні
- **Оплата:**
  - Онлайн карткою (Visa/Mastercard) — миттєво
  - Накладений платіж — комісія ~2% від суми
  - Банківський переказ — для юридичних осіб
- **Повернення:**
  - Термін: 14 днів з моменту отримання
  - Умова: товар має бути в оригінальній упаковці, без слідів використання
  - Процедура: клієнт надсилає заявку, менеджер підтверджує, кошти повертаються протягом 3 робочих днів

## 4. СЦЕНАРІЇ РЕАГУВАННЯ
- **Привітання:** коротке, тепле, можна додати емодзі.
- **Стурбований клієнт:** визнай його емоцію («Я розумію ваше занепокоєння…»), дай факти й запевни, що все буде добре.
- **Технічне питання:** дай чітку інструкцію, за потреби попроси уточнити деталі (наприклад, номер замовлення).
- **Прощання:** ввічливо заверши діалог, побажай гарного дня й запроси звертатися знову.

## 5. ДОДАТКОВІ НАСТАНОВИ
- Завжди говори від імені магазину «Star Agents».
- Не повторюй одне й те ж привітання двічі.
- Використовуй емодзі помірковано — лише для підкреслення тону.
- Відповіді мають бути узгоджені між собою, не суперечити попереднім повідомленням.
"""

class EcommerceSupportAgent:
    """
    Промисловий AI-агент підтримки з ізольованою історією сесій, асинхронним логуванням,
    аналітикою та аналізом намірів (multi-agent ready).
    """

    def __init__(self, max_history: int = 10, log_file: str = None):
        self.llm = LLMService()
        self.sessions: Dict[str, List[Dict[str, str]]] = {}
        self.max_history = max_history
        
        # Встановлюємо шлях до лог-файлу
        if log_file is None:
            log_file = os.getenv("AGENT_LOG_FILE", "/app/logs/dialog_logs.jsonl")
        self.log_file = log_file
        
        # Створюємо папку для логів
        log_dir = os.path.dirname(self.log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
            logger.info(f"Created log directory: {log_dir}")
        
        # Створюємо файл логів, якщо його немає
        if not os.path.exists(self.log_file):
            try:
                with open(self.log_file, "w", encoding="utf-8") as f:
                    pass
                logger.info(f"Created log file: {self.log_file}")
            except Exception as e:
                logger.error(f"Failed to create log file: {str(e)}")

    async def _log_interaction(self, agent_name: str, user_id: str, message: str, reply: str, duration: float, error: str = None) -> None:
        """Асинхронно записує взаємодію у JSONL файл."""
        try:
            log_entry = {
                "timestamp": datetime.datetime.now().isoformat(),
                "agent": agent_name,
                "user_id": user_id,
                "message": message,
                "reply": reply,
                "duration": duration
            }
            if error:
                log_entry["error"] = error

            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._write_log_entry, log_entry)
            logger.info(f"Logged interaction for agent {agent_name}, user {user_id}")
        except Exception as e:
            logger.error(f"Failed to log interaction: {str(e)}")

    def _write_log_entry(self, log_entry: Dict[str, Any]) -> None:
        """Синхронний запис у файл (виконується в окремому потоці)."""
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        except Exception as e:
            logger.error(f"Failed to write log entry: {str(e)}")

    def _get_user_history(self, user_id: str) -> List[Dict[str, str]]:
        if user_id not in self.sessions:
            self.sessions[user_id] = []
        return self.sessions[user_id]

    def _limit_history(self, user_id: str) -> None:
        history = self._get_user_history(user_id)
        if len(history) > self.max_history:
            self.sessions[user_id] = history[-self.max_history:]

    def _build_messages(self, user_id: str, user_message: str, dynamic_prompt: str) -> List[Dict[str, str]]:
        history = self._get_user_history(user_id)
        history.append({"role": "user", "content": user_message})
        self._limit_history(user_id)
        return [{"role": "system", "content": dynamic_prompt}] + self.sessions[user_id]

    def _model_config(self) -> Dict[str, Any]:
        return {
            "model": "openai/gpt-4o-mini",
            "temperature": 0.4,
            "max_tokens": 300,
            "fallback_models": ["google/gemini-3.1-pro-preview"]
        }

    def _handle_error(self, error: Exception, user_message: str) -> str:
        logger.error(f"LLM error for message '{user_message[:50]}': {str(error)}")
        return "Вибачте, зараз не можу відповісти на ваше запитання. Будь ласка, спробуйте ще раз за кілька хвилин."

    async def _analyze_intent(self, user_message: str) -> Dict[str, Any]:
        analysis_prompt = f"""
        Проаналізуй повідомлення клієнта. Поверни JSON з полями:
        1. "intent": "greeting", "shipping_info", "payment_info", "return_policy", "order_status", "general".
        2. "assumptions": список припущень (якщо клієнт запитав абстрактно).

        Повідомлення: "{user_message}"
        Поверни ТІЛЬКИ чистий JSON. Без розмітки markdown.
        """
        try:
            raw_analysis = await self.llm.generate(
                messages=[{"role": "user", "content": analysis_prompt}],
                model="openai/gpt-4o-mini",
                temperature=0.0
            )
            cleaned_analysis = raw_analysis.strip()
            if cleaned_analysis.startswith("```"):
                cleaned_analysis = cleaned_analysis.split("\n", 1)[1].rsplit("```", 1)[0].strip()
                if cleaned_analysis.startswith("json"):
                    cleaned_analysis = cleaned_analysis[4:].strip()
            return json.loads(cleaned_analysis)
        except Exception as e:
            logger.error(f"Intent analysis failed: {str(e)}")
            return {"intent": "general", "assumptions": []}

    async def get_stats(self) -> Dict[str, Any]:
        def _calculate() -> Dict[str, Any]:
            if not os.path.exists(self.log_file):
                logger.warning(f"Log file not found: {self.log_file}")
                return {
                    "total_requests": 0,
                    "avg_duration": 0.0,
                    "errors_count": 0,
                    "unique_users": 0
                }

            total_duration = 0.0
            total_requests = 0
            errors_count = 0
            users = set()
            
            try:
                with open(self.log_file, "r", encoding="utf-8") as f:
                    for line in f:
                        if not line.strip():
                            continue
                        try:
                            data = json.loads(line)
                            total_requests += 1
                            total_duration += data.get("duration", 0.0)
                            if "error" in data or data.get("duration") == 0.0:
                                errors_count += 1
                            if "user_id" in data:
                                users.add(data["user_id"])
                        except json.JSONDecodeError:
                            continue
            except Exception as e:
                logger.error(f"Error reading log file: {str(e)}")
                return {
                    "total_requests": 0,
                    "avg_duration": 0.0,
                    "errors_count": 0,
                    "unique_users": 0
                }

            avg_duration = total_duration / total_requests if total_requests > 0 else 0.0
            return {
                "total_requests": total_requests,
                "avg_duration": round(avg_duration, 3),
                "errors_count": errors_count,
                "unique_users": len(users)
            }
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _calculate)

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        user_message = payload.get("message", "").strip()
        user_id = payload.get("user_id", "anonymous")

        if not user_message:
            return {"agent": "ecommerce_support", "reply": "Будь ласка, напишіть ваше запитання.", "error": "empty_message"}

        start = datetime.datetime.now()
        try:
            analysis = await self._analyze_intent(user_message)
            client_intent = analysis.get("intent", "general")
            client_assumptions = analysis.get("assumptions", [])

            dynamic_prompt = SYSTEM_PROMPT
            if client_assumptions:
                assumptions_str = ", ".join(client_assumptions)
                dynamic_prompt += f"\n\n## 6. ПРИПУЩЕННЯ СИСТЕМИ:\nТи дієш на основі таких припущень: {assumptions_str}. Обов'язково натякни про це клієнту."

            messages = self._build_messages(user_id, user_message, dynamic_prompt)
            config = self._model_config()
            logger.info(f"Intent '{client_intent}' for user {user_id}: {user_message[:50]}...")

            reply = await self.llm.generate(messages=messages, **config)
            duration = (datetime.datetime.now() - start).total_seconds()
            
            if not reply or len(reply.strip()) < 2:
                reply = "Дякую! Я обробляю інформацію."
            
            self._get_user_history(user_id).append({"role": "assistant", "content": reply})

            # Логуємо взаємодію
            await self._log_interaction("ecommerce_support", user_id, user_message, reply, duration)

            return {
                "agent": "ecommerce_support",
                "intent": client_intent,
                "assumptions": client_assumptions,
                "reply": reply,
                "history_length": len(self._get_user_history(user_id)),
                "duration": duration
            }

        except Exception as e:
            reply = self._handle_error(e, user_message)
            duration = (datetime.datetime.now() - start).total_seconds()
            await self._log_interaction("ecommerce_support", user_id, user_message, reply, duration, error=str(e))
            return {"agent": "ecommerce_support", "reply": reply, "error": str(e)}

    def reset_history(self, user_id: str = None) -> None:
        if user_id:
            if user_id in self.sessions:
                self.sessions[user_id].clear()
            logger.info(f"History reset for user {user_id}")
        else:
            self.sessions.clear()
            logger.info("All histories reset")

    def get_history(self, user_id: str) -> List[Dict[str, str]]:
        return self._get_user_history(user_id).copy()

    def get_recent_history(self, user_id: str, n: int = 5) -> List[Dict[str, str]]:
        history = self._get_user_history(user_id)
        return history[-n:] if history else []


def create_ecommerce_support_agent() -> EcommerceSupportAgent:
    return EcommerceSupportAgent()