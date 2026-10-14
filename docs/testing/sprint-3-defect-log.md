# Sprint 3 — Defect Log

- **Sprint:** Sprint 3 — Epic: Registration and Eligibility
- **Document status:** every finding below was reproduced against the code and
  the running application during this session. Findings are labelled as defect,
  expected behaviour, product decision required, deferred improvement, or not
  reproducible.
- **Session note:** this document was lost once when an external clean of the
  working tree removed the Sprint 3 files (see `sprint-3-handover.md`). It has
  been rebuilt and now also records the S3-D1 fix and the browser round.

## Summary

| ID | Area | Story | Severity | Status |
|----|------|-------|----------|--------|
| **S3-D1** | Unhandled error on a corrupt stored date of birth | -14 | Low (defensive) | **FIXED** in this session, with 14 regression tests |
| S3-O1 | Removing the last guardian does not revisit a completed registration | -14 | Observation | Product decision required (unchanged) |
| S3-O2 | Registration for an Inactive member is allowed | -10 | Observation | Product decision required (unchanged) |
| S3-O3 | The amend form can retarget a registration to another member | -11 | Observation | Product decision required (unchanged) |
| S3-O4 | Season and Age Group are free text with no format validation | -10, -11 | Observation | Product decision required (unchanged) |
| S3-O5 | Under-18 rule is not re-checked by the database itself | -14 | Observation | Expected behaviour — recorded, no change |
| S3-C1 | Duplicate same-season registrations (S2-C1 / Sprint 1 D1) | -10 | Low | Open — carried forward, unchanged |
| S3-C2 | Withdrawn registration still on a team roster (S2-C2 / Sprint 1 D2) | -12 | Low | Open — carried forward, unchanged |
| S3-L1 | Registration history cannot show dates — the schema stores none | -13 | Limitation | Not fixable without a schema change |
| S3-L2 | Member form has no `max` on Date of Birth, so a future date must be rejected server-side | -10, -14 | Limitation | Not a defect — layered validation, unchanged |
| S3-N1 | Withdrawal from a stale page is a no-op, not an error | -12 | Info | Not a defect — documented |
| S3-N2 | No registration record can be hard-deleted | -12 | Info | Not a defect — by design |

---

## S3-D1 — A corrupt stored date of birth raised an unhandled error

- **Affected Story:** `MSD426GXUST25-14` (Enforce Under-18 Guardian Rule).
- **Severity:** Low, defensive. Normal use cannot trigger it, because every path
  that writes `members.date_of_birth` validates it first. It requires data
  written outside the service layer (legacy database, manual `UPDATE`, future
  import).
- **Status:** **FIXED and verified** in this session.

### Reproduction (before the fix)

1. Create a member normally.
2. Write a non-ISO string straight into the stored row:

   ```sql
   UPDATE members SET date_of_birth = 'not-a-date' WHERE id = <id>;
   ```

3. Then open the member page, or attempt to complete a registration.

### Actual result before the fix (reproduced earlier in this session)

```text
stored dob: not-a-date

1) services.can_complete_registration(...)
   -> UNHANDLED ValueError: Invalid isoformat string: 'not-a-date'
2) services.create_registration(..., 'Complete')
   -> UNHANDLED ValueError: Invalid isoformat string: 'not-a-date'
3) GET /members/<id>
   -> UNHANDLED ValueError: Invalid isoformat string: 'not-a-date'
4) GET /registrations/<id>   (registration detail)
   -> HTTP 200   (unaffected)
```

In a running application paths 1 and 3 present as HTTP 500, contradicting
`README.md` ("User-friendly validation with flash messages (no raw tracebacks
for normal mistakes)").

### Root cause

`app/services.py::_member_is_junior` and `app/routes.py::member_detail` called
`date.fromisoformat(...)` on a value read from the database. That raises
`ValueError` for a non-ISO string and neither call site handled it.
`models.validate_date_of_birth` only guards values on the way *in*.

### Fix applied

The fix never treats an unreadable date as proof of adulthood, and never
silently assumes the member is a junior either. It refuses and explains.

