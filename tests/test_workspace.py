from __future__ import annotations

import json
from datetime import date

from ir_harness.workspace import Source, assemble, estimate_tokens, load_sources, materialize


def test_layers_load_in_order(ws, cfg):
    layers = [f.layer for f in ws.files]
    assert layers == sorted(layers, key=["rules", "skill", "golden"].index)
    paths = [f.path for f in ws.files]
    assert paths[: len(cfg.always_load)] == list(cfg.always_load)
    assert "skills/research-mapping/SKILL.md" in paths
    assert paths[-1] == "agent/golden/mapping.md"
    assert ws.missing == []


def test_optional_skills_only_on_request(task, asof, root, cfg):
    plain = assemble(task, asof, root=root, config=cfg)
    full = assemble(task, asof, root=root, config=cfg, include_optional=True)
    optional = "skills/landscape-visualization/SKILL.md"
    assert optional not in [f.path for f in plain.files]
    assert optional in [f.path for f in full.files]


def test_only_route_relevant_corrections_are_loaded(ws, root, cfg, asof):
    assert "2026-08-31 - CR 正文不要写「会议称」" in ws.corrections_skipped
    assert any("one primary axis" in title for title in ws.corrections_selected)
    assert "会议称" not in ws.corrections_text
    cr = assemble("把会议纪要整理成 call report", asof, root=root, config=cfg)
    assert any("会议称" in title for title in cr.corrections_selected)
    assert not any("one primary axis" in title for title in cr.corrections_selected)
    assert any("Sources and DD status" in title for title in cr.corrections_selected)  # tagged all
    full = (root / "agent/memory/corrections.md").read_text(encoding="utf-8")
    corrections = next(f for f in cr.files if f.path == "agent/memory/corrections.md")
    assert corrections.tokens < estimate_tokens(full)


def test_point_in_time_freeze(ws):
    assert [s.id for s in ws.excluded_future] == ["S-09"]
    assert "S-09" not in ws.source_ids()
    assert [s.id for s in ws.undated] == ["S-11"]
    assert "S-11" in ws.source_ids()


def test_source_published_on_asof_is_admitted(task, root, cfg):
    same_day = Source("S-X", "t", "news", date(2026, 9, 30))
    ws = assemble(task, date(2026, 9, 30), root=root, config=cfg, sources=[same_day])
    assert ws.source_ids() == {"S-X"}


def test_missing_files_are_recorded_not_hidden(tmp_path, cfg, task, asof):
    ws = assemble(task, asof, root=tmp_path, config=cfg)
    assert ws.files == []
    assert "agent/playbook.md" in ws.missing


def test_budget_and_manifest(task, asof, root, cfg):
    ws = assemble(task, asof, root=root, config=cfg, budget_tokens=100)
    assert ws.over_budget
    manifest = ws.manifest()
    assert manifest["route"] == "mapping"
    assert manifest["asof"] == "2026-09-30"
    assert manifest["context_tokens_est"] == ws.tokens > 100


def test_materialize_writes_the_workspace(ws, tmp_path):
    out = materialize(ws, tmp_path / "w")
    manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["sources_excluded_after_asof"] == ["S-09"]
    assert (out / "corrections.md").read_text(encoding="utf-8") == ws.corrections_text
    sources = json.loads((out / "sources.json").read_text(encoding="utf-8"))
    assert sources["asof"] == "2026-09-30"
    assert len(sources["sources"]) == len(ws.sources) == 12


def test_estimate_tokens_counts_cjk_per_character():
    assert estimate_tokens("投研") == 2
    assert estimate_tokens("abcd") == 1
    assert estimate_tokens("投研abcd") == 3


def test_load_sources_accepts_list_and_dict(tmp_path, example_dir):
    listed = tmp_path / "list.json"
    listed.write_text('[{"id": "A", "origin": "bp", "published": "2026-01-01"}]', "utf-8")
    source = load_sources(listed)[0]
    assert source.status.value == "待DD"
    assert source.entities == ()
    example = load_sources(example_dir / "sources.json")
    assert len(example) == 13
    assert example[0].entities == ("星芽",)
    assert example[0].event == "financing"
