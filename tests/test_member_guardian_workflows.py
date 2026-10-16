"""Sprint 2 — Member and Guardian Management story tests.

This module adds targeted coverage for the seven Sprint 2 stories:

- MSD426GXUST25-2  Create Member Record
- MSD426GXUST25-3  Search and Update Member
- MSD426GXUST25-4  Deactivation of Members
- MSD426GXUST25-5  Support Duplicate Member Names
- MSD426GXUST25-6  Create, Search and Update Guardian
- MSD426GXUST25-7  Link Guardians to Junior Members
- MSD426GXUST25-8  Reflect Guardian Contact Updates

Every test asserts behaviour that was confirmed against the real application
before it was written, and each test runs against the isolated temporary
database supplied by ``tests/conftest.py``. No existing test was removed or
weakened to make these pass.

Scope note: this module covers the Member and Guardian Management epic only.
``test_deactivate_does_not_remove_team_placement`` uses the team fixtures, but
it asserts a *member* deactivation guarantee (that deactivation has no side
effects on unrelated records); it does not test team or player management.
Team and roster behaviour is out of scope for Sprint 2 and is deferred to the
Team and Roster Management epic (see ``docs/testing/sprint-2-defect-log.md``,
item S2-F1).
"""

import pytest

from app import database, services


# ---------------------------------------------------------------------------
# MSD426GXUST25-2 — Create Member Record
# ---------------------------------------------------------------------------

def test_member_create_persists_and_is_retrievable(make_member):
    """A created member is persisted and can be read back by its new id."""
    created = make_member("Persisted Person", dob="2010-05-20", email="p@example.com")

    fetched = services.get_member(created["id"])
    assert fetched is not None
    assert fetched["id"] == created["id"]
    assert fetched["name"] == "Persisted Person"
    assert fetched["date_of_birth"] == "2010-05-20"
    assert fetched["email"] == "p@example.com"


def test_member_create_route_redirects_to_viewable_detail(client):
    """Creating a member through the form redirects to a detail page showing it."""
    response = client.post(
        "/members/new",
        data={"name": "Route Created", "date_of_birth": "2011-02-03", "email": "rc@example.com"},
    )

    assert response.status_code == 302
    location = response.headers["Location"]
    assert location.startswith("/members/")

    detail = client.get(location)
    assert detail.status_code == 200
    assert b"Route Created" in detail.data
    assert b"rc@example.com" in detail.data
    # Success feedback is shown on the redirect target.
    assert b"created." in detail.data


@pytest.mark.parametrize(
    "payload, expected_message",
    [
        ({"name": "", "date_of_birth": "2010-01-01"}, b"Name is required."),
        ({"name": "No Date"}, b"Date of birth is required."),
        ({"name": "Bad Date", "date_of_birth": "not-a-date"}, b"YYYY-MM-DD"),
        ({"name": "Future", "date_of_birth": "2999-01-01"}, b"cannot be in the future"),
        (
            {"name": "Bad Email", "date_of_birth": "2010-01-01", "email": "nope"},
            b"Email address is not valid.",
        ),
    ],
)
def test_member_create_invalid_input_shows_feedback_and_stores_nothing(
    client, payload, expected_message
):
    """Invalid submissions are rejected with feedback and create no record."""
    response = client.post("/members/new", data=payload)

    assert response.status_code == 400
    assert expected_message in response.data
    # The failed submission must not have created a partial record.
    assert services.list_members() == []


# ---------------------------------------------------------------------------
# MSD426GXUST25-3 — Search and Update Member
# ---------------------------------------------------------------------------

def test_member_search_is_partial_and_case_insensitive(make_member):
    """Search matches on a partial name regardless of case."""
    make_member("Jonathan Smithson")
    make_member("Jane Doe")

    for term in ("jon", "JON", "smith", "athan smith"):
        results = services.list_members(term)
        assert [r["name"] for r in results] == ["Jonathan Smithson"], term


def test_member_search_route_returns_only_matches(client, make_member):
    """The /members?q= page lists matching members only."""
    make_member("Findable Fiona")
    make_member("Hidden Harry")

    response = client.get("/members?q=Fiona")

    assert response.status_code == 200
    assert b"Findable Fiona" in response.data
    assert b"Hidden Harry" not in response.data


