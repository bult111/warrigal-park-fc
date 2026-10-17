# Sprint 2 — Test Plan

- **Sprint:** Sprint 2
- **Epic:** Member and Guardian Management
- **Stories in scope:** `MSD426GXUST25-2` … `MSD426GXUST25-8` (7 Stories, 18 Story Points)
- **Document status:** prepared from the actual local repository at the start of
  Sprint 2 QA. It records only behaviour that was read in the source or
  reproduced by running the application.

## Sprint Goal

Complete and verify the member and guardian management workflows, including
member records, searching and updating, deactivation, duplicate member names,
guardian management, guardian linking, and consistency of guardian contact
information.

## Testing objectives

1. Establish a truthful baseline by running the existing suite **before** any
   change, and confirm whether the previously reported Sprint 1 result of
   79 passing tests still holds.
2. Verify each of the seven Sprint 2 Stories against real application
   behaviour rather than against assumptions.
3. Close genuine automated-coverage gaps for those Stories.
4. Record any defect found, with reproduction, and fix only defects that are
   in scope and unambiguous.
5. Keep every existing test intact; do not remove or weaken tests to obtain a
   passing result.
6. Separate automated verification from manual browser verification, and never
   report manual testing as done when it has not been performed.

## Confirmed baseline (measured, not assumed)

| Item | Value |
|------|-------|
| Command | `python -m pytest` |
| Collected | 79 |
| Passed | 79 |
| Failed / Skipped / Errors | 0 / 0 / 0 |
| Result | Matches the Sprint 1 reported figure of 79 |

The baseline was measured on the opened working copy before any file was
modified. Details are in `sprint-2-test-results.md`.

## How the test counts are stated

Three different numbers appear in the Sprint 2 documents. They measure
different things and must not be added together.

| Figure | Value | Meaning |
|--------|------:|---------|
| Distinct pytest tests collected in the new module | **54** | 54 test cases were collected and executed. This is the number reported by pytest and the only figure that changes the suite total. |
| Test functions in the new module | **48** | 48 `def test_...` functions. Three of them use `@pytest.mark.parametrize`, so 48 functions expand to 54 collected cases. |
| Sum of the per-Story counts | **63** | 11 + 12 + 6 + 4 + 9 + 16 + 5. This is a **coverage mapping**, not a test count. |

### Why the per-Story counts sum to 63 and not 54

The per-Story tables below map each test to the Story whose acceptance
behaviour it evidences. Several tests evidence more than one Story, so they are
counted once under each Story they support. Nine tests are mapped to two
Stories each:

| Test mapped to two Stories | Stories |
|---|---|
| `test_member_search_is_partial_and_case_insensitive` | -2, -3 |
| `test_member_search_route_returns_only_matches` | -2, -3 |
| `test_duplicate_names_distinguishable_in_list_and_detail_views` | -3, -5 |
| `test_guardian_create_persists_and_is_retrievable` | -2, -6 |
| `test_guardian_create_route_redirects_to_viewable_detail` | -2, -6 |
| `test_guardian_create_invalid_input_shows_feedback_and_stores_nothing` | -2, -6 |
| `test_guardian_search_partial_and_case_insensitive` | -3, -6 |
| `test_guardian_update_keeps_relationships_intact` | -7, -8 |
| `test_guardian_contact_update_reflected_on_member_page` | -7, -8 |

Therefore:

```text
sum of per-Story counts   63
minus tests counted twice  9
= distinct tests          54   (matches the pytest collection total)
```

The per-Story mapping also counts parametrized cases individually: five cases
in the -2 column, three cases in the -6 column (2 parametrized + the overlap),
and two cases in the -7 column from
`test_link_invalid_identifiers_rejected`. Those are noted in the relevant
tables below.

### Parametrized cases

```text
python -m pytest tests/test_member_guardian_workflows.py --collect-only -q
```

| Parametrized function | Cases | Cases as shown by pytest |
|---|---:|---|
| `test_member_create_invalid_input_shows_feedback_and_stores_nothing` | 5 | `[payload0-Name is required.]` … `[payload4-Email address is not valid.]` |
| `test_guardian_create_invalid_input_shows_feedback_and_stores_nothing` | 2 | `[payload0-Name is required.]`, `[payload1-Email address is not valid.]` |
| `test_link_invalid_identifiers_rejected` | 2 | `[99999-1]`, `[1-99999]` |
| 45 non-parametrized functions | 45 | one case each |
| **Total collected** | **54** | |

