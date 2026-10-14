"""Additional edge-case regression tests added during Sprint 1 QA.

These fill small gaps in the original suite: unhappy paths and boundary
behaviours that were not explicitly asserted before. Every assertion matches
the current, intentional behaviour of the service layer.
"""

import pytest

from app import services


def test_set_member_status_invalid_rejected():
    with pytest.raises(services.ServiceError) as exc_info:
        services.set_member_status(1, "Bogus")
    assert "Invalid member status" in str(exc_info.value)


def test_withdraw_nonexistent_registration_rejected():
    with pytest.raises(services.ServiceError):
        services.withdraw_registration(99999)


def test_update_nonexistent_registration_rejected():
    with pytest.raises(services.ServiceError):
        services.update_registration(99999, 1, "2026", "U16", "Started")


def test_move_player_same_team_rejected():
    with pytest.raises(services.ServiceError):
        services.move_player(1, 5, 5)


def test_remove_player_nonexistent_team_rejected():
    with pytest.raises(services.ServiceError):
        services.remove_player_from_team(99999, 1)


def test_add_player_nonexistent_member_rejected(make_team):
    team = make_team("2026", "Tigers", "U16")
    with pytest.raises(services.ServiceError) as exc_info:
        services.add_player_to_team(team["id"], 99999)
    assert "Member not found" in str(exc_info.value)


def test_can_complete_registration_nonexistent_member():
    allowed, message = services.can_complete_registration(99999)
    assert allowed is False
    assert "Member not found" in message


def test_get_member_none():
    assert services.get_member(99999) is None


def test_get_guardian_none():
    assert services.get_guardian(99999) is None


def test_get_team_none():
    assert services.get_team(99999) is None


def test_get_registration_none():
    assert services.get_registration(99999) is None
