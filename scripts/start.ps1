param(
  [switch]$Build
)

Write-Host "Starting OFFICINA local stack..."

if ($Build) {
  docker compose build
}

docker compose up