def test_member_update_persists_after_reload(make_member):
    """An update is stored and visible when the member is read again."""
    member = make_member("Before Update")

    services.update_member(
        member["id"], "After Update", "1990-06-15", "after@example.com", "0400 123 456", "9 New St"
    )

    reloaded = services.get_member(member["id"])
    assert reloaded["name"] == "After Update"
    assert reloaded["date_of_birth"] == "1990-06-15"
    assert reloaded["email"] == "after@example.com"
    assert reloaded["phone"] == "0400 123 456"
    assert reloaded["address"] == "9 New St"


def test_member_update_route_persists_and_shows_new_values(client, make_member):
    """The edit form saves changes that then appear on the detail page."""
    member = make_member("Editable Ed")

    response = client.post(
        f"/members/{member['id']}/edit",
        data={
            "name": "Edited Ed",
            "date_of_birth": "1992-03-04",
            "email": "edited@example.com",
            "phone": "0400 777 888",
            "address": "12 Edit Ave",
        },
    )

    assert response.status_code == 302
    detail = client.get(f"/members/{member['id']}")
    assert b"Edited Ed" in detail.data
    assert b"edited@example.com" in detail.data


def test_member_update_preserves_status(make_member):
    """Updating details must not silently reset an Inactive member to Active."""
    member = make_member("Inactive Editor")
    services.set_member_inactive(member["id"])

    updated = services.update_member(
        member["id"], "Still Inactive", "1990-01-01", "", "", ""
    )

    assert updated["status"] == "Inactive"


def test_member_update_with_invalid_input_changes_nothing(make_member):
    """A rejected update leaves the stored record exactly as it was."""
    member = make_member("Keep My Data", email="original@example.com")

    with pytest.raises(ValueError):
        services.update_member(member["id"], "Changed", "not-a-date", "", "", "")

    reloaded = services.get_member(member["id"])
    assert reloaded["name"] == "Keep My Data"
    assert reloaded["email"] == "original@example.com"


def test_member_update_invalid_input_shows_feedback(client, make_member):
    """The edit route reports the problem instead of saving bad data."""
    member = make_member("Feedback Member")

    response = client.post(
        f"/members/{member['id']}/edit",
        data={"name": "Nope", "date_of_birth": "still-not-a-date"},
    )

    assert response.status_code == 400
    assert b"valid date" in response.data
    assert services.get_member(member["id"])["name"] == "Feedback Member"


def test_member_update_unknown_id_is_handled_safely():
    """Unknown member ids raise a friendly error rather than crashing."""
    with pytest.raises(services.ServiceError):
        services.update_member(99999, "Ghost", "1990-01-01", "", "", "")


def test_member_update_unknown_id_redirects_with_feedback(client):
    """Editing a missing member redirects to the list instead of erroring."""
    response = client.get("/members/99999/edit")

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/members")

    followed = client.get("/members/99999/edit", follow_redirects=True)
    assert b"Member not found." in followed.data


# ---------------------------------------------------------------------------
# MSD426GXUST25-4 — Deactivation of Members
# ---------------------------------------------------------------------------

def test_deactivate_route_updates_target_member_only(client, make_member):
    """Deactivating one member leaves every other member Active."""
    target = make_member("Target Member")
    bystander = make_member("Bystander Member")

    response = client.post(f"/members/{target['id']}/deactivate")

    assert response.status_code == 302
    assert services.get_member(target["id"])["status"] == "Inactive"
    assert services.get_member(bystander["id"])["status"] == "Active"


def test_deactivate_status_persists_and_is_shown(client, make_member):
    """The Inactive status persists and is displayed on the detail page."""
    member = make_member("Persisted Inactive")

    client.post(f"/members/{member['id']}/deactivate")
    detail = client.get(f"/members/{member['id']}")

    assert services.get_member(member["id"])["status"] == "Inactive"
    assert b"Inactive" in detail.data


