"""Application factory for Warrigal Park FC."""

import os

from flask import Flask

from dotenv import load_dotenv

# Load variables from a local .env file (ignored by version control).
load_dotenv()


def create_app(test_config=None):
    """Create and configure the Flask application."""
    app = Flask(__name__, instance_relative_config=True)

    # Secret key and database path come from the environment (or safe defaults).
    # A relative DATABASE path is resolved against the instance folder.
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-secret-key"),
        DATABASE=os.environ.get("DATABASE", "warrigal_park_fc.db"),
    )

    # Debug mode is driven by FLASK_DEBUG ("1" = on); run.py reads this value.
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
