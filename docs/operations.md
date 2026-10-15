# Operating guide

## Prepare an accurate calendar

Use your approved protocol record as the source. Each event is a required attendance action at an exact elapsed-day offset. Include day zero, all intermediate actions and the last action. Repeating inspections must be represented as separate explicit events. SeedStartGate cannot detect something you omitted and does not know whether your protocol is biologically appropriate.

Name separate calendars where different activities have different staffing: for example, preparation staff Monday–Friday and a monitoring team available seven days. Each event references one calendar. The application does not infer staff skills, holidays, jurisdiction, capacity or specific operators.

Set coverage only through dates you have checked for holidays and leave. The range must cover every resulting action you want to permit. If you screen December start dates for a 90-day protocol, verify the required next-year calendars too. Missing coverage produces `unknown` and exit 3, with no action worklist from a chosen-start check.

`closures` are inclusive date ranges. Overlapping closures are supported and preserve each distinct label. An `extra_open` date can make a normally unstaffed weekday available, but a dated closure still wins. Dates outside coverage are never made available by weekday rules.

Protocol `source` is an operator reference (for example an internal revision ID), not something the tool interprets. Single-line printable strings are required. Leading/trailing whitespace, controls and leading spreadsheet formula characters are rejected, not silently changed. IDs are deliberately restricted to simple ASCII identifiers. Use text labels for longer human-readable names.

## Screen, inspect and check

1. Validate the plan to catch field names, duplicate JSON keys, missing calendars and incorrect date syntax.
2. Screen a range of candidate starts. Both endpoints are included. Review the exit status and `summary.txt`, then examine `candidates.csv` and `conflicts.csv`.
3. Unknown means the calendar record is incomplete for at least one action. Supply verified coverage and rerun. A blocked date has known closure/weekday reasons; do not silently move a future action.
4. Choose an allowed start and run `check` against the same plan. Pass `--expect-sha256` from the screening report to reject changes since that assessment. Harmless JSON whitespace and object key order do not change the canonical fingerprint; input values and array order do.
5. Only a passing check produces a full dated worklist. Review the source protocol and current staffing before starting. The exported checkboxes are a paper convenience, not an application completion ledger.

All reasons remain in JSON/CSV, including known blocked events on a candidate whose other event has unknown coverage. The summary counts such a candidate as unknown. No output truncation converts an incomplete report into success: requests above the documented bounds fail with exit 2 before publication. Split a large range or select fewer protocols, and keep all output directories to preserve the complete assessment.

## Calendar export

`--ics` is optional. A screen's ICS contains all-day `DO NOT START` entries for **known blocked starts**, not action dates. Unknown candidates are excluded from that calendar because their status is unresolved; always read the accompanying report. An allowed check's ICS contains dated planned actions. Blocked/unknown checks never export action ICS.

No alarms, reminders, subscriptions or external calendar writes occur. A calendar application can be used to view/import the file, but it may handle repeated imports differently. Replace the old snapshot after changing inputs. Content-derived UIDs and UTC export stamps are included; no cross-application update/delete guarantee is made. Reports have no local input paths.

## Installation and offline use

The wheel and zipapp have no third-party runtime dependencies. Transfer the downloaded wheel to an offline machine and install with `python -m pip install --no-index --no-deps WHEEL_PATH`; or run `python seedstartgate.pyz` directly. The interpreter must be Python 3.10–3.14. The source archive includes examples, tests and documentation. Building an sdist offline additionally needs setuptools >=77 and wheel already available.

The plan and output can be moved together to another directory. No database, machine-bound paths or service credentials are needed. Do not edit output reports to change a decision; update the plan and generate a new report. The output location must be new and its parent must already exist. Existing paths, including symlinks, are refused. Output publication uses a staging directory on the same filesystem; simultaneous writers and network-filesystem atomicity are outside the supported scope.

For bug reports, include a minimized synthetic plan, exact command, exit code and version. Do not post private seed locations, customer data or internal protocols. Report issues at the [project issue tracker](https://github.com/waxwingfactor/seedstartgate/issues).
