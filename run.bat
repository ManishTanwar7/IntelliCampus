@echo off
title IntelliCampus Desktop Application
echo Starting IntelliCampus Academic Suite...
set SCRIPT_DIR=%~dp0
call "%SCRIPT_DIR%.venv\Scripts\activate.bat"
python "%SCRIPT_DIR%main.py"
pause
