"""Team management tests."""

import pytest

from app import services


def test_create_team(make_team):
    team = make_team("2026", "Tigers", "U16")
    assert team["id"] is not None
    assert team["name"] == "Tigers"
    assert team["season"] == "2026"
    assert team["age_group"] == "U16"


def test_list_teams(make_team):
    make_team("2026", "Tigers", "U16")
    make_team("2026", "Eagles", "U14")
    teams = services.list_teams()
    assert len(teams) == 2
    assert {t["name"] for t in teams} == {"Tigers", "Eagles"}


def test_rename_team(make_team):
    team = make_team("2026", "Tigers", "U16")
    renamed = services.rename_team(team["id"], "2026", "Panthers", "U16")
    assert renamed["name"] == "Panthers"


def test_remove_team(make_team):
    team = make_team("2026", "Tigers", "U16")
    services.delete_team(team["id"])
    assert services.get_team(team["id"]) is None


def test_member_remains_after_team_removal(make_member, make_registration, make_team):
    member = make_member("Keep Me")
    make_registration(member["id"], "2026", "U16", "Complete")
    team = make_team("2026", "Tigers", "U16")
    services.add_player_to_team(team["id"], member["id"])

    services.delete_team(team["id"])

    # The member still exists after the team is removed.
    assert services.get_member(member["id"]) is not None


def test_registration_remains_after_team_removal(make_member, make_registration, make_team):
    member = make_member("Keep Me")
    reg = make_registration(member["id"], "2026", "U16", "Complete")
    team = make_team("2026", "Tigers", "U16")
    services.add_player_to_team(team["id"], member["id"])

    services.delete_team(team["id"])

    # The registration still exists after the team is removed.
    assert services.get_registration(reg["id"]) is not None


def test_remove_nonexistent_team_rejected():
    with pytest.raises(services.ServiceError):
        services.delete_team(99999)
