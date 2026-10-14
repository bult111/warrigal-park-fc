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

- Automated workflow checks: 19 executed, 19 Pass, 0 Fail.
- Manual browser verification (Microsoft Edge): 5 executed, 5 Pass, 0 Fail — see
  `Manual Browser Verification` below.

## Manual Browser Verification

- **Performed by:** the user, in Microsoft Edge 155.0.4283.45.
- **Date:** 2026-10-13 (screenshots saved 23:41–23:50 local time).
- **Screenshots:** `C:\Users\z\Desktop\ScreenShot\Sprint1_Browser_Test`
  (6 PNG files). All six were reviewed and mapped to scenarios by page content;
  see the screenshot index below.

### Application startup (terminal HTTP smoke test — NOT a browser test)

To prepare for manual testing, the app was started against a fresh temporary
database and confirmed to serve over HTTP from the terminal:

- Command: `python run.py` (venv) with `DATABASE`, `HOST=127.0.0.1`,
  `PORT=5001`, `FLASK_DEBUG=0`.
- Temporary database:
  `C:\Users\z\AppData\Local\Temp\dsh-EXtiRJ\warrigal_sprint1_browser_qa.db`
- URL: `http://127.0.0.1:5001`

| Path | HTTP status | Rendered heading |
|------|-------------|------------------|
| `/` | 200 | Dashboard |
| `/members` | 200 | Members |
| `/guardians` | 200 | Guardians |
| `/registrations` | 200 | Registrations |
| `/teams` | 200 | Teams |

This confirms the app boots and serves pages; it is not browser manual testing
and is not a substitute for it.

### Browser scenario results (Microsoft Edge, manual)

| Test ID | Scenario | Steps performed | Result | Evidence |
|---------|----------|-----------------|--------|----------|
| MB-1 | Dashboard | Open the home page; check the stat cards, navigation links and main content render correctly. | Pass | S1 |
| MB-2 | Member management | Create a test member, search for them in the list, edit one field, and confirm the change saved. | Pass | S2 |
| MB-3 | Guardian management | Create a fictional guardian and a junior test member, link them, and check the link result. | Pass | S3 |
| MB-4 | Registration & under-18 rule | Try to complete a junior registration with no guardian (system should reject it), then link a guardian, complete the registration, and view the history. | Pass | S4, S5 |
| MB-5 | Team & roster | Create a test team with a season matching the player's registration, add an eligible player, and check the roster. | Pass | S6 |

All five manual browser scenarios passed. No failures, blockers, or new defects
were reported.

Evidence note: S2 evidences member creation (the search and edit steps were
user-reported without a dedicated screenshot); S4 and S5 evidence the under-18
rejection and the completed registration (the history view was user-reported);
S6 evidences the team with the player added (the dedicated roster view was
user-reported).

### Procedure followed (manual, Microsoft Edge)

Start the app with a fresh temporary database (never the real
`instance/warrigal_park_fc.db`):

```powershell
cd "C:\Users\z\Desktop\deepseek harness\warrigal-park-fc"
$env:DATABASE = Join-Path $env:TEMP ("warrigal_sprint1_browser_" + (Get-Date -Format "yyyyMMdd_HHmmss") + ".db")
$env:HOST = "127.0.0.1"
$env:PORT = "5001"
$env:FLASK_DEBUG = "0"
& ".\.venv\Scripts\python.exe" -m flask --app run.py init-db
& ".\.venv\Scripts\python.exe" run.py
```

Then open `http://127.0.0.1:5001` in Microsoft Edge and follow these steps,
using fictional data only (for example `Sprint1 Browser QA 20261013`,
`sprint1.browser@example.com`).

1. **MB-1 Dashboard** — open `/`; confirm the header navigation (Dashboard /
   Members / Guardians / Registrations / Teams) and the five stat cards render
   without tracebacks or broken layout.
2. **MB-2 Member management** — Members → `+ New Member`; fill Name, Date of
   Birth, Email, Phone, Address → `Create member`; confirm the success flash and
   detail page. Return to Members and search the name; `Edit`, change a field,
   `Save changes`, reopen the detail and confirm the change persisted.
3. **MB-3 Guardian management & link** — Guardians → `+ New Guardian`; create a
   guardian. Members → create a junior member whose date of birth makes them
   under 18. Open the guardian's page → `Link a Member`, select the junior,
   `Link member`; confirm the junior appears under "Linked Junior Members".
4. **MB-4 Registration & under-18 rule** — Registrations → `+ New Registration`;
   select the junior member, a season, an age group, status `Started` →
   `Create registration`. Then `Amend` and set status `Complete` while the
   junior still has no guardian; confirm the form is rejected with the "under
   18" message. Link a guardian (see MB-3), set `Complete` again and confirm it
   succeeds. Open the member's detail and confirm the registration appears in
   the history. Create another registration and `Withdraw Registration`; confirm
   it stays in the history with `Withdrawn` status.
5. **MB-5 Team & roster** — Teams → `+ New Team`; create a team whose season
   matches the test member's registration season. Open the team → `Add Player`,
   select the eligible member, `Add player`. Open `View Roster` and confirm the
   player name and contact info appear. Optionally test `Remove` or `Move`, but
   do not delete other test data.

### Screenshot index (reviewed)

All six are genuine Microsoft Edge captures of the app at
`http://127.0.0.1:5001`, saved in
`C:\Users\z\Desktop\ScreenShot\Sprint1_Browser_Test`:

| Ref | File | Page observed | Scenario |
|-----|------|---------------|----------|
| S1 | `dc03d9c8c93579bfaafa734a1f62856c.png` | Dashboard (`/`): navigation, five stat cards, Welcome card | MB-1 |
| S2 | `66c3d7b5fe68d2f52cab381fe1e785ca.png` | Member detail (`/members/1`): flash "Member 'zz' created."; zz, DOB 2010-06-08 (age 16), Active | MB-2 |
| S3 | `e2e818be367e0f637d9fed652ac2f818.png` | Guardian detail (`/guardians/1`): flash "Member linked to guardian."; linked junior zz (age 16) | MB-3 |
| S4 | `ffff7e44550f88877b76d2b10aa1e708.png` | New Registration (`/registrations/new`): rejected — "Registration cannot be completed because a member under 18 must have at least one guardian." | MB-4 (deny) |
| S5 | `fe0bb7bb7b32f7d3d10ef08e3d00509b.png` | Registration detail (`/registrations/1`): flash "Registration created."; zz, 2026, U16, Complete | MB-4 (allow) |
| S6 | `9bce8a3c3898649de469f46bdabd1e5c.png` | Team detail (`/teams/1`): flash "Player added to team."; team "123" (2026 / U16); Players lists zz | MB-5 |

Screenshot save-times do not strictly follow the scenario order, so evidence is
mapped by page content rather than filename order. No real personal data,
passwords, or tokens are visible in the screenshots.
