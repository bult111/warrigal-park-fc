"""Database access layer for the Warrigal Park FC application.

This module owns the SQLite connection handling, the schema definition and
low-level query helpers. Business rules live in ``services.py`` and should not
be placed here.
"""

import sqlite3
from pathlib import Path

import click
from flask import current_app, g

SCHEMA = """
CREATE TABLE IF NOT EXISTS members (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    name           TEXT NOT NULL,
    date_of_birth  TEXT NOT NULL,
    email          TEXT NOT NULL DEFAULT '',
    phone          TEXT NOT NULL DEFAULT '',
    address        TEXT NOT NULL DEFAULT '',
    status         TEXT NOT NULL DEFAULT 'Active'
);

CREATE TABLE IF NOT EXISTS guardians (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    name    TEXT NOT NULL,
    email   TEXT NOT NULL DEFAULT '',
    phone   TEXT NOT NULL DEFAULT '',
    address TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS guardian_members (
    guardian_id INTEGER NOT NULL,
    member_id   INTEGER NOT NULL,
    PRIMARY KEY (guardian_id, member_id),
    FOREIGN KEY (guardian_id) REFERENCES guardians (id) ON DELETE CASCADE,
    FOREIGN KEY (member_id)   REFERENCES members (id)   ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS registrations (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    member_id INTEGER NOT NULL,
    season    TEXT NOT NULL,
    age_group TEXT NOT NULL,
    status    TEXT NOT NULL DEFAULT 'Started',
    FOREIGN KEY (member_id) REFERENCES members (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS teams (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    season    TEXT NOT NULL,
    name      TEXT NOT NULL,
    age_group TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS team_players (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    team_id   INTEGER NOT NULL,
    member_id INTEGER NOT NULL,
    UNIQUE (team_id, member_id),
    FOREIGN KEY (team_id)   REFERENCES teams (id)   ON DELETE CASCADE,
    FOREIGN KEY (member_id) REFERENCES members (id) ON DELETE CASCADE
);
"""


def get_db():
    """Return the current request's SQLite connection, creating it if needed."""
    if "db" not in g:
        database_path = current_app.config["DATABASE"]
        # A relative database path is resolved against the instance folder.
        path = Path(database_path)
        if not path.is_absolute():
            path = Path(current_app.instance_path) / path
        path.parent.mkdir(parents=True, exist_ok=True)

        g.db = sqlite3.connect(str(path))
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(e=None):
    """Close the connection stored on the application context, if any."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Create the database schema in an empty or missing database file."""
    db = get_db()
    db.executescript(SCHEMA)
    db.commit()


@click.command("init-db")
def init_db_command():
    """CLI command that creates the database tables."""
    init_db()
    click.echo("Initialized the database.")


def init_app(app):
    """Register database teardown and the ``init-db`` CLI command."""
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


def query_all(sql, params=()):
    """Run a SELECT and return every row as a list of ``sqlite3.Row``."""
    return get_db().execute(sql, params).fetchall()


def query_one(sql, params=()):
    """Run a SELECT and return the first row or ``None``."""
    return get_db().execute(sql, params).fetchone()


def execute(sql, params=()):
    """Run a write statement and return the affected row count."""
    db = get_db()
    cursor = db.execute(sql, params)
    db.commit()
    return cursor.rowcount
