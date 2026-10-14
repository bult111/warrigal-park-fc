"""Sprint 3 — Registration and Eligibility story tests.

This module adds targeted coverage for the five Sprint 3 stories:

- MSD426GXUST25-10  Create Registration
- MSD426GXUST25-11  Amend Registration
- MSD426GXUST25-12  Withdraw Registration
- MSD426GXUST25-13  View Member Registration History
- MSD426GXUST25-14  Enforce Under-18 Guardian Rule

Every assertion describes behaviour that was read in the application source and
reproduced by running it. Each test runs against the isolated temporary SQLite
database supplied by ``tests/conftest.py``; the real application database is
never touched. No existing test was removed, renamed or weakened.

Date-boundary tests use the ``exactly_18_dob`` and ``just_under_18_dob``
fixtures from ``conftest.py``, which are computed from ``date.today()``, so the
boundary is tested against the application's real clock rather than a fixed
date that would rot.

Scope note: registration withdrawal is asserted here as a *status* change with
the record retained, which is the model documented in ``README.md`` ("Withdrawn
registrations stay in the database and remain visible in the member's
history"). The interaction between withdrawal and team rosters is a separate,
still-open product question (S3-C2) and is deliberately **not** asserted here.

Provenance note: this module was first written earlier in the same work session
as ``tests/test_registration_workflows.py`` and was lost when the working tree
was cleaned externally. It has been reconstructed from the session record and
verified against the recovered pytest node-id manifest (103 ids) retained with
the browser evidence. The final section (S3-D1 regression) was added after the
reconstruction as part of the S3-D1 fix.
"""

import pytest

from app import database, services


# ---------------------------------------------------------------------------
# Local helpers
# ---------------------------------------------------------------------------

def _count(table, where="", params=()):
    """Return a row count for ``table``, optionally with a WHERE clause."""
    sql = f"SELECT COUNT(*) FROM {table}"
    if where:
        sql += f" WHERE {where}"
    return database.query_one(sql, params)[0]


def _raw_registration(registration_id):
    """Return the stored row for a registration without any mapping."""
    return database.query_one(
        "SELECT id, member_id, season, age_group, status FROM registrations WHERE id = ?",
        (registration_id,),
    )


def _registration_row_count():
    return _count("registrations")


# ---------------------------------------------------------------------------
# MSD426GXUST25-10 — Create Registration
# ---------------------------------------------------------------------------

def test_create_registration_persists_and_is_retrievable(make_member, make_registration):
    """A valid registration is persisted and can be read back by its new id."""
    member = make_member("Create Story Member", dob="2010-05-20")

    created = make_registration(member["id"], "2026", "U16")

    assert created["id"] is not None
    assert created["member_id"] == member["id"]

    fetched = services.get_registration(created["id"])
    assert fetched is not None
    assert fetched["id"] == created["id"]
    assert fetched["member_id"] == member["id"]
    assert fetched["member_name"] == "Create Story Member"
    assert fetched["season"] == "2026"
    assert fetched["age_group"] == "U16"
    assert fetched["status"] == "Started"


def test_create_registration_writes_the_same_values_to_the_database(
    make_member, make_registration
):
    """The stored row matches the values returned to the caller."""
    member = make_member("Database Member")
    created = make_registration(member["id"], "2027", "U18")

    row = _raw_registration(created["id"])
    assert row["member_id"] == member["id"]
    assert row["season"] == "2027"
    assert row["age_group"] == "U18"
    assert row["status"] == "Started"


def test_create_registration_default_status_is_started(make_member):
    """Omitting the status stores ``Started``, which is the documented default."""
    member = make_member("Default Status Member")

    created = services.create_registration(member["id"], "2026", "U16")

    assert created["status"] == "Started"
    assert _raw_registration(created["id"])["status"] == "Started"


@pytest.mark.parametrize("status", ["Started", "Complete"])
def test_create_registration_accepts_every_supported_status(
    make_member, make_registration, status
):
    """Each status in the model's supported set can be stored on creation.

    ``Complete`` is exercised with an adult member so that the under-18
    guardian rule is not what is being tested here.
    """
    member = make_member(f"Status {status}", dob="1990-01-01")

    created = make_registration(member["id"], "2026", "Seniors", status)

    assert created["status"] == status
    assert _raw_registration(created["id"])["status"] == status


def test_create_registration_keeps_member_identity(make_member, make_registration):
    """A registration belongs to the member it was created for, and no other."""
    first = make_member("First Registration Owner")
    second = make_member("Second Registration Owner")

    created = make_registration(first["id"], "2026", "U16")

    assert created["member_id"] == first["id"]
    assert services.member_registration_history(second["id"]) == []


def test_create_registration_unknown_member_rejected(make_registration):
    """A registration cannot be created for a member id that does not exist."""
    before = _registration_row_count()

    with pytest.raises(services.ServiceError) as exc_info:
        make_registration(99999, "2026", "U16")

    assert "Member not found" in str(exc_info.value)
    assert _registration_row_count() == before


def test_create_registration_for_inactive_member_is_allowed(make_member, make_registration):
    """Deactivation is only a status change, so it does not block registration.

    ``README.md`` defines deactivation as a soft state change and states no rule
    that would prevent registering an Inactive member, so the current behaviour
    is asserted and the open question is recorded as S3-O2.
    """
    member = make_member("Inactive Registrant", dob="2010-01-01")
    services.set_member_inactive(member["id"])

    created = make_registration(member["id"], "2026", "U16")

    assert created["member_id"] == member["id"]


@pytest.mark.parametrize(
    "season, age_group, expected_message",
    [
        ("", "U16", "Season is required."),
        ("   ", "U16", "Season is required."),
        (None, "U16", "Season is required."),
        ("2026", "", "Age group is required."),
        ("2026", "   ", "Age group is required."),
        ("2026", None, "Age group is required."),
    ],
)
def test_create_registration_missing_fields_rejected_and_nothing_stored(
    make_member, make_registration, season, age_group, expected_message
):
    """Missing season or age group is refused with a message and stores nothing."""
    member = make_member("Missing Field Member", dob="2010-01-01")
    before = _registration_row_count()

    with pytest.raises(ValueError) as exc_info:
        make_registration(member["id"], season, age_group)

    assert expected_message in str(exc_info.value)
    assert _registration_row_count() == before
    assert services.member_registration_history(member["id"]) == []


def test_create_registration_required_fields_checked_before_insert(
    make_member, make_registration
):
    """Both required text fields are validated before any row is written.

    A payload with *both* fields missing must still leave the table untouched,
    which proves no partial insert happens between the two checks.
    """
    member = make_member("Both Missing Member", dob="2010-01-01")
    before = _registration_row_count()

    with pytest.raises(ValueError):
        make_registration(member["id"], "", "")

    assert _registration_row_count() == before


