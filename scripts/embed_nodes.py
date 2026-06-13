# scripts/embed_nodes.py
# NOTA S32: este script usa nomic-embed-text 768d (legacy).
# El motor de embedding canónico S32 es vertex_ai/text-embedding-004 1536d.
# Mantener como referencia. El nuevo embed vive en fastapi/pipeline/embed.py

import psycopg2
import requests
import json

OLLAMA_URL = "http://localhost:11434/api/embeddings"
OLLAMA_MODEL = "nomic-embed-text"

PG_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "officina",
    "user": "officina",
    "password": "officina"
}

def get_embedding(text):
    response = requests.post(OLLAMA_URL, json={"model": OLLAMA_MODEL, "prompt": text})
    return response.json()["embedding"]

def main():
    conn = psycopg2.connect(**PG_CONFIG)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, functional_definition FROM nodes WHERE embedding IS NULL")
    nodes = cursor.fetchall()
    print(f"Nodes sin embedding: {len(nodes)}")
    for node_id, name, fd in nodes:
        text = f"{name} {fd}"
        embedding = get_embedding(text)
        cursor.execute("UPDATE nodes SET embedding = %s WHERE id = %s", (json.dumps(embedding), str(node_id)))
        print(f"✓ {name}")
    conn.commit()
    cursor.close()
    conn.close()
    print("Bootstrap completo.")

if __name__ == "__main__":
    main()
