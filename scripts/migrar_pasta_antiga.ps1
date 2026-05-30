# EasyFeet — sincroniza pasta antiga -> pasta OneDrive + chats do Cursor
# Executar com Cursor e EasyFeet FECHADOS para evitar "sharing violation".

$ErrorActionPreference = "Stop"

$oldRepo = "C:\Cursor_Projetos\EasyFeet"
$newRepo = "C:\Users\flavi\OneDrive\Documentos\Ideias_Projetos\Cursor_Projetos\EasyFeet"
$oldCursor = "C:\Users\flavi\.cursor\projects\c-Cursor-Projetos-EasyFeet"
$newCursor = "C:\Users\flavi\.cursor\projects\c-Users-flavi-OneDrive-Documentos-Ideias-Projetos-Cursor-Projetos-EasyFeet"

if (-not (Test-Path $newRepo)) {
    throw "Pasta nova nao encontrada: $newRepo"
}

Write-Host "1) Sincronizar codigo/dados do repositorio (ignora build/.venv)..." -ForegroundColor Cyan
if (Test-Path $oldRepo) {
    robocopy $oldRepo $newRepo /E /XO /R:2 /W:2 `
        /XD "__pycache__" ".venv" "build" ".git" `
        /NFL /NDL /NP | Out-Null
} else {
    Write-Host "   Pasta antiga do repo nao existe; pulando." -ForegroundColor Yellow
}

Write-Host "2) Copiar historico Cursor (chats, assets, terminals)..." -ForegroundColor Cyan
if (Test-Path $oldCursor) {
    foreach ($sub in @("agent-transcripts", "agent-tools", "assets", "terminals")) {
        $src = Join-Path $oldCursor $sub
        if (-not (Test-Path $src)) { continue }
        $dst = Join-Path $newCursor $sub
        New-Item -ItemType Directory -Path $dst -Force | Out-Null
        robocopy $src $dst /E /XC /XN /R:2 /W:2 /NFL /NDL /NP | Out-Null
        Write-Host "   OK: $sub"
    }
} else {
    Write-Host "   Projeto Cursor antigo nao encontrado; pulando." -ForegroundColor Yellow
}

Write-Host "3) Normalizar marker_rules.json (caminhos relativos)..." -ForegroundColor Cyan
Set-Location $newRepo
python -c "from easyfeet.marker_rules_store import MarkerRuleStore; MarkerRuleStore(); print('marker_rules OK')"

Write-Host ""
Write-Host "Concluido. Abra o Cursor apenas em:" -ForegroundColor Green
Write-Host $newRepo
Write-Host ""
Write-Host "Para renomear/apagar a pasta antiga, feche Cursor, EasyFeet.exe e aguarde OneDrive." -ForegroundColor Yellow
