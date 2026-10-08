$ErrorActionPreference = 'Stop'
$taskRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$envPath = Join-Path $taskRoot '.env'
if (Test-Path -LiteralPath $envPath) {
    Write-Host '.env already exists; preserved.'
    exit 0
}
$randomBytes = New-Object byte[] 24
$rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
$rng.GetBytes($randomBytes)
$rng.Dispose()
$taskPassword = [BitConverter]::ToString($randomBytes).Replace('-', '').ToLowerInvariant()
$example = [System.IO.File]::ReadAllText((Join-Path $taskRoot '.env.example'))
[System.IO.File]::WriteAllText($envPath, $example.Replace('replace-with-random-local-password', $taskPassword), (New-Object System.Text.UTF8Encoding $false))
Write-Host 'Created .env with a random database password. SEC_USER_AGENT still needs your contact email.'
