# scripts/init_dirs.ps1
# Crea directorios de runtime necesarios que no van en Git
# Ejecutar una vez al clonar el repo en un host nuevo
#
# Uso: .\scripts\init_dirs.ps1

$base = $PSScriptRoot | Split-Path

$dirs = @(
    "$base\data\postgres",
    "$base\data\ollama",
    "$base\data\uploads",
    "$base\data\watch",
    "$base\.opencode\data",
    "$base\.opencode\config"
)

foreach ($d in $dirs) {
    New-Item -ItemType Directory -Force -Path $d | Out-Null
    Write-Host "OK: $d" -ForegroundColor Green
}

Write-Host "`nDirectorios de runtime inicializados." -ForegroundColor Cyan
Write-Host "Recuerda agregar las variables XDG a tu perfil PowerShell:" -ForegroundColor Yellow
Write-Host "  notepad `$PROFILE" -ForegroundColor Yellow