def test_create_registration_invalid_status_rejected(make_member, make_registration):
    """A status outside the supported set is refused and stores nothing."""
    member = make_member("Bad Status Member", dob="2010-01-01")
    before = _registration_row_count()

    with pytest.raises(services.ServiceError) as exc_info:
        make_registration(member["id"], "2026", "U16", "NotAStatus")

    assert "Invalid registration status" in str(exc_info.value)
    assert _registration_row_count() == before


def test_create_registration_route_redirects_to_viewable_detail(client, make_member):
    """The create form redirects to a detail page that shows the new registration."""
    member = make_member("Route Registration Member", dob="2010-05-20")

    response = client.post(
        "/registrations/new",
        data={"member_id": str(member["id"]), "season": "2026", "age_group": "U16", "status": "Started"},
    )

    assert response.status_code == 302
    location = response.headers["Location"]
    assert location.startswith("/registrations/")

    detail = client.get(location)
    assert detail.status_code == 200
    assert b"Route Registration Member" in detail.data
    assert b"2026" in detail.data
    assert b"U16" in detail.data
    assert b"Started" in detail.data
    assert b"Registration created." in detail.data


def test_create_registration_route_appears_in_member_history(client, make_member):
    """A registration created through the form appears in the member's history."""
    member = make_member("History After Route Create", dob="2010-05-20")

    client.post(
        "/registrations/new",
        data={"member_id": str(member["id"]), "season": "2026", "age_group": "U16", "status": "Started"},
    )

    page = client.get(f"/members/{member['id']}")
    assert page.status_code == 200
    assert b"U16" in page.data
    assert b"Registration History" in page.data


@pytest.mark.parametrize(
    "payload, expected_message",
    [
        ({"season": "2026", "age_group": "U16"}, b"Member not found."),
        ({"member_id": "99999", "season": "2026", "age_group": "U16"}, b"Member not found."),
        ({"member_id": "@@bad@@", "season": "2026", "age_group": "U16"}, b"Member not found."),
        ({"member_id": "@real@", "age_group": "U16"}, b"Season is required."),
        ({"member_id": "@real@", "season": "2026"}, b"Age group is required."),
        (
            {"member_id": "@real@", "season": "2026", "age_group": "U16", "status": "Bogus"},
            b"Invalid registration status.",
        ),
    ],
)
def test_create_registration_route_invalid_input_shows_feedback_and_stores_nothing(
    client, make_member, payload, expected_message
):
    """Invalid create submissions are refused safely with feedback on the page."""
    member = make_member("Invalid Route Member", dob="2010-01-01")
    # "@real@" stands for the member that really exists in this test.
    payload = {
        key: (str(member["id"]) if value == "@real@" else value) for key, value in payload.items()
    }
    before = _registration_row_count()

    response = client.post("/registrations/new", data=payload)

    assert response.status_code == 400
    assert expected_message in response.data
    assert _registration_row_count() == before


def test_create_registration_route_keeps_typed_values_on_error(client, make_member):
    """A rejected submission re-renders the form with the typed values retained."""
    make_member("Retained Values Member", dob="2010-01-01")

    response = client.post(
        "/registrations/new",
        data={"member_id": "99999", "season": "2031", "age_group": "U12", "status": "Started"},
    )

    assert response.status_code == 400
    assert b"2031" in response.data
    assert b"U12" in response.data
    assert b"Member not found." in response.data


def test_create_registration_form_offers_members_and_statuses(client, make_member):
    """The create form lists the members that can be registered."""
    make_member("Selectable Member", dob="2010-01-01")

    response = client.get("/registrations/new")

    assert response.status_code == 200
    assert b"New Registration" in response.data
    assert b"Selectable Member" in response.data
    # The status list comes from the model constants.
    assert b"Started" in response.data
    assert b"Complete" in response.data
    assert b"Withdrawn" in response.data


def test_create_registration_failure_leaves_other_registrations_untouched(
    client, make_member, make_registration
):
    """A rejected create does not disturb registrations that already exist."""
    member = make_member("Existing Registration Member", dob="2010-01-01")
    existing = make_registration(member["id"], "2025", "U14")

    client.post("/registrations/new", data={"member_id": "99999", "season": "2026", "age_group": "U16"})

    assert services.get_registration(existing["id"])["season"] == "2025"
    assert _registration_row_count() == 1


# ---------------------------------------------------------------------------
# MSD426GXUST25-11 — Amend Registration
# ---------------------------------------------------------------------------

def test_amend_registration_changes_season_only(make_member, make_registration):
    """Amending the season leaves the other stored fields untouched."""
    member = make_member("Amend Season Member", dob="2010-01-01")
    created = make_registration(member["id"], "2026", "U16", "Started")

    updated = services.update_registration(created["id"], member["id"], "2027", "U16", "Started")

    assert updated["season"] == "2027"
    assert updated["age_group"] == "U16"
    assert updated["status"] == "Started"
    assert updated["member_id"] == member["id"]


def test_amend_registration_changes_age_group_only(make_member, make_registration):
    """Amending the age group leaves the season and status untouched."""
    member = make_member("Amend Age Group Member", dob="2010-01-01")
    created = make_registration(member["id"], "2026", "U16", "Started")

    updated = services.update_registration(created["id"], member["id"], "2026", "U18", "Started")

    assert updated["season"] == "2026"
    assert updated["age_group"] == "U18"
    assert updated["status"] == "Started"


def test_amend_registration_status_started_to_complete_for_adult(make_member, make_registration):
    """An adult registration can be completed without a guardian."""
    adult = make_member("Adult Completion", dob="1990-06-15")
    created = make_registration(adult["id"], "2026", "Seniors", "Started")

    updated = services.update_registration(created["id"], adult["id"], "2026", "Seniors", "Complete")

    assert updated["status"] == "Complete"
    assert _raw_registration(created["id"])["status"] == "Complete"


def test_amend_registration_persists_after_reload(make_member, make_registration):
    """An amendment survives a fresh read rather than only the returned dict."""
    member = make_member("Persisted Amendment", dob="2010-01-01")
    created = make_registration(member["id"], "2026", "U16", "Started")

    services.update_registration(created["id"], member["id"], "2027", "U18", "Started")

    reloaded = services.get_registration(created["id"])
    assert reloaded["season"] == "2027"
    assert reloaded["age_group"] == "U18"
    assert _raw_registration(created["id"])["season"] == "2027"
    assert _raw_registration(created["id"])["age_group"] == "U18"


def test_amend_registration_keeps_the_same_row_and_id(make_member, make_registration):
    """Amending updates the existing record; it never creates a second one."""
    member = make_member("Same Row Member", dob="2010-01-01")
    created = make_registration(member["id"], "2026", "U16", "Started")
    before = _registration_row_count()

    services.update_registration(created["id"], member["id"], "2027", "U18", "Started")

    assert _registration_row_count() == before
    assert services.get_registration(created["id"])["id"] == created["id"]


