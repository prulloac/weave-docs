#!/usr/bin/env python3
"""Check release status, the Feature Register, backlog rows and spec indexing in weave-docs."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SIBLING_WEAVE = ROOT.parent / "weave"
SPECS = ROOT / "specs"

STATUS_LINE_PREFIX = "Status: **"
STATUS_LINE_RE = re.compile(r"^Status: \*\*(v\d+\.\d+\.\d+) is the current")
REGISTER_HEADING = "### Feature Register"
REGISTER_ROW_RE = re.compile(r"^\| \d+ \|")
REGISTER_STATUSES = {"shipped", "stretch", "deferred", "planned", "in progress"}
BACKLOG_STATUSES = {"backlog", "in-progress", "red", "green", "review", "done", "stretch"}
SPEC_LINK_RE = re.compile(r"\((specs/[^)\s]+\.md)\)")
SPEC_STATUSES = {"draft", "stable", "deprecated"}


def cells(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def latest_weave_tag() -> str | None:
    if not (SIBLING_WEAVE / ".git").exists():
        return None
    result = subprocess.run(
        ["git", "-C", str(SIBLING_WEAVE), "tag", "--list", "v*", "--sort=-v:refname"],
        capture_output=True,
        text=True,
        check=False,
    )
    tags = result.stdout.split()
    return tags[0] if tags else None


def check_release_status(roadmap: str, errors: list[str]) -> int:
    status_line = next((line for line in roadmap.splitlines() if line.startswith(STATUS_LINE_PREFIX)), "")
    match = STATUS_LINE_RE.match(status_line)
    if match is None:
        errors.append("ROADMAP.md: status line naming the current release not found")
        return 1
    latest = latest_weave_tag()
    if latest is None:
        print("note: ../weave tags not found; release status not compared")
        return 0
    if match.group(1) != latest:
        errors.append(f"ROADMAP.md: status line says {match.group(1)}, latest weave tag is {latest}")
    return 1


def check_register(roadmap: str, errors: list[str]) -> int:
    section = roadmap[roadmap.index(REGISTER_HEADING) :]
    end = section.find("\nRules:")
    if end != -1:
        section = section[:end]
    checked = 0
    expected = 1
    for line in section.splitlines():
        if not REGISTER_ROW_RE.match(line):
            continue
        row = cells(line)
        number = int(row[0])
        checked += 1
        if number != expected:
            errors.append(f"ROADMAP.md: register row {number} found where {expected} expected")
        expected = number + 1
        if row[6] not in REGISTER_STATUSES:
            errors.append(f"ROADMAP.md: register row {number} has unknown status '{row[6]}'")
        links = SPEC_LINK_RE.findall(row[2])
        if not links:
            errors.append(f"ROADMAP.md: register row {number} has no spec link")
        for link in links:
            if not (ROOT / link).exists():
                errors.append(f"ROADMAP.md: register row {number} links missing {link}")
    return checked


def check_backlog(backlog: str, errors: list[str]) -> int:
    checked = 0
    for line in backlog.splitlines():
        if not line.startswith("|"):
            continue
        row = cells(line)
        if len(row) != 7 or row[0].startswith("---") or row[6] == "Status":
            continue
        checked += 1
        if row[6] not in BACKLOG_STATUSES:
            errors.append(f"backlog.md: row '{row[0]}' has unknown status '{row[6]}'")
        for link in SPEC_LINK_RE.findall(row[1]):
            if not (ROOT / link).exists():
                errors.append(f"backlog.md: row '{row[0]}' links missing {link}")
    return checked


def frontmatter(text: str) -> dict[str, str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    values: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        key, sep, value = line.partition(":")
        if sep and not line.startswith(" "):
            values[key.strip()] = value.strip().strip('"')
    return values


def check_specs(errors: list[str]) -> int:
    index = (SPECS / "README.md").read_text(encoding="utf-8")
    checked = 0
    for path in sorted(SPECS.glob("*.md")):
        if path.name == "README.md":
            continue
        checked += 1
        if f"({path.name})" not in index:
            errors.append(f"specs/README.md: no row links specs/{path.name}")
        front = frontmatter(path.read_text(encoding="utf-8"))
        if front.get("type") != "specification":
            errors.append(f"specs/{path.name}: frontmatter type must be 'specification'")
        if front.get("status") not in SPEC_STATUSES:
            errors.append(f"specs/{path.name}: frontmatter status must be draft, stable or deprecated")
    return checked


def main() -> int:
    errors: list[str] = []
    roadmap = (ROOT / "ROADMAP.md").read_text(encoding="utf-8")
    backlog = (ROOT / "backlog.md").read_text(encoding="utf-8")
    checked = check_release_status(roadmap, errors)
    checked += check_register(roadmap, errors)
    checked += check_backlog(backlog, errors)
    checked += check_specs(errors)
    for error in errors:
        print(f"FAIL {error}")
    print(f"check-consistency: checked {checked} items, {len(errors)} failures")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
