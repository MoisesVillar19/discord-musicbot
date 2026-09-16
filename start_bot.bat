@echo off
rem Arranca el bot usando el venv de la propia carpeta (portable, sin ruta fija).
cd /d "%~dp0"
if not exist "venv\Scripts\python.exe" (
    echo [ERROR] No se encontro venv\Scripts\python.exe
    echo Crea el entorno con: python -m venv venv ^&^& venv\Scripts\activate ^&^& pip install -r requirements.txt
    pause
    exit /b 1
)
call venv\Scripts\activate
python bot.py
pause
