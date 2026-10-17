# Changelog

All notable changes to this project are documented here. Only real, completed
work is listed.

## 0.1.0

- Initial project structure (Flask app factory, config files, entry point).

## 0.2.0

- Member management implemented (create, search, update, set inactive).

## 0.3.0

- Guardian management implemented (create, search, update, link, unlink, view linked juniors).

## 0.4.0

- Registration management implemented (create, view, amend, withdraw, history).

## 0.5.0

- Junior guardian validation implemented (under-18 rule on registration completion).

## 0.6.0

- Team management implemented (create, list, rename, remove).

## 0.7.0

- Player management implemented (add, move, remove with season eligibility).

## 0.8.0

- Roster and history views implemented (roster, registration history, guardian linked juniors, dashboard).

## 0.9.0

- Validation and error handling improved (friendly flash messages, invalid input handling).

## 1.0.0

- Testing and local QA completed (pytest suite, clean-environment verification).

## 1.1.0

- Strengthened automated test coverage with edge cases (age boundary, withdrawn
  registrations, team eligibility, member reactivation, guardian unlink, age
  calculation).
- Improved application configuration (environment-driven host/port/debug,
  clearer `.env.example`, dependency grouping in `requirements.txt`).
- Expanded and corrected project documentation.
- Established a Git feature-branch workflow on GitHub (main plus three feature branches).

## 1.2.0

- Fixed defect S3-D1: a member whose stored `date_of_birth` is not a valid ISO
  date previously raised an unhandled `ValueError`, producing HTTP 500 on the
  member detail page and blocking the under-18 guardian rule. Such a date is now
  refused with a friendly message and is never treated as proof that the member
  is an adult:
  - `app/models.py` - added `safe_parse_date()`, which returns `None` instead of
    raising for an unreadable stored value.
  - `app/services.py` - added `UNREADABLE_DATE_OF_BIRTH_MESSAGE`;
    `can_complete_registration` refuses completion when the stored date cannot be
    read; `_member_is_junior` and `guardian_linked_members` no longer raise.
  - `app/routes.py` - the member detail page reports no age instead of failing.
  - `app/templates/member_detail.html` and `guardian_detail.html` - show that the
    age cannot be read rather than inventing one.
  - No schema change and no migration. Behaviour for valid dates is unchanged.
- Verified the registration and eligibility Stories (create, amend, withdraw,
  member registration history, under-18 guardian rule) and added
  `tests/test_registration_sprint3.py`: 117 cases (103 for the five Stories plus
  14 regression tests for S3-D1), bringing the suite from 133 to 250 passed.
- The coverage includes registration persistence, missing and invalid fields,
  rejected amendments leaving stored rows unchanged, withdrawal that preserves
  the record, registration-history ordering and isolation between members,
  corrupt stored dates of birth, and the eighteenth-birthday boundary (today
  versus tomorrow).
- Executed all 14 browser end-to-end scenarios against the running application
  with a disposable database, capturing 20 screenshots. Twelve scenarios passed
  in full and two are recorded as partial (stale-tab withdrawal submission, and
  server-side invalid-date rules that the browser automation could not reach).
  Details and hashes are in `docs/testing/sprint-3-e2e-checklist.md` and
  `docs/testing/sprint-3-screenshots.txt`.
- Added Sprint 3 testing documentation: test plan, test results, E2E checklist,
  defect log, handover notes, screenshots index and changed-files manifest under
  `docs/testing/`.
- Recorded for a product decision, with no behaviour changed: removing the last
  guardian does not revisit a completed registration; an Inactive member can
  still be registered; the amend form can retarget a registration to another
  member; and Season and Age Group are free text with no format validation.
- Note for reviewers: the browser scenarios were executed by browser automation,
  not by a human. Human acceptance sign-off is still required for all five
  Stories, and none should be marked Done in Jira on the strength of these
  documents.

## 1.3.0

- Sprint 4 (Team and Roster Management) completed:
  - Corrected player eligibility to require a same-season `Complete`
    registration; `Started` and `Withdrawn` registrations no longer qualify
    (previously any non-withdrawn registration did).
  - Fixed defect S2-F1: `remove_player_from_team` now validates the team and
    member, returns `True`/`False` based on whether a membership row was actually
    removed, and the route shows an accurate error instead of a false success for
    a no-op.
  - Team creation/listing, rename and safe removal, same-season player add, move,
    remove, and roster contact display verified end to end.