| File | Change |
|---|---|
| `app/models.py` | Added `safe_parse_date(value)` returning `None` for an unreadable/empty value instead of raising. |
| `app/services.py` | Added `UNREADABLE_DATE_OF_BIRTH_MESSAGE`. `can_complete_registration` now returns `(False, <message>)` when the stored date cannot be read. `_member_is_junior` uses `safe_parse_date` and returns `False` for an unreadable date so it can never raise. `guardian_linked_members` reports `age = None` instead of raising. The now-unused `from datetime import date` import was removed. |
| `app/routes.py` | `member_detail` uses `safe_parse_date` and sets `member["age"] = None` when unreadable. |
| `app/templates/member_detail.html` | Shows `(age cannot be read from the stored date)` instead of an invented age. |
| `app/templates/guardian_detail.html` | Shows an em dash for an unreadable linked-member age. |

No schema change. No migration. No change to the rule for readable dates.

### Why refusal rather than "treat as adult"

The task instruction was explicit: do not silently assume malformed birth dates
make a member an adult. Refusing completion is the only option that cannot
weaken the under-18 guardian rule. The message names the problem and tells the
administrator what to correct, consistent with the application's existing
`ServiceError` + flash design.

### Regression tests added

14 test cases in `tests/test_registration_sprint3.py` (final section, "S3-D1
regression"):

| Test | Asserts |
|---|---|
| `test_unreadable_stored_dob_is_refused_not_treated_as_adult` | The rule refuses with the exact message; never allows |
| `test_unreadable_stored_dob_blocks_registration_creation` | Create-as-Complete refused and stores no row |
| `test_unreadable_stored_dob_blocks_registration_amendment` | Amend-to-Complete refused; stored status unchanged |
| `test_unreadable_stored_dob_still_allows_non_complete_statuses` | Started/amendment still work — the rule guards completion only |
| `test_unreadable_stored_dob_member_page_returns_200` | Member page renders 200 and says the age cannot be read |
| `test_unreadable_stored_dob_route_completion_shows_friendly_message` | Route returns 400 with the friendly message, not 500 |
| `test_unreadable_stored_dob_guardian_page_returns_200` | Guardian page with such a linked member still renders |
| `test_unreadable_stored_dob_leaves_other_data_intact` | Member fields, both registrations and history are unaffected |
| `test_unreadable_stored_dob_variants_are_all_handled` (5 cases) | empty, whitespace, `not-a-date`, `2026-02-30`, `01/02/2026` |
| `test_readable_stored_dob_behaviour_is_unchanged` | Junior still blocked; adult still allowed |

### Retest results

| Check | Command / method | Result |
|---|---|---|
| Regression section only | `python -m pytest tests/test_registration_sprint3.py -k "unreadable or readable_stored"` | **14 passed** |
| Sprint 3 module | `python -m pytest tests/test_registration_sprint3.py -q` | **117 passed** |
| Complete suite | `python -m pytest -q` | **250 passed**, 0 failed, 0 skipped, 0 errors |
| Negative control: `safe_parse_date` mutated to re-raise | module, `-k unreadable` | **12 failed**, 1 passed — the tests really cover the fix |
| Negative control: guardian check disabled | full module | **14 failed**, 103 passed |
| Negative control: `age < 18` changed to `age <= 18` | full module | **1 failed** (the boundary test), 116 passed |
| Browser: member page with corrupt stored date | `GET /members/4` on the live app | **HTTP 200**, page shows `not-a-date (age cannot be read from the stored date)` — `S3-D1-member-page-corrupt-dob-200-ok.png` |
| Browser: completion attempt with corrupt stored date | `POST /registrations/new` on the live app | **HTTP 400**, red flash `This member's date of birth on record cannot be read, so the registration cannot be completed. Please correct the member's date of birth first.` — `S3-D1-completion-refused-friendly-message.png` |

All three negative-control mutations were reverted immediately and the suite was
re-run green afterwards. `git diff -- app/` was inspected to confirm only the
intended fix remains.

### Remaining exposure

A row with an unreadable date of birth still **displays the raw stored value**
(the member page shows `not-a-date`). That is deliberate: the application shows
what is actually stored rather than hiding it, and the fix's job is to prevent a
crash and prevent the rule being satisfied. If the team prefers to hide or
normalise the raw value, that is a presentation decision, not a defect.

---

## S3-O1 — Removing the last guardian does not revisit a completed registration

- **Story:** `MSD426GXUST25-14`. **Status:** Product decision required — unchanged.
- **Carried forward from:** Sprint 2 item S2-O2.
- **Confirmed again in this session:** the rule is enforced at the moment of
  completion only. After unlinking, the registration stays `Complete` while a
  *new* completion attempt would be blocked again.
- **Asserted by:** `test_unlinking_the_last_guardian_does_not_revert_a_complete_registration`.
- **Decision required:** block the unlink, downgrade the registration, or leave it
  as historical fact. Not changed — no written requirement states which.

## S3-O2 — A registration can be created for an Inactive member

- **Story:** `MSD426GXUST25-10`. **Status:** Product decision required — unchanged.
- **Confirmed:** `create_registration` checks only that the member exists;
  `README.md` defines deactivation as a soft status change and states no rule
  that would block registration.
- **Asserted by:** `test_create_registration_for_inactive_member_is_allowed`.
- **Decision required:** should an Inactive member be blocked from new
  registrations? Compare S2-O1 (rosters and team placement).

## S3-O3 — The amend form can retarget a registration to another member

- **Story:** `MSD426GXUST25-11`. **Status:** Product decision required — unchanged.
- **Confirmed:** `Member` is an editable select on the amend form and
  `update_registration` writes `member_id`, so a registration can be moved
  between members (and between their histories).
- **Asserted by:** `test_amend_registration_can_be_repointed_to_another_member`
  and `test_under_18_rule_checked_against_the_new_member_when_retargeted` (the
  latter proves the guardian rule is evaluated against the member the
  registration will point at — the safer of the two possible behaviours).
- **Decision required:** should `member_id` be locked when amending? Not changed —
  restricting it would be a new business rule.
- **Browser step that exercises it:** S3-E2E-11 in the checklist.

## S3-O4 — Season and Age Group are free text

- **Stories:** `MSD426GXUST25-10`, `-11`. **Status:** Product decision required — unchanged.
- **Confirmed by direct probe in this session:**

  ```text
  unvalidated season stored: 'banana'
  trailing-space season stored as: '2026'      (trimmed correctly)
  unvalidated age_group stored: 'anything'
  ```

  Whitespace *is* trimmed, so `2026 ` and `2026` cannot coexist.
- **Consequence:** a typo such as `2062` is accepted silently and then behaves as
  a different season for team eligibility, which matches on the exact string.
- **Decision required:** validate the season as a four-digit year and restrict
  age groups to a club list? `docs/project-scope.md` currently declares advanced
  age-group eligibility checking out of scope.

## S3-O5 — The under-18 rule is enforced in application code, not by the database

- **Story:** `MSD426GXUST25-14`. **Status:** Expected behaviour — no change.
- **Description:** `registrations.status` has no database-level constraint
  tying `Complete` to the presence of a `guardian_members` row. Enforcement lives
  entirely in `services.can_complete_registration`, which is called by
  `create_registration` and `update_registration`.
- **Why this is recorded rather than changed:** the application has a single
  write path for registrations, both callers check the rule, and a database
  trigger would be a schema change. Adding one is not required by any acceptance
  criterion in the repository.
- **Risk if ignored:** a future code path that writes `registrations` directly
  (for example a bulk import) could bypass the rule. Any such feature must call
  the service layer.

## S3-C1 — Duplicate same-season registrations (carried forward)

- **Status:** Open — product decision required. From Sprint 2 S2-C1 / Sprint 1 D1.
- **Confirmed unchanged:** `create_registration` does not check for an existing
  same-member, same-season row and the schema has no uniqueness constraint, while
  `docs/architecture.md` describes registrations as "one per season".
- **Recommendation (unchanged):** either add a unique constraint on
  `(member_id, season)` plus a friendly pre-insert check, or correct the
  architecture wording. Not changed — a constraint would also require handling
  existing duplicates.
- **Not tested either way in Sprint 3**, so no expectation is locked in.

## S3-C2 — A withdrawn registration can still be on a team roster (carried forward)

- **Status:** Open — product decision required. From Sprint 2 S2-C2 / Sprint 1 D2.
- **Confirmed unchanged:** `withdraw_registration` updates only the status; any
  existing `team_players` row remains. Note `add_player_to_team` refuses a
  **withdrawn** registration, so withdrawal blocks *new* placements only.
- **Deliberately out of scope:** this belongs to the Team and Roster Management
  epic. No Sprint 3 test asserts roster behaviour.

## S3-L1 — Registration history cannot show dates

- **Story:** `MSD426GXUST25-13`. **Status:** Limitation of the data model.
- **Description:** `registrations` stores only `id`, `member_id`, `season`,
  `age_group`, `status`. There is no created/updated/withdrawn timestamp, so the
  history view cannot show *when* anything happened. The history view is correct
  for what the model holds.
- **Consequence:** if the authoritative Story -13 criteria ask for registration
  dates, they cannot be satisfied without a schema change and a migration path
  for existing `instance/*.db` files (the project has no migration framework).
- **Not implemented** — no repository requirement asks for a date.

## S3-L2 — No `max` on Date of Birth in the member form

- **Stories:** `-10`, `-14`. **Status:** Not a defect — recorded for testers.
- **Description:** `member_form.html` renders `<input type="date" required>` with
  no `max` attribute, and HTML5 date inputs have no future-date restriction by
  default.
- **Observed in the browser round:** the native date control cannot be used to
  enter an impossible date such as `2026-02-30` at all (the three segments
  simply will not accept it), and an empty date is blocked by `required`. A
  future date is **not** blocked by the control; it must be caught by the server.
- **Verified by automated tests, not the browser:** the server rejects future
  dates (`Date of birth cannot be in the future.`), impossible dates and
  malformed strings. The browser could not be used to reach those paths because
  the automation tool cannot type into a native `type=date` control, and no
  request-interception facility was available for document POST bodies. This is
  the same layered-validation situation recorded as S2-N1.
- **Optional improvement (not applied):** add `max` set to today. This would be
  a presentation change, not a rule change.

## S3-N1 — Withdrawal from a stale page is a no-op, not an error

- **Story:** `MSD426GXUST25-12`. **Status:** Not a defect — documented.
- **Description:** `registration_withdraw` always flashes
  `Registration withdrawn.` after `withdraw_registration`, which re-checks that
  the registration exists. A second withdrawal of an existing record re-flashes
  success while changing nothing; an unknown id produces the accurate
  `Registration not found.`
- **Why acceptable:** the end state the user asked for is true in both cases, the
  stored row is correct, no row count changes, and the UI hides the button once
  the status is `Withdrawn`, so a second withdrawal is only reachable from a
  stale page.
- **Asserted by:** `test_withdraw_registration_is_idempotent`,
  `test_withdraw_unknown_registration_rejected`.
- **Browser note:** the stale-tab reproduction was attempted in this round and is
  recorded in the E2E checklist as not reproducible through the UI, for the same
  reason as Sprint 2's S2-E2E-10.

## S3-N2 — There is no way to hard-delete a registration, by design

- **Story:** `MSD426GXUST25-12`. **Status:** Not a defect.
- **Description:** no service function or route deletes a `registrations` row.
  Withdrawal sets the status; the row is retained. `registrations.member_id` has
  `ON DELETE CASCADE`, but the application never deletes a member either.
- **Consequence:** Story -12's "preserve historical records" requirement is
  structurally guaranteed. Asserted by
  `test_withdraw_registration_keeps_the_row_and_its_details` (row count compared
  before and after) and confirmed in the browser round: 7 registrations before
  and after two withdrawals.

## Items investigated and confirmed correct (no change made)

| Area | Investigation | Outcome |
|---|---|---|
| Validation before write | Does a rejected create/amend leave a partial row? | **Correct.** Validation and the rule check both run before the write. Asserted for every rejection path, and confirmed in the browser (registration count unchanged after two rejected submissions). |
| Whitespace-only input | Is a whitespace-only value accepted for Season or Age Group? | **Correct.** `require_text` trims then rejects empty. Confirmed in the browser: whitespace Season returned HTTP 400 `Season is required.` |
| Trailing whitespace in a season | Can `2026 ` and `2026` coexist and break season matching? | **Correct.** Trimmed on the way in. Verified by direct probe. |
| Guardian rule on the retargeted member | Could retargeting smuggle a junior past the rule? | **Correct.** Evaluated against the member the registration will point at. Asserted. |
| Guardian linked to a different member | Does any guardian link satisfy the rule? | **Correct.** `member_has_guardian` filters on the specific member. Asserted. |
| Two linked guardians | Does a second link break the `LIMIT 1` lookup? | **Correct.** One is sufficient, a second is harmless. Asserted. |
| Eighteenth-birthday boundary | Strictly-less-than versus less-or-equal against real dates | **Correct.** Adult from the birthday. Asserted at day-before/of/after and 29 February; confirmed in the browser for both 18-today (allowed) and 18-tomorrow (blocked). |
| Rule guards completion only | Are Started and Withdrawn affected? | **Correct.** Unaffected. Asserted and exercised in the browser. |
| Error-path form behaviour | Are typed values lost after a rejection? | **Correct.** Retained. Confirmed in the browser for both create and amend. |
| Amend form pre-population | Does it load stored values? | **Correct.** Confirmed in the browser. |
| Withdrawal retention | Is the row deleted? | **Correct.** Not deleted; still in history and on the list. Confirmed in the browser. |
| History isolation | Does one member's page show another's rows? | **Correct.** Not present. Confirmed in the browser for two members. |
| Empty history state | Is it friendly? | **Correct.** "No registrations on record for this member." Confirmed in the browser. |

## Conclusion

- **Defects fixed this session:** 1 (**S3-D1**), with 14 regression tests, three
  negative controls and two browser confirmations.
- **Product decisions still required:** 4 (S3-O1 ... S3-O4). No behaviour changed.
- **Carried-forward decisions:** 2 (S3-C1, S3-C2).
- **Limitations recorded:** 2 (S3-L1, S3-L2).
- **Not defects:** 3 (S3-O5, S3-N1, S3-N2).
- **Regression status:** **250 passed**, 0 failed, 0 skipped, 0 errored, measured
  after all negative-control mutations were reverted.
- **Browser status:** 13 of 14 E2E scenarios executed; 12 fully passed and 1
  partially passed (stale-tab submission not reproducible through the UI). No
  scenario is claimed as passed without a captured screenshot or a recorded
  observation.
- No open item is reachable as a crash or data-loss issue through normal use.


================================================================================
SUPPLEMENTARY ROUND UPDATE - 2026-10-14
================================================================================
Scope: re-testing S3-E2E-13 and S3-E2E-14 only. No application code was changed
in this round, so no defect status changed except as noted below.

## S3-N1 re-confirmed by a genuine stale-tab submission

The previous round could not reproduce a stale-tab submission. This round did.

- Tab A withdrew registration 3: `POST /registrations/3/withdraw` -> 302.
- Tab B, still holding the pre-withdrawal page (`Status: Started`, Withdraw
  button present), then submitted the same form: a real second
  `POST /registrations/3/withdraw` -> 302, 23.53 ms, request and response bodies
  recorded as complete and replay-safe.
- Result: `Withdrawn` status re-written with the same value. Row count unchanged
  at 3. No duplicate (member, season) pair. No error, no 500.

**Status: confirmed, still NOT a defect.** The end state the user asked for is
true, no record is removed, and the UI no longer offers the button on a fresh
page load. The only imprecision is that the success flash is shown again even
though nothing changed, because `registration_withdraw` flashes after
`services.withdraw_registration` confirms the record exists. No change made.

The browser evidence for this is two distinct POSTs in the server log plus two
network captures with different timings; the two result screenshots are
byte-identical because the resulting page is identical.

**Note added:** this round tested two SEQUENTIAL submissions, each completing
before the next began. A true simultaneous double-submit race was NOT executed
and is not claimed. The operation is a plain idempotent
`UPDATE registrations SET status = 'Withdrawn'`, so no corruption is expected,
but that specific race remains untested.

## S3-L2 extended - native date control behaviour, confirmed in the browser

`member_form.html` renders `<input type="date" required>` with no `max`.

Newly confirmed in the browser this round:

- The control **accepts a future year** (typed `9999`) - there is no client-side
  future-date restriction. Evidence:
  `docs/testing/screenshots/sprint-3/S3-E2E-14-future-date-attempt.png`.
- The control refuses an impossible date such as `2026-02-30` outright - the
  segments will not accept that combination.
- An empty date is blocked by the `required` attribute.

Consequence confirmed: a future date must be caught by the **server**, and it is
(see the API supplemental evidence below). Adding `max` to the input would be a
presentation improvement only, giving faster client-side feedback. Not applied,
because it is not required by any acceptance criterion and would change the form
markup in a verification round.

## Tool limitation recorded (not an application defect)

The browser automation tool cannot drive the segmented native `type=date`
control to a complete value: its fill action rejects the control type, and
injected keystrokes are appended to the year segment (`99991`, `0018`) rather
than advancing to month and day. A `Tab` press commits a partial value.

Impact: submitting a *future* date through the browser form could not be
executed. That case is covered instead by the API supplemental test and by the
automated tests. This is a harness limitation, not a defect in the application,
and no application change is warranted.

## S3-D1 re-verified in this round

Not a new finding, but re-confirmed with a fresh disposable database:

| Check | Result |
|---|---|
| `GET /members/4` with stored `date_of_birth = 'not-a-date'` | **HTTP 200** - no 500 |
| Page content | `not-a-date (age cannot be read from the stored date)` |
| Amend that member's `Started` registration to `Complete` | **HTTP 400** with `This member's date of birth on record cannot be read, so the registration cannot be completed. Please correct the member's date of birth first.` |
| Stored registration status afterwards | still `Started` |
| Member treated as an adult? | No - the completion was refused |

Evidence: `sprint-3-e2e-checklist.md` supplementary section and
`docs/testing/screenshots/sprint-3/S3-E2E-14-unreadable-dob-*.png`.

## Server-side date validation re-confirmed (API supplemental, not browser)

Seven real HTTP POSTs to `POST /members/new`. Full table in
`docs/testing/sprint-3-api-dob-validation.txt`:

- valid adult DOB -> 200, member created
- valid junior DOB -> 200, member created
- future DOB -> 400 `Date of birth cannot be in the future.`
- `2026-02-30` -> 400 `Date of birth must be a valid date in YYYY-MM-DD format.`
- `not-a-date` -> 400 `Date of birth must be a valid date in YYYY-MM-DD format.`
- empty DOB -> 400 `Date of birth is required.`
- whitespace DOB -> 400 `Date of birth is required.`

No defect found. Every rejected input left the member count unchanged.

## Defect summary after this round

| ID | Status after this round |
|---|---|
| S3-D1 | Fixed (re-verified) |
| S3-O1 .. S3-O5 | unchanged - product decisions / expected behaviour |
| S3-C1, S3-C2 | unchanged - carried forward |
| S3-L1 | unchanged - schema limitation |
| S3-L2 | extended with confirmed browser behaviour; still not a defect |
| S3-N1 | confirmed by a real stale-tab submission; still not a defect |
| S3-N2 | unchanged - by design |

**Defects found in this round: none. Defects fixed in this round: none.** No
application code was modified.