def test_amend_registration_unknown_registration_rejected(make_member):
    """Amending a registration id that does not exist is refused."""
    member = make_member("Unknown Amendment Member", dob="2010-01-01")

    with pytest.raises(services.ServiceError) as exc_info:
        services.update_registration(99999, member["id"], "2026", "U16", "Started")

    assert "Registration not found" in str(exc_info.value)


@pytest.mark.parametrize(
    "season, age_group, status, expected_message",
    [
        ("", "U16", "Started", "Season is required."),
        ("2026", "", "Started", "Age group is required."),
        ("2026", "U16", "Bogus", "Invalid registration status."),
        ("2026", "U16", "", "Invalid registration status."),
        ("2026", "U16", None, "Invalid registration status."),
    ],
)
def test_amend_registration_invalid_values_rejected_and_nothing_changed(
    make_member, make_registration, season, age_group, status, expected_message
):
    """An invalid amendment is refused and leaves the stored row unchanged."""
    member = make_member("Rejected Amendment Member", dob="2010-01-01")
    created = make_registration(member["id"], "2026", "U16", "Started")

    with pytest.raises(ValueError) as exc_info:
        services.update_registration(created["id"], member["id"], season, age_group, status)

    assert expected_message in str(exc_info.value)
    row = _raw_registration(created["id"])
    assert (row["season"], row["age_group"], row["status"]) == ("2026", "U16", "Started")


def test_amend_registration_unknown_member_rejected_and_nothing_changed(
    make_member, make_registration
):
    """Re-pointing a registration at an unknown member is refused."""
    member = make_member("Rejected Retarget Member", dob="2010-01-01")
    created = make_registration(member["id"], "2026", "U16", "Started")

    with pytest.raises(services.ServiceError) as exc_info:
        services.update_registration(created["id"], 99999, "2026", "U16", "Started")

    assert "Member not found" in str(exc_info.value)
    assert _raw_registration(created["id"])["member_id"] == member["id"]


def test_amend_registration_does_not_change_the_member_record(
    make_member, make_registration
):
    """Amending a registration never modifies the member's own details."""
    member = make_member(
        "Unchanged Member", dob="2010-01-01", email="keep@example.com", phone="0400 000 111"
    )
    created = make_registration(member["id"], "2026", "U16", "Started")

    services.update_registration(created["id"], member["id"], "2027", "U18", "Started")

    reloaded = services.get_member(member["id"])
    assert reloaded["name"] == "Unchanged Member"
    assert reloaded["date_of_birth"] == "2010-01-01"
    assert reloaded["email"] == "keep@example.com"
    assert reloaded["phone"] == "0400 000 111"
    assert reloaded["status"] == "Active"


def test_amend_registration_does_not_change_other_registrations(
    make_member, make_registration
):
    """Amending one registration leaves another registration of that member alone."""
    member = make_member("Two Registration Member", dob="1990-01-01")
    first = make_registration(member["id"], "2025", "U14", "Complete")
    second = make_registration(member["id"], "2026", "U16", "Started")

    services.update_registration(second["id"], member["id"], "2027", "U18", "Started")

    untouched = _raw_registration(first["id"])
    assert (untouched["season"], untouched["age_group"], untouched["status"]) == (
        "2025",
        "U14",
        "Complete",
    )


def test_amend_registration_can_be_repointed_to_another_member(
    make_member, make_registration
):
    """The amend form can retarget a registration, which moves it between histories.

    The ``member_id`` field is editable in ``registration_form.html`` and the
    service writes it, so this is the implemented behaviour. It is asserted
    rather than changed because restricting it would be a new business rule;
    the wording question is recorded as S3-O3 in the defect log.
    """
    original = make_member("Original Registration Owner", dob="2010-01-01")
    other = make_member("New Registration Owner", dob="2010-01-01")
    created = make_registration(original["id"], "2026", "U16", "Started")

    updated = services.update_registration(created["id"], other["id"], "2026", "U16", "Started")

    assert updated["member_id"] == other["id"]
    assert services.member_registration_history(original["id"]) == []
    assert [r["id"] for r in services.member_registration_history(other["id"])] == [created["id"]]
    # Both member records are untouched apart from the registration link.
    assert services.get_member(original["id"])["name"] == "Original Registration Owner"
    assert services.get_member(other["id"])["name"] == "New Registration Owner"


def test_amend_registration_route_persists_and_shows_new_values(
    client, make_member, make_registration
):
    """Amending through the form shows the new values on the detail page."""
    member = make_member("Route Amend Member", dob="2010-01-01")
    created = make_registration(member["id"], "2026", "U16", "Started")

    response = client.post(
        f"/registrations/{created['id']}/edit",
        data={
            "member_id": str(member["id"]),
            "season": "2027",
            "age_group": "U18",
            "status": "Started",
        },
    )

    assert response.status_code == 302
    detail = client.get(f"/registrations/{created['id']}")
    assert b"2027" in detail.data
    assert b"U18" in detail.data
    assert _raw_registration(created["id"])["season"] == "2027"


def test_amend_registration_route_invalid_input_shows_feedback_and_changes_nothing(
    client, make_member, make_registration
):
    """A rejected amendment renders 400 with feedback and leaves the row unchanged."""
    member = make_member("Route Rejected Member", dob="2010-01-01")
    created = make_registration(member["id"], "2026", "U16", "Started")

    response = client.post(
        f"/registrations/{created['id']}/edit",
        data={
            "member_id": str(member["id"]),
            "season": "2026",
            "age_group": "U16",
            "status": "Bogus",
        },
    )

    assert response.status_code == 400
    assert b"Invalid registration status." in response.data
    row = _raw_registration(created["id"])
    assert (row["season"], row["age_group"], row["status"]) == ("2026", "U16", "Started")


def test_amend_registration_form_is_prepopulated(client, make_member, make_registration):
    """The amend form loads the stored values rather than an empty form."""
    member = make_member("Prepopulated Member", dob="2010-01-01")
    created = make_registration(member["id"], "2026", "U16", "Started")

    response = client.get(f"/registrations/{created['id']}/edit")

    assert response.status_code == 200
    assert b"Amend Registration" in response.data
    assert b'value="2026"' in response.data
    assert b'value="U16"' in response.data


def test_amend_unknown_registration_route_redirects_with_feedback(client):
    """Amending an unknown registration id redirects instead of erroring."""
    response = client.get("/registrations/99999/edit", follow_redirects=True)

    assert response.status_code == 200
    assert b"Registration not found." in response.data


# ---------------------------------------------------------------------------
# MSD426GXUST25-12 — Withdraw Registration
# ---------------------------------------------------------------------------

def test_withdraw_registration_sets_withdrawn_status(make_member, make_registration):
    """Withdrawing changes the status to ``Withdrawn``."""
    member = make_member("Withdraw Member", dob="2010-01-01")
    created = make_registration(member["id"], "2026", "U16", "Started")

    withdrawn = services.withdraw_registration(created["id"])

    assert withdrawn["status"] == "Withdrawn"
    assert _raw_registration(created["id"])["status"] == "Withdrawn"


