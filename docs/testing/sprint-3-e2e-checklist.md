# Sprint 3 — End-to-End Checklist

- **Sprint:** Sprint 3 — Epic: Registration and Eligibility
- **Stories:** `MSD426GXUST25-10` ... `MSD426GXUST25-14`
- **Method:** a real Chromium-based browser (Microsoft Edge) driving the live
  Flask application, with screenshots captured for each executed scenario.
- **Document status:** **EXECUTED** in this session. Actual outcomes below are
  observations from that run, not expectations.
- **Evidence folder (absolute path):**
  `C:\Users\HP\Documents\GitHub\warrigal-park-fc\docs\testing\screenshots\sprint-3\`
- **Evidence index with SHA-256 hashes:** `docs/testing/sprint-3-screenshots.txt`

> **How to read the status column.**
> The run was performed with a browser-automation tool driving a real browser
> against the real Flask application served on `http://127.0.0.1:5000`, using a
> disposable SQLite database. It is genuine browser evidence, but it is **not a
> human acceptance sign-off**. A human should still confirm these workflows
> before the Stories are marked Done in Jira.
>
> **One scenario is partial.** S3-E2E-13's stale-tab submission could not be
> reproduced through the UI (see that scenario). It is marked **PASS (partial)**
> and the unverified half is stated explicitly. Nothing is marked PASS without a
> screenshot or a recorded observation.
>
> **Automated tests are not browser tests.** `pytest` results live in
> `sprint-3-test-results.md` and describe HTTP-level behaviour only.

## Preconditions used for this run

- Disposable database `instance/sprint3_e2e_round2.db` (git-ignored via `*.db`),
  created with `flask --app run.py init-db`, deleted at the end of the run.
- Application served on `http://127.0.0.1:5000` via `python run.py` with
  `DATABASE=sprint3_e2e_round2.db`, `PORT=5000`, `FLASK_DEBUG=0`.
- Only synthetic data. No real member information and no production database was
  touched.
- Seeded precondition data (created through the service layer, see
  `sprint-3-handover.md` for the seeding script):

  | Member | DOB | Age on 2026-10-14 | Purpose |
  |---|---|---|---|
  | Adult Tester (id 1) | 1996-10-14 | 30 | adult, no guardian needed |
  | Junior Tester (id 2) | 2014-10-14 | 12 | junior, guardian rule |
  | Boundary Tester (id 3) | 2008-10-14 | 18 (birthday today) | boundary — adult |
  | Tomorrow Tester (id 4) | 2008-10-15 | 17 (birthday tomorrow) | boundary — junior |
  | Second Tester (id 5) | 2001-10-14 | 25 | history isolation control |
  | Guardian Tester (id 1) | — | — | guardian link |

  Two pre-existing registrations for Second Tester: season 2025 / U14 and 2026 / U16.

## Summary

| Test ID | Story | Scenario | Status |
|---|---|---|---|
| S3-E2E-01 | `MSD426GXUST25-10` | Create a valid registration | **PASS** |
| S3-E2E-02 | `MSD426GXUST25-10` | Reject missing required fields | **PASS** |
| S3-E2E-03 | `MSD426GXUST25-11` | Amend a registration | **PASS** |
| S3-E2E-04 | `MSD426GXUST25-11` | Reject an invalid amendment without changing stored data | **PASS** |
| S3-E2E-05 | `MSD426GXUST25-12` | Withdraw a registration and verify history is retained | **PASS** |
| S3-E2E-06 | `MSD426GXUST25-13` | View a member's registration history | **PASS** |
| S3-E2E-07 | `MSD426GXUST25-13` | Verify history isolation between members | **PASS** |
| S3-E2E-08 | `MSD426GXUST25-13` | Verify the empty-history state | **PASS** |
| S3-E2E-09 | `MSD426GXUST25-14` | Eighteenth-birthday boundary: today vs tomorrow | **PASS** |
| S3-E2E-10 | `MSD426GXUST25-14` | Block an under-18 registration without a guardian | **PASS** |
| S3-E2E-11 | `MSD426GXUST25-14` | Permit an eligible under-18 registration with a valid guardian | **PASS** |
| S3-E2E-12 | `MSD426GXUST25-14` | Adult registration does not need the under-18 rule | **PASS** |
| S3-E2E-13 | `MSD426GXUST25-12` | Withdrawal across stale browser tabs | **PASS (partial)** — stale-tab submission not reproducible through the UI |
| S3-E2E-14 | `MSD426GXUST25-14` / `-10` | Invalid date-of-birth handling | **PASS (partial)** — client-side enforcement observed; server rules proven by automated tests only |

**Totals: 14 executed, 12 PASS, 2 PASS (partial), 0 FAIL, 0 BLOCKED, 0 NOT TESTED.**

