# Final Verification Report — Warrigal Park FC

**Date of verification:** 2026-10-16
**Code verified:** `fd7b68c15d92e0511b8609f3c9ce84c9943724ee` — the real tip of
GitHub `main`
**Tree verified:** `a42f0465fee7fddeb6e8d498a5c2e86ca6d857fd`
**Overall result:** 348 unit tests pass; 37/37 browser scenarios pass; **no
application-code defect was found**, so no application code was changed. Four
documentation files were corrected after checking the real remote state.

**Path placeholders:** `<PROJECT_ROOT>` is the repository checkout;
`<TEST_WORKSPACE>` is the scratch workspace outside the repository;
`<LOCAL_ARCHIVE>` is the local archive outside the repository that holds the
internal test artifacts excluded from this repository. See `test-environment.md`.

---

## 1. What was verified, and how

| Item | Value |
|------|-------|
| Repository | https://github.com/bult111/warrigal-park-fc |
| Remote `main` at verification time | `fd7b68c15d92e0511b8609f3c9ce84c9943724ee` (via GitHub REST API) |
| Remote `main` tree | `a42f0465fee7fddeb6e8d498a5c2e86ca6d857fd` |
| Local branch tested | `audit/final-verification-20261016` |
| Base commit of that branch | `3205042ade4beef2753dde4c86fbb5292dc418c8` |
| Tree of that base commit | `a42f0465fee7fddeb6e8d498a5c2e86ca6d857fd` |
| Trees identical? | **Yes** — the tested content is byte-identical to remote `main` |
| `main` branch modified? | **No** — local `main` is still `1ec3a25` |
| Pushed / merged / PR created? | **No** |

### Why the tested commit is not literally `fd7b68c`

`git fetch` cannot reach `github.com:443` from this machine, so no remote objects
could be downloaded. However, `fd7b68c` is a **merge commit with two parents**
(`1ec3a25` and `3205042`), and its single parent tree resolves locally: the local
commit `3205042` (`docs/align-auto-age-feature-status`, also present on the
remote under the same SHA) has tree `a42f0465fee7fddeb6e8d498a5c2e86ca6d857fd`,
which the GitHub API reports as the tree of `fd7b68c`. The equivalence was
confirmed directly:

```text
git rev-parse '3205042^{tree}'   ->  a42f0465fee7fddeb6e8d498a5c2e86ca6d857fd
GitHub API, fd7b68c tree         ->  a42f0465fee7fddeb6e8d498a5c2e86ca6d857fd
```

So the working tree tested here contains exactly the files of remote `main`.
This is a content equivalence, not a claim to have fetched the merge commit.

### Remote facts established from the GitHub REST API

- Remote branches (11): `main`, `docs/align-auto-age-feature-status`,
  `docs/sprint-4-merge-status`, `feature/configuration-improvements`,
  `feature/project-documentation`, `feature/qa-and-validation`,
  `feature/sprint-1-qa-release`, `feature/sprint-2-member-guardian-colacolaco`,
  `feature/sprint-3-registration-eligibility-sandip001159852`,
  `feature/sprint-3-season-age-reference-leo0318-cpu`,
  `feature/sprint-4-team-roster-leo0318-cpu`.
- The branch `feature/auto-age-team-assignment-guardian-adult-leo0318-cpu`
  **does not exist on the remote.** It exists only as a local branch in this
  working copy and points at `1ec3a25`.
- Pull requests: 6 in total, all closed and merged — #1 (`ee2cf04`), #2
  (`86ebc70`), #3 (`d6ee6a0`), #4 (`98fa25b`), #5 (`3dbaf1e`), #6 (`fd7b68c`).
- The feature commit `1ec3a25` was **not** merged by any pull request. It is an
  ordinary commit pushed straight onto `main`.
- `feature/sprint-3-season-age-reference-leo0318-cpu` (`8ac23ef`) is the **only**
  remote branch not contained in `main`.
- GitHub Actions: **0 workflow runs** (`total_count: 0`). No CI is configured and
  no CI result exists for any commit.

### Preservation of work found in the working copy

Before any change, the working copy contained untracked work that was **not**
touched, reset, cleaned or committed:

- `docs/assessment-evidence/`
- `docs/testing/auto-age-guardian-browser-acceptance-20261016.md`
- `docs/testing/screenshots/auto-age-guardian-20261016/`

`main` itself was left at `1ec3a25`. The verification was performed on a separate
branch, and all new evidence was written to new paths.

