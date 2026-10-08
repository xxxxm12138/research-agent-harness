from __future__ import annotations

from dataclasses import replace

from ir_harness.gates import (
    DEFAULT_GATES,
    EvidenceGate,
    IntentGate,
    PoolGate,
    SummaryConsistencyGate,
    TaskPacketGate,
    TemporalGate,
    return_checkpoint,
    run_gates,
)
from ir_harness.provenance import tag_claim
from ir_harness.run_record import PoolEntry, PoolExclusion


def _by_name(results):
    return {r.gate: r for r in results}


def test_good_run_passes_every_gate(good_run, ws):
    results = run_gates(good_run, ws)
    assert [r.gate for r in results if not r.passed] == []
    assert return_checkpoint(results) is None


def test_bad_run_fails_every_gate_and_returns_to_checkpoint_1(bad_run, ws):
    results = run_gates(bad_run, ws)
    assert all(not r.passed for r in results)
    assert len(results) == len(DEFAULT_GATES) == 8
    assert return_checkpoint(results) == 1


def test_bad_run_messages(bad_run, ws):
    errors = {name: " | ".join(r.errors) for name, r in _by_name(run_gates(bad_run, ws)).items()}
    assert "no Task Packet" in errors["task_packet"]
    assert "intent 'memo'" in errors["intent"]
    assert "does not rule out adjacent intent(s): memo, 投资建议, FA 匹配" in errors["intent"]
    assert (
        "financed project '栖语' (S-05) is neither in the pool nor excluded"
        in errors["sample_pool"]
    )
    assert "cited sources (S-02) support at most '待DD'" in errors["evidence"]
    assert "nobody asked for" in errors["intent"]
    assert "before the pool was locked" in errors["sample_pool"]
    assert "'栖语' is not in the pool" in errors["sample_pool"]
    assert "undefined category '健康监测'" in errors["taxonomy"]
    assert "origin 'media' supports at most '媒体口径'" in errors["evidence"]
    assert "unknown source 'S-99'" in errors["evidence"]
    assert "look-ahead leakage" in errors["point_in_time"]
    assert "lacks metric definition" in errors["visualization"]
    assert "the table has 4" in errors["summary_consistency"]


def test_task_packet_gate_names_missing_fields(good_run):
    run = replace(good_run, task_packet={"core_question": "q"})
    errors = TaskPacketGate().check(run).errors
    assert "Task Packet field missing: flip_conditions" in errors
    assert all("core_question" not in e for e in errors)


def test_requested_recommendation_is_allowed(good_run):
    run = replace(good_run, final_recommendation=True, recommendation_requested=True)
    assert IntentGate().check(run).passed


def test_mapping_only_gates_skip_other_routes(bad_run):
    run = replace(bad_run, route="call_report")
    assert PoolGate().check(run).passed
    assert SummaryConsistencyGate().check(run).passed


def test_pool_gate_requires_inclusion_reason(good_run):
    pool = [*good_run.pool, PoolEntry(name="新项目", category="情感陪伴")]
    errors = PoolGate().check(replace(good_run, pool=pool)).errors
    assert errors == ["pool entry '新项目' has no inclusion reason"]


def test_evidence_gate_without_workspace_skips_source_lookup(good_run):
    claim = tag_claim("x", "news", source_id="S-404")
    run = replace(good_run, claims=[claim])
    assert EvidenceGate().check(run).passed
    assert TemporalGate().check(run).passed


def test_temporal_gate_flags_future_source(good_run, ws):
    claim = tag_claim("拾光完成 A 轮", "news", source_id="S-09")
    errors = TemporalGate().check(replace(good_run, claims=[claim]), ws).errors
    assert len(errors) == 1
    assert "after asof 2026-09-30" in errors[0]


def test_intent_gate_needs_adjacent_intents_ruled_out(good_run, ws):
    run = replace(good_run, intent_excludes=["memo"])
    errors = IntentGate().check(run, ws).errors
    assert errors == ["Intent Gate does not rule out adjacent intent(s): 投资建议, FA 匹配"]
    spaced = replace(good_run, intent_excludes=["Memo", "投资 建议", "FA匹配"])
    assert IntentGate().check(spaced, ws).passed


def test_pool_coverage_accepts_explicit_exclusions_only_with_reason(good_run, ws):
    no_reason = replace(good_run, excluded_from_pool=[PoolExclusion("童伴", "")])
    errors = PoolGate().check(no_reason, ws).errors
    assert "pool exclusion '童伴' has no reason" in errors
    assert "financed project '童伴' (S-13) is neither in the pool nor excluded" in errors


def test_cross_verified_claim_passes_and_single_source_does_not(good_run, ws):
    two = tag_claim("星芽完成 Pre-A", "verified", asserted="核实", source_ids=["S-01", "S-12"])
    one = tag_claim("星芽完成 Pre-A", "verified", asserted="核实", source_ids=["S-01"])
    assert EvidenceGate().check(replace(good_run, claims=[two]), ws).passed
    errors = EvidenceGate().check(replace(good_run, claims=[one]), ws).errors
    assert errors == [
        "labelled '核实' but cited sources (S-01) support at most '公开报道': 星芽完成 Pre-A"
    ]
