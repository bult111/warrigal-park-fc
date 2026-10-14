# Sprint 1 — Defect Log

- **Date:** 2026-10-13
- **Branch:** `feature/sprint-1-qa-release`
- **Scope:** results of the regression suite (79 tests) plus a manual code
  review of `app/services.py`, `app/routes.py`, `app/database.py`,
  `app/models.py`, and the templates.

## Summary

No critical or major defects were found. The full regression suite passes
(79/79) and the 19 core end-to-end workflows all pass. The items below are
low-severity observations and known limitations discovered during code review;
none was a provable bug that warranted a code change this sprint. Each is
recorded with a recommendation for the team to decide on.

| ID | Area | Severity | Status | Description |
|----|------|----------|--------|-------------|
| D1 | Registrations | Low | Open (decision needed) | A member can be given more than one registration for the same season. `create_registration` / `update_registration` do not check for an existing same-`member_id` + same-`season` row, and the schema has no uniqueness constraint. `docs/architecture.md` describes registrations as "(one per season)". |
| D2 | Teams / players | Low | Open (decision needed) | Withdrawing a registration does not remove the member from teams they were already placed in; the roster continues to list them. `withdraw_registration` only updates the registration status and never touches `team_players`. |
| D3 | UX robustness | Low | By design / minor | `remove_player_from_team` and `unlink_guardian_member` are silent no-ops when the relationship does not exist — the route always flashes "removed"/"unlinked" even if nothing changed. No data corruption occurs. |
| D4 | Environment | Info | Not a code defect | The `.venv` contains packages not listed in `requirements.txt` (`lxml`, `pypdf`, `python-docx`). None are imported by the application. This is environment hygiene only and does not affect the app or tests. |

## Reproduction and analysis

### D1 — duplicate same-season registration

- **Reproduce:** create a member, then call `create_registration(member_id,
  "2026", "U16")` twice. Both rows are inserted.
- **Expected (per architecture doc):** one registration per member per season.
- **Actual:** duplicates are allowed.
- **Recommendation:** if one-per-season is a hard rule, add a UNIQUE
  `(member_id, season)` constraint (plus a friendly pre-insert check); if
  re-registration within a season is legitimate, update `architecture.md` to
  drop the "(one per season)" wording. Not changed this sprint to avoid making
  a product decision unilaterally.

### D2 — withdrawn registration still listed on roster

- **Reproduce:** register a member, add them to a team, then withdraw the
  registration; the member still appears in `team_players` / the roster.
- **Expected:** unclear from current requirements; the README only states a
  player must have a non-withdrawn registration *to be added*.
- **Actual:** the player remains on the roster after withdrawal.
- **Recommendation:** confirm whether withdrawal should auto-remove the player
  from teams, and if so implement it in `withdraw_registration`. Not changed
  this sprint (behaviour change requiring a product decision).

### D3 — silent no-op on remove/unlink

- **Reproduce:** POST remove for a player not in the team (or unlink a guardian
  not linked to the member). The operation reports success.
- **Impact:** cosmetic; the database is left in a valid state.
- **Recommendation:** optionally return a "nothing to remove" notice. Not
  changed this sprint (no functional harm).

### D4 — extra packages in `.venv`

- **Analysis:** `grep` across the repository found no import of `lxml`,
  `pypdf`, or `python-docx`; they are unrelated to the application.
- **Recommendation:** recreate the virtual environment from `requirements.txt`
  if a clean environment is desired. No action required for the app.

## Conclusion

- Real defects fixed this sprint: **none** (no provable defect required a code
  change; the regression suite and E2E flows all pass).
- Items carried forward for the team: D1 and D2 (product decisions), D3
  (optional UX), D4 (environment hygiene).