def test_deactivate_preserves_registrations_and_guardians(make_member, make_guardian,
                                                          link_guardian, make_registration,
                                                          junior_dob):
    """Deactivation is a soft change: history and guardian links survive."""
    junior = make_member("Junior Deactivate", dob=junior_dob)
    guardian = make_guardian("Deactivate Guardian")
    link_guardian(guardian["id"], junior["id"])
    registration = make_registration(junior["id"], "2026", "U16", "Started")

    services.set_member_inactive(junior["id"])

    assert services.get_member(junior["id"]) is not None
    assert services.member_registration_history(junior["id"]) == [
        {"id": registration["id"], "member_id": junior["id"], "season": "2026",
         "age_group": "U12", "status": "Started"}
    ]
    assert [g["id"] for g in services.member_guardians(junior["id"])] == [guardian["id"]]


def test_deactivate_does_not_remove_team_placement(make_member, make_registration,
                                                   make_team):
    """Deactivation must not delete unrelated records such as team placement."""
    member = make_member("Deactivated Player")
    team = make_team("2026", "Tigers", "Seniors")
    make_registration(member["id"], "2026", "U16", "Complete")  # auto-assigns

    services.set_member_inactive(member["id"])

    assert [p["name"] for p in services.team_players(team["id"])] == ["Deactivated Player"]
    assert services.get_team(team["id"]) is not None


def test_deactivate_is_idempotent_and_reactivatable(make_member):
    """Repeating deactivation is consistent, and activation reverses it."""
    member = make_member("Toggle Member")

    first = services.set_member_inactive(member["id"])
    second = services.set_member_inactive(member["id"])

    assert first["status"] == second["status"] == "Inactive"
    assert services.set_member_status(member["id"], "Active")["status"] == "Active"


def test_deactivate_unknown_member_is_handled_safely(client):
    """Deactivating a missing member is refused, not silently accepted."""
    with pytest.raises(services.ServiceError):
        services.set_member_inactive(99999)

    response = client.post("/members/99999/deactivate", follow_redirects=True)
    assert b"Member not found." in response.data


# ---------------------------------------------------------------------------
# MSD426GXUST25-5 — Support Duplicate Member Names
# ---------------------------------------------------------------------------

def test_duplicate_names_have_independent_identity_and_data(make_member):
    """Two members may share a name while keeping separate identity and data."""
    first = make_member("Alex Duplicate", dob="2000-01-01", email="first@example.com")
    second = make_member("Alex Duplicate", dob="2001-02-02", email="second@example.com")

    assert first["id"] != second["id"]
    assert services.get_member(first["id"])["email"] == "first@example.com"
    assert services.get_member(second["id"])["email"] == "second@example.com"
    assert services.get_member(first["id"])["date_of_birth"] == "2000-01-01"
    assert services.get_member(second["id"])["date_of_birth"] == "2001-02-02"


def test_duplicate_names_distinguishable_in_list_and_detail_views(client, make_member):
    """Both duplicates are listed, and each detail page shows only its own data."""
    first = make_member("Sam Duplicate", email="sam.one@example.com")
    second = make_member("Sam Duplicate", email="sam.two@example.com")

    listing = client.get("/members?q=Sam Duplicate")
    assert listing.data.count(b"Sam Duplicate") >= 2
    assert b"sam.one@example.com" in listing.data
    assert b"sam.two@example.com" in listing.data

    detail_one = client.get(f"/members/{first['id']}")
    detail_two = client.get(f"/members/{second['id']}")
    assert b"sam.one@example.com" in detail_one.data
    assert b"sam.two@example.com" not in detail_one.data
    assert b"sam.two@example.com" in detail_two.data
    assert b"sam.one@example.com" not in detail_two.data


def test_updating_one_duplicate_does_not_change_the_other(make_member):
    """Editing one of two identically named members leaves the other untouched."""
    first = make_member("Jordan Duplicate", email="jordan.one@example.com")
    second = make_member("Jordan Duplicate", email="jordan.two@example.com")

    services.update_member(
        first["id"], "Jordan Renamed", "1999-09-09", "jordan.changed@example.com", "", ""
    )

    untouched = services.get_member(second["id"])
    assert untouched["name"] == "Jordan Duplicate"
    assert untouched["email"] == "jordan.two@example.com"
    assert untouched["date_of_birth"] != "1999-09-09"


