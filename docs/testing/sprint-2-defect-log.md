# Sprint 2 — Defect Log

- **Sprint:** Sprint 2 — Epic: Member and Guardian Management
- **Scope:** findings from a code review of `app/services.py`, `app/routes.py`,
  `app/database.py`, `app/models.py` and the member/guardian templates, plus
  the measured regression-suite results recorded in
  `sprint-2-test-results.md`.
- **Document status:** findings were confirmed by reproduction before being
  recorded. Nothing in this log is speculative.

## Summary

| ID | Area | Story | Severity | Status |
|----|------|-------|----------|--------|
| S2-D1 | Guardian unlink feedback | MSD426GXUST25-7 | Low | **Fixed** (Sprint 2) |
| S2-F1 | Team player removal feedback | Deferred to Sprint 4 | Low | Deferred — change reverted, documented |
| S2-O1 | Member deactivation scope | MSD426GXUST25-4 | Observation | Decision required |
| S2-O2 | Guardian removal after completion | MSD426GXUST25-7 | Observation | Decision required |
| S2-C1 | Duplicate same-season registrations (Sprint 1 D1) | n/a | Low | Open — decision required |
| S2-C2 | Withdrawn registration still on a roster (Sprint 1 D2) | n/a | Low | Open — decision required |
| S2-N1 | Browser vs server validation layering | -2, -3 | Info | Not a defect — documented |

One defect was found and fixed inside the Member and Guardian Management epic.
One related defect was found outside that epic and has been deferred to
Sprint 4, with the out-of-scope change reverted. Two new observations and two
carried-forward Sprint 1 items require a product decision; none of them was
implemented unilaterally.

---

## S2-D1 — Guardian unlink reported success when no link existed

- **Affected Story:** MSD426GXUST25-7 (Link Guardians to Junior Members).
- **Severity:** Low. No data corruption; the database was left valid. The
  impact was misleading user feedback.
- **Related:** Sprint 1 defect log item **D3**, which recorded this as "by
  design / minor" and did not change it. Sprint 2 required verification that
  invalid operations are handled safely, so it was re-examined and fixed.

### Reproduction (before the fix)

1. Create a member and a guardian that are **not** linked.
2. Submit `POST /guardians/<guardian_id>/unlink/<member_id>` (for example by
   re-submitting a stale guardian page after the member was already unlinked).
3. Observe the flash message.

### Expected

An unlink that changed nothing should say so, rather than reporting a success
that did not happen.

### Actual (before the fix)

The route always flashed `Member unlinked from guardian.`, even when no link
existed and no row was deleted.

### Root cause

`app/services.py`: `unlink_guardian_member` performed a `DELETE` and returned
nothing, without checking that either identifier existed.
`app/routes.py`: `guardian_unlink` flashed success unconditionally after the
call.

### Fix applied

- `app/services.py` — `unlink_guardian_member` now raises `ServiceError`
  (`Guardian not found.` / `Member not found.`) for unknown identifiers and
  returns `True` only when a link row was deleted, otherwise `False`.
- `app/routes.py` — `guardian_unlink` flashes `Member unlinked from guardian.`
  on success and `That member was not linked to this guardian.` otherwise.

No schema change. The function still never deletes a member or guardian.

### Retest results

| Check | Command / method | Result |
|---|---|---|
| New service tests for both outcomes | `.venv\Scripts\python.exe -m pytest tests/test_member_guardian_workflows.py` | 54 passed |
| Working-tree fix present | `... -k "no_op or nothing_was_linked"` | 2 passed |
| Negative control: fix deliberately reverted | `... -k "no_op or nothing_was_linked"` | **1 failed**, 1 passed, 52 deselected |
| Fix restored | `.venv\Scripts\python.exe -m pytest` | 133 passed, 0 failed |
| Browser: real unlink of a linked member | scenario S2-E2E-06 | Passed — flashed `Member unlinked from guardian.` |
| Browser: no-op unlink path | scenario S2-E2E-10 | **Partially verified** — see the scenario for why |

The control was re-executed during the pre-upload review and reproduced the
same result. Retest status: **Fixed and verified by automated tests.** The
success path was additionally confirmed in a real browser; the no-op path in the
browser is recorded as partially verified because the stale-tab reproduction
could not be driven reliably through the UI.

