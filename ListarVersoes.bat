@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title EasyFeet - Versoes guardadas

echo.
echo === Tags Git (versoes no historico) ===
git tag -l 2>nul
if errorlevel 1 echo (Git indisponivel ou sem tags)

echo.
echo === Snapshots ZIP ===
if exist "snapshots\*.zip" (
  dir /b /o-d "snapshots\*.zip"
) else (
  echo (Nenhum ZIP em snapshots\ — use CriarSnapshot.bat)
)

echo.
echo Guia completo: MDs\versionamento-local-easyfeet.md
pause
endlocal
