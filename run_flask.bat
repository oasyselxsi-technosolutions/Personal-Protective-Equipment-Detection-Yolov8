@echo off
REM Flask App Launcher Script
REM Usage: run_flask.bat [port]
REM Example: run_flask.bat 8080

if "%1"=="" (
    echo Starting Flask app on default port 5000...
    python flaskapp.py
) else (
    echo Starting Flask app on port %1...
    python flaskapp.py %1
)

echo.
echo Flask app has stopped.
pause
