# OFFICINA Framework — Scripts

## init_dirs.ps1
Crea directorios de runtime necesarios al clonar en host nuevo.
```powershell
.\scripts\init_dirs.ps1
```

## start.ps1
Arranca el stack resolviendo secrets desde Bitwarden.
```powershell
$s = bw unlock --raw
bw sync --session $s
.\scripts\start.ps1 -BwSession $s
```
No requiere `.env` para secrets. Lee desde Bitwarden directamente.
Limpia variables de memoria al terminar.

**Estado:** provisional. Cuando `p-dotenv-bitwarden-only` se implemente,
este script será el arranque canónico permanente.

## stop.ps1
Detiene el stack.
```powershell
.\scripts\stop.ps1
```

## Bitwarden entries requeridas
```
officina-postgres-password
officina-fastapi-api-key
groq-api-key
nvidia-api-key
openrouter-api-key
```
Folder: `02-Proyectos/officina/`

## Excepción documentada — Vertex AI SA JSON
El archivo `secrets/vertex-service-account.json` debe existir
en filesystem (requisito técnico de Google Auth — no es configurable como
variable de texto). Bind-mount `:ro` en FastAPI. Path documentado en
Bitwarden.
