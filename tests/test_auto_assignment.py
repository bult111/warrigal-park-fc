"""Automatic team assignment tests.

A Complete registration for a season makes the member eligible for a team whose
age group matches the computed age group. Eligible players are placed
automatically onto the team with the fewest players, breaking ties by lowest
team id. A placement that already exists is never silently moved.
"""

from datetime import date

import pytest

from app import database, services

SEASON = "2026"
SENIORS = "Seniors"  # the default member fixture is an adult, so Seniors in 2026


def test_complete_registration_auto_assigns_to_matching_team(
    make_member, make_registration, make_team
):
    team = make_team(SEASON, "Tigers", SENIORS)
    member = make_member("Auto Player")

    registration = make_registration(member["id"], SEASON, status="Complete")

    assert registration["status"] == "Complete"
    assert [p["name"] for p in services.team_players(team["id"])] == ["Auto Player"]
    assert services.team_for_member_in_season(member["id"], SEASON)["id"] == team["id"]


def test_complete_without_matching_team_stays_unassigned(make_member, make_registration):
    member = make_member("Waiting Player")

    registration = make_registration(member["id"], SEASON, status="Complete")

    assert registration["status"] == "Complete"
    assert services.team_for_member_in_season(member["id"], SEASON) is None


def test_creating_matching_team_assigns_waiting_player(
    make_member, make_registration, make_team
):
    member = make_member("Waiting Player")
    make_registration(member["id"], SEASON, status="Complete")
    assert services.team_for_member_in_season(member["id"], SEASON) is None

    team = make_team(SEASON, "Tigers", SENIORS)

    assert [p["name"] for p in services.team_players(team["id"])] == ["Waiting Player"]


def test_two_empty_matching_teams_use_the_lowest_id(
    make_member, make_registration, make_team
):
    first = make_team(SEASON, "Tigers", SENIORS)
    second = make_team(SEASON, "Eagles", SENIORS)
    assert first["id"] < second["id"]

    member = make_member("Lowest Id")
    make_registration(member["id"], SEASON, status="Complete")

    assert [p["name"] for p in services.team_players(first["id"])] == ["Lowest Id"]
    assert services.team_players(second["id"]) == []


def test_fewest_players_wins_over_the_lowest_id_team(
    make_member, make_registration, make_team
):
    alpha = make_team(SEASON, "Alpha", SENIORS)  # lowest id
    bravo = make_team(SEASON, "Bravo", SENIORS)
    charlie = make_team(SEASON, "Charlie", SENIORS)

    # Four players distribute Alpha, Bravo, Charlie, Alpha -> 2 / 1 / 1.
    for name in ("P1", "P2", "P3", "P4"):
        member = make_member(name)
        make_registration(member["id"], SEASON, status="Complete")

    assert sorted(p["name"] for p in services.team_players(alpha["id"])) == ["P1", "P4"]
    assert len(services.team_players(bravo["id"])) == 1
    assert len(services.team_players(charlie["id"])) == 1

    late = make_member("Late Player")
    make_registration(late["id"], SEASON, status="Complete")

    # The fuller lowest-id team is skipped; the empty-team tie breaks by id.
    assert "Late Player" not in [p["name"] for p in services.team_players(alpha["id"])]
    assert "Late Player" in [p["name"] for p in services.team_players(bravo["id"])]
    assert "Late Player" not in [
        p["name"] for p in services.team_players(charlie["id"])
    ]


def test_started_registration_is_never_auto_assigned(
    make_member, make_registration, make_team
):
    team = make_team(SEASON, "Tigers", SENIORS)
    member = make_member("Started Player")

    make_registration(member["id"], SEASON, status="Started")

    assert services.team_players(team["id"]) == []
    assert services.team_for_member_in_season(member["id"], SEASON) is None


def test_withdrawn_registration_is_never_auto_assigned(
    make_member, make_registration, make_team
):
    member = make_member("Withdrawn Player")
    registration = make_registration(member["id"], SEASON, status="Started")
    services.withdraw_registration(registration["id"])

    team = make_team(SEASON, "Tigers", SENIORS)

    assert services.team_players(team["id"]) == []
    assert services.team_for_member_in_season(member["id"], SEASON) is None