Registration and member ids used by the run are recorded in each scenario. The
database ended the run with 7 registrations (ids 1-7), 5 members, 1 guardian and
1 guardian link; row counts were compared before and after the withdrawal steps.

---

## S3-E2E-01 — Create a valid registration

- **Story:** `MSD426GXUST25-10` — **Status: PASS**

| Step | Action | Observed result |
|---|---|---|
| 1 | Opened **Registrations -> + New Registration** | New Registration form: Member select, Season, Age Group, Status (default `Started`) |
| 2 | Chose `Adult Tester (1996-10-14)`, Season `2027`, Age Group `Seniors`, Status `Started` | All fields accepted |
| 3 | Clicked **Create registration** | `POST /registrations/new` -> 302; page `/registrations/3` with green flash `Registration created.` |
| 4 | Read the detail table | Member `Adult Tester` (linked), Season `2027`, Age Group `Seniors`, Status badge `Started` |
| 5 | Opened `/members/1` | **Registration History** listed `2027 / Seniors / Started` with a **View** link |
| 6 | Checked the Registrations list | The new row appeared for `Adult Tester` |

- **Expected result:** created, persisted, visible on the detail page and in the
  member's history.
- **Actual result:** exactly as expected. Registration id 3 created.
- **Evidence:** `S3-E2E-01-new-registration-form.png`,
  `S3-E2E-01-registration-created.png`
- **Observations:** none.

## S3-E2E-02 — Reject missing required fields

- **Story:** `MSD426GXUST25-10` — **Status: PASS**

| Step | Action | Observed result |
|---|---|---|
| 1 | Submitted the blank form (no member chosen) | The **browser blocked submission** and showed its own field message (`请在列表中选择项目。`). No request was sent |
| 2 | Chose `Adult Tester`, typed a Season of three spaces and Age Group `U16`, submitted | `POST /registrations/new` -> **HTTP 400** with red flash `Season is required.` |
| 3 | Read the re-rendered form | Member selection and Age Group `U16` were retained; Season was blank |
| 4 | Checked the database | Registration count unchanged at 3 — no partial record |

- **Expected result:** missing or whitespace-only required fields never create a
  record, and the user gets a clear message from either layer.
- **Actual result:** exactly as expected. This confirms the Sprint 2 finding
  S2-N1: HTML5 validation fires first for an empty required field, and a value
  the browser accepts (whitespace) is then rejected server-side.
- **Evidence:** `S3-E2E-02-browser-blocks-empty-member.png`,
  `S3-E2E-02-season-required-server-400.png`
- **Observations:** the browser message is rendered in the browser's own locale
  (Chinese) because the test profile is configured that way; this is browser
  chrome, not application output.

## S3-E2E-03 — Amend a registration

- **Story:** `MSD426GXUST25-11` — **Status: PASS**

| Step | Action | Observed result |
|---|---|---|
| 1 | Opened `/registrations/3` -> **Amend** | Amend form pre-filled: `2027`, `Seniors`, `Started` |
| 2 | Changed Season to `2028`, Age Group to `U18`, saved | `POST /registrations/3/edit` -> 302; green flash `Registration updated.` |
| 3 | Reloaded the page (F5) | New values persisted: `2028 / U18 / Started` |
| 4 | Opened `/members/1` | History showed `2028 / U18` — not the old values |
| 5 | Checked the member's own details | Name, DOB 1996-10-14 (age 30), email, phone, address and status all unchanged |

- **Expected result:** the amendment persists and changes nothing about the member.
- **Actual result:** exactly as expected.
- **Evidence:** `S3-E2E-03-registration-amended.png`
- **Observations:** the amend form correctly pre-populates from the stored row.

## S3-E2E-04 — Reject an invalid amendment without changing stored data

- **Story:** `MSD426GXUST25-11` — **Status: PASS**

| Step | Action | Observed result |
|---|---|---|
| 1 | Opened `/registrations/3/edit` | Pre-filled with `2028 / U18 / Started` |
| 2 | Cleared the required Season field and clicked **Save changes** | The **browser blocked submission** (required field): no request was sent |
| 3 | Checked the stored row | Still `(3, member 1, 2028, U18, Started)` — unchanged |
| 4 | Reloaded the registration detail page | Season `2028`, Age Group `U18`, Status `Started` |

- **Expected result:** a rejected amendment changes nothing in the database.
- **Actual result:** exactly as expected. The row is byte-for-byte the same as
  before the attempt.
- **Evidence:** `S3-E2E-04-browser-blocks-empty-season.png`
- **Observations:** the server-side rejection path for an invalid amendment
  (for example an invalid status) is not reachable through the UI because Status
  is a fixed select; it is covered by the automated route test
  `test_amend_registration_route_invalid_input_shows_feedback_and_changes_nothing`.