@pytest.mark.parametrize("starting_status", ["Started", "Complete"])
def test_withdraw_registration_from_either_status(
    make_member, make_registration, starting_status
):
    """A Started or Complete registration can both be withdrawn."""
    member = make_member(f"Withdraw From {starting_status}", dob="1990-01-01")
    created = make_registration(member["id"], "2026", "Seniors", starting_status)

    withdrawn = services.withdraw_registration(created["id"])

    assert withdrawn["status"] == "Withdrawn"


def test_withdraw_registration_keeps_the_row_and_its_details(
    make_member, make_registration
):
    """Withdrawal is a status change, never a delete; the details are retained."""
    member = make_member("Retained Withdrawal Member", dob="2010-01-01")
    created = make_registration(member["id"], "2026", "U16", "Started")
    before = _registration_row_count()

    services.withdraw_registration(created["id"])

    assert _registration_row_count() == before
    row = _raw_registration(created["id"])
    assert row is not None
    assert row["id"] == created["id"]
    assert row["member_id"] == member["id"]
    assert row["season"] == "2026"
    assert row["age_group"] == "U16"


def test_withdrawn_registration_remains_in_member_history(make_member, make_registration):
    """A withdrawn registration is still returned by the member's history."""
    member = make_member("Withdrawn History Member", dob="2010-01-01")
    created = make_registration(member["id"], "2026", "U16", "Started")

    services.withdraw_registration(created["id"])

    history = services.member_registration_history(member["id"])
    assert len(history) == 1
    assert history[0]["id"] == created["id"]
    assert history[0]["season"] == "2026"
    assert history[0]["status"] == "Withdrawn"


def test_withdraw_registration_is_idempotent(make_member, make_registration):
    """Withdrawing twice leaves one withdrawn record, not a duplicate or an error."""
    member = make_member("Double Withdraw Member", dob="2010-01-01")
    created = make_registration(member["id"], "2026", "U16", "Started")
    before = _registration_row_count()

    services.withdraw_registration(created["id"])
    services.withdraw_registration(created["id"])

    assert _registration_row_count() == before
    assert services.get_registration(created["id"])["status"] == "Withdrawn"


def test_withdraw_unknown_registration_rejected(make_member):
    """Withdrawing an unknown registration id is refused."""
    member = make_member("Unknown Withdraw Member", dob="2010-01-01")
    before = _registration_row_count()

    with pytest.raises(services.ServiceError) as exc_info:
        services.withdraw_registration(99999)

    assert "Registration not found" in str(exc_info.value)
    assert _registration_row_count() == before
    assert services.member_registration_history(member["id"]) == []


def test_withdraw_one_registration_leaves_the_other_alone(make_member, make_registration):
    """Withdrawing one registration does not withdraw another one."""
    member = make_member("Two Membership Member", dob="1990-01-01")
    first = make_registration(member["id"], "2025", "U14", "Complete")
    second = make_registration(member["id"], "2026", "U16", "Started")

    services.withdraw_registration(second["id"])

    assert services.get_registration(first["id"])["status"] == "Complete"
    assert services.get_registration(second["id"])["status"] == "Withdrawn"


def test_withdraw_registration_does_not_change_the_member_record(
    make_member, make_registration
):
    """Withdrawing a registration leaves the member record untouched."""
    member = make_member("Untouched By Withdrawal", dob="2010-01-01", email="w@example.com")
    created = make_registration(member["id"], "2026", "U16", "Started")

    services.withdraw_registration(created["id"])

    reloaded = services.get_member(member["id"])
    assert reloaded["status"] == "Active"
    assert reloaded["email"] == "w@example.com"


def test_withdraw_registration_route_persists_and_shows_status(
    client, make_member, make_registration
):
    """Withdrawing through the form persists and is shown on the detail page."""
    member = make_member("Route Withdraw Member", dob="2010-01-01")
    created = make_registration(member["id"], "2026", "U16", "Started")

    response = client.post(f"/registrations/{created['id']}/withdraw")

    assert response.status_code == 302
    detail = client.get(f"/registrations/{created['id']}")
    assert detail.status_code == 200
    assert b"Withdrawn" in detail.data
    assert b"This registration has been withdrawn" in detail.data
    # The withdraw button is no longer offered once the registration is withdrawn.
    assert b"Withdraw Registration" not in detail.data
    assert _raw_registration(created["id"])["status"] == "Withdrawn"


def test_withdraw_unknown_registration_route_handled_safely(client):
    """The withdraw route for an unknown id redirects with a friendly message."""
    response = client.post("/registrations/99999/withdraw", follow_redirects=True)

    assert response.status_code == 200
    assert b"Registration not found." in response.data


def test_withdrawn_registration_still_visible_in_member_history_page(
    client, make_member, make_registration
):
    """The member page keeps showing a withdrawn registration."""
    member = make_member("Page Withdrawn Member", dob="2010-01-01")
    created = make_registration(member["id"], "2026", "U16", "Started")
    services.withdraw_registration(created["id"])

    page = client.get(f"/members/{member['id']}")

    assert page.status_code == 200
    assert b"Withdrawn" in page.data
    assert b"2026" in page.data
    assert b"No registrations on record" not in page.data


# ---------------------------------------------------------------------------
# MSD426GXUST25-13 — View Member Registration History
# ---------------------------------------------------------------------------

def test_registration_history_returns_the_members_own_registrations(
    make_member, make_registration
):
    """History returns every registration belonging to that member."""
    member = make_member("History Owner", dob="1990-01-01")
    make_registration(member["id"], "2025", "U14", "Complete")
    make_registration(member["id"], "2026", "U16", "Started")

    history = services.member_registration_history(member["id"])

    assert len(history) == 2
    assert {r["season"] for r in history} == {"2025", "2026"}
    assert {r["status"] for r in history} == {"Complete", "Started"}
    assert {r["age_group"] for r in history} == {"U14", "U16"}


def test_registration_history_rows_expose_the_displayed_fields(
    make_member, make_registration
):
    """Each history row carries the fields the member page renders."""
    member = make_member("History Fields Member", dob="2010-01-01")
    created = make_registration(member["id"], "2026", "U16", "Started")

    row = services.member_registration_history(member["id"])[0]

    assert row["id"] == created["id"]
    assert row["member_id"] == member["id"]
    assert row["season"] == "2026"
    assert row["age_group"] == "U16"
    assert row["status"] == "Started"


def test_registration_history_is_newest_season_first(make_member, make_registration):
    """History is ordered by season descending, then by id descending."""
    member = make_member("History Order Member", dob="1990-01-01")
    make_registration(member["id"], "2024", "U12", "Complete")
    make_registration(member["id"], "2026", "U16", "Started")
    make_registration(member["id"], "2025", "U14", "Complete")

    seasons = [r["season"] for r in services.member_registration_history(member["id"])]

    assert seasons == ["2026", "2025", "2024"]


