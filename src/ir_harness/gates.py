"""Process gates: the playbook's stop conditions and self-checks, enforced in code.

Each gate maps to the checkpoint the agent must return to when it fails, so a
failed check produces a concrete next step instead of a vague "revise".
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field

from .checkpoints import CHECKPOINTS
from .provenance import over_label
from .run_record import REQUIRED_TASK_PACKET_FIELDS, RunRecord
from .workspace import Workspace

__all__ = ["CHECKPOINTS", "DEFAULT_GATES", "Gate", "GateResult", "return_checkpoint", "run_gates"]

MAPPING_ROUTES = frozenset({"mapping", "founder"})
FINANCING_EVENT = "financing"


def _norm(text: str) -> str:
    return text.replace(" ", "").lower()


@dataclass
class GateResult:
    gate: str
    checkpoint: int
    errors: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return not self.errors


class Gate:
    name = "gate"
    checkpoint = 5
    routes: frozenset[str] | None = None  # None: applies to every route

    def applies(self, run: RunRecord) -> bool:
        return self.routes is None or run.route in self.routes

    def check(self, run: RunRecord, ws: Workspace | None = None) -> GateResult:
        result = GateResult(self.name, self.checkpoint)
        if self.applies(run):
            result.errors.extend(self.errors(run, ws))
        return result

    def errors(self, run: RunRecord, ws: Workspace | None) -> Iterable[str]:
        raise NotImplementedError


class TaskPacketGate(Gate):
    """Playbook rule 2: no long-form output before a Task Packet."""

    name = "task_packet"
    checkpoint = 1

    def errors(self, run, ws):
        if not run.task_packet:
            yield "no Task Packet before long-form output"
            return
        for key in REQUIRED_TASK_PACKET_FIELDS:
            if not run.task_packet.get(key, "").strip():
                yield f"Task Packet field missing: {key}"


class IntentGate(Gate):
    """Intent Gate: right route and intent, adjacent intents explicitly ruled out, and no
    unrequested verdict in mapping work."""

    name = "intent"
    checkpoint = 1

    def errors(self, run, ws):
        if ws is not None:
            if run.route != ws.route.id:
                yield f"task routes to '{ws.route.id}' but the run says '{run.route}'"
            if run.intent and run.intent != ws.route.intent:
                yield f"intent '{run.intent}' differs from routed intent '{ws.route.intent}'"
            ruled_out = {_norm(item) for item in run.intent_excludes}
            missing = [name for name in ws.route.not_intents if _norm(name) not in ruled_out]
            if missing:
                yield "Intent Gate does not rule out adjacent intent(s): " + ", ".join(missing)
        if (
            run.route in MAPPING_ROUTES
            and run.final_recommendation
            and not run.recommendation_requested
        ):
            yield (
                "mapping deliverable contains a final investment / FA recommendation "
                "nobody asked for"
            )


class PoolGate(Gate):
    """Lock the project / sample pool before writing profiles, and check its coverage.

    Coverage guards against missed early-stage projects (漏检): with a workspace, every
    project that has a financing event in the as-of sources must be in the pool or be
    excluded with a reason, whether the event came from a news story or a screenshot.
    """

    name = "sample_pool"
    checkpoint = 2
    routes = MAPPING_ROUTES

    def errors(self, run, ws):
        if run.profiles and not run.pool_locked:
            yield "profiles drafted before the pool was locked"
        pool = {entry.name for entry in run.pool}
        for name in run.profiles:
            if name not in pool:
                yield f"profile '{name}' is not in the pool"
        for entry in run.pool:
            if not entry.inclusion_reason.strip():
                yield f"pool entry '{entry.name}' has no inclusion reason"
        for excluded in run.excluded_from_pool:
            if not excluded.reason.strip():
                yield f"pool exclusion '{excluded.name}' has no reason"
        if ws is None:
            return
        # Coverage: every project with a financing event in the as-of source set is either
        # in the pool or explicitly excluded with a reason (guards against 漏检).
        covered = pool | {x.name for x in run.excluded_from_pool if x.reason.strip()}
        missing: dict[str, list[str]] = {}
        for source in ws.sources:
            if source.event == FINANCING_EVENT:
                for entity in source.entities:
                    if entity not in covered:
                        missing.setdefault(entity, []).append(source.id)
        for entity, ids in missing.items():
            cited = ", ".join(ids)
            yield f"financed project '{entity}' ({cited}) is neither in the pool nor excluded"


class TaxonomyGate(Gate):
    """One primary classification axis; every label defined in reader-facing language."""

    name = "taxonomy"
    checkpoint = 3
    routes = MAPPING_ROUTES

    def errors(self, run, ws):
        if not run.primary_axis.strip():
            yield "no single primary classification axis"
        for category in run.categories:
            if not category.definition.strip():
                yield f"category '{category.name}' has no definition"
        names = {category.name for category in run.categories}
        for entry in run.pool:
            if entry.category and entry.category not in names:
                yield f"'{entry.name}' uses undefined category '{entry.category}'"


class EvidenceGate(Gate):
    """Every key claim carries a source and a label its evidence can justify.

    Without a workspace the declared origin caps the label. With one, the label is also
    capped by the sources the claim actually cites (cross-verification rule in
    ``provenance.ceiling_for_sources``), so declaring ``origin: verified`` on a BP figure
    does not make it ``核实``.
    """

    name = "evidence"
    checkpoint = 5

    def errors(self, run, ws):
        origins = None
        if ws is not None:
            origins = {s.id: s.origin for s in [*ws.sources, *ws.excluded_future]}
        for claim in run.claims:
            excerpt = claim.text[:40]
            if claim.was_downgraded:
                yield (
                    f"labelled '{claim.downgraded_from}' but origin '{claim.origin}' supports "
                    f"at most '{claim.status}': {excerpt}"
                )
            if claim.kind == "fact" and not claim.source_ids:
                yield f"fact without a source: {excerpt}"
            if origins is None:
                continue
            for source_id in claim.source_ids:
                if source_id not in origins:
                    yield f"cites unknown source '{source_id}': {excerpt}"
            cited = [origins[i] for i in claim.source_ids if i in origins]
            ceiling = over_label(claim, cited)
            if ceiling is not None:
                yield (
                    f"labelled '{claim.status}' but cited sources ({', '.join(claim.source_ids)}) "
                    f"support at most '{ceiling}': {excerpt}"
                )


class TemporalGate(Gate):
    """No claim may rest on a source published after the decision date."""

    name = "point_in_time"
    checkpoint = 5

    def errors(self, run, ws):
        if ws is None:
            return
        future = {source.id: source for source in ws.excluded_future}
        for claim in run.claims:
            for source_id in claim.source_ids:
                source = future.get(source_id)
                if source is not None:
                    yield (
                        f"'{claim.text[:40]}' uses {source.id}, published {source.published}, "
                        f"after asof {ws.asof} (look-ahead leakage)"
                    )


class VisualizationGate(Gate):
    """Insight before visualization: each chart states its claim, metric and sample base."""

    name = "visualization"
    checkpoint = 5

    def errors(self, run, ws):
        required = (
            ("claim", "analytical claim"),
            ("metric_definition", "metric definition"),
            ("sample_base", "sample base"),
        )
        for chart in run.charts:
            for attr, label in required:
                if not getattr(chart, attr).strip():
                    yield f"chart '{chart.title}' lacks {label}"


class SummaryConsistencyGate(Gate):
    """Summary counts must be computed from the final bottom table."""

    name = "summary_consistency"
    checkpoint = 5
    routes = MAPPING_ROUTES

    def errors(self, run, ws):
        total = run.summary.get("n_projects")
        if total is not None and int(total) != len(run.pool):
            yield f"summary says {total} projects, the table has {len(run.pool)}"
        for category, count in run.summary.get("by_category", {}).items():
            actual = sum(1 for entry in run.pool if entry.category == category)
            if int(count) != actual:
                yield f"summary count for '{category}' is {count}, the table has {actual}"


DEFAULT_GATES: tuple[Gate, ...] = (
    TaskPacketGate(),
    IntentGate(),
    PoolGate(),
    TaxonomyGate(),
    EvidenceGate(),
    TemporalGate(),
    VisualizationGate(),
    SummaryConsistencyGate(),
)


def run_gates(
    run: RunRecord,
    ws: Workspace | None = None,
    gates: Sequence[Gate] = DEFAULT_GATES,
) -> list[GateResult]:
    return [gate.check(run, ws) for gate in gates]


def return_checkpoint(results: Sequence[GateResult]) -> int | None:
    """The earliest checkpoint any failed gate points back to (None when all pass)."""
    failed = [result.checkpoint for result in results if not result.passed]
    return min(failed) if failed else None
