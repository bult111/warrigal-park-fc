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
    team = make_team("2026", "Tigers", "Seniors")
    make_registration(member["id"], "2026", "U16", "Complete")  # auto-assigns

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


# ---------------------------------------------------------------------------
# Sprint 4 — Team and Roster Management route/view tests
# ---------------------------------------------------------------------------


def test_team_create_route_success(client):
    response = client.post(
        "/teams/new",
        data={"season": "2026", "name": "Tigers", "age_group": "U16"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Tigers" in response.data
    assert b"created" in response.data

    teams = services.list_teams()
    assert len(teams) == 1
    assert teams[0]["name"] == "Tigers"


def test_team_create_route_invalid(client):
    response = client.post(
        "/teams/new",
        data={"season": "", "name": "Tigers", "age_group": "U16"},
    )
    assert response.status_code == 400
    assert b"Season is required." in response.data
    assert services.list_teams() == []


def test_team_rename_route(client, make_team):
    team = make_team("2026", "Tigers", "U16")

    response = client.post(
        f"/teams/{team['id']}/edit",
        data={"season": "2026", "name": "Panthers", "age_group": "U16"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Panthers" in response.data
    assert services.get_team(team["id"])["name"] == "Panthers"


def test_team_delete_route(client, make_member, make_registration, make_team):
    member = make_member("Keep Me")
    team = make_team("2026", "Tigers", "Seniors")
    reg = make_registration(member["id"], "2026", "U16", "Complete")  # auto-assigns

    response = client.post(f"/teams/{team['id']}/delete", follow_redirects=True)
    assert response.status_code == 200
    assert b"removed" in response.data

    assert services.get_team(team["id"]) is None
    assert services.get_member(member["id"]) is not None
    assert services.get_registration(reg["id"]) is not None


def test_player_add_route_success(client, make_member, make_registration, make_team):
    member = make_member("Add Me")
    make_registration(member["id"], "2026", "U16", "Complete")
    team = make_team("2026", "Tigers", "Seniors")

    response = client.post(
        f"/teams/{team['id']}/players/add",
        data={"member_id": member["id"]},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"added" in response.data
    assert [p["name"] for p in services.team_players(team["id"])] == ["Add Me"]


def test_player_add_route_invalid(client, make_member, make_registration, make_team):
    member = make_member("Started Only")
    make_registration(member["id"], "2026", "U16", "Started")
    team = make_team("2026", "Tigers", "U16")

    response = client.post(
        f"/teams/{team['id']}/players/add",
        data={"member_id": member["id"]},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"does not have a Complete registration for the team" in response.data
    assert services.team_players(team["id"]) == []


def test_player_remove_route_success(client, make_member, make_registration, make_team):
    member = make_member("Remove Me")
    team = make_team("2026", "Tigers", "Seniors")
    make_registration(member["id"], "2026", "U16", "Complete")  # auto-assigns

    response = client.post(
        f"/teams/{team['id']}/players/{member['id']}/remove",
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"removed" in response.data
    assert services.team_players(team["id"]) == []


def test_player_remove_route_noop(client, make_member, make_registration, make_team):
    member = make_member("Not In Team")
    make_registration(member["id"], "2026", "U16", "Complete")
    team = make_team("2026", "Tigers", "U16")

    response = client.post(
        f"/teams/{team['id']}/players/{member['id']}/remove",
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"not in this team" in response.data
    assert services.team_players(team["id"]) == []


def test_player_move_route_success(client, make_member, make_registration, make_team):
    member = make_member("Mover")
    team_a = make_team("2026", "Tigers", "Seniors")
    team_b = make_team("2026", "Eagles", "Seniors")
    make_registration(member["id"], "2026", "U16", "Complete")  # auto-assigns to team A

    response = client.post(
        f"/teams/{team_a['id']}/players/{member['id']}/move",
        data={"to_team_id": team_b["id"]},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"moved" in response.data
    assert services.team_players(team_a["id"]) == []
    assert [p["name"] for p in services.team_players(team_b["id"])] == ["Mover"]


def test_roster_shows_contact_details(client, make_member, make_registration, make_team):
    member = make_member(
        "Roster Contact", email="player@example.com", phone="0400 000 000"
    )
    team = make_team("2026", "Tigers", "Seniors")
    make_registration(member["id"], "2026", "U16", "Complete")  # auto-assigns

    response = client.get(f"/teams/{team['id']}/roster")
    assert response.status_code == 200
    assert b"Roster Contact" in response.data
    assert b"player@example.com" in response.data
    assert b"0400 000 000" in response.data


def test_roster_nonexistent_team(client):
    response = client.get("/teams/99999/roster", follow_redirects=True)
    assert response.status_code == 200
    assert b"Team not found." in response.data
