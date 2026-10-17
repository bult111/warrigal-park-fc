# Sprint 2 — Test Results

- **Sprint:** Sprint 2 — Epic: Member and Guardian Management
- **Repository:** `warrigal-park-fc`
- **Document status:** results of tests actually executed on the local working
  copy during Sprint 2 QA. No result in this document is estimated.

## Environment

| Item | Actual value |
|------|--------------|
| Operating system | Windows |
| Python | 3.13.1 |
| pytest | 8.3.3 (pinned in `requirements.txt`) |
| Flask | 3.0.3 (pinned in `requirements.txt`) |
| python-dotenv | 1.0.1 (pinned in `requirements.txt`) |
| Database used by tests | temporary SQLite file per test, created by `tests/conftest.py` |
| Internet access required for tests | No |

### Environment setup notes and limitations

1. The working copy arrived with **no virtual environment**. The Sprint 1
   `.venv/` belonged to a different computer, so `.venv/` was absent and Flask
   was not importable by the system interpreter.
2. **Resolved during the pre-upload review.** A standard `.venv` was created
   successfully in the project directory and the pinned dependencies installed
   from the unchanged `requirements.txt`:

   ```text
   python -m venv .venv
   .venv\Scripts\python.exe -m pip install -r requirements.txt
   ```

   `pip check` reports `No broken requirements found.` All commands and results
   in this document were produced with `.venv\Scripts\python.exe`. The
   environment is therefore **reproducible from `requirements.txt`**, and no
   dependency version was changed.
3. The earlier `.venv` creation failure (an `ensurepip` "permission denied"
   error while writing its bundled wheel to the system temporary directory) was
   caused by the development tool's restricted file-access mode, which blocked
   writes outside the project directory. With normal access the step above
   succeeds. It was **not** a project defect, and nothing in the project needed
   to change to work around it.
4. The temporary dependency directory and scratch directories used before the
   `.venv` existed were deleted at the end of the review. They are not part of
   the project and are excluded from version control.
5. Python 3.13.1 is newer than the version used in Sprint 1. The full suite
   passes on it, so no version incompatibility was observed.

## Baseline run (before any change)

Command (run before any Sprint 2 file was modified):

```text
python -m pytest
```

Result:

| Metric | Count |
|--------|------:|
| Collected | 79 |
| Passed | 79 |
| Failed | 0 |
| Skipped | 0 |
| Errors | 0 |
| Duration | 3.34s |

The measured baseline **matches** the Sprint 1 reported figure of 79 passing
tests, so the working copy contains the latest available Sprint 1 work. No
pre-existing baseline failure was found.

## Reconciling the test counts

Three different figures are quoted for the new tests. They measure different
things and **must not be added together**.

| Figure | Value | Basis |
|--------|------:|-------|
| Distinct pytest tests collected in the new module | **54** | Verified with `python -m pytest tests/test_member_guardian_workflows.py --collect-only -q` → `54 tests collected`. This is the only figure that changes the suite total (79 + 54 = 133). |
| Test functions written in the new module | **48** | Counted from `def test_` definitions. Three functions use `@pytest.mark.parametrize`, so 48 functions expand into 54 collected cases. |
| Sum of the per-Story mapping counts | **63** | 11 + 12 + 6 + 4 + 9 + 16 + 5, as documented in `sprint-2-test-plan.md`. This is a **coverage mapping**, not a test total. |

### Why the per-Story counts sum to 63

Nine tests evidence the acceptance behaviour of two Stories each, so they are
counted once under each. The mapping therefore double-counts exactly nine
tests:

```text
sum of per-Story counts             63
minus tests mapped to two Stories  - 9
= distinct tests                    54   ← matches pytest collection
```

| Test mapped to two Stories | Stories |
|---|---|
| `test_member_search_is_partial_and_case_insensitive` | -2, -3 |
| `test_member_search_route_returns_only_matches` | -2, -3 |
| `test_duplicate_names_distinguishable_in_list_and_detail_views` | -3, -5 |
| `test_guardian_create_persists_and_is_retrievable` | -2, -6 |
| `test_guardian_create_route_redirects_to_viewable_detail` | -2, -6 |
| `test_guardian_create_invalid_input_shows_feedback_and_stores_nothing` | -2, -6 |
| `test_guardian_search_partial_and_case_insensitive` | -3, -6 |
| `test_guardian_update_keeps_relationships_intact` | -7, -8 |
| `test_guardian_contact_update_reflected_on_member_page` | -7, -8 |

