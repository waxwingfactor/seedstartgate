SeedStartGate constructed example

These offsets are arithmetic fixtures, not seed-treatment instructions.
Replace them with your approved protocol and every staff-required action,
including day zero, interim counts/checks and final handling. Fill calendar
coverage only for dates whose weekdays, holidays and leave you have checked.
All offsets are elapsed calendar days; day zero is the selected start date.

From this directory:
  seedstartgate validate plan.json
  seedstartgate screen plan.json --from 2027-02-01 --through 2027-02-14 --out screened --ics
  seedstartgate check plan.json demo 2027-02-01 --out allowed --ics
  seedstartgate check plan.json demo 2027-02-08 --out blocked --ics

The first check is allowed. The second returns exit 3 because its day-seven
transfer falls on the explicit February 15 closure; no action worklist or ICS
is published for that start. Inspect screened/conflicts.csv for all reasons.
Never treat an unknown date as permitted. Re-screen after staffing/protocol
changes and use --expect-sha256 from a prior report to detect stale decisions.
ICS files are optional snapshots with no alarms. Replace the old imported
snapshot when re-exporting; importing repeatedly may create duplicates.
