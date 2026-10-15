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
