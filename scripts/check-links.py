#!/usr/bin/env python3
"""Check local Markdown links and cross-repo GitHub links in weave-docs."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SIBLING_WEAVE = ROOT.parent / "weave"

LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
FENCE_RE = re.compile(r"^(```|~~~)")
INLINE_CODE_RE = re.compile(r"`[^`]*`")
GITHUB_LINK_RE = re.compile(
    r"https://github\.com/prulloac/(weave|weave-docs)/(?:blob|tree)/main/([^\s)#]+)"
)
EXTERNAL_PREFIXES = ("http://", "https://", "mailto:", "tel:", "data:", "weave://", "#")


def split_target(raw: str) -> str:
    if raw.startswith("<"):
        end = raw.find(">")
        if end != -1:
            return raw[1:end]
    return raw.split(None, 1)[0]


def main() -> int:
    files = sorted(ROOT.rglob("*.md"))
    failures = 0
    checked = 0

    for path in files:
        rel = path.relative_to(ROOT).as_posix()
        in_fence = False
        for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if FENCE_RE.match(line.strip()):
                in_fence = not in_fence
                continue
            if in_fence:
                continue

            cleaned = INLINE_CODE_RE.sub("", line)
            for match in LINK_RE.finditer(cleaned):
                raw = split_target(match.group(1).strip())
                if not raw or raw.startswith(EXTERNAL_PREFIXES):
                    continue
                checked += 1
                target = raw.partition("#")[0].partition("?")[0]
                if not target or target.startswith("/"):
                    continue
                resolved = (path.parent / target).resolve()
                try:
                    resolved.relative_to(ROOT)
                except ValueError:
                    print(f"{rel}:{line_no}: link escapes the repository: {raw}")
                    failures += 1
                    continue
                if not resolved.exists():
                    print(f"{rel}:{line_no}: missing local target: {raw}")
                    failures += 1

            for match in GITHUB_LINK_RE.finditer(cleaned):
                repo, target = match.groups()
                checked += 1
                base = SIBLING_WEAVE if repo == "weave" else ROOT
                if base.exists() and not (base / target).exists():
                    print(f"{rel}:{line_no}: missing {repo} target: {target}")
                    failures += 1

    print(f"check-links: checked {checked} links in {len(files)} files, {failures} failures")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
