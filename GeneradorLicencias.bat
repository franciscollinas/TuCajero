@echo off
cd /d "%~dp0"
"venv\Scripts\python.exe" GeneradorLicencias.py
if errorlevel 1 pause
