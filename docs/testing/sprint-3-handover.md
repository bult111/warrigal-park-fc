# Sprint 3 — Handover Notes

- **Sprint:** Sprint 3 — Epic: Registration and Eligibility
- **Stories:** `MSD426GXUST25-10` ... `MSD426GXUST25-14` (5 Stories, 15 Story Points)
- **Document status:** records only what was actually done and measured in this
  session. No planned result is presented as a completed result.
- **Session:** this session contained three phases — (1) verification and test
  authoring, (2) recovery after an external clean removed the work, (3) the S3-D1
  fix, the browser round, and the final documentation. All three are stated.

## 1. Repository state at the start of this phase

| Item | Value |
|---|---|
| Project path | `<PROJECT_ROOT>` — verified before any change |
| Branch at the start | `main`, working tree **clean** |
| HEAD | `86ebc70 Merge pull request: Sprint 2 Member and Guardian Management` |
| Result | The Sprint 3 files were **absent** — see section 2 |

## 2. What happened to the earlier Sprint 3 work

While the second phase was in progress, the working tree was changed by an
external process. The reflog recorded it precisely:

```text
86ebc70 HEAD@{2026-10-14 22:07:45}: checkout: moving from feature/sprint-3-... to main
86ebc70 HEAD@{2026-10-14 22:07:45}: reset: moving to HEAD
86ebc70 HEAD@{2026-10-14 22:07:33}: checkout: moving from main to feature/sprint-3-...
86ebc70 HEAD@{2026-10-14 22:07:33}: reset: moving to HEAD
```

A branch `feature/sprint-3-registration-eligibility-sandip001159852` was created
and `main` re-checked-out, and the working tree was reverted to `86ebc70`.
Tracked modifications were discarded and untracked files were removed. No
dangling commit held the work — both `main` and the new branch pointed at
`86ebc70`.

**Files lost in that event:** the Sprint 3 test module, all six Sprint 3
documents, the `CHANGELOG.md` 1.2.0 entry, and a screenshot folder.

**How the loss was handled.** Work stopped and the intended branch was
confirmed. The branch was intentional, so the work was recovered rather than
restarted. Nothing was reset or cleaned.

## 3. Recovery method (as executed)

1. **Repository protected.** Path, branch and `git status --porcelain` were
   checked; the tree was clean, so a branch switch could not lose anything.
2. **Branch switched once**, as agreed, to the existing
   `feature/sprint-3-registration-eligibility-sandip001159852`. No reset, no
   clean, no new branch.
3. **Test ids recorded.** pytest's surviving cache
   (`.pytest_cache/v/cache/nodeids`) still held **103** node ids for the lost
   module. They were used as the acceptance checklist for the rebuild.
4. **Test module rebuilt** as `tests/test_registration_sprint3.py` (see the
   naming note below) and then verified mechanically against the manifest:

   ```text
   functions in new module : 80
   functions in manifest   : 80
   MISSING from module     : none
   EXTRA in module         : none
   ```

   The rebuilt module collected and passed **103 cases** on its first run, so it
   covered the same behaviour as the lost design.
5. **Documents rebuilt**, then updated with the new results rather than restored
   verbatim, because this phase produced new evidence.

### Naming note

The rebuilt module is **`tests/test_registration_sprint3.py`**. It covers the
same 103 cases as the lost module; only the filename differs. If the team
prefers the original name, renaming the file is a purely mechanical change with
no effect on the suite.

### What could not be restored

- **The original file bytes.** The rebuild was written from the design notes and
  checked against the preserved list of test ids. Test names and coverage are
  complete; comment wording and minor formatting may differ from the lost
  original.
- **The lost screenshots.** The PNGs saved into the repository were deleted. The
  browser round in this phase therefore captured a **fresh set of 20 images**;
  none of the earlier images were reused or presented as new evidence.

## 4. Baseline (measured in this session, before any change)

| Command | Result |
|---|---|
| `.venv\Scripts\python.exe -m pytest -q` | 133 collected, **133 passed**, 0 failed, 0 skipped, 0 errors (5.29s) |

This matches the Sprint 2 reported figure, confirming the working copy held the
latest committed work and no failing test was inherited.

## 5. Work performed in this phase

### 5.1 S3-D1 defect fix

A member row whose stored `date_of_birth` is not a valid ISO date previously
raised an unhandled `ValueError`, producing HTTP 500 on the member detail page
and blocking the guardian rule. The fix refuses completion with a friendly
message and never treats an unreadable date as proof of adulthood.

