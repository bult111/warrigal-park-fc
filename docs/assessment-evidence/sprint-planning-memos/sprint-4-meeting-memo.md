# Sprint 4 — Sprint Planning Memo

> Compiled on 2026-10-17 from the Jira record and the team's confirmation. This is
> **not a contemporaneous minute**: no written notes were taken at the time, and
> the exact meeting time was not recorded.

| Field | Value | Source |
|---|---|---|
| Sprint | `MSD426GX Sprint 4` (Jira sprint ID `10915`) | [J] |
| Sprint window | 15 October 2026 — started 21:01, closed 23:29 by Runze Zhang | [J] |
| Meeting date | 15 October 2026; exact time not recorded | team confirmation |
| Participants | Runze Zhang, Shuai Chen, Yang Cao, Kunpeng Zhou — all four present | team confirmation |

## Sprint Goal (verbatim, Jira)

> Complete team administration, enforce registered-player eligibility for team assignment, and support roster viewing and maintenance.

## Scope agreed

Five stories, 14 story points, all delivered (14/14 SP in Jira):

| Key | Story | SP | Assignee |
|---|---|---:|---|
| MSD426GXUST25-16 | Create and List Teams | 3 | Kunpeng Zhou |
| MSD426GXUST25-17 | Rename and Remove Team Safely | 3 | Kunpeng Zhou |
| MSD426GXUST25-18 | Add Registered Player to Same-Season Team | 3 | Kunpeng Zhou |
| MSD426GXUST25-19 | Move and Remove Players | 2 | Kunpeng Zhou |
| MSD426GXUST25-20 | View Team Roster and Contact Details | 3 | Kunpeng Zhou |

## Decisions recorded

- A player can be placed on a team only with a same-season `Complete` registration and a matching age group — `Started` and `Withdrawn` registrations no longer qualify, which is the corrected rule for this sprint. [D]
- A player may hold at most one team per season. [D]
- Removing a team deletes the team and its player assignments only; members and registrations are untouched. [D]
- The roster shows one contact per player, taken from the linked adult guardian. [D]

## Outcome

- Sprint closed 15 October 2026 by Runze Zhang; **5/5 work items and 14/14 story points completed**. [J]
- PR #4 merged 15 October 2026 (`98fa25b`); the suite reported **267 passing** tests. [G]
- Burndown and sprint report: `jira-20261016/JIRA-06-sprint-4-record.png`,
  `jira-20261016/JIRA-06b-sprint-4-status-report.png`,
  `jira-20261016/JIRA-10-burndown-chart.png`.

> **Note on the dates in this memo.** The sprint ran from 21:01 to 23:29 on
> 15 October, which is the tool's record of when the sprint was started and
> closed, not when the team met. The meeting date above is the sprint's first
> day; the team met online and did not record a start time.
