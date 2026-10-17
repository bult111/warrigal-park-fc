# Browser End-to-End Acceptance Results — 2026-10-16

Automated browser acceptance of the [Warrigal Park FC] application, executed
against a real running Flask instance driven by a real Microsoft Edge browser
over the Chrome DevTools Protocol.

- **Code under test**: `fd7b68c15d92e0511b8609f3c9ce84c9943724ee` (remote `main`),
  tree `a42f0465fee7fddeb6e8d498a5c2e86ca6d857fd`.
- **Local branch used**: `audit/final-verification-20261016` (based on
  `3205042ade4beef2753dde4c86fbb5292dc418c8`, whose tree is byte-identical to
  the remote `main` tree above).
- **Date**: 2026-10-16.
- **Result**: **37 / 37 scenarios PASS, 0 FAIL, 0 not executed.**
- **Screenshots**: `../screenshots/final-verification-20261016/` (22 PNG files).
- **Raw logs**: not published in this repository. The console logs and the
  machine-readable per-scenario results are preserved in the local test archive
  (`<LOCAL_ARCHIVE>`).
- **Path placeholders**: `<TEST_WORKSPACE>` is the scratch workspace outside the
  repository; `<LOCAL_ARCHIVE>` is the local test archive outside the repository.
  See `test-environment.md` for the full list.

Every scenario below was executed through the application's own HTML pages by
clicking real controls and submitting real forms. No scenario is marked PASS
without an executed run.

> This is **browser automation**, not human acceptance and not course-official
> sign-off.

## How the run worked

| Item | Value |
|------|-------|
| Application | `python run.py` from the project virtual environment |
| Bind address | `http://127.0.0.1:5066` |
| Database | `<TEST_WORKSPACE>/final-verify.db` (isolated temporary SQLite file) |
| Browser | Microsoft Edge `Edg/155.0.4283.45` (headless), CDP on `127.0.0.1:9333` |
| Driver | `cdp.mjs` — a dependency-free CDP client using Node's built-in `fetch`/`WebSocket` |
| Node | v24.9.0 |
| Part 1 | 35 scenarios, one run, from an empty database |
| Part 2 | 2 scenarios, after a scripted injection of legacy/inconsistent rows (see below) |

### Injected preconditions (part 2 only)

Two rows were written directly with SQLite, because the service layer would
never create them. They simulate real legacy/imported data. The injection script
is preserved as `inject_legacy.py` in the local test archive (`<LOCAL_ARCHIVE>`);
it asserts it is writing to the acceptance database and refuses any other target.

1. **Guardian with an unreadable `date_of_birth`** (`'not-a-date'`), linked to a
   junior member — a row of the kind that existed before the guardian
   date-of-birth column was introduced.
2. **A member whose stored date of birth no longer matches an existing team
   assignment**, leaving an inconsistent placement behind.

These injections are preconditions only. Every assertion about application
behaviour is made through the browser UI.

## Scenario results

