# OFFICINA Framework

Sistema personal de orquestación AI con memoria operacional persistente.

## Stack S32

```
PostgreSQL  → grafo + sesión + config (nodos system)
FastAPI     → motor cognitivo: T1 PUSH + T2 PULL + routing + auth
React       → UI dumb
Ollama      → modelos locales fallback
OpenCode    → WorkspaceRuntimeProvider
```

## Estructura

```
db/          → schemas SQL canónicos
fastapi/     → motor cognitivo (pipeline/ cognitive/ routers/ db/)
agents/      → Sleep Agent, Dreaming Agent, Document Agent
react/       → UI
mcp/         → MCP servers (postgres/)
scripts/     → utilidades operacionales
cognition/   → FUV operacional (ledger + infra + runtime docs)
docs/        → ADRs, governance, spec
secrets/     → .gitignore — nunca en repo
data/        → .gitignore — runtime data
```

## FUV operacional

- `cognition/operational-ledger.ndjson` — continuidad de sesión
- `cognition/officina-infra.md` — stack y arquitectura
- `cognition/officina-runtime-s28.md` — runtime turno a turno

## Arranque

```powershell
docker compose up -d
```

Ver `cognition/officina-infra.md` para configuración completa.

## Open Source Runtime Vision

OFFICINA is an AI-native framework for building cost-aware, multi-model operational systems.

It combines PostgreSQL, FastAPI, React, local models, coding agents, MCP servers, and an operational ledger to support reconstructable human-AI software development workflows.

The project explores how solo developers, technical founders, and small teams can coordinate local, open-source, low-cost, and premium AI models without hardcoding dependency on a single provider.

Premium models are intended to be used selectively for high-consequence work such as coding validation, adversarial review, complex reasoning, and persistent operational decisions.

A clean runtime component is also being prepared at:

https://github.com/pierangelopirro/officina-runtime-core




