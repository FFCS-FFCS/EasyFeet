@echo off
setlocal EnableExtensions

REM EasyFeet — protótipo dashboard (total pacientes + ultimos 3 cadastros)
REM Pasta oficial: OneDrive\...\Cursor_Projetos\EasyFeet

cd /d "%~dp0"
title EasyFeet - Teste dashboard

if not exist "teste_dashboard.py" (
  echo [ERRO] Ficheiro nao encontrado nesta pasta:
  echo   %CD%\teste_dashboard.py
  echo.
  echo Abra o projeto em:
  echo   C:\Users\flavi\OneDrive\Documentos\Ideias_Projetos\Cursor_Projetos\EasyFeet
  pause
  exit /b 1
)

python teste_dashboard.py
if errorlevel 1 (
  echo.
  echo [ERRO] Nao foi possivel iniciar o teste. Verifique Python e: pip install -r requirements.txt
  echo Pasta: %CD%
  pause
  exit /b 1
)

endlocal
