"""
Provider: Ollama local (fallback 4 — garantizado)
Modelo: qwen2.5:7b (7b cabe en RAM disponible, 32b no garantizado)
API: Ollama native
"""
import httpx
from config import settings


async def complete(messages: list[dict], **kwargs) -> str:
    payload = {
        "model": settings.OLLAMA_MODEL,
        "messages": messages,
        "stream": False,
        "options": {"temperature": kwargs.get("temperature", 0.7)},
    }
    async with httpx.AsyncClient(timeout=120) as client:
        resp = await client.post(
            f"{settings.OLLAMA_URL}/api/chat",
            json=payload,
        )
        resp.raise_for_status()
        return resp.json()["message"]["content"]
