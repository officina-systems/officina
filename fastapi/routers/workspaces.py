import psycopg
from psycopg.rows import dict_row

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from config import settings
from routers.chat import verify_api_key


router = APIRouter(prefix="/workspaces", tags=["workspaces"])


class WorkspaceCreate(BaseModel):
    name: str
    description: str | None = None


def _connect():
    if not settings.DATABASE_URL:
        raise HTTPException(status_code=500, detail="DATABASE_URL is not configured")
    return psycopg.connect(settings.DATABASE_URL, row_factory=dict_row)


@router.post("")
async def create_workspace(
    req: WorkspaceCreate,
    _: None = Depends(verify_api_key),
):
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO session.workspaces (name, description)
                VALUES (%s, %s)
                RETURNING id, name, description, created_at, updated_at
                """,
                (req.name, req.description),
            )
            return cur.fetchone()


@router.get("")
async def list_workspaces(_: None = Depends(verify_api_key)):
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, name, description, created_at, updated_at
                FROM session.workspaces
                ORDER BY created_at DESC
                """
            )
            return cur.fetchall()
