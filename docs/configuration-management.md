# Configuration Management

This document describes how the project is configured and how its Git version
control is managed. It records only what has actually been implemented.

## Configuration files

| File | Purpose |
|------|---------|
| `requirements.txt` | Pinned Python dependencies for the local project. |
| `.env.example` | Documented example of the environment variables the app reads. |
| `.gitignore` | Files excluded from version control (secrets, venvs, caches, databases). |
| `run.py` | Development entry point that starts the Flask app. |

## Environment variables

Configuration is read in `app/__init__.py` through `os.environ`, and
`python-dotenv` loads a local `.env` file if present. The supported variables
are documented in `.env.example`:

- `FLASK_DEBUG` — `1` enables Flask debug mode and auto-reload.
- `SECRET_KEY` — Flask secret key used for session signing and flash messages.
- `DATABASE` — SQLite database file path (relative paths resolve under `instance/`).
- `HOST` / `PORT` — bind address for `python run.py` (default `127.0.0.1:5000`).

Secrets are not hard-coded. When `.env` is absent the app falls back to a
development secret key and the default database name.

## Database path

The default database is `warrigal_park_fc.db`. A relative `DATABASE` value is
resolved against the Flask instance folder (`instance/`), which the app creates
automatically. An absolute path is used as-is. Tests pass an absolute path to a
temporary file.

The schema is created with:

```text
flask --app run.py init-db
```

or by importing the app and calling `database.init_db()` (as the tests do).

## Requirements file

`requirements.txt` pins:

- Flask (web framework)
- python-dotenv (environment loading)
- pytest (testing)

There are no other third-party dependencies.

## .gitignore

The `.gitignore` excludes, at minimum:

- `.env` (real secrets)
- `.venv/` and `venv/`
- `__pycache__/`, `*.pyc`, `.pytest_cache/`
- `instance/*.db` and `*.db` (local databases)

Real local database files must never be committed.

## Testing configuration

Tests in `tests/` use `conftest.py`, which builds a Flask app with
`TESTING=True` and a `DATABASE` pointing at a temporary SQLite file. Each test
therefore runs against isolated data and is repeatable without internet access
or real people's data. Run tests with:

```text
pytest
```

## Development configuration

For local development:

1. `python -m venv .venv`
2. activate the virtual environment (`.venv\Scripts\activate` on Windows)
3. `pip install -r requirements.txt`
4. optionally copy `.env.example` to `.env` and adjust values
5. `flask --app run.py init-db`
6. `python run.py`

The application is then available at `http://127.0.0.1:5000`.

## Deployment considerations

This is a local, single-user student project. There is no production deployment
or hosting configuration. If the app were deployed, the following would apply
(the code supports them but they are not implemented here):

- set a strong, unique `SECRET_KEY`,
- set `FLASK_DEBUG=0`,
- point `DATABASE` at persistent storage with a backup strategy.

## Git workflow

The project is version-controlled with Git and hosted on GitHub (remote
`origin` at https://github.com/bult111/warrigal-park-fc). The workflow is:

- `main` is the default and stable integration branch.
- Each piece of work is done on a `feature/*` branch created from `main`.
- Feature branches are merged back into `main` with `--no-ff` so the merge is
  recorded as an explicit merge commit.
- The test suite (`pytest`) is run on each feature branch and again after each
  merge.

The current branches are `main`, `feature/qa-and-validation`,
`feature/configuration-improvements`, and `feature/project-documentation`.
All three feature branches have been merged into `main`.
