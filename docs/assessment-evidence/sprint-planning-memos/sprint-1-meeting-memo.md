# Sprint 1 — Sprint Planning Memo

> Compiled on 2026-10-17 from the Jira record and the team's confirmation. This is
> **not a contemporaneous minute**: no written notes were taken at the time, and
> the exact meeting time was not recorded. Everything below is either a field
> read from Jira `[J]`, a fact from the repository `[D]`/`[G]`, or the team's
> confirmation that all four members took part.

| Field | Value | Source |
|---|---|---|
| Sprint | `MSD426GX Sprint 1` (Jira sprint ID `10635`) | [J] |
| Sprint window | 13–14 October 2026 — started 13 Oct, closed 14 Oct by Runze Zhang | [J] |
| Meeting date | 13 October 2026 (first day of the sprint); exact time not recorded | team confirmation |
| Participants | Runze Zhang, Shuai Chen, Yang Cao, Kunpeng Zhou — all four present | team confirmation |

## Sprint Goal (verbatim, Jira)

> Validate the existing Warrigal Park FC application through automated regression testing and end-to-end workflow verification, review local configuration, record and resolve genuine defects, and prepare accurate release and handover documentation.

## Scope agreed

Five stories, 15 story points, all delivered (15/15 SP in Jira):

| Key | Story | SP | Assignee |
|---|---|---:|---|
| MSD426GXUST25-22 | Maintain Automated Regression Test Suite | 5 | Runze Zhang |
| MSD426GXUST25-23 | Verify Core End-to-End Workflows | 3 | Runze Zhang |
| MSD426GXUST25-24 | Maintain Reproducible Local Configuration | 2 | Runze Zhang |
| MSD426GXUST25-25 | Prepare Release and Handover Documentation | 2 | Runze Zhang |
| MSD426GXUST25-26 | Record and Resolve Defects | 3 | Runze Zhang |

## Decisions recorded

- No application code change was planned for this sprint; the scope was verification, defect resolution and documentation. [D]
- The Definition of Done required the regression suite to pass and a handover note to be written before the sprint closed. [D]
- Defects found during verification were written to `docs/testing/sprint-1-defect-log.md` and carried forward rather than fixed silently. [D]
- Environment checks (interpreter, dependency consistency, database initialisation) were run before any test execution, and the results recorded in `docs/testing/sprint-1-test-results.md`. [D]

## Outcome

- Sprint closed 14 October 2026 by Runze Zhang; **5/5 work items and 15/15 story points completed**. [J]
- PR #1 merged 14 October 2026 (`ee2cf04`); the suite reported **79 passing** tests at the close of the sprint. [G]
- Burndown and sprint report: `jira-20261016/JIRA-03-sprint-1-record.png` and `jira-20261016/JIRA-03b-sprint-1-status-report.png`.

> **Note on the dates in this memo.** The sprint start and close timestamps are
> when the sprint was started and closed in Jira, not when the team sat down.
> The meeting date given above is the sprint's first day; the team met online and
> did not record a start time.