| # | Scenario | Expected | Actual | Status | Screenshot(s) |
|---|----------|----------|--------|--------|---------------|
| 1 | **B1a** Dashboard opens with zero data | HTTP 200, title "Dashboard", stat cards present | title "Dashboard — Warrigal Park FC", all stat cards rendered | PASS | `01-dashboard-empty.png` |
| 2 | **B10a** Empty-state pages for every list | Each list page shows its empty-state message | empty states verified for `/members`, `/guardians`, `/registrations`, `/teams` | PASS | — |
| 3 | **B2a** Create members through the form | Each member is created and its detail page opens | 11 members created and listed | PASS | `02-members-list.png` |
| 4 | **B2b** Search members by partial name and by no-match | Search returns matches; an unmatched search shows the empty state | partial-name search and no-match search both correct | PASS | — |
| 5 | **B3** Update a member | Edited values persist and are shown | phone updated to 555-0100 and displayed | PASS | — |
| 6 | **B4** Deactivate and reactivate a member | Status toggles; the row is never deleted | Inactive then Active; member row retained throughout | PASS | `03-member-detail.png` |
| 7 | **B8a** Create teams | Teams created and listed with season and age group | 6 teams created | PASS | — |
| 8 | **B8b** Rename a team | New name stored and displayed | renamed to "Tigers Blue" and back to "Tigers" | PASS | — |
| 9 | **B8c** Remove a team keeps members and registrations | Removing a team deletes only the team | team removed after confirming the dialog; remaining teams Cubs, Eagles, Falcons, Lions, Tigers; Ava Adult still present | PASS | — |
| 10 | **A1a** Age group computed from date of birth and season | Registration stores the computed group | Mia Minor 2016-08-20 recorded as U12 for season 2026 | PASS | `04-registration-age-group.png` |
| 11 | **A1b** Age-group boundary around season-age 5/6 | Season age 6 is U8 and season age 5 is U6 | 2020-12-31 → U8 and 2021-01-01 → U6, either side of the calendar-year boundary | PASS | — |
| 12 | **A2** A hand-submitted age group cannot override the computed one | A POST carrying `age_group=Seniors` is ignored | submitted `age_group=Seniors`; stored value is the computed U14 | PASS | — |
| 13 | **A3** A member below the minimum age cannot be registered | HTTP 400, clear minimum-age message, no registration row | refused with the minimum-age message; no registration row created | PASS | `05-below-minimum-age-rejected.png` |
| 14 | **G1** An adult guardian is verified as an adult | Guardian detail reports a verified adult | Ada Adult (1980-07-07) shown as "verified adult" | PASS | `06-guardian-adult-verified.png` |
| 15 | **G2** An under-18 guardian is rejected | HTTP 400 with the adult requirement, no guardian row | refused with "A guardian must be at least 18 years old."; no row created | PASS | `07-guardian-underage-rejected.png` |
| 16 | **B5** Update a guardian | Edited guardian values persist | guardian phone updated and displayed | PASS | — |
| 17 | **A4+A6a** Complete registration auto-assigns; empty-team tie breaks on lowest team id | Leo Junior (U16) joins Tigers | assigned to 'Tigers' (tie between empty U16 teams broken by lowest id) | PASS | `08-auto-assign-tiebreak.png` |
| 18 | **A5+A6b** Fewest-players-first beats team id | Noah Net (U16) joins Lions | assigned to 'Lions' because it had fewer players than 'Tigers' | PASS | — |
| 19 | **A7** No matching team means no wrong assignment | Player stays unassigned and the UI says so | U18 registration completed with no U18 team; "currently unassigned" notice shown; no team row created | PASS | `09-no-matching-team.png` |
| 20 | **A8** Creating a matching team later assigns the waiting player | Sam Seniorish appears on the new U18 team | Juniors (U18) created; Sam Seniorish automatically placed on it | PASS | `10-auto-assign-on-team-create.png` |
| 21 | **A9** Creating a new team never silently moves an assigned player | Falcons stays empty; Leo stays in Tigers, Noah stays in Lions | Falcons left empty; Leo Junior still in Tigers, Noah Net still in Lions | PASS | — |
| 22 | **G4a** A junior with no eligible guardian cannot complete a registration | Completion refused with the guardian-rule message | Complete refused for Mia Minor with the under-18 guardian-rule message | PASS | `11-junior-missing-guardian-rejected.png` |
| 23 | **B6** Link a guardian to a member and view both directions | Both pages show the link | guardian → member and member → guardian views both show the link | PASS | `12-guardian-linked-junior.png` |
| 24 | **G4b** Completing after an adult guardian is linked auto-assigns the player | Mia Minor completes and joins Eagles (U12) | registration completed; auto-assigned to Eagles (U12) | PASS | `13-complete-after-guardian-shows.png` |
| 25 | **A10-prep** Junior with an adult guardian completes and joins the matching U8 team | Boundary Kid is auto-assigned to Cubs | completed; auto-assigned to Cubs (U8) | PASS | — |
| 26 | **B9** Add, move and remove a player manually | Each manual action accepted and reflected | remove → add → move → remove all succeeded with the expected messages | PASS | `14-manual-player-management.png` |
| 27 | **B9-neg** A member without a Complete registration cannot be added | Refused with an eligibility message | refused: no Complete registration for the team's season | PASS | — |
| 28 | **B7** Create, amend and withdraw a registration, preserving history | Amending recomputes the age group; withdrawal keeps the record | created (U14) → amended to 2028 (U16) → withdrawn; history retains the row | PASS | `15-registration-history-withdrawn.png` |
| 29 | **B12** Roster page shows player contact details | Roster lists the team members | Eagles roster lists Mia Minor with season and age group | PASS | `16-team-roster.png` |
| 30 | **G5** A compatible date-of-birth change keeps registrations consistent | Registration age group rewritten with the new date of birth | 2014-04-04 → 2016-04-04 rewrote the 2026 registration from U14 to U12 | PASS | `17-dob-change-consistent.png` |
| 31 | **G6+G7+G8** A date-of-birth change that would break a team assignment is refused atomically | HTTP 400, no partial write, no move, no duplicate | refused; date of birth still 2011-03-03; registration still U16; exactly 1 roster row | PASS | `18-dob-change-refused.png` |
| 32 | **B10b** Invalid email is rejected | Client-side validation blocks it; the server also rejects it | browser constraint validation flagged it and the server returned "Email address is not valid."; no member created | PASS | — |
| 33 | **B10c** Invalid season is rejected | A non four-digit season is refused | rejected with the four-digit-year message | PASS | — |
| 34 | **B10d** Unknown records redirect with a friendly flash | No traceback for missing members, guardians, registrations or teams | all four unknown-record paths flashed the expected message | PASS | — |
| 35 | **B1b** Dashboard reflects the created data | Non-zero counts | `{"Total Members":11,"Active Members":11,"Guardians":1,"Registrations":8,"Teams":6}` | PASS | `19-dashboard-final.png` |
| 36 | **G3** An unreadable guardian date of birth is never treated as an adult | Guardian shown as not verified; cannot satisfy the under-18 rule | detail page shows "Not verified as an adult"; Complete registration for the linked junior refused | PASS | `20-legacy-guardian-not-verified.png`, `21-legacy-junior-complete-rejected.png` |
| 37 | **A10** An incompatible existing team assignment is reported, not silently moved or duplicated | Saving surfaces the conflict and changes no team row | warning shown: *"the player is in 'Cubs' (U8) but their age group for 2026 is U10"*; Cubs still holds exactly 1 row for that player | PASS | `22-assignment-conflict-reported.png` |

## Response and error observations

- Every HTTP response with status ≥ 400 during the run was an **intended
  validation refusal**, all of them `400`, on:
  `/registrations/new` (×2 — below minimum age, junior without a verified adult
  guardian), `/guardians/new` (×1 — under-18 guardian), `/members/2/edit` (×1 —
  date-of-birth change that would break a team assignment), `/members/new` (×1 —
  invalid email) and `/teams/new` (×1 — invalid season).
- **Zero browser console errors** were recorded in either part.
- No unhandled traceback, `500` response or debug page appeared in any scenario.

## Things this run does not prove

- It is browser **automation**, not a human walkthrough and not course sign-off.
- Screens are captured at 1440×1000 in headless Edge; no other viewport, browser
  or assistive technology was exercised.
- No concurrent/multi-user access, no authentication, and no load behaviour was
  tested (the application is a documented single-user local tool).
- The legacy/inconsistent rows in part 2 were injected by script, not produced by
  ordinary use; the run shows how the UI *reports* them, not that the application
  can create them.