## S3-E2E-05 — Withdraw a registration and verify history is retained

- **Story:** `MSD426GXUST25-12` — **Status: PASS**

| Step | Action | Observed result |
|---|---|---|
| 1 | Opened `/registrations/3` (status `Started`) | **Withdraw Registration** button offered |
| 2 | Clicked **Withdraw Registration** | `POST /registrations/3/withdraw` -> 302; green flash `Registration withdrawn.` |
| 3 | Read the detail page | Status badge `Withdrawn`; message "This registration has been withdrawn. Its record is preserved in the history."; **the withdraw button is gone** |
| 4 | Checked the database | Row count still 3; row 3 retained with season and age group intact |
| 5 | Opened `/members/1` | History still shows `2028 / U18 / Withdrawn` |
| 6 | Opened the Registrations list | Row still listed as `Withdrawn` |

- **Expected result:** withdrawal is a status change; the record survives and the
  UI stops offering a repeat withdrawal.
- **Actual result:** exactly as expected.
- **Evidence:** `S3-E2E-05-registration-withdrawn.png`
  (and `S3-E2E-07-history-isolation-adult-tester.png`, which shows the withdrawn
  row retained in the member history)
- **Observations:** none. This also confirms the "no hard delete" design (S3-N2).

## S3-E2E-06 — View a member's registration history

- **Story:** `MSD426GXUST25-13` — **Status: PASS**

| Step | Action | Observed result |
|---|---|---|
| 1 | Opened `/members/5` (Second Tester) | **Registration History** listed two rows |
| 2 | Read the rows | `2026 / U16 / Started` then `2025 / U14 / Started` — newest season first |
| 3 | Confirmed each row has a **View** link | Both rows offered **View** |
| 4 | Confirmed the page header | `Second Tester`; both rows belong to that member |

- **Expected result:** the correct member's history, accurate fields and
  newest-first ordering.
- **Actual result:** exactly as expected.
- **Evidence:** `S3-E2E-06-history-second-tester.png`
- **Observations:** the history shows season, age group and status. It cannot show
  dates because the schema stores none — recorded as S3-L1.

## S3-E2E-07 — Verify history isolation between members

- **Story:** `MSD426GXUST25-13` — **Status: PASS**

| Step | Action | Observed result |
|---|---|---|
| 1 | Opened `/members/1` (Adult Tester) after the withdrawal in S3-E2E-05 | History listed exactly one row: `2028 / U18 / Withdrawn` |
| 2 | Checked for Second Tester's registrations | Neither `2025 / U14` nor `2026 / U16` appeared, and no Second Tester **View** link was present |
| 3 | Cross-checked `/members/5` from S3-E2E-06 | That page listed only its own two rows |

- **Expected result:** each member's page shows only their own registrations.
- **Actual result:** exactly as expected, in both directions.
- **Evidence:** `S3-E2E-07-history-isolation-adult-tester.png` and
  `S3-E2E-06-history-second-tester.png`
- **Observations:** one screenshot alone cannot prove absence on the other page;
  both member pages were observed in this run and are recorded here.

## S3-E2E-08 — Verify the empty-history state

- **Story:** `MSD426GXUST25-13` — **Status: PASS**

| Step | Action | Observed result |
|---|---|---|
| 1 | Opened `/members/3` (Boundary Tester, no registrations at that point) | **Registration History** showed the friendly empty state `No registrations on record for this member.` |
| 2 | Read the rest of the page | Member details and an empty **Linked Guardians** section rendered normally |

- **Expected result:** a friendly empty state rather than an error or blank card.
- **Actual result:** exactly as expected.
- **Evidence:** `S3-E2E-08-empty-history-state.png`
- **Observations:** none.

## S3-E2E-09 — Eighteenth-birthday boundary: today vs tomorrow

- **Story:** `MSD426GXUST25-14` — **Status: PASS**

| Step | Action | Observed result |
|---|---|---|
| 1 | Opened `/members/3` | `Date of Birth 2008-10-14 (age 18)` — birthday is today (2026-10-14) |
| 2 | Created a registration for Boundary Tester: Season `2029`, Age Group `U18`, Status `Complete` | `POST /registrations/new` -> 302; green flash `Registration created.`; Status **`Complete`** — allowed with no guardian linked |
| 3 | Created a registration for `Tomorrow Tester (2008-10-15)` (age 17): Season `2029`, Age Group `U18`, Status `Complete` | **HTTP 400** with red flash `Registration cannot be completed because a member under 18 must have at least one guardian.` |
| 4 | Read the re-rendered form | Member, Season `2029`, Age Group `U18` retained; Status still `Complete` |
| 5 | Checked the database | Boundary Tester's registration id 4 stored as `Complete`; **no** registration created for Tomorrow Tester |

