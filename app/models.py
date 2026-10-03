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
