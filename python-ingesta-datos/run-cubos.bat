@echo off
cd /d %~dp0

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Run the ETL script
python "src/main.py" "cubos"
