@echo off
setlocal

REM EasyFeet - Limpeza de artefatos de build
REM Remove pastas geradas automaticamente para forçar build limpo.

set "ROOT=%~dp0"
echo.
echo ============================================
echo  EasyFeet - Limpar artefatos de build
echo ============================================
echo.
echo Esta acao remove as pastas:
echo   - build
echo   - dist
echo   - release
echo   - __pycache__ (raiz)
echo.
set /p CONFIRMAR="Deseja continuar? (S/N): "
if /I not "%CONFIRMAR%"=="S" (
  echo Operacao cancelada.
  pause
  exit /b 0
)

if exist "%ROOT%build" (
  rmdir /s /q "%ROOT%build"
  echo [OK] Removido: build
) else (
  echo [INFO] Pasta nao existe: build
)

if exist "%ROOT%dist" (
  rmdir /s /q "%ROOT%dist"
  echo [OK] Removido: dist
) else (
  echo [INFO] Pasta nao existe: dist
)

if exist "%ROOT%release" (
  rmdir /s /q "%ROOT%release"
  echo [OK] Removido: release
) else (
  echo [INFO] Pasta nao existe: release
)

if exist "%ROOT%__pycache__" (
  rmdir /s /q "%ROOT%__pycache__"
  echo [OK] Removido: __pycache__
) else (
  echo [INFO] Pasta nao existe: __pycache__
)

echo.
echo Limpeza concluida.
echo.
pause
endlocal
