@echo off
setlocal enabledelayedexpansion

echo ========================================
echo TuCajero - Build Process
echo ========================================
echo.

REM ========================================
REM CONFIGURACION DE LA TIENDA
REM ========================================
set STORE_NAME=Farmacia CruzMedic
set STORE_LOGO=
set STORE_ADDRESS=Calle 10 #22-15
set STORE_PHONE=+57 300 123 4567
set STORE_NIT=901234567
REM ========================================

echo Configuracion de la tienda:
echo   Nombre: %STORE_NAME%
echo   Logo: %STORE_LOGO%
echo   Direccion: %STORE_ADDRESS%
echo   Telefono: %STORE_PHONE%
echo   NIT: %STORE_NIT%
echo.

echo [1/5] Limpiando builds anteriores...
if exist "tucajero\build" rmdir /s /q "tucajero\build"
if exist "tucajero\dist" rmdir /s /q "tucajero\dist"
if exist "dist" rmdir /s /q "dist"
for %%i in (*.spec) do del /q "%%i"
mkdir dist 2>nul
echo.

echo [2/5] Copiando logo...
if not "%STORE_LOGO%"=="" (
    if exist "%STORE_LOGO%" (
        if not exist "tucajero\assets\store" mkdir "tucajero\assets\store"
        copy /y "%STORE_LOGO%" "tucajero\assets\store\logo.png" >nul
        echo   Logo: %STORE_LOGO% ^> assets\store\logo.png
    ) else (
        echo   ADVERTENCIA: Logo no encontrado: %STORE_LOGO%
    )
)
echo.

echo [3/5] Generando configuracion...
(
echo {
echo   "store_name": "%STORE_NAME%",
echo   "logo_path": "assets/store/logo.png",
echo   "address": "%STORE_ADDRESS%",
echo   "phone": "%STORE_PHONE%",
echo   "nit": "%STORE_NIT%"
echo }
) > "tucajero\config\store_config.json"
echo   Config: config\store_config.json
echo.

echo [4/5] Compilando executable...
call venv\Scripts\activate.bat
pyinstaller --noconfirm TuCajero.spec
deactivate
echo.

if exist "tucajero\dist\TuCajero.exe" (
    move /y "tucajero\dist\TuCajero.exe" "dist\TuCajero.exe" >nul
    echo   EXE: dist\TuCajero.exe
)
echo.

echo [5/5] Generando instalador Inno Setup...

set "SANITIZED_NAME=%STORE_NAME: =%"
set "ISS_FILE=build_tucajero.iss"

(
echo [Setup]
echo AppName=TuCajero - %STORE_NAME%
echo AppVersion=1.0
echo DefaultDirName={autopf}\TuCajero
echo DefaultGroupName=TuCajero - %STORE_NAME%
echo OutputBaseFilename=TuCajero_%SANITIZED_NAME%_Setup
echo Compression=lzma2
echo SolidCompression=yes
echo WizardStyle=modern
echo.
echo [Files]
echo Source: "dist\TuCajero.exe"; DestDir: "{app}"; Flags: ignoreversion
echo Source: "tucajero\assets\*"; DestDir: "{app}\assets"; Flags: ignoreversion recursesubdirs createallsubdirs
echo Source: "tucajero\database\*"; DestDir: "{app}\database"; Flags: ignoreversion recursesubdirs createallsubdirs
echo.
echo [Icons]
echo Name: "{group}\TuCajero - %STORE_NAME%"; Filename: "{app}\TuCajero.exe"
echo Name: "{commondesktop}\TuCajero - %STORE_NAME%"; Filename: "{app}\TuCajero.exe"
echo.
echo [Run]
echo Filename: "{app}\TuCajero.exe"; Description: "Ejecutar TuCajero"; Flags: postinstall nowait skipifsilent
) > "%ISS_FILE%"

echo   ISS: %ISS_FILE%

set "ISCC="
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" set "ISCC=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if exist "C:\Program Files\Inno Setup 6\ISCC.exe" set "ISCC=C:\Program Files\Inno Setup 6\ISCC.exe"

if defined ISCC (
    "%ISCC%" "%ISS_FILE%"
    if exist "Output\TuCajero_%SANITIZED_NAME%_Setup.exe" (
        move /y "Output\TuCajero_%SANITIZED_NAME%_Setup.exe" "dist\" >nul
        echo   Installer: dist\TuCajero_%SANITIZED_NAME%_Setup.exe
        rmdir /s /q "Output" 2>nul
    )
    del "%ISS_FILE%"
) else (
    echo.
    echo   INSTALADOR: Inno Setup 6 no encontrado.
    echo   Instala Inno Setup desde: https://jrsoftware.org/isinfo.php
    echo   Luego ejecuta: "%ISCC%" "%ISS_FILE%"
)

echo.
echo ========================================
echo Build completado!
echo ========================================
echo.
dir dist\ /b
echo.
pause
