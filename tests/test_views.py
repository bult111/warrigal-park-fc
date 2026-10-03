"""View / page rendering tests using the Flask test client."""

from app import services


def test_dashboard(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Dashboard" in response.data


def test_member_page(client, make_member):
    make_member("Visible Member")
    response = client.get("/members")
    assert response.status_code == 200
    assert b"Visible Member" in response.data


def test_guardian_page(client, make_guardian):
    make_guardian("Visible Guardian")
    response = client.get("/guardians")
    assert response.status_code == 200
    assert b"Visible Guardian" in response.data


def test_registration_page(client, make_member, make_registration):
    member = make_member("Reg Member")
    make_registration(member["id"], "2026", "U16")
    response = client.get("/registrations")
    assert response.status_code == 200
    assert b"Reg Member" in response.data


def test_team_page(client, make_team):
    make_team("2026", "Tigers", "U16")
    response = client.get("/teams")
    assert response.status_code == 200
    assert b"Tigers" in response.data


def test_roster_page(client, make_member, make_registration, make_team):
    member = make_member("Roster Player")
    make_registration(member["id"], "2026", "U16", "Complete")
    team = make_team("2026", "Tigers", "U16")
    services.add_player_to_team(team["id"], member["id"])

    response = client.get(f"/teams/{team['id']}/roster")
    assert response.status_code == 200
    assert b"Tigers" in response.data
    assert b"Roster Player" in response.data


def test_empty_roster(client, make_team):
    team = make_team("2026", "Eagles", "U14")
    response = client.get(f"/teams/{team['id']}/roster")
    assert response.status_code == 200
    assert b"No players are currently registered in this team" in response.data


def test_registration_history_view(client, make_member, make_registration):
    member = make_member("History Player")
    make_registration(member["id"], "2025", "U14", "Complete")
    make_registration(member["id"], "2026", "U16", "Started")

    response = client.get(f"/members/{member['id']}")
    assert response.status_code == 200
    assert b"2025" in response.data
    assert b"2026" in response.data


def test_guardian_linked_juniors_view(
    client, make_member, make_guardian, link_guardian, junior_dob
):
    junior = make_member("Linked Junior", dob=junior_dob)
    guardian = make_guardian("Linked Guardian")
    link_guardian(guardian["id"], junior["id"])

    response = client.get(f"/guardians/{guardian['id']}")
    assert response.status_code == 200
    assert b"Linked Junior" in response.data
