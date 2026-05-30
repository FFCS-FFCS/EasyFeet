@echo off
setlocal

REM EasyFeet - Build automatizado do instalador (Windows)
REM Uso: duplo clique neste .bat ou execute no CMD.

set "ROOT=%~dp0"
set "PS1=%ROOT%scripts\build_windows_installer.ps1"

if not exist "%PS1%" (
  echo [ERRO] Script nao encontrado: "%PS1%"
  pause
  exit /b 1
)

echo.
echo ============================================
echo  EasyFeet - Gerar instalador
echo ============================================
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File "%PS1%"
if errorlevel 1 (
  echo.
  echo [ERRO] Falha ao gerar instalador.
  pause
  exit /b 1
)

echo.
echo [OK] Instalador gerado com sucesso.
echo Verifique a pasta: "%ROOT%release"
echo.
pause
endlocal
