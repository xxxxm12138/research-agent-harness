"""Tests for the landscape-visualization scripts (skipped without the ``viz`` extra)."""

from __future__ import annotations

import sys

import pytest

pd = pytest.importorskip("pandas")


@pytest.fixture(scope="module")
def scripts(root):
    path = str(root / "skills" / "landscape-visualization" / "scripts")
    sys.path.insert(0, path)
    try:
        import render_market_landscape_html as html_renderer

        import _landscape_config as config

        yield config, html_renderer
    finally:
        sys.path.remove(path)


def test_config_defaults_and_helpers(scripts, example_dir):
    config, _ = scripts
    cfg = config.load_config(None)
    assert config.investor_items("A; 待 DD, B、C", cfg) == ["A", "B", "C"]
    assert config.type_items("财务VC;国资", cfg) == ["财务 VC", "政府基金"]
    assert config.category_x(["a", "b"], cfg) == {"a": 0.25, "b": 0.75}
    example = config.load_config(example_dir / "landscape.config.json")
    assert example.x_by_category["记录与记忆"] == 0.83
    assert example.y_ticks[0] == (0.25, "被动采集")


def test_heatmap_selection_keeps_focus_and_drops_excluded(scripts):
    config, _ = scripts
    cfg = config.LandscapeConfig(heatmap_focus_investors=["Z"], heatmap_exclude_investors={"Angel"})
    lists = [["A", "B"], ["A", "Angel"], ["Z"]] + [[f"X{i}"] for i in range(12)]
    selected = config.heatmap_investors(lists, cfg)
    assert selected[0] == "A"
    assert "Z" in selected
    assert "Angel" not in selected


def test_payload_from_example(scripts, example_dir):
    config, html_renderer = scripts
    cfg = config.load_config(example_dir / "landscape.config.json")
    payload = html_renderer.build_payload(pd.read_csv(example_dir / "landscape.csv"), cfg)
    records = {r["project"]: r for r in payload["records"]}
    assert len(records) == 6
    assert records["星芽"]["investor_list"] == ["示例美元基金 α", "示例产业资本 β"]
    assert records["回声"]["investor_list"] == []
    assert records["栖语"]["amount_usd_m"] is None
    assert sum(r["amount_usd_m"] or 0 for r in records.values()) == pytest.approx(8.17)


def test_html_escapes_title_and_embedded_data(scripts):
    _, html_renderer = scripts
    payload = {"records": [{"project": "</script><b>x"}]}
    page = html_renderer.render_html("<b>t</b>", payload, template="__TITLE__|__DATA__")
    title, data = page.split("|", 1)
    assert title == "&lt;b&gt;t&lt;/b&gt;"
    assert "</script>" not in data
    assert "<\\/script>" in data


@pytest.mark.filterwarnings("ignore::UserWarning")
def test_png_renderer_runs_on_example(root, example_dir, tmp_path):
    pytest.importorskip("matplotlib")
    sys.path.insert(0, str(root / "skills" / "landscape-visualization" / "scripts"))
    try:
        import render_market_landscape as png_renderer
    finally:
        sys.path.pop(0)
    out = tmp_path / "landscape.svg"
    png_renderer.main(
        [
            "--input",
            str(example_dir / "landscape.csv"),
            "--config",
            str(example_dir / "landscape.config.json"),
            "--output",
            str(out),
            "--title",
            "示例",
        ]
    )
    assert out.stat().st_size > 10_000