### Parametrized cases

```text
python -m pytest tests/test_member_guardian_workflows.py --collect-only -q
```

| Parametrized function | Collected cases |
|---|---:|
| `test_member_create_invalid_input_shows_feedback_and_stores_nothing` | 5 |
| `test_guardian_create_invalid_input_shows_feedback_and_stores_nothing` | 2 |
| `test_link_invalid_identifiers_rejected` | 2 |
| 45 non-parametrized functions | 45 |
| **Total** | **54** |

Per-Story mapping summary:

| Story | Mapping count | Of which new |
|---|---:|---:|
| MSD426GXUST25-2 Create Member Record | 11 | 10 |
| MSD426GXUST25-3 Search and Update Member | 12 | 10 |
| MSD426GXUST25-4 Deactivation of Members | 6 | 5 |
| MSD426GXUST25-5 Support Duplicate Member Names | 4 | 3 |
| MSD426GXUST25-6 Create, Search and Update Guardian | 9 | 7 |
| MSD426GXUST25-7 Link Guardians to Junior Members | 16 | 13 |
| MSD426GXUST25-8 Reflect Guardian Contact Updates | 5 | 4 |
| **Sum of mapping counts** | **63** | **52** |

The 52 "new mapped" entries reduce to the 54 collected cases because six
functions are parametrized and because nine tests are counted under two
Stories; the two effects overlap. The authoritative figure remains the pytest
collection total of **54**.

## Changes made during Sprint 2

### Retained (in scope for Member and Guardian Management)

1. **Defect fix S2-D1 — accurate feedback for a no-op guardian unlink.**
   `app/services.py`: `unlink_guardian_member` now validates that the guardian
   and member exist (raising `ServiceError` for unknown identifiers) and returns
   `True` only when a link row was actually deleted.
   `app/routes.py`: `guardian_unlink` now flashes a success message only when a
   link was removed, and `That member was not linked to this guardian.`
   otherwise.
2. **New tests.** `tests/test_member_guardian_workflows.py` — 48 functions
   collecting 54 cases across all seven Sprint 2 Stories.
3. No existing test was removed, weakened or renamed.

### Removed during the pre-upload review (out of scope)

An equivalent change had also been made to `remove_player_from_team`
(`app/services.py`) and `player_remove` (`app/routes.py`). Team and player
removal belongs to the **Team and Roster Management** epic, planned for
Sprint 4, so that change was **reverted** to keep Sprint 2 within its epic. No
test covered the reverted code, so the suite is unchanged by the revert. The
issue is recorded as **S2-F1** in `sprint-2-defect-log.md` for Sprint 4.

## Targeted run (new tests)

Command:

```text
.venv\Scripts\python.exe -m pytest tests/test_member_guardian_workflows.py -v
```

Result:

| Metric | Count |
|--------|------:|
| Collected | 54 |
| Passed | 54 |
| Failed | 0 |
| Skipped | 0 |
| Errors | 0 |
| Duration | 2.11s |

### Negative control for the defect fix

To prove the new tests actually detect the defect rather than merely passing,
the `guardian_unlink` route handler was temporarily reverted to the old
success-only behaviour and the tests were re-run. The control was executed
again during the pre-upload review in the clean `.venv` and reproduced the same
outcome.

| Run | Command (filtered) | Result |
|-----|--------------------|--------|
| Working-tree fix present | `... -m pytest tests/test_member_guardian_workflows.py -k "no_op or nothing_was_linked"` | 2 passed |
| Fix deliberately reverted | same command | **1 failed**, 1 passed, 52 deselected |
| Fix restored | `... -m pytest` | **133 passed** |

The single failure was
`test_unlink_route_reports_no_op_instead_of_success` — exactly the
Story MSD426GXUST25-7 / S2-D1 behaviour under repair. The failure appeared
**only** while the fix was reverted. After restoring the fix, the handler was
confirmed present in `app/routes.py` (line 218) and the full suite was re-run
green at 133 passed. No source file was left in the reverted state.

