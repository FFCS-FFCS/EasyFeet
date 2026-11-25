param(
  [switch]$Demo
)

$ErrorActionPreference = "Stop"

$buildLabel = if ($Demo) { "EasyFeet build DEMO (com dados atuais)" } else { "EasyFeet build (Windows)" }
Write-Host "== $buildLabel ==" -ForegroundColor Cyan

$root = Split-Path -Parent $PSScriptRoot
$FORBIDDEN_ROOT = "C:\Cursor_Projetos\EasyFeet"
$rootNorm = [System.IO.Path]::GetFullPath($root).TrimEnd('\')
if ($rootNorm -ieq $FORBIDDEN_ROOT) {
  throw @"
Build bloqueado: pasta descontinuada ($FORBIDDEN_ROOT).
Abra o Cursor e execute build_instalador.bat apenas em:
C:\Users\flavi\OneDrive\Documentos\Ideias_Projetos\Cursor_Projetos\EasyFeet
"@
}
Set-Location $root

$distDir = Join-Path $root "dist"
$buildDir = Join-Path $root "build"
$releaseDir = Join-Path $root "release"
$bundleDir = Join-Path $distDir "EasyFeet"
$menuConfig = Join-Path $root "menu-config-v2.json"
$imagensDir = Join-Path $root "Imagens"
$helpLinhas = Join-Path $root "marcador_plantar\\help_plantar_pt.txt"
$helpPontos = Join-Path $root "marcador_pontos\\help_pontos_pt.txt"

if (Test-Path $buildDir) { Remove-Item $buildDir -Recurse -Force }
if (Test-Path $distDir) {
  try {
    Remove-Item $distDir -Recurse -Force -ErrorAction Stop
  } catch {
    Write-Host "AVISO: dist em uso; build em dist_new (feche EasyFeet/Word na pasta dist)." -ForegroundColor Yellow
    $distDir = Join-Path $root "dist_new"
    if (Test-Path $distDir) { Remove-Item $distDir -Recurse -Force }
  }
}
if (Test-Path $releaseDir) { Remove-Item $releaseDir -Recurse -Force }
New-Item -ItemType Directory -Path $releaseDir | Out-Null

Write-Host "1) Gerando EasyFeet.exe..." -ForegroundColor Yellow
python -m PyInstaller `
  --noconfirm `
  --windowed `
  --onedir `
  --name EasyFeet `
  --distpath "$distDir" `
  --workpath "$buildDir" `
  --specpath "$buildDir" `
  --add-data "$menuConfig;." `
  --add-data "$imagensDir;Imagens" `
  "$root\\easyfeet_main.py"
if ($LASTEXITCODE -ne 0) { throw "Falha ao gerar EasyFeet.exe" }

Write-Host "2) Gerando EFM_Marcadores.exe..." -ForegroundColor Yellow
python -m PyInstaller `
  --noconfirm `
  --windowed `
  --onedir `
  --name EFM_Marcadores `
  --distpath "$distDir" `
  --workpath "$buildDir" `
  --specpath "$buildDir" `
  --add-data "$helpLinhas;marcador_plantar" `
  --add-data "$helpPontos;marcador_pontos" `
  "$root\\EFM_Marcadores.py"
if ($LASTEXITCODE -ne 0) { throw "Falha ao gerar EFM_Marcadores.exe" }

Write-Host "3) Consolidando ficheiros no bundle EasyFeet..." -ForegroundColor Yellow
$efmDir = Join-Path $distDir "EFM_Marcadores"
if (-not (Test-Path $efmDir)) {
  throw "Pasta do EFM não encontrada: $efmDir"
}

# Copia os ficheiros de topo do EFM (ex.: EFM_Marcadores.exe).
Get-ChildItem $efmDir -File | ForEach-Object {
  Copy-Item $_.FullName -Destination (Join-Path $bundleDir $_.Name) -Force
}

# Junta o conteúdo interno do EFM dentro de dist/EasyFeet/_internal
# sem criar o aninhamento _internal/_internal.
$bundleInternal = Join-Path $bundleDir "_internal"
$efmInternal = Join-Path $efmDir "_internal"
if (-not (Test-Path $bundleInternal)) { New-Item -ItemType Directory -Path $bundleInternal | Out-Null }
if (Test-Path $efmInternal) {
  Get-ChildItem $efmInternal | ForEach-Object {
    Copy-Item $_.FullName -Destination $bundleInternal -Recurse -Force
  }
}

# Copia a pasta data do projeto (BD, regras, imagens) para o bundle instalável
$srcData = Join-Path $root "data"
if (-not (Test-Path $srcData)) {
  throw "Pasta data do projeto nao encontrada: $srcData"
}
$destData = Join-Path $bundleDir "data"
if (Test-Path $destData) { Remove-Item $destData -Recurse -Force }
Copy-Item $srcData -Destination $bundleDir -Recurse -Force
$dbPath = Join-Path $destData "easyfeet.db"
if (-not (Test-Path $dbPath)) {
  throw "Base de dados nao copiada para o bundle: $dbPath"
}
$dbSize = (Get-Item $dbPath).Length
Write-Host "   data/ copiada (easyfeet.db: $dbSize bytes)" -ForegroundColor DarkGray

Write-Host "4) Compilando instalador Inno Setup..." -ForegroundColor Yellow
$iscc = Get-Command iscc -ErrorAction SilentlyContinue
if (-not $iscc) {
  $commonPaths = @(
    "$Env:ProgramFiles(x86)\Inno Setup 6\ISCC.exe",
    "$Env:ProgramFiles\Inno Setup 6\ISCC.exe",
    "$Env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe"
  )
  foreach ($p in $commonPaths) {
    if (Test-Path $p) {
      $iscc = @{ Source = $p }
      break
    }
  }
}
if (-not $iscc) {
  throw "Inno Setup (iscc) não encontrado no PATH nem nas pastas padrão."
}

$appVersion = "2.0.0"
$versionPy = Join-Path $root "easyfeet\version.py"
if (Test-Path $versionPy) {
  $verMatch = Select-String -Path $versionPy -Pattern 'APP_VERSION\s*=\s*"([^"]+)"' | Select-Object -First 1
  if ($verMatch) { $appVersion = $verMatch.Matches[0].Groups[1].Value }
}

$distBundleRel = if ($distDir -like "*dist_new*") { "..\dist_new\EasyFeet" } else { "..\dist\EasyFeet" }
$issArgs = @(
  "/DMyAppVersion=$appVersion",
  "/DDistBundle=$distBundleRel",
  "scripts\easyfeet_installer.iss"
)
if ($Demo) {
  $demoOutput = "EasyFeet-Setup-DEMO-$appVersion"
  $issArgs = @(
    "/DMyAppVersion=$appVersion",
    '/DMyAppName=EasyFeet (DEMO)',
    "/DOutputBaseFilename=$demoOutput",
    "/DDistBundle=$distBundleRel",
    "scripts\easyfeet_installer.iss"
  )
  Write-Host "   Modo DEMO: instalador $demoOutput.exe (inclui data/ atual)" -ForegroundColor DarkGray
}
& $iscc.Source @issArgs

$zipName = if ($Demo) { "EasyFeet_DEMO_Com_Dados.zip" } else { "EasyFeet_Com_Dados.zip" }
$zipPath = Join-Path $root $zipName
if (Test-Path $zipPath) { Remove-Item $zipPath -Force }
Write-Host "5) Criando ZIP portatil ($zipName)..." -ForegroundColor Yellow
try {
  Compress-Archive -Path $bundleDir -DestinationPath $zipPath -Force
} catch {
  Write-Host "AVISO: ZIP nao criado (ficheiros em uso). Instalador .exe ja esta em release\." -ForegroundColor Yellow
}

Write-Host "Build concluído." -ForegroundColor Green
Write-Host "Pasta dist: $bundleDir"
Write-Host "Instalador em: $releaseDir"
Write-Host "ZIP portatil: $zipPath"
