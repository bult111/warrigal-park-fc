"""HTTP routes for the Warrigal Park FC application.

This layer is responsible only for translating HTTP requests into service
calls and choosing which template to render. All business rules live in
``services.py``.
"""

from flask import Blueprint, flash, redirect, render_template, request, url_for

from . import models, services

bp = Blueprint("main", __name__)


def _flash_error(error):
    """Flash a user-friendly message for a business-rule violation."""
    flash(str(error), "error")


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

@bp.route("/")
def index():
    return render_template("index.html", stats=services.dashboard_stats())


# ---------------------------------------------------------------------------
# Members
# ---------------------------------------------------------------------------

@bp.route("/members")
def members():
    search = request.args.get("q", "")
    return render_template(
        "members.html", members=services.list_members(search), search=search
    )


@bp.route("/members/new", methods=("GET", "POST"))
def member_new():
    if request.method == "POST":
        form = request.form
        try:
            member = services.create_member(
                form.get("name"),
                form.get("date_of_birth"),
                form.get("email"),
                form.get("phone"),
                form.get("address"),
            )
            flash(f"Member '{member['name']}' created.", "success")
            return redirect(url_for("main.member_detail", member_id=member["id"]))
        except (ValueError, services.ServiceError) as error:
            _flash_error(error)
            return render_template(
                "member_form.html", member=None, form=form, errors=[str(error)]
            ), 400
    return render_template("member_form.html", member=None, form={}, errors=[])


@bp.route("/members/<int:member_id>")
def member_detail(member_id):
    member = services.get_member(member_id)
    if member is None:
        flash("Member not found.", "error")
        return redirect(url_for("main.members"))
    history = services.member_registration_history(member_id)
    guardians = services.member_guardians(member_id)
    from datetime import date

    member["age"] = models.calculate_age(date.fromisoformat(member["date_of_birth"]))
    return render_template(
        "member_detail.html", member=member, history=history, guardians=guardians
    )


@bp.route("/members/<int:member_id>/edit", methods=("GET", "POST"))
def member_edit(member_id):
    member = services.get_member(member_id)
    if member is None:
        flash("Member not found.", "error")
        return redirect(url_for("main.members"))
    if request.method == "POST":
        form = request.form
        try:
            member = services.update_member(
                member_id,
                form.get("name"),
                form.get("date_of_birth"),
                form.get("email"),
                form.get("phone"),
                form.get("address"),
            )
            flash(f"Member '{member['name']}' updated.", "success")
            return redirect(url_for("main.member_detail", member_id=member_id))
        except (ValueError, services.ServiceError) as error:
            _flash_error(error)
            return render_template(
                "member_form.html", member=member, form=form, errors=[str(error)]
            ), 400
    return render_template("member_form.html", member=member, form=member, errors=[])


@bp.route("/members/<int:member_id>/deactivate", methods=("POST",))
def member_deactivate(member_id):
    try:
        member = services.set_member_inactive(member_id)
        flash(f"Member '{member['name']}' is now inactive.", "success")
    except (ValueError, services.ServiceError) as error:
        _flash_error(error)
    return redirect(url_for("main.member_detail", member_id=member_id))


@bp.route("/members/<int:member_id>/activate", methods=("POST",))
def member_activate(member_id):
    try:
        member = services.set_member_status(member_id, models.MEMBER_STATUS_ACTIVE)
        flash(f"Member '{member['name']}' is now active.", "success")
    except (ValueError, services.ServiceError) as error:
        _flash_error(error)
    return redirect(url_for("main.member_detail", member_id=member_id))


# ---------------------------------------------------------------------------
# Guardians
# ---------------------------------------------------------------------------

@bp.route("/guardians")
def guardians():
    search = request.args.get("q", "")
    return render_template(
        "guardians.html", guardians=services.list_guardians(search), search=search
    )


@bp.route("/guardians/new", methods=("GET", "POST"))
def guardian_new():
    if request.method == "POST":
        form = request.form
        try:
            guardian = services.create_guardian(
                form.get("name"),
                form.get("email"),
                form.get("phone"),
                form.get("address"),
            )
            flash(f"Guardian '{guardian['name']}' created.", "success")
            return redirect(url_for("main.guardian_detail", guardian_id=guardian["id"]))
        except (ValueError, services.ServiceError) as error:
            _flash_error(error)
            return render_template(
                "guardian_form.html", guardian=None, form=form, errors=[str(error)]
            ), 400
    return render_template("guardian_form.html", guardian=None, form={}, errors=[])


