"""Validation and error-handling tests.

These tests assert that normal user mistakes raise :class:`ServiceError` (or
``ValueError``) with a friendly message instead of crashing with a traceback.
"""

import pytest

from app import services


def test_missing_name_rejected():
    with pytest.raises(ValueError):
        services.create_member("", "2010-01-01", "", "", "")


def test_invalid_date_of_birth_rejected():
    with pytest.raises(ValueError):
        services.create_member("Bad Date", "not-a-date", "", "", "")


def test_future_date_of_birth_rejected():
    with pytest.raises(ValueError):
        services.create_member("Future Person", "2999-01-01", "", "", "")


def test_invalid_email_rejected():
    with pytest.raises(ValueError):
        services.create_member("Bad Email", "2010-01-01", "not-an-email", "", "")


def test_nonexistent_member_registration_rejected(make_registration):
    with pytest.raises(services.ServiceError):
        make_registration(99999, "2026", "U16")


def test_nonexistent_guardian_link_rejected(make_member):
    member = make_member("Someone")
    with pytest.raises(services.ServiceError):
        services.link_guardian_member(99999, member["id"])


def test_nonexistent_member_link_rejected(make_guardian):
    guardian = make_guardian("Guardian")
    with pytest.raises(services.ServiceError):
        services.link_guardian_member(guardian["id"], 99999)


def test_nonexistent_team_add_player_rejected(make_member):
    member = make_member("Someone")
    with pytest.raises(services.ServiceError):
        services.add_player_to_team(99999, member["id"])


def test_invalid_registration_status_rejected(make_member, make_registration):
    member = make_member("Someone")
    with pytest.raises(services.ServiceError):
        make_registration(member["id"], "2026", "U16", "NotAStatus")


def test_duplicate_guardian_link_rejected(make_member, make_guardian, link_guardian):
    member = make_member("Someone")
    guardian = make_guardian("Guardian")
    link_guardian(guardian["id"], member["id"])
    with pytest.raises(services.ServiceError):
        services.link_guardian_member(guardian["id"], member["id"])


def test_duplicate_team_player_rejected(make_member, make_registration, make_team):
    member = make_member("Someone")
    make_registration(member["id"], "2026", "U16", "Complete")
    team = make_team("2026", "Tigers", "U16")

    services.add_player_to_team(team["id"], member["id"])
    with pytest.raises(services.ServiceError):
        services.add_player_to_team(team["id"], member["id"])