| File | Change |
|---|---|
| `app/models.py` | Added `safe_parse_date()` returning `None` instead of raising |
| `app/services.py` | Added `UNREADABLE_DATE_OF_BIRTH_MESSAGE`; `can_complete_registration` refuses unreadable dates; `_member_is_junior` and `guardian_linked_members` no longer raise; removed an unused import |
| `app/routes.py` | `member_detail` uses `safe_parse_date` and yields no age when unreadable |
| `app/templates/member_detail.html` | Shows `(age cannot be read from the stored date)` |
| `app/templates/guardian_detail.html` | Shows an em dash for an unreadable linked-member age |
| `tests/test_registration_sprint3.py` | 14 new regression tests |

No schema change and no migration. The rule for valid dates is unchanged.

### 5.2 Browser end-to-end round

All 14 scenarios in the checklist were executed against the live application on a
disposable database, with screenshots captured for each executed scenario.

| Result | Count |
|---|---:|
| Executed | 14 |
| Fully passed | 12 |
| Passed (partial, with the gap named) | 2 |
| Failed | 0 |
| Blocked / Not tested | 0 |
| Additional S3-D1 browser confirmation | 1 |
| Screenshots | 20 |

Screenshots and their hashes: `docs/testing/sprint-3-screenshots.txt`. The two
partial scenarios are S3-E2E-13 (stale-tab submission not reproducible through
the UI) and S3-E2E-14 (the automation tool cannot drive a native `type=date`
control, so server-side invalid-date rules rest on the automated tests).

### 5.3 Findings review

S3-O1 to S3-O4, S3-C1, S3-C2 and S3-L1 were re-checked against the code. None
required a change to satisfy an existing acceptance criterion. Two new records
were added: **S3-O5** (the rule is enforced in application code, not by the
database) and **S3-L2** (no `max` on the Date of Birth control). Details are in
`sprint-3-defect-log.md`.

## 6. Test results

All commands run with `.venv\Scripts\python.exe` in the project directory.

| Run | Command | Result |
|---|---|---|
| Baseline | `-m pytest -q` | 133 passed |
| Rebuilt module, first run | `-m pytest tests/test_registration_sprint3.py -q` | **103 passed** — reconstruction verified |
| S3-D1 regression only | `-m pytest tests/test_registration_sprint3.py -q -k "unreadable or readable_stored"` | **14 passed** |
| Sprint 3 module, final | `-m pytest tests/test_registration_sprint3.py -q` | **117 passed**, 0 failed |
| Full suite, final | `-m pytest -q` | **250 passed**, 0 failed, 0 skipped, 0 errors (10.40s) |
| Pre-existing suite only | `-m pytest -q --ignore=tests/test_registration_sprint3.py` | 133 passed |
| Dependency check | `-m pip check` | No broken requirements found. |
| Syntax check | `-m compileall -q app tests` | exit 0 |

Environment: Python 3.13.1, pytest 8.3.3, Flask 3.0.3, SQLite 3.45.3.

### Negative controls (proof the tests are meaningful)

| Control | Mutation | Result |
|---|---|---|
| 1 | `safe_parse_date` made to re-raise | **12 failed**, 1 passed |
| 2 | Guardian check disabled | **14 failed**, 103 passed |
| 3 | `age < 18` changed to `age <= 18` | **1 failed**, 116 passed |
| 4 | History member filter removed | **24 failed** |

All four mutations were reverted immediately; `git diff -- app/` was inspected
afterwards and the suite was re-run green.

## 7. Findings summary

- **Fixed:** S3-D1, with 14 regression tests, four negative controls and two
  browser confirmations.
- **Product decisions required (unchanged, no behaviour altered):** S3-O1
  (guardian removed after completion), S3-O2 (registering an Inactive member),
  S3-O3 (retargeting a registration to another member), S3-O4 (free-text season
  and age group).
- **Carried forward:** S3-C1 (duplicate same-season registrations) and S3-C2
  (withdrawn registration still on a roster).
- **Limitations:** S3-L1 (no timestamps, so history cannot show dates) and S3-L2
  (no `max` on the date control).
- **Recorded as expected behaviour / not defects:** S3-O5, S3-N1, S3-N2.
- **Investigated and confirmed correct:** validation before write, whitespace
  trimming, guardian rule scoping, idempotent withdrawal, history isolation,
  error-path form behaviour, and the eighteenth-birthday boundary.

## 8. Verification of the five Stories

| Story | Title | SP | Automated | Browser |
|---|---|---:|---|---|
| `MSD426GXUST25-10` | Create Registration | 3 | **Pass** | **Pass** |
| `MSD426GXUST25-11` | Amend Registration | 2 | **Pass** | **Pass** |
| `MSD426GXUST25-12` | Withdraw Registration | 2 | **Pass** | **Pass (partial on stale tabs)** |
| `MSD426GXUST25-13` | View Member Registration History | 3 | **Pass** | **Pass** |
| `MSD426GXUST25-14` | Enforce Under-18 Guardian Rule | 5 | **Pass** | **Pass** |

