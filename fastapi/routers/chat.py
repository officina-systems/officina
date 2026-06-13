"""
Router /v1/chat/completions

Compatible con OpenAI Chat Completions API.
Delega al cognitive router (fallback chain).
T1 PUSH: retrieval + Forma C + prompt assembly antes de inference.
Persistencia session.messages cuando conversation_id está presente.
Carga historial persistido desde session.messages cuando conversation_id está presente.
Carga documentos procesados desde session.documents cuando conversation_id está presente.
Streaming: no implementado en esta version (P1).
"""
import os
import time
import uuid
import logging
import psycopg
from psycopg.rows import dict_row

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Any

from cognitive import router as cognitive_router
from config import settings
from pipeline.retrieval import retrieve
from pipeline.forma_c import clarify_task
from pipeline.prompt import assemble_prompt

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1", tags=["chat"])

security = HTTPBearer(auto_error=False)


def verify_api_key(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> None:
    if not settings.FASTAPI_API_KEY:
        return  # sin key configurada: acceso libre (dev)
    if credentials is None or credentials.credentials != settings.FASTAPI_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    model: str = "officina"
    messages: list[Message]
    temperature: float | None = None
    max_tokens: int | None = None
    stream: bool = False
    conversation_id: str | None = None
    workspace_id: str | None = None
    folder_id: str | None = None


class Choice(BaseModel):
    index: int
    message: Message
    finish_reason: str


class Usage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class ChatResponse(BaseModel):
    id: str
    object: str
    created: int
    model: str
    choices: list[Choice]
    usage: Usage


def _last_user_message(messages: list[dict]) -> str:
    for message in reversed(messages):
        if message.get("role") == "user":
            return message.get("content", "")
    return messages[-1]["content"] if messages else ""


def _load_conversation_history(
    conversation_id: str | None,
    current_user_content: str,
    limit: int = 20,
) -> list[dict]:
    if not conversation_id or not settings.DATABASE_URL:
        return []

    with psycopg.connect(settings.DATABASE_URL, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id
                FROM session.conversations
                WHERE id = %s
                """,
                (conversation_id,),
            )
            if cur.fetchone() is None:
                raise HTTPException(status_code=404, detail="conversation_id not found")

            cur.execute(
                """
                SELECT role, content
                FROM session.messages
                WHERE conversation_id = %s
                ORDER BY created_at DESC
                LIMIT %s
                """,
                (conversation_id, limit),
            )
            rows = list(reversed(cur.fetchall()))

    history = [{"role": row["role"], "content": row["content"]} for row in rows]

    if history:
        last = history[-1]
        if last.get("role") == "user" and last.get("content") == current_user_content:
            history = history[:-1]

    return history


def _load_session_documents(
    conversation_id: str | None,
    limit: int = 5,
    chars_per_document: int = 4000,
) -> list[str]:
    if not conversation_id or not settings.DATABASE_URL:
        return []

    with psycopg.connect(settings.DATABASE_URL, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT filename, storage_path
                FROM session.documents
                WHERE conversation_id = %s
                  AND status = 'processed'
                ORDER BY created_at DESC
                LIMIT %s
                """,
                (conversation_id, limit),
            )
            rows = cur.fetchall()

    documents: list[str] = []

    for row in rows:
        extracted_path = f"{row['storage_path']}.md"

        if not os.path.exists(extracted_path):
            logger.warning(f"[chat] extracted document missing: {extracted_path}")
            continue

        try:
            with open(extracted_path, "r", encoding="utf-8") as f:
                text = f.read(chars_per_document)
        except Exception as e:
            logger.warning(f"[chat] failed reading session document {extracted_path}: {e}")
            continue

        if text.strip():
            documents.append(
                f"### {row['filename']}\n{text.strip()}"
            )

    return documents


def _persist_conversation_messages(
    conversation_id: str | None,
    user_content: str,
    assistant_content: str,
    model_used: str,
    prompt_tokens: int,
    completion_tokens: int,
) -> None:
    if not conversation_id or not settings.DATABASE_URL:
        return

    with psycopg.connect(settings.DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id
                FROM session.conversations
                WHERE id = %s
                """,
                (conversation_id,),
            )
            if cur.fetchone() is None:
                raise HTTPException(status_code=404, detail="conversation_id not found")

            cur.execute(
                """
                INSERT INTO session.messages (
                    conversation_id,
                    role,
                    content,
                    model_used,
                    tokens_used
                )
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    conversation_id,
                    "user",
                    user_content,
                    None,
                    prompt_tokens,
                ),
            )

            cur.execute(
                """
                INSERT INTO session.messages (
                    conversation_id,
                    role,
                    content,
                    model_used,
                    tokens_used
                )
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    conversation_id,
                    "assistant",
                    assistant_content,
                    model_used,
                    completion_tokens,
                ),
            )

            cur.execute(
                """
                UPDATE session.conversations
                SET updated_at = now()
                WHERE id = %s
                """,
                (conversation_id,),
            )


@router.post("/chat/completions", response_model=ChatResponse)
async def chat_completions(
    req: ChatRequest,
    _: None = Depends(verify_api_key),
) -> Any:
    start_time = time.time()

    if req.stream:
        raise HTTPException(status_code=501, detail="Streaming not yet implemented")

    raw_messages = [{"role": m.role, "content": m.content} for m in req.messages]

    if not raw_messages:
        raise HTTPException(status_code=400, detail="messages cannot be empty")

    original_message = _last_user_message(raw_messages)

    try:
        persisted_history = _load_conversation_history(
            conversation_id=req.conversation_id,
            current_user_content=original_message,
        )
        request_history = raw_messages[:-1]
        combined_history = persisted_history + request_history
        session_documents = _load_session_documents(
            conversation_id=req.conversation_id,
        )

        retrieval_result = await retrieve(
            message=original_message,
            conversation_id=req.conversation_id,
            workspace_id=req.workspace_id,
            folder_id=req.folder_id,
        )
        clarified = await clarify_task(original_message)
        prompt_messages = assemble_prompt(
            retrieval_result=retrieval_result,
            original_message=original_message,
            clarified_message=clarified,
            session_documents=session_documents,
            history=combined_history,
        )
    except Exception as e:
        logger.error(f"[chat] t1_push failed: {e}")
        raise HTTPException(status_code=500, detail=f"T1 PUSH failed: {e}")

    try:
        result = await cognitive_router.complete(prompt_messages)
    except RuntimeError as e:
        logger.error(f"[chat] all providers failed: {e}")
        raise HTTPException(status_code=503, detail=str(e))

    text = result["text"]
    provider = result["provider"]
    model_used = f"officina-{provider}"

    prompt_chars = sum(len(m["content"]) for m in prompt_messages)
    completion_chars = len(text)
    prompt_tokens = max(1, prompt_chars // 4)
    completion_tokens = max(1, completion_chars // 4) if completion_chars else 0
    latency_ms = int((time.time() - start_time) * 1000)

    logger.info(
        f"[chat] provider={provider} "
        f"prompt_messages={len(prompt_messages)} "
        f"history_messages={len(combined_history)} "
        f"session_documents={len(session_documents)} "
        f"completion_chars={completion_chars}"
    )

    if settings.DATABASE_URL:
        try:
            with psycopg.connect(settings.DATABASE_URL) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO usage (
                            conversation_id,
                            model_used,
                            provider,
                            tokens_input,
                            tokens_output,
                            latency_ms,
                            tool_calls
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """,
                        (
                            req.conversation_id,
                            model_used,
                            provider,
                            prompt_tokens,
                            completion_tokens,
                            latency_ms,
                            None,
                        ),
                    )
        except Exception as e:
            logger.error(f"[chat] usage logging failed: {e}")

    _persist_conversation_messages(
        conversation_id=req.conversation_id,
        user_content=original_message,
        assistant_content=text,
        model_used=model_used,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
    )

    return ChatResponse(
        id=f"chatcmpl-{uuid.uuid4().hex[:12]}",
        object="chat.completion",
        created=int(time.time()),
        model=model_used,
        choices=[
            Choice(
                index=0,
                message=Message(role="assistant", content=text),
                finish_reason="stop",
            )
        ],
        usage=Usage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
        ),
    )


@router.get("/models")
async def list_models(_: None = Depends(verify_api_key)) -> dict:
    models = [
        {"id": "officina", "object": "model", "owned_by": "officina"},
        {"id": "officina-vertex", "object": "model", "owned_by": "officina"},
        {"id": "officina-groq", "object": "model", "owned_by": "officina"},
        {"id": "officina-nvidia", "object": "model", "owned_by": "officina"},
        {"id": "officina-openrouter", "object": "model", "owned_by": "officina"},
        {"id": "officina-ollama", "object": "model", "owned_by": "officina"},
    ]
    return {"object": "list", "data": models}