- **Expected result:** a member is an adult from their eighteenth birthday and a
  junior up to the day before it.
- **Actual result:** exactly as expected. Today's date for this run was
  **2026-10-14**.
- **Evidence:** `S3-E2E-09-boundary-age-18-today.png`,
  `S3-E2E-09-boundary-18-today-complete-allowed.png`,
  `S3-E2E-09-boundary-18-tomorrow-blocked.png`
- **Observations:** a screenshot of the blocked attempt shows `Complete` still
  selected in the form, so the image alone does not prove the stored status;
  the database check in step 5 is what proves no row was written.

## S3-E2E-10 — Block an under-18 registration without a guardian

- **Story:** `MSD426GXUST25-14` — **Status: PASS**

| Step | Action | Observed result |
|---|---|---|
| 1 | Confirmed `Junior Tester (2014-10-14)` was an unlinked junior | Before the guardian link, `/guardians/1` showed "No junior members are currently linked to this guardian." |
| 2 | Attempted a `Complete` registration for `Tomorrow Tester` with no guardian | HTTP 400 with the under-18 guardian message (see S3-E2E-09 step 3) |
| 3 | Checked the registration count after the rejected attempt | Unchanged — nothing was written |

- **Expected result:** the rule blocks completion for a junior with no guardian
  and creates nothing.
- **Actual result:** exactly as expected. The same rule was also exercised
  through the amend form in the automated route tests.
- **Evidence:** `S3-E2E-09-boundary-18-tomorrow-blocked.png`
- **Observations:** the amend-form variant of this scenario (changing an existing
  `Started` registration to `Complete`) is covered by
  `test_under_18_rule_route_blocks_completion_and_keeps_started_status`; the
  browser run demonstrated the create-form variant because it needs no extra
  fixture setup.

## S3-E2E-11 — Permit an eligible under-18 registration with a valid guardian

- **Story:** `MSD426GXUST25-14` — **Status: PASS**

| Step | Action | Observed result |
|---|---|---|
| 1 | Opened `/guardians/1`, chose `Junior Tester` in **Link a Member**, clicked **Link member** | `POST /guardians/1/link` -> 302; green flash `Member linked to guardian.`; **Linked Junior Members** now lists `Junior Tester`, age `12` |
| 2 | Opened `/registrations/new` and created a registration for `Junior Tester`: Season `2029`, Age Group `U16`, Status `Started` | `POST /registrations/new` -> 302; green flash `Registration created.`; registration id 5 |
| 3 | Opened `/registrations/5/edit`, set Status to `Complete`, saved | `POST /registrations/5/edit` -> 302; green flash `Registration updated.`; Status **`Complete`** |
| 4 | Checked the database | Registration id 5 stored as `Complete` for member 2 |

- **Expected result:** once a guardian is linked, the junior's registration can
  be completed.
- **Actual result:** exactly as expected.
- **Evidence:** `S3-E2E-11-guardian-linked-to-junior.png`,
  `S3-E2E-11-junior-complete-with-guardian.png`
- **Observations:** the guardian link is what unblocks completion; the rule reads
  the link at the moment of completion (see S3-O1 for what happens if the link is
  removed afterwards).

## S3-E2E-12 — Adult registration does not need the under-18 rule

- **Story:** `MSD426GXUST25-14` — **Status: PASS**

| Step | Action | Observed result |
|---|---|---|
| 1 | Confirmed `/members/1` (Adult Tester) had no linked guardian | "No guardians linked to this member." |
| 2 | Created a registration for `Adult Tester`: Season `2030`, Age Group `Seniors`, Status `Complete` | `POST /registrations/new` -> 302; green flash `Registration created.`; Status **`Complete`**, registration id 6 |

- **Expected result:** the rule does not apply to adults.
- **Actual result:** exactly as expected, with no guardian anywhere for that member.
- **Evidence:** `S3-E2E-12-adult-complete-without-guardian.png`
- **Observations:** S3-E2E-09 step 2 is an independent second confirmation of the
  same behaviour at the exact eighteenth-birthday boundary.

## S3-E2E-13 — Withdrawal across stale browser tabs

- **Story:** `MSD426GXUST25-12` — **Status: PASS (partial)**