## Story-to-test mapping

Existing tests are listed where they already covered a Story; new Sprint 2
tests are in `tests/test_member_guardian_workflows.py`. The counts in the
headings are mappings, not distinct test totals — see the section above.

### MSD426GXUST25-2 — Create Member Record (3 SP)

Per-Story mapping count: **11** (1 existing + 10 new; the new 10 are 6 functions
expanding to 10 cases because `test_member_create_invalid_input_shows_feedback_and_stores_nothing` is parametrized 5 ways).

| Acceptance check | Method | Where |
|---|---|---|
| Valid record is created and persisted | Service | existing `test_members.py::test_create_member`; new `test_member_create_persists_and_is_retrievable` |
| Newly created member can be viewed | Route | new `test_member_create_route_redirects_to_viewable_detail` |
| Required fields and invalid input follow documented rules | Route + service | existing `test_validation.py`; new parametrised `test_member_create_invalid_input_shows_feedback_and_stores_nothing` |
| Success and failure feedback is shown | Route | new `test_member_create_route_redirects_to_viewable_detail`, `test_member_create_invalid_input_shows_feedback_and_stores_nothing` |
| Failed submissions create no incomplete record | Route | new `test_member_create_invalid_input_shows_feedback_and_stores_nothing` |

### MSD426GXUST25-3 — Search and Update Member (3 SP)

Per-Story mapping count: **12** (2 existing + 10 new; overlaps -2 for the two
member-search tests and -5 for
`test_duplicate_names_distinguishable_in_list_and_detail_views`).

| Acceptance check | Method | Where |
|---|---|---|
| Supported search fields return expected results | Service + route | existing `test_members.py`; new `test_member_search_is_partial_and_case_insensitive`, `test_member_search_route_returns_only_matches` |
| Same-named members stay distinguishable | Service + route | new `test_duplicate_names_distinguishable_in_list_and_detail_views` |
| Valid updates persist after reopening | Service + route | existing `test_update_member`; new `test_member_update_persists_after_reload`, `test_member_update_route_persists_and_shows_new_values` |
| Invalid updates and unknown ids handled safely | Service + route | new `test_member_update_with_invalid_input_changes_nothing`, `test_member_update_invalid_input_shows_feedback`, `test_member_update_unknown_id_is_handled_safely`, `test_member_update_unknown_id_redirects_with_feedback` |
| Updating one member does not modify another | Service | new `test_updating_one_duplicate_does_not_change_the_other` |

### MSD426GXUST25-4 — Deactivation of Members (2 SP)

Per-Story mapping count: **6** (1 existing + 5 new).

| Acceptance check | Method | Where |
|---|---|---|
| Correct member is updated | Route | new `test_deactivate_route_updates_target_member_only` |
| Resulting status persists | Service + route | existing `test_set_inactive`; new `test_deactivate_status_persists_and_is_shown` |
| History, guardian links and unrelated records are preserved | Service | new `test_deactivate_preserves_registrations_and_guardians`, `test_deactivate_does_not_remove_team_placement` |
| Invalid or repeated operations behave consistently | Service + route | new `test_deactivate_is_idempotent_and_reactivatable`, `test_deactivate_unknown_member_is_handled_safely` |
| No permanent deletion where deactivation is required | Service | new `test_deactivate_preserves_registrations_and_guardians` (record still retrievable) |

### MSD426GXUST25-5 — Support Duplicate Member Names (2 SP)

Per-Story mapping count: **4** (1 existing + 3 new; overlaps -3 for
`test_duplicate_names_distinguishable_in_list_and_detail_views`).

| Acceptance check | Method | Where |
|---|---|---|
| Different members may share a name | Service | existing `test_duplicate_names_allowed`; new `test_duplicate_names_have_independent_identity_and_data` |
| Each member keeps an independent identity and data | Service | new `test_duplicate_names_have_independent_identity_and_data` |
| Search and detail views distinguish them | Route | new `test_duplicate_names_distinguishable_in_list_and_detail_views` |
| Updating one duplicate does not change the other | Service | new `test_updating_one_duplicate_does_not_change_the_other` |
| Not confused with duplicate registrations for one member | Service | new `test_duplicate_names_are_not_duplicate_registrations` |

