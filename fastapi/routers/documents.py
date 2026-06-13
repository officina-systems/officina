import os
import uuid
import shutil
import psycopg
from psycopg.rows import dict_row

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from pydantic import BaseModel
from markitdown import MarkItDown

from config import settings
from routers.chat import verify_api_key
from pipeline.embed import embed_text


router = APIRouter(prefix="/documents", tags=["documents"])

UPLOAD_DIR = "/app/uploads"


class DocumentCreate(BaseModel):
    filename: str
    storage_path: str
    content_type: str | None = None
    folder_id: str | None = None
    conversation_id: str | None = None
    status: str = "pending"


class CrystallizeRequest(BaseModel):
    name: str | None = None
    node_type: str = "persistent"


def _connect():
    if not settings.DATABASE_URL:
        raise HTTPException(status_code=500, detail="DATABASE_URL is not configured")
    return psycopg.connect(settings.DATABASE_URL, row_factory=dict_row)


def _insert_document(
    folder_id: str | None,
    conversation_id: str | None,
    filename: str,
    content_type: str | None,
    storage_path: str,
    status: str = "pending",
):
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO session.documents (
                    folder_id,
                    conversation_id,
                    filename,
                    content_type,
                    storage_path,
                    status
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING
                    id,
                    folder_id,
                    conversation_id,
                    filename,
                    content_type,
                    storage_path,
                    status,
                    created_at
                """,
                (
                    folder_id,
                    conversation_id,
                    filename,
                    content_type,
                    storage_path,
                    status,
                ),
            )
            return cur.fetchone()


def _split_text_chunks(
    text: str,
    chunk_size: int = 3500,
    overlap: int = 300,
) -> list[str]:
    text = text.strip()

    if not text:
        return []

    if len(text) <= chunk_size:
        return [text]

    chunks: list[str] = []
    start = 0

    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(text):
            break

        start = max(0, end - overlap)

    return chunks
def _extract_operational_summary(
    text: str,
    max_items: int = 5,
    max_item_chars: int = 220,
) -> list[str]:
    normalized = " ".join(text.split())

    if not normalized:
        return []

    raw_parts = []
    buffer = ""

    for char in normalized:
        buffer += char
        if char in ".!?":
            part = buffer.strip()
            if part:
                raw_parts.append(part)
            buffer = ""

    if buffer.strip():
        raw_parts.append(buffer.strip())

    items: list[str] = []

    for part in raw_parts:
        if len(part) > max_item_chars:
            part = part[:max_item_chars].rstrip() + "..."

        if part and part not in items:
            items.append(part)

        if len(items) >= max_items:
            break

    if not items:
        fallback = normalized[:max_item_chars].rstrip()
        if len(normalized) > max_item_chars:
            fallback += "..."
        items.append(fallback)

    return items


def _build_document_definition(
    *,
    filename: str,
    external_id: str,
    chunk_count: int,
    text_content: str,
) -> str:
    summary_items = _extract_operational_summary(text_content)
    summary = "\n".join(f"- {item}" for item in summary_items)

    return (
        "[DOCUMENT]\n"
        f"filename: {filename}\n"
        f"external_id: {external_id}\n"
        "source_status: crystallized\n"
        "content_location: node_chunks\n"
        f"chunk_count: {chunk_count}\n"
        "operational_summary:\n"
        f"{summary}"
    )


def _get_document(document_id: str):
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    id,
                    folder_id,
                    conversation_id,
                    filename,
                    content_type,
                    storage_path,
                    status,
                    created_at
                FROM session.documents
                WHERE id = %s
                """,
                (document_id,),
            )
            row = cur.fetchone()

    if row is None:
        raise HTTPException(status_code=404, detail="document not found")

    return row


