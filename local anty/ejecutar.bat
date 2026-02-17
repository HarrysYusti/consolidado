@echo off
echo Instalando dependencias (si aplica)...
rem El script usa solo librerias estandar, pero verificamos python.
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python no esta instalado o no esta en el PATH.
    pause
    exit /b
)

echo Ejecutando script de consolidacion V2...
python consolidar_v2.py

echo.
echo ==========================================
echo Ejecucion finalizada. Revisa el reporte arriba.
echo ==========================================
pause
