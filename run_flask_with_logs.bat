@echo off
REM Run Flask app with logging to file
REM Usage: run_flask_with_logs.bat [port]
REM Example: run_flask_with_logs.bat 5000

setlocal

REM Create logs directory if it doesn't exist
if not exist "logs" mkdir logs

REM Get port from command line or default to 5000
set "PORT=%1"
if "%PORT%"=="" set "PORT=5000"

REM Set timestamp for log file
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set "TIMESTAMP=%datetime:~0,8%_%datetime:~8,6%"

set "LOGFILE=logs\flask_output_%TIMESTAMP%.log"

echo ===============================================================================
echo FLASK PPE DETECTION APP WITH LOGGING
echo ===============================================================================
echo Port: %PORT%
echo Output log file: %LOGFILE%
echo Main app log: logs\flaskapp.log
echo.
echo Press Ctrl+C to stop the application
echo ===============================================================================
echo.

REM Write header to log file
echo =============================================================================== > "%LOGFILE%"
echo FLASK PPE DETECTION APP OUTPUT LOG >> "%LOGFILE%"
echo =============================================================================== >> "%LOGFILE%"
echo Start Time: %date% %time% >> "%LOGFILE%"
echo Port: %PORT% >> "%LOGFILE%"
echo =============================================================================== >> "%LOGFILE%" 
echo. >> "%LOGFILE%"

REM Run Flask app and redirect output to both console and file
echo Starting Flask app on port %PORT%...
python flaskapp.py %PORT% > "%LOGFILE%" 2>&1

echo.
echo ===============================================================================
echo Flask app stopped at %date% %time%
echo.
echo Check these log files for details:
echo   - Console output: %LOGFILE%
echo   - Detailed app logs: logs\flaskapp.log
echo ===============================================================================

pause
