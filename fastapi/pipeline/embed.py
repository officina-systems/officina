"""
pipeline/embed.py — Genera embeddings via Vertex AI gemini-embedding-001

Uso:
  from pipeline.embed import embed_text, embed_node_chunk

TODO: embed_node_chunk inserta en node_chunks una vez schema BD validado.
"""
import logging
from cognitive.providers.vertex import embed as vertex_embed

logger = logging.getLogger(__name__)


async def embed_text(text: str) -> list[float]:
    """Retorna vector 1536d para texto arbitrario."""
    return await vertex_embed(text)


async def embed_node_chunk(
    conn,
    node_id: str,
    chunk_text: str,
) -> None:
    """
    Genera embedding y hace INSERT en node_chunks.
    conn: conexion psycopg activa.
    """
    vector = await vertex_embed(chunk_text)
    vector_str = "[" + ",".join(str(v) for v in vector) + "]"
    await conn.execute(
        """
        INSERT INTO node_chunks (node_id, chunk_text, embedding, status)
        VALUES (%s, %s, %s::vector, 'active')
        ON CONFLICT DO NOTHING
        """,
        (node_id, chunk_text, vector_str),
    )
    logger.info(f"[embed] chunk inserted for node {node_id}")
