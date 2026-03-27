@echo off
setlocal enabledelayedexpansion

echo ========================================
echo TuCajero - Ejecutar con Debug
echo ========================================
echo.

set LOGFILE="%TEMP%\tucajero_debug_%date:~-4,4%%date:~-7,2%%date:~-10,2%.txt"

echo Ejecutando TuCajero.exe...
echo Logs en: %LOGFILE%
echo.

start /wait "" "dist\TuCajero.exe"
set EXITCODE=%ERRORLEVEL%

echo.
echo ========================================
echo Resultado: Exit Code = %EXITCODE%
echo ========================================

if exist %LOCALAPPDATA%\TuCajero\logs\app.log (
    echo.
    echo === ULTIMOS 50 LOGS ===
    powershell -Command "Get-Content '%LOCALAPPDATA%\TuCajero\logs\app.log' -Tail 50"
)

if %EXITCODE% neq 0 (
    echo.
    echo === ERROR DETECTADO ===
    echo Codigo de error: %EXITCODE%
    echo.
    echo Si la aplicacion no inicio, revisa:
    echo 1. Que tengas Python instalado
    echo 2. Que los archivos de la BD existan
    echo 3. Los logs en: %%LOCALAPPDATA%%\TuCajero\logs\app.log
)

echo.
pause
