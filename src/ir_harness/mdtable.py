"""Minimal markdown helpers: sections, pipe tables and backticked tokens."""

from __future__ import annotations

import re

_HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*$")
_SEPARATOR = re.compile(r":?-{2,}:?")
_BACKTICK = re.compile(r"`([^`]+)`")


def section(text: str, heading: str) -> str:
    """Return the body under ``heading`` up to the next heading of the same or higher level."""
    body: list[str] = []
    level = 0
    inside = False
    for line in text.splitlines():
        match = _HEADING.match(line)
        if match:
            depth, title = len(match.group(1)), match.group(2)
            if inside and depth <= level:
                break
            if not inside and title.lower() == heading.lower():
                inside, level = True, depth
                continue
        if inside:
            body.append(line)
    return "\n".join(body)


def _cells(row: str) -> list[str]:
    return [cell.strip() for cell in row.strip().strip("|").split("|")]


def parse_table(block: str) -> list[dict[str, str]]:
    """Parse the first pipe table in ``block`` into row dicts keyed by the header cells."""
    rows: list[str] = []
    for raw in block.splitlines():
        line = raw.strip()
        if line.startswith("|"):
            rows.append(line)
        elif rows:
            break
    if len(rows) < 2:
        return []
    header = _cells(rows[0])
    parsed: list[dict[str, str]] = []
    for row in rows[1:]:
        cells = _cells(row)
        if all(_SEPARATOR.fullmatch(cell) for cell in cells if cell):
            continue
        parsed.append(dict(zip(header, cells, strict=False)))
    return parsed


def backticked(cell: str) -> list[str]:
    """Return every `backticked` token in ``cell`` in order."""
    return _BACKTICK.findall(cell)
