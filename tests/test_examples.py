"""The fictional examples are data, so they are tested like data."""

from __future__ import annotations

import csv
import json

from ir_harness.mdtable import parse_table, section


def _num(cell: str) -> float | None:
    cell = cell.strip().replace(",", "").replace("%", "")
    return None if cell in ("", "—", "-") else float(cell)


def test_worked_example_parameters(root):
    text = (root / "skills/deal-modeling/references/worked-example.md").read_text("utf-8")
    p = {row["项目"]: _num(row["值"]) for row in parse_table(section(text, "关键参数"))}
    pre, invest = p["投前估值（$）"], p["本轮投资额（$）"]
    fx, registered = p["汇率（示例）"], p["投前注册资本（¥）"]
    pps = pre / registered
    new = round(invest / pps)
    assert p["投后估值（$）"] == pre + invest
    assert p["每股价格（$ / ¥1 注册资本）"] == round(pps, 2)
    assert p["新增注册资本（¥）"] == new
    assert p["资本公积（¥）"] == round(invest * fx - new)


def test_worked_example_cap_table(root):
    text = (root / "skills/deal-modeling/references/worked-example.md").read_text("utf-8")
    rows = parse_table(section(text, "Cap Table"))
    holders, total = rows[:-1], rows[-1]
    post_total = sum(_num(r["投后注册资本（¥）"]) for r in holders)
    pre_total = sum(_num(r["投前注册资本（¥）"]) or 0 for r in holders)
    assert _num(total["投后注册资本（¥）"]) == post_total
    assert _num(total["投前注册资本（¥）"]) == pre_total
    for r in holders:
        before = _num(r["投前注册资本（¥）"]) or 0
        added = _num(r["新增注册资本（¥）"]) or 0
        assert _num(r["投后注册资本（¥）"]) == before + added
        assert _num(r["投后%"]) == round(100 * (before + added) / post_total, 2)
        if before:
            assert _num(r["投前%"]) == round(100 * before / pre_total, 2)
    assert round(sum(_num(r["投后%"]) for r in holders), 2) == 100.0


def test_report_matches_run_record(example_dir):
    run = json.loads((example_dir / "run.json").read_text("utf-8"))
    report = (example_dir / "report.md").read_text("utf-8")
    for entry in run["pool"]:
        assert f"| {entry['category']} | {entry['name']} |" in report
    assert f"项目池 {run['summary']['n_projects']} 个" in report
    for category, count in run["summary"]["by_category"].items():
        assert f"{category} {count}" in report
    for title in run["sections"]:
        assert f"## {title}" in report or f". {title}" in report


def test_report_lists_every_source_and_marks_the_future_one(example_dir):
    sources = json.loads((example_dir / "sources.json").read_text("utf-8"))["sources"]
    report = (example_dir / "report.md").read_text("utf-8")
    rows = {row["编号"]: row for row in parse_table(section(report, "6. 信息来源与核验状态"))}
    assert set(rows) == {s["id"] for s in sources}
    assert "否" in rows["S-09"]["是否使用"]
    assert "否" in rows["S-13"]["是否使用"]


def test_every_financed_project_is_pooled_or_excluded(example_dir):
    run = json.loads((example_dir / "run.json").read_text("utf-8"))
    sources = json.loads((example_dir / "sources.json").read_text("utf-8"))["sources"]
    covered = {e["name"] for e in run["pool"]} | {e["name"] for e in run["excluded_from_pool"]}
    financed = {
        entity
        for s in sources
        if s["event"] == "financing" and (s["published"] or "") <= run["asof"]
        for entity in s["entities"]
    }
    assert financed <= covered


def test_landscape_table_matches_pool(example_dir):
    run = json.loads((example_dir / "run.json").read_text("utf-8"))
    with (example_dir / "landscape.csv").open(encoding="utf-8") as fh:
        table = {row["project"]: row for row in csv.DictReader(fh)}
    assert {e["name"]: e["category"] for e in run["pool"]} == {
        name: row["category"] for name, row in table.items()
    }
    disclosed = [row for row in table.values() if row["amount_usd_m"]]
    assert {row["source_status"] for row in disclosed} <= {"公开报道", "核实"}
