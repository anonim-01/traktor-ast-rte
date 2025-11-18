"""
Windows-compatible startup script for Flask application.
Uses Waitress WSGI server instead of Gunicorn (which is Unix-only).
"""

import os
import platform
from app import create_app

app = create_app()

if __name__ == "__main__":
    if platform.system() == "Windows":
        # Use Waitress for Windows
        from waitress import serve
        print("Starting Flask app with Waitress (Windows-compatible)...")
        serve(app, host="0.0.0.0", port=8000)
    else:
        # Use Gunicorn for Unix/Linux
        print("Starting Flask app with Gunicorn...")
        os.system("gunicorn -c gunicorn_config.py main:app")
