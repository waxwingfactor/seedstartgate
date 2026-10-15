"""Independent contract acceptance tests, exercised through the public CLI.

Use ``SEEDSTARTGATE_TEST_INSTALLED=1`` to test the package installed in the
current interpreter without adding the development source to PYTHONPATH.
"""

from __future__ import annotations

import copy
import csv
import io
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
WEEK = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]


def fixture():
    return {
        "schema_version": 1,
        "name": "Constructed acceptance plan",
        "calendars": {
            "crew": {
                "coverage_start": "2009-01-01",
                "coverage_end": "2011-12-31",
                "weekdays": WEEK.copy(),
                "closures": [],
                "extra_open": [],
            }
        },
        "protocols": {
            "example": {
                "label": "Constructed sequence",
                "source": "Operator-authored test fixture; no species advice",
                "events": [
                    {"id": "begin", "day": 0, "action": "Begin prepared protocol", "calendar": "crew"},
                    {"id": "transfer", "day": 30, "action": "Perform recorded transfer", "calendar": "crew"},
                ],
            }
        },
    }


class CLIContractAcceptance(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="seedstartgate-acceptance-")
        self.addCleanup(self.temporary.cleanup)
        self.work = Path(self.temporary.name)
        self.sequence = 0

    def path(self, name="out"):
        self.sequence += 1
        return self.work / f"{name}-{self.sequence}"

    def plan(self, data=None, raw=None):
        path = self.path("plan").with_suffix(".json")
        path.write_text(raw if raw is not None else json.dumps(fixture() if data is None else data), encoding="utf-8")
        return path

    def cli(self, *arguments, expected=0):
        environment = os.environ.copy()
        environment.pop("PYTHONPATH", None)
        environment["PYTHONNOUSERSITE"] = "1"
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        if environment.get("SEEDSTARTGATE_TEST_INSTALLED") != "1":
            environment["PYTHONPATH"] = str(ROOT / "src")
        result = subprocess.run(
            [sys.executable, "-m", "seedstartgate", *map(str, arguments)],
            cwd=self.work,
            env=environment,
            text=True,
            encoding="utf-8",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=30,
            check=False,
        )
        self.assertEqual(
            result.returncode,
            expected,
            f"CLI arguments: {arguments!r}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}",
        )
        self.assertNotIn("Traceback (most recent call last)", result.stderr)
        return result

    def rows(self, directory, filename):
        return list(csv.DictReader(io.StringIO((directory / filename).read_text(encoding="utf-8"))))

    def screen(self, data, start, end, expected=0, *extra):
        plan = self.plan(data)
        out = self.path()
        self.cli("screen", plan, "--from", start, "--through", end, "--out", out, *extra, expected=expected)
        return out

    def check(self, data, start, expected=0, *extra):
        plan = self.plan(data)
        out = self.path()
        self.cli("check", plan, "example", start, "--out", out, *extra, expected=expected)
        return out

    def assert_diagnostic_only(self, directory):
        self.assertTrue((directory / "report.json").is_file())
        self.assertTrue((directory / "summary.txt").is_file())
        for name in ("actions.csv", "actions.txt", "actions.ics"):
            self.assertFalse((directory / name).exists(), name)

    def test_historical_december_second_plus_thirty_is_new_years_day(self):
        data = fixture()
        data["calendars"]["crew"]["closures"] = [
            {"start": "2010-01-01", "end": "2010-01-01", "label": "New Years day 2010"}
        ]
        out = self.screen(data, "2009-12-01", "2009-12-03", 0, "--ics")
        candidates = self.rows(out, "candidates.csv")
        self.assertEqual(
            [(row["start"], row["status"]) for row in candidates],
            [("2009-12-01", "allowed"), ("2009-12-02", "blocked"), ("2009-12-03", "allowed")],
        )
        reasons = self.rows(out, "conflicts.csv")
        self.assertTrue(any(row["start"] == "2009-12-02" and row["event"] == "transfer"
                            and row["event_date"] == "2010-01-01"
                            and "New Years day 2010" in row["detail"] for row in reasons))
        blocked = self.check(data, "2009-12-02", 3, "--ics")
        self.assert_diagnostic_only(blocked)

    def test_elapsed_days_cross_leap_day(self):
        data = fixture()
        data["calendars"]["crew"]["coverage_end"] = "2012-12-31"
        data["protocols"]["example"]["events"][1]["day"] = 2
        out = self.check(data, "2012-02-28", 0, "--ics")
        actions = self.rows(out, "actions.csv")
        self.assertEqual([(row["event"], row["date"]) for row in actions],
                         [("begin", "2012-02-28"), ("transfer", "2012-03-01")])
        data["protocols"]["example"]["events"][1]["day"] = 1
        out = self.check(data, "2012-02-28")
        self.assertEqual(self.rows(out, "actions.csv")[1]["date"], "2012-02-29")

    def test_all_events_and_overlapping_closure_reasons_are_preserved(self):
        data = fixture()
        data["protocols"]["example"]["events"][1]["day"] = 0
        data["calendars"]["crew"]["closures"] = [
            {"start": "2010-01-01", "end": "2010-01-02", "label": "Annual closure"},
            {"start": "2010-01-01", "end": "2010-01-01", "label": "Staff absence"},
        ]
        out = self.screen(data, "2010-01-01", "2010-01-01", 3)
        reasons = self.rows(out, "conflicts.csv")
        self.assertEqual({row["event"] for row in reasons}, {"begin", "transfer"})
        for event in ("begin", "transfer"):
            details = "\n".join(row["detail"] for row in reasons if row["event"] == event)
            self.assertIn("Annual closure", details)
            self.assertIn("Staff absence", details)

    def test_distinct_calendars_apply_to_each_event(self):
        data = fixture()
        data["calendars"]["specialist"] = copy.deepcopy(data["calendars"]["crew"])
        data["calendars"]["specialist"]["weekdays"] = ["mon"]
        data["protocols"]["example"]["events"][1].update(day=1, calendar="specialist")
        out = self.screen(data, "2010-01-03", "2010-01-04")
        self.assertEqual([(row["start"], row["status"]) for row in self.rows(out, "candidates.csv")],
                         [("2010-01-03", "allowed"), ("2010-01-04", "blocked")])
        reasons = self.rows(out, "conflicts.csv")
        self.assertTrue(any(row["calendar"] == "specialist" and row["event"] == "transfer"
                            and row["event_date"] == "2010-01-05" for row in reasons))

    def test_extra_open_overrides_weekday_but_closure_overrides_extra_open(self):
        data = fixture()
        data["calendars"]["crew"]["weekdays"] = ["mon", "tue", "wed", "thu", "fri"]
        data["calendars"]["crew"]["extra_open"] = ["2010-01-02"]
        data["protocols"]["example"]["events"] = [data["protocols"]["example"]["events"][0]]
        self.check(data, "2010-01-02")
        data["calendars"]["crew"]["closures"] = [
            {"start": "2010-01-02", "end": "2010-01-02", "label": "Exception cancelled"}
        ]
        out = self.check(data, "2010-01-02", 3, "--ics")
        self.assert_diagnostic_only(out)
        self.assertIn("Exception cancelled", (out / "report.json").read_text(encoding="utf-8"))

    def test_unknown_coverage_fails_closed_and_retains_known_reasons(self):
        data = fixture()
        data["calendars"]["crew"]["coverage_end"] = "2010-01-15"
        data["calendars"]["crew"]["closures"] = [
            {"start": "2010-01-01", "end": "2010-01-01", "label": "Known closure"}
        ]
        out = self.screen(data, "2010-01-01", "2010-01-01", 3, "--ics")
        self.assertEqual(self.rows(out, "candidates.csv")[0]["status"], "unknown")
        reasons = self.rows(out, "conflicts.csv")
        self.assertEqual({row["event"] for row in reasons}, {"begin", "transfer"})
        self.assertIn("Known closure", "\n".join(row["detail"] for row in reasons))
        self.assertNotIn("BEGIN:VEVENT", (out / "excluded-starts.ics").read_text(encoding="utf-8"))
        checked = self.check(data, "2010-01-01", 3, "--ics")
        self.assert_diagnostic_only(checked)

    def test_computed_dates_after_2199_are_unknown(self):
        data = fixture()
        data["calendars"]["crew"].update(coverage_start="2199-01-01", coverage_end="2199-12-31")
        data["protocols"]["example"]["events"][1]["day"] = 1
        out = self.check(data, "2199-12-31", 3, "--ics")
        self.assert_diagnostic_only(out)
        self.assertIn("unknown", (out / "report.json").read_text(encoding="utf-8"))

    def test_selected_protocols_are_complete_and_one_without_allowed_start_changes_exit(self):
        data = fixture()
        data["calendars"]["closed"] = copy.deepcopy(data["calendars"]["crew"])
        data["calendars"]["closed"]["weekdays"] = []
        data["protocols"]["another"] = copy.deepcopy(data["protocols"]["example"])
        for event in data["protocols"]["another"]["events"]:
            event["calendar"] = "closed"
        out = self.screen(data, "2010-01-01", "2010-01-02", 3)
        candidates = self.rows(out, "candidates.csv")
        self.assertEqual(len(candidates), 4)
        self.assertEqual({row["protocol"] for row in candidates}, {"another", "example"})
        selected = self.screen(data, "2010-01-01", "2010-01-02", 0, "--protocol", "example")
        self.assertEqual({row["protocol"] for row in self.rows(selected, "candidates.csv")}, {"example"})

    def test_canonical_fingerprint_detects_stale_configuration(self):
        data = fixture()
        out = self.screen(data, "2010-01-01", "2010-01-02")
        fingerprint = self.rows(out, "candidates.csv")[0]["config_sha256"]
        self.assertRegex(fingerprint, r"^[0-9a-f]{64}$")
        self.check(data, "2010-01-01", 0, "--expect-sha256", fingerprint)
        data["name"] = "Changed plan"
        plan = self.plan(data)
        stale = self.path()
        self.cli("check", plan, "example", "2010-01-01", "--out", stale,
                 "--expect-sha256", fingerprint, expected=2)
        self.assertFalse(stale.exists())

    def test_outputs_are_deterministic_and_do_not_leak_input_paths(self):
        data = fixture()
        data["calendars"]["crew"]["closures"] = [
            {"start": "2010-01-31", "end": "2010-01-31", "label": "Closed"}
        ]
        first = self.screen(data, "2010-01-01", "2010-01-02", 0, "--ics")
        # Formatting and object-key order must not affect canonical config identity.
        second_plan = self.plan(raw=json.dumps(data, sort_keys=True, indent=3))
        second = self.path()
        self.cli("screen", second_plan, "--from", "2010-01-01", "--through", "2010-01-02",
                 "--out", second, "--ics")
        self.assertEqual({path.name for path in first.iterdir()}, {path.name for path in second.iterdir()})
        for path in first.iterdir():
            first_bytes = path.read_bytes()
            second_bytes = (second / path.name).read_bytes()
            if path.suffix == ".ics":
                # RFC creation metadata may vary; event identity/content must not.
                first_bytes = re.sub(rb"(?m)^DTSTAMP:[^\r\n]+\r\n", b"", first_bytes)
                second_bytes = re.sub(rb"(?m)^DTSTAMP:[^\r\n]+\r\n", b"", second_bytes)
            self.assertEqual(first_bytes, second_bytes, path.name)
            self.assertNotIn(str(self.work).encode(), path.read_bytes())

    def test_csv_contract_columns(self):
        out = self.screen(fixture(), "2010-01-01", "2010-01-01")
        self.assertEqual(list(self.rows(out, "candidates.csv")[0]),
                         ["protocol", "start", "status", "config_sha256"])
        header = (out / "conflicts.csv").read_text(encoding="utf-8").splitlines()[0]
        self.assertEqual(next(csv.reader([header])),
                         ["protocol", "start", "event", "event_date", "calendar", "kind", "detail"])
        checked = self.check(fixture(), "2010-01-01")
        self.assertEqual(list(self.rows(checked, "actions.csv")[0]),
                         ["date", "protocol", "event", "action", "calendar", "config_sha256"])

    def test_ics_is_all_day_folded_utf8_without_alarms(self):
        data = fixture()
        data["protocols"]["example"]["events"][0]["action"] = "Prepare " + "é" * 150
        out = self.check(data, "2010-01-01", 0, "--ics")
        raw = (out / "actions.ics").read_bytes()
        self.assertNotIn(b"\n", raw.replace(b"\r\n", b""))
        self.assertTrue(raw.endswith(b"\r\n"))
        for line in raw.split(b"\r\n"):
            self.assertLessEqual(len(line), 75, repr(line))
            line.decode("utf-8")
        unfolded = re.sub(r"\r\n[ \t]", "", raw.decode("utf-8"))
        self.assertEqual(unfolded.count("BEGIN:VEVENT"), 2)
        self.assertIn("DTSTART;VALUE=DATE:20100101", unfolded)
        self.assertIn("DTSTART;VALUE=DATE:20100131", unfolded)
        self.assertNotIn("VALARM", unfolded)
        self.assertEqual(len(re.findall(r"^UID:.+$", unfolded, flags=re.MULTILINE)), 2)

    def test_invalid_schema_values_are_rejected_without_publishing(self):
        changes = [
            ("boolean schema version", lambda p: p.update(schema_version=True)),
            ("unknown top field", lambda p: p.update(unrecognized="value")),
            ("boolean event offset", lambda p: p["protocols"]["example"]["events"][1].update(day=True)),
            ("floating event offset", lambda p: p["protocols"]["example"]["events"][1].update(day=30.0)),
            ("negative event offset", lambda p: p["protocols"]["example"]["events"][1].update(day=-1)),
            ("too large event offset", lambda p: p["protocols"]["example"]["events"][1].update(day=3661)),
            ("NaN", lambda p: p["protocols"]["example"]["events"][1].update(day=float("nan"))),
            ("unknown calendar", lambda p: p["protocols"]["example"]["events"][1].update(calendar="absent")),
            ("unknown event field", lambda p: p["protocols"]["example"]["events"][1].update(extra="value")),
            ("duplicate event id", lambda p: p["protocols"]["example"]["events"][1].update(id="begin")),
            ("no day zero", lambda p: p["protocols"]["example"]["events"][0].update(day=1)),
            ("duplicate weekday", lambda p: p["calendars"]["crew"].update(weekdays=["mon", "mon"])),
            ("unknown weekday", lambda p: p["calendars"]["crew"].update(weekdays=["Monday"])),
            ("unknown calendar field", lambda p: p["calendars"]["crew"].update(extra=1)),
            ("non-ISO date", lambda p: p["calendars"]["crew"].update(coverage_start="2009-1-01")),
            ("impossible date", lambda p: p["calendars"]["crew"].update(coverage_start="2009-02-29")),
            ("date below supported minimum", lambda p: p["calendars"]["crew"].update(coverage_start="1899-12-31")),
            ("extra open outside coverage", lambda p: p["calendars"]["crew"].update(extra_open=["2012-01-01"])),
            ("duplicate extra open", lambda p: p["calendars"]["crew"].update(extra_open=["2010-01-01", "2010-01-01"])),
            ("unsafe formula name", lambda p: p.update(name="=HYPERLINK(1)")),
            ("unsafe action", lambda p: p["protocols"]["example"]["events"][0].update(action="@SUM(1)")),
            ("newline source", lambda p: p["protocols"]["example"].update(source="source\nsecond line")),
            ("blank source", lambda p: p["protocols"]["example"].update(source="")),
            ("trailing whitespace", lambda p: p.update(name="name ")),
        ]
        for label, mutation in changes:
            with self.subTest(label=label):
                data = fixture()
                mutation(data)
                plan = self.plan(data)
                original = plan.read_bytes()
                out = self.path()
                self.cli("screen", plan, "--from", "2010-01-01", "--through", "2010-01-01",
                         "--out", out, expected=2)
                self.assertFalse(out.exists())
                self.assertEqual(plan.read_bytes(), original)

    def test_malformed_duplicate_key_and_oversized_json(self):
        duplicate = json.dumps(fixture()).replace('"schema_version": 1', '"schema_version": 1, "schema_version": 1', 1)
        for raw in ("{", "[]", "null", duplicate, " " * (2 * 1024 * 1024 + 1)):
            with self.subTest(prefix=raw[:60]):
                plan = self.plan(raw=raw)
                self.cli("validate", plan, expected=2)

    def test_hostile_integer_utf8_and_nesting_fail_cleanly(self):
        huge_integer = json.dumps(fixture()).replace('"schema_version": 1', '"schema_version": ' + '9' * 5000, 1)
        deep_json = '[' * 1500 + '0' + ']' * 1500
        for raw in (huge_integer, deep_json):
            with self.subTest(kind="huge_integer" if raw == huge_integer else "deep_json"):
                plan = self.plan(raw=raw)
                self.cli("validate", plan, expected=2)
        invalid_utf8 = self.path("invalid-utf8").with_suffix(".json")
        invalid_utf8.write_bytes(b'{"name":"\xff"}')
        self.cli("validate", invalid_utf8, expected=2)

    def test_resource_bounds_fail_without_publishing(self):
        data = fixture()
        data["calendars"]["crew"].update(coverage_start="1900-01-01", coverage_end="2199-12-31")
        plan = self.plan(data)
        out = self.path()
        self.cli("screen", plan, "--from", "2000-01-01", "--through", "2011-01-01", "--out", out, expected=2)
        self.assertFalse(out.exists())
        template = data["protocols"]["example"]
        template["events"] = [{"id": f"e{i}", "day": i, "action": f"Action {i}", "calendar": "crew"}
                              for i in range(128)]
        data["protocols"] = {f"p{i}": copy.deepcopy(template) for i in range(100)}
        plan = self.plan(data)
        out = self.path()
        self.cli("screen", plan, "--from", "2010-01-01", "--through", "2010-01-20", "--out", out, expected=2)
        self.assertFalse(out.exists())

    def test_overlapping_closures_hit_output_bound_with_only_eight_event_evaluations(self):
        data = fixture()
        data["calendars"]["crew"]["closures"] = [
            {"start": "2010-01-01", "end": "2010-12-31", "label": f"Closure {number:03d} " + "x" * 488}
            for number in range(512)
        ]
        self.assertTrue(all(len(closure["label"]) == 500 for closure in data["calendars"]["crew"]["closures"]))
        plan = self.plan(data)
        # The schema is valid and four candidates need only eight event checks,
        # but 4 * 2 * 512 distinct 500-character reasons exceed 2,000,000 chars.
        self.cli("validate", plan)
        original = plan.read_bytes()
        out = self.path()
        self.cli("screen", plan, "--from", "2010-01-01", "--through", "2010-01-04",
                 "--out", out, expected=2)
        self.assertFalse(out.exists())
        self.assertEqual(plan.read_bytes(), original)

    def test_candidate_row_bound_applies_below_event_evaluation_bound(self):
        data = fixture()
        template = data["protocols"]["example"]
        template["events"] = [template["events"][0]]
        data["protocols"] = {f"p{number}": copy.deepcopy(template) for number in range(100)}
        plan = self.plan(data)
        self.cli("validate", plan)
        out = self.path()
        # 501 inclusive dates * 100 one-event protocols = 50,100 candidates,
        # while event evaluations remain below their independent 250,000 bound.
        self.cli("screen", plan, "--from", "2009-01-01", "--through", "2010-05-16",
                 "--out", out, expected=2)
        self.assertFalse(out.exists())

    def test_screen_reason_count_bound_with_short_closure_labels(self):
        data = fixture()
        data["protocols"]["example"]["events"] = [data["protocols"]["example"]["events"][0]]
        data["calendars"]["crew"]["closures"] = [
            {"start": "2010-01-01", "end": "2010-12-31", "label": f"c{number:03d}"}
            for number in range(512)
        ]
        plan = self.plan(data)
        self.cli("validate", plan)
        out = self.path()
        # 98 dates * 512 reasons = 50,176 reasons, but only 200,704 detail
        # characters; the reason-count cap must apply before the character cap.
        self.cli("screen", plan, "--from", "2010-01-01", "--through", "2010-04-08",
                 "--out", out, expected=2)
        self.assertFalse(out.exists())

    def test_single_check_reason_count_bound_with_short_closure_labels(self):
        data = fixture()
        data["protocols"]["example"]["events"] = [
            {"id": f"e{number}", "day": 0, "action": f"Action {number}", "calendar": "crew"}
            for number in range(128)
        ]
        data["calendars"]["crew"]["closures"] = [
            {"start": "2010-01-01", "end": "2010-01-01", "label": f"c{number:03d}"}
            for number in range(512)
        ]
        plan = self.plan(data)
        self.cli("validate", plan)
        out = self.path()
        # One check produces 65,536 reasons and 262,144 detail characters.
        self.cli("check", plan, "example", "2010-01-01", "--out", out, "--ics", expected=2)
        self.assertFalse(out.exists())

    def test_no_overwrite_of_existing_directory_or_file(self):
        plan = self.plan()
        directory = self.path()
        directory.mkdir()
        marker = directory / "keep.txt"
        marker.write_bytes(b"untouched")
        self.cli("screen", plan, "--from", "2010-01-01", "--through", "2010-01-01",
                 "--out", directory, expected=2)
        self.assertEqual(list(directory.iterdir()), [marker])
        self.assertEqual(marker.read_bytes(), b"untouched")
        output_file = self.path()
        output_file.write_bytes(b"existing file")
        self.cli("check", plan, "example", "2010-01-01", "--out", output_file, expected=2)
        self.assertEqual(output_file.read_bytes(), b"existing file")

    def test_broken_output_symlink_is_preserved(self):
        plan = self.plan()
        target = self.path("missing-target")
        destination = self.path("dangling-output")
        try:
            destination.symlink_to(target, target_is_directory=True)
        except (OSError, NotImplementedError) as error:
            if os.name == "nt":
                self.skipTest(f"Windows does not permit this symlink: {error}")
            raise
        self.assertTrue(destination.is_symlink())
        self.assertFalse(destination.exists())
        original_link = os.readlink(destination)
        self.cli("check", plan, "example", "2010-01-01", "--out", destination, expected=2)
        self.assertTrue(destination.is_symlink())
        self.assertEqual(os.readlink(destination), original_link)
        self.assertFalse(target.exists())

    def test_invalid_cli_inputs_do_not_publish(self):
        plan = self.plan()
        for options in (("--from", "2010-01-02", "--through", "2010-01-01"),
                        ("--from", "2010-01-01", "--through", "2010-01-01", "--protocol", "absent")):
            with self.subTest(options=options):
                out = self.path()
                self.cli("screen", plan, *options, "--out", out, expected=2)
                self.assertFalse(out.exists())

    def test_init_creates_valid_constructed_example_and_refuses_existing_target(self):
        directory = self.path("initialized")
        self.cli("init", directory)
        self.assertTrue((directory / "plan.json").is_file())
        self.assertTrue((directory / "README.txt").is_file())
        self.cli("validate", directory / "plan.json")
        before = {path.name: path.read_bytes() for path in directory.iterdir() if path.is_file()}
        self.cli("init", directory, expected=2)
        self.assertEqual(before, {path.name: path.read_bytes() for path in directory.iterdir() if path.is_file()})


if __name__ == "__main__":
    unittest.main()
