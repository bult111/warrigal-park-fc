"""Application factory for Warrigal Park FC."""

import os
from pathlib import Path

from flask import Flask

from dotenv import load_dotenv

# Load variables from a local .env file (ignored by version control).
load_dotenv()


def create_app(test_config=None):
    """Create and configure the Flask application."""
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-secret-key"),
        DATABASE=os.environ.get("DATABASE", "warrigal_park_fc.db"),
    )

    # Development / debug mode can be toggled through the environment.
    app.config["FLASK_ENV"] = os.environ.get("FLASK_ENV", "development")
    app.config["DEBUG"] = os.environ.get("FLASK_DEBUG", "0") == "1"

    if test_config:
        app.config.update(test_config)

    # Guarantee the instance folder exists for the SQLite file.
    os.makedirs(app.instance_path, exist_ok=True)

    # Register the database helpers and the `flask init-db` command.
    from . import database

    database.init_app(app)

    # Register the HTTP routes.
    from . import routes

    app.register_blueprint(routes.bp)

    # Convenience template globals used across pages.
    from . import models as _models

    @app.template_global()
    def member_statuses():
        return _models.MEMBER_STATUSES

    @app.template_global()
    def registration_statuses():
        return _models.REGISTRATION_STATUSES

    return app
