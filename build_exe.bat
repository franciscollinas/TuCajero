@echo off
echo ========================================
echo TuCajero - Build EXE
echo ========================================
echo.

echo [1/3] Limpiando builds anteriores...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
echo [2/3] Compilando con PyInstaller...
call venv\Scripts\activate
pyinstaller --noconfirm TuCajero.spec
deactivate

echo [3/3] Moviendo EXE...
if exist "dist\TuCajero.exe" (
    echo   EXE: dist\TuCajero.exe
)

echo.
echo ========================================
echo Build completado!
echo ========================================
dir dist\ /b
echo.
pause
