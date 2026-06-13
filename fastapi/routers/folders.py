import psycopg
from psycopg.rows import dict_row

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from config import settings
from routers.chat import verify_api_key


router = APIRouter(prefix="/folders", tags=["folders"])


class FolderCreate(BaseModel):
    workspace_id: str
    name: str
    description: str | None = None


def _connect():
    if not settings.DATABASE_URL:
        raise HTTPException(status_code=500, detail="DATABASE_URL is not configured")
    return psycopg.connect(settings.DATABASE_URL, row_factory=dict_row)


@router.post("")
async def create_folder(
    req: FolderCreate,
    _: None = Depends(verify_api_key),
):
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO session.folders (workspace_id, name, description)
                VALUES (%s, %s, %s)
                RETURNING id, workspace_id, name, description, created_at, updated_at
                """,
                (req.workspace_id, req.name, req.description),
            )
            return cur.fetchone()


@router.get("")
async def list_folders(
    workspace_id: str | None = Query(default=None),
    _: None = Depends(verify_api_key),
):
    with _connect() as conn:
        with conn.cursor() as cur:
            if workspace_id:
                cur.execute(
                    """
                    SELECT id, workspace_id, name, description, created_at, updated_at
                    FROM session.folders
                    WHERE workspace_id = %s
                    ORDER BY created_at DESC
                    """,
                    (workspace_id,),
                )
            else:
                cur.execute(
                    """
                    SELECT id, workspace_id, name, description, created_at, updated_at
                    FROM session.folders
                    ORDER BY created_at DESC
                    """
                )
            return cur.fetchall()
