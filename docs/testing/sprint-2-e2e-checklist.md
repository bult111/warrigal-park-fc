# Sprint 2 — End-to-End Checklist

- **Sprint:** Sprint 2 — Epic: Member and Guardian Management
- **Method:** browser verification against a temporary SQLite database
- **Document status:** **executed** by browser automation on the local
  application on 2026-10-14. The scenarios were run twice that day — once to
  verify behaviour and once to capture the screenshot set — and the results
  below are the actual observations, not expectations.

> **Important — how to read the status column.**
> The run below was performed with a browser-automation tool driving a real
> Chromium browser against the real Flask application, not by a human clicking
> through the UI. It is stronger evidence than an intended-outcome description,
> but it is **not** a human acceptance sign-off. A human should still confirm
> these workflows before the Stories are marked Done in Jira.
>
> Screenshots **are** saved to disk for this run. They live in an evidence
> folder **outside the repository** (so nothing new has to be committed):
>
> `<LOCAL_EVIDENCE_DIR>\Sprint2_Browser_Evidence\`
>
> That folder contains **17 PNG files** (plus a `README.txt` index). Two of the
> 17 are byte-identical duplicates of each other
> (`S2-E2E-04_duplicates_list.png` and `S2-E2E-04_duplicates_isolated.png`,
> same SHA-256), so there are **16 distinct images**. All 17 were inspected
> visually during the documentation review; the content of each image matched
> the scenario it is mapped to.
>
> If the team wants the images inside the repository, ask first and then copy
> only the selected files under `docs/testing/screenshots/sprint-2/` — do not
> commit all of them.
>
> **Screenshot coverage is not equal for every scenario.** Some claims in the
> step tables were verified by page observation during the run and are *not*
> visible in any screenshot (for example whether the member also appeared in
> the Members list, or whether the stored registration status stayed
> `Started`). Each scenario below states what its screenshot actually
> establishes.
>
> Scenario **S2-E2E-10** is recorded as **Blocked**: its first half (unlinking a
> linked member) passed, but the second half — the no-op unlink message — could
> not be reproduced through a second click in one browser session (see that
> scenario for details), and no screenshot exists for the no-op message itself.

## Preconditions used for this run

- Temporary database `sprint2_manual_check.db` in `instance/`, created with
  `flask --app run.py init-db` and deleted after the run. The real application
  database was never used.
- Application served on `http://127.0.0.1:5001` via `python run.py`.
- Only the fictional data in the scenarios below was entered.
- The temporary `.db` file was deleted at the end of the run.

## Summary

| Test ID | Story | Scenario | Status |
|---------|-------|----------|--------|
| S2-E2E-01 | MSD426GXUST25-2 | Create and view a member | **Passed** |
| S2-E2E-02 | MSD426GXUST25-3 | Search and update a member | **Passed** |
| S2-E2E-03 | MSD426GXUST25-4 | Deactivate a member and confirm status | **Passed** |
| S2-E2E-04 | MSD426GXUST25-5 | Two members with the same name stay separate | **Passed** |
| S2-E2E-05 | MSD426GXUST25-6 | Create, search and update a guardian | **Passed** |
| S2-E2E-06 | MSD426GXUST25-7 | Link a guardian to a junior member | **Passed** |
| S2-E2E-07 | MSD426GXUST25-8 | Update guardian contact and verify the views | **Passed** |
| S2-E2E-08 | MSD426GXUST25-2 / -3 | Invalid input is rejected with feedback | **Passed** (with a finding) |
| S2-E2E-09 | MSD426GXUST25-7 | Under-18 rule blocks completion without a guardian | **Passed** |
| S2-E2E-10 | MSD426GXUST25-7 (fix) | Unlink a guardian that is not linked | **Blocked** (first half passed) |

Recorded data used: members `Ava Testplayer` (id 1), `Bob Secondplayer` (id 2),
`Casey Samename` (ids 3 and 4), `Junior Testchild` (id 5), `Solo Testjunior`
(id 6); guardian `Nina Testguardian` (id 1); registration #1.

---

## S2-E2E-01 — Create and view a member

- **Story:** MSD426GXUST25-2
- **Status:** **Passed**