### MSD426GXUST25-6 — Create, Search and Update Guardian (3 SP)

Per-Story mapping count: **9** (2 existing + 7 new; the new 7 are 4 functions
expanding to 7 cases because
`test_guardian_create_invalid_input_shows_feedback_and_stores_nothing` is
parametrized 2 ways. Overlaps -2 for the three guardian-create tests and -3 for
`test_guardian_search_partial_and_case_insensitive`).

| Acceptance check | Method | Where |
|---|---|---|
| Guardians can be created with valid details | Service + route | existing `test_create_guardian`; new `test_guardian_create_persists_and_is_retrievable`, `test_guardian_create_route_redirects_to_viewable_detail` |
| Supported searches return correct results | Service | existing `test_search_guardian`; new `test_guardian_search_partial_and_case_insensitive` |
| Updates persist and appear in detail views | Service + route | existing `test_update_guardian`; new `test_guardian_update_persists_after_reload`, `test_guardian_update_route_persists_and_shows_new_values` |
| Missing records and invalid input handled safely | Service + route | new `test_guardian_create_invalid_input_shows_feedback_and_stores_nothing`, `test_guardian_update_with_invalid_input_changes_nothing`, `test_guardian_update_unknown_id_is_handled_safely` |
| Relationships remain intact after an update | Service | new `test_guardian_update_keeps_relationships_intact` |

### MSD426GXUST25-7 — Link Guardians to Junior Members (3 SP)

Per-Story mapping count: **16** (3 existing + 13 new; the new 13 are 11
functions expanding to 13 cases because `test_link_invalid_identifiers_rejected`
is parametrized 2 ways. Overlaps -8 for
`test_guardian_update_keeps_relationships_intact` and
`test_guardian_contact_update_reflected_on_member_page`).

| Acceptance check | Method | Where |
|---|---|---|
| Correct guardian linked to the intended junior | Service + route | existing `test_one_guardian_linked_to_multiple_juniors`; new `test_link_guardian_to_junior_persists_in_both_directions`, `test_link_route_persists_and_is_visible_on_both_pages` |
| Relationship persists and is visible in the views | Route | new `test_link_route_persists_and_is_visible_on_both_pages` |
| Invalid identifiers handled safely | Service + route | existing `test_nonexistent_guardian_link_rejected`, `test_nonexistent_member_link_rejected`; new `test_link_invalid_identifiers_rejected`, `test_link_route_without_member_choice_is_refused` |
| Existing relationship constraints maintained | Service | existing `test_duplicate_guardian_link_rejected`; new `test_duplicate_link_creates_one_relationship` |
| Under-18 rule still requires a guardian | Service | existing `test_registration.py` rules; new `test_under_18_rule_requires_guardian_before_completion`, `test_under_18_rule_satisfied_once_guardian_linked` |
| Successful and unsuccessful unlink operations | Service + route | new `test_unlink_removes_only_the_relationship`, `test_unlink_reports_when_nothing_was_linked`, `test_unlink_route_reports_no_op_instead_of_success`, `test_unlink_route_reports_success_when_link_removed`, `test_unlink_unknown_identifiers_is_handled_safely` |

### MSD426GXUST25-8 — Reflect Guardian Contact Updates (2 SP)

Per-Story mapping count: **5** (1 existing + 4 new; overlaps -7 for
`test_guardian_update_keeps_relationships_intact` and
`test_guardian_contact_update_reflected_on_member_page`).

| Acceptance check | Method | Where |
|---|---|---|
| Contact updates persist | Service | existing `test_guardian_contact_update_reflected`; new `test_guardian_update_persists_after_reload` |
| Relevant pages display updated contact information | Route | new `test_guardian_contact_update_reflected_on_member_page`, `test_guardian_contact_update_reflected_on_guardian_pages` |
| Guardian-member relationships remain intact | Service | new `test_guardian_update_keeps_relationships_intact` |
| Updating one guardian does not change another | Service | new `test_updating_one_guardian_does_not_change_another` |
| No unnecessary stale duplicated contact data | Structural | new `test_guardian_contact_is_read_from_the_shared_record` |

