# Sprint 2 — Handover Notes

- **Sprint:** Sprint 2 — Epic: Member and Guardian Management
- **Stories:** `MSD426GXUST25-2` … `MSD426GXUST25-8` (7 Stories, 18 Story Points)
- **Document status:** records only what was actually done and measured on the
  local working copy.

## Actual scope of this sprint

Verification and QA of the member and guardian management workflows, a
targeted defect fix to the guardian unlink feedback path, new automated
coverage for all seven Stories, and this documentation.

Deliberately **not** done:

- No feature was rewritten. The member and guardian workflows were already
  implemented and were verified rather than rebuilt.
- No database schema change and no migration.
- No change to the registration, team, player or dashboard logic.
- No decision was made on the open product questions (S2-O1, S2-O2, S2-C1,
  S2-C2). They remain for the team.

### Scope deviation considered and corrected

During the initial Sprint 2 work, the same "reported success for a no-op"
defect was also fixed in the team-player removal path
(`remove_player_from_team` in `app/services.py` and `player_remove` in
`app/routes.py`, alongside the Sprint 1 defect D3).

The team- and player-removal no-op feedback change belongs to the **Team and
Roster Management** epic, which is planned for **Sprint 4**, not to Member and
Guardian Management.
During the pre-upload review that change was therefore **reverted**, so this
sprint contains no out-of-epic source modification. The revert was verified to
leave the suite unchanged at 133 passed, because no test covered that path. The
issue is recorded as **S2-F1** in `sprint-2-defect-log.md` with a
recommendation for Sprint 4.

This deviation is stated here deliberately rather than concealed. No
functionality was removed and no existing regression test was weakened.

## Baseline (measured before any change)

| Command | Result |
|---|---|
| `python -m pytest` | 79 collected, 79 passed, 0 failed, 0 skipped, 0 errors (3.34s) |

This matches the Sprint 1 reported figure, confirming the working copy
contained the latest available Sprint 1 work.

## Modified files

### Application code

| File | Change | Purpose |
|---|---|---|
| `app/services.py` | Modified | `unlink_guardian_member` now validates that the guardian and member exist and returns whether a link row was actually removed. Fixes S2-D1. The `remove_player_from_team` change was reverted (out of scope, S2-F1). |
| `app/routes.py` | Modified | `guardian_unlink` now flashes success only when a link was removed, and an explanatory error message otherwise. The `player_remove` change was reverted (out of scope, S2-F1). |

### Tests

| File | Change | Purpose |
|---|---|---|
| `tests/test_member_guardian_workflows.py` | **Added** | 48 test functions collecting **54 cases** across all seven Sprint 2 Stories, including the S2-D1 regression tests. |

No existing test file was modified, and no test was removed, weakened or
renamed.

### Documentation

| File | Change |
|---|---|
| `docs/testing/sprint-2-test-plan.md` | Added |
| `docs/testing/sprint-2-test-results.md` | Added |
| `docs/testing/sprint-2-e2e-checklist.md` | Added |
| `docs/testing/sprint-2-defect-log.md` | Added |
| `docs/testing/sprint-2-handover.md` | Added |
| `docs/testing/sprint-2-changed-files.txt` | Added (plain-text manifest of changed files) |

No Sprint 1 document was modified, and no unrelated document was touched.

## Test counts (reconciled)

| Figure | Value | Basis |
|--------|------:|-------|
| Distinct tests collected in the new module | **54** | `--collect-only -q` → `54 tests collected` |
| Test functions written | **48** | 3 are parametrized, expanding to 54 cases |
| Sum of the per-Story mapping counts | **63** | Coverage mapping; 9 tests support two Stories each, so 63 − 9 = 54 |

Final suite total: **79 + 54 = 133**. The per-Story figures are mappings, not
distinct test totals, and must not be added to the suite total. The full
reconciliation is in `sprint-2-test-results.md`.

## Test results

All commands below were run with `.venv\Scripts\python.exe` in the project
directory.

| Run | Command | Result |
|---|---|---|
| Baseline (before change) | `python -m pytest` | 79 passed, 0 failed |
| New tests only | `python -m pytest tests/test_member_guardian_workflows.py -v` | 54 passed, 0 failed (2.11s) |
| Fix present (working tree) | `python -m pytest tests/test_member_guardian_workflows.py -k "no_op or nothing_was_linked"` | 2 passed |
| Negative control (fix deliberately reverted) | same command | **1 failed**, 1 passed, 52 deselected |
| Final (after change and scope cleanup) | `python -m pytest` | **133 passed, 0 failed, 0 skipped, 0 errors** (5.18s) |

