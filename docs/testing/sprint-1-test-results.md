# Sprint 1 — Automated Regression Test Results

- **Date:** 2026-10-13
- **Branch:** `feature/sprint-1-qa-release`
- **Working directory:** `<PROJECT_ROOT>`
- **OS:** Windows (win32)
- **Interpreter:** `.venv\Scripts\python.exe` — Python 3.10.11
- **pytest:** 8.3.3
- **Flask:** 3.0.3

## Environment readiness

| Check | Command | Result |
|-------|---------|--------|
| Python version | `python --version` | Python 3.10.11 |
| pip version | `python -m pip --version` | pip 23.0.1 |
| Dependency consistency | `.venv\Scripts\python.exe -m pip check` | No broken requirements found |
| App factory loads | `python -c "from app import create_app; app = create_app()"` | OK |
| DB init (temp DB) | `flask --app run.py init-db` (temp `DATABASE`) | "Initialized the database." |

Dependencies in `requirements.txt` (Flask 3.0.3, python-dotenv 1.0.1, pytest 8.3.3)
match the versions installed in the project virtual environment.

## Test command

```powershell
.venv\Scripts\python.exe -m pytest -v
```

## Baseline result (before Sprint 1 additions)

```text
68 passed in 1.88s
```

- Collected: 68
- Passed: 68
- Failed: 0
- Skipped: 0
- Errors: 0

## Changes made to the suite this sprint

Added `tests/test_edge_cases.py` (11 tests) to cover unhappy paths and boundary
behaviours that were not previously asserted:

- invalid member status is rejected,
- withdrawing / updating a non-existent registration is rejected,
- moving a player to the same team is rejected,
- removing a player from a non-existent team is rejected,
- adding a non-existent member to a team is rejected,
- completing a registration for a non-existent member is rejected,
- `get_member` / `get_guardian` / `get_team` / `get_registration` return `None`
  for missing records.

No existing tests were removed or weakened.

## Final result (after Sprint 1 additions)

```text
79 passed in 2.10s
```

- Collected: 79
- Passed: 79
- Failed: 0
- Skipped: 0
- Errors: 0

## Coverage by area

| Area | Test file(s) | Status |
|------|--------------|--------|
| Member management | `test_members.py`, `test_views.py` | All pass |
| Guardian management | `test_guardians.py`, `test_views.py` | All pass |
| Registration + under-18 rule | `test_registration.py`, `test_views.py` | All pass |
| Team management | `test_teams.py`, `test_views.py` | All pass |
| Player / team membership | `test_players.py` | All pass |
| Validation / error handling | `test_validation.py` | All pass |
| Page rendering (views) | `test_views.py` | All pass |
| Edge cases (new) | `test_edge_cases.py` | All pass |

## Failures and how they were handled

None. The full suite passed with no failures, skips, or errors. No application
defects were surfaced by the regression suite (see `sprint-1-defect-log.md` for
the limitations observed during manual code review and E2E verification).
