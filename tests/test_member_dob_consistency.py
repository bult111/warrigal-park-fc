"""Date-of-birth change consistency tests.

Changing a member's date of birth can change the age group of their existing
registrations. ``services.update_member`` re-checks every affected registration
before writing anything, and applies the member row together with every
registration age group in a single transaction, so a rejected or failing change
never leaves partial state.
"""

from contextlib import contextmanager
from datetime import date

import pytest

from app import database, services

SEASON = "2026"
SEASON_YEAR = 2026


def dob_for(season_age):
    """A date of birth that yields ``season_age`` in ``SEASON``."""
    return date(SEASON_YEAR - season_age, 1, 1).isoformat()


def _team_rows(member_id):
    """Return the ``(team_id,)`` rows a member is assigned to, ordered by id."""
    return database.query_all(
        "SELECT team_id FROM team_players WHERE member_id = ? ORDER BY team_id",
        (member_id,),
    )


def test_dob_change_updates_registration_age_group(make_member, make_registration):
    """A DOB change rewrites the stored age group of the affected registration."""
    member = make_member("Dob One", dob=dob_for(20))
    registration = make_registration(member["id"], SEASON, status="Started")
    assert registration["age_group"] == "Seniors"

    services.update_member(member["id"], "Dob One", dob_for(16), "", "", "")

    assert services.get_member(member["id"])["date_of_birth"] == dob_for(16)
    assert services.get_registration(registration["id"])["age_group"] == "U18"


def test_dob_change_recomputes_each_registration_for_its_own_season(
    make_member, make_registration
):
    """Each registration is recomputed against its own season, not one season."""
    member = make_member("Dob Two", dob=dob_for(20))
    first = make_registration(member["id"], "2026", status="Started")
    second = make_registration(member["id"], "2027", status="Started")

    services.update_member(member["id"], "Dob Two", dob_for(15), "", "", "")

    # Season age 15 in 2026 -> U16, and 16 in 2027 -> U18.
    assert services.get_registration(first["id"])["age_group"] == "U16"
    assert services.get_registration(second["id"])["age_group"] == "U18"


def test_dob_change_that_breaks_a_team_assignment_is_rejected(
    make_member, make_guardian, link_guardian, make_registration, make_team
):
    """A change that leaves an assignment mismatched is refused wholesale."""
    member = make_member("Dob Three", dob=dob_for(14))  # U16 in 2026
    guardian = make_guardian("Guardian Three")
    link_guardian(guardian["id"], member["id"])
    team = make_team(SEASON, "U16 Team", "U16")
    registration = make_registration(member["id"], SEASON, status="Complete")
    assert [p["member_id"] for p in services.team_players(team["id"])] == [member["id"]]

    with pytest.raises(services.ServiceError):
        services.update_member(member["id"], "Dob Three", dob_for(16), "", "", "")

    assert services.get_member(member["id"])["date_of_birth"] == dob_for(14)
    stored = services.get_registration(registration["id"])
    assert (stored["id"], stored["season"], stored["age_group"], stored["status"]) == (
        registration["id"],
        SEASON,
        "U16",
        "Complete",
    )
    assert [dict(row) for row in _team_rows(member["id"])] == [{"team_id": team["id"]}]


def test_one_incompatible_registration_rejects_the_whole_change(
    make_member, make_guardian, link_guardian, make_registration, make_team
):
    """When only one registration conflicts, no registration is updated."""
    member = make_member("Dob Four", dob=dob_for(14))
    guardian = make_guardian("Guardian Four")
    link_guardian(guardian["id"], member["id"])
    make_team(SEASON, "U16 Team", "U16")
    assigned = make_registration(member["id"], SEASON, status="Complete")
    other = make_registration(member["id"], "2027", status="Complete")
    assigned_before = services.get_registration(assigned["id"])["age_group"]
    other_before = services.get_registration(other["id"])["age_group"]

    with pytest.raises(services.ServiceError):
        services.update_member(member["id"], "Dob Four", dob_for(16), "", "", "")

    assert services.get_member(member["id"])["date_of_birth"] == dob_for(14)
    assert services.get_registration(assigned["id"])["age_group"] == assigned_before
    assert services.get_registration(other["id"])["age_group"] == other_before


def test_dob_change_below_the_minimum_age_is_rejected(make_member, make_registration):
    """A DOB that puts a registration below the minimum age stores nothing."""
    member = make_member("Dob Five", dob=dob_for(20))
    registration = make_registration(member["id"], SEASON, status="Started")

    with pytest.raises(services.ServiceError):
        services.update_member(member["id"], "Dob Five", dob_for(2), "", "", "")

    assert services.get_member(member["id"])["date_of_birth"] == dob_for(20)
    assert services.get_registration(registration["id"])["age_group"] == "Seniors"


def test_junior_complete_after_dob_change_needs_a_verified_adult_guardian(
    make_member, make_guardian, link_guardian, make_registration
):
    """A DOB change to a junior with a Complete registration needs an adult."""
    member = make_member("Dob Six", dob=dob_for(20))
    registration = make_registration(member["id"], SEASON, status="Complete")

    with pytest.raises(services.ServiceError):
        services.update_member(member["id"], "Dob Six", dob_for(16), "", "", "")

    assert services.get_member(member["id"])["date_of_birth"] == dob_for(20)
    assert services.get_registration(registration["id"])["age_group"] == "Seniors"

    guardian = make_guardian("Guardian Six")
    link_guardian(guardian["id"], member["id"])

    services.update_member(member["id"], "Dob Six", dob_for(16), "", "", "")

    assert services.get_member(member["id"])["date_of_birth"] == dob_for(16)
    assert services.get_registration(registration["id"])["age_group"] == "U18"


def test_midwrite_failure_rolls_back_the_whole_change(
    app, monkeypatch, make_member, make_registration
):
    """A failure on the second write leaves neither change applied."""
    member = make_member("Dob Seven", dob=dob_for(20))
    registration = make_registration(member["id"], SEASON, status="Started")
    original_dob = member["date_of_birth"]
    original_group = registration["age_group"]

    real = database.get_db()

    class _FlakyConnection:
        """Delegates to the real connection but fails on the second write."""

        def __init__(self):
            self.calls = 0

        def execute(self, sql, params=()):
            self.calls += 1
            if self.calls == 2:
                raise RuntimeError("simulated failure on the second write")
            return real.execute(sql, params)

    @contextmanager
    def _flaky_transaction():
        proxy = _FlakyConnection()
        try:
            yield proxy
            real.commit()
        except Exception:
            real.rollback()
            raise

    monkeypatch.setattr(database, "transaction", _flaky_transaction)

    with pytest.raises(RuntimeError):
        services.update_member(member["id"], "Dob Seven", dob_for(16), "", "", "")

    # The member write that succeeded before the failure must be rolled back too.
    assert services.get_member(member["id"])["date_of_birth"] == original_dob
    assert services.get_registration(registration["id"])["age_group"] == original_group
