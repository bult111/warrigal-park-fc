"""Member management tests."""

import pytest

from app import services


def test_create_member(make_member):
    member = make_member("Alice Example", dob="2011-05-20", email="alice@example.com")
    assert member["id"] is not None
    assert member["name"] == "Alice Example"
    assert member["status"] == "Active"


def test_search_member(make_member):
    make_member("John Smith")
    make_member("Jane Doe")
    results = services.list_members("John")
    assert len(results) == 1
    assert results[0]["name"] == "John Smith"


def test_search_member_case_insensitive(make_member):
    make_member("John Smith")
    results = services.list_members("john")
    assert len(results) == 1


def test_duplicate_names_allowed(make_member):
    make_member("John Smith", email="one@example.com")
    make_member("John Smith", email="two@example.com")
    results = services.list_members("John Smith")
    # Both records must be returned; names are not unique identifiers.
    assert len(results) == 2
    assert {r["email"] for r in results} == {"one@example.com", "two@example.com"}


def test_update_member(make_member):
    member = make_member("Old Name")
    updated = services.update_member(
        member["id"], "New Name", "2000-01-01", "new@example.com", "0400 000 000", "1 Park Rd"
    )
    assert updated["name"] == "New Name"
    assert updated["email"] == "new@example.com"
    assert updated["phone"] == "0400 000 000"
    assert updated["address"] == "1 Park Rd"


def test_set_inactive(make_member):
    member = make_member("Someone")
    updated = services.set_member_inactive(member["id"])
    assert updated["status"] == "Inactive"
    # The record is a soft state change, not a delete.
    assert services.get_member(member["id"]) is not None


def test_set_inactive_nonexistent_member():
    with pytest.raises(services.ServiceError):
        services.set_member_inactive(99999)


def test_reactivate_member(make_member):
    member = make_member("Reactive")
    services.set_member_inactive(member["id"])
    assert services.get_member(member["id"])["status"] == "Inactive"

    reactivated = services.set_member_status(member["id"], "Active")
    assert reactivated["status"] == "Active"


def test_update_nonexistent_member_rejected():
    with pytest.raises(services.ServiceError):
        services.update_member(99999, "Ghost", "2000-01-01", "", "", "")


def test_search_no_results(make_member):
    make_member("John Smith")
    assert services.list_members("zzz-no-match") == []