@bp.route("/guardians/<int:guardian_id>")
def guardian_detail(guardian_id):
    guardian = services.get_guardian(guardian_id)
    if guardian is None:
        flash("Guardian not found.", "error")
        return redirect(url_for("main.guardians"))
    linked = services.guardian_linked_members(guardian_id)
    members = services.list_members()
    return render_template(
        "guardian_detail.html", guardian=guardian, linked=linked, members=members
    )


@bp.route("/guardians/<int:guardian_id>/edit", methods=("GET", "POST"))
def guardian_edit(guardian_id):
    guardian = services.get_guardian(guardian_id)
    if guardian is None:
        flash("Guardian not found.", "error")
        return redirect(url_for("main.guardians"))
    if request.method == "POST":
        form = request.form
        try:
            guardian = services.update_guardian(
                guardian_id,
                form.get("name"),
                form.get("email"),
                form.get("phone"),
                form.get("address"),
            )
            flash(f"Guardian '{guardian['name']}' updated.", "success")
            return redirect(url_for("main.guardian_detail", guardian_id=guardian_id))
        except (ValueError, services.ServiceError) as error:
            _flash_error(error)
            return render_template(
                "guardian_form.html", guardian=guardian, form=form, errors=[str(error)]
            ), 400
    return render_template("guardian_form.html", guardian=guardian, form=guardian, errors=[])


@bp.route("/guardians/<int:guardian_id>/link", methods=("POST",))
def guardian_link(guardian_id):
    member_id = request.form.get("member_id", type=int)
    try:
        if member_id is None:
            raise services.ServiceError("Please choose a member to link.")
        services.link_guardian_member(guardian_id, member_id)
        flash("Member linked to guardian.", "success")
    except (ValueError, services.ServiceError) as error:
        _flash_error(error)
    return redirect(url_for("main.guardian_detail", guardian_id=guardian_id))


@bp.route("/guardians/<int:guardian_id>/unlink/<int:member_id>", methods=("POST",))
def guardian_unlink(guardian_id, member_id):
    try:
        services.unlink_guardian_member(guardian_id, member_id)
        flash("Member unlinked from guardian.", "success")
    except (ValueError, services.ServiceError) as error:
        _flash_error(error)
    return redirect(url_for("main.guardian_detail", guardian_id=guardian_id))


# ---------------------------------------------------------------------------
# Registrations
# ---------------------------------------------------------------------------

@bp.route("/registrations")
def registrations():
    return render_template("registrations.html", registrations=services.list_registrations())


@bp.route("/registrations/new", methods=("GET", "POST"))
def registration_new():
    members = services.list_members()
    if request.method == "POST":
        form = request.form
        try:
            registration = services.create_registration(
                request.form.get("member_id", type=int),
                form.get("season"),
                form.get("age_group"),
                form.get("status") or models.REGISTRATION_STATUS_STARTED,
            )
            flash("Registration created.", "success")
            return redirect(url_for("main.registration_detail", registration_id=registration["id"]))
        except (ValueError, services.ServiceError) as error:
            _flash_error(error)
            return render_template(
                "registration_form.html",
                registration=None,
                members=members,
                form=form,
                errors=[str(error)],
            ), 400
    return render_template(
        "registration_form.html", registration=None, members=members, form={}, errors=[]
    )


@bp.route("/registrations/<int:registration_id>")
def registration_detail(registration_id):
    registration = services.get_registration(registration_id)
    if registration is None:
        flash("Registration not found.", "error")
        return redirect(url_for("main.registrations"))
    return render_template("registration_detail.html", registration=registration)


@bp.route("/registrations/<int:registration_id>/edit", methods=("GET", "POST"))
def registration_edit(registration_id):
    registration = services.get_registration(registration_id)
    if registration is None:
        flash("Registration not found.", "error")
        return redirect(url_for("main.registrations"))
    members = services.list_members()
    if request.method == "POST":
        form = request.form
        try:
            registration = services.update_registration(
                registration_id,
                request.form.get("member_id", type=int),
                form.get("season"),
                form.get("age_group"),
                form.get("status"),
            )
            flash("Registration updated.", "success")
            return redirect(url_for("main.registration_detail", registration_id=registration_id))
        except (ValueError, services.ServiceError) as error:
            _flash_error(error)
            return render_template(
                "registration_form.html",
                registration=registration,
                members=members,
                form=form,
                errors=[str(error)],
            ), 400
    return render_template(
        "registration_form.html",
        registration=registration,
        members=members,
        form=registration,
        errors=[],
    )


