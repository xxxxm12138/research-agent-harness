from __future__ import annotations

import pytest

from ir_harness.router import (
    RouterConfig,
    RoutingError,
    load_router,
    match_route,
    missing_references,
    referenced_files,
)

ROUTER_MD = """# Router

## Always Load

| File | Why |
|---|---|
| `agent/a.md` `agent/b.md` | rules |

## Routes

| Route | Intent | Task signals | Required skills | Optional skills | Golden | Rubric | Output |
|---|---|---|---|---|---|---|---|
| `alpha` | A intent | apple, 苹果 | `s/a.md` | — | — | — | a.md |
| `beta` | B intent | apple；banana | `s/b.md` | `s/c.md` | `g.md` | `r.md` | b.md |

## Route Rules

1. not a table
"""


@pytest.fixture()
def tiny(tmp_path) -> RouterConfig:
    (tmp_path / "agent").mkdir()
    (tmp_path / "agent" / "router.md").write_text(ROUTER_MD, encoding="utf-8")
    return load_router(tmp_path)


def test_parses_always_load_and_routes(tiny):
    assert tiny.always_load == ("agent/a.md", "agent/b.md")
    assert [r.id for r in tiny.routes] == ["alpha", "beta"]
    beta = tiny.get("beta")
    assert beta.signals == ("apple", "banana")
    assert beta.optional_skills == ("s/c.md",)
    assert beta.golden == ("g.md",)
    assert beta.rubric == "r.md"
    assert tiny.get("alpha").rubric is None


def test_more_signals_win_and_table_order_breaks_ties(tiny):
    assert match_route("APPLE and banana", tiny).id == "beta"
    assert match_route("an apple", tiny).id == "alpha"
    assert match_route("我想吃苹果", tiny).id == "alpha"


def test_no_signal_raises(tiny):
    with pytest.raises(RoutingError):
        match_route("something unrelated", tiny)


def test_unknown_route_id(tiny):
    with pytest.raises(KeyError):
        tiny.get("gamma")


def test_missing_references_lists_absent_paths(tiny, tmp_path):
    assert "s/a.md" in referenced_files(tiny)
    assert "agent/a.md" in missing_references(tmp_path)


def test_repo_router_is_consistent(cfg, root):
    assert missing_references(root) == []
    assert {r.id for r in cfg.routes} == {
        "founder",
        "founder_dd",
        "mapping",
        "track_analysis",
        "screening",
        "call_report",
        "deal_modeling",
        "narrative",
    }


@pytest.mark.parametrize(
    ("task", "expected"),
    [
        ("帮我做 AI 陪伴硬件赛道的 mapping，看哪些机构投了", "mapping"),
        ("下周见团队，先做个 Pitch 前研究", "mapping"),
        ("过去两年 AI 创业者画像有什么变化", "founder"),
        ("背调一下这个创始人，再做个 mapping", "founder_dd"),
        ("帮我写一份 AI 硬件的投资备忘录", "track_analysis"),
        ("这个项目值不值得看", "screening"),
        ("把这份会议纪要整理成 Call Report", "call_report"),
        ("帮我算一下 cap table 稀释", "deal_modeling"),
        ("帮我梳理一下 BP 卖点和融资故事", "narrative"),
    ],
)
def test_repo_routes(cfg, task, expected):
    assert match_route(task, cfg).id == expected
