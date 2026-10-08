from __future__ import annotations

import pytest

from ir_harness.provenance import (
    Status,
    ceiling_for_sources,
    origin_rule,
    over_label,
    parse_status,
    tag_claim,
)


@pytest.mark.parametrize(
    ("label", "expected"),
    [
        ("核实", Status.VERIFIED),
        ("待DD", Status.PENDING_DD),
        ("待 DD", Status.PENDING_DD),
        ("pending_dd", Status.PENDING_DD),
        ("媒体口径", Status.MEDIA),
        (Status.LEAD, Status.LEAD),
    ],
)
def test_parse_status(label, expected):
    assert parse_status(label) is expected


def test_parse_status_rejects_unknown_labels():
    with pytest.raises(ValueError):
        parse_status("大概是真的")


def test_default_status_comes_from_origin():
    assert tag_claim("x", "filing").status is Status.VERIFIED
    assert tag_claim("x", "screenshot").status is Status.LEAD
    assert str(tag_claim("x", "news").status) == "公开报道"


def test_bp_figure_cannot_be_labelled_verified():
    claim = tag_claim("月活 3 万台", "bp", asserted="核实", source_id="S-02")
    assert claim.status is Status.PENDING_DD
    assert claim.downgraded_from is Status.VERIFIED
    assert claim.was_downgraded


def test_weaker_label_is_allowed():
    claim = tag_claim("金额未披露", "official", asserted="未公开")
    assert claim.status is Status.UNDISCLOSED
    assert not claim.was_downgraded


def test_unknown_origin_is_treated_as_pending_dd():
    assert origin_rule("someone told me") == (Status.PENDING_DD, Status.PENDING_DD)
    assert tag_claim("x", "", asserted="公开报道").status is Status.PENDING_DD


def test_inference_kind():
    assert tag_claim("推断", "inference").kind == "inference"
    assert tag_claim("事实", "news").kind == "fact"
    assert tag_claim("未知", "news", kind="unknown").kind == "unknown"


def test_four_tiers():
    assert Status.VERIFIED.tier == "已核实"
    assert Status.MEDIA.tier == "公开报道"
    assert {Status.LEAD.tier, Status.PENDING_DD.tier, Status.UNDISCLOSED.tier} == {"待DD"}
    assert tag_claim("x", "bp").status.tier == tag_claim("x", "screenshot").status.tier == "待DD"


@pytest.mark.parametrize(
    ("origins", "ceiling"),
    [
        (["bp"], Status.PENDING_DD),
        (["news"], Status.PUBLIC),
        (["news", "news"], Status.PUBLIC),
        (["news", "official"], Status.VERIFIED),
        (["filing"], Status.VERIFIED),
        (["bp", "news"], Status.PUBLIC),
        (["verified"], Status.PENDING_DD),
        ([], Status.PENDING_DD),
    ],
)
def test_cross_verification_ceiling(origins, ceiling):
    assert ceiling_for_sources(origins) is ceiling


def test_declared_origin_cannot_launder_a_bp_figure():
    claim = tag_claim("月活 3 万台", "verified", asserted="核实", source_id="S-02")
    assert not claim.was_downgraded
    assert over_label(claim, ["bp"]) is Status.PENDING_DD
    assert over_label(claim, ["news", "official"]) is None
    assert over_label(claim, []) is None


def test_multiple_source_ids_are_merged_in_order():
    claim = tag_claim("x", "news", source_id="S-1", source_ids=["S-2", "S-1"])
    assert claim.source_ids == ("S-1", "S-2")
    assert claim.source_id == "S-1"
    assert tag_claim("x", "news").source_id is None
