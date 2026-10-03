# Warrigal Park FC Member Registration and Team Roster System

A simple local web application for managing club members, guardians,
registrations and teams at Warrigal Park FC. Built as a student project
(ISYS3001 Assessment 2) using Flask and SQLite.

## Purpose

The system lets a club administrator:

- record members and their guardians,
- manage season registrations,
- enforce the rule that members under 18 need a guardian,
- organise registered players into teams for a season,
- view team rosters, registration history and guardian links.

## Main features

- **Member management** — create, search (duplicate names allowed), update, set inactive.
- **Guardian management** — create, search, update, link to members, view linked juniors.
- **Registration management** — create, view, amend, withdraw; history retained across seasons.
- **Junior guardian rule** — under-18 members require a guardian before a registration can be Complete.
- **Team management** — create, list, rename, remove (removal keeps members and registrations).
- **Player management** — add, move and remove players; players must have a same-season registration.
- **Roster, registration history and guardian linked juniors views**.
- **Dashboard** with basic counts.
- **User-friendly validation** with flash messages (no raw tracebacks for normal mistakes).

## Technology stack

- Python 3
- Flask (web framework)
- SQLite (database)
- HTML5, CSS3, Jinja2 (frontend)
- pytest (testing)
- python-dotenv (configuration)

## Folder structure

```text
warrigal-park-fc/
├── app/
│   ├── __init__.py          # app factory + configuration
│   ├── database.py          # SQLite connection + schema + query helpers
│   ├── models.py            # constants, validation, age calc, row mappers
│   ├── services.py          # business rules
│   ├── routes.py            # HTTP routes
│   ├── templates/           # Jinja2 templates
│   └── static/style.css     # stylesheet
├── tests/                   # pytest tests
├── docs/                    # architecture, scope, configuration docs
├── instance/                # local SQLite database (git-ignored)
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── CHANGELOG.md
└── run.py                   # development entry point
```

## Installation

### 1. Virtual environment setup

From the project directory, create and activate a virtual environment.

Windows:

```text
python -m venv .venv
.venv\Scripts\activate
```

### 2. Dependency installation

```text
pip install -r requirements.txt
```

### 3. Database initialization

Create the SQLite tables:

```text
flask --app run.py init-db
```

The database file is created inside the `instance/` folder.

## Local run instructions

```text
python run.py
```

Open <http://127.0.0.1:5000> in a browser.

## Testing instructions

```text
pytest
```

The tests run against an isolated temporary SQLite database and do not require
internet access.

## Important business rules

1. **Duplicate names are allowed.** A member's `id` — never the name — is the
   unique identifier, and a name search returns every matching record.
2. **Under-18 guardian rule.** A member under 18 must have at least one linked
   guardian before a registration can be set to `Complete`. Adults do not
   require a guardian.
3. **Soft deactivation.** Setting a member inactive changes their status; it
   never deletes the member.
4. **Registration history is retained.** Withdrawn registrations stay in the
   database and remain visible in the member's history.
5. **Season eligibility.** A player can be added to a team only if they have a
   non-withdrawn registration for the same season as the team.
6. **Team removal safety.** Removing a team deletes only the team and its
   player assignments; members and registrations are untouched.

## Scope limitations

This is a local, single-user application with no authentication, payments,
fixtures/results, import/export, email/SMS, or external integrations. See
`docs/project-scope.md` for the full in-scope / out-of-scope list.