def test_duplicate_names_are_not_duplicate_registrations(make_member, make_registration):
    """Sharing a name says nothing about duplicate same-season registrations.

    Two same-named members each register for the same season: that is two
    legitimate registrations for two different people. This keeps the
    duplicate-name story separate from the open duplicate-registration
    question recorded as D1 in the Sprint 1 defect log.
    """
    first = make_member("Casey SameName")
    second = make_member("Casey SameName")

    reg_first = make_registration(first["id"], "2026", "U16", "Started")
    reg_second = make_registration(second["id"], "2026", "U16", "Started")

    assert reg_first["member_id"] != reg_second["member_id"]
    assert len(services.member_registration_history(first["id"])) == 1
    assert len(services.member_registration_history(second["id"])) == 1


# ---------------------------------------------------------------------------
# MSD426GXUST25-6 — Create, Search and Update Guardian
# ---------------------------------------------------------------------------

def test_guardian_create_persists_and_is_retrievable(make_guardian):
    """A created guardian is persisted with all of its contact details."""
    created = make_guardian("Persisted Guardian", "pg@example.com", "0400 111 222", "3 Park Rd")

    fetched = services.get_guardian(created["id"])
    assert fetched["name"] == "Persisted Guardian"
    assert fetched["email"] == "pg@example.com"
    assert fetched["phone"] == "0400 111 222"
    assert fetched["address"] == "3 Park Rd"


def test_guardian_create_route_redirects_to_viewable_detail(client):
    """Creating a guardian through the form redirects to a detail page showing it."""
    response = client.post(
        "/guardians/new",
        data={
            "name": "Route Guardian",
            "date_of_birth": "1980-05-05",
            "email": "rg@example.com",
            "phone": "0400 333 444",
        },
    )

    assert response.status_code == 302
    detail = client.get(response.headers["Location"])
    assert detail.status_code == 200
    assert b"Route Guardian" in detail.data
    assert b"rg@example.com" in detail.data


@pytest.mark.parametrize(
    "payload, expected_message",
    [
        ({"name": "", "date_of_birth": "1980-05-05"}, b"Name is required."),
        (
            {"name": "Bad Email", "date_of_birth": "1980-05-05", "email": "not-an-email"},
            b"Email address is not valid.",
        ),
    ],
)
def test_guardian_create_invalid_input_shows_feedback_and_stores_nothing(
    client, payload, expected_message
):
    """Invalid guardian submissions are rejected and create no record."""
    response = client.post("/guardians/new", data=payload)

    assert response.status_code == 400
    assert expected_message in response.data
    assert services.list_guardians() == []


def test_guardian_search_partial_and_case_insensitive(make_guardian):
    """Guardian search matches partial names regardless of case."""
    make_guardian("Margaret Guardian")
    make_guardian("Bob Helper")

    assert [g["name"] for g in services.list_guardians("marg")] == ["Margaret Guardian"]
    assert [g["name"] for g in services.list_guardians("HELPER")] == ["Bob Helper"]
    assert services.list_guardians("no-such-guardian") == []


def test_guardian_update_persists_after_reload(make_guardian):
    """Guardian updates persist and are visible when the record is re-read."""
    guardian = make_guardian("Before Guardian")

    services.update_guardian(
        guardian["id"], "After Guardian", "1980-05-05", "after@example.com",
        "0400 555 666", "7 New Rd"
    )

    reloaded = services.get_guardian(guardian["id"])
    assert reloaded["name"] == "After Guardian"
    assert reloaded["email"] == "after@example.com"
    assert reloaded["phone"] == "0400 555 666"
    assert reloaded["address"] == "7 New Rd"


def test_guardian_update_route_persists_and_shows_new_values(client, make_guardian):
    """The guardian edit route saves changes shown on the detail page."""
    guardian = make_guardian("Editable Guardian")

    response = client.post(
        f"/guardians/{guardian['id']}/edit",
        data={
            "name": "Edited Guardian",
            "date_of_birth": "1980-05-05",
            "email": "edited.guardian@example.com",
            "phone": "0400 999 000",
            "address": "5 Edit Rd",
        },
    )

    assert response.status_code == 302
    detail = client.get(f"/guardians/{guardian['id']}")
    assert b"Edited Guardian" in detail.data
    assert b"edited.guardian@example.com" in detail.data