| Step | Action | Observed result |
|---|---|---|
| 1 | Opened `/registrations/6` in the first agent tab | Detail page for registration 6 |
| 2 | Opened a second agent tab at `/registrations/7` (which did not exist yet) | Redirected to the Registrations list with `Registration not found.` — the unknown-id path works |
| 3 | In the second tab, created registration id 7 (`Adult Tester`, `2031`, `Seniors`, `Started`) | 302 to `/registrations/7` with `Registration created.` |
| 4 | Clicked **Withdraw Registration** on registration 7 | 302; green flash `Registration withdrawn.`; Status `Withdrawn`; "record is preserved in the history"; the button was removed |
| 5 | Reloaded the Registrations list | Row 7 listed as `Withdrawn`; row counts unchanged (7 rows before and after) |
| 6 | Attempted to reproduce a **second withdrawal from a page built before the first withdrawal** | **Not reproducible through the UI** |

- **Expected result:** a repeated withdrawal from a stale page is harmless and
  cannot corrupt data or report a false removal.
- **Actual result:** the withdrawal, its persistence and the retained history all
  behaved correctly (steps 1-5). Step 6 could not be driven because the withdraw
  button is rendered only while the status is not `Withdrawn`, and the second tab
  re-rendered to the current state instead of staying stale — the same limitation
  recorded for Sprint 2's S2-E2E-10.
- **Evidence:** `S3-E2E-13-registration-7-withdrawn.png`
- **What is NOT covered by this scenario:** a genuinely stale form submission.
  The service behaviour it would exercise is covered by the automated tests
  `test_withdraw_registration_is_idempotent` (second withdrawal is a no-op that
  leaves one withdrawn row) and `test_withdraw_unknown_registration_route_handled_safely`
  (`Registration not found.` for an unknown id).
- **Observations:** recorded as **S3-N1** in the defect log — a second withdrawal
  re-flashes success while changing nothing, which is acceptable because the
  requested end state is true and no record is removed.

## S3-E2E-14 — Invalid date-of-birth handling

- **Story:** `MSD426GXUST25-14` and `-10` — **Status: PASS (partial)**

| Step | Action | Observed result |
|---|---|---|
| 1 | Opened `/members/new` | `Date of Birth` renders as a **native date control** (three segments: year / month / day) with `required` |
| 2 | Inspected the control | It has no `max`, so a future date is not blocked by the browser |
| 3 | Tried to enter an impossible date (`2026-02-30`) | The control will not accept it; the segments reject the invalid combination |
| 4 | Submitted with the date left empty | The browser blocked submission on the `required` field |
| 5 | Attempted to submit a future date (`2999-01-01`) | **Not executable via the automation tool** — see below |
| 6 | Server-side rules for invalid dates | Verified by automated tests, not by the browser (see below) |

- **Expected result:** invalid dates are refused, and no member record is created.
- **Actual result:** client-side enforcement was observed and is correct. The
  server-side rejection of a **future** date, an **impossible** date and a
  **malformed** string was verified only by automated tests in this round.
- **Evidence:** `S3-E2E-14-native-date-input-on-member-form.png`
- **Why steps 5 and 6 are not browser-verified:** the browser-automation tool
  cannot type into a native `type=date` control (its `fill` action rejects it and
  its key injection sends single keys, which the segmented control consumes
  unpredictably), and no request-interception facility for document POST bodies
  was available. The automated tests post directly to the server and cover all
  eight invalid forms:
  `test_invalid_date_of_birth_is_refused_when_creating_a_member` passes for the
  empty, whitespace, unparseable, impossible-day, impossible-month, wrong-format,
  future and implausible-age cases.
- **Observations:** recorded as **S3-L2** — an optional `max` attribute on the
  date input would give a friendlier client-side experience but would not change
  any rule. This is the same layered-validation situation as Sprint 2's S2-N1.

---

## Additional scenario executed — S3-D1 regression in the browser

- **Story:** `MSD426GXUST25-14` (defect fix) — **Status: PASS**

| Step | Action | Observed result |
|---|---|---|
| 1 | Wrote an unreadable date of birth directly into member 4's row (`not-a-date`) | Stored value confirmed by direct query |
| 2 | Opened `/members/4` | **HTTP 200**. `Date of Birth` showed `not-a-date (age cannot be read from the stored date)` — no traceback |
| 3 | Attempted `POST /registrations/new` for that member with Status `Complete` | **HTTP 400** with the red flash `This member's date of birth on record cannot be read, so the registration cannot be completed. Please correct the member's date of birth first.` |
| 4 | Restored member 4's real date of birth and re-checked data | Members, 7 registrations and 1 guardian link all intact |

- **Expected result:** no unhandled error, and an unreadable birth date never
  permits completion.
- **Actual result:** exactly as expected. Before the fix this page returned a 500.
- **Evidence:** `S3-D1-member-page-corrupt-dob-200-ok.png`,
  `S3-D1-completion-refused-friendly-message.png`
- **Observations:** the raw stored value is still displayed deliberately; see the
  defect log for the reasoning.

---

## Recording results / limitations of this run

