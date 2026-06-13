"""
Provider: Vertex AI (Gemini 2.5 Flash)
Auth: Service Account JSON via google-auth
Uso: inferencia primaria T1+T2
"""
import json
import httpx
import google.auth
import google.auth.transport.requests
from google.oauth2 import service_account

from config import settings

_SCOPES = ["https://www.googleapis.com/auth/cloud-platform"]
_credentials: service_account.Credentials | None = None


def _get_credentials() -> service_account.Credentials:
    global _credentials
    if _credentials is None:
        _credentials = service_account.Credentials.from_service_account_file(
            settings.VERTEX_SA_JSON_PATH,
            scopes=_SCOPES,
        )
    # Refresh si expirado
    request = google.auth.transport.requests.Request()
    if not _credentials.valid:
        _credentials.refresh(request)
    return _credentials


def _endpoint() -> str:
    return (
        f"https://{settings.VERTEX_LOCATION}-aiplatform.googleapis.com/v1/"
        f"projects/{settings.VERTEX_PROJECT_ID}/locations/{settings.VERTEX_LOCATION}/"
        f"publishers/google/models/{settings.VERTEX_INFERENCE_MODEL}:generateContent"
    )


async def complete(messages: list[dict], **kwargs) -> str:
    """Llamada a Gemini via Vertex AI REST. Retorna texto."""
    creds = _get_credentials()
    headers = {
        "Authorization": f"Bearer {creds.token}",
        "Content-Type": "application/json",
    }
    # Convertir formato OpenAI -> Gemini
    contents = [
        {"role": "model" if m["role"] == "assistant" else m["role"],
         "parts": [{"text": m["content"]}]}
        for m in messages if m["role"] != "system"
    ]
    system_parts = [
        {"text": m["content"]} for m in messages if m["role"] == "system"
    ]
    payload: dict = {"contents": contents}
    if system_parts:
        payload["systemInstruction"] = {"parts": system_parts}

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(_endpoint(), headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]


async def embed(text: str) -> list[float]:
    """Embedding via gemini-embedding-001, outputDimensionality=1536."""
    creds = _get_credentials()
    headers = {
        "Authorization": f"Bearer {creds.token}",
        "Content-Type": "application/json",
    }
    endpoint = (
        f"https://{settings.VERTEX_LOCATION}-aiplatform.googleapis.com/v1/"
        f"projects/{settings.VERTEX_PROJECT_ID}/locations/{settings.VERTEX_LOCATION}/"
        f"publishers/google/models/{settings.VERTEX_EMBED_MODEL}:predict"
    )
    payload = {
        "instances": [{"content": text}],
        "parameters": {"outputDimensionality": settings.VERTEX_EMBED_DIM},
    }
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(endpoint, headers=headers, json=payload)
        resp.raise_for_status()
        return resp.json()["predictions"][0]["embeddings"]["values"]
