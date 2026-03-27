@echo off
echo ========================================
echo TuCajero - Ver Logs en Tiempo Real
echo ========================================
echo.
echo Presiona Ctrl+C para salir
echo.
echo [LOGS] %LOCALAPPDATA%\TuCajero\logs\app.log
echo.
tail -f "%LOCALAPPDATA%\TuCajero\logs\app.log" 2>nul || powershell -Command "Get-Content '%LOCALAPPDATA%\TuCajero\logs\app.log' -Wait -Tail 50"