def test_registration_history_same_season_is_newest_id_first(
    make_member, make_registration
):
    """Within one season the most recently created registration is listed first."""
    member = make_member("Same Season Member", dob="2010-01-01")
    first = make_registration(member["id"], "2026", "U16", "Started")
    second = make_registration(member["id"], "2026", "U18", "Started")

    ids = [r["id"] for r in services.member_registration_history(member["id"])]

    assert ids == [second["id"], first["id"]]


def test_registration_history_is_empty_for_a_member_without_registrations(make_member):
    """A member with no registrations has an empty history, not an error."""
    member = make_member("No History Member", dob="2010-01-01")

    assert services.member_registration_history(member["id"]) == []


def test_registration_history_is_isolated_between_members(
    make_member, make_registration
):
    """One member's history never contains another member's registrations."""
    first = make_member("Isolated History One", dob="2010-01-01")
    second = make_member("Isolated History Two", dob="2011-01-01")
    make_registration(first["id"], "2026", "U16", "Started")
    make_registration(second["id"], "2027", "U18", "Started")

    first_history = services.member_registration_history(first["id"])
    second_history = services.member_registration_history(second["id"])

    assert [r["season"] for r in first_history] == ["2026"]
    assert [r["season"] for r in second_history] == ["2027"]
    assert {r["member_id"] for r in first_history} == {first["id"]}
    assert {r["member_id"] for r in second_history} == {second["id"]}


def test_registration_history_of_unknown_member_is_empty():
    """An unknown member id yields no history rows rather than an error."""
    assert services.member_registration_history(99999) == []


def test_registration_history_is_not_shared_between_duplicate_names(
    make_member, make_registration
):
    """Members sharing a name still have separate registration histories."""
    first = make_member("Same Name Registrant", dob="2010-01-01")
    second = make_member("Same Name Registrant", dob="2011-01-01")
    make_registration(first["id"], "2026", "U16", "Started")

    assert len(services.member_registration_history(first["id"])) == 1
    assert services.member_registration_history(second["id"]) == []


def test_registration_history_page_shows_seasons_statuses_and_links(
    client, make_member, make_registration
):
    """The member page renders each history row with a link to its detail page."""
    member = make_member("History Page Member", dob="1990-01-01")
    complete = make_registration(member["id"], "2025", "U14", "Complete")
    withdrawn = make_registration(member["id"], "2026", "U16", "Started")
    services.withdraw_registration(withdrawn["id"])

    page = client.get(f"/members/{member['id']}")

    assert page.status_code == 200
    assert b"Registration History" in page.data
    assert b"2025" in page.data
    assert b"2026" in page.data
    assert b"Complete" in page.data
    assert b"Withdrawn" in page.data
    assert f"/registrations/{complete['id']}".encode() in page.data
    assert f"/registrations/{withdrawn['id']}".encode() in page.data


def test_registration_history_page_does_not_show_another_members_registration(
    client, make_member, make_registration
):
    """A member's page shows only that member's history rows."""
    first = make_member("Page Isolation One", dob="2010-01-01")
    second = make_member("Page Isolation Two", dob="2011-01-01")
    make_registration(first["id"], "2026", "U16", "Started")
    other = make_registration(second["id"], "2027", "U18", "Started")

    page = client.get(f"/members/{first['id']}")

    assert page.status_code == 200
    assert b"2026" in page.data
    assert b"2027" not in page.data
    assert f"/registrations/{other['id']}".encode() not in page.data


def test_registration_history_empty_state_is_explained(client, make_member):
    """A member with no registrations sees a friendly empty state."""
    member = make_member("Empty History Page Member", dob="2010-01-01")

    page = client.get(f"/members/{member['id']}")

    assert page.status_code == 200
    assert b"No registrations on record for this member." in page.data


def test_registration_history_survives_member_deactivation(
    client, make_member, make_registration
):
    """History is still visible after the member is made Inactive."""
    member = make_member("Inactive History Member", dob="2010-01-01")
    make_registration(member["id"], "2026", "U16", "Started")
    services.set_member_inactive(member["id"])

    page = client.get(f"/members/{member['id']}")

    assert page.status_code == 200
    assert b"Inactive" in page.data
    assert b"2026" in page.data


def test_registration_detail_page_shows_the_member_link(client, make_member, make_registration):
    """A history row links to a detail page that links back to the member."""
    member = make_member("Detail Link Member", dob="2010-01-01")
    created = make_registration(member["id"], "2026", "U16", "Started")

    page = client.get(f"/registrations/{created['id']}")

    assert page.status_code == 200
    assert b"Detail Link Member" in page.data
    assert f"/members/{member['id']}".encode() in page.data


def test_registration_list_page_shows_each_members_registration(
    client, make_member, make_registration
):
    """The registrations list shows the registrations of every member."""
    first = make_member("List Member One", dob="2010-01-01")
    second = make_member("List Member Two", dob="2011-01-01")
    make_registration(first["id"], "2026", "U16", "Started")
    make_registration(second["id"], "2027", "U18", "Started")

    page = client.get("/registrations")

    assert page.status_code == 200
    assert b"List Member One" in page.data
    assert b"List Member Two" in page.data


# ---------------------------------------------------------------------------
# MSD426GXUST25-14 — Enforce Under-18 Guardian Rule
# ---------------------------------------------------------------------------

def test_under_18_without_guardian_cannot_complete(make_member, make_registration, junior_dob):
    """A junior with no linked guardian is blocked from completing a registration."""
    junior = make_member("Blocked Junior", dob=junior_dob)
    created = make_registration(junior["id"], "2026", "U16", "Started")

    with pytest.raises(services.ServiceError) as exc_info:
        services.update_registration(created["id"], junior["id"], "2026", "U16", "Complete")

    assert "under 18" in str(exc_info.value)
    assert "guardian" in str(exc_info.value)
    assert _raw_registration(created["id"])["status"] == "Started"
    assert services.get_registration(created["id"])["status"] == "Started"


def test_under_18_with_a_guardian_can_complete(
    make_member, make_guardian, make_registration, link_guardian, junior_dob
):
    """A junior with a linked guardian can complete a registration."""
    junior = make_member("Permitted Junior", dob=junior_dob)
    guardian = make_guardian("Permitting Guardian")
    link_guardian(guardian["id"], junior["id"])
    created = make_registration(junior["id"], "2026", "U16", "Started")

    completed = services.update_registration(created["id"], junior["id"], "2026", "U16", "Complete")

    assert completed["status"] == "Complete"
    assert _raw_registration(created["id"])["status"] == "Complete"


