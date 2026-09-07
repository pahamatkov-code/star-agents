import httpx
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

    async def generate(
        self,
        messages: list[dict],
        model: str = None,
        temperature: float = 0.4,
        max_tokens: int = 300,
        fallback_models: list[str] = None
    ):
        """
        Універсальний метод генерації відповіді з підтримкою:
        - моделі
        - температури
        - ліміту токенів
        - fallback моделей
        """

        model = model or settings.OPENROUTER_MODEL
        fallback_models = fallback_models or []

        headers = {
            "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "Accept": "application/json",

            # 🔥 ОБОВ’ЯЗКОВІ заголовки OpenRouter
            "Referer": "http://localhost",
            "X-Title": "StarAgents",
            "User-Agent": "StarAgents/1.0",
        }

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        # Якщо є fallback — додаємо
        if fallback_models:
            payload["fallback_models"] = fallback_models

        try:
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(
                    self.BASE_URL,
                    json=payload,
                    headers=headers
                )
                response.raise_for_status()
                data = response.json()

                return data["choices"][0]["message"]["content"]

        except Exception as e:
            logger.error(f"LLMService error: {str(e)}")
            raise
