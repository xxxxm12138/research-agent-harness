from __future__ import annotations

from dataclasses import replace

import pytest

from ir_harness.rubric import Rubric, Scorecard, load_rubric, score


@pytest.fixture()
def rubric(root) -> Rubric:
    return load_rubric(root / "agent" / "evals" / "rubrics" / "mapping.md")


@pytest.fixture()
def route(cfg):
    return cfg.get("mapping")


def test_load_rubric(rubric):
    assert rubric.name == "Rubric: Mapping"
    assert len(rubric.dimensions) == 7
    assert (rubric.pass_at, rubric.borderline_at, rubric.max_score) == (12, 9, 14)


def test_load_rubric_rejects_files_without_a_table(tmp_path):
    path = tmp_path / "empty.md"
    path.write_text("# Rubric\n\nno table\n", encoding="utf-8")
    with pytest.raises(ValueError):
        load_rubric(path)


def test_good_run_passes_on_rule_dimensions_alone(good_run, rubric, route):
    card = score(good_run, rubric, route=route)
    assert card.total == 12
    assert card.pending == ["Judgment quality"]
    assert card.verdict == "pass"
    assert "Total 12/14 (+ up to 2 pending) -> pass" in card.to_markdown()


def test_bad_run_fails(bad_run, rubric, route):
    card = score(bad_run, rubric, route=route)
    assert {row.name: row.score for row in card.rows} == {
        "Route selection": 1,
        "Task Packet": 0,
        "Coordinate system": 0,
        "Evidence binding": 1,
        "Judgment quality": None,
        "Output shape": 1,
        "Self-improvement": 0,
    }
    assert card.verdict == "fail"


def test_judge_scores_are_clamped(good_run, rubric, route):
    card = score(good_run, rubric, route=route, judge=lambda dim, run: 5)
    judged = next(row for row in card.rows if row.method == "judge")
    assert judged.score == 2
    assert card.total == 14


def test_provisional_until_judge_decides(good_run, rubric, route):
    run = replace(good_run, plain_language_report=False, self_review={})
    card = score(run, rubric, route=route)
    assert card.total == 9
    assert card.verdict == "provisional"
    judged = score(run, rubric, route=route, judge=lambda dim, r: 0)
    assert judged.verdict == "borderline"


def test_verdict_bands(rubric):
    card = Scorecard(rubric)
    assert card.verdict == "fail"


def test_source_aware_evidence_binding(good_run, bad_run, rubric, route, sources):
    origins = {s.id: s.origin for s in sources}
    good = score(good_run, rubric, route=route, source_origins=origins)
    assert next(r for r in good.rows if r.name == "Evidence binding").score == 2
    bad = score(bad_run, rubric, route=route, source_origins=origins)
    row = next(r for r in bad.rows if r.name == "Evidence binding")
    assert row.note == "2/4 claims sourced and correctly labelled"
    plain = score(bad_run, rubric, route=route)
    assert next(r for r in plain.rows if r.name == "Evidence binding").note.startswith("3/4")
