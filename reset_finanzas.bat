@echo off
cd /d "%~dp0"
echo ADVERTENCIA: esto borrara todos los movimientos y el ahorro actual.
set /p confirmar="Escribe BORRAR para continuar: "
if /I not "%confirmar%"=="BORRAR" (
  echo Operacion cancelada.
  pause
  exit /b
)
if exist finanzas.db del finanzas.db
python -m database.db
echo Base de datos reiniciada.
pause
