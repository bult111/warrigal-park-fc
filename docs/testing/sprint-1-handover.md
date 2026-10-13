# Sprint 1 — Release & Handover Notes

- **Date:** 2026-10-13
- **Branch:** `feature/sprint-1-qa-release`
- **Working directory:** `C:\Users\z\Desktop\deepseek harness\warrigal-park-fc`

This document records what was actually done during Sprint 1 QA on the local
machine, and what still needs manual action. It is intentionally limited to
verified facts.

## Scope of this sprint (QA, not feature work)

Sprint 1 covered maintaining the regression suite, verifying core workflows,
checking reproducible local configuration, recording defects, and preparing
handover notes. No application feature code was changed.

## Completed

1. **Regression suite run** — full suite executed twice:
   - Baseline: `68 passed` (1.88s).
   - After additions: `79 passed` (2.10s).
2. **Coverage strengthened** — added `tests/test_edge_cases.py` (11 new tests
   for unhappy paths and missing-record lookups). No existing test was removed
   or weakened.
3. **End-to-end verification** — 19 core workflows verified against a
   temporary database using a combination of Flask test client requests and
   direct service-layer calls; all passed. See
   `sprint-1-e2e-checklist.md`.
4. **Configuration review** — `requirements.txt`, `.env.example`, `.gitignore`,
   `app/database.py`, `README.md`, and `docs/` were checked against the code.
   - `requirements.txt` matches the installed venv (Flask 3.0.3,
     python-dotenv 1.0.1, pytest 8.3.3); `pip check` reports no broken deps.
   - `.env.example` and the database path/initialisation description are
     accurate. `flask --app run.py init-db` was verified on a temporary DB.
   - `.gitignore` correctly excludes `.env`, virtual envs, caches, and `*.db`.
   - No `.env` file exists locally (no secrets at risk).
5. **Documentation consistency** — updated the "current branches" lists in
   `README.md` and `docs/configuration-management.md` to include the in-progress
   `feature/sprint-1-qa-release` branch.

## Files changed / added

Added:

- `tests/test_edge_cases.py`
- `docs/testing/sprint-1-test-results.md`
- `docs/testing/sprint-1-e2e-checklist.md`
- `docs/testing/sprint-1-defect-log.md`
- `docs/testing/sprint-1-handover.md`

Modified:

- `README.md` (current-branch list)
- `docs/configuration-management.md` (current-branch list)

## Test results (final)

- Command: `.venv\Scripts\python.exe -m pytest -v`
- Collected: 79
- Passed: 79
- Failed: 0
- Skipped: 0
- Errors: 0

## Known limitations / open items

See `sprint-1-defect-log.md`. In short:

- D1: duplicate same-season registrations are not prevented (product decision
  required).
- D2: withdrawing a registration does not remove the member from teams
  (product decision required).
- D3: `remove_player` / `unlink` are silent no-ops when the relationship does
  not exist (minor).
- D4: the venv contains unused packages (`lxml`, `pypdf`, `python-docx`) not in
  `requirements.txt` (environment hygiene).

## Not done this sprint

- No Git operations were performed by the agent (`git add` / `commit` / `push`
  / `fetch` / `pull` / `merge`). All changes remain as uncommitted working-tree
  modifications for the user to review in GitHub Desktop.
- No live-browser manual click-through was performed (no browser automation
  available). Marked for manual verification.
- No `CHANGELOG.md` version bump (no application release was made; only QA and
  documentation work).
- No application code changed.

## Manual handover steps (for the user)

1. Review the changes in GitHub Desktop (repository `warrigal-park-fc`).
2. Confirm the branch is `feature/sprint-1-qa-release`.
3. Confirm `tests/test_edge_cases.py` and the four `docs/testing/*.md` files
   are included, and that no `.env`, `.venv/`, `__pycache__/`, `.pytest_cache/`,
   or `*.db` files are staged (`.gitignore` should already exclude them).
4. Run the suite once more locally if desired:
   `python -m pytest -v` (activate `.venv` first).
5. Commit and push via GitHub Desktop, then open a PR to `main` for review by
   Member A or the repository owner.
