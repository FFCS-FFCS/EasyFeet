@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"
title EasyFeet - Marcar versao (Git + ZIP)

where git >nul 2>nul
if errorlevel 1 (
  echo [ERRO] Git nao encontrado. Instale Git for Windows.
  pause
  exit /b 1
)

echo.
echo === EasyFeet - Marcar versao ===
echo.
echo 1. Grava alteracoes no Git local (commit)
echo 2. Cria uma tag (ex.: v1.1.0)
echo 3. Gera snapshot ZIP em snapshots\
echo.

set "VER="
set /p VER="Nome da versao/tag (ex. v1.1.0): "
if "%VER%"=="" (
  echo [ERRO] Versao obrigatoria.
  pause
  exit /b 1
)

git add -A
echo.
echo --- Alteracoes preparadas ---
git status -sb
echo.

set "DO_COMMIT=S"
set /p DO_COMMIT="Fazer commit agora? [S/N] (%DO_COMMIT%): "
if /i "%DO_COMMIT%"=="S" (
  set "MSG=release: EasyFeet %VER%"
  set /p MSG="Mensagem do commit [%MSG%]: "
  git commit -m "%MSG%"
  if errorlevel 1 (
    echo (Nenhum commit novo ou commit cancelado — continuando para tag...)
  )
)

git tag -l "%VER%" >nul 2>nul
for /f %%A in ('git tag -l "%VER%"') do set "TAG_EXISTS=1"
if defined TAG_EXISTS (
  echo.
  echo [AVISO] A tag %VER% ja existe.
  set /p RETAG="Substituir tag? [S/N]: "
  if /i "!RETAG!"=="S" (
    git tag -d "%VER%"
    git tag -a "%VER%" -m "EasyFeet %VER%"
  )
) else (
  git tag -a "%VER%" -m "EasyFeet %VER%"
)

echo.
echo Tag criada/confirmada: %VER%
git tag -l "%VER%"
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\criar_snapshot.ps1" -Version "%VER%"

echo.
echo Concluido. Ver MDs\versionamento-local-easyfeet.md para voltar a esta versao.
pause
endlocal
