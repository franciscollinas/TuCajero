@echo off
chcp 65001 >nul 2>&1
setlocal EnableDelayedExpansion

echo ================================================
echo    TuCajero - Herramienta de Diagnóstico
echo ================================================
echo.

set "HAS_ISSUES=0"
set "DATA_DIR=%LOCALAPPDATA%\TuCajero"
set "DB_PATH=%DATA_DIR%\database\pos.db"
set "LOG_FILE=%DATA_DIR%\logs\app.log"

echo [1/5] Verificando directorio de datos...
if exist "%DATA_DIR%" (
    echo   OK: %DATA_DIR%
) else (
    echo   INFO: Primera instalación (no hay datos aún)
    echo.
    goto :summary
)
echo.

echo [2/5] Verificando base de datos...
if exist "%DB_PATH%" (
    for %%A in ("%DB_PATH%") do (
        set "DB_SIZE=%%~zA"
    )
    echo   OK: pos.db (Tamano: !DB_SIZE! bytes)
) else (
    echo   WARN: Base de datos no existe
    echo   INFO: Se creara al abrir la aplicacion
    set "HAS_ISSUES=1"
)
echo.

echo [3/5] Verificando archivos de bloqueo...
set "BLOCKED=0"

if exist "%DB_PATH%-wal" (
    for %%A in ("%DB_PATH%-wal") do set "WAL_SIZE=%%~zA"
    echo   WARN: Archivo WAL presente (!WAL_SIZE! bytes)
    set "BLOCKED=1"
    set "HAS_ISSUES=1"
)

if exist "%DB_PATH%-shm" (
    echo   WARN: Archivo SHM presente
    set "BLOCKED=1"
    set "HAS_ISSUES=1"
)

if "!BLOCKED!"=="0" (
    echo   OK: Sin archivos de bloqueo
)
echo.

echo [4/5] Verificando procesos...
tasklist /FI "IMAGENAME eq TuCajero.exe" 2>nul | find /I "TuCajero.exe" >nul
if !ERRORLEVEL!==0 (
    echo   WARN: TuCajero.exe esta corriendo
    set "HAS_ISSUES=1"
) else (
    echo   OK: TuCajero.exe no esta corriendo
)
echo.

echo [5/5] Verificando logs recientes...
if exist "%LOG_FILE%" (
    echo   OK: Log encontrado
    echo   --- Ultimas 10 lineas ---
    powershell -Command "Get-Content '%LOG_FILE%' -Tail 10 -ErrorAction SilentlyContinue"
) else (
    echo   INFO: Sin logs (primera ejecucion)
)
echo.

:summary
echo ================================================
echo                 RESULTADO
echo ================================================

if "%HAS_ISSUES%"=="1" (
    echo Estado: ATENCION NECESARIA
    echo.
    echo Se detectaron problemas que pueden impedir
    echo que TuCajero abra correctamente.
    echo.
    echo Opciones:
    echo   [1] Intentar reparacion automatica
    echo   [2] Mostrar ayuda
    echo   [3] Salir
    echo.
    set /p CHOICE="Seleccione opcion (1-3): "
    
    if "!CHOICE!"=="1" (
        echo.
        echo [REPARANDO] Iniciando...
        
        if exist "%DB_PATH%-wal" (
            echo   - Eliminando WAL...
            del /F /Q "%DB_PATH%-wal" 2>nul
        )
        
        if exist "%DB_PATH%-shm" (
            echo   - Eliminando SHM...
            del /F /Q "%DB_PATH%-shm" 2>nul
        )
        
        echo.
        echo REPARACION COMPLETADA
        echo.
        echo Puede intentar abrir TuCajero nuevamente.
    ) else if "!CHOICE!"=="2" (
        echo.
        echo --- AYUDA ---
        echo.
        echo Los archivos WAL/SHM se crean cuando TuCajero
        echo esta en ejecucion o no se cerro correctamente.
        echo.
        echo Si TuCajero no abre:
        echo   1. Cierre todos los procesos TuCajero.exe
        echo   2. Ejecute esta herramienta
        echo   3. Seleccione opcion 1 para reparar
        echo   4. Intente abrir TuCajero nuevamente
        echo.
    )
) else (
    echo Estado: OPERATIVO
    echo.
    echo No se detectaron problemas.
    echo TuCajero deberia funcionar correctamente.
)
echo.

endlocal
echo Presione cualquier tecla para salir...
pause >nul
