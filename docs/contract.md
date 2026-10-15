# Supported contract, version 1

SeedStartGate compiles fixed elapsed-calendar-day protocols into allowed and excluded start dates. It does not solve schedules, choose duration ranges, allocate resources, or record physical completion. A `day: 30` event occurs on `start + timedelta(days=30)`; day zero is the start itself. Weekends remain elapsed days. Every event requires attendance on its named calendar.

## Input

One UTF-8 JSON object, <=2 MiB, no duplicate keys, NaN, unknown fields or inferred values:

- `schema_version`: integer 1 (booleans are rejected).
- `name`: nonblank text <=200 characters.
- `calendars`: object with 1..32 ID keys. Each value has `coverage_start`, `coverage_end` (inclusive ISO YYYY-MM-DD), `weekdays` (unique mon/tue/wed/thu/fri/sat/sun strings), `closures` (list of `{start,end,label}` inclusive date ranges), and `extra_open` (unique dates, explicit staffed-day exceptions). Closures override extra-open dates. Closures and extra-open dates must be inside coverage. Coverage means the operator has checked the calendar, including missing holidays/vacations; the application does not fetch them.
- `protocols`: object with 1..100 ID keys. Each value has `label`, `source` (nonblank user-supplied authority/reference), `events`: 1..128 objects `{id,day,action,calendar}`. Event IDs must be unique within a protocol, day is an integer 0..3660, and at least one event must be day zero. Calendar references must exist. Multiple events on one day are supported; none is skipped.

IDs: ASCII letter then up to 63 ASCII letters, digits, underscore, dot or hyphen. Labels/actions/source are nonblank, single-line text <=500 characters; controls, leading formula characters (=,+,-,@), and leading/trailing whitespace are rejected so CSVs can be opened as text in spreadsheets. Names use the same character safety. All input dates: 1900-01-01..2199-12-31, strict ten-character ISO form. Dates outside calendar coverage are unknown, never allowed. A computed event date beyond year 2199 is unknown. No species treatment database, climate rules, legal/quality certification or biological recommendations are included.

## Commands

- `seedstartgate init DIRECTORY`: create a new directory with constructed `plan.json`, an explanatory README and no real species advice.
- `seedstartgate validate PLAN`: validate schema; does not assert any proposed start is permitted.
- `seedstartgate screen PLAN --from YYYY-MM-DD --through YYYY-MM-DD --out DIRECTORY [--protocol ID ...] [--ics]`: enumerate every date (inclusive) for each selected protocol. Default: all protocols sorted by ID. <=3660 dates per protocol, <=50,000 candidate rows, <=250,000 candidate/event evaluations, <=50,000 conflict reasons and <=2,000,000 total reason-detail characters. Bounds apply before publishing any report; split requests that exceed them. The reason bounds also apply to a single check. Output directory must not exist; publish a complete directory atomically, never overwrite.
- `seedstartgate check PLAN PROTOCOL START --out DIRECTORY [--ics] [--expect-sha256 HASH]`: independently re-evaluate all events. Optional expected canonical config fingerprint detects stale decisions. On allowed status, emit complete actions CSV/text/JSON and optional all-day ICS. Blocked or unknown status emits diagnosis only, with no executable action worklist/ICS.

Screen status per candidate: `unknown` if any event is outside coverage; otherwise `blocked` if any event is closed/unstaffed; otherwise `allowed`. Preserve all event reasons, including known closures on an otherwise unknown candidate. For one event a closure reports every overlapping closure label; otherwise weekly closure reports unstaffed weekday; extra-open overrides weekly closure only. Do not silently move actions.

## Output and exit codes

JSON/CSV/text reports are UTF-8, deterministic, include product/schema versions and canonical configuration SHA-256, and contain no absolute input paths or wall-clock generation date. ICS creation timestamps vary between exports. `screen` produces `report.json`, `candidates.csv`, `conflicts.csv`, `summary.txt`, optionally `excluded-starts.ics`. ICS contains only known blocked candidates; unknown candidates appear in the report but never masquerade as known exclusions. Candidate CSV columns: `protocol,start,status,config_sha256`. Conflicts CSV columns: `protocol,start,event,event_date,calendar,kind,detail`. JSON retains all reasons. `check` always writes `report.json` and `summary.txt`; allowed only: `actions.csv`, `actions.txt`, optional `actions.ics`. Action CSV columns: `date,protocol,event,action,calendar,config_sha256`. ICS is an optional offline view with an actual UTC export DTSTAMP, all-day events, CRLF, UTF-8 octet line folding, stable content-derived UIDs, no alarms, no calendar service writes. Imports are snapshots: replace/delete the prior import after input changes; importers may duplicate events.

Exit 0: valid input / complete screen with at least one allowed date per selected protocol and no unknown date / allowed check. Exit 2: invalid input, command, stale fingerprint, resource bound or filesystem failure (no output directory published). Exit 3: screen contains unknown dates or a selected protocol has no allowed start; or check is blocked/unknown (diagnostic directory published). A successfully written CSV is not a statement that all dates are safe. Existing outputs and inputs are never edited. No network, external commands, plugins, execution of input text, or runtime third-party dependencies.

Compatibility: Python 3.10 through 3.14 on Linux, macOS and Windows. No multi-user locks, cloud sync, capacity guarantees, monitoring reminders, hour/minute precision or automatic holiday inference. Run on a local filesystem. Atomic directory publication protects against partial normal failures; concurrent writers to the same destination are unsupported. Keep exported files private if protocol or lot names are sensitive.
