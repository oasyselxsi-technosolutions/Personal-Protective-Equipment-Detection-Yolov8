@echo off
echo Starting PPE Detection Flask App in Production Mode...
echo.

REM Set production environment
set FLASK_ENV=production
set FLASK_DEBUG=False

REM Check if virtual environment exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo Warning: Virtual environment not found. Using system Python.
)

echo.
echo Starting Flask application...
echo Server will be available at: http://0.0.0.0:5000
echo Press Ctrl+C to stop the server
echo.

REM Start Flask app in production mode
python flaskapp.py

pause
