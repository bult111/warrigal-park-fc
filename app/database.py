"""Database access layer for the Warrigal Park FC application.

This module owns the SQLite connection handling, the schema definition and
low-level query helpers. Business rules live in ``services.py`` and should not
be placed here.
"""

import sqlite3
from contextlib import contextmanager
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
    address TEXT NOT NULL DEFAULT '',
    -- Nullable: legacy guardians created before the column existed stay valid
    -- but are not treated as verified adults until a date of birth is recorded.
    date_of_birth TEXT
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


def _migrate(db):
    """Apply idempotent schema migrations to an existing database.

    Called for every new connection (and by ``init_db``) so that a database
    created by an earlier version gains the ``guardians.date_of_birth`` column
    before any code reads it. Safe to run repeatedly, and a no-op while the
    ``guardians`` table does not exist yet.
    """
    tables = {
        row["name"]
        for row in db.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
    }
    if "guardians" not in tables:
        return
    columns = {row["name"] for row in db.execute("PRAGMA table_info(guardians)")}
    if "date_of_birth" not in columns:
        try:
            db.execute("ALTER TABLE guardians ADD COLUMN date_of_birth TEXT")
            db.commit()
        except sqlite3.OperationalError as error:
            # Another connection may have added the column between the check and
            # the ALTER; treat a duplicate-column error as already migrated.
            if "duplicate column name" not in str(error).lower():
                raise


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
        # Bring an older database up to the current schema before it is used.
        _migrate(g.db)
    return g.db


def close_db(e=None):
    """Close the connection stored on the application context, if any."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Create the database schema and apply migrations to an existing file."""
    db = get_db()
    db.executescript(SCHEMA)
    _migrate(db)
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


@contextmanager
def transaction():
    """Run several writes as a single atomic unit.

    ``execute`` commits after every statement, so a change that must succeed or
    fail as a whole has to run inside this block and use the connection
    directly rather than ``execute``::

        with database.transaction() as db:
            db.execute("UPDATE ...", (...))
            db.execute("UPDATE ...", (...))

    The block commits when it completes and rolls back if any exception is
    raised, leaving no partially written state.
    """
    db = get_db()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