- Automated test suite: **267 passed** (0 failed, 0 errors, 0 skipped).
- Browser acceptance: **21/21 scenarios passed**, executed by the DSH environment
  using Microsoft Edge + Chrome DevTools Protocol (automation, not human
  sign-off). See `docs/testing/sprint-4-acceptance-results.md`.

## 1.4.0

- Automatic age groups:
  - The age group is computed from the member's date of birth and the season
    (`season_age = season_year - birth_year`) against a fixed list (`U6`, `U8`,
    `U10`, `U12`, `U14`, `U16`, `U18`, `Seniors`) and stored on the registration;
    the age group submitted by the form is ignored. A member below 4 in a season
    cannot be registered. This is the course project's own rule, not an official
    Football Australia regulation.
  - Amending a registration to another season recomputes the age group.
- Automatic team assignment:
  - A `Complete` registration places the eligible player onto a matching team
    (same season and age group), choosing the fewest players and breaking ties by
    the lowest team id; creating a matching team later assigns waiting players.
    An existing placement is never silently moved.
  - Manual add and move also enforce the season and age-group match and at most
    one team per season. Withdrawing the last `Complete` registration for a
    season removes that season's assignment; the registration row is kept.
- Guardian date of birth:
  - `guardians` gains a `date_of_birth`, added by an idempotent migration that
    preserves existing guardians and links. A guardian must be verified as an
    adult (18 or over) before they can be linked or satisfy the under-18 rule; a
    legacy guardian without a date of birth is not verified.
- Date-of-birth consistency fix:
  - Changing a member's date of birth can change the age group of their existing
    registrations. `services.update_member` now re-checks every affected
    registration before writing anything and applies the member row together
    with every recomputed registration age group in a single transaction, so a
    rejected or failing change leaves no partial state.
  - Automatic assignment never relies on a stale stored age group: it always uses
    the age group recomputed from the member's date of birth and the season. An
    existing placement that no longer matches is reported through
    `services.assignment_conflict` rather than being silently moved or
    duplicated.
- New regression tests:
  - `tests/test_member_dob_consistency.py` (7 tests) covers the age-group rewrite
    after a date-of-birth change, rejection of a change that would break a team
    assignment, rejection below the minimum age, the junior verified-adult
    requirement after a change, and rollback of a mid-write failure.
  - `tests/test_auto_assignment.py` adds stored-vs-computed age-group coverage,
    including the stale-group, mismatch-reporting and fewest-players/tie-break
    paths.
- Automated test suite: **348 passed** (0 failed, 0 errors, 0 skipped).

## 1.4.1

Documentation-only change. No application code, database schema, dependency or
test was modified.

- Corrected the repository-status statements in `README.md`:
  - `1ec3a25` (automatic age groups, automatic team assignment, guardian adult
    verification) was previously described as "the current tip of `main`". The
    real tip of `main` is the merge commit
    `fd7b68c15d92e0511b8609f3c9ce84c9943724ee` of PR #6, "Align documentation
    with merged feature status". `1ec3a25` remains the feature commit.
  - Removed the claim that the branch
    `feature/auto-age-team-assignment-guardian-adult-leo0318-cpu` is present on
    the remote. It is **not** on the remote; it exists only as a local branch and
    points at `1ec3a25`.
  - Updated the remote branch list to the branches actually reported by the
    GitHub API on 2026-10-16, and recorded that
    `feature/sprint-3-season-age-reference-leo0318-cpu` (`8ac23ef`) is the only
    remote branch not merged into `main`.
  - Recorded PR #5 (`3dbaf1e`) and PR #6 (`fd7b68c`) explicitly, and clarified
    that `1ec3a25` reached `main` as an ordinary commit rather than a `--no-ff`
    merge, so it has no pull-request merge record.
- Corrected `docs/configuration-management.md` so its branch and merge history
  matches the remote and the README.
- Recorded that this repository has **no** GitHub Actions workflow and no
  workflow run, so no CI result is claimed.
- Re-verified the automated suite on the audited code
  (`fd7b68c`, tree `a42f0465`) on 2026-10-16 with
  `.\.venv\Scripts\python.exe -m pytest -q`: **348 passed**, 0 failed, 0 errors,
  0 skipped. The **267 passed** Sprint 4 figure and the **335 passed** unmerged
  figure above are historical records and are unchanged.
- Ran a fresh browser end-to-end acceptance pass against the audited code with an
  isolated temporary SQLite database; results, screenshots and environment
  details are in `docs/testing/final-verification-20261016/`. The
  **21/21** Sprint 4 browser figure remains a separate historical record.