---

## 2. Automated test results

**Command actually executed** (project virtual environment, project root):

```text
.\.venv\Scripts\python.exe -m pytest -q
```

**Result actually observed:**

```text
........................................................................ [ 20%]
........................................................................ [ 41%]
........................................................................ [ 62%]
........................................................................ [ 82%]
............................................................             [100%]
348 passed in 9.94s
```

| Metric | Value |
|--------|-------|
| Passed | **348** |
| Failed | 0 |
| Errors | 0 |
| Skipped | 0 |
| Exit code | 0 |
| Commit / tree tested | `fd7b68c` / `a42f0465` (via `3205042`, identical tree) |
| Re-run after all documentation edits? | **Yes** — the result above is the post-edit run |

Raw output: `pytest-results.txt`. The full collected-test inventory (348 ids,
`pytest-collected-tests.txt`) is kept in the local test archive; see
"Archived outside the repository" in section 5.

### Required test modules are discovered and executed

```text
tests/test_age_groups.py                35
tests/test_auto_assignment.py           23
tests/test_guardian_adult.py            19
tests/test_member_dob_consistency.py     7
tests/test_edge_cases.py                11
tests/test_guardians.py                  6
tests/test_member_guardian_workflows.py 54
tests/test_members.py                   10
tests/test_players.py                   17
tests/test_registration.py              13
tests/test_registration_sprint3.py     112
tests/test_teams.py                      9
tests/test_validation.py                12
tests/test_views.py                     20
--------------------------------------------
348 tests collected
```

Every module named in the task brief is present, discovered and executed.

### Other checks

| Command | Result |
|---------|--------|
| `git diff --check` | Clean — exit code 0, no whitespace/conflict-marker output |
| `.\.venv\Scripts\python.exe -m compileall -q app tests` | Clean — exit code 0 |

### Test-number reconciliation

| Figure | Where recorded | Meaning |
|--------|----------------|---------|
| 267 passed | `CHANGELOG.md` 1.3.0, Sprint 4 docs, README | **Historical.** Sprint 4 state, before the automatic age-group / guardian work. Preserved as-is. |
| 335 passed | not currently shown (superseded) | **Historical.** Recorded while the feature work was still described as unmerged. |
| 348 passed | `CHANGELOG.md` 1.4.0 and 1.4.1, README | **Current, and independently re-run on 2026-10-16** against tree `a42f0465`. Confirmed identical. |

No historical figure was deleted or re-labelled.

### Dependency installation

No installation was required. The existing `.venv` already satisfied
`requirements.txt`; the run used Python 3.10.11 with Flask 3.0.3,
python-dotenv 1.0.1 and pytest 8.3.3. See `test-environment.md`.

---

## 3. Browser end-to-end acceptance

Executed against a real Flask instance in a real Microsoft Edge browser over the
Chrome DevTools Protocol, using an **isolated temporary SQLite database**.

- **Result: 37 / 37 scenarios PASS, 0 FAIL, 0 not executed.**
- Full detail and per-scenario narrative: `browser-acceptance-results.md`.
- Screenshots: `../screenshots/final-verification-20261016/` (22 real PNG captures).
- Raw console logs and machine-readable per-scenario results are **not** kept in
  this repository; they are preserved in the local test archive (see
  "Archived outside the repository" in section 5).
- Authoring scripts (`run1.mjs`, `run2.mjs`, `cdp.mjs`, `init_temp_db.py`,
  `inject_legacy.py`, `db_dump.py`) were run from a scratch workspace outside the
  repository, `<TEST_WORKSPACE>`, and are copied into the local test archive.

Two rows were **injected by script** (not by the application) to reproduce legacy
data: a guardian with an unreadable `date_of_birth`, and a member whose date of
birth no longer matches an existing team assignment. The injection script is
preserved in the local test archive as `inject_legacy.py`; every behavioural
assertion about them was made through the UI.

### Scenario table

