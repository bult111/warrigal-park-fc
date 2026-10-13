# Sprint 1 — Core End-to-End Workflow Checklist

- **Date:** 2026-10-13
- **Branch:** `feature/sprint-1-qa-release`
- **Method:** see the per-scenario "Method" column. All checks ran against a
  temporary SQLite database (isolated; the real `instance/warrigal_park_fc.db`
  was never modified).
- **Evidence:** one-off script `_sprint1_e2e.py` (executed and then deleted).

The 19 workflow checks were performed against a temporary SQLite database using
a combination of Flask test client requests and direct service-layer calls. The
method used for each scenario is identified in the checklist. All recorded
automated workflow checks passed.

Method legend:

- **Flask test client** — an HTTP request sent through the Flask test client to
  a real route, with the response checked.
- **Service layer** — a direct call to an `app.services` function, checked
  against its return value.
- **Flask test client + service check** — an HTTP request followed by a
  service-layer call that verifies the resulting database state.

| ID | Scenario | Steps | Method | Expected | Actual | Result |
|----|----------|-------|--------|----------|--------|--------|
| M1 | Create member | POST `/members/new` with name, DOB, email, phone, address | Flask test client | Redirect to detail page, member shown | Detail page shows "Alice Junior" | Pass |
| M2 | Duplicate member name | Create a second member with the same name | Flask test client | Allowed; both records kept | Second create succeeded (200) | Pass |
| M3 | Query/search member | `services.list_members("Alice Junior")` | Service layer | Both duplicates returned | 2 records returned | Pass |
| M4 | Modify member | `services.update_member(...)` with new name/email | Service layer | Updated values persisted | Name and email updated | Pass |
| G1 | Create guardian | POST `/guardians/new` | Flask test client | Detail page shows guardian | "Bob Guardian" shown | Pass |
| G2 | Modify guardian | `services.update_guardian(...)` then `services.get_guardian(...)` | Service layer | New email persisted | Email updated | Pass |
| G3 | Link guardian ↔ junior member | POST `/guardians/<id>/link` with `member_id` | Flask test client | Member appears in guardian's linked list | "Alice Jnr" shown | Pass |
| R1 | Create registration | POST `/registrations/new` (Started) | Flask test client | Registration created as Started | 2026 / U16 Started | Pass |
| R2 | Junior guardian rule (deny) | Create junior registration directly as Complete, no guardian | Flask test client | Rejected with "under 18" message | HTTP 400 + message | Pass |
| R3 | Junior guardian rule (allow) | Link guardian, then `services.update_registration(...)` to Complete | Service layer | Completion succeeds | Status Complete | Pass |
| R4 | Withdraw + history | `services.withdraw_registration(...)`, then `services.member_registration_history(...)` | Service layer | Withdrawn status retained in history | 2025 = Withdrawn, 2026 still present | Pass |
| T1 | Create team | POST `/teams/new` | Flask test client | Team created | "Tigers" shown | Pass |
| T2 | Query team | `services.list_teams()` | Service layer | Team present with season | 2026 / U16 | Pass |
| P1 | Add eligible player | Add member with same-season Complete registration | Flask test client | Player added | "Alice Jnr" in team | Pass |
| P2 | Player eligibility (wrong season) | Add member registered for a different season | Flask test client + service check | Rejected; player not added | Player not in team | Pass |
| P3 | Move player already assigned to target team | Player is assigned to both source and target teams; attempt move source → target | Flask test client + service check | Rejected because already assigned to target; both assignments unchanged | Rejected ("This player is already in that team."); player still assigned to both teams | Pass |
| P4 | Move player between teams | `services.remove_player_from_team(...)`, then `services.move_player(...)` | Service layer | Player leaves source, joins target | Moved correctly | Pass |
| R5 | Roster + contact info | GET `/teams/<id>/roster` | Flask test client | Player and email shown | "Alice Jnr" + email shown | Pass |
| D1 | Dashboard | GET `/` | Flask test client | Dashboard renders | 200 + "Dashboard" | Pass |

**Note on P3:** the original one-off script confirmed the move was rejected and
the player remained in the source team. During this review the scenario was
re-executed on a fresh temporary database, additionally confirming the player
remained assigned to both the source and target teams after the rejection (see
the P3 "Actual" cell).

## Result summary

- Executed: 19
- Pass: 19
- Fail: 0
- Not tested (manual browser click-through): 1 — see below

## Not tested / pending manual verification

- **Real browser UI click-through** (Chrome/Edge against a live server) was not
  performed because no browser-automation tool was available in this session.
  The HTTP scenarios were exercised through the Flask test client and the other
  scenarios through direct service-layer calls; neither is a substitute for a
  human visual pass. A human should still do a quick visual pass of the pages
  in a browser before release.
