@echo off
echo ========================================
echo TuCajeroPOS - Sistema de Punto de Venta
echo ========================================
echo.
echo Iniciando aplicacion...
echo.

cd /d "%~dp0dist"
start TuCajero.exe

echo Aplicacion iniciada.
echo.
echo Para cerrar la aplicacion:
echo 1. Cierra la ventana de TuCajeroPOS
echo 2. O presiona Ctrl+C en esta ventana
echo.
pause
