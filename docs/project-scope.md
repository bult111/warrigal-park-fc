# Project Scope

This document records the scope that has actually been implemented in the
Warrigal Park FC Member Registration and Team Roster System.

## In Scope (implemented)

- **Member management** — create, search (including duplicate names), update,
  and set a member Inactive (a soft state change, never a hard delete).
- **Guardian management** — create, search, update, link guardians to members,
  and view a guardian's linked junior members. Guardian contact details live
  only on the guardian record and are shown wherever the guardian is referenced.
  Each guardian records a `date_of_birth` that must verify them as an adult
  (18 or over).
- **Registration management** — create, view, amend and withdraw registrations,
  with registration history retained across seasons.
- **Automatic age groups** — the age group is computed from the member's date of
  birth and the season (`season_age = season_year − birth_year`) against a fixed
  list (`U6`, `U8`, `U10`, `U12`, `U14`, `U16`, `U18`, `Seniors`); the submitted
  age group is ignored. A member below 4 in a season cannot be registered. This
  is the course project's own rule, not an official Football Australia
  regulation.
- **Junior guardian validation** — a member under 18 must have at least one
  linked guardian verified as an adult before a registration can become
  Complete.
- **Team management** — create, list, rename and remove teams. Removing a team
  never deletes members or registrations.
- **Player management** — add a registered player to a team, move a player
  between teams, and remove a player from a team. A player must hold a `Complete`
  registration for the same season as the team and a matching age group, and may
  hold only one team per season.
- **Automatic team assignment** — a `Complete` registration places the eligible
  player onto a matching team automatically, choosing the fewest players and then
  the lowest team id, including when a matching team is created later. An
  existing placement is never silently moved, and withdrawing the last `Complete`
  registration for a season removes that season's assignment.
- **Team roster** — a read-only roster view showing team details and player
  contact information, with a friendly empty state.
- **Registration history** — a member's registrations across seasons.
- **Guardian linked juniors** — a guardian's linked members with contact info.
- **Dashboard** — counts for total members, active members, guardians,
  registrations and teams.
- **Validation and error handling** — user-friendly messages for missing
  fields, invalid dates, invalid references, guardian and eligibility rule
  violations, and duplicate relationships.

## Out of Scope (not implemented)

- Payments, fees, or discounts
- PlayFootball / PlayRegister integration
- Import / export of data
- WWCC / Blue Card management
- Squad-size enforcement
- Official Football Australia age-group regulations (the implemented rule is the
  course project's own, derived from date of birth and season)
- Fixtures, results, or ladders
- Canteen or uniforms management
- SMS or email notification
- Family self-registration
- Public club website
- Complex authentication (login, roles, permissions)

## Future Improvements (not yet implemented)

The following are reasonable next steps but are not part of the current
implementation:

- User authentication and role-based access (for example admin vs. registrar).
- CSV import/export of members, guardians and registrations.
- Automated email notifications for registration confirmations.
- A public-facing club website front-end.
- Squad-size limits when placing players into teams (age-group eligibility is
  already enforced).
