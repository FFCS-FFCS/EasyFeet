@echo off
setlocal

REM Converte um arquivo .md para .docx usando Pandoc
REM Uso:
REM   1) Duplo clique e informe o nome do arquivo .md
REM   2) ou: converter_md_para_docx.bat 2026-05-07-visao-geral-e-registro-evolutivo.md

set "DIR=%~dp0"
set "PANDOC_CMD=pandoc"

where pandoc >nul 2>nul
if errorlevel 1 (
  if exist "%LOCALAPPDATA%\Pandoc\pandoc.exe" (
    set "PANDOC_CMD=%LOCALAPPDATA%\Pandoc\pandoc.exe"
  ) else (
    echo [ERRO] Pandoc nao encontrado.
    echo Instale com:
    echo   winget install --id JohnMacFarlane.Pandoc --exact --silent
    pause
    exit /b 1
  )
)

if "%~1"=="" (
  echo Arquivos .md disponiveis:
  dir /b "%DIR%*.md"
  echo.
  set /p "MD=Digite o nome do .md (com extensao): "
) else (
  set "MD=%~1"
)

if not exist "%DIR%%MD%" (
  echo [ERRO] Arquivo nao encontrado: "%DIR%%MD%"
  pause
  exit /b 1
)

set "OUT=%MD:.md=.docx%"
"%PANDOC_CMD%" "%DIR%%MD%" -o "%DIR%%OUT%"
if errorlevel 1 (
  echo [ERRO] Falha ao converter.
  pause
  exit /b 1
)

echo [OK] Gerado: "%DIR%%OUT%"
pause
endlocal
