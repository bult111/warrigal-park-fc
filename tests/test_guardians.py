"""Guardian management tests."""

from app import services


def test_create_guardian(make_guardian):
    guardian = make_guardian("Jane Guardian", "jane@example.com", "0400 111 222", "2 Park Rd")
    assert guardian["id"] is not None
    assert guardian["name"] == "Jane Guardian"


def test_search_guardian(make_guardian):
    make_guardian("Jane Guardian")
    make_guardian("Bob Helper")
    results = services.list_guardians("Jane")
    assert len(results) == 1
    assert results[0]["name"] == "Jane Guardian"


def test_update_guardian(make_guardian):
    guardian = make_guardian("Old Guardian")
    updated = services.update_guardian(
        guardian["id"], "New Guardian", "new@example.com", "0400 999 999", "9 Park Rd"
    )
    assert updated["name"] == "New Guardian"
    assert updated["email"] == "new@example.com"


def test_one_guardian_linked_to_multiple_juniors(make_guardian, make_member, link_guardian, junior_dob):
    guardian = make_guardian("Shared Guardian")
    junior_one = make_member("Junior One", dob=junior_dob)
    junior_two = make_member("Junior Two", dob=junior_dob)

    link_guardian(guardian["id"], junior_one["id"])
    link_guardian(guardian["id"], junior_two["id"])

    linked = services.guardian_linked_members(guardian["id"])
    assert len(linked) == 2
    assert {m["name"] for m in linked} == {"Junior One", "Junior Two"}


def test_guardian_contact_update_reflected(make_guardian, make_member, link_guardian, junior_dob):
    guardian = make_guardian("Parent", "old@example.com")
    junior = make_member("Junior", dob=junior_dob)
    link_guardian(guardian["id"], junior["id"])

    services.update_guardian(
        guardian["id"], "Parent", "new@example.com", "0400 000 000", "1 Park Rd"
    )

    # The member's guardian list must show the updated contact details.
    guardians = services.member_guardians(junior["id"])
    assert len(guardians) == 1
    assert guardians[0]["email"] == "new@example.com"


def test_unlink_guardian(make_guardian, make_member, link_guardian, junior_dob):
    guardian = make_guardian("Unlink Me")
    junior = make_member("Junior", dob=junior_dob)
    link_guardian(guardian["id"], junior["id"])
    assert len(services.guardian_linked_members(guardian["id"])) == 1

    services.unlink_guardian_member(guardian["id"], junior["id"])

    assert services.guardian_linked_members(guardian["id"]) == []