def test_guardian_update_with_invalid_input_changes_nothing(make_guardian):
    """A rejected guardian update leaves the stored record unchanged."""
    guardian = make_guardian("Keep Guardian", "original@example.com")

    with pytest.raises(ValueError):
        services.update_guardian(guardian["id"], "Changed", "1980-05-05", "bad-email", "", "")

    reloaded = services.get_guardian(guardian["id"])
    assert reloaded["name"] == "Keep Guardian"
    assert reloaded["email"] == "original@example.com"


def test_guardian_update_unknown_id_is_handled_safely(client):
    """Unknown guardian ids raise a friendly error and redirect safely."""
    with pytest.raises(services.ServiceError):
        services.update_guardian(99999, "Ghost Guardian", "1980-05-05", "", "", "")

    response = client.get("/guardians/99999/edit", follow_redirects=True)
    assert b"Guardian not found." in response.data


# ---------------------------------------------------------------------------
# MSD426GXUST25-7 — Link Guardians to Junior Members
# ---------------------------------------------------------------------------

def test_link_guardian_to_junior_persists_in_both_directions(make_member, make_guardian,
                                                             junior_dob):
    """A link is stored and visible from both the guardian and the member side."""
    junior = make_member("Linked Junior", dob=junior_dob)
    guardian = make_guardian("Linking Guardian")

    services.link_guardian_member(guardian["id"], junior["id"])

    assert [m["id"] for m in services.guardian_linked_members(guardian["id"])] == [junior["id"]]
    assert [g["id"] for g in services.member_guardians(junior["id"])] == [guardian["id"]]
    assert services.member_has_guardian(junior["id"]) is True


def test_link_route_persists_and_is_visible_on_both_pages(client, make_member, make_guardian,
                                                          junior_dob):
    """Linking through the form is reflected on the guardian and member pages."""
    junior = make_member("Viewable Junior", dob=junior_dob)
    guardian = make_guardian("Viewable Guardian")

    response = client.post(
        f"/guardians/{guardian['id']}/link", data={"member_id": str(junior["id"])}
    )

    assert response.status_code == 302
    guardian_page = client.get(f"/guardians/{guardian['id']}")
    assert b"Viewable Junior" in guardian_page.data

    member_page = client.get(f"/members/{junior['id']}")
    assert b"Viewable Guardian" in member_page.data


@pytest.mark.parametrize(
    "guardian_id, member_id",
    [
        (99999, 1),   # guardian does not exist
        (1, 99999),   # member does not exist
    ],
)
def test_link_invalid_identifiers_rejected(guardian_id, member_id, make_member, make_guardian):
    """Invalid guardian or member identifiers are refused by the service layer."""
    make_member("Real Member")
    make_guardian("Real Guardian")

    with pytest.raises(services.ServiceError):
        services.link_guardian_member(guardian_id, member_id)


def test_link_route_without_member_choice_is_refused(client, make_guardian):
    """Submitting the link form with no member selected reports an error."""
    guardian = make_guardian("No Choice Guardian")

    response = client.post(f"/guardians/{guardian['id']}/link", data={}, follow_redirects=True)

    assert b"Please choose a member to link." in response.data


def test_duplicate_link_creates_one_relationship(make_member, make_guardian, junior_dob):
    """The same guardian/member pair cannot be linked twice."""
    junior = make_member("No Double Link", dob=junior_dob)
    guardian = make_guardian("Once Guardian")
    services.link_guardian_member(guardian["id"], junior["id"])

    with pytest.raises(services.ServiceError):
        services.link_guardian_member(guardian["id"], junior["id"])

    assert len(services.guardian_linked_members(guardian["id"])) == 1