def test_season_mismatch_is_never_auto_assigned(
    make_member, make_registration, make_team
):
    team = make_team("2025", "Tigers", SENIORS)
    member = make_member("Wrong Season")

    make_registration(member["id"], SEASON, status="Complete")

    assert services.team_players(team["id"]) == []
    assert services.team_for_member_in_season(member["id"], SEASON) is None


def test_age_group_mismatch_is_never_auto_assigned(
    make_member, make_registration, make_team
):
    team = make_team(SEASON, "Juniors", "U16")  # the member is Seniors in 2026
    member = make_member("Wrong Group")

    make_registration(member["id"], SEASON, status="Complete")

    assert services.team_players(team["id"]) == []
    assert services.team_for_member_in_season(member["id"], SEASON) is None


def test_creating_a_mismatched_team_does_not_assign(
    make_member, make_registration, make_team
):
    member = make_member("Wrong Group")  # Seniors in 2026
    make_registration(member["id"], SEASON, status="Complete")

    team = make_team(SEASON, "Juniors", "U16")

    assert services.team_players(team["id"]) == []
    assert services.team_for_member_in_season(member["id"], SEASON) is None


def test_existing_assignment_is_not_moved_by_later_triggers(
    make_member, make_registration, make_team
):
    first = make_team(SEASON, "Tigers", SENIORS)
    member = make_member("Placed Player")
    make_registration(member["id"], SEASON, status="Complete")
    assert [p["name"] for p in services.team_players(first["id"])] == ["Placed Player"]

    # A new, emptier matching team appears: the placement must stand.
    second = make_team(SEASON, "Eagles", SENIORS)
    assert [p["name"] for p in services.team_players(first["id"])] == ["Placed Player"]
    assert services.team_players(second["id"]) == []

    # An explicit trigger is also a no-op for an already-assigned member.
    assert services.auto_assign_player(member["id"], SEASON)["id"] == first["id"]
    assert services.team_players(second["id"]) == []


def test_manual_add_requires_season_and_age_group(
    make_member, make_registration, make_team
):
    member = make_member("Manual Player")
    make_registration(member["id"], SEASON, status="Complete")
    wrong_season = make_team("2025", "Tigers", SENIORS)
    wrong_group = make_team(SEASON, "Juniors", "U16")

    with pytest.raises(services.ServiceError):
        services.add_player_to_team(wrong_season["id"], member["id"])
    with pytest.raises(services.ServiceError):
        services.add_player_to_team(wrong_group["id"], member["id"])

    assert services.team_players(wrong_season["id"]) == []
    assert services.team_players(wrong_group["id"]) == []


def test_move_rejects_cross_season_target(make_member, make_registration, make_team):
    member = make_member("Cross Season")
    source = make_team(SEASON, "Tigers", SENIORS)
    make_registration(member["id"], SEASON, status="Complete")
    target = make_team("2025", "Eagles", SENIORS)

    with pytest.raises(services.ServiceError):
        services.move_player(member["id"], source["id"], target["id"])

    assert [p["name"] for p in services.team_players(source["id"])] == ["Cross Season"]
    assert services.team_players(target["id"]) == []


def test_move_rejects_wrong_age_group_target(make_member, make_registration, make_team):
    member = make_member("Wrong Group")  # Seniors in 2026
    source = make_team(SEASON, "Tigers", SENIORS)
    make_registration(member["id"], SEASON, status="Complete")
    target = make_team(SEASON, "Juniors", "U16")

    with pytest.raises(services.ServiceError):
        services.move_player(member["id"], source["id"], target["id"])

    assert [p["name"] for p in services.team_players(source["id"])] == ["Wrong Group"]
    assert services.team_players(target["id"]) == []


