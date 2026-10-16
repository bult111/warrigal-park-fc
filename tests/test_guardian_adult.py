"""Guardian date-of-birth and adult-verification tests.

A guardian must record a date of birth that verifies them as an adult (18 or
over) before they can be linked and count towards the junior completion rule.
Legacy guardians (no date of birth) remain valid rows but do not satisfy it, and
the migration that adds the column is idempotent and preserves existing data.
"""

import sqlite3
from datetime import date, timedelta

import pytest

from app import database, services


def _years_ago(years):
    """Return a date exactly ``years`` ago, safe against Feb 29 birthdays."""
    today = date.today()
    try:
        return today.replace(year=today.year - years)
    except ValueError:
        return date(today.year - years, 2, 28)


# ---------------------------------------------------------------------------
# Guardian date of birth
# ---------------------------------------------------------------------------

def test_create_guardian_with_adult_dob(make_guardian):
    guardian = make_guardian("Adult Guardian", dob="1980-01-01")

    assert guardian["id"] is not None
    assert guardian["date_of_birth"] == "1980-01-01"
    assert guardian["age"] >= 18
    assert guardian["is_adult"] is True


def test_guardian_turning_18_today_is_accepted():
    guardian = services.create_guardian(
        "Birthday Today", _years_ago(18).isoformat(), "", "", ""
    )
    assert guardian["age"] == 18
    assert guardian["is_adult"] is True


def test_guardian_one_day_before_18_is_rejected():
    dob = (_years_ago(18) + timedelta(days=1)).isoformat()  # 18th birthday tomorrow

    with pytest.raises(ValueError) as exc_info:
        services.create_guardian("Almost Adult", dob, "", "", "")

    assert "18" in str(exc_info.value)
    assert services.list_guardians() == []


@pytest.mark.parametrize(
    "dob", [None, "", "   ", "not-a-date", "01/02/2000", "2999-01-01", "1800-01-01"]
)
def test_invalid_guardian_dob_is_rejected(dob):
    with pytest.raises(ValueError):
        services.create_guardian("Bad Dob", dob, "", "", "")
    assert services.list_guardians() == []


def test_update_guardian_revalidates_dob(make_guardian):
    guardian = make_guardian("Update Me", dob="1980-01-01")

    updated = services.update_guardian(
        guardian["id"], "Update Me", "1990-01-01", "u@example.com", "0400 111 222", "1 Rd"
    )
    assert updated["date_of_birth"] == "1990-01-01"
    assert updated["email"] == "u@example.com"

    for bad in ["not-a-date", _years_ago(10).isoformat(), "2999-01-01", ""]:
        with pytest.raises(ValueError):
            services.update_guardian(guardian["id"], "Update Me", bad, "", "", "")

    # Rejected updates leave the stored record unchanged.
    stored = services.get_guardian(guardian["id"])
    assert stored["date_of_birth"] == "1990-01-01"
    assert stored["email"] == "u@example.com"


# ---------------------------------------------------------------------------
# Adult verification and the junior completion rule
# ---------------------------------------------------------------------------

def test_junior_can_complete_with_verified_adult_guardian(
    make_member, make_guardian, link_guardian
):
    junior = make_member("Junior", dob=_years_ago(10).isoformat())
    guardian = make_guardian("Adult Guardian")
    link_guardian(guardian["id"], junior["id"])

    allowed, message = services.can_complete_registration(junior["id"])
    assert allowed is True
    assert message == ""

    registration = services.create_registration(junior["id"], "2026", status="Complete")
    assert registration["status"] == "Complete"


def test_junior_cannot_complete_without_guardian(make_member):
    junior = make_member("Junior", dob=_years_ago(10).isoformat())

    allowed, message = services.can_complete_registration(junior["id"])
    assert allowed is False
    assert "guardian" in message.lower()

    with pytest.raises(services.ServiceError):
        services.create_registration(junior["id"], "2026", status="Complete")


def test_link_refuses_guardian_who_is_under_18(make_member):
    # create_guardian refuses an under-18 date of birth, so insert the row
    # directly to model a guardian record that is not a verified adult.
    db = database.get_db()
    cursor = db.execute(
        "INSERT INTO guardians (name, date_of_birth) VALUES (?, ?)",
        ("Underage Guardian", _years_ago(15).isoformat()),
    )
    db.commit()
    guardian_id = cursor.lastrowid

    junior = make_member("Junior", dob=_years_ago(10).isoformat())

    with pytest.raises(services.ServiceError):
        services.link_guardian_member(guardian_id, junior["id"])

    assert services.member_guardians(junior["id"]) == []


