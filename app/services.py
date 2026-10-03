"""Service layer: business rules for the Warrigal Park FC application.

Routes translate HTTP input into calls here; this layer talks to the database
layer and raises :class:`ServiceError` with a user-facing message whenever a
business rule is violated. Keeping the rules here (rather than in templates or
route handlers) makes them testable in isolation.
"""

from datetime import date

from . import database
from . import models

JUNIOR_GUARDIAN_REQUIRED_MESSAGE = (
    "Registration cannot be completed because a member under 18 must have "
    "at least one guardian."
)


class ServiceError(ValueError):
    """A business-rule violation that should be shown to the user."""


# ---------------------------------------------------------------------------
# Members
# ---------------------------------------------------------------------------

def list_members(search=None):
    """Return all members, optionally filtered by a case-insensitive name search."""
    if search and search.strip():
        like = f"%{search.strip()}%"
        rows = database.query_all(
            "SELECT * FROM members WHERE name LIKE ? ORDER BY name, id", (like,)
        )
    else:
        rows = database.query_all("SELECT * FROM members ORDER BY name, id")
    return [models.member_to_dict(r) for r in rows]


def get_member(member_id):
    """Return a member as a dict, or ``None`` when it does not exist."""
    row = database.query_one("SELECT * FROM members WHERE id = ?", (member_id,))
    return models.member_to_dict(row) if row else None


def _validate_member_fields(name, date_of_birth, email, phone, address):
    name = models.require_text(name, "Name")
    dob = models.validate_date_of_birth(date_of_birth)
    email = models.validate_email(email)
    phone = models.optional_text(phone)
    address = models.optional_text(address)
    return name, dob, email, phone, address