| # | Scenario | Expected | Actual | Status | Screenshot(s) |
|---|----------|----------|--------|--------|---------------|
| 1 | **B1a** Dashboard opens with zero data | HTTP 200, title "Dashboard", stat cards present | title "Dashboard — Warrigal Park FC", all stat cards rendered | PASS | `01-dashboard-empty.png` |
| 2 | **B10a** Empty-state pages for every list | Each list page shows its empty-state message | empty states verified for `/members`, `/guardians`, `/registrations`, `/teams` | PASS | — |
| 3 | **B2a** Create members through the form | Each member is created and its detail page opens | 11 members created and listed | PASS | `02-members-list.png` |
| 4 | **B2b** Search members by partial name and by no-match | Search returns matches; unmatched search shows the empty state | partial-name search and no-match search both correct | PASS | — |
| 5 | **B3** Update a member | Edited values persist and are shown | phone updated to 555-0100 and displayed | PASS | — |
| 6 | **B4** Deactivate and reactivate a member | Status toggles; the row is never deleted | Inactive then Active; member row retained throughout | PASS | `03-member-detail.png` |
| 7 | **B8a** Create teams | Teams created and listed with season and age group | 6 teams created | PASS | — |
| 8 | **B8b** Rename a team | New name stored and displayed | renamed to "Tigers Blue" and back to "Tigers" | PASS | — |
| 9 | **B8c** Remove a team keeps members and registrations | Removing a team deletes only the team | team removed after confirming the dialog; members intact | PASS | — |
| 10 | **A1a** Age group computed from date of birth and season | Registration stores the computed group | Mia Minor 2016-08-20 recorded as U12 for 2026 | PASS | `04-registration-age-group.png` |
| 11 | **A1b** Age-group boundary around season-age 5/6 | Season age 6 is U8 and season age 5 is U6 | 2020-12-31 → U8; 2021-01-01 → U6 | PASS | — |
| 12 | **A2** A hand-submitted age group cannot override the computed one | A POST carrying `age_group=Seniors` is ignored | submitted `Seniors`; stored value is the computed U14 | PASS | — |
| 13 | **A3** A member below the minimum age cannot be registered | HTTP 400, clear message, no registration row | refused with the minimum-age message; no row created | PASS | `05-below-minimum-age-rejected.png` |
| 14 | **G1** An adult guardian is verified as an adult | Guardian detail reports a verified adult | Ada Adult (1980-07-07) shown as "verified adult" | PASS | `06-guardian-adult-verified.png` |
| 15 | **G2** An under-18 guardian is rejected | HTTP 400, adult requirement, no guardian row | refused: "A guardian must be at least 18 years old."; no row created | PASS | `07-guardian-underage-rejected.png` |
| 16 | **B5** Update a guardian | Edited guardian values persist | guardian phone updated and displayed | PASS | — |
| 17 | **A4+A6a** Complete registration auto-assigns; empty-team tie breaks on lowest team id | Leo Junior (U16) joins Tigers | assigned to 'Tigers' (tie between empty U16 teams broken by lowest id) | PASS | `08-auto-assign-tiebreak.png` |
| 18 | **A5+A6b** Fewest-players-first beats team id | Noah Net (U16) joins Lions | assigned to 'Lions' because it had fewer players | PASS | — |
| 19 | **A7** No matching team means no wrong assignment | Player stays unassigned and the UI says so | "currently unassigned" notice shown; no team row created | PASS | `09-no-matching-team.png` |
| 20 | **A8** Creating a matching team later assigns the waiting player | Sam Seniorish appears on the new U18 team | Juniors (U18) created; Sam automatically placed on it | PASS | `10-auto-assign-on-team-create.png` |
| 21 | **A9** Creating a new team never silently moves an assigned player | Falcons stays empty; Leo in Tigers, Noah in Lions | Falcons empty; Leo still in Tigers, Noah still in Lions | PASS | — |
| 22 | **G4a** A junior with no eligible guardian cannot complete a registration | Completion refused with the guardian-rule message | Complete refused for Mia Minor | PASS | `11-junior-missing-guardian-rejected.png` |
| 23 | **B6** Link a guardian to a member and view both directions | Both pages show the link | guardian → member and member → guardian both correct | PASS | `12-guardian-linked-junior.png` |
| 24 | **G4b** Completing after an adult guardian is linked auto-assigns the player | Mia Minor completes and joins Eagles (U12) | completed; auto-assigned to Eagles (U12) | PASS | `13-complete-after-guardian-shows.png` |
| 25 | **A10-prep** Junior with an adult guardian completes and joins the matching U8 team | Boundary Kid is auto-assigned to Cubs | completed; auto-assigned to Cubs (U8) | PASS | — |
| 26 | **B9** Add, move and remove a player manually | Each manual action accepted and reflected | remove → add → move → remove all succeeded | PASS | `14-manual-player-management.png` |
| 27 | **B9-neg** A member without a Complete registration cannot be added | Refused with an eligibility message | refused: no Complete registration for the team's season | PASS | — |
| 28 | **B7** Create, amend and withdraw a registration, preserving history | Amend recomputes the age group; withdrawal keeps the record | created U14 → amended to 2028 U16 → withdrawn; history retains the row | PASS | `15-registration-history-withdrawn.png` |
| 29 | **B12** Roster page shows player contact details | Roster lists the team members | Eagles roster lists Mia Minor with season and age group | PASS | `16-team-roster.png` |
| 30 | **G5** A compatible date-of-birth change keeps registrations consistent | Registration age group rewritten with the new date of birth | 2014-04-04 → 2016-04-04 rewrote the 2026 registration U14 → U12 | PASS | `17-dob-change-consistent.png` |
| 31 | **G6+G7+G8** A date-of-birth change that would break a team assignment is refused atomically | HTTP 400, no partial write, no move, no duplicate | refused; date of birth unchanged; registration still U16; exactly 1 roster row | PASS | `18-dob-change-refused.png` |
| 32 | **B10b** Invalid email is rejected | Client-side validation blocks it; the server also rejects it | browser flagged it; server returned "Email address is not valid."; no member created | PASS | — |
| 33 | **B10c** Invalid season is rejected | A non four-digit season is refused | rejected with the four-digit-year message | PASS | — |
| 34 | **B10d** Unknown records redirect with a friendly flash | No traceback for missing records | all four unknown-record paths flashed the expected message | PASS | — |
| 35 | **B1b** Dashboard reflects the created data | Non-zero counts | `{"Total Members":11,"Active Members":11,"Guardians":1,"Registrations":8,"Teams":6}` | PASS | `19-dashboard-final.png` |
| 36 | **G3** An unreadable guardian date of birth is never treated as an adult | Guardian shown as not verified; cannot satisfy the under-18 rule | "Not verified as an adult"; Complete registration for the linked junior refused | PASS | `20-legacy-guardian-not-verified.png`, `21-legacy-junior-complete-rejected.png` |
| 37 | **A10** An incompatible existing team assignment is reported, not silently moved or duplicated | Saving surfaces the conflict and changes no team row | warning: *"the player is in 'Cubs' (U8) but their age group for 2026 is U10"*; exactly 1 row retained | PASS | `22-assignment-conflict-reported.png` |

