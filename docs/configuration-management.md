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
  recorded as an explicit merge commit. One exception is recorded below: the
  commit `1ec3a25` was pushed directly onto `main`.
- The test suite (`pytest`) is run on each feature branch and again after each
  merge.

The remote (`origin`) retains the following branches, confirmed from the GitHub
API on 2026-10-16:

| Branch | Head | Merged into `main`? |
|--------|------|---------------------|
| `main` | `fd7b68c15d92e0511b8609f3c9ce84c9943724ee` | — (integration branch) |
| `docs/align-auto-age-feature-status` | `3205042ade4beef2753dde4c86fbb5292dc418c8` | Yes, via PR #6 (`fd7b68c`) |
| `docs/sprint-4-merge-status` | `721281494370b40aac9c89a320cad56005baea2e` | Yes, via PR #5 (`3dbaf1e`) |
| `feature/configuration-improvements` | `8ee0b5291b045d598c84df0644570ed414735062` | Yes |
| `feature/project-documentation` | `66499c0ea269870b541496aeefdb7e0463173ec4` | Yes |
| `feature/qa-and-validation` | `d680b5c3a009ff61e62e8fb18f6b5a27f2b88b72` | Yes |
| `feature/sprint-1-qa-release` | `ebd622b680ebbf1c1a11585f8c15397b10b95524` | Yes, via PR #1 (`ee2cf04`) |
| `feature/sprint-2-member-guardian-colacolaco` | `efd1da1cfe4a62489f6b104a634bf3595ac78243` | Yes, via PR #2 (`86ebc70`) |
| `feature/sprint-3-registration-eligibility-sandip001159852` | `ab7d851a7fe3e00cd70d0042b9922c7ebafa6d95` | Yes, via PR #3 (`d6ee6a0`) |
| `feature/sprint-3-season-age-reference-leo0318-cpu` | `8ac23ef37d93ced0d6af8192d785a3af72731fee` | **No** — unmerged alternative rule interpretation |
| `feature/sprint-4-team-roster-leo0318-cpu` | `94acc1bd405635d9b5151ab975a9bb4904effc0c` | Yes, via PR #4 (`98fa25b`) |

Sprints 1 through 4 are therefore all part of `main`. The branch
`feature/auto-age-team-assignment-guardian-adult-leo0318-cpu` is **not** present
on the remote: it exists only as a local branch in the developer's working copy.
The automatic age-group, automatic team-assignment and guardian adult-verification
work is on `main` as the ordinary commit
`1ec3a25ccf44abeebf8f0c6c3647b4ea8b90593b`; because it was pushed directly rather
than merged with `--no-ff`, it has no pull-request merge record. The current tip
of `main` is the documentation merge commit `fd7b68c` (PR #6), whose tree
`a42f0465` is the state this project's documentation describes.

No CI service is configured: there is no GitHub Actions workflow in the
repository and the GitHub API reports zero workflow runs, so no CI pass is
claimed anywhere in this project.