def test_only_one_team_per_season(make_member, make_registration, make_team):
    member = make_member("One Team Only")
    first = make_team(SEASON, "Tigers", SENIORS)
    make_registration(member["id"], SEASON, status="Complete")
    second = make_team(SEASON, "Eagles", SENIORS)

    with pytest.raises(services.ServiceError):
        services.add_player_to_team(second["id"], member["id"])

    assert [p["name"] for p in services.team_players(first["id"])] == ["One Team Only"]
    assert services.team_players(second["id"]) == []


def test_withdraw_only_complete_registration_removes_assignment(
    make_member, make_registration, make_team
):
    team = make_team(SEASON, "Tigers", SENIORS)
    member = make_member("Single Complete")
    registration = make_registration(member["id"], SEASON, status="Complete")
    assert [p["name"] for p in services.team_players(team["id"])] == ["Single Complete"]

    services.withdraw_registration(registration["id"])

    assert services.team_players(team["id"]) == []
    assert services.team_for_member_in_season(member["id"], SEASON) is None
    stored = services.get_registration(registration["id"])
    assert stored is not None
    assert stored["status"] == "Withdrawn"


def test_withdraw_one_of_two_complete_registrations_keeps_assignment(
    make_member, make_registration, make_team
):
    team = make_team(SEASON, "Tigers", SENIORS)
    member = make_member("Double Complete")
    first = make_registration(member["id"], SEASON, status="Complete")
    second = make_registration(member["id"], SEASON, status="Complete")
    assert [p["name"] for p in services.team_players(team["id"])] == ["Double Complete"]

    services.withdraw_registration(first["id"])

    # The surviving Complete registration still supports the assignment.
    assert [p["name"] for p in services.team_players(team["id"])] == ["Double Complete"]
    assert services.get_registration(first["id"])["status"] == "Withdrawn"
    assert services.get_registration(second["id"])["status"] == "Complete"

    # Only once no Complete registration remains is the assignment dropped.
    services.withdraw_registration(second["id"])
    assert services.team_players(team["id"]) == []
    assert services.get_registration(second["id"]) is not None
    assert services.get_registration(second["id"])["status"] == "Withdrawn"


# ---------------------------------------------------------------------------
# Stored-vs-computed age group consistency for automatic assignment
# ---------------------------------------------------------------------------

SEASON_YEAR = 2026


def _dob_for(season_age):
    """A date of birth that yields ``season_age`` in ``SEASON``."""
    return date(SEASON_YEAR - season_age, 1, 1).isoformat()


def _store_complete_with_stale_group(registration_id, age_group):
    """Force a Complete status and a stale age group directly in the database."""
    database.get_db().execute(
        "UPDATE registrations SET status = 'Complete', age_group = ? WHERE id = ?",
        (age_group, registration_id),
    )
    database.get_db().commit()


def test_auto_assign_ignores_a_stale_stored_age_group(
    make_member, make_registration, make_team
):
    """A legacy stored age group is never used to choose a team."""
    member = make_member("Stale Player", dob=_dob_for(14))  # computed U16 in 2026
    registration = make_registration(member["id"], SEASON, status="Started")
    _store_complete_with_stale_group(registration["id"], "Seniors")

    stale_only = make_team(SEASON, "Stale Seniors", "Seniors")

    assert services.auto_assign_player(member["id"], SEASON) is None
    assert services.team_players(stale_only["id"]) == []
    assert services.team_for_member_in_season(member["id"], SEASON) is None


def test_pending_assignment_uses_the_computed_group(
    make_member, make_registration, make_team
):
    """Creating the matching team assigns a waiting player despite a stale group."""
    member = make_member("Stale Pending", dob=_dob_for(14))
    registration = make_registration(member["id"], SEASON, status="Started")
    _store_complete_with_stale_group(registration["id"], "Seniors")

    team = make_team(SEASON, "Computed U16", "U16")

    assert [p["member_id"] for p in services.team_players(team["id"])] == [member["id"]]
    assert services.team_for_member_in_season(member["id"], SEASON)["id"] == team["id"]


