@echo off
rem Abre el panel local (administra el bot: start/stop, alters, config, logs).
cd /d "%~dp0"
if not exist "venv\Scripts\python.exe" (
    echo [ERROR] No se encontro venv\Scripts\python.exe
    echo Crea el entorno con: python -m venv venv ^&^& venv\Scripts\activate ^&^& pip install -r requirements.txt
    pause
    exit /b 1
)
start "" "venv\Scripts\pythonw.exe" "panel\panel.py"
