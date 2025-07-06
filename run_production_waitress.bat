@echo off
echo Installing production dependencies...
echo.

REM Check if virtual environment exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo Creating virtual environment...
    python -m venv venv
    call venv\Scripts\activate.bat
)

echo.
echo Installing/updating packages...
pip install -r requirements.txt

echo.
echo Starting PPE Detection Flask App with Waitress (Windows Production Server)...
echo Server will be available at: http://0.0.0.0:5000
echo Press Ctrl+C to stop the server
echo.

REM Set production environment variables
set FLASK_ENV=production
set FLASK_DEBUG=False

REM Start with Waitress (better for Windows than Gunicorn)
waitress-serve --host=0.0.0.0 --port=5000 wsgi:app

pause