| Step | Action | Observed result |
|---|---|---|
| 1–2 | Opened **Members** → **+ New Member** | Members page empty ("No members found."); New Member form rendered |
| 3 | Entered `Ava Testplayer`, DOB `2012-04-18`, `ava.testplayer@example.com`, `0400 100 200`, `1 Test Street` | All fields accepted |
| 4 | Clicked **Create member** | Redirected to `/members/1`; green flash `Member 'Ava Testplayer' created.` |

- **Expected result:** redirect to the new detail page with success feedback,
  all fields shown, `Status: Active`, empty Linked Guardians and empty
  Registration History.
- **Actual result:** exactly as expected. Detail page showed
  `2012-04-18 (age 14)`, all contact fields, `Status: Active`, "No guardians
  linked to this member." and "No registrations on record for this member."
  The member also appeared on the Members list.
- **Evidence:** `S2-E2E-01_member_created.png` — shows the green flash
  `Member 'Ava Testplayer' created.` and the full detail page with
  `2012-04-18 (age 14)`, all contact fields, `Status: Active` and the empty
  Linked Guardians section. This image establishes the create-and-view outcome.
  *Not* visible in the image: the member's presence on the Members list
  (observed during the run, not photographed).

## S2-E2E-02 — Search and update a member

- **Story:** MSD426GXUST25-3
- **Status:** **Passed**

| Step | Action | Observed result |
|---|---|---|
| 0 | Created `Bob Secondplayer` (DOB `2011-03-22`) as a control | Created successfully |
| 1 | Searched `ava` | Only `Ava Testplayer` returned; `Bob Secondplayer` absent |
| 2–3 | Searched `TESTPLAYER` (upper case) | Only `Ava Testplayer` returned — search is case-insensitive |
| 4–5 | Opened Ava → **Edit**, changed email to `ava.updated@example.com`, phone to `0400 999 888`, address to `25 Updated Road` | Edit form was pre-populated with the existing values |
| 6 | Clicked **Save changes** | Flash `Member 'Ava Testplayer' updated.`; detail page showed all three new values |
| 7 | Reopened from the Members list | Updated values persisted in the list: `ava.updated@example.com`, `0400 999 888` |

- **Expected result:** partial and case-insensitive search; updates persist;
  the second member is unaffected.
- **Actual result:** exactly as expected. `Bob Secondplayer` still showed
  `bob.secondplayer@example.com` and `2011-03-22` throughout.
- **Evidence:** `S2-E2E-02_search_testplayer.png` — the search box contains
  `TESTPLAYER` and only the `Ava Testplayer` row is returned, which establishes
  the case-insensitive search. `S2-E2E-02_member_updated.png` — the green flash
  `Member 'Ava Testplayer' updated.` with `ava.updated@example.com`,
  `0400 999 888` and `25 Updated Road`, which establishes the update.
  *Not* visible in either image: that `Bob Secondplayer` was unaffected
  (observed during the run).

## S2-E2E-03 — Deactivate a member and confirm the status

- **Story:** MSD426GXUST25-4
- **Status:** **Passed**

| Step | Action | Observed result |
|---|---|---|
| 1–2 | Opened Ava → **Set Inactive** | Flash `Member 'Ava Testplayer' is now inactive.`; `Status: Inactive`; button changed to **Set Active** |
| 3 | Reloaded the page (F5) | Still `Status: Inactive` — persisted |
| 4 | Checked the Members list | Ava `Inactive`; Bob still `Active` — only the target changed |
| 5 | Opened Ava → **Set Active** | Flash `Member 'Ava Testplayer' is now active.`; `Status: Active` |

- **Expected result:** soft status change that persists, affects only the target
  member, preserves other data, and is reversible; the member is never deleted.
- **Actual result:** exactly as expected. Contact details, Linked Guardians and
  Registration History were still present while inactive.
- **Evidence:** `S2-E2E-03_member_inactive.png` — the `Status` field shows the
  grey **Inactive** badge and the action button has changed to **Set Active**,
  which establishes that deactivation took effect and persisted after reload.
  `S2-E2E-03_inactive_evidence_alt.png` — a second capture of the same
  inactive state showing the updated contact details.
  *Not* visible in either image: the Members list showing only this member as
  `Inactive`, and the successful reactivation step (both observed during the
  run).

## S2-E2E-04 — Two members with the same name stay separate

