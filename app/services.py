"""Service layer: business rules for the Warrigal Park FC application.

Routes translate HTTP input into calls here; this layer talks to the database
layer and raises :class:`ServiceError` with a user-facing message whenever a
business rule is violated. Keeping the rules here (rather than in templates or
route handlers) makes them testable in isolation.
"""

from . import database
from . import models

JUNIOR_GUARDIAN_REQUIRED_MESSAGE = (
    "Registration cannot be completed because a member under 18 must have at "
    "least one guardian who is verified as an adult (18 or over)."
)

# Shown when a guardian's recorded date of birth shows they are not an adult,
# or is missing/unreadable, so the guardian cannot satisfy the junior rule.
GUARDIAN_NOT_ADULT_MESSAGE = (
    "This guardian cannot be linked because their record does not verify them "
    "as an adult (18 or over). Add a valid date of birth for the guardian first."
)

# Shown when a player is assigned to a team whose age group does not match the
# age group computed from the member's date of birth and the team's season.
AGE_GROUP_MISMATCH_MESSAGE = (
    "This member's age group for the team's season does not match the team's "
    "age group."
)

# Shown when a member already has a team for a season and a second assignment
# in the same season is attempted.
ALREADY_ASSIGNED_MESSAGE = (
    "This player is already assigned to a team in that season."
)