## Final full-suite run (after implementation and scope cleanup)

Command:

```text
.venv\Scripts\python.exe -m pytest
```

Result:

| Metric | Baseline | Final | Change |
|--------|---------:|------:|-------:|
| Collected | 79 | 133 | +54 |
| Passed | 79 | 133 | +54 |
| Failed | 0 | 0 | 0 |
| Skipped | 0 | 0 | 0 |
| Errors | 0 | 0 | 0 |
| Duration | 3.34s | 5.18s | +1.84s |

Per-module breakdown of the final run:

| Test module | Tests |
|-------------|------:|
| `tests/test_edge_cases.py` | 11 |
| `tests/test_guardians.py` | 6 |
| `tests/test_member_guardian_workflows.py` (new) | 54 |
| `tests/test_members.py` | 10 |
| `tests/test_players.py` | 11 |
| `tests/test_registration.py` | 13 |
| `tests/test_teams.py` | 7 |
| `tests/test_validation.py` | 12 |
| `tests/test_views.py` | 9 |
| **Total** | **133** |

## Pre-upload verification run (final state of the working tree)

After the scope cleanup (removing the out-of-epic team/player change), deleting
all temporary scratch and dependency directories, and leaving the source
unchanged, the suite was executed once more for upload evidence.

Branch at the time of this run:
`feature/sprint-2-member-guardian-colacolaco` (confirmed from `.git/HEAD`).

Commands:

```text
.venv\Scripts\python.exe -m pip check
.venv\Scripts\python.exe -m pytest
```

Result:

| Command | Output |
|---|---|
| `pip check` | `No broken requirements found.` |
| `pytest` | **133 passed in 5.09s** (0 failed, 0 skipped, 0 errors) |

This matches the final run above. No source file has been modified since this
run, so the recorded result describes the exact state of the working tree being
uploaded.

## Re-verification runs (documentation review)

The suite was run again during the documentation reviews to re-verify the
reported numbers before they are handed over.

Command:

```text
.venv\Scripts\python.exe -m pytest
```

Result (exact tail of the output, 2026-10-14):

```text
tests\test_validation.py ............                                    [ 93%]
tests\test_views.py .........                                            [100%]

============================= 133 passed in 4.77s =============================
```

An earlier review run on the same day produced `133 passed in 4.79s`. So the
verified current result is **133 collected, 133 passed, 0 failed, 0 skipped,
0 errors**. This matches the previously recorded final figures exactly; no test
was changed to obtain it.


## Coverage changes

Coverage was assessed by Story-to-test mapping rather than by a line-coverage
tool (no coverage plugin is pinned in `requirements.txt`, and none was added).

Newly covered behaviour:

- Route-level success **and** failure feedback for member and guardian create
  and edit, including that a rejected submission stores nothing.
- Route-level redirect targets after create/update (302 to the detail page).
- Member and guardian edit forms retaining typed values after a validation
  error, while the stored record is unchanged.
- Deactivation preserving registration history, guardian links and team
  placement, and being idempotent and reversible.
- Duplicate member names distinguished in the list and detail views, with
  isolated updates.
- The distinction between duplicate member names and duplicate registrations.
- Guardian linking visible from both the guardian and member sides, including
  unlink success, unlink no-op, and unlink with unknown identifiers.
- Guardian contact updates reflected on the member page and guardian pages,
  with no stale value remaining and no effect on other guardians.
- A structural guard that `guardian_members` holds no contact columns, so
  guardian contact is never duplicated.

Not covered (deferred by scope): team and player removal feedback (**S2-F1**).
The reverted code has no test, and the suite total is unaffected by the revert.

Behaviour that was already covered and did not need new tests is listed in
`sprint-2-test-plan.md`.

## Browser verification run

**Date of the browser run:** 2026-10-14 (derived from the screenshot file
timestamps, 19:43–20:10 local time; not assumed or invented).

A browser run was executed against the real application served on
`http://127.0.0.1:5001` with a temporary database
(`instance/sprint2_manual_check.db`, deleted after the run). It was driven by
browser automation, not by a human clicking through the interface.