- **Story:** MSD426GXUST25-5
- **Status:** **Passed**

| Step | Action | Observed result |
|---|---|---|
| 1 | Created `Casey Samename`, DOB `2010-01-05`, `casey.one@example.com` | Created as `/members/3` |
| 2 | Created `Casey Samename`, DOB `2011-06-15`, `casey.two@example.com` | Created as `/members/4` — **no duplicate-name error** |
| 3 | Searched `Casey Samename` | Two rows, both named `Casey Samename`, distinguished by DOB and email |
| 4 | Opened each record | Two distinct URLs (`/members/3`, `/members/4`) with different data |
| 5 | Edited the **first**, email → `casey.changed@example.com` | Flash `Member 'Casey Samename' updated.` |
| 6 | Reopened the **second** record | Still `casey.two@example.com`, DOB `2011-06-15` — unchanged |

- **Expected result:** duplicates allowed, independently identified, both listed,
  and updates isolated to one record.
- **Actual result:** exactly as expected.
- **Evidence:** `S2-E2E-04_duplicates_list.png` — two rows both named
  `Casey Samename`, distinguished by `2010-01-05 / casey.one@example.com` and
  `2011-06-15 / casey.two@example.com`, which establishes that duplicate names
  are stored as separate records. `S2-E2E-04_duplicate_edited_list.png` — the
  first row now reads `casey.changed@example.com` while the second still reads
  `casey.two@example.com`, which establishes that the update touched only one
  record. `S2-E2E-04_duplicates_isolated.png` is a byte-identical duplicate of
  `S2-E2E-04_duplicates_list.png` and adds no new evidence.

## S2-E2E-05 — Create, search and update a guardian

- **Story:** MSD426GXUST25-6
- **Status:** **Passed**

| Step | Action | Observed result |
|---|---|---|
| 1–3 | Created `Nina Testguardian`, `nina@example.com`, `0400 555 111`, `5 Guard Lane` | Flash `Guardian 'Nina Testguardian' created.`; detail page showed all details |
| 4 | Searched `nina` | Only `Nina Testguardian` returned |
| 5–6 | **Edit**, changed phone to `0400 777 222` and email to `nina.updated@example.com` | Edit form pre-populated with existing values |
| 7 | Clicked **Save changes** | Flash `Guardian 'Nina Testguardian' updated.`; new phone and email shown |

- **Expected result:** creation, search and update all behave correctly.
- **Actual result:** exactly as expected.
- **Evidence:** `S2-E2E-05_guardian_created.png` — the green flash
  `Guardian 'Nina Testguardian' created.` with the name, `nina@example.com`,
  `0400 555 111`, `5 Guard Lane` and an empty Linked Junior Members section.
  This image establishes only the **create** step. The guardian **search** and
  **update** steps for this scenario were verified by page observation during
  the run and are not covered by any screenshot.

## S2-E2E-06 — Link a guardian to a junior member

- **Story:** MSD426GXUST25-7
- **Status:** **Passed**

| Step | Action | Observed result |
|---|---|---|
| 0 | Created `Junior Testchild`, DOB `2014-09-01` (age 12) | Created as `/members/5` |
| 1–2 | Opened Nina → selected `Junior Testchild` → **Link member** | Flash `Member linked to guardian.` |
| 3 | Checked **Linked Junior Members** | `Junior Testchild`, age `12`, listed |
| 4 | Opened the junior's member page | `Nina Testguardian` listed under **Linked Guardians** — visible from both sides |
| 5 | Clicked **Unlink** | Flash `Member unlinked from guardian.`; the junior disappeared from the list; both records still existed afterwards |

- **Expected result:** the link persists, is visible in both views, and unlinking
  removes only the relationship.
- **Actual result:** exactly as expected.
- **Evidence:** `S2-E2E-06_guardian_linked_junior.png` — the green flash
  `Member linked to guardian.` with `Junior Testchild`, age `12`, listed under
  Linked Junior Members. `S2-E2E-06_two_juniors_linked.png` — the same guardian
  listing two linked juniors (`Junior Testchild` and `Solo Testjunior`).
  `S2-E2E-06_unlink_success.png` — the green flash
  `Member unlinked from guardian.` with `Junior Testchild` no longer in the
  list, which establishes that unlinking removed only the relationship.
  *Not* visible in any of these images: the member-side Linked Guardians view
  (observed during the run) and that the member records still existed after
  unlink.

