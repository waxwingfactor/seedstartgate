# SeedStartGate

**Check every future handling date before starting a seed protocol.** SeedStartGate is an offline compiler for seed-treatment do-not-start calendars. It screens fixed day offsets against your checked staffing calendars, explains every excluded start, and marks missing coverage as unknown.

For small native-seed preparation teams with approved protocols. Inspired by the [BC Tree Seed Centre's documented Excel workflow](https://www2.gov.bc.ca/assets/gov/farming-natural-resources-and-industry/forestry/tree-seed/tree-seed-centre/tswgnewsbulletin50.pdf), which already solved this calculation locally. A maintained spreadsheet remains a good alternative. See [dated research and positioning](docs/research.md) for the evidence and its limits.

## Install

Python **3.10–3.14**, on Linux, macOS or Windows. No third-party runtime dependencies or network use.

Download the wheel from [Releases](https://github.com/waxwingfactor/seedstartgate/releases), then:

```console
python -m pip install seedstartgate-1.0.0-py3-none-any.whl
seedstartgate --version
```

Or download `seedstartgate.pyz` from the same release and run `python seedstartgate.pyz` in place of `seedstartgate`. The zipapp requires supported Python but no installation or pip packages. A source distribution is also supplied; building it requires setuptools >=77 and wheel, which pip normally fetches automatically. [Release verification](docs/verification.md) records the actual published-artifact checks; release assets include SHA-256 sums.

## Try the complete workflow

Create the included **constructed arithmetic example**:

```console
seedstartgate init my-calendar
seedstartgate validate my-calendar/plan.json
seedstartgate screen my-calendar/plan.json --from 2027-02-01 --through 2027-02-14 --out screened --ics
seedstartgate check my-calendar/plan.json demo 2027-02-01 --out approved --ics
seedstartgate check my-calendar/plan.json demo 2027-02-08 --out rejected --ics
```

The February 1 start passes. The February 8 start returns **exit 3** because its day-seven transfer falls on the explicit February 15 closure. `rejected` contains diagnosis only; it has no action worklist or calendar. Example offsets are not species treatment instructions.

`screened/candidates.csv` lists every start with `allowed`, `blocked` or `unknown`. `conflicts.csv` preserves every affected event and reason. The summary gives counts per protocol. Optional `excluded-starts.ics` contains known blocked starts only, with no alarms; unknown starts remain visibly unresolved in CSV/JSON.

After reviewing candidates, `check` independently evaluates the chosen start. A passing check produces `actions.csv`, a printable `actions.txt`, JSON and optional all-day action ICS. To detect a changed protocol or calendar, pass the prior report's configuration fingerprint using `--expect-sha256 HASH`. There is no automatic execution or completion record.

## Author your plan

The example is a complete editable input. Replace its protocols with your approved action offsets and source reference. Include **every** attendance action, including day zero and later counts or inspections. `day: 30` means exactly start +30 elapsed calendar days; weekends do not pause a treatment. Same-day events have no implied time order.

Each named calendar declares an inclusive checked coverage range, staffed weekdays, dated closure ranges and optional extra-open dates. Closures override extra-open exceptions. The tool does not fetch holidays or infer staff leave. An event outside checked coverage is **unknown**, even if its weekday normally has staff.

Use repeated `--protocol ID` options to screen a subset. Invalid fields, missing references, unsupported dates and resource-bound violations fail clearly. Inputs and existing outputs are never overwritten. See the [exact input/output contract](docs/contract.md) and [operating guide](docs/operations.md).

| Exit | Meaning |
| --- | --- |
| `0` | Valid schema; or fully known screen with an allowed start for every selected protocol; or allowed chosen-start check. |
| `2` | Invalid/unsupported input, stale fingerprint or filesystem failure; no output directory is published. |
| `3` | Diagnostic report published: unknown screening dates, a protocol with no allowed start, or a blocked/unknown chosen start. |

## Scope and limits

This checks **declared calendar availability**. It does not select treatments, interpret seed-testing rules, predict germination, guarantee sufficient labor or storage, optimize schedules, or validate biological suitability. Omitted events and inaccurate staffing inputs cannot be detected. Recheck after any change.

Protocols use fixed integer day offsets, not hours, variable duration windows or conditional steps. ICS files are optional snapshots; replace/delete the previous import after changes because calendar apps may duplicate imports. JSON/CSV/text are deterministic; ICS has an actual UTC export timestamp. Use a local filesystem and one writer per output path. [Full boundaries](docs/contract.md).

## Development and review

```console
python -m pip install -e .
python -m unittest discover -s tests -v
python -m pip install build==1.3.0 setuptools==80.9.0 wheel==0.45.1
python -m build --no-isolation
python scripts/build_zipapp.py
```

CI builds and installs both wheel and sdist, runs the independent CLI acceptance suite, checks the installed workflow and exercises the standalone zipapp on Linux/macOS/Windows with Python 3.10 and 3.14. Local verification also uses Python 3.12. See [review records](docs/reviews.md), [verification](docs/verification.md), and the [MIT license](LICENSE). Separate AI agents wrote acceptance tests and reviewed implementation; these are not human customer reviews or independent GitHub account approvals.
