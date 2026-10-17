# Warrigal Park FC Member Registration and Team Roster System

A simple local web application for managing club members, guardians,
registrations and teams at Warrigal Park FC. Built with Flask and SQLite for
ISYS3001 Managing Software Development: the individual Assessment 2 deliverable
was developed into a group project for Assessment 3 by Team 25 (Cao Yang,
Chen Shuai, Zhang Runze, Zhou Kunpeng).

Project planning is recorded in Jira, project `MSD426GXUST25`
(<https://scu-it.atlassian.net/jira/software/c/projects/MSD426GXUST25/boards/2017>):
four Epics, twenty-two user stories with acceptance criteria and story points,
and the sprint goal for each of the five sprints. This repository holds the
code, the tests and the written evidence that correspond to that backlog.

## Purpose

The system lets a club administrator:

- record members and their guardians,
- manage season registrations,
- enforce the rule that members under 18 need a guardian,
- organise registered players into teams for a season,
- view team rosters, registration history and guardian links.

## Main features

- **Member management** — create, search (duplicate names allowed), update, set inactive.
- **Guardian management** — create, search, update, link to members, view linked juniors. Each guardian records a `date_of_birth` that must verify them as an adult (18 or over).
- **Registration management** — create, view, amend, withdraw; history retained across seasons. The age group is computed from the member's date of birth and the season and is never taken from the submitted form.
- **Junior guardian rule** — under-18 members require a linked, adult-verified guardian before a registration can be Complete.
- **Automatic age groups** — the season age (`season_year − birth_year`) maps onto a fixed list: `U6`, `U8`, `U10`, `U12`, `U14`, `U16`, `U18`, `Seniors`. This is the course project's own rule, not an official Football Australia regulation.
- **Automatic team assignment** — a Complete registration places the eligible player onto a matching team (same season and age group), fewest players first and then the lowest team id.
- **Team management** — create, list, rename, remove (removal keeps members and registrations).
- **Player management** — add, move and remove players; players must hold a same-season `Complete` registration and a matching age group, with at most one team per season.
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

Open <http://127.0.0.1:5000> in a browser. The host and port default to
`127.0.0.1:5000` and can be overridden with the `HOST` and `PORT` environment
variables (see `.env.example`).

## Testing instructions

```text
pytest
```

The tests run against an isolated temporary SQLite database and do not require
internet access.

## Important business rules

1. **Duplicate names are allowed.** A member's `id` — never the name — is the
   unique identifier, and a name search returns every matching record.
2. **Guardian adult rule.** A guardian must record a `date_of_birth` that
   verifies them as an adult (18 or over; the 18th birthday itself counts). A
   guardian with a missing or unreadable date of birth stays a valid row but is
   not verified, so it cannot satisfy the under-18 rule.
3. **Under-18 guardian rule.** A member under 18 must have at least one linked,
   adult-verified guardian before a registration can be set to `Complete`.
   Adults (18 or over) do not require a guardian.
4. **Automatic age group.** The age group is always computed from the member's
   date of birth and the season (`season_age = season_year − birth_year`) and
   stored on the registration: `U6`, `U8`, `U10`, `U12`, `U14`, `U16`, `U18` or
   `Seniors`. A member below 4 in a season cannot be registered. This is the
   course project's own rule, not an official Football Australia regulation.
5. **Automatic team assignment.** A `Complete` registration makes the player
   eligible for a team in the same season and matching age group, and places
   them on it automatically — fewest players first, then the lowest team id —
   including when a matching team is created later. An existing placement is
   never silently moved.
6. **Soft deactivation.** Setting a member inactive changes their status; it
   never deletes the member.
7. **Registration history is retained.** Withdrawn registrations stay in the
   database and remain visible in the member's history. A season's team
   assignment is dropped only when no `Complete` registration for it remains.
8. **Team eligibility.** A player can be placed on a team only with a `Complete`
   registration for the same season and a matching age group, and only one team
   per season.
9. **Team removal safety.** Removing a team deletes only the team and its
   player assignments; members and registrations are untouched.

## Git workflow

The project uses Git for version control, with the repository hosted on GitHub
(remote `origin`). The workflow is:

- `main` is the default and integration branch.
- Feature work is done on `feature/*` branches created from `main`.
- Feature branches are merged back into `main` with `--no-ff` merge commits so
  each integration is recorded explicitly.
- Not every change follows that path: the commit `1ec3a25` was pushed straight
  onto `main` as an ordinary commit rather than through a `--no-ff` merge, so no
  pull-request merge record exists for it (see below).
- The test suite (`pytest`) is run on each feature branch before merging.

### Branches and sprint status

`main` is the default and integration branch. The following branches exist on the
remote (`origin`), as confirmed from the GitHub API on 2026-10-17:

- `main` (`8c04c5e`, the merge commit of PR #7)
- `docs/align-auto-age-feature-status`
- `docs/redact-local-paths-20261016`
- `docs/sprint-4-merge-status`
- `feature/configuration-improvements`
- `feature/project-documentation`
- `feature/qa-and-validation`
- `feature/sprint-1-qa-release`
- `feature/sprint-2-member-guardian-colacolaco`
- `feature/sprint-3-registration-eligibility-sandip001159852`
- `feature/sprint-3-season-age-reference-leo0318-cpu` (**not** merged into `main`)
- `feature/sprint-4-team-roster-leo0318-cpu`

Every branch in that list is already contained in `main` except
`feature/sprint-3-season-age-reference-leo0318-cpu` (`8ac23ef`, "fix: measure the
under-18 guardian rule at the season reference date"). That branch is an
alternative rule interpretation that was never merged; `main` measures the
under-18 rule as of today, which is what the business rules above describe.

The branch `feature/auto-age-team-assignment-guardian-adult-leo0318-cpu` is
**not** present on the remote. It exists only as a local branch in the developer's
working copy, where it points at `1ec3a25`; the same commit is reachable from
`main`, where it is an ancestor of the current tip.

Completed sprints merged into `main` (from the Git history):

- **Sprint 1** — QA and regression testing (`feature/sprint-1-qa-release`).
- **Sprint 2** — Member and Guardian Management
  (`feature/sprint-2-member-guardian-colacolaco`).
- **Sprint 3** — Registration and Eligibility
  (`feature/sprint-3-registration-eligibility-sandip001159852`).

**Sprint 4** — Team and Roster Management was merged into `main` via PR #4
(merge commit `98fa25b0dda738659a752dfc27189ebce286b685`, from the branch
`feature/sprint-4-team-roster-leo0318-cpu`). Its work covers team
creation/listing, renaming and safe removal, same-season `Complete`-registration
player eligibility, player move/remove (including the S2-F1 no-op feedback fix),
and roster contact display.

Sprint 4 recorded **267 passed** pytest tests (0 failed, 0 errors, 0 skipped)
and a **21/21** browser acceptance run driven by the DSH environment using Edge
and the Chrome DevTools Protocol; see
`docs/testing/sprint-4-acceptance-results.md`. These results were recorded on
the Sprint 4 branch before the merge and have not been re-run since. Browser
checks are automation, not human sign-off.

Three later documentation-only pull requests were merged into `main`:

- **PR #5** — "docs: correct Sprint 4 merge status" (branch
  `docs/sprint-4-merge-status`, head `7212814`), merge commit
  `3dbaf1e66127787d9ef50b549a0e21b0270aba2f`.
- **PR #6** — "Align documentation with merged feature status" (branch
  `docs/align-auto-age-feature-status`, head
  `3205042ade4beef2753dde4c86fbb5292dc418c8`), merge commit
  `fd7b68c15d92e0511b8609f3c9ce84c9943724ee`.
- **PR #7** — "docs: add final verification evidence and redact local paths"
  (branch `docs/redact-local-paths-20261016`, head `3a7714f`), merge commit
  `8c04c5ec60e5ec53ec65f31c4bcb11dfa1605389`. This added the final verification
  evidence set under `docs/testing/final-verification-20261016/` and redacted
  local file paths from earlier test records. It changed documentation and
  evidence only.

### Automatic age groups, automatic team assignment and the guardian adult rule

These features are part of `main`. The work landed as the ordinary commit
`1ec3a25` ("feat: add automatic age-group assignment and adult guardian
validation"). That commit was pushed directly onto `main`; it is **not** the tip
of `main` and it is **not** a `--no-ff` merge commit, so there is no
pull-request merge record for it.

The current tip of `main` is `8c04c5ec60e5ec53ec65f31c4bcb11dfa1605389`, the
merge commit of PR #7 (2026-10-17). PRs #5, #6 and #7 each changed documentation
or evidence only, so no application code has changed since `1ec3a25`. The commit
history on `main` is therefore:

```text
8c04c5e  Merge PR #7: final verification evidence and path redaction  <- main tip
fd7b68c  docs: align documentation with current feature status (PR #6)
1ec3a25  feat: add automatic age-group assignment and adult guardian validation
3dbaf1e  Merge pull request #5 from bult111/docs/sprint-4-merge-status
```

On that code state (`fd7b68c`, tree `a42f0465`) the full suite records
**348 passed** (0 failed, 0 errors, 0 skipped), including the date-of-birth
consistency regression tests in `tests/test_member_dob_consistency.py`. This
figure was re-run and confirmed on 2026-10-16; the evidence is in
`docs/testing/final-verification-20261016/`. It supersedes the **335 passed**
figure recorded while the work was still described as unmerged. The
**267 passed** figure stated above remains the Sprint 4 record and is unchanged.

No GitHub Actions workflow is configured for this repository and no workflow run
has ever been recorded, so no CI result is claimed anywhere in this project.

## Scope limitations

This is a local, single-user application with no authentication, payments,
fixtures/results, import/export, email/SMS, or external integrations. See
`docs/project-scope.md` for the full in-scope / out-of-scope list.
