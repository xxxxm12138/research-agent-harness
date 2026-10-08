from __future__ import annotations

from ir_harness.mdtable import backticked, parse_table, section

DOC = """# Title

## Alpha

intro

| A | B |
|:--|--:|
| 1 | 2 |
| 3 |

after

### Alpha child

child text

## Beta

| X |
|---|
| y |
"""


def test_section_stops_at_same_level_heading():
    body = section(DOC, "Alpha")
    assert "intro" in body
    assert "child text" in body
    assert "Beta" not in body


def test_section_is_case_insensitive_and_missing_is_empty():
    assert "| X |" in section(DOC, "beta")
    assert section(DOC, "Gamma") == ""


def test_parse_table_skips_separator_and_pads_short_rows():
    rows = parse_table(section(DOC, "Alpha"))
    assert rows == [{"A": "1", "B": "2"}, {"A": "3"}]


def test_parse_table_needs_header_and_row():
    assert parse_table("| only header |") == []
    assert parse_table("no table here") == []


def test_backticked():
    assert backticked("load `a.md` and `b/c.md`, not d") == ["a.md", "b/c.md"]
    assert backticked("—") == []