def test_can_complete_registration_reports_the_junior_rule(make_member, junior_dob):
    """The rule check reports the junior case without raising."""
    junior = make_member("Rule Check Junior", dob=junior_dob)

    allowed, message = services.can_complete_registration(junior["id"])

    assert allowed is False
    assert "under 18" in message


def test_can_complete_registration_allows_junior_with_guardian(
    make_member, make_guardian, link_guardian, junior_dob
):
    """The rule check allows a junior once a guardian is linked."""
    junior = make_member("Rule Check Linked Junior", dob=junior_dob)
    guardian = make_guardian("Rule Check Guardian")
    link_guardian(guardian["id"], junior["id"])

    allowed, message = services.can_complete_registration(junior["id"])

    assert allowed is True
    assert message == ""


def test_can_complete_registration_allows_adult_without_guardian(make_member, adult_dob):
    """An adult is not subject to the guardian requirement."""
    adult = make_member("Rule Check Adult", dob=adult_dob)

    allowed, message = services.can_complete_registration(adult["id"])

    assert allowed is True
    assert message == ""


def test_can_complete_registration_unknown_member_reports_not_found():
    """An unknown member id is reported through the rule check, not a crash."""
    allowed, message = services.can_complete_registration(99999)

    assert allowed is False
    assert "Member not found" in message


def test_under_18_guardian_rule_applies_when_created_as_complete(
    make_member, make_registration, junior_dob
):
    """Creating a junior registration directly as Complete is also blocked."""
    junior = make_member("Direct Complete Junior", dob=junior_dob)
    before = _registration_row_count()

    with pytest.raises(services.ServiceError) as exc_info:
        make_registration(junior["id"], "2026", "U16", "Complete")

    assert "under 18" in str(exc_info.value)
    assert _registration_row_count() == before


def test_under_18_guardian_rule_does_not_block_started_status(
    make_member, make_registration, junior_dob
):
    """The rule only guards completion; Started and Withdrawn are unaffected."""
    junior = make_member("Started Junior", dob=junior_dob)

    started = make_registration(junior["id"], "2026", "U16", "Started")
    withdrawn = services.withdraw_registration(started["id"])

    assert withdrawn["status"] == "Withdrawn"

    # Re-created as Started and amended back to Started without a guardian.
    again = make_registration(junior["id"], "2027", "U18", "Started")
    amended = services.update_registration(again["id"], junior["id"], "2027", "U18", "Started")
    assert amended["status"] == "Started"


def test_exactly_18_today_does_not_need_a_guardian(
    make_member, make_registration, exactly_18_dob
):
    """A member whose eighteenth birthday is today is treated as an adult."""
    member = make_member("Eighteenth Birthday Today", dob=exactly_18_dob)
    created = make_registration(member["id"], "2026", "Seniors", "Started")

    completed = services.update_registration(created["id"], member["id"], "2026", "Seniors", "Complete")

    assert completed["status"] == "Complete"


def test_one_day_before_eighteenth_birthday_still_needs_a_guardian(
    make_member, make_registration, just_under_18_dob
):
    """A member one day short of eighteen still needs a guardian."""
    member = make_member("Eighteenth Birthday Tomorrow", dob=just_under_18_dob)
    created = make_registration(member["id"], "2026", "U18", "Started")

    with pytest.raises(services.ServiceError) as exc_info:
        services.update_registration(created["id"], member["id"], "2026", "U18", "Complete")

    assert "under 18" in str(exc_info.value)
    assert _raw_registration(created["id"])["status"] == "Started"


def test_adult_registration_without_a_guardian_can_complete(
    make_member, make_registration, adult_dob
):
    """An adult with no guardian at all can complete a registration."""
    adult = make_member("Independent Adult", dob=adult_dob)
    created = make_registration(adult["id"], "2026", "Seniors", "Started")

    completed = services.update_registration(created["id"], adult["id"], "2026", "Seniors", "Complete")

    assert completed["status"] == "Complete"
    assert services.member_guardians(adult["id"]) == []


def test_guardian_linked_to_another_member_does_not_satisfy_the_rule(
    make_member, make_guardian, make_registration, link_guardian, junior_dob
):
    """The rule needs a guardian linked to *this* member, not to any member."""
    linked_junior = make_member("Already Linked Junior", dob=junior_dob)
    unlinked_junior = make_member("Still Unlinked Junior", dob=junior_dob)
    guardian = make_guardian("Busy Guardian")
    link_guardian(guardian["id"], linked_junior["id"])
    created = make_registration(unlinked_junior["id"], "2026", "U16", "Started")

    with pytest.raises(services.ServiceError):
        services.update_registration(created["id"], unlinked_junior["id"], "2026", "U16", "Complete")

    assert _raw_registration(created["id"])["status"] == "Started"


def test_linking_a_guardian_unblocks_a_blocked_registration(
    make_member, make_guardian, make_registration, link_guardian, junior_dob
):
    """A previously blocked completion succeeds after a guardian is linked."""
    junior = make_member("Unblocked Junior", dob=junior_dob)
    created = make_registration(junior["id"], "2026", "U16", "Started")

    with pytest.raises(services.ServiceError):
        services.update_registration(created["id"], junior["id"], "2026", "U16", "Complete")

    guardian = make_guardian("Late Guardian")
    link_guardian(guardian["id"], junior["id"])

    completed = services.update_registration(created["id"], junior["id"], "2026", "U16", "Complete")
    assert completed["status"] == "Complete"


def test_second_guardian_link_does_not_break_the_rule(
    make_member, make_guardian, make_registration, link_guardian, junior_dob
):
    """Two linked guardians satisfy the rule exactly as one does."""
    junior = make_member("Two Guardian Junior", dob=junior_dob)
    first = make_guardian("First Guardian")
    second = make_guardian("Second Guardian")
    link_guardian(first["id"], junior["id"])
    link_guardian(second["id"], junior["id"])
    created = make_registration(junior["id"], "2026", "U16", "Started")

    assert services.member_has_guardian(junior["id"]) is True
    completed = services.update_registration(created["id"], junior["id"], "2026", "U16", "Complete")
    assert completed["status"] == "Complete"


def test_unlinking_the_last_guardian_does_not_revert_a_complete_registration(
    make_member, make_guardian, make_registration, link_guardian, junior_dob
):
    """Unlinking afterwards leaves an already completed registration Complete.

    This is the confirmed behaviour recorded as S2-O2 (and repeated here as
    S3-O1): the rule is enforced at the moment of completion and is not
    re-evaluated when a link is removed. Asserted, not changed, because no
    written requirement states which behaviour is wanted.
    """
    junior = make_member("Unlinked After Completion", dob=junior_dob)
    guardian = make_guardian("Guardian Removed Later")
    link_guardian(guardian["id"], junior["id"])
    created = make_registration(junior["id"], "2026", "U16", "Started")
    services.update_registration(created["id"], junior["id"], "2026", "U16", "Complete")

    services.unlink_guardian_member(guardian["id"], junior["id"])

    assert services.member_has_guardian(junior["id"]) is False
    assert services.get_registration(created["id"])["status"] == "Complete"
    # A new completion attempt would now be blocked again.
    allowed, _ = services.can_complete_registration(junior["id"])
    assert allowed is False


