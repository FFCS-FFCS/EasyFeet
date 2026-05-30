@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title EasyFeet - Criar snapshot ZIP

echo.
echo === EasyFeet - Criar snapshot (ZIP) ===
echo.
echo O ZIP vai para a pasta snapshots\
echo (codigo + docs; SEM data\ de pacientes)
echo.

set "VER=v1.0.0"
set /p VER="Versao para o nome do ficheiro [%VER%]: "
if "%VER%"=="" set "VER=v1.0.0"

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\criar_snapshot.ps1" -Version "%VER%"
if errorlevel 1 (
  echo.
  echo [ERRO] Falha ao criar snapshot.
  pause
  exit /b 1
)

echo.
pause
endlocal
