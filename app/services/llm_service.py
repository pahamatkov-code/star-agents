import httpx
from app.core.config import settings


class LLMService:
    BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

    async def generate(self, messages: list[dict]):
        headers = {
            "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "Accept": "application/json",

            # 🔥 ОБОВ’ЯЗКОВІ заголовки OpenRouter
            "Referer": "http://localhost",
            "X-Title": "StarAgents",
            "User-Agent": "StarAgents/1.0",

            # 🔥 КРИТИЧНО ДЛЯ GPT‑4o‑mini
            "X-Model": settings.OPENROUTER_MODEL,
        }

        payload = {
            "model": settings.OPENROUTER_MODEL,
            "messages": messages,
        }

        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                self.BASE_URL,
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
