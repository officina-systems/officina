"""
Provider: NVIDIA NIM (fallback 2)
Modelo: nvidia/llama-3.1-nemotron-ultra-253b-v1
API: OpenAI-compatible
"""
import httpx
from config import settings


async def complete(messages: list[dict], **kwargs) -> str:
    headers = {
        "Authorization": f"Bearer {settings.NVIDIA_NIM_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": settings.NVIDIA_MODEL,
        "messages": messages,
        "temperature": kwargs.get("temperature", 0.7),
    }
    async with httpx.AsyncClient(timeout=90) as client:
        resp = await client.post(
            f"{settings.NVIDIA_BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]