def create_member(name, date_of_birth, email, phone, address):
    """Create a new Active member. Duplicate names are allowed."""
    name, dob, email, phone, address = _validate_member_fields(
        name, date_of_birth, email, phone, address
    )
    cursor = database.get_db().execute(
        """
        INSERT INTO members (name, date_of_birth, email, phone, address, status)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (name, dob.isoformat(), email, phone, address, models.MEMBER_STATUS_ACTIVE),
    )
    database.get_db().commit()
    return get_member(cursor.lastrowid)


def update_member(member_id, name, date_of_birth, email, phone, address):
    """Update an existing member's details, preserving its current status."""
    if get_member(member_id) is None:
        raise ServiceError("Member not found.")
    name, dob, email, phone, address = _validate_member_fields(
        name, date_of_birth, email, phone, address
    )
    database.execute(
        """
        UPDATE members
        SET name = ?, date_of_birth = ?, email = ?, phone = ?, address = ?
        WHERE id = ?
        """,
        (name, dob.isoformat(), email, phone, address, member_id),
    )
    return get_member(member_id)


def set_member_status(member_id, status):
    """Set a member's status to Active or Inactive."""
    if status not in models.MEMBER_STATUSES:
        raise ServiceError("Invalid member status.")
    if get_member(member_id) is None:
        raise ServiceError("Member not found.")
    database.execute(
        "UPDATE members SET status = ? WHERE id = ?", (status, member_id)
    )
    return get_member(member_id)


def set_member_inactive(member_id):
    """Mark a member Inactive (a soft state change, never a hard delete)."""
    return set_member_status(member_id, models.MEMBER_STATUS_INACTIVE)


def member_registration_history(member_id):
    """Return a member's registrations across all seasons, newest first."""
    rows = database.query_all(
        """
        SELECT id, member_id, season, age_group, status
        FROM registrations
        WHERE member_id = ?
        ORDER BY season DESC, id DESC
        """,
        (member_id,),
    )
    return [models.registration_to_dict(r) for r in rows]


# ---------------------------------------------------------------------------
# Guardians
# ---------------------------------------------------------------------------

def list_guardians(search=None):
    """Return all guardians, optionally filtered by a name search."""
    if search and search.strip():
        like = f"%{search.strip()}%"
        rows = database.query_all(
            "SELECT * FROM guardians WHERE name LIKE ? ORDER BY name, id", (like,)
        )
    else:
        rows = database.query_all("SELECT * FROM guardians ORDER BY name, id")
    return [models.guardian_to_dict(r) for r in rows]


def get_guardian(guardian_id):
    """Return a guardian as a dict, or ``None`` when it does not exist."""
    row = database.query_one("SELECT * FROM guardians WHERE id = ?", (guardian_id,))
    return models.guardian_to_dict(row) if row else None


def _validate_guardian_fields(name, email, phone, address):
    name = models.require_text(name, "Name")
    email = models.validate_email(email)
    phone = models.optional_text(phone)
    address = models.optional_text(address)
    return name, email, phone, address


def create_guardian(name, email, phone, address):
    """Create a new guardian."""
    name, email, phone, address = _validate_guardian_fields(
        name, email, phone, address
    )
    cursor = database.get_db().execute(
        "INSERT INTO guardians (name, email, phone, address) VALUES (?, ?, ?, ?)",
        (name, email, phone, address),
    )
    database.get_db().commit()
    return get_guardian(cursor.lastrowid)


def update_guardian(guardian_id, name, email, phone, address):
    """Update a guardian's contact details."""
    if get_guardian(guardian_id) is None:
        raise ServiceError("Guardian not found.")
    name, email, phone, address = _validate_guardian_fields(
        name, email, phone, address
    )
    database.execute(
        "UPDATE guardians SET name = ?, email = ?, phone = ?, address = ? WHERE id = ?",
        (name, email, phone, address, guardian_id),
    )
    return get_guardian(guardian_id)


def guardian_linked_members(guardian_id):
    """Return the junior members linked to a guardian, with age included."""
    rows = database.query_all(
        """
        SELECT m.id, m.name, m.date_of_birth, m.email, m.phone, m.address, m.status
        FROM guardian_members gm
        JOIN members m ON m.id = gm.member_id
        WHERE gm.guardian_id = ?
        ORDER BY m.name, m.id
        """,
        (guardian_id,),
    )
    members = []
    for r in rows:
        member = models.member_to_dict(r)
        member["age"] = models.calculate_age(date.fromisoformat(r["date_of_birth"]))
        members.append(member)
    return members


def link_guardian_member(guardian_id, member_id):
    """Link a guardian to a member, rejecting invalid or duplicate links."""
    if get_guardian(guardian_id) is None:
        raise ServiceError("Guardian not found.")
    if get_member(member_id) is None:
        raise ServiceError("Member not found.")
    existing = database.query_one(
        "SELECT 1 FROM guardian_members WHERE guardian_id = ? AND member_id = ?",
        (guardian_id, member_id),
    )
    if existing:
        raise ServiceError("This guardian is already linked to that member.")
    database.execute(
        "INSERT INTO guardian_members (guardian_id, member_id) VALUES (?, ?)",
        (guardian_id, member_id),
    )


def unlink_guardian_member(guardian_id, member_id):
    """Remove a guardian-member link (never deletes the member or guardian)."""
    database.execute(
        "DELETE FROM guardian_members WHERE guardian_id = ? AND member_id = ?",
        (guardian_id, member_id),
    )


def member_guardians(member_id):
    """Return the guardians linked to a member."""
    rows = database.query_all(
        """
        SELECT g.id, g.name, g.email, g.phone, g.address
        FROM guardian_members gm
        JOIN guardians g ON g.id = gm.guardian_id
        WHERE gm.member_id = ?
        ORDER BY g.name, g.id
        """,
        (member_id,),
    )
    return [models.guardian_to_dict(r) for r in rows]


def member_has_guardian(member_id):
    """Return ``True`` when at least one guardian is linked to the member."""
    row = database.query_one(
        "SELECT 1 FROM guardian_members WHERE member_id = ? LIMIT 1", (member_id,)
    )
    return row is not None


# ---------------------------------------------------------------------------
# Registrations
# ---------------------------------------------------------------------------

def list_registrations():
    """Return all registrations joined to member names, newest first."""
    rows = database.query_all(
        """
        SELECT r.id, r.member_id, r.season, r.age_group, r.status, m.name AS member_name
        FROM registrations r
        JOIN members m ON m.id = r.member_id
        ORDER BY r.season DESC, r.id DESC
        """
    )
    results = []
    for r in rows:
        item = models.registration_to_dict(r)
        item["member_name"] = r["member_name"]
        results.append(item)
    return results


def get_registration(registration_id):
    """Return a registration with its member name, or ``None``."""
    row = database.query_one(
        """
        SELECT r.id, r.member_id, r.season, r.age_group, r.status, m.name AS member_name
        FROM registrations r
        JOIN members m ON m.id = r.member_id
        WHERE r.id = ?
        """,
        (registration_id,),
    )
    if row is None:
        return None
    item = models.registration_to_dict(row)
    item["member_name"] = row["member_name"]
    return item


def _validate_registration_fields(member_id, season, age_group, status):
    if get_member(member_id) is None:
        raise ServiceError("Member not found.")
    season = models.require_text(season, "Season")
    age_group = models.require_text(age_group, "Age group")
    if status not in models.REGISTRATION_STATUSES:
        raise ServiceError("Invalid registration status.")
    return member_id, season, age_group, status


def create_registration(
    member_id, season, age_group, status=models.REGISTRATION_STATUS_STARTED
):
    """Create a registration. Defaults to ``Started`` status."""
    member_id, season, age_group, status = _validate_registration_fields(
        member_id, season, age_group, status
    )
    # A registration created directly as Complete must still satisfy the rule.
    if status == models.REGISTRATION_STATUS_COMPLETE:
        allowed, message = can_complete_registration(member_id)
        if not allowed:
            raise ServiceError(message)
    cursor = database.get_db().execute(
        """
        INSERT INTO registrations (member_id, season, age_group, status)
        VALUES (?, ?, ?, ?)
        """,
        (member_id, season, age_group, status),
    )
    database.get_db().commit()
    return get_registration(cursor.lastrowid)


def _member_is_junior(member_id):
    member = get_member(member_id)
    dob = date.fromisoformat(member["date_of_birth"])
    return models.calculate_age(dob) < models.JUNIOR_AGE_LIMIT


def can_complete_registration(member_id):
    """Return ``(allowed, message)`` for completing a registration.

    Applies the under-18 guardian rule: juniors need at least one linked
    guardian; adults do not.
    """
    if get_member(member_id) is None:
        return False, "Member not found."
    if _member_is_junior(member_id) and not member_has_guardian(member_id):
        return False, JUNIOR_GUARDIAN_REQUIRED_MESSAGE
    return True, ""


def update_registration(registration_id, member_id, season, age_group, status):
    """Amend a registration, enforcing the guardian rule on completion."""
    existing = get_registration(registration_id)
    if existing is None:
        raise ServiceError("Registration not found.")
    member_id, season, age_group, status = _validate_registration_fields(
        member_id, season, age_group, status
    )

    # Enforce the under-18 guardian rule when a registration becomes Complete.
    if status == models.REGISTRATION_STATUS_COMPLETE:
        allowed, message = can_complete_registration(member_id)
        if not allowed:
            raise ServiceError(message)

    database.execute(
        """
        UPDATE registrations
        SET member_id = ?, season = ?, age_group = ?, status = ?
        WHERE id = ?
        """,
        (member_id, season, age_group, status, registration_id),
    )
    return get_registration(registration_id)


def withdraw_registration(registration_id):
    """Withdraw a registration, preserving it in the history."""
    if get_registration(registration_id) is None:
        raise ServiceError("Registration not found.")
    database.execute(
        "UPDATE registrations SET status = ? WHERE id = ?",
        (models.REGISTRATION_STATUS_WITHDRAWN, registration_id),
    )
    return get_registration(registration_id)


# ---------------------------------------------------------------------------
# Teams
# ---------------------------------------------------------------------------

def list_teams():
    """Return all teams, grouped visually by season then name."""
    rows = database.query_all(
        "SELECT * FROM teams ORDER BY season DESC, name, id"
    )
    return [models.team_to_dict(r) for r in rows]


def get_team(team_id):
    """Return a team as a dict, or ``None``."""
    row = database.query_one("SELECT * FROM teams WHERE id = ?", (team_id,))
    return models.team_to_dict(row) if row else None


def _validate_team_fields(season, name, age_group):
    season = models.require_text(season, "Season")
    name = models.require_text(name, "Team name")
    age_group = models.require_text(age_group, "Age group")
    return season, name, age_group


def create_team(season, name, age_group):
    """Create a new team."""
    season, name, age_group = _validate_team_fields(season, name, age_group)
    cursor = database.get_db().execute(
        "INSERT INTO teams (season, name, age_group) VALUES (?, ?, ?)",
        (season, name, age_group),
    )
    database.get_db().commit()
    return get_team(cursor.lastrowid)


def rename_team(team_id, season, name, age_group):
    """Update a team's season, name and age group."""
    if get_team(team_id) is None:
        raise ServiceError("Team not found.")
    season, name, age_group = _validate_team_fields(season, name, age_group)
    database.execute(
        "UPDATE teams SET season = ?, name = ?, age_group = ? WHERE id = ?",
        (season, name, age_group, team_id),
    )
    return get_team(team_id)


def delete_team(team_id):
    """Delete a team and its player assignments.

    Members and registrations are deliberately untouched.
    """
    if get_team(team_id) is None:
        raise ServiceError("Team not found.")
    db = database.get_db()
    db.execute("DELETE FROM team_players WHERE team_id = ?", (team_id,))
    db.execute("DELETE FROM teams WHERE id = ?", (team_id,))
    db.commit()


def team_players(team_id):
    """Return the players assigned to a team with their contact details."""
    rows = database.query_all(
        """
        SELECT tp.id AS team_player_id, m.id AS member_id, m.name, m.email, m.phone
        FROM team_players tp
        JOIN members m ON m.id = tp.member_id
        WHERE tp.team_id = ?
        ORDER BY m.name, m.id
        """,
        (team_id,),
    )
    return [
        {
            "team_player_id": r["team_player_id"],
            "member_id": r["member_id"],
            "name": r["name"],
            "email": r["email"],
            "phone": r["phone"],
        }
        for r in rows
    ]


# ---------------------------------------------------------------------------
# Players (team membership)
# ---------------------------------------------------------------------------

def _eligible_registration(member_id, season):
    """Return the member's non-withdrawn registration for ``season`` or None."""
    row = database.query_one(
        """
        SELECT id, member_id, season, age_group, status
        FROM registrations
        WHERE member_id = ? AND season = ? AND status != ?
        ORDER BY id
        LIMIT 1
        """,
        (member_id, season, models.REGISTRATION_STATUS_WITHDRAWN),
    )
    return models.registration_to_dict(row) if row else None


def _member_has_any_registration_for_season(member_id, season):
    return _eligible_registration(member_id, season) is not None


def add_player_to_team(team_id, member_id):
    """Add a member to a team, enforcing same-season registration eligibility.

    The player must have a non-withdrawn registration for the team's season.
    """
    team = get_team(team_id)
    if team is None:
        raise ServiceError("Team not found.")
    if get_member(member_id) is None:
        raise ServiceError("Member not found.")

    existing = database.query_one(
        "SELECT 1 FROM team_players WHERE team_id = ? AND member_id = ?",
        (team_id, member_id),
    )
    if existing:
        raise ServiceError("This player is already in that team.")

    if not _member_has_any_registration_for_season(member_id, team["season"]):
        raise ServiceError(
            "This member does not have a registration for the team's season "
            f"({team['season']})."
        )

    database.execute(
        "INSERT INTO team_players (team_id, member_id) VALUES (?, ?)",
        (team_id, member_id),
    )


def move_player(member_id, from_team_id, to_team_id):
    """Move a player from one team to another without touching registrations."""
    if from_team_id == to_team_id:
        raise ServiceError("The player is already in that team.")
    if get_team(from_team_id) is None or get_team(to_team_id) is None:
        raise ServiceError("Team not found.")

    membership = database.query_one(
        "SELECT 1 FROM team_players WHERE team_id = ? AND member_id = ?",
        (from_team_id, member_id),
    )
    if membership is None:
        raise ServiceError("That player is not in the source team.")

    add_player_to_team(to_team_id, member_id)  # re-checks eligibility + duplicates
    database.execute(
        "DELETE FROM team_players WHERE team_id = ? AND member_id = ?",
        (from_team_id, member_id),
    )


def remove_player_from_team(team_id, member_id):
    """Remove a player from a team, keeping their registration intact."""
    if get_team(team_id) is None:
        raise ServiceError("Team not found.")
    database.execute(
        "DELETE FROM team_players WHERE team_id = ? AND member_id = ?",
        (team_id, member_id),
    )


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

def dashboard_stats():
    """Return simple counts for the dashboard cards."""
    def scalar(sql, params=()):
        return database.query_one(sql, params)[0]

    return {
        "total_members": scalar("SELECT COUNT(*) FROM members"),
        "active_members": scalar(
            "SELECT COUNT(*) FROM members WHERE status = ?",
            (models.MEMBER_STATUS_ACTIVE,),
        ),
        "guardians": scalar("SELECT COUNT(*) FROM guardians"),
        "registrations": scalar("SELECT COUNT(*) FROM registrations"),
        "teams": scalar("SELECT COUNT(*) FROM teams"),
    }