@bp.route("/registrations/<int:registration_id>/withdraw", methods=("POST",))
def registration_withdraw(registration_id):
    try:
        services.withdraw_registration(registration_id)
        flash("Registration withdrawn.", "success")
    except (ValueError, services.ServiceError) as error:
        _flash_error(error)
    return redirect(url_for("main.registration_detail", registration_id=registration_id))


# ---------------------------------------------------------------------------
# Teams
# ---------------------------------------------------------------------------

@bp.route("/teams")
def teams():
    return render_template("teams.html", teams=services.list_teams())


@bp.route("/teams/new", methods=("GET", "POST"))
def team_new():
    if request.method == "POST":
        form = request.form
        try:
            team = services.create_team(
                form.get("season"), form.get("name"), form.get("age_group")
            )
            flash(f"Team '{team['name']}' created.", "success")
            return redirect(url_for("main.team_detail", team_id=team["id"]))
        except (ValueError, services.ServiceError) as error:
            _flash_error(error)
            return render_template(
                "team_form.html", team=None, form=form, errors=[str(error)]
            ), 400
    return render_template("team_form.html", team=None, form={}, errors=[])


@bp.route("/teams/<int:team_id>")
def team_detail(team_id):
    team = services.get_team(team_id)
    if team is None:
        flash("Team not found.", "error")
        return redirect(url_for("main.teams"))
    players = services.team_players(team_id)
    members = services.list_members()
    all_teams = services.list_teams()
    return render_template(
        "team_detail.html",
        team=team,
        players=players,
        members=members,
        all_teams=all_teams,
    )


@bp.route("/teams/<int:team_id>/edit", methods=("GET", "POST"))
def team_edit(team_id):
    team = services.get_team(team_id)
    if team is None:
        flash("Team not found.", "error")
        return redirect(url_for("main.teams"))
    if request.method == "POST":
        form = request.form
        try:
            team = services.rename_team(
                team_id, form.get("season"), form.get("name"), form.get("age_group")
            )
            flash(f"Team renamed to '{team['name']}'.", "success")
            return redirect(url_for("main.team_detail", team_id=team_id))
        except (ValueError, services.ServiceError) as error:
            _flash_error(error)
            return render_template(
                "team_form.html", team=team, form=form, errors=[str(error)]
            ), 400
    return render_template("team_form.html", team=team, form=team, errors=[])


@bp.route("/teams/<int:team_id>/delete", methods=("POST",))
def team_delete(team_id):
    try:
        team = services.get_team(team_id)
        services.delete_team(team_id)
        name = team["name"] if team else "Team"
        flash(f"Team '{name}' removed. Members and registrations were kept.", "success")
    except (ValueError, services.ServiceError) as error:
        _flash_error(error)
    return redirect(url_for("main.teams"))


@bp.route("/teams/<int:team_id>/roster")
def team_roster(team_id):
    team = services.get_team(team_id)
    if team is None:
        flash("Team not found.", "error")
        return redirect(url_for("main.teams"))
    players = services.team_players(team_id)
    return render_template("roster.html", team=team, players=players)


# ---------------------------------------------------------------------------
# Players
# ---------------------------------------------------------------------------

@bp.route("/teams/<int:team_id>/players/add", methods=("POST",))
def player_add(team_id):
    member_id = request.form.get("member_id", type=int)
    try:
        if member_id is None:
            raise services.ServiceError("Please choose a player to add.")
        services.add_player_to_team(team_id, member_id)
        flash("Player added to team.", "success")
    except (ValueError, services.ServiceError) as error:
        _flash_error(error)
    return redirect(url_for("main.team_detail", team_id=team_id))


@bp.route(
    "/teams/<int:team_id>/players/<int:member_id>/move", methods=("POST",)
)
def player_move(team_id, member_id):
    to_team_id = request.form.get("to_team_id", type=int)
    try:
        if to_team_id is None:
            raise services.ServiceError("Please choose a destination team.")
        services.move_player(member_id, team_id, to_team_id)
        flash("Player moved. Registration was kept.", "success")
    except (ValueError, services.ServiceError) as error:
        _flash_error(error)
    return redirect(url_for("main.team_detail", team_id=team_id))


@bp.route(
    "/teams/<int:team_id>/players/<int:member_id>/remove", methods=("POST",)
)
def player_remove(team_id, member_id):
    try:
        services.remove_player_from_team(team_id, member_id)
        flash("Player removed from team. Registration was kept.", "success")
    except (ValueError, services.ServiceError) as error:
        _flash_error(error)
    return redirect(url_for("main.team_detail", team_id=team_id))
