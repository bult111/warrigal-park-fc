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

# A sensible upper bound used to reject obviously incorrect birth dates.
MAX_REASONABLE_AGE = 130

# Age-group rule for this course project (NOT an official Football Australia
# regulation). The age group is derived from the season age, which is the age a
# member reaches on 31 December of the season year:
#
#     season_age = season_year - birth_year
#
# Each pair is ``(youngest season age in the group, group label)``.
AGE_GROUP_THRESHOLDS = (
    (18, "Seniors"),
    (16, "U18"),
    (14, "U16"),
    (12, "U14"),
    (10, "U12"),
    (8, "U10"),
    (6, "U8"),
    (4, "U6"),
)
# Groups from youngest to oldest, for use in forms.
AGE_GROUPS = tuple(group for _, group in reversed(AGE_GROUP_THRESHOLDS))

# Members younger than this in a season cannot be placed in an age group.
MIN_REGISTRATION_AGE = 4

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def calculate_age(dob: date, today: date | None = None) -> int:
    """Return the age in whole years for ``dob`` as of ``today`` (or now)."""
    today = today or date.today()
    years = today.year - dob.year
    if (today.month, today.day) < (dob.month, dob.day):
        years -= 1
    return years


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


def validate_adult_date_of_birth(value, today: date | None = None) -> date:
    """Validate a guardian date of birth, requiring an adult (18 or over).

    The 18th birthday itself counts as an adult. Raises ``ValueError`` for a
    missing, unparseable, future, implausible or under-18 date.
    """
    today = today or date.today()
    dob = validate_date_of_birth(value, today=today)
    if calculate_age(dob, today) < JUNIOR_AGE_LIMIT:
        raise ValueError("A guardian must be at least 18 years old.")
    return dob


def parse_season(season):
    """Parse a season into a four-digit calendar year, or raise ``ValueError``."""
    if season is None or str(season).strip() == "":
        raise ValueError("Season is required.")
    text = str(season).strip()
    if len(text) != 4 or not text.isdigit():
        raise ValueError("Season must be a four-digit year, for example 2026.")
    return int(text)


def get_age_group(date_of_birth, season):
    """Return the age group for a date of birth in a registration season.

    The season age is ``season_year - birth_year``, i.e. the age reached on
    31 December of the season year. A member below :data:`MIN_REGISTRATION_AGE`
    is refused. This is the course project's own rule (see
    ``docs/project-scope.md``); it is not an official Football Australia
    regulation.
    """
    year = parse_season(season)
    dob = date_of_birth if isinstance(date_of_birth, date) else parse_date(date_of_birth)
    season_age = year - dob.year
    for min_age, group in AGE_GROUP_THRESHOLDS:
        if season_age >= min_age:
            return group
    raise ValueError(
        f"A member must be at least {MIN_REGISTRATION_AGE} in the {year} season "
        "to be placed in an age group."
    )


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
    """Map a ``guardians`` row to a plain dict for the templates.

    ``date_of_birth`` is ``None`` for legacy guardians created before the field
    existed; such guardians are not verified as adults.
    """
    dob = safe_parse_date(row["date_of_birth"])
    age = calculate_age(dob) if dob else None
    return {
        "id": row["id"],
        "name": row["name"],
        "date_of_birth": row["date_of_birth"],
        "email": row["email"],
        "phone": row["phone"],
        "address": row["address"],
        "age": age,
        "is_adult": age is not None and age >= JUNIOR_AGE_LIMIT,
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
