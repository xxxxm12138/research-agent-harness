"""Rubric parsing and scoring.

Dimensions that can be checked from the run record are scored by rules; open
judgment dimensions go to a judge (an LLM-as-a-judge or a human) and are marked
pending otherwise. The verdict only becomes final when the pending dimensions
cannot change it.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from .mdtable import parse_table
from .provenance import over_label
from .router import Route
from .run_record import REQUIRED_TASK_PACKET_FIELDS, TASK_PACKET_FIELDS, RunRecord

Judge = Callable[[str, RunRecord], "int | None"]
RuleResult = "tuple[int, str] | None"

_PASS = re.compile(r"`(\d+)\+`\s*[:：]\s*pass", re.IGNORECASE)
_BORDERLINE = re.compile(r"`(\d+)\s*[-–]\s*\d+`\s*[:：]\s*borderline", re.IGNORECASE)

AXIS_WORDS = ("分类", "坐标", "边界", "axis", "axes")
PLAYER_WORDS = ("项目池", "总表", "画像", "玩家", "players", "profiles")


@dataclass(frozen=True)
class Dimension:
    name: str
    levels: tuple[str, str, str]


@dataclass(frozen=True)
class Rubric:
    name: str
    dimensions: tuple[Dimension, ...]
    pass_at: int
    borderline_at: int

    @property
    def max_score(self) -> int:
        return 2 * len(self.dimensions)


def load_rubric(path: Path | str) -> Rubric:
    path = Path(path)
    text = path.read_text(encoding="utf-8")
    title = next((ln[2:].strip() for ln in text.splitlines() if ln.startswith("# ")), path.stem)
    dimensions = tuple(
        Dimension(row["Dimension"].strip(), (row.get("0", ""), row.get("1", ""), row.get("2", "")))
        for row in parse_table(text)
        if row.get("Dimension", "").strip()
    )
    if not dimensions:
        raise ValueError(f"no dimension table in {path}")
    pass_match, border_match = _PASS.search(text), _BORDERLINE.search(text)
    pass_at = int(pass_match.group(1)) if pass_match else 2 * len(dimensions) - 2
    borderline_at = int(border_match.group(1)) if border_match else pass_at - 3
    return Rubric(title, dimensions, pass_at, borderline_at)


@dataclass(frozen=True)
class Context:
    run: RunRecord
    route: Route | None
    source_origins: dict[str, str] | None = None


def _route_selection(ctx: Context) -> tuple[int, str] | None:
    if ctx.route is None:
        return None
    loaded = set(ctx.run.loaded_files)
    required, golden = set(ctx.route.required_skills), set(ctx.route.golden)
    if required <= loaded and (not golden or golden & loaded):
        return 2, "all required skills and a golden sample loaded"
    if ctx.route.required_skills and ctx.route.required_skills[0] in loaded:
        return 1, "main skill loaded; support skill or golden sample missing"
    return 0, "required skills not loaded"


def _task_packet(ctx: Context) -> tuple[int, str]:
    packet = ctx.run.task_packet
    filled = [k for k in TASK_PACKET_FIELDS if packet.get(k, "").strip()]
    if all(packet.get(k, "").strip() for k in REQUIRED_TASK_PACKET_FIELDS) and len(filled) >= 7:
        return (
            2,
            f"{len(filled)}/{len(TASK_PACKET_FIELDS)} fields incl. decision and flip conditions",
        )
    if packet.get("core_question", "").strip():
        return 1, "core question present; decision / evidence incomplete"
    return 0, "missing or generic"


def _first_index(sections: list[str], words: tuple[str, ...]) -> int | None:
    for index, title in enumerate(sections):
        if any(word in title.lower() for word in words):
            return index
    return None


def _coordinate_system(ctx: Context) -> tuple[int, str]:
    run = ctx.run
    axis_at = _first_index(run.sections, AXIS_WORDS)
    players_at = _first_index(run.sections, PLAYER_WORDS)
    defined = bool(run.categories) and all(c.definition.strip() for c in run.categories)
    leads = axis_at is not None and (players_at is None or axis_at < players_at)
    if run.primary_axis.strip() and defined and leads:
        return 2, "boundary and primary axis defined before players"
    if axis_at is not None or run.primary_axis.strip():
        return 1, "axes present but not leading or not defined"
    return 0, "starts with a player list"


def _evidence_binding(ctx: Context) -> tuple[int, str]:
    claims = ctx.run.claims
    if not claims:
        return 0, "no claims recorded"
    origins = ctx.source_origins

    def ok(claim) -> bool:
        if claim.was_downgraded or (claim.kind == "fact" and not claim.source_ids):
            return False
        if origins is None:
            return True
        return over_label(claim, [origins[i] for i in claim.source_ids if i in origins]) is None

    good = sum(1 for claim in claims if ok(claim))
    note = f"{good}/{len(claims)} claims sourced and correctly labelled"
    ratio = good / len(claims)
    if ratio >= 0.9:
        return 2, note
    if ratio >= 0.5:
        return 1, note
    return 0, note


def _output_shape(ctx: Context) -> tuple[int, str]:
    if ctx.run.plain_language_report and ctx.run.sections:
        return 2, "formal deliverable plus plain-language report"
    if ctx.run.sections and ctx.run.summary:
        return 1, "formal output plus partial summary"
    return 0, "one report only"


def _self_improvement(ctx: Context) -> tuple[int, str]:
    review = ctx.run.self_review
    concrete = [
        item
        for key in ("missing_evidence", "skill_gaps", "memory_candidates")
        for item in review.get(key, [])
        if item.strip()
    ]
    if len(concrete) >= 2:
        return 2, f"{len(concrete)} concrete gaps / memory candidates"
    if concrete or review.get("notes"):
        return 1, "generic reflection"
    return 0, "no reflection"


RULE_SCORERS: dict[str, Callable[[Context], tuple[int, str] | None]] = {
    "route selection": _route_selection,
    "task packet": _task_packet,
    "coordinate system": _coordinate_system,
    "evidence binding": _evidence_binding,
    "output shape": _output_shape,
    "self-improvement": _self_improvement,
}


@dataclass(frozen=True)
class DimensionScore:
    name: str
    score: int | None
    method: str  # rule | judge | pending
    note: str = ""


@dataclass
class Scorecard:
    rubric: Rubric
    rows: list[DimensionScore] = field(default_factory=list)

    @property
    def total(self) -> int:
        return sum(row.score for row in self.rows if row.score is not None)

    @property
    def pending(self) -> list[str]:
        return [row.name for row in self.rows if row.score is None]

    @property
    def verdict(self) -> str:
        low, high = self.total, self.total + 2 * len(self.pending)
        if low >= self.rubric.pass_at:
            return "pass"
        if high < self.rubric.borderline_at:
            return "fail"
        if self.pending:
            return "provisional"
        return "borderline" if low >= self.rubric.borderline_at else "fail"

    def to_markdown(self) -> str:
        lines = [
            f"### {self.rubric.name}",
            "",
            "| Dimension | Score | Method | Note |",
            "|---|---|---|---|",
        ]
        for row in self.rows:
            value = "-" if row.score is None else str(row.score)
            lines.append(f"| {row.name} | {value} | {row.method} | {row.note} |")
        pending = f" (+ up to {2 * len(self.pending)} pending)" if self.pending else ""
        lines += [
            "",
            f"Total {self.total}/{self.rubric.max_score}{pending} -> {self.verdict} "
            f"(pass >= {self.rubric.pass_at}, borderline >= {self.rubric.borderline_at})",
        ]
        return "\n".join(lines)


def score(
    run: RunRecord,
    rubric: Rubric,
    *,
    route: Route | None = None,
    judge: Judge | None = None,
    source_origins: dict[str, str] | None = None,
) -> Scorecard:
    """Score a run; pass ``source_origins`` (id -> origin) to check labels against sources."""
    ctx = Context(run, route, source_origins)
    card = Scorecard(rubric)
    for dimension in rubric.dimensions:
        scorer = RULE_SCORERS.get(dimension.name.strip().lower())
        result = scorer(ctx) if scorer else None
        if result is not None:
            value, note = result
            card.rows.append(DimensionScore(dimension.name, value, "rule", note))
            continue
        judged = judge(dimension.name, run) if judge else None
        if judged is None:
            card.rows.append(
                DimensionScore(dimension.name, None, "pending", "needs LLM judge or human review")
            )
        else:
            card.rows.append(DimensionScore(dimension.name, max(0, min(2, judged)), "judge"))
    return card
