"""Strict input validation and exhaustive fixed-offset calendar screening."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
import hashlib
import json
from pathlib import Path
import re
from typing import Any

from . import __version__

MAX_INPUT_BYTES = 2 * 1024 * 1024
MAX_EVALUATIONS = 250_000
MAX_CANDIDATES = 50_000
MAX_REASONS = 50_000
MAX_REASON_CHARS = 2_000_000
WEEKDAYS = ("mon", "tue", "wed", "thu", "fri", "sat", "sun")
ID_PATTERN = re.compile(r"[A-Za-z][A-Za-z0-9_.-]{0,63}\Z", re.ASCII)
DATE_PATTERN = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}\Z", re.ASCII)
MIN_DATE, MAX_DATE = date(1900, 1, 1), date(2199, 12, 31)


class InputError(ValueError):
    """An invalid or unsupported request; no planning result is implied."""


def _object(value: Any, keys: set[str], where: str) -> dict:
    if not isinstance(value, dict):
        raise InputError(f"{where}: expected an object")
    if set(value) != keys:
        raise InputError(f"{where}: fields must be {', '.join(sorted(keys))}")
    return value


def _text(value: Any, where: str, maximum: int = 500) -> str:
    if (not isinstance(value, str) or not value or value != value.strip()
            or len(value) > maximum or not value.isprintable()
            or value[0] in "=+-@"):
        raise InputError(f"{where}: expected nonblank single-line text (max {maximum}); no leading = + - @ or whitespace")
    return value


def _id(value: Any, where: str) -> str:
    if not isinstance(value, str) or not ID_PATTERN.fullmatch(value):
        raise InputError(f"{where}: invalid ID (ASCII letter then up to 63 letters/digits/_.-)")
    return value


def parse_date(value: Any, where: str = "date") -> date:
    if not isinstance(value, str) or not DATE_PATTERN.fullmatch(value):
        raise InputError(f"{where}: use YYYY-MM-DD")
    try:
        result = date.fromisoformat(value)
    except ValueError as exc:
        raise InputError(f"{where}: invalid calendar date {value}") from exc
    if not MIN_DATE <= result <= MAX_DATE:
        raise InputError(f"{where}: supported dates are 1900-01-01 through 2199-12-31")
    return result


def _list(value: Any, where: str, maximum: int) -> list:
    if not isinstance(value, list) or len(value) > maximum:
        raise InputError(f"{where}: expected a list with at most {maximum} entries")
    return value


def _unique_pairs(pairs: list[tuple[str, Any]]) -> dict:
    result: dict = {}
    for key, value in pairs:
        if key in result:
            raise InputError(f"duplicate JSON key: {key!r}")
        result[key] = value
    return result


def _bad_constant(value: str) -> None:
    raise InputError(f"JSON constant {value} is unsupported")


@dataclass(frozen=True)
class Calendar:
    start: date
    end: date
    weekdays: frozenset[int]
    closures: tuple[tuple[date, date, str], ...]
    extra_open: frozenset[date]

    def reasons(self, day: date) -> list[dict[str, str]]:
        if not self.start <= day <= self.end:
            return [{"kind": "unknown_coverage", "detail": f"outside checked calendar coverage {self.start} through {self.end}"}]
        closures = [label for first, last, label in self.closures if first <= day <= last]
        if closures:
            return [{"kind": "closure", "detail": label} for label in sorted(set(closures))]
        if day not in self.extra_open and day.weekday() not in self.weekdays:
            return [{"kind": "unstaffed_weekday", "detail": f"{WEEKDAYS[day.weekday()]} is not a staffed weekday"}]
        return []


@dataclass(frozen=True)
class Event:
    id: str
    day: int
    action: str
    calendar: str


@dataclass(frozen=True)
class Protocol:
    label: str
    source: str
    events: tuple[Event, ...]


@dataclass(frozen=True)
class Plan:
    name: str
    calendars: dict[str, Calendar]
    protocols: dict[str, Protocol]
    sha256: str


def parse_plan(raw: Any) -> Plan:
    obj = _object(raw, {"schema_version", "name", "calendars", "protocols"}, "plan")
    if type(obj["schema_version"]) is not int or obj["schema_version"] != 1:
        raise InputError("schema_version: expected integer 1")
    name = _text(obj["name"], "name", 200)
    raw_calendars = obj["calendars"]
    if not isinstance(raw_calendars, dict) or not 1 <= len(raw_calendars) <= 32:
        raise InputError("calendars: expected 1..32 named objects")
    calendars = {}
    for key, value in sorted(raw_calendars.items()):
        _id(key, "calendar ID")
        c = _object(value, {"coverage_start", "coverage_end", "weekdays", "closures", "extra_open"}, f"calendar {key}")
        first = parse_date(c["coverage_start"], f"{key}.coverage_start")
        last = parse_date(c["coverage_end"], f"{key}.coverage_end")
        if first > last:
            raise InputError(f"{key}: coverage_start must not follow coverage_end")
        weekdays = _list(c["weekdays"], f"{key}.weekdays", 7)
        if any(not isinstance(d, str) or d not in WEEKDAYS for d in weekdays) or len(set(weekdays)) != len(weekdays):
            raise InputError(f"{key}.weekdays: use unique mon/tue/wed/thu/fri/sat/sun values")
        closures = []
        for i, closure in enumerate(_list(c["closures"], f"{key}.closures", 512)):
            r = _object(closure, {"start", "end", "label"}, f"{key}.closures[{i}]")
            a, b = parse_date(r["start"]), parse_date(r["end"])
            label = _text(r["label"], "closure label")
            if not first <= a <= b <= last:
                raise InputError(f"{key}: closure range must be ordered and inside coverage")
            closures.append((a, b, label))
        opened = [parse_date(d, f"{key}.extra_open") for d in _list(c["extra_open"], f"{key}.extra_open", 3660)]
        if len(set(opened)) != len(opened) or any(not first <= d <= last for d in opened):
            raise InputError(f"{key}.extra_open: dates must be unique and inside coverage")
        calendars[key] = Calendar(first, last, frozenset(WEEKDAYS.index(d) for d in weekdays), tuple(closures), frozenset(opened))
    raw_protocols = obj["protocols"]
    if not isinstance(raw_protocols, dict) or not 1 <= len(raw_protocols) <= 100:
        raise InputError("protocols: expected 1..100 named objects")
    protocols = {}
    for key, value in sorted(raw_protocols.items()):
        _id(key, "protocol ID")
        p = _object(value, {"label", "source", "events"}, f"protocol {key}")
        label, source = _text(p["label"], f"{key}.label"), _text(p["source"], f"{key}.source")
        events = []
        for i, value in enumerate(_list(p["events"], f"{key}.events", 128)):
            e = _object(value, {"id", "day", "action", "calendar"}, f"{key}.events[{i}]")
            event_id = _id(e["id"], "event ID")
            if type(e["day"]) is not int or not 0 <= e["day"] <= 3660:
                raise InputError(f"{key}.{event_id}.day: expected integer 0..3660")
            action = _text(e["action"], f"{key}.{event_id}.action")
            cal = _id(e["calendar"], f"{key}.{event_id}.calendar")
            if cal not in calendars:
                raise InputError(f"{key}.{event_id}: unknown calendar {cal}")
            events.append(Event(event_id, e["day"], action, cal))
        if not events or not any(e.day == 0 for e in events):
            raise InputError(f"{key}: at least one day-zero event is required")
        if len({e.id for e in events}) != len(events):
            raise InputError(f"{key}: duplicate event ID")
        protocols[key] = Protocol(label, source, tuple(sorted(events, key=lambda e: (e.day, e.id))))
    canonical = json.dumps(raw, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode("utf-8")
    return Plan(name, calendars, protocols, hashlib.sha256(canonical).hexdigest())


def load_plan(path: str | Path) -> Plan:
    try:
        with Path(path).open("rb") as handle:
            data = handle.read(MAX_INPUT_BYTES + 1)
        if len(data) > MAX_INPUT_BYTES:
            raise InputError("plan exceeds 2 MiB input limit")
        raw = json.loads(data.decode("utf-8"), object_pairs_hook=_unique_pairs, parse_constant=_bad_constant)
        return parse_plan(raw)
    except InputError:
        raise
    except (UnicodeError, ValueError, RecursionError) as exc:
        raise InputError(f"invalid UTF-8 JSON: {exc}") from exc


def _protocol(plan: Plan, protocol: str) -> Protocol:
    if protocol not in plan.protocols:
        raise InputError(f"unknown protocol {protocol!r}")
    return plan.protocols[protocol]


def check_start(plan: Plan, protocol: str, start: date) -> dict:
    """Return every action and every reason, without changing any dates."""
    p = _protocol(plan, protocol)
    if not MIN_DATE <= start <= MAX_DATE:
        raise InputError("start date is outside the supported range")
    actions, issues = [], []
    reason_chars = 0
    for event in p.events:
        event_date = start + timedelta(days=event.day)
        reasons = plan.calendars[event.calendar].reasons(event_date)
        actions.append({"date": event_date.isoformat(), "protocol": protocol, "event": event.id, "action": event.action, "calendar": event.calendar})
        for reason in reasons:
            reason_chars += len(reason["detail"])
            if len(issues) >= MAX_REASONS or reason_chars > MAX_REASON_CHARS:
                raise InputError("conflict reason output exceeds supported bound; split the request or simplify closures")
            issues.append({"event": event.id, "event_date": event_date.isoformat(), "calendar": event.calendar, **reason})
    status = "unknown" if any(i["kind"] == "unknown_coverage" for i in issues) else "blocked" if issues else "allowed"
    return {"protocol": protocol, "start": start.isoformat(), "status": status, "issues": issues, "actions": actions}


def envelope(plan: Plan, kind: str) -> dict:
    return {"schema_version": 1, "product": "SeedStartGate", "product_version": __version__, "kind": kind, "name": plan.name, "config_sha256": plan.sha256}


def screen(plan: Plan, first: date, last: date, protocols: list[str] | None = None) -> dict:
    selected = sorted(plan.protocols if protocols is None else protocols)
    if not selected or len(set(selected)) != len(selected):
        raise InputError("select at least one protocol, without duplicate IDs")
    for key in selected:
        _protocol(plan, key)
    days = (last - first).days + 1
    if not MIN_DATE <= first <= last <= MAX_DATE or not 1 <= days <= 3660:
        raise InputError("screen range must be ordered, supported, and contain at most 3660 dates")
    evaluations = days * sum(len(plan.protocols[key].events) for key in selected)
    if days * len(selected) > MAX_CANDIDATES:
        raise InputError(f"maximum {MAX_CANDIDATES} candidate rows; split the range or select fewer protocols")
    if evaluations > MAX_EVALUATIONS:
        raise InputError(f"request needs {evaluations} event evaluations; maximum is {MAX_EVALUATIONS}; split the range or select fewer protocols")
    candidates, counts = [], {}
    reason_count = reason_chars = 0
    for key in selected:
        counts[key] = {"allowed": 0, "blocked": 0, "unknown": 0}
        for offset in range(days):
            checked = check_start(plan, key, first + timedelta(days=offset))
            checked.pop("actions")
            reason_count += len(checked["issues"])
            reason_chars += sum(len(i["detail"]) for i in checked["issues"])
            if reason_count > MAX_REASONS or reason_chars > MAX_REASON_CHARS:
                raise InputError("conflict reason output exceeds supported bound; split the request or simplify closures")
            candidates.append(checked)
            counts[key][checked["status"]] += 1
    attention = any(c["unknown"] or not c["allowed"] for c in counts.values())
    return {**envelope(plan, "screen"), "from": first.isoformat(), "through": last.isoformat(), "status": "needs_attention" if attention else "complete", "counts": counts, "candidates": candidates}


def check_report(plan: Plan, protocol: str, start: date) -> dict:
    result = check_start(plan, protocol, start)
    # A rejected start must not ship a worklist even in the machine-readable report.
    if result["status"] != "allowed":
        result.pop("actions")
    p = _protocol(plan, protocol)
    return {**envelope(plan, "check"), "protocol_label": p.label, "protocol_source": p.source, **result}
