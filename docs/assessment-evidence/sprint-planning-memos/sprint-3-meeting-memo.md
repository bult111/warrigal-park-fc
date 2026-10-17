# Sprint 3 — Sprint Planning Memo

> Compiled on 2026-10-17 from the Jira record and the team's confirmation. This is
> **not a contemporaneous minute**: no written notes were taken at the time, and
> the exact meeting time was not recorded.

| Field | Value | Source |
|---|---|---|
| Sprint | `MSD426GX Sprint 3` (Jira sprint ID `10914`) | [J] |
| Sprint window | 15 October 2026 — started 00:08, closed 02:28 by Shuai Chen | [J] |
| Meeting date | 15 October 2026; exact time not recorded | team confirmation |
| Participants | Runze Zhang, Shuai Chen, Yang Cao, Kunpeng Zhou — all four present | team confirmation |

## Sprint Goal (verbatim, Jira)

> Complete and validate the registration and eligibility management workflows, including creating, amending and withdrawing registrations, viewing member registration history, and enforcing the guardian requirement for members under 18. Ensure that registration data is handled consistently, eligibility rules are correctly applied, and all implemented workflows are supported by automated and manual testing.

## Scope agreed

Five stories, 15 story points, all delivered (15/15 SP in Jira):

| Key | Story | SP | Assignee |
|---|---|---:|---|
| MSD426GXUST25-10 | Create Registration | 3 | Yang Cao |
| MSD426GXUST25-11 | Amend Registration | 2 | Yang Cao |
| MSD426GXUST25-12 | Withdraw Registration | 2 | Yang Cao |
| MSD426GXUST25-13 | View Member Registration History | 3 | Yang Cao |
| MSD426GXUST25-14 | Enforce Under-18 Guardian Rule | 5 | Yang Cao |

## Decisions recorded

- The under-18 guardian rule is evaluated at the moment a registration is set to `Complete`; an adult (18 or over) needs no guardian. [D]
- The age group is always computed from the member's date of birth and the season and is never taken from the submitted form. [D]
- A registration with an unreadable stored date of birth is refused with a clear message rather than being treated as adult — the S3-D1 fix. [D]
- Withdrawing a registration keeps the row; history is retained across seasons. [D]
- Registration dates are not held on a registration record; this remains an open product decision. [D]

## Outcome

- Sprint closed 15 October 2026 by Shuai Chen; **5/5 work items and 15/15 story points completed**. [J]
- PR #3 merged 14 October 2026 (`d6ee6a0`); the suite reported **250 passing** tests. [G]
- Burndown and sprint report: `jira-20261016/JIRA-05-sprint-3-record.png` and `jira-20261016/JIRA-05b-sprint-3-status-report.png`.

> **Note on the dates in this memo.** The sprint ran from 00:08 to 02:28 on
> 15 October, which is the tool's record of when the sprint was started and
> closed, not when the team met. The meeting date above is the sprint's first
> day; the team met online and did not record a start time.
