"""Player (team membership) management tests."""

import pytest

from app import services


def test_same_season_registered_player_accepted(make_member, make_registration, make_team):
    member = make_member("Eligible Player")
    make_registration(member["id"], "2026", "U16", "Complete")
    team = make_team("2026", "Tigers", "U16")

    services.add_player_to_team(team["id"], member["id"])

    players = services.team_players(team["id"])
    assert len(players) == 1
    assert players[0]["name"] == "Eligible Player"


def test_unregistered_player_rejected(make_member, make_team):
    member = make_member("No Registration")
    team = make_team("2026", "Tigers", "U16")

    with pytest.raises(services.ServiceError):
        services.add_player_to_team(team["id"], member["id"])

    assert services.team_players(team["id"]) == []


def test_wrong_season_player_rejected(make_member, make_registration, make_team):
    member = make_member("Wrong Season")
    make_registration(member["id"], "2025", "U16", "Complete")
    team = make_team("2026", "Tigers", "U16")

    with pytest.raises(services.ServiceError):
        services.add_player_to_team(team["id"], member["id"])

    assert services.team_players(team["id"]) == []


def test_move_player(make_member, make_registration, make_team):
    member = make_member("Mover")
    make_registration(member["id"], "2026", "U16", "Complete")
    team_a = make_team("2026", "Tigers", "U16")
    team_b = make_team("2026", "Eagles", "U16")
    services.add_player_to_team(team_a["id"], member["id"])

    services.move_player(member["id"], team_a["id"], team_b["id"])

    assert services.team_players(team_a["id"]) == []
    assert [p["name"] for p in services.team_players(team_b["id"])] == ["Mover"]


def test_remove_player(make_member, make_registration, make_team):
    member = make_member("Remover")
    make_registration(member["id"], "2026", "U16", "Complete")
    team = make_team("2026", "Tigers", "U16")
    services.add_player_to_team(team["id"], member["id"])

    services.remove_player_from_team(team["id"], member["id"])

    assert services.team_players(team["id"]) == []


def test_registration_preserved_after_move(make_member, make_registration, make_team):
    member = make_member("Mover")
    reg = make_registration(member["id"], "2026", "U16", "Complete")
    team_a = make_team("2026", "Tigers", "U16")
    team_b = make_team("2026", "Eagles", "U16")
    services.add_player_to_team(team_a["id"], member["id"])

    services.move_player(member["id"], team_a["id"], team_b["id"])

    assert services.get_registration(reg["id"]) is not None
    assert services.get_registration(reg["id"])["status"] == "Complete"


def test_registration_preserved_after_remove(make_member, make_registration, make_team):
    member = make_member("Remover")
    reg = make_registration(member["id"], "2026", "U16", "Complete")
    team = make_team("2026", "Tigers", "U16")
    services.add_player_to_team(team["id"], member["id"])

    services.remove_player_from_team(team["id"], member["id"])

    assert services.get_registration(reg["id"]) is not None
    assert services.get_registration(reg["id"])["status"] == "Complete"


def test_move_to_wrong_season_rejected(make_member, make_registration, make_team):
    member = make_member("Season Mover")
    make_registration(member["id"], "2026", "U16", "Complete")
    team_a = make_team("2026", "Tigers", "U16")
    team_b = make_team("2025", "Eagles", "U14")
    services.add_player_to_team(team_a["id"], member["id"])

    with pytest.raises(services.ServiceError):
        services.move_player(member["id"], team_a["id"], team_b["id"])

    # The player stays in team A.
    assert [p["name"] for p in services.team_players(team_a["id"])] == ["Season Mover"]


def test_withdrawn_registration_not_eligible_for_team(make_member, make_registration, make_team):
    """A withdrawn registration does not make a player eligible for a team."""
    member = make_member("Withdrawn Player")
    reg = make_registration(member["id"], "2026", "U16", "Started")
    services.withdraw_registration(reg["id"])
    team = make_team("2026", "Tigers", "U16")

    with pytest.raises(services.ServiceError):
        services.add_player_to_team(team["id"], member["id"])

    assert services.team_players(team["id"]) == []


def test_move_player_to_nonexistent_team_rejected(make_member, make_registration, make_team):
    member = make_member("Move Ghost")
    make_registration(member["id"], "2026", "U16", "Complete")
    team_a = make_team("2026", "Tigers", "U16")
    services.add_player_to_team(team_a["id"], member["id"])

    with pytest.raises(services.ServiceError):
        services.move_player(member["id"], team_a["id"], 99999)

    assert [p["name"] for p in services.team_players(team_a["id"])] == ["Move Ghost"]


def test_move_player_already_in_target_team_rejected(make_member, make_registration, make_team):
    member = make_member("Dual Team")
    make_registration(member["id"], "2026", "U16", "Complete")
    team_a = make_team("2026", "Tigers", "U16")
    team_b = make_team("2026", "Eagles", "U16")
    services.add_player_to_team(team_a["id"], member["id"])
    services.add_player_to_team(team_b["id"], member["id"])

    with pytest.raises(services.ServiceError):
        services.move_player(member["id"], team_a["id"], team_b["id"])
