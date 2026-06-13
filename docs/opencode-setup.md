# OpenCode — Setup y ubicacion

## Instalacion

- **Tipo:** local dentro de `officina/` via npm
- **Binario:** `officina/node_modules/.bin/opencode`
- **Ejecutar siempre con:** `npx opencode` desde raiz de `officina/`
- **Version instalada:** 1.16.2

## BD SQLite — excepcion documentada

OpenCode usa SQLite fijo internamente para sesiones de coding.
No es configurable a PostgreSQL (hardcodeado en el binario).

**Justificacion excepcion:**
- Componente externo — no modificable
- Almacena sesiones de coding efimeras, no conocimiento operacional del grafo
- No rompe ningun invariante de PostgreSQL como FUV

**Redireccion via XDG** (ver abajo) mueve el SQLite dentro de `officina/.opencode/data/`
cumpliendo el principio de ubicacion dentro del directorio.

## Paths en runtime

```
BD SQLite:  officina/.opencode/data/opencode/opencode.db
Config:     officina/.opencode/config/opencode/opencode.jsonc
Logs:       officina/.opencode/data/opencode/log/
Repos:      officina/.opencode/data/opencode/repos/
```

Paths NO redirigibles (aceptado — caches del SO):
```
bin:    C:\Users\Home\.cache\opencode\bin
cache:  C:\Users\Home\.cache\opencode
state:  C:\Users\Home\.local\state\opencode
tmp:    %TEMP%\opencode
```

## Variables de entorno requeridas

Deben estar en el perfil de PowerShell (`$PROFILE`) para que persistan:

```powershell
# Agregar a $PROFILE (ejecutar: notepad $PROFILE)
$env:XDG_DATA_HOME   = "C:\Users\Home\officina\.opencode\data"
$env:XDG_CONFIG_HOME = "C:\Users\Home\officina\.opencode\config"
```

## Cognitive Provider

OpenCode apunta a FastAPI como proveedor de inferencia:
- `baseURL: http://localhost:8000/v1`
- `apiKey:` desde `.env` → `FASTAPI_API_KEY` (provisional)
- Modelo default: `openai/officina-primary`

FastAPI cognitive router maneja el fallback:
`Vertex gemini-2.5-flash → Groq → NVIDIA → OpenRouter → Ollama`

## Configuracion final (pendiente P3 — runtime analysis)

- Conectar `apiKey` desde Bitwarden
- Validar que `/v1/models` y `/v1/chat/completions` responden correctamente
- Registrar nodo system `opencode-config` en PostgreSQL
