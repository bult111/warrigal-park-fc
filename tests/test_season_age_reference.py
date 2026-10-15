"""The under-18 guardian rule is measured at the season reference date.

Why this file exists
--------------------
The rule used to be implemented as ``calculate_age(dob) < JUNIOR_AGE_LIMIT``, and
``calculate_age`` defaults its reference point to ``date.today()``. Measuring a
season-long rule against "today" means the rule's answer changes part-way through the
season for any player whose 18th birthday falls inside it, so the same database gives
different answers on different days.

The association determines age groups by the player's age as at 31 December of the
playing year (club circular 2026/03, item 2), so the club's own under-18 rule is measured
at the same point. The case study plants this exact boundary on purpose, in the margin
note on the circular:

    "Jayden Marsh is 17 now and turns 18 on 4 May, and he's playing seniors this year.
     Does he need Section B or not? Asked NFA 20/1 - no answer yet. V.O."

A player born 4 May 2008 turns 18 on 4 May 2026. Under the season reference date that
birthday falls inside the season, so he is 18 for the whole of the 2026 season and does
not need a guardian. Under the old implementation his answer flipped on his birthday.
"""

from datetime import date

import pytest

from app import models, services


def _frozen_today(day):
    """Return a ``date`` subclass whose ``today()`` is fixed, for monkeypatching."""

    class _Frozen(date):
        @classmethod
        def today(cls):
            return day

    return _Frozen


# The case study's own boundary case: 18th birthday inside the 2026 season.
MID_SEASON_BIRTHDAY_DOB = "2008-05-04"


# --- The reference date itself -----------------------------------------------------------


def test_season_reference_date_is_the_last_day_of_the_playing_year():
    assert models.season_reference_date("2026") == date(2026, 12, 31)
    assert models.season_reference_date(2026) == date(2026, 12, 31)


@pytest.mark.parametrize(
    "season, expected",
    [
        ("2026", 2026),
        (2026, 2026),
        ("2026 Season", 2026),
        ("Season 2027", 2027),
        ("U16 2025", 2025),
        ("", date.today().year),
        (None, date.today().year),
        ("no year here", date.today().year),
    ],
)
def test_season_year_reads_a_year_from_common_spellings(season, expected):
    assert models.season_year(season) == expected


# --- The boundary at the reference date --------------------------------------------------


def test_exactly_18_at_the_reference_is_an_adult():
    dob = date(2008, 12, 31)  # 18 on 31 December 2026, the reference date itself
    assert models.is_junior(dob, models.season_reference_date("2026")) is False


def test_one_day_younger_at_the_reference_is_a_junior():
    dob = date(2009, 1, 1)  # 17 on 31 December 2026
    assert models.is_junior(dob, models.season_reference_date("2026")) is True


# --- The defect: the answer must not move during a season --------------------------------


def test_a_mid_season_birthday_does_not_change_the_rule_during_the_season(
    app, monkeypatch, make_member
):
    """The regression test for the defect this change fixes.

    The member has no guardian. Whether the registration may be completed must not depend
    on which day of the season the code happens to run on.
    """
    member = make_member("Mid Season Birthday", dob=MID_SEASON_BIRTHDAY_DOB)

    answers = set()
    for day in (
        date(2026, 1, 1),
        date(2026, 5, 3),   # the day before his 18th birthday
        date(2026, 5, 4),   # his 18th birthday
        date(2026, 5, 5),
        date(2026, 12, 31),
    ):
        monkeypatch.setattr(models, "date", _frozen_today(day))
        allowed, _message = services.can_complete_registration(member["id"], "2026")
        answers.add(allowed)

    assert answers == {True}, (
        "the rule gave different answers on different days of the same season: %r" % answers
    )


def test_the_same_player_is_a_junior_in_an_earlier_season(
    app, monkeypatch, make_member
):
    """The mirror of the test above, and the proof that the season is what decides.

    The same member, the same database, a different season: in 2025 he was 17 on the
    reference date, so the guardian rule applies and the registration is refused.
    """
    member = make_member("Mid Season Birthday", dob=MID_SEASON_BIRTHDAY_DOB)

    for day in (date(2025, 6, 1), date(2026, 6, 1), date(2030, 1, 1)):
        monkeypatch.setattr(models, "date", _frozen_today(day))
        allowed, message = services.can_complete_registration(member["id"], "2025")
        assert allowed is False, "expected a refusal for the 2025 season on %s" % day
        assert message == services.JUNIOR_GUARDIAN_REQUIRED_MESSAGE


def test_the_season_decides_not_the_calendar(app, monkeypatch, make_member):
    """One member, one database, two seasons, two answers."""
    member = make_member("Mid Season Birthday", dob=MID_SEASON_BIRTHDAY_DOB)
    monkeypatch.setattr(models, "date", _frozen_today(date(2026, 7, 1)))

    assert services.can_complete_registration(member["id"], "2025")[0] is False
    assert services.can_complete_registration(member["id"], "2026")[0] is True


# --- The rule still behaves for the ordinary cases ---------------------------------------


def test_a_linked_guardian_satisfies_the_rule_for_a_junior(
    app, monkeypatch, make_member, make_guardian, link_guardian
):
    member = make_member("Junior With Guardian", dob=MID_SEASON_BIRTHDAY_DOB)
    guardian = make_guardian("Parent")
    link_guardian(guardian["id"], member["id"])
    monkeypatch.setattr(models, "date", _frozen_today(date(2026, 7, 1)))

    allowed, message = services.can_complete_registration(member["id"], "2025")
    assert allowed is True, message


def test_completing_without_a_season_uses_the_current_year(make_member):
    """Callers that do not pass a season keep working."""
    member = make_member(
        "Current Year Junior", dob=date(date.today().year - 10, 1, 1).isoformat()
    )
    allowed, message = services.can_complete_registration(member["id"])
    assert allowed is False
    assert message == services.JUNIOR_GUARDIAN_REQUIRED_MESSAGE


def test_an_unknown_member_is_still_reported():
    allowed, message = services.can_complete_registration(999_999, "2026")
    assert allowed is False
    assert message == "Member not found."
