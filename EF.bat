@echo off
setlocal EnableExtensions

REM EasyFeet — app principal (Python, pasta deste .bat)
REM Pasta oficial: OneDrive\...\Cursor_Projetos\EasyFeet

cd /d "%~dp0"
title EasyFeet

if not exist "easyfeet_main.py" (
  echo [ERRO] Nao encontrei "easyfeet_main.py" nesta pasta:
  echo   %CD%
  echo.
  echo Abra o projeto em:
  echo   C:\Users\flavi\OneDrive\Documentos\Ideias_Projetos\Cursor_Projetos\EasyFeet
  pause
  exit /b 1
)

where py >nul 2>nul
if %errorlevel%==0 (
  py -3 "easyfeet_main.py"
) else (
  python "easyfeet_main.py"
)

if errorlevel 1 (
  echo.
  echo [ERRO] Falha ao executar o EasyFeet. Verifique: pip install -r requirements.txt
  echo Pasta: %CD%
  pause
  exit /b 1
)

endlocal
