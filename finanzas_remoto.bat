@echo off
cd /d "%~dp0"
echo ================================
echo FINANZAS - ACCESO REMOTO CON NGROK
echo ================================
start "Finanzas Flask" cmd /k python web\app.py
timeout /t 3 /nobreak >nul
start "Ngrok" cmd /k ngrok http 5000