def test_shared_guardian_can_link_to_multiple_juniors(make_member, make_guardian, junior_dob):
    """One guardian may be responsible for more than one junior."""
    guardian = make_guardian("Shared Parent")
    first = make_member("Shared Junior One", dob=junior_dob)
    second = make_member("Shared Junior Two", dob=junior_dob)

    services.link_guardian_member(guardian["id"], first["id"])
    services.link_guardian_member(guardian["id"], second["id"])

    assert {m["name"] for m in services.guardian_linked_members(guardian["id"])} == {
        "Shared Junior One",
        "Shared Junior Two",
    }


def test_unlink_removes_only_the_relationship(make_member, make_guardian, junior_dob):
    """Unlinking removes the link while keeping both member and guardian."""
    junior = make_member("Unlink Junior", dob=junior_dob)
    guardian = make_guardian("Unlink Guardian")
    services.link_guardian_member(guardian["id"], junior["id"])

    assert services.unlink_guardian_member(guardian["id"], junior["id"]) is True

    assert services.guardian_linked_members(guardian["id"]) == []
    assert services.member_guardians(junior["id"]) == []
    assert services.get_member(junior["id"]) is not None
    assert services.get_guardian(guardian["id"]) is not None


def test_unlink_reports_when_nothing_was_linked(make_member, make_guardian):
    """Unlinking a pair that was never linked reports that nothing changed.

    This covers Sprint 1 defect D3: the operation must not claim success when
    no relationship existed.
    """
    member = make_member("Never Linked")
    guardian = make_guardian("Never Linked Guardian")

    assert services.unlink_guardian_member(guardian["id"], member["id"]) is False
    assert services.get_member(member["id"]) is not None
    assert services.get_guardian(guardian["id"]) is not None


def test_unlink_route_reports_no_op_instead_of_success(client, make_member, make_guardian):
    """The unlink route must not flash success when no link existed (D3)."""
    member = make_member("Unlinked Target")
    guardian = make_guardian("Unlinked Guardian")

    response = client.post(
        f"/guardians/{guardian['id']}/unlink/{member['id']}", follow_redirects=True
    )

    assert b"was not linked to this guardian" in response.data
    assert b"Member unlinked from guardian." not in response.data


def test_unlink_route_reports_success_when_link_removed(client, make_member, make_guardian,
                                                        junior_dob):
    """The unlink route still confirms success when a real link is removed."""
    junior = make_member("Real Unlink Junior", dob=junior_dob)
    guardian = make_guardian("Real Unlink Guardian")
    services.link_guardian_member(guardian["id"], junior["id"])

    response = client.post(
        f"/guardians/{guardian['id']}/unlink/{junior['id']}", follow_redirects=True
    )

    assert b"Member unlinked from guardian." in response.data
    assert b"was not linked to this guardian" not in response.data


def test_unlink_unknown_identifiers_is_handled_safely(make_member, make_guardian):
    """Unlinking with a missing guardian or member is refused safely."""
    make_member("Existing Member")
    make_guardian("Existing Guardian")

    with pytest.raises(services.ServiceError):
        services.unlink_guardian_member(99999, 1)
    with pytest.raises(services.ServiceError):
        services.unlink_guardian_member(1, 99999)


def test_under_18_rule_requires_guardian_before_completion(make_member, make_registration,
                                                           junior_dob):
    """The Sprint 1 under-18 guardian rule still blocks completion (unchanged)."""
    junior = make_member("Rule Junior", dob=junior_dob)
    registration = make_registration(junior["id"], "2026", "U16", "Started")

    with pytest.raises(services.ServiceError) as exc_info:
        services.update_registration(
            registration["id"], junior["id"], "2026", "U16", "Complete"
        )

    assert "under 18" in str(exc_info.value)
    assert services.get_registration(registration["id"])["status"] == "Started"


def test_under_18_rule_satisfied_once_guardian_linked(make_member, make_guardian,
                                                      make_registration, junior_dob):
    """Linking a guardian unblocks completing the junior's registration."""
    junior = make_member("Rule Junior Two", dob=junior_dob)
    guardian = make_guardian("Rule Guardian")
    registration = make_registration(junior["id"], "2026", "U16", "Started")

    services.link_guardian_member(guardian["id"], junior["id"])
    completed = services.update_registration(
        registration["id"], junior["id"], "2026", "U16", "Complete"
    )

    assert completed["status"] == "Complete"


