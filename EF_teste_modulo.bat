@echo off
setlocal EnableExtensions

REM EasyFeet — protótipo módulo marcadores (barra de ações centralizada)
REM Pasta oficial: OneDrive\...\Cursor_Projetos\EasyFeet

cd /d "%~dp0"
title EasyFeet - Teste modulo marcadores

if not exist "teste_modulo_marcadores.py" (
  echo [ERRO] Ficheiro nao encontrado nesta pasta:
  echo   %CD%\teste_modulo_marcadores.py
  echo.
  echo Abra o projeto em:
  echo   C:\Users\flavi\OneDrive\Documentos\Ideias_Projetos\Cursor_Projetos\EasyFeet
  pause
  exit /b 1
)

python teste_modulo_marcadores.py
if errorlevel 1 (
  echo.
  echo [ERRO] Nao foi possivel iniciar o teste. Verifique Python e: pip install -r requirements.txt
  echo Pasta: %CD%
  pause
  exit /b 1
)

endlocal
