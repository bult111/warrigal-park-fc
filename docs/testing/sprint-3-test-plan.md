# Sprint 3 — Test Plan

- **Sprint:** Sprint 3 — Epic: Registration and Eligibility
- **Stories in scope:** `MSD426GXUST25-10` ... `MSD426GXUST25-14`
  (5 Stories, 15 Story Points)
- **Document status:** written from the actual local repository, then updated at
  the end of the session to reflect what was actually executed. It records only
  behaviour that was read in the source, reproduced by running the application,
  or observed in the browser round.
- **Environment:** Windows, Python 3.13.1, pytest 8.3.3, Flask 3.0.3,
  SQLite 3.45.3, Microsoft Edge (Chromium) for the browser round.

## Sprint goal

Verify and complete the registration and eligibility workflows so that a
registration can be created, amended and withdrawn safely, that a member's
registration history is correct and isolated per member, and that the under-18
guardian rule is enforced — including the eighteenth-birthday boundary — without
inventing any business rule the project does not already state.

## Stories in scope

| Story | Title | Story Points |
|---|---|---:|
| `MSD426GXUST25-10` | Create Registration | 3 |
| `MSD426GXUST25-11` | Amend Registration | 2 |
| `MSD426GXUST25-12` | Withdraw Registration | 2 |
| `MSD426GXUST25-13` | View Member Registration History | 3 |
| `MSD426GXUST25-14` | Enforce Under-18 Guardian Rule | 5 |
| **Total** | | **15** |

No Story was created, renamed, re-pointed or re-estimated, and no Story was
marked Done.

## Testing objectives

1. Establish a truthful baseline by running the existing suite **before** any
   change.
2. Verify each of the five Stories against real application behaviour.
3. Close genuine automated-coverage gaps, including positive, negative, boundary,
   persistence and regression cases.
4. Investigate whether the data model supports what the Stories ask for, and
   record anything it cannot support rather than inventing it.
5. Record every defect with a reproduction; fix only what is in scope and
   unambiguous.
6. Keep every existing test intact — none removed, renamed or weakened.
7. Execute the browser scenarios for real and keep automated and browser
   verification strictly separate.

## Approach (final, as executed)

The plan has three layers, and the results documents keep them apart:

| Layer | Tool | What it proves | Where reported |
|---|---|---|---|
| Service and route tests | `pytest` + Flask test client | Validation, business rules, persistence, HTTP status codes, rendered text | `sprint-3-test-results.md` |
| Browser end-to-end | Real browser against the running app | Real form interaction, navigation, native HTML5 controls, flash messages as rendered | `sprint-3-e2e-checklist.md` |
| Direct data probes | SQLite queries and short scripts | Stored rows, row counts before/after, corrupt-data conditions | both |

The regression suite was extended with 14 new cases for the S3-D1 fix, taking the
Sprint 3 module to **117 cases** and the full suite to **250**.

## Confirmed baseline (measured, not assumed)

| Item | Value |
|------|-------|
| Command | `.venv\Scripts\python.exe -m pytest -q` |
| Collected | 133 |
| Passed | 133 |
| Failed / Skipped / Errors | 0 / 0 / 0 |
| Time | 5.29s |

Measured on the working copy before any change in this session. Details are in
`sprint-3-test-results.md`.

## How the tests are written

- **Framework:** `pytest`, using the fixtures already defined in
  `tests/conftest.py`. No fixture, helper or existing test was modified.
- **Isolation:** every test runs against a fresh temporary SQLite database from
  the `app` fixture. The real application database is never opened by the suite.
- **Service-layer tests** call `app/services.py` directly, so rules are tested
  independently of HTTP.
- **Route tests** use the Flask test client and assert status codes, flash text,
  retained form values, and the stored row after the request.
- **Persistence asserts** read the raw row through the database layer rather than
  trusting the value returned by the service.
- **Boundary tests** use the `exactly_18_dob` and `just_under_18_dob` fixtures,
  computed from `date.today()`, so the boundary is tested against the
  application's real clock rather than a hard-coded date.
- **Negative tests** assert both that the operation is refused *and* that the
  stored data is unchanged and no extra row was created.
- **Negative controls (mutations)** are used to prove the tests are meaningful;
  the four controls and their outcomes are recorded in
  `sprint-3-test-results.md`.

## Story-to-implementation map

| Story | Implementation | Recovered coverage | Added in this session |
|---|---|---:|---|
| -10 Create Registration | `services.create_registration`, `_validate_registration_fields`, `routes.registration_new`, `registration_form.html` | 27 | — |
| -11 Amend Registration | `services.update_registration`, `routes.registration_edit` | 19 | — |
| -12 Withdraw Registration | `services.withdraw_registration`, `routes.registration_withdraw`, `registration_detail.html` | 12 | — |
| -13 View Member Registration History | `services.member_registration_history`, `routes.member_detail`, `member_detail.html` | 14 | — |
| -14 Enforce Under-18 Guardian Rule | `models.calculate_age`, `models.validate_date_of_birth`, `models.safe_parse_date` *(new)*, `services._member_is_junior`, `services.can_complete_registration`, `services.member_has_guardian`, `guardian_members` | 31 | 14 (S3-D1 regression) |
| **Total** | | **103** | **14** |

## Coverage gaps identified before writing tests

