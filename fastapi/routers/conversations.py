import psycopg
from psycopg.rows import dict_row

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from config import settings
from routers.chat import verify_api_key


router = APIRouter(prefix="/conversations", tags=["conversations"])


class ConversationCreate(BaseModel):
    workspace_id: str | None = None
    folder_id: str | None = None
    title: str | None = None
    model_group: str = "officina-primary"


def _connect():
    if not settings.DATABASE_URL:
        raise HTTPException(status_code=500, detail="DATABASE_URL is not configured")
    return psycopg.connect(settings.DATABASE_URL, row_factory=dict_row)


@router.post("")
async def create_conversation(
    req: ConversationCreate,
    _: None = Depends(verify_api_key),
):
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO session.conversations (workspace_id, folder_id, title, model_group)
                VALUES (%s, %s, %s, %s)
                RETURNING id, workspace_id, folder_id, title, model_group, created_at, updated_at
                """,
                (req.workspace_id, req.folder_id, req.title, req.model_group),
            )
            return cur.fetchone()


@router.get("")
async def list_conversations(
    workspace_id: str | None = Query(default=None),
    folder_id: str | None = Query(default=None),
    _: None = Depends(verify_api_key),
):
    with _connect() as conn:
        with conn.cursor() as cur:
            if folder_id:
                cur.execute(
                    """
                    SELECT id, workspace_id, folder_id, title, model_group, created_at, updated_at
                    FROM session.conversations
                    WHERE folder_id = %s
                    ORDER BY created_at DESC
                    """,
                    (folder_id,),
                )
            elif workspace_id:
                cur.execute(
                    """
                    SELECT id, workspace_id, folder_id, title, model_group, created_at, updated_at
                    FROM session.conversations
                    WHERE workspace_id = %s
                    ORDER BY created_at DESC
                    """,
                    (workspace_id,),
                )
            else:
                cur.execute(
                    """
                    SELECT id, workspace_id, folder_id, title, model_group, created_at, updated_at
                    FROM session.conversations
                    ORDER BY created_at DESC
                    """
                )
            return cur.fetchall()
