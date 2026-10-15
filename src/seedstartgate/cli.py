"""Command-line interface; no network or third-party runtime dependencies."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from importlib import resources
from pathlib import Path
import re
import sys

from . import __version__
from .core import InputError, check_report, load_plan, parse_date, screen
from .output import publish_directory, write_check, write_screen


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description="Compile fixed seed-protocol offsets into do-not-start calendars. No treatment recommendations.")
    root.add_argument("--version", action="version", version=f"SeedStartGate {__version__}")
    sub = root.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init", help="create a new constructed example directory")
    init.add_argument("directory")
    validate = sub.add_parser("validate", help="validate input schema, not start-date feasibility")
    validate.add_argument("plan")
    scan = sub.add_parser("screen", help="screen every date in an inclusive range")
    scan.add_argument("plan")
    scan.add_argument("--from", dest="first", required=True, metavar="YYYY-MM-DD")
    scan.add_argument("--through", dest="last", required=True, metavar="YYYY-MM-DD")
    scan.add_argument("--protocol", action="append", help="select a protocol; repeat for multiple IDs")
    scan.add_argument("--out", required=True, help="new output directory; parent must exist")
    scan.add_argument("--ics", action="store_true", help="also export known excluded starts as an all-day calendar")
    check = sub.add_parser("check", help="check one chosen start; worklist only if every action passes")
    check.add_argument("plan")
    check.add_argument("protocol")
    check.add_argument("start", metavar="YYYY-MM-DD")
    check.add_argument("--out", required=True)
    check.add_argument("--ics", action="store_true", help="export allowed actions as an all-day calendar")
    check.add_argument("--expect-sha256", help="require the current configuration fingerprint to match a prior report")
    return root


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.command == "init":
            def write_example(directory: Path) -> None:
                bundled = resources.files("seedstartgate").joinpath("data")
                for source, target in (("example.json", "plan.json"), ("example.txt", "README.txt")):
                    (directory / target).write_bytes(bundled.joinpath(source).read_bytes())
            publish_directory(args.directory, write_example)
            print("Created constructed example. Read README.txt before use.")
            return 0
        plan = load_plan(args.plan)
        if args.command == "validate":
            print(f"Valid schema. Start dates have not been checked. SHA-256: {plan.sha256}")
            return 0
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") if args.ics else None
        if args.command == "screen":
            report = screen(plan, parse_date(args.first), parse_date(args.last), args.protocol)
            publish_directory(args.out, lambda directory: write_screen(directory, report, timestamp))
            print(f"Screen: {report['status']}. Read summary.txt, candidates.csv and conflicts.csv.")
            return 0 if report["status"] == "complete" else 3
        if args.expect_sha256 is not None:
            if not re.fullmatch(r"[a-f0-9]{64}", args.expect_sha256) or args.expect_sha256 != plan.sha256:
                raise InputError("stale or invalid configuration fingerprint; screen the current plan again")
        report = check_report(plan, args.protocol, parse_date(args.start))
        publish_directory(args.out, lambda directory: write_check(directory, report, timestamp))
        print(f"Start: {report['status']}. " + ("Complete action worklist written." if report["status"] == "allowed" else "Diagnosis only; no action worklist or calendar written."))
        return 0 if report["status"] == "allowed" else 3
    except (InputError, OSError, UnicodeError) as exc:
        print(f"seedstartgate: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
