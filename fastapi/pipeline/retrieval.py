import psycopg
from psycopg.rows import dict_row

from config import settings
from pipeline.embed import embed_text


SIMILARITY_THRESHOLD = 0.7
TRAVERSAL_HOPS = 2


def _vector_literal(vec: list[float]) -> str:
    return "[" + ",".join(str(float(x)) for x in vec) + "]"


async def retrieve(
    message: str,
    conversation_id: str | None = None,
    workspace_id: str | None = None,
    folder_id: str | None = None,
) -> dict:
    if not settings.DATABASE_URL:
        raise RuntimeError("DATABASE_URL is not configured")

    query_vector = await embed_text(message)
    query_vector_literal = _vector_literal(query_vector)

    external_ids = [
        value for value in [conversation_id, workspace_id, folder_id]
        if value is not None and str(value).strip()
    ]

    with psycopg.connect(settings.DATABASE_URL, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, name, functional_definition
                FROM nodes
                WHERE node_type = 'persistent'
                  AND status = 'active'
                ORDER BY name
                """
            )
            bucket_1 = cur.fetchall()

            if external_ids:
                cur.execute(
                    """
                    SELECT id, name, functional_definition
                    FROM nodes
                    WHERE external_id = ANY(%s)
                      AND status = 'active'
                    ORDER BY name
                    """,
                    (external_ids,),
                )
                bucket_2 = cur.fetchall()
            else:
                bucket_2 = []

            cur.execute(
                """
                SELECT DISTINCT ON (nc.node_id)
                    n.id,
                    n.name,
                    n.functional_definition,
                    (nc.embedding <=> %s::vector) AS distance
                FROM node_chunks nc
                JOIN nodes n ON n.id = nc.node_id
                WHERE nc.embedding IS NOT NULL
                  AND nc.status = 'active'
                  AND n.status = 'active'
                  AND (nc.embedding <=> %s::vector) < %s
                ORDER BY nc.node_id, nc.embedding <=> %s::vector
                """,
                (
                    query_vector_literal,
                    query_vector_literal,
                    SIMILARITY_THRESHOLD,
                    query_vector_literal,
                ),
            )
            bucket_3 = cur.fetchall()

            seed_ids = []
            for row in bucket_1 + bucket_2 + bucket_3:
                node_id = str(row["id"])
                if node_id not in seed_ids:
                    seed_ids.append(node_id)

            all_ids = list(seed_ids)

            frontier = list(seed_ids)
            for _ in range(TRAVERSAL_HOPS):
                if not frontier:
                    break

                cur.execute(
                    """
                    SELECT DISTINCT target_node_id AS id
                    FROM edges
                    WHERE status = 'active'
                      AND source_node_id = ANY(%s::uuid[])
                      AND target_node_id IS NOT NULL

                    UNION

                    SELECT DISTINCT source_node_id AS id
                    FROM edges
                    WHERE status = 'active'
                      AND target_node_id = ANY(%s::uuid[])
                      AND source_node_id IS NOT NULL
                    """,
                    (frontier, frontier),
                )
                next_ids = [str(row["id"]) for row in cur.fetchall()]
                next_ids = [node_id for node_id in next_ids if node_id not in all_ids]

                all_ids.extend(next_ids)
                frontier = next_ids

            if all_ids:
                cur.execute(
                    """
                    SELECT id, name, node_type, contextual_type, functional_definition
                    FROM nodes
                    WHERE id = ANY(%s::uuid[])
                    ORDER BY name
                    """,
                    (all_ids,),
                )
                final_nodes = cur.fetchall()
            else:
                final_nodes = []

    return {
        "bucket_1": bucket_1,
        "bucket_2": bucket_2,
        "bucket_3": bucket_3,
        "all_ids": all_ids,
        "final_nodes": final_nodes,
    }
