param([Parameter(Mandatory=$true)][string]$BackupFile)
$ErrorActionPreference = 'Stop'
$labRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$labBackup = (Resolve-Path -LiteralPath $BackupFile).Path
$labNetwork = 'industryflow-reading'
$labPassword = [guid]::NewGuid().ToString('N')
function Invoke-LabDocker {
    param([string[]]$Arguments)
    & docker @Arguments
    if ($LASTEXITCODE -ne 0) { throw ('Docker failed: ' + $Arguments[0]) }
}
Push-Location $labRoot
try {
    foreach ($labName in @('industryflow-reading-db','industryflow-reading-api','industryflow-reading-web')) {
        $labExisting = & docker ps -aq --filter "name=^/$labName$"
        if ($labExisting) { throw "Lab container already exists: $labName. Reuse it or explicitly remove that lab only." }
    }
    $labApiImage = & docker image inspect industryflow-api:local --format '{{.Id}}'
    if ($LASTEXITCODE -ne 0) { throw 'API image unavailable' }
    $labWebImage = & docker image inspect industryflow-web:local --format '{{.Id}}'
    if ($LASTEXITCODE -ne 0) { throw 'Web image unavailable' }
    Invoke-LabDocker -Arguments @('tag',$labApiImage,'industryflow-reading-api:baseline')
    Invoke-LabDocker -Arguments @('tag',$labWebImage,'industryflow-reading-web:baseline')
    $labNetworks = & docker network ls --format '{{.Name}}'
    if ($labNetworks -notcontains $labNetwork) { Invoke-LabDocker -Arguments @('network','create',$labNetwork) }
    Invoke-LabDocker -Arguments @('run','-d','--name','industryflow-reading-db','--network',$labNetwork,'-e',"POSTGRES_PASSWORD=$labPassword",'-e','POSTGRES_USER=industry','-e','POSTGRES_DB=industry_reading','postgres:16.15-trixie')
    $labReady = $false
    for ($labAttempt=0; $labAttempt -lt 30; $labAttempt++) {
        & docker exec industryflow-reading-db pg_isready -U industry -d industry_reading 2>$null | Out-Null
        if ($LASTEXITCODE -eq 0) { $labReady=$true; break }
        Start-Sleep -Seconds 1
    }
    if (-not $labReady) { throw 'Lab PostgreSQL did not start' }
    Invoke-LabDocker -Arguments @('cp',$labBackup,'industryflow-reading-db:/tmp/baseline.dump')
    Invoke-LabDocker -Arguments @('exec','industryflow-reading-db','pg_restore','-U','industry','-d','industry_reading','--exit-on-error','/tmp/baseline.dump')
    Invoke-LabDocker -Arguments @('run','-d','--init','--name','industryflow-reading-api','--network',$labNetwork,'-p','127.0.0.1:8013:8000','-e',"DATABASE_URL=postgresql+psycopg://industry:${labPassword}@industryflow-reading-db:5432/industry_reading",$labApiImage)
    Invoke-LabDocker -Arguments @('run','-d','--init','--name','industryflow-reading-web','--network',$labNetwork,'-p','127.0.0.1:3013:3010','-e','API_ORIGIN=http://industryflow-reading-api:8000',$labWebImage)
    Write-Host 'Isolated lab: web http://127.0.0.1:3013; API http://127.0.0.1:8013. No worker or external ingestion.'
    Write-Host "Baseline images: $labApiImage / $labWebImage"
} finally { Pop-Location }