## Test methods

- **Framework:** `pytest`, using the existing `tests/conftest.py` fixtures.
- **Isolation:** every test runs against a fresh temporary SQLite database
  created by the `app` fixture. The real application database is never used.
- **Service-layer tests:** call `app/services.py` functions directly to test
  business rules independently of HTTP.
- **Route tests:** use the Flask test client, including `follow_redirects=True`
  where flash feedback is asserted.
- **Structural test:** `PRAGMA table_info` is used once to assert that
  `guardian_members` stores no contact columns, protecting the design decision
  behind Story MSD426GXUST25-8.
- **Negative tests:** invalid input is asserted both to raise and to leave the
  stored data unchanged, so a "fails loudly but corrupts data" regression would
  be caught.

## Confirmed acceptance checks

The following were verified by reading the code and reproducing behaviour.
They are confirmed as working, so no change was made:

- Member and guardian creation rejects invalid input, returns HTTP 400 and
  creates no partial record; the failure message is rendered on the page.
- Member and guardian edit forms retain the values the user typed when
  validation fails, while the stored record stays unchanged.
- Deactivation is a soft state change; registrations, guardian links and team
  placement are preserved.
- Duplicate member names are permitted and each record keeps separate data.
- Guardian contact details are read from the single `guardians` row through a
  join, so updates appear on the member page and guardian pages with no stale
  duplication.
- The under-18 guardian rule is enforced when a registration becomes
  `Complete`, whether created or amended.

## Defects found and actions

| ID | Story | Severity | Summary | Action |
|---|---|---|---|---|
| S2-D1 | MSD426GXUST25-7 | Low | `unlink_guardian_member` reported success for a pair that was not linked (Sprint 1 defect D3, confirmed by reproduction). | `unlink_guardian_member` now returns whether a row was removed and `guardian_unlink` reports accurately. Tests added. |
| S2-F1 | Deferred to Team and Roster Management (Sprint 4) | Low | `remove_player_from_team` has the same silent-success pattern as S2-D1, but team/player removal is outside the Member and Guardian Management epic. | Change was implemented during initial Sprint 2 work and then **deliberately removed** from this sprint to keep the scope clean. Documented for Sprint 4; see `sprint-2-defect-log.md`. |

## Unresolved requirements and open decisions

These are recorded as **decision required**, not implemented. They are carried
forward from Sprint 1 and are not part of the seven Sprint 2 Stories.

1. **D1 — duplicate same-season registrations.** `create_registration` does not
   prevent a second registration for the same member and season, and the schema
   has no uniqueness constraint, while `docs/architecture.md` describes
   registrations as "one per season". A product decision is required. This is
   **not** the same question as duplicate member names
   (MSD426GXUST25-5).
2. **D2 — withdrawn registration still on a roster.** `withdraw_registration`
   does not remove the member from `team_players`. A product decision is
   required.
3. **Inactive-member behaviour (new observation).** The requirements do not
   state what deactivation should do about team placement, future
   registrations, or guardian links. The current implementation keeps all of
   them. No rule was invented; see `sprint-2-defect-log.md` (S2-O1).
4. **Guardian removal after a registration is Complete (new observation).** A
   `Complete` registration stays `Complete` if the guardian link is later
   removed. Whether completion should be re-validated on unlink is not
   specified. See `sprint-2-defect-log.md` (S2-O2).
5. **Jira acceptance criteria.** Authorised Jira acceptance criteria were not
   available in the repository. Expected behaviour was therefore derived from
   the code, the README business rules, and `docs/architecture.md`. Any
   divergence between those derived expectations and the authoritative Jira
   criteria must be resolved by the team.

## Out of scope for this sprint

- **Team and player management.** No change is retained for
  `remove_player_from_team` or `player_remove`; the attempted fix was reverted
  and is deferred (S2-F1).
- No changes to registrations, teams, players or the dashboard.
- No database schema changes.
- No authentication, deployment or configuration changes.
- No Git operations (branching, staging, committing, pushing, pull requests).
- No Jira changes.
