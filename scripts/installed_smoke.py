"""Exercise an installed distribution from a fresh working directory.

Run with the installed environment's interpreter. No checkout imports.
"""
from pathlib import Path
import json
import os
import subprocess
import sys
import tempfile


command = [sys.executable, "-I", str(Path(sys.argv[1]).resolve())] if len(sys.argv) == 2 else [sys.executable, "-I", "-m", "seedstartgate"]


def run(*arguments, expected=0, cwd):
    result = subprocess.run([*command, *map(str, arguments)], cwd=cwd, capture_output=True, text=True)
    if result.returncode != expected:
        raise AssertionError(f"{arguments}: expected {expected}, got {result.returncode}: {result.stdout} {result.stderr}")
    return result


with tempfile.TemporaryDirectory(prefix="seedstartgate-smoke-") as temporary:
    base = Path(temporary)
    run("init", "example", cwd=base)
    example = base / "example"
    run("validate", "plan.json", cwd=example)
    run("screen", "plan.json", "--from", "2027-02-01", "--through", "2027-02-14", "--out", "screen", "--ics", cwd=example)
    report = json.loads((example / "screen" / "report.json").read_text(encoding="utf-8"))
    assert len(report["candidates"]) == 14
    run("check", "plan.json", "demo", "2027-02-01", "--out", "allowed", "--ics", "--expect-sha256", report["config_sha256"], cwd=example)
    run("check", "plan.json", "demo", "2027-02-08", "--out", "blocked", "--ics", cwd=example, expected=3)
    assert not (example / "blocked" / "actions.ics").exists()
    run("check", "plan.json", "demo", "2027-02-01", "--out", "allowed", cwd=example, expected=2)
    run("check", "plan.json", "demo", "2027-02-01", "--out", "stale", "--expect-sha256", "0" * 64, cwd=example, expected=2)
    assert not (example / "stale").exists()
    moved = base / "relocated"
    example.rename(moved)
    run("check", "plan.json", "demo", "2027-02-01", "--out", "after-move", cwd=moved)
print("Installed workflow passed: screening, allowed actions, blocked/no ICS, no-overwrite, stale fingerprint and relocation.")