def test_mismatched_existing_assignment_is_not_duplicated_or_moved(
    make_member, make_guardian, link_guardian, make_registration, make_team
):
    """An assignment that no longer matches is reported, not silently changed."""
    member = make_member("Mismatch Player", dob=_dob_for(14))  # U16
    guardian = make_guardian("Guardian Mismatch")
    link_guardian(guardian["id"], member["id"])
    u16 = make_team(SEASON, "U16 Team", "U16")
    make_registration(member["id"], SEASON, status="Complete")
    assert [p["member_id"] for p in services.team_players(u16["id"])] == [member["id"]]

    # Make the member Seniors directly so the existing U16 placement is stale.
    database.get_db().execute(
        "UPDATE members SET date_of_birth = ? WHERE id = ?",
        (_dob_for(20), member["id"]),
    )
    database.get_db().commit()
    seniors = make_team(SEASON, "Seniors Team", "Seniors")

    returned = services.auto_assign_player(member["id"], SEASON)
    assert returned["id"] == u16["id"]

    rows = database.query_all(
        """
        SELECT tp.team_id
        FROM team_players tp
        JOIN teams t ON t.id = tp.team_id
        WHERE tp.member_id = ? AND t.season = ?
        """,
        (member["id"], SEASON),
    )
    assert [row["team_id"] for row in rows] == [u16["id"]]
    assert services.team_players(seniors["id"]) == []

    conflict = services.assignment_conflict(member["id"], SEASON)
    assert conflict is not None
    assert "U16 Team" in conflict


def test_auto_assign_prefers_the_team_with_fewest_players(
    make_member, make_guardian, link_guardian, make_registration, make_team
):
    """The least-full matching team wins even when it is not the lowest id."""
    first = make_team(SEASON, "First", "U16")
    second = make_team(SEASON, "Second", "U16")
    third = make_team(SEASON, "Third", "U16")

    # Two players on the first team, one on the second, none on the third.
    for team, count in ((first, 2), (second, 1)):
        for index in range(count):
            filler = make_member(f"Filler {team['id']}-{index}", dob=_dob_for(14))
            database.execute(
                "INSERT INTO team_players (team_id, member_id) VALUES (?, ?)",
                (team["id"], filler["id"]),
            )

    target = make_member("Target Player", dob=_dob_for(14))
    guardian = make_guardian("Guardian Target")
    link_guardian(guardian["id"], target["id"])
    make_registration(target["id"], SEASON, status="Complete")

    assert [p["member_id"] for p in services.team_players(third["id"])] == [target["id"]]
    assert target["id"] not in [
        p["member_id"] for p in services.team_players(first["id"])
    ]
    assert target["id"] not in [
        p["member_id"] for p in services.team_players(second["id"])
    ]


def test_auto_assign_tie_breaks_by_lowest_team_id(
    make_member, make_guardian, link_guardian, make_registration, make_team
):
    """With equal player counts the lowest team id is chosen."""
    first = make_team(SEASON, "First", "U16")
    second = make_team(SEASON, "Second", "U16")
    target = make_member("Tie Player", dob=_dob_for(14))
    guardian = make_guardian("Guardian Tie")
    link_guardian(guardian["id"], target["id"])

    make_registration(target["id"], SEASON, status="Complete")

    assert [p["member_id"] for p in services.team_players(first["id"])] == [target["id"]]
    assert services.team_players(second["id"]) == []


def test_waiting_player_is_assigned_when_the_matching_team_is_created(
    make_member, make_guardian, link_guardian, make_registration, make_team
):
    """No matching team keeps the registration Complete but unassigned."""
    member = make_member("Waiting Player", dob=_dob_for(14))
    guardian = make_guardian("Guardian Waiting")
    link_guardian(guardian["id"], member["id"])

    registration = make_registration(member["id"], SEASON, status="Complete")

    assert registration["status"] == "Complete"
    assert services.team_for_member_in_season(member["id"], SEASON) is None

    team = make_team(SEASON, "U16 Team", "U16")

    assert [p["member_id"] for p in services.team_players(team["id"])] == [member["id"]]
