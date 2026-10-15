"""Deterministic text/CSV reports and optional all-day iCalendar snapshots."""
from __future__ import annotations

import csv
from datetime import date, timedelta
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
from typing import Callable

from .core import InputError


def publish_directory(destination: str | Path, write: Callable[[Path], None]) -> None:
    """Publish one complete local output directory, without overwriting a path."""
    target = Path(destination).absolute()
    if os.path.lexists(target):
        raise InputError(f"output already exists: {target}")
    if not target.parent.is_dir():
        raise InputError("output parent directory must already exist")
    staging = Path(tempfile.mkdtemp(prefix=".seedstartgate-", dir=target.parent))
    try:
        write(staging)
        if os.path.lexists(target):
            raise InputError(f"output already exists: {target}")
        os.rename(staging, target)
    finally:
        if staging.exists():
            shutil.rmtree(staging)


def _text(path: Path, value: str) -> None:
    with path.open("x", encoding="utf-8", newline="") as handle:
        handle.write(value)


def _csv(path: Path, fields: list[str], rows) -> None:
    with path.open("x", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def _escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")


def _fold(line: str) -> str:
    """RFC 5545 folding at 75 UTF-8 octets, without splitting a code point."""
    result, current, size = [], "", 0
    for char in line:
        length = len(char.encode("utf-8"))
        if size + length > 75:
            result.append(current)
            current, size = " ", 1
        current += char
        size += length
    result.append(current)
    return "\r\n".join(result)


def _ics(events: list[dict], created: str) -> str:
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//SeedStartGate//Calendar snapshot 1//EN", "CALSCALE:GREGORIAN"]
    for event in events:
        day = date.fromisoformat(event["date"])
        uid = hashlib.sha256(json.dumps(event, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()
        lines.extend(["BEGIN:VEVENT", f"UID:{uid}@seedstartgate.invalid", f"DTSTAMP:{created}",
                      f"DTSTART;VALUE=DATE:{day:%Y%m%d}", f"DTEND;VALUE=DATE:{day + timedelta(days=1):%Y%m%d}",
                      f"SUMMARY:{_escape(event['summary'])}", f"DESCRIPTION:{_escape(event['description'])}",
                      "TRANSP:TRANSPARENT", "END:VEVENT"])
    lines.append("END:VCALENDAR")
    return "\r\n".join(_fold(line) for line in lines) + "\r\n"


def write_screen(directory: Path, report: dict, ics_timestamp: str | None = None) -> None:
    _text(directory / "report.json", json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    rows = ({**row, "config_sha256": report["config_sha256"]} for row in report["candidates"])
    _csv(directory / "candidates.csv", ["protocol", "start", "status", "config_sha256"], rows)
    issues = ({"protocol": row["protocol"], "start": row["start"], **issue} for row in report["candidates"] for issue in row["issues"])
    _csv(directory / "conflicts.csv", ["protocol", "start", "event", "event_date", "calendar", "kind", "detail"], issues)
    lines = ["SeedStartGate | Start-date screening", report["name"], f"Status: {report['status']}", f"Range: {report['from']} through {report['through']} (inclusive)", f"Configuration SHA-256: {report['config_sha256']}", "", "Protocol                         Allowed   Blocked   Unknown"]
    for key, counts in report["counts"].items():
        lines.append(f"{key:32} {counts['allowed']:7} {counts['blocked']:9} {counts['unknown']:9}")
    lines.extend(["", "Read candidates.csv for every start date and conflicts.csv for every reason.", "Unknown dates are never permitted. A complete screen is not a capacity guarantee.", "Check a selected start against the current plan before using its action worklist.", ""])
    _text(directory / "summary.txt", "\n".join(lines))
    if ics_timestamp is not None:
        events = []
        for row in report["candidates"]:
            if row["status"] != "blocked":
                continue
            details = "\n".join(f"{i['event']} on {i['event_date']} ({i['calendar']}): {i['detail']}" for i in row["issues"])
            events.append({"date": row["start"], "summary": f"DO NOT START: {row['protocol']}", "description": f"SeedStartGate known exclusion.\n{details}\nConfiguration SHA-256: {report['config_sha256']}"})
        _text(directory / "excluded-starts.ics", _ics(events, ics_timestamp))


def write_check(directory: Path, report: dict, ics_timestamp: str | None = None) -> None:
    _text(directory / "report.json", json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    lines = ["SeedStartGate | Chosen-start check", report["name"], f"Protocol: {report['protocol']} ({report['protocol_label']})", f"Source: {report['protocol_source']}", f"Start: {report['start']}", f"Status: {report['status']}", f"Configuration SHA-256: {report['config_sha256']}", ""]
    if report["status"] != "allowed":
        lines.append("NO ACTION WORKLIST: this start did not pass every event.")
        lines.extend(f"{i['event']} on {i['event_date']} ({i['calendar']}): {i['kind']}: {i['detail']}" for i in report["issues"])
        _text(directory / "summary.txt", "\n".join(lines) + "\n")
        return
    lines.append("Every listed action is on a known staffed date. This does not establish treatment suitability, available labor/space, or completion.")
    _text(directory / "summary.txt", "\n".join(lines) + "\n")
    rows = [{**row, "config_sha256": report["config_sha256"]} for row in report["actions"]]
    _csv(directory / "actions.csv", ["date", "protocol", "event", "action", "calendar", "config_sha256"], rows)
    worklist = ["SeedStartGate | Dated actions", f"{report['protocol']} | start {report['start']}", f"Protocol source: {report['protocol_source']}", f"Configuration SHA-256: {report['config_sha256']}", "Status: allowed by declared staffing calendars; verify the protocol and current staffing before starting.", ""]
    worklist.extend(f"[ ] {row['date']}  {row['event']}  {row['action']}  [{row['calendar']}]" for row in rows)
    _text(directory / "actions.txt", "\n".join(worklist) + "\n")
    if ics_timestamp is not None:
        events = [{"date": row["date"], "summary": f"{row['protocol']}: {row['action']}", "description": f"Event: {row['event']}\nCalendar: {row['calendar']}\nProtocol source: {report['protocol_source']}\nStart: {report['start']}\nConfiguration SHA-256: {report['config_sha256']}\nPlanned action; not a completion record."} for row in rows]
        _text(directory / "actions.ics", _ics(events, ics_timestamp))
