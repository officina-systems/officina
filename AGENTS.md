# OFFICINA Framework — OpenCode Context

## Rol de OpenCode

OpenCode es el WorkspaceRuntimeProvider del OFFICINA Framework.
Ejecuta código, modifica archivos, corre tests, itera.
Complementa MCP (lectura) — OpenCode es escritura y ejecución.

## Cognitive Provider

OpenCode apunta a FastAPI como Cognitive Provider:
```
base_url: http://localhost:8000/v1
api_key:  FASTAPI_API_KEY (desde .env)
```

El cognitive router de FastAPI maneja el fallback:
Vertex AI gemini-2.5-flash → Groq llama-3.3-70b → NVIDIA nemotron → OpenRouter → Ollama qwen2.5:7b

## Estructura del repositorio

```
officina/
  fastapi/          → motor cognitivo central (T1 PUSH + T2 PULL + routing)
    cognitive/      → router.py, providers/, tools.py
    pipeline/       → retrieval.py, prompt.py, embed.py, forma_c.py
    routers/        → chat.py, workspaces.py, conversations.py, documents.py
    db/             → officina.py, session.py
    main.py
  react/            → UI dumb (React 18 + Vite + Tailwind)
  agents/           → Sleep Agent, Dreaming Agent, Document Agent
  db/               → SQL schemas (migrations)
  mcp/              → MCP server postgres
  scripts/          → utilidades
  cognition/        → operational-ledger.ndjson, officina-infra.md
  secrets/          → .gitignored — SA JSON Vertex AI
  data/             → .gitignored — postgres, ollama, uploads, watch
```

## Stack activo (Docker)

```
officina-postgres   :5432   PostgreSQL 17 + pgvector
officina-ollama     :11434  Ollama (embeddings fallback, qwen2.5:7b)
officina-fastapi    :8000   FastAPI (motor cognitivo)
```

## BD officina — esquema

```
public.nodes        → grafo de conocimiento + configuración del stack
public.edges        → relaciones between nodes
public.node_chunks  → chunks embebidos vector(1536)
public.usage        → spend logging
session.workspaces  → workspaces operativos
session.folders     → folders por workspace
session.conversations → conversaciones
session.messages    → mensajes
session.documents   → documentos procesados
```

## Convenciones de implementación

- Python: async/await en toda la capa FastAPI
- Ningún módulo usa `os.getenv()` directamente — todo pasa por `config.py`
- Secrets: nunca en código ni en logs
- SQL: queries via `asyncpg` o `psycopg2` — no ORM
- Embeddings: `pipeline/embed.py` → Vertex AI gemini-embedding-001, 1536d
- Errores: propagar con contexto, no silenciar
- Tests: verificar contra `localhost:8000/health` antes de asumir FastAPI activo

## Reglas operacionales

- `git status` antes de cualquier modificación de archivos
- No tocar `secrets/` — bind-mounted read-only
- No modificar `data/` — runtime data, fuera de Git
- Commits descriptivos con prefijo de sesión: `S34: <descripción>`
- Al terminar una tarea: `git add`, `git commit`, `git push`

## Control plane

Claude.ai (Project Officina) es el plano de control externo.
OpenCode ejecuta — Claude diseña y verifica.
Handoff via `executable-handoff` en instrucciones de tarea.