**These rows are verification results, not acceptance.** No Story has been
accepted and none should be marked Done in Jira on the strength of this document.
The browser round was automation, not a human.

## 9. Limitations of this handover

1. **No human executed the scenarios.** The browser round used automation driving
   a real browser; human acceptance review remains outstanding for all five
   Stories.
2. **Two browser scenarios are partial**, and both state the unverified half.
3. **The test module was rebuilt**, so it covers the same 103 cases as the lost
   module but is not byte-identical to it, and it is named
   `test_registration_sprint3.py`.
4. **No coverage percentage is reported**; no coverage tool was run.
5. **Jira acceptance criteria were not available**, so expectations were derived
   from the repository documents listed in the test plan.
6. **No CI or GitHub Actions run was performed or observed.**
7. **One assertion failed during this session** and is documented rather than
   hidden: `test_unreadable_stored_dob_member_page_returns_200` used a
   too-broad `b"age "` check that matched the word "Page" in the HTML title. The
   application was correct (HTTP 200); the assertion was replaced with a precise
   one.
8. The `.pytest_cache`, `.venv`, `__pycache__` and `instance/` directories are all
   git-ignored and are not part of the change set. The disposable E2E database was
   deleted after the run.

## 10. Confirmation of local-only changes

- All edits were made inside the project working directory.
- **No Git command that changes repository state was run** other than the single
  branch switch agreed beforehand: no add, stage, commit, push,
  fetch, pull, merge, reset, clean or stash.
- No pull request was created or merged.
- No Jira issue, status, Story Point or Epic assignment was read or changed.
- Nothing was uploaded to GitHub.
- No `.env` file was created or read; no secret was written.
- No database, virtual environment or cache file is part of the deliverable.

## 11. Suggested commit and next steps

### Suggested commit message

```text
fix: handle unreadable stored dates of birth and add Sprint 3 coverage
```

### Suggested pull request

- **Title:** `Sprint 3: Registration and Eligibility`
- **Base:** `main` — **Compare:**
  `feature/sprint-3-registration-eligibility-sandip001159852`
- **Description must state honestly:**
  - the full suite reports **250 passed** (0 failed, 0 skipped, 0 errors), from a
    measured baseline of 133;
  - `tests/test_registration_sprint3.py` holds 117 cases: 103 Sprint 3 cases plus 14 for the S3-D1 fix;
  - **defect S3-D1 is fixed** — an unreadable stored date of birth no longer
    causes HTTP 500 and no longer permits completion — with regression tests and
    negative controls;
  - **browser round executed**: 14 scenarios, 12 fully passed, 2 partial, 20
    screenshots, all captured by browser automation and **not** by a human;
  - four product decisions (S3-O1 to S3-O4) and two carried-forward items
    (S3-C1, S3-C2) remain open and no behaviour was changed for them.

Do not state that human testing passed. Do not mark any Story Done in Jira on the
strength of these documents. Do not merge without review.

### Recommended next steps

1. Have a person run the 14 scenarios (or at least the two partial ones) and
   record their own outcomes.
2. Obtain the authoritative Jira acceptance criteria and compare them with the
   derived expectations, especially whether Story -13 expects registration dates.
3. Decide S3-O1 to S3-O4, then update `README.md`, `docs/architecture.md` and
   `docs/project-scope.md` to match the chosen behaviour.
4. Schedule S3-C1 and S3-C2 as backlog items.
5. Review the module filename `tests/test_registration_sprint3.py` before
   merging.
6. Re-run `python -m pytest` after any merge to confirm the suite is still 250
   passed.


================================================================================
SUPPLEMENTARY ROUND HANDOVER - 2026-10-14 (22:56 to 23:10)
================================================================================

Purpose: close the two scenarios left partial by the previous round, and save
this round's real browser screenshots to the local Windows desktop as well as the
project evidence folder.

## A. Environment and repository state for this round

| Item | Value |
|---|---|
| Project path | `<PROJECT_ROOT>` |
| Branch (verified before any action) | `feature/sprint-3-registration-eligibility-sandip001159852` |
| HEAD | `86ebc70` |
| Working tree at start | Already dirty with the previous round's committed-pending work (5 modified source/template files, `CHANGELOG.md`, the Sprint 3 documents, the test module, the screenshots folder). Preserved untouched; nothing was cleaned, reset or overwritten. |
| Branch changed this round? | **No.** No checkout, switch, commit, push, merge, reset or clean was run. |
| Application code changed this round? | **No.** |

## B. Desktop path