# Shown when a member's stored date of birth cannot be read, so the age - and
# therefore the under-18 guardian rule - cannot be evaluated safely.
UNREADABLE_DATE_OF_BIRTH_MESSAGE = (
    "This member's date of birth on record cannot be read, so the registration "
    "cannot be completed. Please correct the member's date of birth first."
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


def _dob_change_conflicts(member_id, dob, registrations):
    """Return the reasons a new date of birth cannot be applied, or ``[]``.

    Every affected registration is checked before anything is written: each
    season must still yield a valid age group, no existing team assignment may
    stop matching the recomputed age group, and a ``Complete`` registration for
    a member who would become a junior must still have a verified adult
    guardian.
    """
    conflicts = []
    for registration in registrations:
        try:
            models.get_age_group(dob, registration["season"])
        except ValueError as error:
            conflicts.append(
                f"{error} (the {registration['season']} registration)"
            )
    if conflicts:
        return conflicts

    for registration in registrations:
        if registration["status"] != models.REGISTRATION_STATUS_COMPLETE:
            continue
        computed = models.get_age_group(dob, registration["season"])
        assigned = team_for_member_in_season(member_id, registration["season"])
        if assigned is not None and assigned["age_group"] != computed:
            conflicts.append(
                f"the player is in '{assigned['name']}' "
                f"({assigned['season']}, {assigned['age_group']}) but would be "
                f"{computed} in {registration['season']}"
            )
    if conflicts:
        return conflicts

    completes = [
        r for r in registrations
        if r["status"] == models.REGISTRATION_STATUS_COMPLETE
    ]
    if (
        completes
        and models.calculate_age(dob) < models.JUNIOR_AGE_LIMIT
        and not member_has_adult_guardian(member_id)
    ):
        conflicts.append(
            "the member would be under 18 with a Complete registration and has "
            "no guardian verified as an adult"
        )
    return conflicts


def update_member(member_id, name, date_of_birth, email, phone, address):
    """Update an existing member's details, keeping registrations consistent.

    Changing the date of birth can change the age group of existing
    registrations. Before anything is written, every affected registration is
    re-checked and the change is refused with a clear message if it would leave
    an invalid age group, break an existing team assignment, or remove the
    verified adult guardian a junior Complete registration relies on.

    When the change is applied, the member row and every affected registration
    age group are written in one transaction, so a failure rolls the whole
    change back and never leaves a partial update. Registration ids, seasons,
    statuses and team records are preserved.
    """
    member = get_member(member_id)
    if member is None:
        raise ServiceError("Member not found.")
    name, dob, email, phone, address = _validate_member_fields(
        name, date_of_birth, email, phone, address
    )

    age_group_updates = []
    if dob.isoformat() != member["date_of_birth"]:
        registrations = member_registration_history(member_id)
        conflicts = _dob_change_conflicts(member_id, dob, registrations)
        if conflicts:
            raise ServiceError(
                "Date of birth cannot be changed: " + "; ".join(conflicts) + "."
            )
        age_group_updates = [
            (registration["id"], models.get_age_group(dob, registration["season"]))
            for registration in registrations
        ]

    with database.transaction() as db:
        db.execute(
            """
            UPDATE members
            SET name = ?, date_of_birth = ?, email = ?, phone = ?, address = ?
            WHERE id = ?
            """,
            (name, dob.isoformat(), email, phone, address, member_id),
        )
        for registration_id, age_group in age_group_updates:
            db.execute(
                "UPDATE registrations SET age_group = ? WHERE id = ?",
                (age_group, registration_id),
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


def _validate_guardian_fields(name, date_of_birth, email, phone, address):
    name = models.require_text(name, "Name")
    # A guardian must have a date of birth that verifies them as an adult.
    dob = models.validate_adult_date_of_birth(date_of_birth)
    email = models.validate_email(email)
    phone = models.optional_text(phone)
    address = models.optional_text(address)
    return name, dob, email, phone, address


def create_guardian(name, date_of_birth, email, phone, address):
    """Create a new guardian. The date of birth must verify an adult (18+)."""
    name, dob, email, phone, address = _validate_guardian_fields(
        name, date_of_birth, email, phone, address
    )
    cursor = database.get_db().execute(
        """
        INSERT INTO guardians (name, date_of_birth, email, phone, address)
        VALUES (?, ?, ?, ?, ?)
        """,
        (name, dob.isoformat(), email, phone, address),
    )
    database.get_db().commit()
    return get_guardian(cursor.lastrowid)


def update_guardian(guardian_id, name, date_of_birth, email, phone, address):
    """Update a guardian's details, re-validating the adult date of birth."""
    if get_guardian(guardian_id) is None:
        raise ServiceError("Guardian not found.")
    name, dob, email, phone, address = _validate_guardian_fields(
        name, date_of_birth, email, phone, address
    )
    database.execute(
        """
        UPDATE guardians
        SET name = ?, date_of_birth = ?, email = ?, phone = ?, address = ?
        WHERE id = ?
        """,
        (name, dob.isoformat(), email, phone, address, guardian_id),
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
        dob = models.safe_parse_date(r["date_of_birth"])
        # An unreadable stored date yields no age rather than a crash.
        member["age"] = models.calculate_age(dob) if dob else None
        members.append(member)
    return members


def link_guardian_member(guardian_id, member_id):
    """Link a guardian to a member, rejecting invalid, duplicate or non-adult links."""
    guardian = get_guardian(guardian_id)
    if guardian is None:
        raise ServiceError("Guardian not found.")
    if get_member(member_id) is None:
        raise ServiceError("Member not found.")
    if not guardian["is_adult"]:
        raise ServiceError(GUARDIAN_NOT_ADULT_MESSAGE)
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
    """Remove a guardian-member link (never deletes the member or guardian).

    Returns ``True`` when a link was actually removed and ``False`` when there
    was nothing to remove, so the caller can report the outcome accurately
    instead of claiming success for a no-op. Unknown identifiers raise
    :class:`ServiceError`.
    """
    if get_guardian(guardian_id) is None:
        raise ServiceError("Guardian not found.")
    if get_member(member_id) is None:
        raise ServiceError("Member not found.")
    removed = database.execute(
        "DELETE FROM guardian_members WHERE guardian_id = ? AND member_id = ?",
        (guardian_id, member_id),
    )
    return removed > 0


def member_guardians(member_id):
    """Return the guardians linked to a member."""
    rows = database.query_all(
        """
        SELECT g.id, g.name, g.date_of_birth, g.email, g.phone, g.address
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


def member_has_adult_guardian(member_id):
    """Return ``True`` when a linked guardian is verified as an adult.

    A guardian with a missing or unreadable ``date_of_birth`` (a legacy record)
    does not count as verified, even though the link row exists.
    """
    rows = database.query_all(
        """
        SELECT g.date_of_birth
        FROM guardian_members gm
        JOIN guardians g ON g.id = gm.guardian_id
        WHERE gm.member_id = ?
        """,
        (member_id,),
    )
    for row in rows:
        dob = models.safe_parse_date(row["date_of_birth"])
        if dob is not None and models.calculate_age(dob) >= models.JUNIOR_AGE_LIMIT:
            return True
    return False


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


def _require_season(season):
    """Return a validated four-digit season year, or raise :class:`ServiceError`."""
    try:
        return models.parse_season(season)
    except ValueError as error:
        raise ServiceError(str(error))


def _computed_age_group(member, season):
    """Compute the age group from a member's stored DOB and a season.

    The submitted age group is never trusted: the value used for storage is
    always derived here.
    """
    dob = models.safe_parse_date(member["date_of_birth"])
    if dob is None:
        raise ServiceError(UNREADABLE_DATE_OF_BIRTH_MESSAGE)
    try:
        return models.get_age_group(dob, season)
    except ValueError as error:
        raise ServiceError(str(error))


def _validate_registration_fields(member_id, season, status):
    member = get_member(member_id)
    if member is None:
        raise ServiceError("Member not found.")
    year = _require_season(season)
    if status not in models.REGISTRATION_STATUSES:
        raise ServiceError("Invalid registration status.")
    age_group = _computed_age_group(member, year)
    return member_id, str(year), age_group, status


def create_registration(
    member_id, season, age_group=None, status=models.REGISTRATION_STATUS_STARTED
):
    """Create a registration. The age group is computed from the member's DOB.

    The ``age_group`` argument is accepted for compatibility with existing
    callers but is ignored: the stored value is always derived from the
    member's date of birth and the season. A registration created directly as
    ``Complete`` must satisfy the adult-guardian rule and is then offered to the
    auto-assignment flow.
    """
    member_id, season, age_group, status = _validate_registration_fields(
        member_id, season, status
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
    registration = get_registration(cursor.lastrowid)
    if status == models.REGISTRATION_STATUS_COMPLETE:
        auto_assign_player(member_id, season)
    return registration


def _member_is_junior(member_id):
    """Return ``True`` only when the member is known to be under 18.

    An unreadable stored date of birth returns ``False`` so this helper never
    raises; :func:`can_complete_registration` is responsible for refusing the
    completion in that case, so an invalid date can never be treated as proof
    that the member is an adult.
    """
    member = get_member(member_id)
    dob = models.safe_parse_date(member["date_of_birth"])
    if dob is None:
        return False
    return models.calculate_age(dob) < models.JUNIOR_AGE_LIMIT


def can_complete_registration(member_id):
    """Return ``(allowed, message)`` for completing a registration.

    Applies the under-18 guardian rule: juniors need at least one linked
    guardian; adults do not. A member whose stored date of birth cannot be read
    is refused rather than assumed to be an adult.
    """
    member = get_member(member_id)
    if member is None:
        return False, "Member not found."
    if models.safe_parse_date(member["date_of_birth"]) is None:
        return False, UNREADABLE_DATE_OF_BIRTH_MESSAGE
    if _member_is_junior(member_id) and not member_has_adult_guardian(member_id):
        return False, JUNIOR_GUARDIAN_REQUIRED_MESSAGE
    return True, ""


def update_registration(
    registration_id, member_id, season, age_group=None, status=None
):
    """Amend a registration, recomputing the age group from DOB and season.

    The ``age_group`` argument is accepted for compatibility but ignored.
    """
    existing = get_registration(registration_id)
    if existing is None:
        raise ServiceError("Registration not found.")
    previous_member_id = existing["member_id"]
    previous_season = existing["season"]
    member_id, season, age_group, status = _validate_registration_fields(
        member_id, season, status
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
    # Keep team assignments consistent after the amendment, then assign if the
    # registration is (now) Complete.
    _reconcile_team_assignments(previous_member_id, previous_season)
    _reconcile_team_assignments(member_id, season)
    if status == models.REGISTRATION_STATUS_COMPLETE:
        auto_assign_player(member_id, season)
    return get_registration(registration_id)


def withdraw_registration(registration_id):
    """Withdraw a registration, preserving it in the history.

    If this was the member's last valid ``Complete`` registration for the
    season, the member's team assignment for that season is removed.
    """
    existing = get_registration(registration_id)
    if existing is None:
        raise ServiceError("Registration not found.")
    database.execute(
        "UPDATE registrations SET status = ? WHERE id = ?",
        (models.REGISTRATION_STATUS_WITHDRAWN, registration_id),
    )
    registration = get_registration(registration_id)
    _reconcile_team_assignments(existing["member_id"], existing["season"])
    return registration


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
    year = _require_season(season)
    name = models.require_text(name, "Team name")
    age_group = models.require_text(age_group, "Age group")
    if age_group not in models.AGE_GROUPS:
        raise ServiceError(
            "Age group must be one of: " + ", ".join(models.AGE_GROUPS) + "."
        )
    return str(year), name, age_group


def create_team(season, name, age_group):
    """Create a new team, then auto-assign any waiting eligible players."""
    season, name, age_group = _validate_team_fields(season, name, age_group)
    cursor = database.get_db().execute(
        "INSERT INTO teams (season, name, age_group) VALUES (?, ?, ?)",
        (season, name, age_group),
    )
    database.get_db().commit()
    team = get_team(cursor.lastrowid)
    auto_assign_pending_players(season, age_group)
    return team


def _team_assignment_conflicts(team_id, season, age_group):
    """Return human-readable conflicts for a proposed team season/age change."""
    rows = database.query_all(
        """
        SELECT m.name, m.date_of_birth
        FROM team_players tp
        JOIN members m ON m.id = tp.member_id
        WHERE tp.team_id = ?
        ORDER BY m.name, m.id
        """,
        (team_id,),
    )
    conflicts = []
    for row in rows:
        dob = models.safe_parse_date(row["date_of_birth"])
        if dob is None:
            conflicts.append(f"{row['name']} has an unreadable date of birth")
            continue
        try:
            computed = models.get_age_group(dob, season)
        except ValueError as error:
            conflicts.append(f"{row['name']} ({error})")
            continue
        if computed != age_group:
            conflicts.append(
                f"{row['name']} is {computed} in {season}, not {age_group}"
            )
    return conflicts


def rename_team(team_id, season, name, age_group):
    """Update a team's season, name and age group.

    An edit that would leave already-assigned players in a team whose season or
    age group no longer matches their computed age group is refused, so no
    assignment is left in an inconsistent state.
    """
    if get_team(team_id) is None:
        raise ServiceError("Team not found.")
    season, name, age_group = _validate_team_fields(season, name, age_group)
    conflicts = _team_assignment_conflicts(team_id, season, age_group)
    if conflicts:
        raise ServiceError(
            "Cannot change this team's season or age group while it has "
            "players who would not match: " + "; ".join(conflicts)
            + ". Move or remove those players first."
        )
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
    """Return a member's Complete registration for ``season``, or ``None``.

    Only a ``Complete`` registration makes a player eligible for a team in that
    season. ``Started`` and ``Withdrawn`` registrations do not qualify.
    """
    row = database.query_one(
        """
        SELECT id, member_id, season, age_group, status
        FROM registrations
        WHERE member_id = ? AND season = ? AND status = ?
        ORDER BY id
        LIMIT 1
        """,
        (member_id, season, models.REGISTRATION_STATUS_COMPLETE),
    )
    return models.registration_to_dict(row) if row else None


def _member_has_any_registration_for_season(member_id, season):
    return _eligible_registration(member_id, season) is not None


def _member_age_group(member, season):
    """Return the member's computed age group for a season."""
    dob = models.safe_parse_date(member["date_of_birth"])
    if dob is None:
        raise ServiceError(UNREADABLE_DATE_OF_BIRTH_MESSAGE)
    try:
        return models.get_age_group(dob, season)
    except ValueError as error:
        raise ServiceError(str(error))


def team_for_member_in_season(member_id, season):
    """Return the team a member is assigned to for a season, or ``None``."""
    row = database.query_one(
        """
        SELECT t.id, t.season, t.name, t.age_group
        FROM team_players tp
        JOIN teams t ON t.id = tp.team_id
        WHERE tp.member_id = ? AND t.season = ?
        ORDER BY t.id
        LIMIT 1
        """,
        (member_id, season),
    )
    return models.team_to_dict(row) if row else None


def _matching_teams(season, age_group):
    """Return matching teams ordered by fewest players, then lowest id."""
    rows = database.query_all(
        """
        SELECT t.id, t.season, t.name, t.age_group, COUNT(tp.id) AS player_count
        FROM teams t
        LEFT JOIN team_players tp ON tp.team_id = t.id
        WHERE t.season = ? AND t.age_group = ?
        GROUP BY t.id
        ORDER BY player_count ASC, t.id ASC
        """,
        (season, age_group),
    )
    return [dict(r) for r in rows]


def assignment_conflict(member_id, season):
    """Return a message when a member's team for a season no longer matches.

    An existing assignment whose age group differs from the one computed from
    the member's current date of birth is reported here rather than being
    silently moved or duplicated. Returns ``None`` when there is no conflict.
    """
    assigned = team_for_member_in_season(member_id, season)
    if assigned is None:
        return None
    member = get_member(member_id)
    if member is None:
        return None
    try:
        computed = _member_age_group(member, season)
    except ServiceError:
        return (
            f"the player is in '{assigned['name']}' but their date of birth "
            "cannot be read to confirm their age group"
        )
    if computed != assigned["age_group"]:
        return (
            f"the player is in '{assigned['name']}' ({assigned['age_group']}) "
            f"but their age group for {season} is {computed}"
        )
    return None


def auto_assign_player(member_id, season):
    """Assign an eligible player to the least-full matching team.

    The age group is always recomputed from the member's current date of birth
    and the season, so a stored ``age_group`` on a legacy registration is never
    used to pick a team. Returns that team, or ``None`` when there is no
    matching team. A member already assigned in the season is never moved and
    never given a second team; a mismatching existing assignment is left for the
    caller to report via :func:`assignment_conflict`.
    """
    registration = _eligible_registration(member_id, season)
    if registration is None:
        return None
    member = get_member(member_id)
    if member is None:
        return None
    try:
        age_group = _member_age_group(member, season)
    except ServiceError:
        return None
    existing = team_for_member_in_season(member_id, season)
    if existing is not None:
        # Never add a second team for the season even when the existing one no
        # longer matches; the conflict is reported instead.
        return existing
    teams = _matching_teams(season, age_group)
    if not teams:
        return None
    target = teams[0]
    database.execute(
        "INSERT INTO team_players (team_id, member_id) VALUES (?, ?)",
        (target["id"], member_id),
    )
    return get_team(target["id"])


def auto_assign_pending_players(season, age_group):
    """Assign every eligible, not-yet-assigned player for a season and age group.

    Returns the list of ``(member_id, team_id)`` assignments made. Used when a
    matching team is created. Players whose registration is not ``Complete``,
    or whose computed age group differs, are skipped.
    """
    rows = database.query_all(
        """
        SELECT r.member_id, m.date_of_birth
        FROM registrations r
        JOIN members m ON m.id = r.member_id
        WHERE r.season = ? AND r.status = ?
        ORDER BY r.member_id
        """,
        (season, models.REGISTRATION_STATUS_COMPLETE),
    )
    assignments = []
    for row in rows:
        member_id = row["member_id"]
        dob = models.safe_parse_date(row["date_of_birth"])
        if dob is None:
            continue
        try:
            computed = models.get_age_group(dob, season)
        except ValueError:
            continue
        if computed != age_group:
            continue
        if team_for_member_in_season(member_id, season) is not None:
            continue
        team = auto_assign_player(member_id, season)
        if team is not None:
            assignments.append((member_id, team["id"]))
    return assignments


def _reconcile_team_assignments(member_id, season):
    """Drop a member's team assignment for a season with no valid Complete registration.

    Only the assignment for that season is touched, and only when the member has
    no remaining ``Complete`` registration for it. Members, registrations and
    guardian links are never deleted.
    """
    if _member_has_any_registration_for_season(member_id, season):
        return False
    removed = database.execute(
        """
        DELETE FROM team_players
        WHERE member_id = ?
          AND team_id IN (SELECT id FROM teams WHERE season = ?)
        """,
        (member_id, season),
    )
    return removed > 0


def add_player_to_team(team_id, member_id):
    """Add a member to a team (manual placement).

    Enforces a Complete registration for the team's season, a matching computed
    age group, no duplicate association and at most one team per season.
    """
    team = get_team(team_id)
    if team is None:
        raise ServiceError("Team not found.")
    member = get_member(member_id)
    if member is None:
        raise ServiceError("Member not found.")

    existing = database.query_one(
        "SELECT 1 FROM team_players WHERE team_id = ? AND member_id = ?",
        (team_id, member_id),
    )
    if existing:
        raise ServiceError("This player is already in that team.")

    if not _member_has_any_registration_for_season(member_id, team["season"]):
        raise ServiceError(
            "This member does not have a Complete registration for the team's "
            f"season ({team['season']})."
        )

    computed = _member_age_group(member, team["season"])
    if computed != team["age_group"]:
        raise ServiceError(
            f"{AGE_GROUP_MISMATCH_MESSAGE} This member is {computed} in "
            f"{team['season']}, but the team is {team['age_group']}."
        )

    other = team_for_member_in_season(member_id, team["season"])
    if other is not None:
        raise ServiceError(
            f"{ALREADY_ASSIGNED_MESSAGE} The player is in '{other['name']}'."
        )

    database.execute(
        "INSERT INTO team_players (team_id, member_id) VALUES (?, ?)",
        (team_id, member_id),
    )


def move_player(member_id, from_team_id, to_team_id):
    """Move a player between two teams of the same season.

    The target team must be in the same season and match the player's computed
    age group. Registrations are not touched.
    """
    if from_team_id == to_team_id:
        raise ServiceError("The player is already in that team.")
    source = get_team(from_team_id)
    target = get_team(to_team_id)
    if source is None or target is None:
        raise ServiceError("Team not found.")
    if source["season"] != target["season"]:
        raise ServiceError(
            "A player can only be moved between teams in the same season."
        )

    membership = database.query_one(
        "SELECT 1 FROM team_players WHERE team_id = ? AND member_id = ?",
        (from_team_id, member_id),
    )
    if membership is None:
        raise ServiceError("That player is not in the source team.")

    member = get_member(member_id)
    if member is None:
        raise ServiceError("Member not found.")

    existing = database.query_one(
        "SELECT 1 FROM team_players WHERE team_id = ? AND member_id = ?",
        (to_team_id, member_id),
    )
    if existing:
        raise ServiceError("This player is already in that team.")

    if not _member_has_any_registration_for_season(member_id, target["season"]):
        raise ServiceError(
            "This member does not have a Complete registration for the team's "
            f"season ({target['season']})."
        )

    computed = _member_age_group(member, target["season"])
    if computed != target["age_group"]:
        raise ServiceError(
            f"{AGE_GROUP_MISMATCH_MESSAGE} This member is {computed} in "
            f"{target['season']}, but the team is {target['age_group']}."
        )

    database.execute(
        "INSERT INTO team_players (team_id, member_id) VALUES (?, ?)",
        (to_team_id, member_id),
    )
    database.execute(
        "DELETE FROM team_players WHERE team_id = ? AND member_id = ?",
        (from_team_id, member_id),
    )


def remove_player_from_team(team_id, member_id):
    """Remove a player from a team, keeping their registration intact.

    Returns ``True`` when a membership row was actually removed and ``False``
    when there was nothing to remove, so callers can report the outcome
    accurately instead of claiming success for a no-op. Unknown identifiers
    raise :class:`ServiceError`.
    """
    if get_team(team_id) is None:
        raise ServiceError("Team not found.")
    if get_member(member_id) is None:
        raise ServiceError("Member not found.")
    removed = database.execute(
        "DELETE FROM team_players WHERE team_id = ? AND member_id = ?",
        (team_id, member_id),
    )
    return removed > 0


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
