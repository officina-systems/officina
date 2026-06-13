"""
Router /v1/embeddings

Compatible con OpenAI Embeddings API.
Delega a pipeline.embed.embed_text() → vertex.embed() → gemini-embedding-001 (1536d).
"""
import time
import logging

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Any

from pipeline.embed import embed_text
from config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1", tags=["embeddings"])

security = HTTPBearer(auto_error=False)


def verify_api_key(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> None:
    if not settings.FASTAPI_API_KEY:
        return  # dev: sin key configurada, acceso libre
    if credentials is None or credentials.credentials != settings.FASTAPI_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


class EmbeddingRequest(BaseModel):
    input: str | list[str]
    model: str = "gemini-embedding-001"


class EmbeddingObject(BaseModel):
    object: str = "embedding"
    index: int
    embedding: list[float]


class EmbeddingResponse(BaseModel):
    object: str = "list"
    data: list[EmbeddingObject]
    model: str
    usage: dict


@router.post("/embeddings", response_model=EmbeddingResponse)
async def create_embeddings(
    req: EmbeddingRequest,
    _: None = Depends(verify_api_key),
) -> Any:
    inputs: list[str] = [req.input] if isinstance(req.input, str) else req.input

    results: list[EmbeddingObject] = []
    total_chars = 0
    for i, text in enumerate(inputs):
        try:
            vector = await embed_text(text)
        except Exception as e:
            logger.error(f"[embeddings] vertex failed for input[{i}]: {e}")
            raise HTTPException(status_code=503, detail=f"Embedding failed: {e}")
        results.append(EmbeddingObject(index=i, embedding=vector))
        total_chars += len(text)

    logger.info(f"[embeddings] {len(inputs)} input(s), dims={len(results[0].embedding) if results else 0}")

    return EmbeddingResponse(
        data=results,
        model=req.model,
        usage={"prompt_tokens": total_chars // 4, "total_tokens": total_chars // 4},
    )