def test_legacy_guardian_without_dob_does_not_satisfy_rule(make_member):
    # A legacy guardian row that predates the date_of_birth column.
    db = database.get_db()
    cursor = db.execute(
        "INSERT INTO guardians (name, date_of_birth) VALUES (?, NULL)",
        ("Legacy Guardian",),
    )
    db.commit()
    guardian_id = cursor.lastrowid

    junior = make_member("Junior", dob=_years_ago(10).isoformat())
    db.execute(
        "INSERT INTO guardian_members (guardian_id, member_id) VALUES (?, ?)",
        (guardian_id, junior["id"]),
    )
    db.commit()

    # The link row exists, but the guardian is not verified as an adult.
    assert services.member_has_guardian(junior["id"]) is True
    assert services.member_has_adult_guardian(junior["id"]) is False

    allowed, message = services.can_complete_registration(junior["id"])
    assert allowed is False
    assert "guardian" in message.lower()

    with pytest.raises(services.ServiceError):
        services.create_registration(junior["id"], "2026", status="Complete")


def test_adult_member_does_not_require_a_guardian(make_member, make_registration):
    adult = make_member("Adult Member")  # the fixture default DOB is an adult

    allowed, message = services.can_complete_registration(adult["id"])
    assert allowed is True
    assert message == ""

    registration = make_registration(adult["id"], "2026", status="Complete")
    assert registration["status"] == "Complete"


def test_member_turning_18_today_does_not_require_a_guardian(
    make_member, make_registration
):
    adult = make_member("Birthday Today", dob=_years_ago(18).isoformat())

    allowed, _ = services.can_complete_registration(adult["id"])
    assert allowed is True

    registration = make_registration(adult["id"], "2026", status="Complete")
    assert registration["status"] == "Complete"


# ---------------------------------------------------------------------------
# Migration adding guardians.date_of_birth
# ---------------------------------------------------------------------------

def test_migration_adds_guardian_dob_and_preserves_rows(tmp_path):
    path = tmp_path / "legacy.db"
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    conn.executescript(
        """
        CREATE TABLE members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            date_of_birth TEXT NOT NULL,
            email TEXT NOT NULL DEFAULT '',
            phone TEXT NOT NULL DEFAULT '',
            address TEXT NOT NULL DEFAULT '',
            status TEXT NOT NULL DEFAULT 'Active'
        );
        CREATE TABLE guardians (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL DEFAULT '',
            phone TEXT NOT NULL DEFAULT '',
            address TEXT NOT NULL DEFAULT ''
        );
        CREATE TABLE guardian_members (
            guardian_id INTEGER NOT NULL,
            member_id INTEGER NOT NULL,
            PRIMARY KEY (guardian_id, member_id)
        );
        """
    )
    conn.execute(
        "INSERT INTO members (name, date_of_birth) VALUES ('Legacy Junior', '2016-05-05')"
    )
    conn.execute(
        "INSERT INTO guardians (name, email, phone, address) "
        "VALUES ('Legacy Guardian', 'legacy@example.com', '0400 000 000', '1 Old Rd')"
    )
    conn.execute("INSERT INTO guardian_members (guardian_id, member_id) VALUES (1, 1)")
    conn.commit()

    database._migrate(conn)
    database._migrate(conn)  # idempotent: a second run must not fail

    columns = {row["name"] for row in conn.execute("PRAGMA table_info(guardians)")}
    assert "date_of_birth" in columns

    guardian = conn.execute("SELECT * FROM guardians WHERE id = 1").fetchone()
    assert guardian["name"] == "Legacy Guardian"
    assert guardian["email"] == "legacy@example.com"
    assert guardian["phone"] == "0400 000 000"
    assert guardian["address"] == "1 Old Rd"
    assert guardian["date_of_birth"] is None

    link = conn.execute(
        "SELECT * FROM guardian_members WHERE guardian_id = 1 AND member_id = 1"
    ).fetchone()
    assert link is not None
    conn.close()


def test_init_db_twice_keeps_the_guardian_dob_column(app):
    database.init_db()
    database.init_db()

    columns = {
        row["name"] for row in database.query_all("PRAGMA table_info(guardians)")
    }
    assert "date_of_birth" in columns
