# IntelliCampus Desktop Launcher
Write-Host "Launching IntelliCampus Desktop Application..." -ForegroundColor Cyan
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
& "$scriptDir\.venv\Scripts\python.exe" "$scriptDir\main.py"
