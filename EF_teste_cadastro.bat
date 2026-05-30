@echo off
setlocal EnableExtensions

REM EasyFeet — protótipo cadastro (altura, peso, IMC, lateralidade)
REM Pasta oficial: OneDrive\...\Cursor_Projetos\EasyFeet

cd /d "%~dp0"
title EasyFeet - Teste cadastro paciente

if not exist "teste_cadastro_paciente_extendido.py" (
  echo [ERRO] Ficheiro nao encontrado nesta pasta:
  echo   %CD%\teste_cadastro_paciente_extendido.py
  echo.
  echo Abra o projeto em:
  echo   C:\Users\flavi\OneDrive\Documentos\Ideias_Projetos\Cursor_Projetos\EasyFeet
  pause
  exit /b 1
)

python teste_cadastro_paciente_extendido.py
if errorlevel 1 (
  echo.
  echo [ERRO] Nao foi possivel iniciar o teste. Verifique Python e: pip install -r requirements.txt
  echo Pasta: %CD%
  pause
  exit /b 1
)

endlocal