## S2-E2E-07 — Update guardian contact and verify the views

- **Story:** MSD426GXUST25-8
- **Status:** **Passed**

| Step | Action | Observed result |
|---|---|---|
| 0 | Re-linked `Junior Testchild` to Nina (required after the E2E-06 unlink) | Link restored |
| 1–3 | Edited Nina: email → `nina.changed@example.com`, phone → `0400 321 654` | Flash `Guardian 'Nina Testguardian' updated.` |
| 4 | Opened `Junior Testchild`'s member page | **Linked Guardians** showed `nina.changed@example.com` and `0400 321 654`; the previous email no longer appeared anywhere on the page; the link was still present |
| 5 | Opened the **Guardians** list and the guardian detail page | Both showed the new email and phone |

- **Expected result:** updated contact details appear wherever the guardian is
  referenced, with no stale value, and relationships stay intact.
- **Actual result:** exactly as expected. This confirms the design decision that
  contact details are read from the single `guardians` row via a join.
- **Evidence:** `S2-E2E-07_member_shows_new_contact.png` — `Junior Testchild`'s
  member page with the Linked Guardians table showing `Nina Testguardian`,
  `nina.changed@example.com` and `0400 321 654`. This single image establishes
  the whole outcome: the member page renders the guardian's **current** contact
  details and no stale address, and the relationship is still present.
  *Not* visible in this image: the Guardians list view and the guardian detail
  page (both observed during the run).

## S2-E2E-08 — Invalid input is rejected with feedback

- **Story:** MSD426GXUST25-2 and MSD426GXUST25-3
- **Status:** **Passed** — with a finding worth recording

| Step | Action | Observed result |
|---|---|---|
| 1 | Submitted **New Member** with the Name blank | The browser blocked submission and showed its own field message (`请填写此字段。`). No record created. |
| 2 | Entered `Bad Date` with a future date `2999-01-01` and submitted | Server responded **HTTP 400** with flash `Date of birth cannot be in the future.` The typed name **and** the entered date remained in the form. No record created. |
| 3 | Entered `Bad Email` with `nope` in the Email field and submitted | The browser blocked submission on the email field. No record created. |
| 4 | Checked the Members list after each attempt | Still only the six legitimate members — no partial records |

### Finding recorded (not a defect)

The application enforces validation in two layers, and the **browser's own HTML5
validation fires first** for two of the cases in the checklist:

- The `required` attribute on Name and Date of Birth blocks an empty submit.
- `type="email"` blocks a malformed address such as `nope`.

Because the browser stops those two submissions, the server-side messages
(`Name is required.`, `Email address is not valid.`) are not reached through the
normal form in a modern browser. They remain correct defence in depth and are
still proven by the automated tests, which post directly to the server.

Values that pass the browser's checks but are still invalid — such as a future
date — **do** reach the server and produce the expected 400 response and
friendly flash. This is the behaviour the checklist step 2 was really testing,
and it passed.

- **Evidence:** `S2-E2E-08_future_date_rejected.png` — the **red** flash
  `Date of birth cannot be in the future.` while the New Member form still holds
  `Future Person` and `2999/01/01`, which establishes server-side rejection with
  the typed values retained. (No screenshot exists for the empty-name and
  malformed-email cases, because the browser blocked those submissions before
  they reached the server — see the finding above.)

## S2-E2E-09 — Under-18 rule still blocks completion without a guardian

- **Story:** MSD426GXUST25-7 (Sprint 1 rule regression check)
- **Status:** **Passed**

| Step | Action | Observed result |
|---|---|---|
| 1 | Created `Solo Testjunior`, DOB `2014-09-01` (age 12); confirmed no guardian linked | "No guardians linked to this member." |
| 2 | Created registration #1 for Solo, season `2027`, age group `U16`, status `Started` | Flash `Registration created.` |
| 3 | Opened **Amend**, set Status to `Complete`, clicked **Save changes** | Flash `Registration cannot be completed because a member under 18 must have at least one guardian.` |
| 4 | Reloaded the registration | Status still **`Started`** — the record was not modified |
| 5 | Linked a guardian (`Nina Testguardian`) to Solo | Flash `Member linked to guardian.` |
| 6 | Set Status to `Complete` again and saved | Flash `Registration updated.`; Status became **`Complete`** |