Environment: Python 3.13.1, pytest 8.3.3, Flask 3.0.3, python-dotenv 1.0.1,
`pip check` clean, each test on its own temporary SQLite database.

The negative control failed **only** while the fix was reverted; the single
failure was `test_unlink_route_reports_no_op_instead_of_success`. The fix was
then restored, confirmed present in `app/routes.py`, and the full suite re-run
green. No file was left in the reverted state.

See `sprint-2-test-results.md` for the full breakdown.

## Findings summary

- **Fixed:** S2-D1 — the guardian unlink route used to flash success when no
  link existed (the item Sprint 1 logged as D3). Now accurate, with regression
  tests.
- **Deferred to Sprint 4:** S2-F1 — the same pattern in team player removal.
  The out-of-scope change was reverted and documented.
- **New observations for decision:** S2-O1 (what deactivation should mean for
  team placement and future registrations) and S2-O2 (removing the last
  guardian of a junior with a `Complete` registration).
- **Carried forward for decision:** S2-C1 (duplicate same-season registrations,
  Sprint 1 D1) and S2-C2 (withdrawn registration still on a roster, Sprint 1
  D2). Neither was changed.
- Investigated and confirmed **correct**, so left alone: edit forms retaining
  typed values on error, failure feedback on invalid create, guardian contact
  read from the single shared record, and duplicate-name separation.

Details are in `sprint-2-defect-log.md`.

## Browser verification performed

A browser run was executed against the real application on a temporary database
(`sprint2_manual_check.db`, served on port 5001, deleted afterwards). It was
driven by browser automation, not by a human clicking through the interface.

| Test ID | Scenario | Result |
|---|---|---|
| S2-E2E-01 | Create and view a member | Passed |
| S2-E2E-02 | Search and update a member | Passed |
| S2-E2E-03 | Deactivate a member and confirm status | Passed |
| S2-E2E-04 | Two members with the same name stay separate | Passed |
| S2-E2E-05 | Create, search and update a guardian | Passed |
| S2-E2E-06 | Link a guardian to a junior member | Passed |
| S2-E2E-07 | Update guardian contact and verify the views | Passed |
| S2-E2E-08 | Invalid input is rejected with feedback | Passed (with finding S2-N1) |
| S2-E2E-09 | Under-18 rule blocks completion without a guardian | Passed |
| S2-E2E-10 | Unlink a guardian that is not linked | **Blocked** (first half passed) |

Details, observations and evidence notes are in `sprint-2-e2e-checklist.md`.

### What remains for a human

1. **S2-E2E-10** — the no-op unlink could not be driven reliably through the UI
   because extra tabs re-rendered instead of staying stale. A human should run
   the two-tab check documented in the checklist and mark it `Passed` or `Fail`.
