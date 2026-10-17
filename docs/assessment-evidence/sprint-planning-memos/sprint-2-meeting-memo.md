# Sprint 2 — Sprint Planning Memo

> Compiled on 2026-10-17 from the Jira record and the team's confirmation. This is
> **not a contemporaneous minute**: no written notes were taken at the time, and
> the exact meeting time was not recorded.

| Field | Value | Source |
|---|---|---|
| Sprint | `MSD426GX Sprint 2` (Jira sprint ID `10912`) | [J] |
| Sprint window | 14–15 October 2026 — created 14 Oct, closed 15 Oct by Shuai Chen | [J] |
| Meeting date | 14 October 2026 (first day of the sprint); exact time not recorded | team confirmation |
| Participants | Runze Zhang, Shuai Chen, Yang Cao, Kunpeng Zhou — all four present | team confirmation |

## Sprint Goal (verbatim, Jira)

> Complete member and guardian management workflows, including member records, guardian relationships, and contact information updates.

## Scope agreed

Seven stories, 18 story points, all delivered (18/18 SP in Jira):

| Key | Story | SP | Assignee |
|---|---|---:|---|
| MSD426GXUST25-2 | Create Member Record | 3 | Shuai Chen |
| MSD426GXUST25-3 | Search and Update Member | 3 | Shuai Chen |
| MSD426GXUST25-4 | Deactivation of Members | 2 | Shuai Chen |
| MSD426GXUST25-5 | Support Duplicate Member Names | 2 | Shuai Chen |
| MSD426GXUST25-6 | Create, Search and Update Guardian | 3 | Shuai Chen |
| MSD426GXUST25-7 | Link Guardians to Junior Members | 3 | Shuai Chen |
| MSD426GXUST25-8 | Reflect Guardian Contact Updates | 2 | Shuai Chen |

**Recorded honestly:** Jira shows the committed total at sprint start as **0 SP**,
because the seven stories were only pulled into the sprint during execution.
This is visible in the sprint record and is not corrected after the fact.

## Decisions recorded

- Duplicate member names are allowed; a member's `id`, never the name, is the unique identifier, and search returns every match. [D]
- A guardian must record a `date_of_birth` that verifies them as an adult (18 or over); a guardian with a missing or unreadable date of birth is not verified. [D]
- Deactivating a member is a status change only — the member is never deleted. [D]
- Guardian–junior links are many-to-many, so one contact update reaches every linked child. [D]

## Outcome

- Sprint closed 15 October 2026 by Shuai Chen; **7/7 work items and 18/18 story points completed**. [J]
- PR #2 merged 14 October 2026 (`86ebc70`); the suite reported **133 passing** tests. [G]
- Burndown and sprint report: `jira-20261016/JIRA-04-sprint-2-record.png` and `jira-20261016/JIRA-04b-sprint-2-status-report.png`.

> **Note on the dates in this memo.** Jira's `startDate` for this sprint is earlier
> than its own `createdDate`, which means the start date was filled in after the
> fact rather than being the real start moment. The meeting date above is the
> sprint's first day; the team met online and did not record a start time.