**Failure, partial and unexecuted scenarios: none.** Every scenario in the plan
ran to completion. Six `400` responses were observed and all were the intended
validation refusals; no `500`, no traceback and no browser console error occurred.

### Database isolation

| Database | Touched? |
|----------|----------|
| `instance\warrigal_park_fc.db` (real project DB) | **No** — the file does not exist on this machine and was never opened |
| `instance\presentation_demo.db` (pre-existing, 2026-10-15) | **No** |
| `….final-verify-20261016\final-verify.db` (acceptance) | Yes — the only DB the tested server used |
| pytest `tmp_path` databases | Yes — created and discarded by the suite |

The final acceptance database state is recorded in `database-state-final.txt`:
11 members, 2 guardians, 8 registrations, 6 teams, 4 team assignments, **no
member with two teams in one season**, and exactly one age-group mismatch — the
deliberately injected one, which the UI reports.

---

## 4. Documentation corrections

Only verified problems were changed. No application code, test, dependency,
database or historical evidence file was modified.

| # | File | Problem found | Correction | Evidence |
|---|------|---------------|------------|----------|
| 1 | `README.md` | Said the feature commit `1ec3a25` "is the current tip of `main`" | Recorded that the tip of `main` is the PR #6 merge commit `fd7b68c15d92e0511b8609f3c9ce84c9943724ee`, and that `1ec3a25` is the feature commit, not the tip | GitHub API `branches/main`; local `git log` |
| 2 | `README.md` | Claimed `feature/auto-age-team-assignment-guardian-adult-leo0318-cpu` exists and "points at the same commit" | Recorded that this branch is **not on the remote**; it exists only as a local branch | GitHub API `branches` list (11 branches, feature branch absent) |
| 3 | `README.md` | Remote-branch list omitted the `docs/*` and `feature/sprint-3-season-age-reference-*` branches and did not say which are merged | Replaced with the actual remote branch list and recorded that `feature/sprint-3-season-age-reference-leo0318-cpu` (`8ac23ef`) is the only unmerged branch | GitHub API `branches`; `git merge-base --is-ancestor` per branch |
| 4 | `README.md` | Documented "feature branches are merged with `--no-ff`" without the known exception | Added the exception that `1ec3a25` was pushed directly, so it has no PR merge record | GitHub API `pulls` (6 PRs, none with `merge_commit_sha = 1ec3a25`) |
| 5 | `README.md` | PR #5 and PR #6 were not recorded | Added both, with branch, head SHA and merge commit | GitHub API `pulls` |
| 6 | `README.md` | 348 passed appeared without a date, command, SHA or a statement that it was re-run | Added the verified re-run statement pointing at this evidence folder | This report; `pytest-results.txt` |
| 7 | `CHANGELOG.md` | No record of the documentation correction or of the re-verification | Added a `1.4.1` entry (documentation-only) listing the corrections and the re-run result; left 1.3.0's 267 and 1.4.0's 348 untouched | This report |
| 8 | `docs/configuration-management.md` | Branch/merge history was incomplete and did not mention the `--no-ff` exception or the missing remote branch | Replaced with a branch table (head SHA + how each merged) and the exception note | GitHub API; local history |
| 9 | `docs/configuration-management.md` (and README, Sprint 4 doc) | No statement about CI beyond "not verified" | Recorded the verified fact that the repository has **no** GitHub Actions workflow and **zero** workflow runs, so no CI pass is claimed | GitHub API `actions/runs` → `total_count: 0` |
| 10 | `docs/testing/sprint-4-acceptance-results.md` | Historical record (267 passed, 21/21) was accurate but had no pointer to the later verification | Added an additive "Later re-verification" section; the 267/21-21 figures were **left unchanged** | This report |

