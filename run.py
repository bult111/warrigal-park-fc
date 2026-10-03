"""Development entry point for the Warrigal Park FC application.

Run with:

    python run.py

The application is served at http://127.0.0.1:5000 by default. The host, port
and debug mode can be overridden with the HOST, PORT and FLASK_DEBUG
environment variables (see ``.env.example``).
"""

import os

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(
        host=os.environ.get("HOST", "127.0.0.1"),
        port=int(os.environ.get("PORT", "5000")),
        debug=app.config.get("DEBUG", False),
    )
