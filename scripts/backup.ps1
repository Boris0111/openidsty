$ErrorActionPreference = 'Stop'
$taskRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
Push-Location $taskRoot
try {
    $backupDir = Join-Path $taskRoot 'backups'
    New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
    $destination = Join-Path $backupDir ('industry-' + (Get-Date -Format 'yyyyMMdd-HHmmss') + '.dump')
    & docker compose exec -T db sh -c 'pg_dump -U industry -d "$POSTGRES_DB" -Fc -f /tmp/industry-backup.dump'
    if ($LASTEXITCODE -ne 0) { throw 'pg_dump failed' }
    & docker compose cp db:/tmp/industry-backup.dump $destination
    if ($LASTEXITCODE -ne 0) { throw 'Backup copy failed' }
    Write-Host ('Backup: ' + $destination)
    Get-FileHash -LiteralPath $destination -Algorithm SHA256
} finally { Pop-Location }
