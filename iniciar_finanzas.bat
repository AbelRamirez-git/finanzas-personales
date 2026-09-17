@echo off
cd /d "%~dp0"
echo ================================
echo INICIANDO SISTEMA DE FINANZAS
echo ================================
python -m database.db
python web\app.py
pause
