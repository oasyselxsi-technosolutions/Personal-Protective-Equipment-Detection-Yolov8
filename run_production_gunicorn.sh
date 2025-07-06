#!/bin/bash
# Production startup script for Linux/Unix systems

echo "Starting PPE Detection Flask App with Gunicorn..."
echo "Server will be available at: http://0.0.0.0:5000"
echo "Press Ctrl+C to stop the server"
echo

# Set production environment variables
export FLASK_ENV=production
export FLASK_DEBUG=False

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
else
    echo "Warning: Virtual environment not found. Using system Python."
fi

# Install dependencies if needed
pip install -r requirements.txt

# Start with Gunicorn
gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 wsgi:app
