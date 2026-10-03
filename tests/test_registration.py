"""Registration management and under-18 guardian rule tests."""

import pytest

from app import services


def test_create_registration(make_member, make_registration):
    member = make_member("Reggie Member")
    reg = make_registration(member["id"], "2026", "U16")
    assert reg["id"] is not None
    assert reg["season"] == "2026"
    assert reg["age_group"] == "U16"
    assert reg["status"] == "Started"


def test_view_registration(make_member, make_registration):
    member = make_member("Reggie Member")
    reg = make_registration(member["id"], "2026", "U16")
    fetched = services.get_registration(reg["id"])
    assert fetched["member_id"] == member["id"]
    assert fetched["member_name"] == "Reggie Member"


def test_amend_registration(make_member, make_registration):
    member = make_member("Reggie Member")
    reg = make_registration(member["id"], "2026", "U16")
    updated = services.update_registration(reg["id"], member["id"], "2027", "U18", "Started")
    assert updated["season"] == "2027"
    assert updated["age_group"] == "U18"


def test_withdraw_registration(make_member, make_registration):
    member = make_member("Reggie Member")
    reg = make_registration(member["id"], "2026", "U16")
    withdrawn = services.withdraw_registration(reg["id"])
    assert withdrawn["status"] == "Withdrawn"


def test_registration_history(make_member, make_registration):
    member = make_member("History Member")
    make_registration(member["id"], "2025", "U14", "Complete")
    make_registration(member["id"], "2026", "U16", "Started")

    history = services.member_registration_history(member["id"])
    assert len(history) == 2
    seasons = {r["season"] for r in history}
    assert seasons == {"2025", "2026"}


# ---------------------------------------------------------------------------
# Under-18 guardian business rule (Phase 6)
# ---------------------------------------------------------------------------

def test_junior_without_guardian_rejected(make_member, make_registration, junior_dob):
    junior = make_member("Junior NoGuardian", dob=junior_dob)
    reg = make_registration(junior["id"], "2026", "U16", "Started")

    with pytest.raises(services.ServiceError) as exc_info:
        services.update_registration(reg["id"], junior["id"], "2026", "U16", "Complete")

    assert "under 18" in str(exc_info.value)
    # The registration must NOT have become Complete.
    assert services.get_registration(reg["id"])["status"] == "Started"


def test_junior_with_guardian_accepted(
    make_member, make_guardian, make_registration, link_guardian, junior_dob
):
    junior = make_member("Junior WithGuardian", dob=junior_dob)
    guardian = make_guardian("Supportive Parent")
    link_guardian(guardian["id"], junior["id"])
    reg = make_registration(junior["id"], "2026", "U16", "Started")

    updated = services.update_registration(reg["id"], junior["id"], "2026", "U16", "Complete")
    assert updated["status"] == "Complete"


def test_adult_without_guardian_accepted(make_member, make_registration, adult_dob):
    adult = make_member("Adult Member", dob=adult_dob)
    reg = make_registration(adult["id"], "2026", "Seniors", "Started")

    updated = services.update_registration(reg["id"], adult["id"], "2026", "Seniors", "Complete")
    assert updated["status"] == "Complete"


def test_adult_without_guardian_started_is_fine(make_member, make_registration, adult_dob):
    adult = make_member("Adult Member", dob=adult_dob)
    reg = make_registration(adult["id"], "2026", "Seniors", "Started")
    # Completing without a guardian is allowed for adults.
    assert services.can_complete_registration(adult["id"])[0] is True
    assert reg["status"] == "Started"


def test_junior_created_directly_complete_rejected(make_member, make_registration, junior_dob):
    """Creating a junior registration directly as Complete also needs a guardian."""
    junior = make_member("Junior Direct", dob=junior_dob)
    with pytest.raises(services.ServiceError):
        make_registration(junior["id"], "2026", "U16", "Complete")


def test_exactly_18_no_guardian_required(make_member, make_registration, exactly_18_dob):
    """A member whose 18th birthday is today does not need a guardian."""
    member = make_member("Turning 18", dob=exactly_18_dob)
    reg = make_registration(member["id"], "2026", "Seniors", "Started")

    updated = services.update_registration(reg["id"], member["id"], "2026", "Seniors", "Complete")
    assert updated["status"] == "Complete"


def test_just_under_18_requires_guardian(make_member, make_registration, just_under_18_dob):
    """A member whose 18th birthday is tomorrow still needs a guardian."""
    member = make_member("Almost 18", dob=just_under_18_dob)
    reg = make_registration(member["id"], "2026", "U18", "Started")

    with pytest.raises(services.ServiceError) as exc_info:
        services.update_registration(reg["id"], member["id"], "2026", "U18", "Complete")

    assert "under 18" in str(exc_info.value)
    assert services.get_registration(reg["id"])["status"] == "Started"


def test_withdrawn_registration_retained_in_history(make_member, make_registration):
    """Withdrawing a registration keeps it visible in the member's history."""
    member = make_member("Withdrawn History")
    reg = make_registration(member["id"], "2026", "U16", "Started")
    services.withdraw_registration(reg["id"])

    history = services.member_registration_history(member["id"])
    assert len(history) == 1
    assert history[0]["season"] == "2026"
    assert history[0]["status"] == "Withdrawn"
