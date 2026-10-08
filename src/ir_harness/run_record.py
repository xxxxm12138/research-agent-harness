"""The structured run record every agent run must emit (see agent/run_record_contract.md).

Gates and rubric scoring read this record, not the prose, so checking a run does
not depend on the model's self-report or on a human re-reading the report.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

from .provenance import Claim, tag_claim

TASK_PACKET_FIELDS = (
    "background",
    "core_question",
    "reader_decision",
    "deliverables",
    "required_methods",
    "evidence_standard",
    "output_path",
    "flip_conditions",
    "confirmation",
)
REQUIRED_TASK_PACKET_FIELDS = (
    "core_question",
    "reader_decision",
    "deliverables",
    "evidence_standard",
    "flip_conditions",
)


def _text(value: Any) -> str:
    if isinstance(value, (list, tuple)):
        return "; ".join(str(item) for item in value if str(item).strip())
    return "" if value is None else str(value)


@dataclass(frozen=True)
class PoolEntry:
    name: str
    category: str = ""
    inclusion_reason: str = ""
    source_status: str = ""


@dataclass(frozen=True)
class PoolExclusion:
    name: str
    reason: str = ""


@dataclass(frozen=True)
class Category:
    name: str
    definition: str = ""


@dataclass(frozen=True)
class Chart:
    title: str
    claim: str = ""
    metric_definition: str = ""
    sample_base: str = ""


@dataclass
class RunRecord:
    task: str
    asof: date
    route: str
    intent: str = ""
    intent_excludes: list[str] = field(default_factory=list)
    loaded_files: list[str] = field(default_factory=list)
    task_packet: dict[str, str] = field(default_factory=dict)
    primary_axis: str = ""
    categories: list[Category] = field(default_factory=list)
    pool: list[PoolEntry] = field(default_factory=list)
    pool_locked: bool = False
    excluded_from_pool: list[PoolExclusion] = field(default_factory=list)
    profiles: list[str] = field(default_factory=list)
    sections: list[str] = field(default_factory=list)
    claims: list[Claim] = field(default_factory=list)
    charts: list[Chart] = field(default_factory=list)
    summary: dict[str, Any] = field(default_factory=dict)
    plain_language_report: bool = False
    final_recommendation: bool = False
    recommendation_requested: bool = False
    self_review: dict[str, list[str]] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> RunRecord:
        taxonomy = data.get("taxonomy", {})
        claims = [
            tag_claim(
                item["text"],
                item.get("origin", ""),
                source_id=item.get("source_id"),
                source_ids=item.get("source_ids", ()),
                asserted=item.get("status"),
                kind=item.get("kind"),
            )
            for item in data.get("claims", [])
        ]
        return cls(
            task=data.get("task", ""),
            asof=date.fromisoformat(data["asof"]),
            route=data.get("route", ""),
            intent=data.get("intent", ""),
            intent_excludes=list(data.get("intent_excludes", [])),
            loaded_files=list(data.get("loaded_files", [])),
            task_packet={k: _text(v) for k, v in data.get("task_packet", {}).items()},
            primary_axis=taxonomy.get("primary_axis", ""),
            categories=[Category(**c) for c in taxonomy.get("categories", [])],
            pool=[PoolEntry(**p) for p in data.get("pool", [])],
            pool_locked=bool(data.get("pool_locked", False)),
            excluded_from_pool=[PoolExclusion(**e) for e in data.get("excluded_from_pool", [])],
            profiles=list(data.get("profiles", [])),
            sections=list(data.get("sections", [])),
            claims=claims,
            charts=[Chart(**c) for c in data.get("charts", [])],
            summary=dict(data.get("summary", {})),
            plain_language_report=bool(data.get("plain_language_report", False)),
            final_recommendation=bool(data.get("final_recommendation", False)),
            recommendation_requested=bool(data.get("recommendation_requested", False)),
            self_review={k: list(v) for k, v in data.get("self_review", {}).items()},
        )

    @classmethod
    def load(cls, path: Path | str) -> RunRecord:
        return cls.from_dict(json.loads(Path(path).read_text(encoding="utf-8")))