@router.post("")
async def create_document(
    req: DocumentCreate,
    _: None = Depends(verify_api_key),
):
    return _insert_document(
        folder_id=req.folder_id,
        conversation_id=req.conversation_id,
        filename=req.filename,
        content_type=req.content_type,
        storage_path=req.storage_path,
        status=req.status,
    )


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    folder_id: str | None = Form(default=None),
    conversation_id: str | None = Form(default=None),
    _: None = Depends(verify_api_key),
):
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    safe_name = os.path.basename(file.filename or "upload.bin")
    stored_name = f"{uuid.uuid4()}-{safe_name}"
    storage_path = os.path.join(UPLOAD_DIR, stored_name)

    try:
        with open(storage_path, "wb") as out:
            shutil.copyfileobj(file.file, out)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"upload failed: {e}")
    finally:
        file.file.close()

    return _insert_document(
        folder_id=folder_id,
        conversation_id=conversation_id,
        filename=safe_name,
        content_type=file.content_type,
        storage_path=storage_path,
        status="pending",
    )


@router.post("/{document_id}/process")
async def process_document(
    document_id: str,
    _: None = Depends(verify_api_key),
):
    document = _get_document(document_id)
    storage_path = document["storage_path"]

    if not os.path.exists(storage_path):
        with _connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE session.documents
                    SET status = 'failed'
                    WHERE id = %s
                    """,
                    (document_id,),
                )
        raise HTTPException(status_code=404, detail="document file not found")

    try:
        result = MarkItDown().convert(storage_path)
        text_content = result.text_content or ""
        extracted_path = f"{storage_path}.md"

        with open(extracted_path, "w", encoding="utf-8") as out:
            out.write(text_content)

        with _connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE session.documents
                    SET status = 'processed'
                    WHERE id = %s
                    """,
                    (document_id,),
                )
    except Exception as e:
        with _connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE session.documents
                    SET status = 'failed'
                    WHERE id = %s
                    """,
                    (document_id,),
                )
        raise HTTPException(status_code=500, detail=f"document processing failed: {e}")

    return {
        "id": document["id"],
        "filename": document["filename"],
        "storage_path": storage_path,
        "extracted_path": extracted_path,
        "status": "processed",
        "text_preview": text_content[:1000],
    }


@router.post("/{document_id}/crystallize")
async def crystallize_document(
    document_id: str,
    req: CrystallizeRequest | None = None,
    _: None = Depends(verify_api_key),
):
    document = _get_document(document_id)

    if document["status"] != "processed":
        raise HTTPException(
            status_code=409,
            detail="document must be processed before crystallization",
        )

    extracted_path = f"{document['storage_path']}.md"

    if not os.path.exists(extracted_path):
        raise HTTPException(status_code=404, detail="extracted document file not found")

    with open(extracted_path, "r", encoding="utf-8") as f:
        text_content = f.read().strip()

    if not text_content:
        raise HTTPException(status_code=409, detail="extracted document is empty")

    external_id = f"document:{document_id}"
    node_name = req.name if req and req.name else f"document:{document['filename']}"
    node_type = req.node_type if req else "persistent"

    if node_type != "persistent":
        raise HTTPException(status_code=400, detail="only persistent crystallization is supported in MT-5.1")

    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, name, node_type, status, contextual_type, external_id
                FROM nodes
                WHERE external_id = %s
                ORDER BY created_at ASC
                LIMIT 1
                """,
                (external_id,),
            )
            existing_node = cur.fetchone()

            if existing_node is not None:
                cur.execute(
                    """
                    SELECT id, node_id, status
                    FROM node_chunks
                    WHERE node_id = %s
                    ORDER BY created_at ASC
                    LIMIT 1
                    """,
                    (existing_node["id"],),
                )
                existing_chunk = cur.fetchone()

                if existing_chunk is not None:
                    cur.execute(
                        """
                        UPDATE session.documents
                        SET status = 'crystallized'
                        WHERE id = %s
                        """,
                        (document_id,),
                    )
                    return {
                        "document_id": document_id,
                        "node": existing_node,
                        "chunk": existing_chunk,
                        "external_id": external_id,
                        "document_status": "crystallized",
                        "existing": True,
                        "created": False,
                        "text_preview": text_content[:1000],
                    }

            text_chunks = _split_text_chunks(text_content)
            document_definition = _build_document_definition(
                filename=document["filename"],
                external_id=external_id,
                chunk_count=len(text_chunks),
                text_content=text_content,
            )

            if existing_node is None:
                cur.execute(
                    """
                    INSERT INTO nodes (
                        name,
                        functional_definition,
                        node_type,
                        status,
                        contextual_type,
                        external_id
                    )
                    VALUES (%s, %s, 'persistent', 'active', NULL, %s)
                    RETURNING id, name, node_type, status, contextual_type, external_id
                    """,
                    (
                        node_name,
                        document_definition,
                        external_id,
                    ),
                )
                node = cur.fetchone()
            else:
                node = existing_node

            chunks = []

            for text_chunk in text_chunks:
                embedding = await embed_text(text_chunk)
                vector_str = "[" + ",".join(str(v) for v in embedding) + "]"

                cur.execute(
                    """
                    INSERT INTO node_chunks (
                        node_id,
                        chunk_text,
                        embedding,
                        status
                    )
                    VALUES (%s, %s, %s::vector, 'active')
                    RETURNING id, node_id, status
                    """,
                    (
                        node["id"],
                        text_chunk,
                        vector_str,
                    ),
                )
                chunks.append(cur.fetchone())

            chunk = chunks[0] if chunks else None

            cur.execute(
                """
                UPDATE session.documents
                SET status = 'crystallized'
                WHERE id = %s
                """,
                (document_id,),
            )

    return {
        "document_id": document_id,
        "node": node,
        "chunk": chunk,
        "chunks": chunks,
        "chunk_count": len(chunks),
        "external_id": external_id,
        "document_status": "crystallized",
        "existing": existing_node is not None,
        "created": True,
        "text_preview": text_content[:1000],
    }


