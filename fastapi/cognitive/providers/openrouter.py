"""
Provider: OpenRouter (fallback 3)
Modelo: meta-llama/llama-3.3-70b-instruct:free
API: OpenAI-compatible
"""
import httpx
from config import settings


async def complete(messages: list[dict], **kwargs) -> str:
    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://officina.local",
    }
    payload = {
        "model": settings.OPENROUTER_MODEL,
        "messages": messages,
        "temperature": kwargs.get("temperature", 0.7),
    }
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            f"{settings.OPENROUTER_BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]
