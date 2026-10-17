# JIRA Screenshot Index — ISYS3001 A3

**Purpose:** index of real Jira UI screenshots captured for the ISYS3001 A3
assessment evidence set.

- **Project / board:** `MSD426GXUST25` / `MSD426GXUST25 board` (board id `2017`)
- **Board URL:** https://scu-it.atlassian.net/jira/software/c/projects/MSD426GXUST25/boards/2017/
- **Capture date:** 2026-10-16
- **Capture method:** live Jira Cloud session in a local browser, read-only.
  No issue, sprint, status, assignee, priority or configuration was created,
  edited, started, completed or deleted at any point.
- **Screenshot directory:** `docs/assessment-evidence/jira-20261016/` (this folder)
- **Relationship to the A3 brief:** the brief requires Jira to hold the product
  backlog (user stories, acceptance criteria, story points), the SCRUM process
  (sprint planning, sprint backlogs, test plan, release management) and the
  project-performance evidence used by the project report. The mapping column
  below ties each image to those requirements.

---

## 1. Screenshot table

| File name | What the screenshot shows | Jira page / URL | Related issue / sprint (as actually visible) | A3 use | Evidence status | Limitations |
|---|---|---|---|---|---|---|
| `JIRA-02-backlog-sprints.png` | Backlog tab: Epic panel listing `Member and Guardian Management`, `Registration and Eligibility`, `Team and Roster Management`; sprint group **MSD426GX Sprint 5** (0 个工作项, not started, "冲刺开始" button present); **Backlog** section (0 个工作项). | `https://scu-it.atlassian.net/jira/software/c/projects/MSD426GXUST25/boards/2017/backlog` | Sprint `MSD426GX Sprint 5` (0 items); 3 epics named above. | Product backlog / sprint breakdown | Obtained, but content-incomplete | Backlog and Sprint 5 both contain **0 work items**. Closed Sprints 1–4 do not appear in this view, so this page cannot evidence the sprint backlogs; use the Sprint Reports instead. |
| `JIRA-03-sprint-1-record.png` | Sprint Report for **MSD426GX Sprint 1**: name, "关闭冲刺，由 Runze Zhang 结束", period 13/十月/26 10:49 下午 – 14/十月/26 7:30 下午, the sprint goal text, and the burndown chart on story points. | `.../boards/2017/reports/sprint-retrospective?sprint=10635` | Sprint 1; closed by Runze Zhang. | SCRUM process — sprint planning / sprint record | Obtained | Only the upper part of the report fits the 1280×720 viewport; the issue-level detail is in `JIRA-03b`. |
| `JIRA-03b-sprint-1-status-report.png` | Sprint 1 **状态报告 / 已完成的事务**: issues `MSD426GXUST25-22` … `-26` with type 故事, priority, status 已完成 and Story Points; header total **Story Points (15)**. | `.../reports/sprint-retrospective?sprint=10635` | Sprint 1; issues 22, 23, 24, 25, 26. | SCRUM process — sprint backlog + completion; story points | Obtained | Shows the completed issues only. The report renders no "issues not completed" block for this sprint. |
| `JIRA-04-sprint-2-record.png` | Sprint Report for **MSD426GX Sprint 2**: closed by Shuai Chen, period 14/十月/26 12:00 上午 – 15/十月/26 12:01 上午, sprint goal, burndown chart. | `.../reports/sprint-retrospective?sprint=10912` | Sprint 2; closed by Shuai Chen. | SCRUM process — sprint planning / sprint record | Obtained | Upper part of the report only; details in `JIRA-04b`. |
| `JIRA-04b-sprint-2-status-report.png` | Sprint 2 **状态报告 / 已完成的事务**: issues `MSD426GXUST25-2` … `-8` with type, priority, status 已完成 and Story Points; header total **Story Points (18)**. | `.../reports/sprint-retrospective?sprint=10912` | Sprint 2; issues 2–8. | SCRUM process — sprint backlog + completion; story points | Obtained | Completed issues only. |
| `JIRA-05-sprint-3-record.png` | Sprint Report for **MSD426GX Sprint 3**: closed by Shuai Chen, period 15/十月/26 12:08 上午 – 15/十月/26 2:28 上午, sprint goal, burndown chart. | `.../reports/sprint-retrospective?sprint=10914` | Sprint 3; closed by Shuai Chen. | SCRUM process — sprint planning / sprint record | Obtained | Upper part of the report only; details in `JIRA-05b`. |
| `JIRA-05b-sprint-3-status-report.png` | Sprint 3 **状态报告 / 已完成的事务**: issues `MSD426GXUST25-10` … `-14` with type, priority, status 已完成 and Story Points; header total **Story Points (15)**. | `.../reports/sprint-retrospective?sprint=10914` | Sprint 3; issues 10–14. | SCRUM process — sprint backlog + completion; story points | Obtained | Completed issues only; the last row is partly below the viewport edge. |
| `JIRA-06-sprint-4-record.png` | Sprint Report for **MSD426GX Sprint 4**: closed by Runze Zhang, period 15/十月/26 9:01 下午 – 15/十月/26 11:29 下午, sprint goal, burndown chart. | `.../reports/sprint-retrospective?sprint=10915` | Sprint 4; closed by Runze Zhang. | SCRUM process — sprint planning / sprint record | Obtained | Upper part of the report only; details in `JIRA-06b`. |
| `JIRA-06b-sprint-4-status-report.png` | Sprint 4 **状态报告 / 已完成的事务**: issues `MSD426GXUST25-16` … `-20` with type, priority, status 已完成 and Story Points; header total **Story Points (14)**. | `.../reports/sprint-retrospective?sprint=10915` | Sprint 4; issues 16–20. | SCRUM process — sprint backlog + completion; story points | Obtained | Completed issues only; the bottom row is partly cut by the viewport. |
| `JIRA-07-issue-2-create-member-record.png` | Issue **MSD426GXUST25-2 "Create Member Record"**: breadcrumb `MSD426GXUST25 / MSD426GXUST25-1 / MSD426GXUST25-2`, status 已完成, the user-story description ("As a club administrator, I want to…") and four numbered **Acceptance Criteria**. | `https://scu-it.atlassian.net/browse/MSD426GXUST25-2` | Issue `MSD426GXUST25-2`, parent Epic `MSD426GXUST25-1`. | Product backlog — user story + acceptance criteria | Obtained | The `Sprint` field value is not visible in this frame; see `JIRA-07b`. |
| `JIRA-07b-issue-2-fields-story-points.png` | Same issue, **详细信息** panel: 经办人 Shuai Chen, 报告人 Runze Zhang, labels/dates empty, **Story Points 3**. | `https://scu-it.atlassian.net/browse/MSD426GXUST25-2` | Issue `MSD426GXUST25-2`. | Product backlog — story point estimation | Obtained, but content-incomplete | The **Sprint** field row sits on the last pixel row of the viewport; its value is not readable here. Sprint membership for this issue is authoritative from `JIRA-04b`, where Jira lists it under Sprint 2. |
| `JIRA-07c-issue-2-priority-parent-team.png` | Same issue, details panel scrolled: **Team** `Group 25`, **优先级** `High (migrated)`, **父项** `MSD426GXUST25-1 Member and Guardian Management`. | `https://scu-it.atlassian.net/browse/MSD426GXUST25-2` | Issue `MSD426GXUST25-2`. | Product backlog — priority / epic structure | Obtained | The 添加冲刺 (Sprint) control renders above this frame; its value could not be read at this viewport size. |
| `JIRA-08-issue-23-verify-e2e-workflows.png` | Issue **MSD426GXUST25-23 "Verify Core End-to-End Workflows"**: breadcrumb to `MSD426GXUST25-21`, status 已完成, testing user story, five bullet **Acceptance Criteria**, 经办人/报告人 Runze Zhang, **Story Points 3**. | `https://scu-it.atlassian.net/browse/MSD426GXUST25-23` | Issue `MSD426GXUST25-23`, parent Epic `MSD426GXUST25-21`. | Product backlog — testing story; SCRUM process — test evidence | Obtained | The `Sprint` field value is below the viewport edge. |
| `JIRA-08b-issue-23-test-results-comment.png` | Comment on the same issue by Runze Zhang ("2天前"): *"Sprint 1 Completion Record — End-to-End Workflow Verification"*, automated results *"19 workflow checks executed; 19 passed and 0 failed"*. | `https://scu-it.atlassian.net/browse/MSD426GXUST25-23` | Issue `MSD426GXUST25-23`; refers to Sprint 1. | SCRUM process — test plan & results | Obtained | This is a Jira comment, not a separate test-plan artefact. |
| `JIRA-08c-issue-23-evidence-links.png` | Continuation of the same comment: scope verified, *"Manual browser results: 5 out of 5 browser scenarios passed in Microsoft Edge"*, *"Six screenshots were reviewed and mapped to the relevant scenarios"*, and the **Evidence** links (End-to-End Workflow Checklist; Automated Regression Test Results; Sprint 1 Pull Request #1). | `https://scu-it.atlassian.net/browse/MSD426GXUST25-23` | Issue `MSD426GXUST25-23`. | SCRUM process — test results; link to Git repository | Obtained | The linked items are Jira/GitHub references rendered inside Jira; the targets themselves were not opened during this capture. |
| `JIRA-09-sprint-report-sprint-selector-all-sprints.png` | Sprint Report with the sprint selector expanded, listing **MSD426GX Sprint 4, Sprint 3, Sprint 2, Sprint 1**. | `.../reports/sprint-retrospective?sprint=10915` | Sprints 1–4 (all closed). | SCRUM process — proof that four sprints exist | Obtained | The dropdown omits the currently selected sprint, so the selected sprint is shown by the closed control above the list rather than inside the list. |
| `JIRA-10-burndown-chart.png` | **燃尽图** (Burndown Chart) report for `MSD426GX Sprint 4`, metric Story Points, with the sprint goal and the burndown/guideline lines. | `.../boards/2017/reports/burndown-chart?sprint=10915` | Sprint 4. | SCRUM process / project report — progress tracking | Obtained | Sprint 4 only; the other sprints' burndowns appear inside their Sprint Report pages (`JIRA-03`…`JIRA-06`). |
| `JIRA-11-velocity-chart.png` | **速度报告** (Velocity Chart): bars for `MSD426GX Sprint 1`–`Sprint 4` with 承诺 / 已完成 series and an average of **15.5** story points. | `.../boards/2017/reports/velocity` | Sprints 1–4. | Project report — team velocity / performance | Obtained | Only four sprints have data; Sprint 5 contributes nothing because it was never started. |
| `JIRA-12-all-work-items-jql-26.png` | JQL search `project = MSD426GXUST25 ORDER BY key ASC`, titled 所有工作, showing the first issues (`-1`…`-10`) with 经办人 and 报告人, and the total **"26 个，共 26 个"**. | `https://scu-it.atlassian.net/issues/?jql=project%20%3D%20MSD426GXUST25%20ORDER%20BY%20key%20ASC` | All 26 project work items. | Product backlog — backlog size and ownership | Obtained, but content-incomplete | The result grid scrolls internally and only about ten rows are visible in one frame; the full 26-row inventory (key, type, priority, summary) was read from the Reports page "Work item details" table and is transcribed in section 2 below. |
| `JIRA-13-reports-dashboard.png` | Board **报告** dashboard: 22 work items completed / 26 updated / 26 created in the last 7 days, plus Work items by status (Done 22, To Do 4), by type (Story 22, Epic 4) and by assignee (Shuai Chen 8, Yang Cao 6, Runze Zhang 6, Kunpeng Zhou 6). | `.../boards/2017/reports` | Sprints 1–4; 26 work items. | Project report — project performance | Obtained | This is Jira's built-in board report dashboard, not a sprint-scoped report. |
| `JIRA-14-available-reports-modal.png` | **更多报告** modal listing the available Agile reports: 燃耗图, 燃尽图, 冲刺报告, 速率表, 累积流程图, 版本报告, "Epic" 报告, 控制图, "Epic" 燃尽图, 发布燃尽图, plus DevOps and issue-analysis reports. | `.../boards/2017/reports` | n/a (report catalogue). | SCRUM process — evidence that reports exist | Obtained | This proves the reports are *available*; it is not itself progress evidence. Some listed reports (e.g. 版本报告, DevOps reports) were not opened. |
| `JIRA-15-list-view-epics-only.png` | Project **列表** (list) view showing only `MSD426GXUST25-1`, `-9`, `-15`, `-21` with their assignees and reporters. | `https://scu-it.atlassian.net/jira/software/c/projects/MSD426GXUST25/list` | The 4 Epics. | Product backlog (context only) | Obtained, but misleading in isolation | This view returned only the four Epics and must **not** be presented as the product backlog; the authoritative count is 26 work items (`JIRA-12`, `JIRA-13`). Included for completeness. |

---

## 2. Full work-item inventory actually present in Jira

Read from the Reports page "Work item details" table (26 rows, paginated 20 per
page). Types and priorities are as displayed by Jira.

| Key | Type | Priority | Summary |
|---|---|---|---|
| MSD426GXUST25-1 | Epic | Medium | Member and Guardian Management |
| MSD426GXUST25-2 | Story | High (migrated) | Create Member Record |
| MSD426GXUST25-3 | Story | High (migrated) | Search and Update Member |
| MSD426GXUST25-4 | Story | High (migrated) | Deactivation of Members |
| MSD426GXUST25-5 | Story | High (migrated) | Support Duplicate Member Names |
| MSD426GXUST25-6 | Story | High (migrated) | Create, Search and Update Guardian |
| MSD426GXUST25-7 | Story | Medium | Link Guardians to Junior Members |
| MSD426GXUST25-8 | Story | Medium | Reflect Guardian Contact Updates |
| MSD426GXUST25-9 | Epic | Medium | Registration and Eligibility |
| MSD426GXUST25-10 | Story | Medium | Create Registration |
| MSD426GXUST25-11 | Story | Medium | Amend Registration |
| MSD426GXUST25-12 | Story | Medium | Withdraw Registration |
| MSD426GXUST25-13 | Story | High (migrated) | View Member Registration History |
| MSD426GXUST25-14 | Story | High (migrated) | Enforce Under-18 Guardian Rule |
| MSD426GXUST25-15 | Epic | Medium | Team and Roster Management |
| MSD426GXUST25-16 | Story | High (migrated) | Create and List Teams |
| MSD426GXUST25-17 | Story | Medium | Rename and Remove Team Safely |
| MSD426GXUST25-18 | Story | High (migrated) | Add Registered Player to Same-Season Team |
| MSD426GXUST25-19 | Story | Medium | Move and Remove Players |
| MSD426GXUST25-20 | Story | High (migrated) | View Team Roster and Contact Details |
| MSD426GXUST25-21 | Epic | Medium | Quality Assurance and Release |
| MSD426GXUST25-22 | Story | High (migrated) | Maintain Automated Regression Test Suite |
| MSD426GXUST25-23 | Story | High (migrated) | Verify Core End-to-End Workflows |
| MSD426GXUST25-24 | Story | Medium | Maintain Reproducible Local Configuration |
| MSD426GXUST25-25 | Story | Medium | Prepare Release and Handover Documentation |
| MSD426GXUST25-26 | Story | Medium | Record and Resolve Defects |

**Total: 26 work items — 4 Epics + 22 Stories.** No Bug, Task or Sub-task type
was observed in the project.

Sprint membership as reported by Jira's own sprint reports:

| Sprint | Issues | Story Points | Closed by | Reported period |
|---|---|---|---|---|
| MSD426GX Sprint 1 | 22–26 | 15 | Runze Zhang | 13/10/2026 22:49 – 14/10/2026 19:30 |
| MSD426GX Sprint 2 | 2–8 | 18 | Shuai Chen | 14/10/2026 00:00 – 15/10/2026 00:01 |
| MSD426GX Sprint 3 | 10–14 | 15 | Shuai Chen | 15/10/2026 00:08 – 15/10/2026 02:28 |
| MSD426GX Sprint 4 | 16–20 | 14 | Runze Zhang | 15/10/2026 21:01 – 15/10/2026 23:29 |
| MSD426GX Sprint 5 | none | 0 | — (not started) | no dates set |

---

## 3. Evidence Gaps

Items that could **not** be evidenced from Jira in this session, or that need the
student's confirmation. No substitute or mock screenshot was created for any of
these.

1. **Sprint planning meeting memos / meeting minutes — not found in Jira.**
   The A3 brief lists "the sprint planning, meeting memos" as a deliverable.
   Nothing in the board, backlog, reports or the inspected issues contains a
   meeting record. Confluence is linked in the Jira sidebar but was **not**
   inspected during this capture — meeting notes may live there.

2. **No active sprint.** Sprint 5 exists but was never started and holds 0
   work items, and the Backlog also holds 0. The board therefore shows no
   cards, so no screenshot can show work flowing through board columns; the
   Sprint Reports (`JIRA-03` … `JIRA-06`) carry the process evidence instead.
   Confirm whether a board view with cards is expected, or whether Sprint
   Reports are sufficient.

3. **Sprint 5 is empty and undated.** Only Sprints 1–4 carry content, and all
   four were closed within roughly three days (13–15 October 2026). Confirm
   whether the Jira sprint record is complete, or whether a fifth sprint was
   planned and abandoned.

4. **Team roles and project-manager rotation are not evidenced in Jira.**
   The brief requires each member to take a turn as project manager, and the
   Project Charter template has a "Project roles and responsibilities" section.
   No role, ownership or rotation record was visible in the board, backlog,
   epics or the two issues inspected. This may exist elsewhere (Confluence, the
   Project Charter document) but is not Jira evidence.

5. **Jira users cannot be mapped to the Git repository contributors.**
   Jira shows four display names — Shuai Chen, Yang Cao, Runze Zhang, Kunpeng
   Zhou. None of these names appears anywhere in the repository docs, which
   reference only GitHub handles (`bult111`, `leo0318-cpu`, `sandip001159852`,
   `colacolaco`). The mapping is unverified and must be confirmed, especially
   because the Git history, not Jira, is the source for individual contribution.

6. **Team size discrepancy to confirm.** The A3 brief specifies a project team
   of 3 members; the Jira reports dashboard shows **4** distinct assignees
   (Shuai Chen 8 items, Yang Cao 6, Runze Zhang 6, Kunpeng Zhou 6). This is an
   observed fact only — the cause (a fourth member, a former member, or a
   lecturer/tutor account) is unknown and was not investigated.

7. **The `Sprint` field value could not be read on the issue detail pages** at
   the available 1280×720 viewport; the row sits below the fold. Sprint
   membership is instead evidenced by the Sprint Reports, which are Jira's
   authoritative source. If a per-issue Sprint field screenshot is required,
   the browser window needs to be taller.

8. **No standalone test-plan artefact in Jira.** Testing is represented by
   Stories (`-22`, `-23`, `-26`) and by a Jira comment recording results, not by
   a dedicated test-plan document. The repository's `docs/testing/` files are
   the test plan and results; Jira only references them.

9. **Release/version management is thin.** The Epic "Quality Assurance and
   Release" and issue `-25` exist, and priorities show "High (migrated)", but no
   Jira Releases/Versions or fixVersion values were observed on the two issues
   inspected (`修复版本: 无` on `-2`). The 版本报告 exists in the report catalogue
   but was not opened and may be empty.

10. **Original estimate / time tracking is empty.** Issue `-2` shows
    `原始预估: 添加预估值` and `时间跟踪: 无记录的时间`, so Jira holds no logged
    work time. Any time claims in the A3 report cannot be sourced from Jira.

11. **All 26 work items appear to have been created on 2026-10-13.** The
    reports dashboard states "26 created in the last 7 days" and the creation
    trend plots all 26 on 2026-10-13; issue `-2` shows "已创建 3天前". Priorities
    labelled "High (migrated)" also suggest the issues were imported rather than
    built up issue-by-issue. This is relevant because the brief instructs teams
    to start in Week 1, and the A3 due date is 12 October 2026. Confirm whether
    an extension applied and how the report should describe the timeline.

12. **Repository documents state that Jira was never available.** Several
    existing files assert the opposite of what is now true:

    - `docs/testing/sprint-2-test-plan.md` — "Authorised Jira acceptance
      criteria were not available".
    - `docs/testing/sprint-3-handover.md` — "No Jira issue, status, Story Point
      or Epic assignment was read or changed."
    - `docs/testing/sprint-3-test-plan.md` — "No Jira access was available or
      used."
    - `CHANGELOG.md` — "none should be marked Done in Jira on the strength of
      these".

    Those statements describe the position when they were written, but Jira now
    contains acceptance criteria for the same Stories. The A3 report should not
    repeat "no Jira access" as a current statement, and anything already written
    about "no Jira acceptance criteria" needs reconciling with `JIRA-07`/`JIRA-08`.

13. **Not inspected in this session:** Confluence pages, Jira project settings
    and permissions, board configuration/filter, the 版本报告 / 累积流程图 /
    DevOps reports, and the remaining 24 issue detail pages. Only `-2` and `-23`
    were opened in full.

---

## 4. Verification statement

Every image in this folder was captured from a live, authenticated Jira session
on 2026-10-16 and saved as PNG. No screenshot is hand-drawn, simulated or reconstructed, and no Jira data was created or modified to
produce them. Where a required field was empty, below the fold, or the
underlying artefact did not exist, that is recorded above rather than filled in.
