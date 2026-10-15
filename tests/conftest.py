"""Shared pytest fixtures for the Warrigal Park FC test suite.

Every test runs against a fresh, isolated SQLite database in a temporary
directory so tests are repeatable and never touch real data.
"""

from datetime import date

import pytest

from app import create_app, database, models, services

# The season the age-boundary fixtures are calibrated against.
#
# These fixtures used to be defined relative to `date.today()` ("18 years ago today"),
# which only describes a boundary case if the rule is also measured against today. The
# under-18 guardian rule is measured at the season reference date - 31 December of the
# playing year - so the fixtures are anchored there instead. A fixture anchored to today
# describes a different player on every day of the year.
SEASON = "2026"
_REFERENCE = models.season_reference_date(SEASON)


def _years_ago(years):
    """Return a date exactly ``years`` ago, safe against Feb 29 birthdays."""
    today = date.today()
    try:
        return today.replace(year=today.year - years)
    except ValueError:
        # Feb 29 mapped onto a non-leap year.
        return date(today.year - years, 2, 28)


@pytest.fixture
def app(tmp_path):
    """A configured Flask app backed by a temporary SQLite database."""
    app = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-secret",
            "DATABASE": str(tmp_path / "test.db"),
        }
    )
    with app.app_context():
        database.init_db()
    yield app


@pytest.fixture
def client(app):
    """A Flask test client."""
    return app.test_client()


@pytest.fixture(autouse=True)
def app_context(app):
    """Keep an application context active so service calls work in tests."""
    with app.app_context():
        yield


@pytest.fixture
def junior_dob():
    """A date of birth that makes a member clearly under 18."""
    return _years_ago(10).isoformat()


@pytest.fixture
def adult_dob():
    """A date of birth that makes a member clearly 18 or over."""
    return _years_ago(30).isoformat()


@pytest.fixture
def exactly_18_dob():
    """A date of birth making a member exactly 18 at the season reference date.

    The season reference is the last day of the playing year, so the latest birth date
    that is already an adult for the season is that same day, 18 years earlier.
    """
    return date(_REFERENCE.year - models.JUNIOR_AGE_LIMIT, 12, 31).isoformat()


@pytest.fixture
def just_under_18_dob():
    """A date of birth making a member 17 at the season reference date.

    Exactly one day after ``exactly_18_dob``: the birthday that would make them an adult
    falls after the season reference, so they are a junior for the whole season.
    """
    return date(_REFERENCE.year - models.JUNIOR_AGE_LIMIT + 1, 1, 1).isoformat()


@pytest.fixture
def make_member(app):
    """Factory that creates a member and returns its dict."""
    def _make(name="John Smith", dob=None, email="", phone="", address=""):
        dob = dob or _years_ago(20).isoformat()
        with app.app_context():
            return services.create_member(name, dob, email, phone, address)

    return _make


@pytest.fixture
def make_guardian(app):
    """Factory that creates a guardian and returns its dict."""
    def _make(name="Jane Guardian", email="", phone="", address=""):
        with app.app_context():
            return services.create_guardian(name, email, phone, address)

    return _make


@pytest.fixture
def make_registration(app):
    """Factory that creates a registration and returns its dict."""
    def _make(member_id, season="2026", age_group="U16", status="Started"):
        with app.app_context():
            return services.create_registration(member_id, season, age_group, status)

    return _make


@pytest.fixture
def make_team(app):
    """Factory that creates a team and returns its dict."""
    def _make(season="2026", name="Tigers", age_group="U16"):
        with app.app_context():
            return services.create_team(season, name, age_group)

    return _make


@pytest.fixture
def link_guardian(app):
    """Factory that links a guardian to a member."""
    def _link(guardian_id, member_id):
        with app.app_context():
            services.link_guardian_member(guardian_id, member_id)

    return _link
