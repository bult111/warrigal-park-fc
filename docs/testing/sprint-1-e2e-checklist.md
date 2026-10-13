# Sprint 1 — Core End-to-End Workflow Checklist

- **Date:** 2026-10-13
- **Branch:** `feature/sprint-1-qa-release`
- **Method:** Flask test client against a temporary SQLite database (isolated;
  the real `instance/warrigal_park_fc.db` was never modified).
- **Evidence:** one-off script `_sprint1_e2e.py` (executed and then deleted).

Every scenario below was executed through the real HTTP routes and produced the
listed result. All automated scenarios passed.

| ID | Scenario | Steps | Expected | Actual | Result |
|----|----------|-------|----------|--------|--------|
| M1 | Create member | POST `/members/new` with name, DOB, email, phone, address | Redirect to detail page, member shown | Detail page shows "Alice Junior" | Pass |
| M2 | Duplicate member name | Create a second member with the same name | Allowed; both records kept | Second create succeeded (200) | Pass |
| M3 | Query/search member | `list_members("Alice Junior")` | Both duplicates returned | 2 records returned | Pass |
| M4 | Modify member | Update name/email via service | Updated values persisted | Name and email updated | Pass |
| G1 | Create guardian | POST `/guardians/new` | Detail page shows guardian | "Bob Guardian" shown | Pass |
| G2 | Modify guardian | Update guardian email | New email persisted | Email updated | Pass |
| G3 | Link guardian ↔ junior member | POST `/guardians/<id>/link` with `member_id` | Member appears in guardian's linked list | "Alice Jnr" shown | Pass |
| R1 | Create registration | POST `/registrations/new` (Started) | Registration created as Started | 2026 / U16 Started | Pass |
| R2 | Junior guardian rule (deny) | Create junior registration directly as Complete, no guardian | Rejected with "under 18" message | HTTP 400 + message | Pass |
| R3 | Junior guardian rule (allow) | Link guardian, then complete registration | Completion succeeds | Status Complete | Pass |
| R4 | Withdraw + history | Withdraw a registration, read history | Withdrawn status retained in history | 2025 = Withdrawn, 2026 still present | Pass |
| T1 | Create team | POST `/teams/new` | Team created | "Tigers" shown | Pass |
| T2 | Query team | `list_teams()` | Team present with season | 2026 / U16 | Pass |
| P1 | Add eligible player | Add member with same-season Complete registration | Player added | "Alice Jnr" in team | Pass |
| P2 | Player eligibility (wrong season) | Add member registered for a different season | Rejected; player not added | Player not in team | Pass |
| P3 | Move player (already in target) | Move a player who is already in the target team | Rejected; player unchanged | Player still in source team | Pass |
| P4 | Move player between teams | Remove from target, then move | Player leaves source, joins target | Moved correctly | Pass |
| R5 | Roster + contact info | GET `/teams/<id>/roster` | Player and email shown | "Alice Jnr" + email shown | Pass |
| D1 | Dashboard | GET `/` | Dashboard renders | 200 + "Dashboard" | Pass |

## Result summary

- Executed: 19
- Pass: 19
- Fail: 0
- Not tested (manual browser click-through): 1 — see below

## Not tested / pending manual verification

- **Real browser UI click-through** (Chrome/Edge against a live server) was not
  performed because no browser-automation tool was available in this session.
  The routes, form submissions, redirects, flash messages and page rendering
  were verified through the Flask test client instead. A human should still do
  a quick visual pass of the pages in a browser before release.
