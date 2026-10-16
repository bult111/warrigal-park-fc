"""Player (team membership) management tests."""

import pytest

from app import services


def test_complete_registration_auto_assigns_player(make_member, make_registration, make_team):
    """A Complete registration is auto-assigned to a matching team."""
    member = make_member("Eligible Player")
    team = make_team("2026", "Tigers", "Seniors")
    make_registration(member["id"], "2026", "U16", "Complete")

    assert [p["name"] for p in services.team_players(team["id"])] == ["Eligible Player"]


def test_manual_add_after_removal_accepted(make_member, make_registration, make_team):
    """A Complete same-season player can be re-added manually after a removal."""
    member = make_member("Eligible Player")
    team = make_team("2026", "Tigers", "Seniors")
    make_registration(member["id"], "2026", "U16", "Complete")
    services.remove_player_from_team(team["id"], member["id"])

    services.add_player_to_team(team["id"], member["id"])

    assert [p["name"] for p in services.team_players(team["id"])] == ["Eligible Player"]


def test_unregistered_player_rejected(make_member, make_team):
    member = make_member("No Registration")
    team = make_team("2026", "Tigers", "Seniors")

    with pytest.raises(services.ServiceError):
        services.add_player_to_team(team["id"], member["id"])

    assert services.team_players(team["id"]) == []


def test_started_registration_not_eligible(make_member, make_registration, make_team):
    """A Started (not Complete) registration does not make a player eligible."""
    member = make_member("Started Only")
    make_registration(member["id"], "2026", "U16", "Started")
    team = make_team("2026", "Tigers", "Seniors")

    with pytest.raises(services.ServiceError):
        services.add_player_to_team(team["id"], member["id"])

    assert services.team_players(team["id"]) == []


def test_withdrawn_registration_not_eligible_for_team(make_member, make_registration, make_team):
    """A withdrawn registration does not make a player eligible for a team."""
    member = make_member("Withdrawn Player")
    reg = make_registration(member["id"], "2026", "U16", "Started")
    services.withdraw_registration(reg["id"])
    team = make_team("2026", "Tigers", "Seniors")

    with pytest.raises(services.ServiceError):
        services.add_player_to_team(team["id"], member["id"])

    assert services.team_players(team["id"]) == []


def test_wrong_season_player_rejected(make_member, make_registration, make_team):
    member = make_member("Wrong Season")
    make_registration(member["id"], "2025", "U16", "Complete")
    team = make_team("2026", "Tigers", "Seniors")

    with pytest.raises(services.ServiceError):
        services.add_player_to_team(team["id"], member["id"])

    assert services.team_players(team["id"]) == []


def test_complete_registration_qualifies_despite_earlier_started(
    make_member, make_registration, make_team
):
    """A Complete registration qualifies even when an earlier Started row exists."""
    member = make_member("Multi Reg")
    team = make_team("2026", "Tigers", "Seniors")
    make_registration(member["id"], "2026", "U16", "Started")
    make_registration(member["id"], "2026", "U16", "Complete")

    assert [p["name"] for p in services.team_players(team["id"])] == ["Multi Reg"]


def test_age_group_mismatch_rejected(make_member, make_registration, make_team):
    """A player cannot join a team whose age group differs from their own."""
    member = make_member("Mismatch Player")
    make_registration(member["id"], "2026", "U16", "Complete")
    team = make_team("2026", "Tigers", "U16")

    with pytest.raises(services.ServiceError):
        services.add_player_to_team(team["id"], member["id"])

    assert services.team_players(team["id"]) == []


def test_remove_player(make_member, make_registration, make_team):
    member = make_member("Remover")
    team = make_team("2026", "Tigers", "Seniors")
    make_registration(member["id"], "2026", "U16", "Complete")

    removed = services.remove_player_from_team(team["id"], member["id"])

    assert removed is True
    assert services.team_players(team["id"]) == []


def test_remove_player_not_in_team_returns_false(make_member, make_registration, make_team):
    member = make_member("Outsider")
    team = make_team("2026", "Tigers", "Seniors")
    make_registration(member["id"], "2026", "U16", "Complete")
    services.remove_player_from_team(team["id"], member["id"])

    removed = services.remove_player_from_team(team["id"], member["id"])

    assert removed is False
    assert services.team_players(team["id"]) == []


def test_remove_nonexistent_member_rejected(make_team):
    team = make_team("2026", "Tigers", "Seniors")
    with pytest.raises(services.ServiceError) as exc_info:
        services.remove_player_from_team(team["id"], 99999)
    assert "Member not found" in str(exc_info.value)


def test_move_player(make_member, make_registration, make_team):
    member = make_member("Mover")
    team_a = make_team("2026", "Tigers", "Seniors")
    team_b = make_team("2026", "Eagles", "Seniors")
    make_registration(member["id"], "2026", "U16", "Complete")  # auto-assigns to team A

    services.move_player(member["id"], team_a["id"], team_b["id"])

    assert services.team_players(team_a["id"]) == []
    assert [p["name"] for p in services.team_players(team_b["id"])] == ["Mover"]


def test_registration_preserved_after_move(make_member, make_registration, make_team):
    member = make_member("Mover")
    team_a = make_team("2026", "Tigers", "Seniors")
    team_b = make_team("2026", "Eagles", "Seniors")
    reg = make_registration(member["id"], "2026", "U16", "Complete")

    services.move_player(member["id"], team_a["id"], team_b["id"])

    assert services.get_registration(reg["id"]) is not None
    assert services.get_registration(reg["id"])["status"] == "Complete"


def test_registration_preserved_after_remove(make_member, make_registration, make_team):
    member = make_member("Remover")
    team = make_team("2026", "Tigers", "Seniors")
    reg = make_registration(member["id"], "2026", "U16", "Complete")

    services.remove_player_from_team(team["id"], member["id"])

    assert services.get_registration(reg["id"]) is not None
    assert services.get_registration(reg["id"])["status"] == "Complete"


def test_move_to_wrong_season_rejected(make_member, make_registration, make_team):
    member = make_member("Season Mover")
    team_a = make_team("2026", "Tigers", "Seniors")
    team_b = make_team("2025", "Eagles", "Seniors")
    make_registration(member["id"], "2026", "U16", "Complete")

    with pytest.raises(services.ServiceError):
        services.move_player(member["id"], team_a["id"], team_b["id"])

    # The player stays in team A.
    assert [p["name"] for p in services.team_players(team_a["id"])] == ["Season Mover"]


def test_move_player_to_nonexistent_team_rejected(make_member, make_registration, make_team):
    member = make_member("Move Ghost")
    team_a = make_team("2026", "Tigers", "Seniors")
    make_registration(member["id"], "2026", "U16", "Complete")

    with pytest.raises(services.ServiceError):
        services.move_player(member["id"], team_a["id"], 99999)

    assert [p["name"] for p in services.team_players(team_a["id"])] == ["Move Ghost"]


def test_second_team_in_same_season_rejected(make_member, make_registration, make_team):
    """A player can only hold one team assignment per season."""
    member = make_member("Dual Team")
    team_a = make_team("2026", "Tigers", "Seniors")
    team_b = make_team("2026", "Eagles", "Seniors")
    make_registration(member["id"], "2026", "U16", "Complete")  # auto-assigns to team A

    with pytest.raises(services.ServiceError):
        services.add_player_to_team(team_b["id"], member["id"])

    assert [p["name"] for p in services.team_players(team_a["id"])] == ["Dual Team"]
    assert services.team_players(team_b["id"]) == []