def test_under_18_rule_message_is_the_documented_wording(make_member, junior_dob):
    """The refusal message is the application's existing wording, unchanged."""
    junior = make_member("Message Junior", dob=junior_dob)

    allowed, message = services.can_complete_registration(junior["id"])

    assert allowed is False
    assert message == services.JUNIOR_GUARDIAN_REQUIRED_MESSAGE
    assert message == (
        "Registration cannot be completed because a member under 18 must have "
        "at least one guardian."
    )


def test_under_18_rule_route_blocks_completion_and_keeps_started_status(
    client, make_member, make_registration, junior_dob
):
    """The amend form refuses completion for a junior with no guardian."""
    junior = make_member("Route Blocked Junior", dob=junior_dob)
    created = make_registration(junior["id"], "2026", "U16", "Started")

    response = client.post(
        f"/registrations/{created['id']}/edit",
        data={
            "member_id": str(junior["id"]),
            "season": "2026",
            "age_group": "U16",
            "status": "Complete",
        },
    )

    assert response.status_code == 400
    assert b"under 18" in response.data
    assert b"at least one guardian" in response.data
    assert _raw_registration(created["id"])["status"] == "Started"


def test_under_18_rule_route_allows_completion_once_linked(
    client, make_member, make_guardian, make_registration, link_guardian, junior_dob
):
    """The amend form allows completion for a junior whose guardian is linked."""
    junior = make_member("Route Allowed Junior", dob=junior_dob)
    guardian = make_guardian("Route Guardian")
    link_guardian(guardian["id"], junior["id"])
    created = make_registration(junior["id"], "2026", "U16", "Started")

    response = client.post(
        f"/registrations/{created['id']}/edit",
        data={
            "member_id": str(junior["id"]),
            "season": "2026",
            "age_group": "U16",
            "status": "Complete",
        },
    )

    assert response.status_code == 302
    assert _raw_registration(created["id"])["status"] == "Complete"


def test_under_18_rule_route_blocks_create_as_complete_for_a_junior(
    client, make_member, junior_dob
):
    """Creating a junior registration directly as Complete is refused by the route."""
    junior = make_member("Route Direct Junior", dob=junior_dob)
    before = _registration_row_count()

    response = client.post(
        "/registrations/new",
        data={
            "member_id": str(junior["id"]),
            "season": "2026",
            "age_group": "U16",
            "status": "Complete",
        },
    )

    assert response.status_code == 400
    assert b"under 18" in response.data
    assert _registration_row_count() == before


def test_under_18_rule_checked_against_the_new_member_when_retargeted(
    make_member, make_guardian, make_registration, link_guardian, junior_dob, adult_dob
):
    """Retargeting a registration to a junior applies the rule to that junior."""
    adult = make_member("Retarget Adult", dob=adult_dob)
    junior = make_member("Retarget Junior", dob=junior_dob)
    guardian = make_guardian("Retarget Guardian")
    link_guardian(guardian["id"], adult["id"])
    created = make_registration(adult["id"], "2026", "Seniors", "Started")

    # The adult (with a guardian) may complete.
    services.update_registration(created["id"], adult["id"], "2026", "Seniors", "Complete")

    # Re-pointing the same registration at a junior without a guardian is refused.
    with pytest.raises(services.ServiceError) as exc_info:
        services.update_registration(created["id"], junior["id"], "2026", "U16", "Complete")

    assert "under 18" in str(exc_info.value)
    row = _raw_registration(created["id"])
    assert row["member_id"] == adult["id"]
    assert row["status"] == "Complete"


@pytest.mark.parametrize(
    "invalid_dob, expected_message",
    [
        ("", "Date of birth is required."),
        ("   ", "Date of birth is required."),
        ("not-a-date", "YYYY-MM-DD"),
        ("2026-02-30", "YYYY-MM-DD"),
        ("2026-13-01", "YYYY-MM-DD"),
        ("01/02/2026", "YYYY-MM-DD"),
        ("2999-01-01", "cannot be in the future"),
        ("1800-01-01", "not plausible"),
    ],
)
def test_invalid_date_of_birth_is_refused_when_creating_a_member(
    invalid_dob, expected_message
):
    """Every invalid date-of-birth form is refused with a friendly message.

    None of these can reach the guardian rule, because a member with an invalid
    date of birth can never be created through the service layer.
    """
    before = _count("members")

    with pytest.raises(ValueError) as exc_info:
        services.create_member("Invalid Dob Member", invalid_dob, "", "", "")

    assert expected_message in str(exc_info.value)
    assert _count("members") == before


def test_age_calculation_boundary_is_deterministic():
    """The age calculation around the eighteenth birthday is exact."""
    from datetime import date

    from app import models

    # Day before the eighteenth birthday.
    assert models.calculate_age(date(2008, 3, 11), today=date(2026, 3, 10)) == 17
    # On the eighteenth birthday.
    assert models.calculate_age(date(2008, 3, 10), today=date(2026, 3, 10)) == 18
    # Day after.
    assert models.calculate_age(date(2008, 3, 9), today=date(2026, 3, 10)) == 18
    # A February 29 birthday in a non-leap year is treated as 28 February.
    assert models.calculate_age(date(2008, 2, 29), today=date(2026, 2, 28)) == 17
    assert models.calculate_age(date(2008, 2, 29), today=date(2026, 3, 1)) == 18


def test_under_18_rule_uses_the_stored_date_of_birth(
    make_member, make_registration, junior_dob, adult_dob
):
    """Two members with the same season but different ages are treated differently."""
    junior = make_member("Age Rule Junior", dob=junior_dob)
    adult = make_member("Age Rule Adult", dob=adult_dob)
    junior_reg = make_registration(junior["id"], "2026", "U16", "Started")
    adult_reg = make_registration(adult["id"], "2026", "Seniors", "Started")

    with pytest.raises(services.ServiceError):
        services.update_registration(junior_reg["id"], junior["id"], "2026", "U16", "Complete")

    completed = services.update_registration(adult_reg["id"], adult["id"], "2026", "Seniors", "Complete")
    assert completed["status"] == "Complete"


def test_under_18_rule_does_not_touch_the_guardian_link(
    make_member, make_registration, junior_dob
):
    """A blocked completion leaves the guardian relationship data untouched."""
    junior = make_member("No Side Effect Junior", dob=junior_dob)
    created = make_registration(junior["id"], "2026", "U16", "Started")
    guardians_before = _count("guardian_members")

    with pytest.raises(services.ServiceError):
        services.update_registration(created["id"], junior["id"], "2026", "U16", "Complete")

    assert services.member_guardians(junior["id"]) == []
    assert _count("guardian_members") == guardians_before
    assert _count("guardians") == 0


