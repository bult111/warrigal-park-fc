# Sprint 4 — Acceptance Results

Sprint 4 (Team and Roster Management) was verified in two ways: the automated
pytest suite and a browser acceptance run. Both were executed in the DSH
environment; neither constitutes human acceptance sign-off.

- Developed on branch `feature/sprint-4-team-roster-leo0318-cpu`; merged into
  `main` via PR #4 (merge commit `98fa25b0dda738659a752dfc27189ebce286b685`).
- Date: 2026-10-15.

## Automated tests

Command (from the project root, using the project virtual environment):

```text
.\.venv\Scripts\python.exe -m pytest -q
```

Result:

- 267 passed
- 0 failed
- 0 errors
- 0 skipped

## Browser acceptance

A browser acceptance run was executed against a real local instance of the
application, driven by the DSH environment using Microsoft Edge and the Chrome
DevTools Protocol (no Playwright, no Selenium, no third-party packages). An
isolated project copy and an isolated SQLite database were used; the original
database was not touched.

Result: **21 / 21 scenarios PASS, 0 FAIL**.

The detailed per-scenario record (expected result, actual page content, and
status) is in
`../../sprint4-acceptance-evidence-20261015/acceptance-report.md`.

Screenshots captured from the running browser via `Page.captureScreenshot`:

| Story | Scenario | Screenshot |
|---|---|---|
| 16 | Teams list (seeded teams) | `screenshots/sprint-4/16-teams-initial.png` |
| 16 | Create team | `screenshots/sprint-4/16-team-created.png` |
| 16 | New team in list | `screenshots/sprint-4/16-teams-after-create.png` |
| 16 | Invalid create rejected | `screenshots/sprint-4/16-team-create-invalid.png` |
| 17 | Rename team | `screenshots/sprint-4/17-team-renamed.png` |
| 17 | Delete team | `screenshots/sprint-4/17-team-deleted.png` |
| 18 | Complete player added | `screenshots/sprint-4/18-complete-added.png` |
| 18 | Started player rejected | `screenshots/sprint-4/18-started-rejected.png` |
| 19 | Move player | `screenshots/sprint-4/19-player-moved.png` |
| 19 | Remove player | `screenshots/sprint-4/19-player-removed.png` |
| 20 | Roster contact details | `screenshots/sprint-4/20-roster-contact.png` |
| — | CDP connection test | `screenshots/sprint-4/cdp-connect-test.png` |

Scenarios verified by page-content assertions without a dedicated screenshot
(Withdrawn / wrong-season / duplicate rejection, cross-season move rejection,
remove-no-op error, guardian-link preservation, empty roster, nonexistent-team
roster) are covered in the detailed report referenced above.

## Important caveats

- The browser run is **automation**, executed by the DSH environment over
  Edge + CDP. It is **not** human manual testing and is **not** course-official
  sign-off.
- The automated pytest result and the browser acceptance are separate kinds of
  evidence; a passing pytest suite is not itself browser acceptance.
- The pytest and browser results above were recorded on the Sprint 4 branch
  before the merge; they were not re-run as part of this documentation update.
- No GitHub Actions workflow run or commit status was verified, so CI is not
  claimed as passing.
