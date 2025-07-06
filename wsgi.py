"""
WSGI entry point for the PPE Detection Flask application.
This file is used by production WSGI servers like Gunicorn or Waitress.
"""
from flaskapp import app

if __name__ == "__main__":
    app.run()
