# Sprint 4 Browser Acceptance Results

Pass: 21, Fail: 0, Total: 21

| Story | Step | Expected | Status | Actual |
|---|---|---|---|---|
| Story16 | teams list shows seeded teams | Eagles + Falcons | PASS | ⚽ Warrigal Park FC
Dashboard
Members
Guardians
Registrations
Teams
Teams
+ New Team
Season	Name	Age Group
2026	Eagles	U |
| Story16 | create team via form | flash 'created' + Tigers | PASS | ⚽ Warrigal Park FC
Dashboard
Members
Guardians
Registrations
Teams
Team 'Tigers' created.
Tigers
View Roster Rename Back |
| Story16 | new team appears in list | Tigers | PASS | ⚽ Warrigal Park FC
Dashboard
Members
Guardians
Registrations
Teams
Teams
+ New Team
Season	Name	Age Group
2026	Eagles	U |
| Story16 | invalid create rejected | Season is required. | PASS | ⚽ Warrigal Park FC
Dashboard
Members
Guardians
Registrations
Teams
Season is required.
New Team
Back to teams
Season *
T |
| Story17 | rename team | Panthers | PASS | ⚽ Warrigal Park FC
Dashboard
Members
Guardians
Registrations
Teams
Team renamed to 'Panthers'.
Panthers
View Roster Rena |
| Story17 | deleted team gone from list | Disposable absent | PASS | ⚽ Warrigal Park FC
Dashboard
Members
Guardians
Registrations
Teams
Teams
+ New Team
Season	Name	Age Group
2026	Eagles	U |
| Story17 | member kept after team removal | Alice Complete | PASS | ⚽ Warrigal Park FC
Dashboard
Members
Guardians
Registrations
Teams
Members
+ New Member
Search
Name	Date of Birth	Email	 |
| Story17 | registration kept after team removal | Alice Complete | PASS | ⚽ Warrigal Park FC
Dashboard
Members
Guardians
Registrations
Teams
Registrations
+ New Registration
Member	Season	Age Gr |
| Story18 | Complete player added | flash added + Alice | PASS | players=["Alice Complete"] |
| Story18 | Started player rejected | error, Bob not in players | PASS | players=["Alice Complete"] |
| Story18 | Withdrawn player rejected | error, Carol not in players | PASS | players=["Alice Complete"] |
| Story18 | wrong-season player rejected | error, Dave not in players | PASS | players=["Alice Complete"] |
| Story18 | duplicate add rejected | already in that team | PASS | ⚽ Warrigal Park FC
Dashboard
Members
Guardians
Registrations
Teams
This player is already in that team.
Panthers
View Ro |
| Story19 | move player same-season | Panthers empty, Eagles has Alice | PASS | Panthers=[] Eagles=["Alice Complete"] |
| Story19 | cross-season move rejected | Alice stays in Eagles | PASS | Eagles=["Alice Complete"] |
| Story19 | remove player success | Alice absent from Eagles | PASS | Eagles=[] |
| Story19 | remove non-member gives error | not in this team | PASS | ⚽ Warrigal Park FC
Dashboard
Members
Guardians
Registrations
Teams
That player is not in this team.
Eagles
View Roster R |
| Story19 | guardian link preserved after remove | Junior Kid linked | PASS | ⚽ Warrigal Park FC
Dashboard
Members
Guardians
Registrations
Teams
Guardian G
Edit Back to guardians
Name	Guardian G
Ema |
| Story20 | roster shows name/email/phone | Alice + email + phone | PASS | ⚽ Warrigal Park FC
Dashboard
Members
Guardians
Registrations
Teams
Eagles
Manage Team Back to teams

Season: 2026  ·  Age Group: U16

Player	Email	Pho |
| Story20 | empty roster | empty state | PASS | ⚽ Warrigal Park FC
Dashboard
Members
Guardians
Registrations
Teams
Falcons
Manage Team Back to teams

Season: 2025  ·  A |
| Story20 | nonexistent team roster | Team not found. | PASS | ⚽ Warrigal Park FC
Dashboard
Members
Guardians
Registrations
Teams
Team not found.
Teams
+ New Team
Season	Name	Age Grou |