- **Expected result:** the rule blocks completion without a guardian and allows
  it once one is linked; the rule must not be weakened.
- **Actual result:** exactly as expected. The rule is intact.
- **Evidence:** `S2-E2E-09_under18_blocked.png` — the **red** flash
  `Registration cannot be completed because a member under 18 must have at least
  one guardian.` on the Amend Registration form for `Solo Testjunior`, season
  `2027`, age group `U16`. This establishes that the rule blocked the attempt.
  **Caveat:** the image shows `Complete` still selected in the form, so the
  image alone does *not* prove the stored status stayed `Started` — that was
  confirmed during the run by reopening the registration, and is asserted by the
  automated tests.
  `S2-E2E-09_registration_complete.png` — the green flash
  `Registration updated.` with `Status: Complete` after a guardian was linked,
  which establishes that the rule allows completion once the requirement is met.

## S2-E2E-10 — Unlink a guardian that is not linked

- **Story:** MSD426GXUST25-7 (Sprint 2 defect fix S2-D1 / Sprint 1 D3)
- **Status:** **Blocked** — first half passed, second half not executable
  through the UI in this run

| Step | Action | Observed result |
|---|---|---|
| 1 | Opened the guardian's page and confirmed `Junior Testchild` was linked | Listed under Linked Junior Members |
| 2 | Clicked **Unlink** | Flash `Member unlinked from guardian.`; the junior was removed from the list |
| 3 | Attempted to trigger the same unlink again through a second, deliberately stale browser tab | **Not reliably reproducible** — see below |

- **Evidence:** the first half is supported by
  `S2-E2E-06_unlink_success.png` (green flash `Member unlinked from guardian.`
  with the junior removed from the list). **No screenshot exists for the no-op
  message**, because step 3 was never executed. This scenario therefore cannot
  be reported as `Passed` on the strength of the screenshots.

### Why this scenario is Blocked

The intended reproduction is to submit the unlink for a relationship that no
longer exists. Because the Unlink button is only rendered for members who *are*
linked, this requires a page whose form was built while the link existed but is
submitted after the link was removed.

In this run, extra tabs created for that purpose did not stay stale: selecting
them caused the browser to re-render them, and they showed the already-unlinked
page. The stale-form submission therefore could not be driven reliably through
the user interface, and no attempt was made to bypass the UI.

The behaviour itself is nevertheless evidenced by three other things:

1. `unlink_guardian_member` returns whether a row was removed and
   `guardian_unlink` chooses the message from that value
   (`app/routes.py` line 218).
2. The new automated tests cover both outcomes directly:
   `test_unlink_route_reports_no_op_instead_of_success` (no-op → error message)
   and `test_unlink_route_reports_success_when_link_removed` (real removal →
   success message).
3. The negative-control run proved that reverting the handler makes
   `test_unlink_route_reports_no_op_instead_of_success` fail, so the test really
   does exercise the corrected branch.

### What a human should do to close this out

Re-run just this scenario with two browser tabs:

1. Open the guardian's detail page in **tab A** and in **tab B**, so both show
   the member as linked.
2. In **tab A**, click **Unlink** and confirm the success message.
3. Switch to **tab B** **without reloading it**, and click **Unlink** for the
   same member.
4. Expected: tab B must show
   `That member was not linked to this guardian.` and must **not** claim
   `Member unlinked from guardian.`

Record the result and a screenshot for tab B, then change this status to
`Passed` or `Fail`.

---

## Recording results

This document now reflects one executed run. If a human re-runs the scenarios:

- Update the `Observed result` cells with what you see.
- Add your screenshots to the evidence folder
  (`<LOCAL_EVIDENCE_DIR>\Sprint2_Browser_Evidence\`) or another non-repository
  location, and record the file names in the `Evidence` lines.
- Mark S2-E2E-10 fully `Passed` only after the two-tab check above succeeds.
- If a scenario fails, record the exact steps, expected and actual behaviour and
  add it to `sprint-2-defect-log.md`.

Do not record a scenario as `Passed` without having observed the expected result.
