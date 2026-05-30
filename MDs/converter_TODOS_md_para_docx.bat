@echo off
setlocal

REM Converte todos os arquivos .md da pasta atual para .docx

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

echo Convertendo todos os .md em "%DIR%"...
set "COUNT=0"

for %%F in ("%DIR%*.md") do (
  set /a COUNT+=1
  set "OUT=%%~dpnF.docx"
  echo - %%~nxF  ^>  %%~nF.docx
  "%PANDOC_CMD%" "%%~fF" -o "%%~dpnF.docx"
  if errorlevel 1 (
    echo [ERRO] Falha na conversao de %%~nxF
  )
)

if "%COUNT%"=="0" (
  echo [INFO] Nenhum arquivo .md encontrado.
) else (
  echo [OK] Conversao concluida.
)

pause
endlocal
