# Architecture

This document describes the actual, implemented architecture of the Warrigal
Park FC Member Registration and Team Roster System.

## Text diagram

```
Browser (HTML5 + CSS3 + Jinja2-rendered templates)
   |
   |  HTTP request / response
   v
Flask Routes (app/routes.py)
   |  calls service functions, flashes user messages
   v
Service Layer (app/services.py)
   |  business rules: guardian rule, season eligibility, validation
   v
Database Layer (app/database.py + app/models.py)
   |  SQLite connection, schema, parameterized SQL, data mapping
   v
SQLite database file (instance/warrigal_park_fc.db)
```

## Frontend

- Server-rendered HTML5 pages using Jinja2 templates in `app/templates/`.
- A single shared layout, `base.html`, provides the header, navigation and
  flash-message area.
- Styling comes from one stylesheet, `app/static/style.css` (CSS3).
- JavaScript is minimal and only used for a client-side delete confirmation;
  every other behaviour is handled by normal HTML forms and server redirects.

## Flask backend

The application uses the Flask application-factory pattern in `app/__init__.py`
via `create_app()`. This makes the app easy to configure in tests by passing a
`test_config` dictionary.

## Route layer — `app/routes.py`

Routes are registered as a single blueprint. Each route only:

1. reads the request (query string or form data),
2. calls one or more service functions,
3. flashes a user-facing message,
4. renders a template or redirects.

No business rules or raw SQL live in the route layer.

## Service layer — `app/services.py`

All business rules live here, including:

- the under-18 guardian rule (`can_complete_registration`),
- team player season eligibility (`add_player_to_team`),
- field validation,
- guardian linking,
- registration state changes.

The service layer raises `ServiceError` (a `ValueError` subclass) with a
user-friendly message when a rule is violated; routes catch it and display the
message as a flash.

## Database layer — `app/database.py` and `app/models.py`

- `database.py` owns the SQLite connection, the schema, `init-db`, and small
  query helpers (`query_all`, `query_one`, `execute`). All statements are
  parameterized.
- `models.py` holds status constants, date/email validation, the age
  calculation and `sqlite3.Row` → `dict` mappers.

Foreign keys are enabled (`PRAGMA foreign_keys = ON`) on every connection.

## Data relationships

- `members` — one club member; `status` is Active or Inactive.
- `guardians` — an independent guardian record holding its own contact details.
- `guardian_members` — many-to-many link between guardians and members.
- `registrations` — one member can have many registrations (one per season).
- `teams` — a team for a specific season and age group.
- `team_players` — many-to-many link between teams and members (players).

```text
guardians 1 ──< guardian_members >── 1 members
                                          │
                                          1
                                          │
                                          ▼
                                   registrations (many per member)

teams 1 ──< team_players >── 1 members
```

## Testing structure

Tests live in `tests/` and use `pytest`. `conftest.py` provides:

- an isolated Flask app backed by a temporary SQLite database,
- a test client,
- factory fixtures (`make_member`, `make_guardian`, `make_registration`,
  `make_team`, `link_guardian`) and date helpers.

Tests call the service layer directly (unit tests) and exercise pages through
the Flask test client (view tests). They never touch the real database.

## Configuration structure

Configuration is loaded through `app/__init__.py` from environment variables
(`SECRET_KEY`, `DATABASE`, `FLASK_ENV`, `FLASK_DEBUG`), with a local `.env`
file supported by `python-dotenv`. See `configuration-management.md` for
details.