2. **Screenshots** — 17 PNG files (16 distinct; one byte-identical duplicate)
   are saved outside the repository in
   `C:\Users\HP\Documents\Sprint2_Browser_Evidence\`, and all of them were
   inspected visually during the final documentation review. No screenshot
   exists for the E2E-10 no-op message. Recommended for the PR: one image per
   scenario outcome — `S2-E2E-01_member_created.png`,
   `S2-E2E-02_member_updated.png`, `S2-E2E-03_member_inactive.png`,
   `S2-E2E-04_duplicate_edited_list.png`, `S2-E2E-05_guardian_created.png`,
   `S2-E2E-06_two_juniors_linked.png`, `S2-E2E-07_member_shows_new_contact.png`,
   `S2-E2E-08_future_date_rejected.png` and
   `S2-E2E-09_registration_complete.png`. Copy them into
   `docs/testing/screenshots/sprint-2/` **only after the team approves**, and
   leave the originals in place.
3. **Acceptance sign-off** — automation is not a substitute for a human
   confirming the workflows before the Stories are marked Done in Jira.

### Note on S2-N1

The browser blocks an empty Name/Date of Birth and a malformed email via HTML5
validation before the request reaches the server, so those two server-side
messages are not visible through the normal form in a modern browser. This is
correct layered behaviour, not a defect, and is recorded as **S2-N1** in
`sprint-2-defect-log.md`. A future date of birth, which passes the browser's
checks, did reach the server and produced the expected 400 response and flash.

## Recommended next steps

1. Close out the **one blocked scenario** — a human should run the two-tab
   check for S2-E2E-10 documented in `sprint-2-e2e-checklist.md` and record
   `Passed` or `Fail`. The other nine scenarios already have executed results.
2. Obtain the authoritative Jira acceptance criteria for the seven Stories and
   compare them with the derived expectations in `sprint-2-test-plan.md`.
3. Obtain product decisions on S2-O1, S2-O2, S2-C1 and S2-C2 so the follow-up
   sprint can implement them without guessing.
4. Carry **S2-F1** (team player removal feedback) into the Team and Roster
   Management epic for Sprint 4.
5. Review the working-tree changes in GitHub Desktop, then commit and push from
   the team member's own account.
6. Re-run `python -m pytest` after any merge to `main` to confirm the suite is
   still 133 passed.

## Limitations of this handover

- The automated suite passes, which does **not** by itself mean the seven
  Stories meet every acceptance criterion. Human acceptance review is still
  required for all seven Stories.
- The Stories must not be marked Done in Jira on the strength of this document.
- No coverage percentage is reported, because no coverage tool was run.
- Line-level code coverage was not measured; coverage was assessed by
  Story-to-test mapping.
- **Browser verification was performed by automation, not by a human.** Nine of
  the ten scenarios passed; S2-E2E-10 is Blocked (first half passed). 17 PNG
  files are saved outside the repository in
  `C:\Users\HP\Documents\Sprint2_Browser_Evidence\`, and all were inspected
  visually during the final review; each image matched its scenario. No image
  exists for the S2-E2E-10 no-op message, and no image can substitute for human
  acceptance.
- **Screenshot coverage is uneven.** Some checklist claims were verified by page
  observation during the run rather than photographed; the checklist now flags
  each of those explicitly (for example E2E-05 search/update, E2E-09's stored
  `Started` status, and list-level effects).
- The `.venv` creation difficulty noted before this review is resolved. It was
  caused by the development tool's restricted file-access mode blocking writes
  to the system temporary directory, not by the project. With normal access,
  `python -m venv .venv` and `pip install -r requirements.txt` succeed, and all
  results in this handover were produced that way.
- The `.venv` directory is excluded by `.gitignore` and must not be committed.
  The temporary dependency and scratch directories used before the `.venv`
  existed were deleted during this review, and the temporary browser-test
  database was deleted after the run.
- **No test run was performed after deleting those scratch directories.** The
  final 133-passed run used the `.venv`, which is the environment described
  here.

## Confirmation of local-only changes

- All edits were made inside the project working directory opened in the
  development environment.
- No Git command that changes repository state was run: no add, stage, commit,
  push, fetch, pull, merge, branch or checkout.
- No pull request was created or merged.
- No Jira issue, status, story point or Epic assignment was changed.
- Nothing has been uploaded to GitHub. All changes remain in the local working
  tree for review.

## Upload details for the team member

- **Repository directory:** `C:\Users\HP\Documents\GitHub\warrigal-park-fc`
- **Branch (confirmed from `.git/HEAD`):**
  `feature/sprint-2-member-guardian-colacolaco` — already the checked-out
  branch, so **no branch change is required**.
- **Changed files (9):** 2 modified source files, 1 new test module, and 6 new
  documentation/manifest files. Confirmed with a read-only status check; no
  `.venv/`, `.env`, `instance/`, `__pycache__/`, `.pytest_cache/` or `*.db`
  entries appeared, and `git check-ignore` confirmed `.venv/` and `.env` are
  excluded by `.gitignore`.
- **Source diff scope:** 18 insertions and 4 deletions confined to
  `unlink_guardian_member` (`app/services.py`) and `guardian_unlink`
  (`app/routes.py`). No team or player removal code is present.

### Suggested commit message

```text
fix: correct guardian unlink feedback and add Sprint 2 test coverage
```

### Suggested pull request

- **Title:** `Sprint 2: Member and Guardian Management`
- **Base:** `main` — **Compare:** `feature/sprint-2-member-guardian-colacolaco`
- **Description must state honestly:**
  - automated suite reports 133 passed (0 failed, 0 skipped, 0 errors);
  - the guardian unlink no-op feedback defect (S2-D1) is fixed, with
    regression tests;
  - the team player removal change was reverted as out of scope and deferred
    to Sprint 4 as S2-F1;
  - **browser testing is still pending — all ten E2E scenarios are
    `Not Tested`**, so no claim of completed manual acceptance is made.

Do not state that manual testing passed. Do not merge without review.
