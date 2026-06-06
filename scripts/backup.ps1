# Backup do banco Postgres do Ragnarok (container docker).
# Uso: .\scripts\backup.ps1   -> gera backups\ragnarok_<timestamp>.sql
$ErrorActionPreference = "Stop"
$stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$dir = "backups"
if (-not (Test-Path $dir)) { New-Item -ItemType Directory $dir | Out-Null }
$arquivo = "$dir\ragnarok_$stamp.sql"

Write-Host "Gerando backup em $arquivo ..."
docker compose exec -T db pg_dump -U ragnarok ragnarok | Out-File -Encoding utf8 $arquivo
Write-Host "Backup concluido: $arquivo"
Write-Host "Para restaurar:  .\scripts\restore.ps1 $arquivo"
