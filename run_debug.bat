@echo off
echo ========================================
echo TuCajero - Ejecucion con debug
echo ========================================
echo.
cd /d "%~dp0dist"
echo Ejecutando TuCajero.exe...
echo.
TuCajero.exe
echo.
echo Codigo de error: %ERRORLEVEL%
echo.
pause
