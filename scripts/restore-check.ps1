param([Parameter(Mandatory=$true)][string]$BackupFile)
$ErrorActionPreference = 'Stop'
$taskRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$resolvedBackup = (Resolve-Path -LiteralPath $BackupFile).Path
if ([System.IO.Path]::GetExtension($resolvedBackup) -ne '.dump') { throw 'Expected a pg_dump .dump file' }
$restoreDb = 'industry_restore_' + (Get-Date -Format 'yyyyMMddHHmmss')
if ($restoreDb -notmatch '^industry_restore_[0-9]{14}$') { throw 'Invalid restore database name' }
Push-Location $taskRoot
try {
    & docker compose exec -T db createdb -U industry $restoreDb
    if ($LASTEXITCODE -ne 0) { throw 'Could not create isolated restore database' }
    & docker compose cp $resolvedBackup db:/tmp/industry-restore.dump
    if ($LASTEXITCODE -ne 0) { throw 'Backup copy failed' }
    & docker compose exec -T db pg_restore -U industry -d $restoreDb --exit-on-error /tmp/industry-restore.dump
    if ($LASTEXITCODE -ne 0) { throw 'Restore failed; application database untouched' }
    & docker compose exec -T db psql -U industry -d $restoreDb -c "SELECT 'segments' AS kind, count(*) FROM segments UNION ALL SELECT 'companies',count(*) FROM companies UNION ALL SELECT 'events',count(*) FROM events UNION ALL SELECT 'financials',count(*) FROM financials;"
    if ($LASTEXITCODE -ne 0) { throw 'Restore verification failed' }
    Write-Host ('Verified isolated database: ' + $restoreDb + '; original industry database untouched.')
} finally { Pop-Location }