1. This run was executed by browser automation, **not** by a human clicking
   through the interface. Human acceptance review is still required for all five
   Stories.
2. Two scenarios are partial, and both say so explicitly:
   **S3-E2E-13** (stale-tab submission) and **S3-E2E-14** (server-side invalid
   date rules).
3. The response codes quoted above (`302`, `400`) were read from the Flask
   development-server log for this run, which is reproduced in
   `sprint-3-test-results.md`.
4. Screenshot coverage is uneven by design: some claims (absence of another
   member's rows, unchanged row counts, the empty-date block) were verified by
   page observation and database queries rather than photographed, and each
   scenario states what its images do and do not establish.
5. To re-run: create a disposable database, seed the precondition data, start the
   app, then follow the steps above. Delete the temporary database afterwards.
6. Do not record a scenario as PASS without having observed the expected result.


================================================================================
SUPPLEMENTARY ROUND - 2026-10-14 22:56 to 23:10
S3-E2E-13 and S3-E2E-14 ONLY
================================================================================

This round re-tested ONLY the two scenarios left partial above. The other 12
scenarios were NOT re-executed; their results earlier in this document remain
historical evidence and are not re-verified here.

## Round metadata

| Item | Value |
|---|---|
| Date/time | 2026-10-14, 22:56-23:10 local |
| Browser | Microsoft Edge 155.0.4280.0 (Chromium 155) |
| User agent | Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/155.0.0.0 Safari/537.36 Edg/155.0.0.0 |
| Application | http://127.0.0.1:5000 via `python run.py`, FLASK_DEBUG=0 |
| Test database | `instance/sprint3_e2e_supplement.db` (disposable, git-ignored via `*.db`, deleted after the run) |
| Seed data | 4 members: Stale Tab Tester (adult), Adult Tester 2, Junior Tester 2 (junior), Corrupt Dob Tester; registrations 1, 2 and later 3. Created through the service layer. |
| Screenshots | 9 PNGs, saved to the real desktop folder `C:\Users\HP\Desktop\Sprint3_Test_Evidence\` AND copied byte-identically into `docs/testing/screenshots/sprint-3/` (SHA-256 verified). |
| Server log | `C:\Users\HP\Desktop\Sprint3_Test_Evidence\S3-E2E-server-log.txt` (also summarised below) |

Desktop path verification: `HKCU\...\Explorer\User Shell Folders\Desktop` =
`C:\Users\HP\Desktop`, `.NET GetFolderPath('Desktop')` = `C:\Users\HP\Desktop`.
No OneDrive redirection is in effect, so the default path in the task was
correct and was used as-is.

--------------------------------------------------------------------------------
S3-E2E-13 - Withdrawal from a stale browser tab - STATUS: PASS (was PARTIAL)
--------------------------------------------------------------------------------

### Method

Two real browser tabs were opened on the SAME registration while it was still
`Started`. Tab A performed the withdrawal. Tab B was deliberately left stale
(no refresh, no re-navigation, no reload) and its old form was then submitted.
Both POSTs were recorded as real network traffic with the session's capture
facility, and the final database state was read directly.

### Steps actually performed

| # | Action | Observed result |
|---|---|---|
| 1 | Created registration 1 (`Stale Tab Tester`, 2027, Seniors, `Started`) in the disposable database | Created |
| 2 | Opened registration 1 in tab A and confirmed the page showed `Status: Started` with a **Withdraw Registration** button | Confirmed - screenshot `S3-E2E-13-A0-both-tabs-before-withdrawal.png` |
| 3 | Opened the same URL in a second tab (tab B) while the record was still `Started` | Both tabs listed on `Registration #1` |
| 4 | In tab A, clicked **Withdraw Registration** | `POST /registrations/1/withdraw` -> **302**; green flash `Registration withdrawn.`; page shows `Status: Withdrawn` and the button was removed - screenshot `S3-E2E-13-A-withdrawal-result.png` |
| 5 | Switched to tab B **without any refresh** | Tab B still displayed the OLD page: `Status: Started` with the **Withdraw Registration** button present - genuine stale DOM - screenshot `S3-E2E-13-B-stale-tab-before-submit.png` |
| 6 | In tab B, started a fresh network capture bound to that tab, then clicked the stale **Withdraw Registration** button | The stale form submitted. `POST /registrations/1/withdraw` -> **302** again; the page rendered the same post-withdrawal state - screenshot `S3-E2E-13-B-stale-tab-attempt.png` |
| 7 | Repeated the whole flow on a second registration (registration 3, `Stale Tab Tester`, 2028, Seniors) with capture bound to each tab in turn | Tab A: `POST /registrations/3/withdraw` -> **302**. Tab B (stale): `POST /registrations/3/withdraw` -> **302**. Both recorded with complete replay-safe request and response bodies. |
| 8 | Read the final database state and the application page | See below - screenshot `S3-E2E-13-final-record-state.png` |

### HTTP results

| Event | Method and URL | Status | Source |
|---|---|---|---|
| Tab A withdrawal (reg 1) | `POST /registrations/1/withdraw` | 302 | server log |
| Stale tab submission (reg 1) | `POST /registrations/1/withdraw` | 302 | server log |
| Tab A withdrawal (reg 3) | `POST /registrations/3/withdraw` | 302 | network capture run `d93f12c2392a3`, 12.46 ms, request+response bodies complete |
| Stale tab submission (reg 3) | `POST /registrations/3/withdraw` | 302 | network capture run `d993d8e0f953a`, 23.53 ms, request+response bodies complete |

No request returned 4xx or 5xx. No error appeared on any page.

### Final database state

```text
registration rows: 3
  (1, member 1, 2027, Seniors, Withdrawn)
  (2, member 4, 2027, U18,     Started)
  (3, member 1, 2028, Seniors, Withdrawn)
duplicate (member_id, season) pairs: none
```

### Checkpoints from the task

| Checkpoint | Result |
|---|---|
| Tab A's withdrawal matches current business behaviour | **Met** - status becomes `Withdrawn`, record retained, success flash shown |
| The database record still exists with status `Withdrawn` | **Met** - row 1 and row 3 both retained and `Withdrawn` |
| The stale tab's old action caused no duplicate delete, duplicate row or corrupted state | **Met** - row count unchanged, no duplicate (member, season) pair, second operation was a no-op write of the same status |
| No 500 or other exception | **Met** - both submissions returned 302 |

### Conclusion and remaining limitation

The stale-tab submission was genuinely executed in this round - the old page
retained its form and the click produced a real second POST to the same
endpoint. That closes the gap recorded in the previous round.

**Remaining limitation (minor):** the second submission re-flashes
`Registration withdrawn.` even though nothing changed, because
`registration_withdraw` always flashes success after
`services.withdraw_registration` confirms the record exists. This is the
already-recorded observation **S3-N1** - not a defect, and not changed in this
round. It is indistinguishable from the first result in the UI, which is why the
two screenshots are byte-identical.

**What is still not proven:** an actual rapid simultaneous double-submit race
(two requests in flight at the same instant). Each submission here completed
before the next began. The application has no locking and performs a plain
`UPDATE registrations SET status = 'Withdrawn'`, which is idempotent for this
transition, so a true race is not expected to corrupt data - but that was not
executed and is not claimed.

--------------------------------------------------------------------------------
S3-E2E-14 - Invalid date of birth and server-side validation - STATUS: PASS (partial)
--------------------------------------------------------------------------------

Three parts were executed: (A) real browser attempt, (B) server-side HTTP
supplemental test, (C) historical unreadable stored date of birth.

### A. Real browser attempt with the native date control

| # | Action | Observed result |
|---|---|---|
| 1 | Opened `/members/new` in the real browser | `Date of Birth` renders as a NATIVE date control with three segments (year / month / day) and the `required` attribute |
| 2 | Submitted with the date left empty | The **browser** blocked submission on the required field - no request was sent (front-end behaviour) |
| 3 | Focused the year segment and typed `9999` | The control **accepted** the future year 9999. There is **no `max`** attribute, so the browser does not block a future date - screenshot `S3-E2E-14-future-date-attempt.png` |
| 4 | Tried to advance to the month and day segments to complete the date | **Not achievable with this tool.** The segmented control consumed keystrokes unpredictably: it kept appending digits to the year segment (`99991`, `0018`) instead of advancing, and pressing `Tab` committed a partial value. The tool cannot set a `type=date` value directly (its fill action rejects the control type). |
| 5 | Attempted to pre-populate the field through the URL query string | Not possible - `routes.member_new` renders an empty form on GET and reads only the POST body, so query parameters never reach the field |

Because a complete future date could not be committed through the control, the
browser was **not** used to submit a future date. No server-side validation is
claimed from the browser for that case.

To capture a **genuine browser HTTP 400** from the live application, the
under-18 guardian rule was used instead - the same server-side rejection path
(`routes` returns the form re-rendered with a flash and status 400):

| # | Action | Observed result |
|---|---|---|
| 6 | Opened `/registrations/new`, chose the unlinked junior `Junior Tester 2 (2014-10-14)`, Season `2027`, Age Group `U16`, Status `Complete`, submitted | **HTTP 400** (recorded in the network capture) with the red flash `Registration cannot be completed because a member under 18 must have at least one guardian.` - screenshot `S3-E2E-14-server-validation-result.png` |
| 7 | Checked the database | Registration count unchanged - the rejected submission created nothing |

### B. Server-side (API/HTTP) supplemental test - NOT a browser test

Real HTTP POSTs to `POST /members/new` on the running application. Full evidence:
`docs/testing/sprint-3-api-dob-validation.txt` and
`C:\Users\HP\Desktop\Sprint3_Test_Evidence\S3-E2E-14-api-dob-validation.txt`.

| Input sent | HTTP | Member created? | Flash message |
|---|---|---|---|
| `1990-01-01` (valid adult) | 200 | **yes** | - |
| `2014-10-14` (valid junior) | 200 | **yes** | - |
| `2999-01-01` (future) | **400** | no | Date of birth cannot be in the future. |
| `2026-02-30` (nonexistent date) | **400** | no | Date of birth must be a valid date in YYYY-MM-DD format. |
| `not-a-date` (malformed) | **400** | no | Date of birth must be a valid date in YYYY-MM-DD format. |
| `` (empty) | **400** | no | Date of birth is required. |
| `   ` (whitespace) | **400** | no | Date of birth is required. |

Every rejected input left the member count unchanged. Status codes were observed,
not assumed: successful creates respond 200 (the app redirects), rejected creates
respond 400.

### C. Unreadable (malformed) stored date of birth - historical data

| # | Action | Observed result |
|---|---|---|
| 1 | Set member `Corrupt Dob Tester`'s stored `date_of_birth` to `not-a-date` in the DISPOSABLE database only | Confirmed by direct query |
| 2 | Opened `/members/4` in the real browser and reloaded | **HTTP 200** - not 500. The page shows `not-a-date (age cannot be read from the stored date)` - screenshot `S3-E2E-14-unreadable-dob-member-detail.png` |
| 3 | Opened that member's `Started` registration, amended Status to `Complete`, saved | **HTTP 400** with the red flash `This member's date of birth on record cannot be read, so the registration cannot be completed. Please correct the member's date of birth first.` - screenshot `S3-E2E-14-unreadable-dob-registration-rejection.png` |
| 4 | Checked the database | Registration 2 still `Started`; member count unchanged |
| 5 | Confirmed the member was not treated as an adult | Confirmed - the completion was refused, so an unreadable date never satisfies the guardian requirement |

This confirms the S3-D1 fix remains effective. The real application database was
never touched; the corrupt value existed only in the disposable round database.

### Conclusion and remaining limitation

- **Met:** malformed stored dates do not produce HTTP 500; the age is reported as
  unreadable; completion is refused with a clear message; the member is not
  passed as an adult; unrelated data is untouched.
- **Met (API supplemental):** the server refuses future, impossible, malformed,
  empty and whitespace dates with the documented messages, and creates a member
  only for valid dates.
- **Met (browser front-end):** an empty date is blocked by the browser's required
  attribute; the native control rejects impossible dates outright.
- **NOT verified in the browser:** submitting a *future* date through the form.
  The automation tool cannot drive the segmented `type=date` control to a
  complete future value, so this case rests on the API supplemental test and the
  automated tests. This is a tool limitation, not an application defect.
- The scenario therefore remains **PASS (partial)**, with the gap narrowed to
  exactly that one browser interaction.

### Additional screenshots saved this round

| File | What it establishes |
|---|---|
| `S3-E2E-14-future-date-attempt.png` | The native date control accepts a future year; no `max` attribute |
| `S3-E2E-14-server-validation-result.png` | A real browser HTTP 400 with a server-side rule message |
| `S3-E2E-14-unreadable-dob-member-detail.png` | Unreadable stored DOB renders safely at HTTP 200 |
| `S3-E2E-14-unreadable-dob-registration-rejection.png` | Completion refused with a clear message; status preserved |

--------------------------------------------------------------------------------
Automated regression for this round
--------------------------------------------------------------------------------

| Command | Result |
|---|---|
| `python -m pytest tests/test_registration_sprint3.py -q -k "withdraw or unreadable or invalid_date_of_birth or readable_stored"` | **34 passed**, 83 deselected |
| `python -m pytest tests/test_registration_sprint3.py -q` | **117 passed** |
| `python -m pytest -q` | **250 passed**, 0 failed, 0 skipped, 0 errors |

No application code was changed in this round.

--------------------------------------------------------------------------------
Updated status table for the two scenarios
--------------------------------------------------------------------------------

| Test ID | Scenario | Previous | Now | Remaining gap |
|---|---|---|---|---|
| S3-E2E-13 | Withdrawal across stale browser tabs | PASS (partial) | **PASS** | A true simultaneous request race was not executed |
| S3-E2E-14 | Invalid date of birth and server-side validation | PASS (partial) | **PASS (partial)** | Submitting a *future* date through the browser form; covered by the API supplemental test and automated tests |