---

## S2-N1 — Browser-level validation fires before server-side messages

- **Affected Stories:** MSD426GXUST25-2, MSD426GXUST25-3.
- **Severity:** Info — **not a defect**. Recorded because it affects how the
  acceptance criteria are demonstrated.
- **Found during:** browser execution of scenario S2-E2E-08.

### Description

Validation is enforced in two layers. The form templates use HTML5 constraints
(`required` on Name and Date of Birth, `type="email"` on Email), so in a modern
browser the **browser blocks two of the checklist's invalid submissions before
they reach the server**:

- an empty Name or Date of Birth is stopped by `required`;
- a malformed email such as `nope` is stopped by `type="email"`.

The server-side messages (`Name is required.`,
`Email address is not valid.`) are therefore not reached through the normal form
in a modern browser. They remain correct as defence in depth (for example if
HTML5 validation is bypassed) and are proven by the automated tests, which post
directly to the server.

Values that pass the browser's checks but are still invalid **do** reach the
server. Observed in the browser: a future date of birth (`2999-01-01`) produced
HTTP 400 with the flash `Date of birth cannot be in the future.`, the typed
values were retained in the form, and no record was created.

### Impact

None on data integrity. The practical impact is on test evidence: a tester
following the original S2-E2E-08 steps would see the browser's own field
message rather than the application's flash for two of the cases. The checklist
has been corrected to describe this accurately.

### Recommendation

No code change. Scenario S2-E2E-08 in
`docs/testing/sprint-2-e2e-checklist.md` now explains the two layers so future
testers do not report a false defect.

---

## S2-F1 — Team player removal feedback (deferred to Sprint 4)

- **Affected area:** team and player management — **not** the Member and
  Guardian Management epic.
- **Severity:** Low. Same silent-success pattern as S2-D1; no data corruption.
- **Description:** `remove_player_from_team` in `app/services.py` performs a
  `DELETE` without checking that the team and member exist, and `player_remove`
  in `app/routes.py` always flashes
  `Player removed from team. Registration was kept.` — including when the
  member was not in the team. This is the second half of Sprint 1 defect **D3**.

### Scope decision

An equivalent fix (validate the identifiers, return whether a row was removed,
and flash accordingly) was implemented during the initial Sprint 2 work.
Because team and player removal belongs to the **Team and Roster Management**
epic planned for **Sprint 4**, that change was **reverted** so that Sprint 2
contains no out-of-epic modifications. Both files were restored to their
pre-Sprint-2 behaviour:

- `app/services.py` — `remove_player_from_team` again only checks that the team
  exists (its original check) and returns nothing.
- `app/routes.py` — `player_remove` again flashes success unconditionally.

Nothing was removed or weakened: no test in the suite covered this code path,
so the revert left the suite total unchanged at 133 passed.

### Recommendation for Sprint 4

Apply the same treatment as S2-D1: validate both identifiers, return whether a
membership row was deleted, and flash an accurate message.

---

## S2-O1 — Scope of member deactivation is undefined

