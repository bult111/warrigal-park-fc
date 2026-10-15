"""Data structures and validation helpers for Warrigal Park FC.

This module holds the small amount of shared "model" logic that is not tied to
the database connection itself: status constants, field validation, the age
calculation used by the under-18 guardian rule, and ``sqlite3.Row`` -> ``dict``
mappers used by the templates.
"""

import re
from datetime import date

MEMBER_STATUS_ACTIVE = "Active"
MEMBER_STATUS_INACTIVE = "Inactive"
MEMBER_STATUSES = (MEMBER_STATUS_ACTIVE, MEMBER_STATUS_INACTIVE)

REGISTRATION_STATUS_STARTED = "Started"
REGISTRATION_STATUS_COMPLETE = "Complete"
REGISTRATION_STATUS_WITHDRAWN = "Withdrawn"
REGISTRATION_STATUSES = (
    REGISTRATION_STATUS_STARTED,
    REGISTRATION_STATUS_COMPLETE,
    REGISTRATION_STATUS_WITHDRAWN,
)

# The age threshold used by the under-18 guardian rule.
JUNIOR_AGE_LIMIT = 18

# The point in the year at which a player's age is measured for a season.
#
# The association determines age groups by the player's age as at 31 December of the
# playing year (club circular 2026/03, item 2). The club's under-18 guardian rule is a
# season-long rule, so it is measured at the same point: a rule that gave a different
# answer on different days of the same season would not be a season rule at all.
SEASON_REFERENCE_MONTH = 12
SEASON_REFERENCE_DAY = 31

# A sensible upper bound used to reject obviously incorrect birth dates.
MAX_REASONABLE_AGE = 130

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def calculate_age(dob: date, today: date | None = None) -> int:
    """Return the age in whole years for ``dob`` as of ``today`` (or now)."""
    today = today or date.today()
    years = today.year - dob.year
    if (today.month, today.day) < (dob.month, dob.day):
        years -= 1
    return years


def season_year(season) -> int:
    """Return the year a season belongs to.

    ``season`` may be a year (``2026``), a string containing one (``"2026"``,
    ``"2026 Season"``), or a season code. Anything without a four-digit year falls back
    to the current year, so callers never have to guard against a missing season.
    """
    match = re.search(r"\d{4}", str(season if season is not None else ""))
    return int(match.group(0)) if match else date.today().year


def season_reference_date(season=None) -> date:
    """Return the date at which a player's age is measured for ``season``.

    See ``SEASON_REFERENCE_MONTH`` above for why the rule is measured at a fixed point
    rather than at the date the code happens to run.
    """
    return date(season_year(season), SEASON_REFERENCE_MONTH, SEASON_REFERENCE_DAY)


def is_junior(dob: date, on: date) -> bool:
    """Return whether a player born on ``dob`` is under the junior age limit on ``on``."""
    return calculate_age(dob, on) < JUNIOR_AGE_LIMIT


def parse_date(value):
    """Parse an ISO ``YYYY-MM-DD`` string into a ``date``.

    Raises ``ValueError`` with a user-friendly message for invalid input.
    """
    if value is None or str(value).strip() == "":
        raise ValueError("Date of birth is required.")
    try:
        return date.fromisoformat(str(value).strip())
    except ValueError:
        raise ValueError("Date of birth must be a valid date in YYYY-MM-DD format.")


def safe_parse_date(value):
    """Parse a stored ISO date without raising, returning ``None`` if unreadable.

    Used when reading a date that is already in the database. Values written
    through the service layer are always validated first, but a legacy row, a
    manual ``UPDATE`` or imported data could hold a non-ISO string. Returning
    ``None`` lets callers fail safely instead of raising an unhandled
    ``ValueError`` from :meth:`date.fromisoformat`.
    """
    try:
        return date.fromisoformat(str(value).strip())
    except (TypeError, ValueError):
        return None


def validate_date_of_birth(value, today: date | None = None) -> date:
    """Validate a date of birth and return it as a ``date``.

    Rejects empty values, unparseable strings, future dates and dates that
    imply an unreasonable age.
    """
    dob = parse_date(value)
    today = today or date.today()
    if dob > today:
        raise ValueError("Date of birth cannot be in the future.")
    if calculate_age(dob, today) >= MAX_REASONABLE_AGE:
        raise ValueError("Date of birth is not plausible.")
    return dob


def validate_email(value):
    """Validate an optional email address.

    Empty values are allowed; a non-empty value must look like an email.
    """
    if value is None or str(value).strip() == "":
        return ""
    value = str(value).strip()
    if not _EMAIL_RE.match(value):
        raise ValueError("Email address is not valid.")
    return value


def require_text(value, field_name, min_length=1):
    """Return a non-empty trimmed string or raise ``ValueError``."""
    if value is None or str(value).strip() == "":
        raise ValueError(f"{field_name} is required.")
    text = str(value).strip()
    if len(text) < min_length:
        raise ValueError(f"{field_name} is required.")
    return text


def optional_text(value):
    """Return a trimmed string or an empty string for missing input."""
    if value is None:
        return ""
    return str(value).strip()


def member_to_dict(row) -> dict:
    """Map a ``members`` row to a plain dict for the templates."""
    return {
        "id": row["id"],
        "name": row["name"],
        "date_of_birth": row["date_of_birth"],
        "email": row["email"],
        "phone": row["phone"],
        "address": row["address"],
        "status": row["status"],
    }


def guardian_to_dict(row) -> dict:
    """Map a ``guardians`` row to a plain dict for the templates."""
    return {
        "id": row["id"],
        "name": row["name"],
        "email": row["email"],
        "phone": row["phone"],
        "address": row["address"],
    }


def registration_to_dict(row) -> dict:
    """Map a ``registrations`` row to a plain dict for the templates."""
    return {
        "id": row["id"],
        "member_id": row["member_id"],
        "season": row["season"],
        "age_group": row["age_group"],
        "status": row["status"],
    }


def team_to_dict(row) -> dict:
    """Map a ``teams`` row to a plain dict for the templates."""
    return {
        "id": row["id"],
        "season": row["season"],
        "name": row["name"],
        "age_group": row["age_group"],
    }