# ---------------------------------------------------------------------------
# S3-D1 regression — an unreadable stored date of birth must not crash
#
# Added with the S3-D1 fix. Previously date.fromisoformat raised an unhandled
# ValueError when a member row held a non-ISO date_of_birth (legacy data, a
# manual UPDATE, or a future import), which produced HTTP 500 on the member
# detail page and in the guardian rule. The rule must now refuse completion
# with a friendly message, and must never treat the member as an adult.
# ---------------------------------------------------------------------------

def _corrupt_stored_dob(member_id, value="not-a-date"):
    """Write an unreadable date of birth straight into the member row."""
    database.execute(
        "UPDATE members SET date_of_birth = ? WHERE id = ?", (value, member_id)
    )


def test_unreadable_stored_dob_is_refused_not_treated_as_adult(make_member):
    """The rule check refuses, and never silently allows, an unreadable birth date."""
    member = make_member("Corrupt Dob Member", dob="2014-01-01")
    _corrupt_stored_dob(member["id"])

    allowed, message = services.can_complete_registration(member["id"])

    assert allowed is False
    assert message == services.UNREADABLE_DATE_OF_BIRTH_MESSAGE
    assert "date of birth" in message.lower()


def test_unreadable_stored_dob_blocks_registration_creation(make_member, make_registration):
    """Creating a registration as Complete is refused with a friendly message."""
    member = make_member("Corrupt Dob Create", dob="2014-01-01")
    _corrupt_stored_dob(member["id"])
    before = _registration_row_count()

    with pytest.raises(services.ServiceError) as exc_info:
        make_registration(member["id"], "2026", "U16", "Complete")

    assert str(exc_info.value) == services.UNREADABLE_DATE_OF_BIRTH_MESSAGE
    assert _registration_row_count() == before


def test_unreadable_stored_dob_blocks_registration_amendment(
    make_member, make_registration
):
    """Amending a registration to Complete is refused and changes nothing."""
    member = make_member("Corrupt Dob Amend", dob="1990-01-01")
    created = make_registration(member["id"], "2026", "Seniors", "Started")
    _corrupt_stored_dob(member["id"])

    with pytest.raises(services.ServiceError) as exc_info:
        services.update_registration(created["id"], member["id"], "2026", "Seniors", "Complete")

    assert str(exc_info.value) == services.UNREADABLE_DATE_OF_BIRTH_MESSAGE
    assert _raw_registration(created["id"])["status"] == "Started"


def test_unreadable_stored_dob_still_allows_non_complete_statuses(
    make_member, make_registration
):
    """The guardian rule guards completion only, so Started still works."""
    member = make_member("Corrupt Dob Started", dob="2014-01-01")
    _corrupt_stored_dob(member["id"])

    created = make_registration(member["id"], "2026", "U16", "Started")
    assert created["status"] == "Started"

    amended = services.update_registration(
        created["id"], member["id"], "2027", "U18", "Started"
    )
    assert amended["season"] == "2027"


def test_unreadable_stored_dob_member_page_returns_200(client, make_member):
    """The member detail page renders instead of raising an unhandled error."""
    member = make_member("Corrupt Dob Page", dob="2014-01-01")
    _corrupt_stored_dob(member["id"])

    page = client.get(f"/members/{member['id']}")

    assert page.status_code == 200
    assert b"Corrupt Dob Page" in page.data
    # The age cannot be derived, so the page says so instead of inventing one.
    assert b"(age cannot be read from the stored date)" in page.data
    assert b"(age 12)" not in page.data


def test_unreadable_stored_dob_route_completion_shows_friendly_message(
    client, make_member, make_registration
):
    """The amend form returns 400 with the friendly message, not a 500."""
    member = make_member("Corrupt Dob Route", dob="1990-01-01")
    created = make_registration(member["id"], "2026", "Seniors", "Started")
    _corrupt_stored_dob(member["id"])

    response = client.post(
        f"/registrations/{created['id']}/edit",
        data={
            "member_id": str(member["id"]),
            "season": "2026",
            "age_group": "Seniors",
            "status": "Complete",
        },
    )

    assert response.status_code == 400
    assert b"date of birth" in response.data.lower()
    assert _raw_registration(created["id"])["status"] == "Started"


def test_unreadable_stored_dob_guardian_page_returns_200(
    client, make_member, make_guardian, link_guardian
):
    """The guardian page with a linked unreadable-date member also renders."""
    member = make_member("Corrupt Dob Linked", dob="2014-01-01")
    guardian = make_guardian("Corrupt Dob Guardian")
    link_guardian(guardian["id"], member["id"])
    _corrupt_stored_dob(member["id"])

    page = client.get(f"/guardians/{guardian['id']}")

    assert page.status_code == 200
    assert b"Corrupt Dob Linked" in page.data


def test_unreadable_stored_dob_leaves_other_data_intact(make_member, make_registration):
    """Repairing the rule must not damage unrelated member or registration data."""
    member = make_member("Corrupt Dob Intact", dob="1990-01-01", email="intact@example.com")
    first = make_registration(member["id"], "2025", "U14", "Complete")
    second = make_registration(member["id"], "2026", "Seniors", "Started")
    _corrupt_stored_dob(member["id"])

    services.can_complete_registration(member["id"])

    reloaded = services.get_member(member["id"])
    assert reloaded["name"] == "Corrupt Dob Intact"
    assert reloaded["email"] == "intact@example.com"
    assert reloaded["status"] == "Active"
    assert services.get_registration(first["id"])["status"] == "Complete"
    assert services.get_registration(second["id"])["status"] == "Started"
    assert len(services.member_registration_history(member["id"])) == 2


@pytest.mark.parametrize("bad_value", ["", "   ", "not-a-date", "2026-02-30", "01/02/2026"])
def test_unreadable_stored_dob_variants_are_all_handled(make_member, bad_value):
    """Every unreadable stored form is handled, not just one example."""
    member = make_member("Corrupt Dob Variant", dob="2014-01-01")
    _corrupt_stored_dob(member["id"], bad_value)

    allowed, message = services.can_complete_registration(member["id"])

    assert allowed is False
    assert message == services.UNREADABLE_DATE_OF_BIRTH_MESSAGE


def test_readable_stored_dob_behaviour_is_unchanged(make_member, junior_dob, adult_dob):
    """A valid stored date of birth keeps the original rule behaviour."""
    junior = make_member("Valid Junior", dob=junior_dob)
    adult = make_member("Valid Adult", dob=adult_dob)

    junior_allowed, junior_message = services.can_complete_registration(junior["id"])
    adult_allowed, adult_message = services.can_complete_registration(adult["id"])

    assert junior_allowed is False
    assert junior_message == services.JUNIOR_GUARDIAN_REQUIRED_MESSAGE
    assert adult_allowed is True
    assert adult_message == ""