Explicitly **not** done: no PR was created; no branch was created to match the
README's old claim; no historical test number or defect record was deleted; no
GitHub Actions or deployment success was claimed.

---

## 5. Files changed

### Modified (all documentation — no business logic)

| File | Purpose | Business logic? |
|------|---------|-----------------|
| `README.md` | Correct branch/SHA/PR status; add re-verification pointer | No |
| `CHANGELOG.md` | Add `1.4.1` documentation-consistency and re-verification entry | No |
| `docs/configuration-management.md` | Correct branch table, merge history and CI statement | No |
| `docs/testing/sprint-4-acceptance-results.md` | Additive pointer to this verification | No |

```text
 CHANGELOG.md                                | 36 ++++++++++++++
 README.md                                   | 77 ++++++++++++++++++++++-------
 docs/configuration-management.md            | 45 ++++++++++++-----
 docs/testing/sprint-4-acceptance-results.md |  9 ++++
 4 files changed, 137 insertions(+), 30 deletions(-)
```

### Added (evidence)

| Path | Purpose |
|------|---------|
| `docs/testing/final-verification-20261016/final-verification-report.md` | This report |
| `docs/testing/final-verification-20261016/pytest-results.txt` | Raw `pytest -q` output |
| `docs/testing/final-verification-20261016/browser-acceptance-results.md` | Per-scenario browser acceptance record |
| `docs/testing/final-verification-20261016/test-environment.md` | Machine, dependency, Git and DB-isolation record |
| `docs/testing/final-verification-20261016/database-state-final.txt` | Final isolated database dump and consistency checks |
| `docs/testing/screenshots/final-verification-20261016/*.png` | 22 real browser captures |

#### Archived outside the repository

Six internal test artifacts are deliberately **not** committed, so that the
public change set contains only the reports, the results and the screenshots.
They are preserved unmodified in the local test archive `<LOCAL_ARCHIVE>`, and
the archive records the SHA-256 of each original in
`SHA256SUMS-originals.txt` so the copies can be checked against this report.

| Archived file | Purpose |
|---------------|---------|
| `pytest-collected-tests.txt` | Full collected-test inventory (348 ids) |
| `browser-run1-console.txt`, `browser-run2-console.txt` | Raw acceptance console logs |
| `browser-run1-results.json`, `browser-run2-results.json` | Machine-readable per-scenario results |
| `inject_legacy.py` | The exact script used for the two injected legacy rows |

### Application code / tests

**None changed.** No defect requiring a code change was found, so no application
logic, schema, dependency or test file was touched. No new dependency was added.

---

## 6. What is verified, and what is not

### Verified correct

- All 348 automated tests pass, including every module named in the brief
  (age groups, auto assignment, guardian adult validation, DOB consistency,
  members, guardians, registration, teams, edge cases, validation, views).
- Age-group computation from date of birth and season, including the season-age
  5/6 boundary either side of the calendar year.