| Test ID | Scenario | Result |
|---|---|---|
| S2-E2E-01 | Create and view a member | Passed |
| S2-E2E-02 | Search and update a member | Passed |
| S2-E2E-03 | Deactivate a member and confirm status | Passed |
| S2-E2E-04 | Two members with the same name stay separate | Passed |
| S2-E2E-05 | Create, search and update a guardian | Passed |
| S2-E2E-06 | Link a guardian to a junior member | Passed |
| S2-E2E-07 | Update guardian contact and verify the views | Passed |
| S2-E2E-08 | Invalid input is rejected with feedback | Passed (finding S2-N1) |
| S2-E2E-09 | Under-18 rule blocks completion without a guardian | Passed |
| S2-E2E-10 | Unlink a guardian that is not linked | **Blocked** (first half passed) |

Manual scenario counts: **9 passed, 1 blocked, 0 failed, 0 not tested.**

S2-E2E-10 is Blocked because the stale-tab reproduction of the no-op unlink
could not be driven reliably through the UI; its first half (unlinking a
linked member) passed. The underlying no-op behaviour is covered by automated
tests and the negative control. See `sprint-2-e2e-checklist.md` for the
observations and the two-tab procedure a human should run.

Screenshots **are** saved to disk for this run, in an evidence folder outside
the repository: `<EVIDENCE_DIR>\Sprint2_Browser_Evidence\` — **17 PNG
files** (16 distinct; `S2-E2E-04_duplicates_list.png` and
`S2-E2E-04_duplicates_isolated.png` are byte-identical) plus a `README.txt`
index. Each scenario in the checklist lists its image file names.

All 17 images were inspected visually during this documentation review. Every
image's content matched the scenario it is mapped to (for example the green
flash `Member 'Ava Testplayer' created.`, the grey **Inactive** badge on the
member page, the two `Casey Samename` rows with different dates of birth and
emails, the red flash `Date of birth cannot be in the future.` with the typed
values retained, and `Status: Complete` on Registration #1). The review also
confirmed which claims are **not** visible in any screenshot, and the checklist
now marks those explicitly. No screenshot exists for the S2-E2E-10 no-op
message, because that step was not executed.

One finding was recorded: **S2-N1** — the browser's HTML5 validation blocks an
empty Name/Date of Birth and a malformed email before the request reaches the
server, so those two server-side messages are not visible through the normal
form in a modern browser. This is correct layered behaviour, not a defect.
See `sprint-2-defect-log.md`.

The full automated suite was re-run after the browser session finished to
confirm the run left no state behind: **133 passed**.

## Failures and limitations

- **Unresolved test failures:** none. The verified current result is 133 passed,
  0 failed, 0 skipped, 0 errored (re-run on 2026-10-14: 133 passed in 4.79s).
- **Baseline problems:** none. The baseline was already green at 79 passed.
- **Not verified by any test run:** visual layout and styling; human acceptance
  of the workflows; and the business decisions listed in
  `sprint-2-test-plan.md` (duplicate same-season registrations, roster after
  withdrawal, inactive-member scope, guardian removal after completion).
- **No coverage percentage is reported**, because no coverage measurement tool
  was installed or run. Reporting a number would require fabricating it.
- **No test duration other than the measured values above** is reported.
- Passing tests do not by themselves prove a Story meets all acceptance
  criteria; human acceptance review remains necessary for all seven Stories.
- **Browser scenarios:** nine passed and one (S2-E2E-10) is Blocked, as
  recorded above. They were executed by browser automation rather than a human,
  so they do not replace human acceptance sign-off.
- **Screenshots:** 17 PNG files (16 distinct) are saved in the evidence folder
  `<EVIDENCE_DIR>\Sprint2_Browser_Evidence\` and all of them were
  inspected visually during this review. No image exists for the S2-E2E-10
  no-op message, and no image can prove that a human performed the runs — human
  confirmation remains outstanding.
- **Relationship between automated tests and browser checks:** the automated
  suite (133 tests) proves the service and route behaviour directly, including
  the S2-D1 no-op unlink path via `test_unlink_route_reports_no_op_instead_of_success`
  and its negative control. The browser run proves the same flows work end to
  end through the real UI for nine scenarios; the one UI gap (S2-E2E-10 no-op)
  is exactly the path the automated tests do cover.