| # | Gap | Story |
|---|---|---|
| 1 | No test asserted that a created registration is written to the database row. | -10 |
| 2 | No test covered missing/blank season or age group, or an unknown member, on create. | -10 |
| 3 | No route-level test covered a rejected create (status, feedback, no stored row). | -10 |
| 4 | No test asserted that amending one field leaves the others and other registrations alone. | -11 |
| 5 | No test asserted that a rejected amendment leaves the stored row unchanged. | -11 |
| 6 | No test covered amending to an invalid status, or an unknown registration. | -11 |
| 7 | No test asserted withdrawal preserves the row rather than deleting it. | -12 |
| 8 | No test covered route-level withdrawal, the repeat case, or an unknown id. | -12 |
| 9 | No test asserted history ordering, rendered row fields, or detail links. | -13 |
| 10 | No test asserted **history isolation between different members**. | -13 |
| 11 | No test asserted the eighteenth-birthday boundary through the workflow. | -14 |
| 12 | No test asserted that a guardian linked to *another* member does not satisfy the rule. | -14 |
| 13 | No test covered invalid date-of-birth values feeding the age calculation. | -14 |
| 14 | No test asserted the refusal message wording. | -14 |
| 15 | *(added this session)* No test covered a corrupt **stored** date of birth, which caused an unhandled `ValueError` (S3-D1). | -14 |

## Test cases (final)

All Sprint 3 tests live in `tests/test_registration_sprint3.py` — **117 collected
cases** in **90 test functions**. Per-Story figures are coverage mappings; several
tests evidence a second Story, and the recovered figures were measured by mapping
the 103 recovered node ids to their Story section.

| Story | Cases in the module |
|---|---:|
| MSD426GXUST25-10 Create Registration | 27 |
| MSD426GXUST25-11 Amend Registration | 19 |
| MSD426GXUST25-12 Withdraw Registration | 12 |
| MSD426GXUST25-13 View Member Registration History | 14 |
| MSD426GXUST25-14 Enforce Under-18 Guardian Rule | 31 recovered + 14 S3-D1 = 45 |
| **Total** | **117** |

### MSD426GXUST25-14 — the S3-D1 regression cases (added this session)

| Test | Asserts |
|---|---|
| `test_unreadable_stored_dob_is_refused_not_treated_as_adult` | Refuses with the exact message; never allows |
| `test_unreadable_stored_dob_blocks_registration_creation` | Create-as-`Complete` refused, no row stored |
| `test_unreadable_stored_dob_blocks_registration_amendment` | Amend-to-`Complete` refused, status unchanged |
| `test_unreadable_stored_dob_still_allows_non_complete_statuses` | `Started` paths still work |
| `test_unreadable_stored_dob_member_page_returns_200` | Member page renders, no invented age |
| `test_unreadable_stored_dob_route_completion_shows_friendly_message` | HTTP 400 with the friendly message, not 500 |
| `test_unreadable_stored_dob_guardian_page_returns_200` | Guardian page still renders |
| `test_unreadable_stored_dob_leaves_other_data_intact` | Unrelated member/registration data untouched |
| `test_unreadable_stored_dob_variants_are_all_handled` (5 cases) | Five unreadable stored forms |
| `test_readable_stored_dob_behaviour_is_unchanged` | Valid dates keep the original rule behaviour |

The full per-Story test tables for Stories -10 to -14 are unchanged from the
earlier version of this plan; the 14 S3-D1 cases above are the only additions to
test scope. They were added because the defect fix changed application behaviour
and therefore needed its own regression guard.

## Browser end-to-end scope

14 scenarios were executed against the live application; see
`docs/testing/sprint-3-e2e-checklist.md`. Twelve passed fully and two are
recorded as partial, with the unverified half named explicitly:

- **S3-E2E-13 (partial):** the stale-tab withdrawal submission could not be
  reproduced through the UI, because the withdraw button is only rendered while
  the status is not `Withdrawn`.
- **S3-E2E-14 (partial):** the native `type=date` control cannot be driven by the
  automation tool, so the server-side invalid-date rules rest on the automated
  tests. The client-side behaviour (required field, impossible date rejected by
  the control) was observed directly.

## Source of truth used for acceptance expectations

No Jira access was available or used, and no acceptance criteria were supplied
with the task, so expected behaviour was derived from the repository:

1. `README.md` — "Important business rules" 2 and 4 (under-18 guardian rule;
   registration history retained).
2. `docs/project-scope.md` — registration management and junior guardian
   validation are in scope.
3. `docs/architecture.md` — the service layer owns business rules, raises
   `ServiceError`, and `registrations` is "many per member (one per season)".
4. `app/models.py` — status constants and `JUNIOR_AGE_LIMIT = 18`.
5. The templates, for what the user actually sees.

**Ambiguity to escalate:** `docs/architecture.md` describes registrations as "one
per season", but neither the service layer nor the schema enforces it (S3-C1 /
Sprint 1 D1). Any authoritative criterion making that a hard rule needs its own
story and approval.

## Verification of the tests themselves (negative controls)

| Control | Temporary mutation | Result |
|---|---|---|
| 1 | `models.safe_parse_date` made to re-raise | **12 failed**, 1 passed (`-k unreadable`) |
| 2 | Guardian check disabled in `can_complete_registration` | **14 failed**, 103 passed |
| 3 | `_member_is_junior`: `age < 18` changed to `age <= 18` | **1 failed** (boundary test), 116 passed |
| 4 | `member_registration_history` member filter removed | **24 failed** |

All mutations were reverted immediately, `git diff` was inspected, and the suite
returned to 250 passed.

## Out of scope for this sprint

- No change to team, player, dashboard or member/guardian management behaviour.
- No database schema change and no migration.
- No Git operation that changes repository state: nothing was staged, committed,
  pushed, merged, fetched, pulled or reset. One branch switch was performed, at
  the user's explicit instruction, to the existing Sprint 3 feature branch.
- No Jira access or change.
- No roster-related assertion for withdrawal (S3-C2 is a separate epic).
