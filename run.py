"""Development entry point for the Warrigal Park FC application.

Run with:

    python run.py

The application is served at http://127.0.0.1:5000 by default.
"""

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
