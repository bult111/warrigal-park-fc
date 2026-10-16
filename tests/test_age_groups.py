"""Age-group calculation tests.

The age group is the course project's own rule (not an official Football
Australia regulation): the season age is ``season_year - birth_year`` and maps
onto a fixed group list. These tests call ``app.models.get_age_group`` directly
and check how the service layer stores and recomputes the value.
"""

from datetime import date

import pytest

from app import database, models, services

SEASON = 2026


def _dob_for_season_age(season_age, season=SEASON):
    """Return a date of birth whose season age in ``season`` is ``season_age``."""
    return date(season - season_age, 6, 15)


@pytest.mark.parametrize(
    "season_age, expected",
    [
        (4, "U6"),
        (5, "U6"),
        (6, "U8"),
        (7, "U8"),
        (8, "U10"),
        (9, "U10"),
        (10, "U12"),
        (11, "U12"),
        (12, "U14"),
        (13, "U14"),
        (14, "U16"),
        (15, "U16"),
        (16, "U18"),
        (17, "U18"),
        (18, "Seniors"),
        (19, "Seniors"),
        (30, "Seniors"),
    ],
)
def test_get_age_group_maps_season_age_to_group(season_age, expected):
    dob = _dob_for_season_age(season_age)
    assert models.get_age_group(dob, str(SEASON)) == expected


def test_get_age_group_accepts_an_iso_dob_string():
    dob = _dob_for_season_age(14)  # U16 in 2026
    assert models.get_age_group(dob.isoformat(), str(SEASON)) == "U16"


def test_same_dob_differs_by_season():
    dob = date(2010, 6, 15)
    assert models.get_age_group(dob, "2024") == "U16"  # season age 14
    assert models.get_age_group(dob, "2026") == "U18"  # season age 16
    assert models.get_age_group(dob, "2028") == "Seniors"  # season age 18


@pytest.mark.parametrize("season", [None, "", "   ", "26", "20255", "abcd", "20a6"])
def test_get_age_group_rejects_invalid_season(season):
    with pytest.raises(ValueError):
        models.get_age_group(date(2010, 6, 15), season)


@pytest.mark.parametrize(
    "dob", ["", "not-a-date", "2020/01/01", "2020-13-01", "2020-02-30"]
)
def test_get_age_group_rejects_unparseable_dob(dob):
    with pytest.raises(ValueError):
        models.get_age_group(dob, str(SEASON))


def test_get_age_group_rejects_below_minimum_age():
    dob = _dob_for_season_age(3)  # season age 3, below the U6 minimum of 4
    with pytest.raises(ValueError) as exc_info:
        models.get_age_group(dob, str(SEASON))
    assert "at least 4" in str(exc_info.value)


def test_create_registration_stores_the_computed_age_group(make_member):
    dob = _dob_for_season_age(16)  # U18 in 2026
    member = make_member("Submitted Wrong Group", dob=dob.isoformat())

    # The age_group the caller submits is ignored; the stored value is computed.
    registration = services.create_registration(
        member["id"], str(SEASON), age_group="U6", status="Started"
    )

    assert registration["age_group"] == models.get_age_group(dob, str(SEASON))
    assert registration["age_group"] == "U18"


def test_update_registration_recomputes_age_group_for_new_season(make_member):
    dob = date(2010, 6, 15)
    member = make_member("Season Changer", dob=dob.isoformat())
    registration = services.create_registration(member["id"], "2024", status="Started")
    assert registration["age_group"] == "U16"  # season age 14

    amended = services.update_registration(
        registration["id"], member["id"], "2026", status="Started"
    )

    assert amended["season"] == "2026"
    assert amended["age_group"] == "U18"  # season age 16
    assert services.get_registration(registration["id"])["age_group"] == "U18"


def test_create_registration_rejects_unreadable_stored_dob(make_member):
    member = make_member("Bad Stored Dob")
    # Simulate a legacy/corrupt stored value that is not a readable date.
    database.execute(
        "UPDATE members SET date_of_birth = ? WHERE id = ?",
        ("not-a-date", member["id"]),
    )

    with pytest.raises(services.ServiceError):
        services.create_registration(member["id"], str(SEASON), status="Started")
