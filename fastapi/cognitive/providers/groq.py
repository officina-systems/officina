"""
Provider: Groq (fallback 1)
Modelo: llama-3.3-70b-versatile
API: OpenAI-compatible
"""
import httpx
from config import settings

_BASE = "https://api.groq.com/openai/v1/chat/completions"


async def complete(messages: list[dict], **kwargs) -> str:
    headers = {
        "Authorization": f"Bearer {settings.GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": settings.GROQ_MODEL,
        "messages": messages,
        "temperature": kwargs.get("temperature", 0.7),
    }
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(_BASE, headers=headers, json=payload)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]