| Item | Value |
|---|---|
| Real desktop | `<USER_PROFILE>\Desktop` |
| How verified | `HKCU\...\Explorer\User Shell Folders\Desktop` and `.NET GetFolderPath('Desktop')` both returned `<USER_PROFILE>\Desktop`; `<USER_PROFILE>\OneDrive\Desktop` does not exist |
| OneDrive redirection | None - the default path in the task was correct |
| Evidence folder created | `<EVIDENCE_DIR>\Sprint3_Test_Evidence\` |

## C. What was executed

| Scenario | Previous status | Status after this round |
|---|---|---|
| S3-E2E-13 Withdrawal from a stale browser tab | PASS (partial) | **PASS** |
| S3-E2E-14 Invalid date of birth and server-side validation | PASS (partial) | **PASS (partial)** - gap narrowed to one browser interaction |

- Disposable database `instance/sprint3_e2e_supplement.db`, initialised with the
  project's real command `flask --app run.py init-db`, deleted after the run.
- 9 new screenshots captured from the real browser.
- No application code changed, so no fix or regression test was needed.

## D. Key results

**S3-E2E-13 (now PASS).** Tab A withdrew a registration (`POST .../withdraw` ->
302). A second tab, left stale with `Status: Started` and the Withdraw button
still rendered, then submitted the same form: a real second POST to the same
endpoint, also 302. Final database state: row retained as `Withdrawn`, row count
unchanged, no duplicate `(member_id, season)` pair, no error. Both POSTs are
recorded in the server log and in two network captures with distinct timings
(12.46 ms and 23.53 ms) and complete request/response bodies.

**S3-E2E-14 (still partial).** Confirmed in the browser: the native `type=date`
control accepts a future year (no `max`), refuses impossible dates, and blocks an
empty date via `required`. Server-side rejection of future, impossible,
malformed, empty and whitespace dates was confirmed by seven real HTTP POSTs
(**API supplemental test, not browser**). The unreadable stored date of birth
path was re-verified: member page returns 200, completion is refused with 400 and
a clear message, and the member is not passed as an adult.
**Gap:** submitting a future date through the browser form itself - the
automation tool cannot drive the segmented date control to a complete value.

## E. Automated results for this round

```
python -m pytest tests/test_registration_sprint3.py -q -k "withdraw or unreadable or invalid_date_of_birth or readable_stored"
  -> 34 passed, 83 deselected
python -m pytest tests/test_registration_sprint3.py -q   -> 117 passed
python -m pytest -q                                      -> 250 passed, 0 failed, 0 skipped, 0 errors
```

## F. Screenshots and verification

9 PNG files were saved to BOTH:
- `<EVIDENCE_DIR>\Sprint3_Test_Evidence\` (real desktop), and
- `docs/testing/screenshots/sprint-3/` (project evidence, relative path).

All 9 are non-zero, structurally valid PNGs, and byte-identical between the two
locations (SHA-256 compared). Full record:
`docs/testing/sprint-3-screenshot-verification.txt`.

Filenames delivered as requested:
- `S3-E2E-13-A-withdrawal-result.png`
- `S3-E2E-13-B-stale-tab-attempt.png`
- `S3-E2E-13-final-record-state.png`
- `S3-E2E-14-future-date-attempt.png`
- `S3-E2E-14-server-validation-result.png`
- `S3-E2E-14-unreadable-dob-member-detail.png`
- `S3-E2E-14-unreadable-dob-registration-rejection.png`

Plus two additional genuine captures: `S3-E2E-13-A0-both-tabs-before-withdrawal.png`
(both tabs loaded before withdrawal) and `S3-E2E-13-B-stale-tab-before-submit.png`
(the stale page proving `Started` was still displayed).

## G. Important caveat on one filename

`S3-E2E-14-server-validation-result.png` is a **real browser HTTP 400** captured
from the live application, but the rule it illustrates is the under-18 guardian
rule on `POST /registrations/new`, **not** a date-of-birth rule. The
date-of-birth server validation results are recorded as text in
`sprint-3-api-dob-validation.txt`, because the browser could not submit a future
date. The filename was requested by the task; its meaning is stated here and in
the checklist so it is not misread.

## H. What is still not verified

1. Submitting a **future date** through the browser form (tool limitation).
2. A true **simultaneous** double-submit race on withdrawal (sequential
   submissions only).
3. The other 12 E2E scenarios were **not** re-executed this round; their earlier
   results remain historical.

## I. Recommended next steps

1. Have a human perform the two remaining gaps above, ideally by pasting a future
   date into the date field.
2. Review the 9 new screenshots on the desktop and the project copies.
3. Decide whether to commit the 9 new PNGs under
   `docs/testing/screenshots/sprint-3/` or keep screenshots outside the repo.
4. Decide whether to add `max` to the Date of Birth input (S3-L2, presentation
   only).
5. Then proceed to GitHub Desktop review and commit on
   `feature/sprint-3-registration-eligibility-sandip001159852`.