- **Affected Story:** MSD426GXUST25-4 (Deactivation of Members).
- **Severity:** Observation — not a defect against any written requirement.
- **Description:** The repository defines deactivation only as a status change
  ("Soft deactivation. Setting a member inactive changes their status; it never
  deletes the member." — `README.md`). It does not state what should happen to
  a deactivated member's team placement, future registrations, or guardian
  links.
- **Actual behaviour (confirmed):** team placement, registrations and guardian
  links are all preserved; only `status` changes. A deactivated member remains
  listed in `team_players` and on rosters, and can still be added to a team if
  they hold a non-withdrawn registration for that season.
- **Decision required:** confirm whether an inactive member should be excluded
  from rosters, blocked from new registrations, or blocked from being added to
  teams. The current behaviour is self-consistent and was **not** changed,
  because inventing a rule would risk contradicting the requirements.
- **Evidence:** `app/services.py::set_member_status`, `set_member_inactive`,
  `add_player_to_team`, `team_players`; new tests
  `test_deactivate_preserves_registrations_and_guardians` and
  `test_deactivate_does_not_remove_team_placement`.

## S2-O2 — Removing a guardian does not revisit a completed registration

- **Affected Story:** MSD426GXUST25-7 (Link Guardians to Junior Members).
- **Severity:** Observation — not a defect against any written requirement.
- **Description:** The under-18 guardian rule is enforced at the moment a
  registration becomes `Complete`. If the guardian link is removed afterwards,
  the registration remains `Complete` and the junior is left without a linked
  guardian.
- **Actual behaviour (confirmed):** `unlink_guardian_member` changes only the
  `guardian_members` table; it does not inspect or downgrade registrations.
- **Decision required:** confirm whether unlinking the last guardian of a
  junior with a `Complete` registration should be blocked, should downgrade the
  registration, or should be allowed with the registration left as historical
  fact. Not changed, to avoid inventing a rule.
- **Evidence:** `app/services.py::unlink_guardian_member`,
  `can_complete_registration`, `update_registration`.

## S2-C1 — Duplicate same-season registrations (Sprint 1 D1, carried forward)

- **Status:** Open — product decision required. **Not** the same question as
  duplicate member names (Story MSD426GXUST25-5).
- **Description:** A member can be given more than one registration for the
  same season. `create_registration` and `update_registration` do not check for
  an existing same-member, same-season row, and the schema has no uniqueness
  constraint, while `docs/architecture.md` describes registrations as "one per
  season".
- **Actual behaviour:** duplicates are allowed.
- **Recommendation (unchanged from Sprint 1):** if one-per-season is a hard
  rule, add a `UNIQUE (member_id, season)` constraint plus a friendly
  pre-insert check; otherwise correct the wording in `docs/architecture.md`.
- **Sprint 2 note:** a test
  (`test_duplicate_names_are_not_duplicate_registrations`) was added to make the
  distinction between the two questions explicit in the suite.

## S2-C2 — Withdrawn registration still listed on a roster (Sprint 1 D2, carried forward)

- **Status:** Open — product decision required.
- **Description:** Withdrawing a registration does not remove the member from
  teams they were already placed in.
- **Actual behaviour:** `withdraw_registration` updates only the registration
  status; the member remains in `team_players` and on the roster.
- **Recommendation (unchanged from Sprint 1):** confirm whether withdrawal
  should auto-remove the player, and if so implement it in
  `withdraw_registration`.

## Items explicitly not treated as defects

The following were investigated during Sprint 2 and confirmed to be correct, so
no change was made:

| Area | Investigation | Outcome |
|---|---|---|
| Member/guardian edit forms | Suspected that typed values were lost after a validation error. | **Not a defect.** The form re-renders with the submitted values retained, while the stored record is unchanged. Covered by new tests. |
| Failure feedback on invalid create | Suspected that the `errors` variable passed to the form templates was never rendered. | **Not a defect.** Routes flash the same message before rendering, so the user sees clear feedback. Covered by new tests. |
| Guardian contact consistency | Consulted the schema and templates for stale duplicated contact data (Story MSD426GXUST25-8). | **Correct by design.** Guardian contact is stored once in `guardians`; `guardian_members` has no contact columns and views join to the guardian row, so updates appear everywhere. Guarded by a new structural test. |
| Duplicate member names | Checked that duplicates remain separate through create, search, update and detail views. | **Correct.** Identified by `id`, never by name. |
| Extra packages in the old virtual environment (Sprint 1 D4) | The Sprint 1 `.venv` belonged to a different machine and is not present in this working copy. | **Not applicable here.** No unused packages were introduced; dependencies were installed strictly from `requirements.txt`. |

## Conclusion

- **Defects fixed this sprint:** 1 (S2-D1, previously Sprint 1 D3, guardian
  unlink only).
- **Defects deferred to Sprint 4:** 1 (S2-F1, team player removal; the
  out-of-scope change was reverted).
- **New observations requiring a decision:** 2 (S2-O1, S2-O2).
- **Carried-forward decisions:** 2 (S2-C1 / D1, S2-C2 / D2).
- **Regression status:** 133 passed, 0 failed, 0 skipped, 0 errored — measured
  after the scope cleanup and after restoring the fix.
- No open defect is a crash, data-loss or data-corruption issue.
- No out-of-epic source change remains in the Sprint 2 working tree.
