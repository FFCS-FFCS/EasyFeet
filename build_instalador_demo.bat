@echo off
setlocal

REM EasyFeet - Instalador DEMO com base de dados e ficheiros atuais (data/)
REM Uso: duplo clique neste .bat (feche EasyFeet antes de executar).

set "ROOT=%~dp0"
set "PS1=%ROOT%scripts\build_windows_installer.ps1"

if not exist "%PS1%" (
  echo [ERRO] Script nao encontrado: "%PS1%"
  pause
  exit /b 1
)

echo.
echo ============================================
echo  EasyFeet - Instalador DEMO (com dados)
echo ============================================
echo.
echo Inclui a pasta data\ actual (easyfeet.db, pacientes, regras).
echo Feche o EasyFeet se estiver aberto.
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File "%PS1%" -Demo
if errorlevel 1 (
  echo.
  echo [ERRO] Falha ao gerar instalador DEMO.
  pause
  exit /b 1
)

echo.
echo [OK] Instalador DEMO gerado.
echo   Instalador: "%ROOT%release\EasyFeet-Setup-DEMO-2.0.0.exe"
echo   ZIP portatil: "%ROOT%EasyFeet_DEMO_Com_Dados.zip"
echo.
pause
endlocal