@router.get("/{document_id}")
async def inspect_document(
    document_id: str,
    _: None = Depends(verify_api_key),
):
    document = _get_document(document_id)
    extracted_path = f"{document['storage_path']}.md"
    extracted_exists = os.path.exists(extracted_path)
    graph_external_id = f"document:{document_id}"

    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, name, node_type, contextual_type, external_id, status
                FROM nodes
                WHERE external_id = %s
                ORDER BY created_at ASC
                LIMIT 1
                """,
                (graph_external_id,),
            )
            node = cur.fetchone()

            chunk_count = 0
            if node is not None:
                cur.execute(
                    """
                    SELECT count(*) AS chunk_count
                    FROM node_chunks
                    WHERE node_id = %s
                    """,
                    (node["id"],),
                )
                chunk_count = cur.fetchone()["chunk_count"]

    return {
        "document": document,
        "extracted_path": extracted_path,
        "extracted_exists": extracted_exists,
        "graph_external_id": graph_external_id,
        "node": node,
        "chunk_count": chunk_count,
    }

@router.get("")
async def list_documents(
    folder_id: str | None = Query(default=None),
    conversation_id: str | None = Query(default=None),
    status: str | None = Query(default=None),
    _: None = Depends(verify_api_key),
):
    clauses = []
    params = []

    if folder_id:
        clauses.append("folder_id = %s")
        params.append(folder_id)

    if conversation_id:
        clauses.append("conversation_id = %s")
        params.append(conversation_id)

    if status:
        clauses.append("status = %s")
        params.append(status)

    where_sql = ""
    if clauses:
        where_sql = "WHERE " + " AND ".join(clauses)

    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT
                    id,
                    folder_id,
                    conversation_id,
                    filename,
                    content_type,
                    storage_path,
                    status,
                    created_at
                FROM session.documents
                {where_sql}
                ORDER BY created_at DESC
                """,
                tuple(params),
            )
            return cur.fetchall()






