# EasyFeet — cria ZIP versionado em snapshots/ (sem data/ nem builds).
param(
    [string]$Version = "v1.0.0"
)

$ErrorActionPreference = "Stop"
$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$Date = Get-Date -Format "yyyy-MM-dd"
$SnapDir = Join-Path $Root "snapshots"
$SafeVer = ($Version -replace '[^\w\.\-]', '_')
$ZipName = "EasyFeet_${SafeVer}_${Date}.zip"
$ZipPath = Join-Path $SnapDir $ZipName

New-Item -ItemType Directory -Force -Path $SnapDir | Out-Null

$staging = Join-Path $env:TEMP ("EasyFeet_snapshot_" + [guid]::NewGuid().ToString("N").Substring(0, 8))
New-Item -ItemType Directory -Path $staging | Out-Null

try {
    $excludeDirs = @(
        "data", "build", "dist", "dist_new", "release",
        "__pycache__", ".git", "snapshots", ".venv", "venv", ".pytest_cache"
    )
    $xd = ($excludeDirs | ForEach-Object { "/XD", $_ }) -join " "
    $robocmd = "robocopy `"$Root`" `"$staging`" /E /XD $($excludeDirs -join ' ') /XF *.zip desktop.ini *.lnk /NFL /NDL /NJH /NJS /nc /ns /np"
    cmd /c $robocmd | Out-Null
    $rc = $LASTEXITCODE
    if ($rc -ge 8) {
        throw "robocopy falhou com codigo $rc"
    }

    if (Test-Path $ZipPath) {
        Remove-Item -Force $ZipPath
    }
    Compress-Archive -Path (Join-Path $staging "*") -DestinationPath $ZipPath -Force

    Write-Host ""
    Write-Host "Snapshot criado com sucesso:"
    Write-Host "  $ZipPath"
    Write-Host ""
    Write-Host "Para executar esta versao noutra pasta:"
    Write-Host "  1. Descompacte o ZIP numa pasta, ex.: EasyFeet_$SafeVer"
    Write-Host "  2. pip install -r requirements.txt"
    Write-Host "  3. Duplo clique em EF.bat"
    Write-Host ""
}
finally {
    if (Test-Path $staging) {
        Remove-Item -Recurse -Force $staging -ErrorAction SilentlyContinue
    }
}