# ---------------------------------------------------------------------------
# MSD426GXUST25-8 — Reflect Guardian Contact Updates
# ---------------------------------------------------------------------------

def test_guardian_contact_update_reflected_on_member_page(client, make_member, make_guardian,
                                                          link_guardian, junior_dob):
    """The member detail page shows the guardian's current contact details."""
    junior = make_member("Contact Junior", dob=junior_dob)
    guardian = make_guardian("Contact Guardian", email="stale@example.com", phone="0400 000 111")
    link_guardian(guardian["id"], junior["id"])

    services.update_guardian(
        guardian["id"], "Contact Guardian", "1980-05-05", "current@example.com",
        "0400 222 333", "8 New Rd"
    )

    page = client.get(f"/members/{junior['id']}")
    assert b"current@example.com" in page.data
    assert b"0400 222 333" in page.data
    assert b"stale@example.com" not in page.data


def test_guardian_contact_update_reflected_on_guardian_pages(client, make_guardian):
    """The guardian detail and list pages show the updated contact details."""
    guardian = make_guardian("Page Guardian", email="stale@example.com")
    services.update_guardian(
        guardian["id"], "Page Guardian", "1980-05-05", "current@example.com",
        "0400 444 555", ""
    )

    detail = client.get(f"/guardians/{guardian['id']}")
    assert b"current@example.com" in detail.data
    assert b"stale@example.com" not in detail.data

    listing = client.get("/guardians")
    assert b"current@example.com" in listing.data
    assert b"stale@example.com" not in listing.data


def test_guardian_update_keeps_relationships_intact(make_member, make_guardian, junior_dob):
    """A contact update must not break existing guardian-member relationships."""
    junior = make_member("Relationship Junior", dob=junior_dob)
    guardian = make_guardian("Relationship Guardian")
    services.link_guardian_member(guardian["id"], junior["id"])

    services.update_guardian(
        guardian["id"], "Renamed Guardian", "1980-05-05", "new@example.com",
        "0400 666 777", "1 New Rd"
    )

    assert [m["id"] for m in services.guardian_linked_members(guardian["id"])] == [junior["id"]]
    assert [g["id"] for g in services.member_guardians(junior["id"])] == [guardian["id"]]


def test_updating_one_guardian_does_not_change_another(make_member, make_guardian, junior_dob):
    """Updating one guardian leaves every other guardian's data untouched."""
    junior = make_member("Two Guardian Junior", dob=junior_dob)
    first = make_guardian("First Guardian", email="first@example.com")
    second = make_guardian("Second Guardian", email="second@example.com")
    services.link_guardian_member(first["id"], junior["id"])
    services.link_guardian_member(second["id"], junior["id"])

    services.update_guardian(
        first["id"], "First Guardian", "1980-05-05", "first.changed@example.com", "", ""
    )

    assert services.get_guardian(second["id"])["email"] == "second@example.com"
    emails = {g["email"] for g in services.member_guardians(junior["id"])}
    assert emails == {"first.changed@example.com", "second@example.com"}


def test_guardian_contact_is_read_from_the_shared_record(make_guardian, make_member,
                                                         junior_dob):
    """Contact details come from the one guardian row, not from duplicated data.

    The schema stores guardian contact details only in ``guardians``;
    ``guardian_members`` holds no contact columns. This test guards against a
    future change that would introduce stale duplicated contact data.
    """
    columns = {
        row["name"]
        for row in database.query_all("PRAGMA table_info(guardian_members)")
    }
    assert columns == {"guardian_id", "member_id"}

    junior = make_member("Schema Junior", dob=junior_dob)
    guardian = make_guardian("Schema Guardian", email="sole@example.com")
    services.link_guardian_member(guardian["id"], junior["id"])

    services.update_guardian(
        guardian["id"], "Schema Guardian", "1980-05-05", "sole.updated@example.com", "", ""
    )

    assert services.member_guardians(junior["id"])[0]["email"] == "sole.updated@example.com"
