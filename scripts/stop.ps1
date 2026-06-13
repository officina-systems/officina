# scripts/stop.ps1
# Detener OFFICINA Framework
#
# Uso: .\scripts\stop.ps1

docker compose down
Write-Host "Stack detenido." -ForegroundColor Cyan
