# scripts/start.ps1
# Arranque OFFICINA Framework
# Prerequisito: .env con BW_CLIENTID, BW_CLIENTSECRET, BW_PASSWORD, POSTGRES_PASSWORD
# Bitwarden CLI 2026.5.0 en node_modules/.bin/bw
#
# Uso: .\scripts\start.ps1

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$bw = ".\node_modules\.bin\bw"

Write-Host "OFFICINA start" -ForegroundColor Cyan

# Leer bootstrap desde .env
function Get-EnvVar([string]$name) {
    $line = Get-Content .env | Select-String "^$name=" | Select-Object -First 1
    if (-not $line) { throw "Variable $name no encontrada en .env" }
    return $line.ToString().Split("=", 2)[1]
}

$env:BW_CLIENTID     = Get-EnvVar "BW_CLIENTID"
$env:BW_CLIENTSECRET = Get-EnvVar "BW_CLIENTSECRET"
$env:BW_PASSWORD     = Get-EnvVar "BW_PASSWORD"
$env:POSTGRES_PASSWORD = Get-EnvVar "POSTGRES_PASSWORD"

try {
    # Login y unlock Bitwarden
    Write-Host "Bitwarden login..." -ForegroundColor Yellow
    & $bw logout 2>$null
    & $bw login --apikey
    $env:BW_SESSION = & $bw unlock --passwordenv BW_PASSWORD --raw
    $env:BW_PASSWORD = ""
    Write-Host "Vault desbloqueado. Token: $($env:BW_SESSION.Length) chars" -ForegroundColor Green

    # Sync y resolver secrets
    & $bw sync --session $env:BW_SESSION 2>$null
    $item = & $bw get item "officina_secrets" --session $env:BW_SESSION | ConvertFrom-Json
    $fields = $item.fields

    function Get-Field([string]$name) {
        $val = ($fields | Where-Object name -eq $name).value
        if (-not $val) { throw "Campo '$name' no encontrado en officina_secrets" }
        return $val
    }

    $env:FASTAPI_API_KEY    = Get-Field "FASTAPI_API_KEY"
    $env:GROQ_API_KEY       = Get-Field "GROQ_API_KEY"
    $env:NVIDIA_NIM_API_KEY = Get-Field "NVIDIA_NIM_API_KEY"
    $env:OPENROUTER_API_KEY = Get-Field "OPENROUTER_API_KEY"
    $env:DATABASE_URL       = "postgresql://officina:$($env:POSTGRES_PASSWORD)@postgres:5432/officina"

    Write-Host "Secrets resueltos." -ForegroundColor Green

    # Arrancar stack
    docker compose up -d
    Start-Sleep -Seconds 3
    $health = curl -s http://localhost:8000/health 2>$null
    Write-Host "FastAPI health: $health" -ForegroundColor Cyan

} finally {
    $env:BW_CLIENTID     = ""
    $env:BW_CLIENTSECRET = ""
    $env:BW_PASSWORD     = ""
    $env:BW_SESSION      = ""
    $env:FASTAPI_API_KEY    = ""
    $env:GROQ_API_KEY       = ""
    $env:NVIDIA_NIM_API_KEY = ""
    $env:OPENROUTER_API_KEY = ""
    $env:DATABASE_URL       = ""
    Write-Host "Variables limpiadas." -ForegroundColor Gray
}
