# Restaura um backup .sql no banco Postgres do Ragnarok (container docker).
# Uso: .\scripts\restore.ps1 backups\ragnarok_20260606_090000.sql
param([Parameter(Mandatory=$true)][string]$Arquivo)
$ErrorActionPreference = "Stop"
if (-not (Test-Path $Arquivo)) { throw "Arquivo nao encontrado: $Arquivo" }

Write-Host "ATENCAO: isto sobrescreve os dados atuais do banco com o backup."
Write-Host "Restaurando de $Arquivo ..."
# pg_dump padrao inclui os comandos; aplicamos via psql.
Get-Content $Arquivo | docker compose exec -T db psql -U ragnarok -d ragnarok
Write-Host "Restauracao concluida."