- A hand-submitted age group cannot override the computed value.
- A member below the minimum age cannot be registered.
- Complete registration triggers automatic assignment; matching season and age
  group are respected; fewest-players-first with lowest-team-id tie-breaking;
  no assignment when no team matches; a later matching team picks up waiting
  players; existing placements are never silently moved.
- Adult guardian verification, rejection of under-18 guardians, and the rule that
  a missing/unreadable guardian date of birth is never treated as adult.
- Juniors cannot complete a registration without a linked, verified adult guardian.
- A member date-of-birth change keeps affected registration age groups
  consistent; an incompatible change is refused with no partial write.
- An inconsistent existing placement is reported in the UI and neither moved nor
  duplicated; the final database contains no duplicate same-season assignment.
- Team create/rename/remove, player add/move/remove, roster, registration history
  and guardian link views all behave as documented.
- No unhandled traceback, `500`, or browser console error occurred in any scenario.

### Test-passing but not browser-verified

- None. Every browser scenario that was planned was executed.

### Not verified

- **CI.** No GitHub Actions workflow exists and no run has ever been recorded, so
  there is no CI result to verify. Nothing is claimed.
- **Human acceptance / course sign-off.** All acceptance here is browser
  automation. No teacher or team member has reviewed or signed off anything.
- The alternative rule in the unmerged branch
  `feature/sprint-3-season-age-reference-leo0318-cpu` was not evaluated as
  behaviour; only its merge status was checked.
- Rendering and behaviour outside headless Edge 155 at 1440×1000 (other
  browsers, real keyboard/AT users, mobile viewports) was not exercised.
- Whether the remote repository changed again after 2026-10-16 14:16 UTC. The
  remote state recorded here is a point-in-time API reading.
- Anything requiring the ISYS3001 A3 final evaluation report, personal
  reflections or team-member confirmation — deliberately out of scope.

### Remaining defects and limitations

1. **Environment hygiene (pre-existing, not an application defect).** The project
   `.venv` contains packages that `requirements.txt` does not declare (`lxml`,
   `openpyxl`, `pypdf`, `python-docx`, `et_xmlfile`, `exceptiongroup`, `tomli`,
   `typing_extensions`). Neither `app/` nor `tests/` imports any of them, so the
   results are unaffected. Removing them from a shared environment was left alone.
2. **Git history cannot be undone.** `1ec3a25` reached `main` as a direct commit
   instead of a `--no-ff` merge. This is now documented rather than "fixed": it is
   history, and rewriting it would require a force-push the task forbids.
3. **Legacy data is reported, not repaired.** A guardian with an unreadable date
   of birth, or a team assignment that no longer matches a member's computed age
   group, is surfaced in the UI but not automatically corrected or migrated.
   Whether the application should offer a repair/migration step is a product
   decision for the owner, not something this audit changed.
4. **Open business-rule question.** `main` measures the under-18 guardian rule as
   of *today*, while the unmerged branch `feature/sprint-3-season-age-reference-leo0318-cpu`
   measures it at the *season reference date*. Both are defensible for a football
   club; changing it would change user-visible behaviour, so it was left as-is and
   is raised for your decision.
5. **Validation refusals return HTTP 400.** This is the implemented design and is
   consistent across forms; noted so the behaviour is not mistaken for a fault.
6. **Scope.** This remains a local, single-user application with no
   authentication, concurrency handling or production deployment configuration.

---

## 7. Next steps suggested by the evidence

1. **Review the four documentation corrections on branch
   `audit/final-verification-20261016`** and decide whether to merge them. No push
   has been made and no PR exists.
2. **Decide the under-18 age-reference question** (item 6.4 above). If the season
   reference date is preferred, that is a deliberate behaviour change and should be
   a separate, explicitly approved piece of work with its own regression tests.
3. **Decide whether legacy-data repair is wanted** (item 6.3). If yes, it needs a
   designed migration path; the current behaviour already fails safe and reports.
4. **Optionally tidy the virtual environment** (item 6.1) so `pip freeze` matches
   `requirements.txt`, or extend `requirements.txt` if those tools are genuinely
   used for coursework outside the app.
5. **If CI is expected for the assessment**, add a GitHub Actions workflow — at
   present the repository has none, and no amount of local testing substitutes for
   a CI run.
6. **Human acceptance is still outstanding.** The browser evidence here supports
   review but does not replace a human walkthrough or a teacher's sign-off.
