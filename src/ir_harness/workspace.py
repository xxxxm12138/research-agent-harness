"""Workspace assembly: route-scoped, layered loading plus point-in-time freezing.

A workspace is the information set available *at the decision date*:

- it loads only what the selected route needs (rules -> skills -> golden samples) and,
  from the corrections memory, only the entries tagged for that route;
- it records every required file that is missing instead of silently skipping it;
- it drops any source published after ``asof``, so neither the agent nor the
  evaluation can look ahead.

``materialize`` writes the workspace to its own folder, which is what the model sees.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

from .corrections import CORRECTIONS_FILE, parse_memory
from .paths import repo_root
from .provenance import Status, origin_rule
from .router import Route, RouterConfig, load_router, match_route

DEFAULT_BUDGET_TOKENS = 60_000


def estimate_tokens(text: str) -> int:
    """Rough estimate: one token per CJK character, one per four other characters."""
    cjk = sum(1 for ch in text if "㐀" <= ch <= "鿿" or "豈" <= ch <= "﫿")
    return cjk + (len(text) - cjk + 3) // 4


@dataclass(frozen=True)
class Source:
    id: str
    title: str
    origin: str
    published: date | None = None
    ref: str = ""
    entities: tuple[str, ...] = ()
    event: str = ""  # e.g. "financing"; used by the pool-coverage check

    @property
    def status(self) -> Status:
        return origin_rule(self.origin)[0]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Source:
        published = data.get("published")
        return cls(
            id=str(data["id"]),
            title=str(data.get("title", "")),
            origin=str(data.get("origin", "")),
            published=date.fromisoformat(published) if published else None,
            ref=str(data.get("ref", "")),
            entities=tuple(data.get("entities", ())),
            event=str(data.get("event", "")),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "origin": self.origin,
            "published": self.published.isoformat() if self.published else None,
            "ref": self.ref,
            "entities": list(self.entities),
            "event": self.event,
            "status": self.status.value,
            "tier": self.status.tier,
        }


def load_sources(path: Path | str) -> list[Source]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    items = data["sources"] if isinstance(data, dict) else data
    return [Source.from_dict(item) for item in items]


@dataclass(frozen=True)
class LoadedFile:
    path: str
    layer: str  # rules | skill | golden
    tokens: int


@dataclass
class Workspace:
    route: Route
    asof: date
    files: list[LoadedFile] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)
    sources: list[Source] = field(default_factory=list)
    excluded_future: list[Source] = field(default_factory=list)
    undated: list[Source] = field(default_factory=list)
    budget_tokens: int = DEFAULT_BUDGET_TOKENS
    corrections_text: str | None = None
    corrections_selected: list[str] = field(default_factory=list)
    corrections_skipped: list[str] = field(default_factory=list)

    @property
    def tokens(self) -> int:
        return sum(f.tokens for f in self.files)

    @property
    def over_budget(self) -> bool:
        return self.tokens > self.budget_tokens

    def source_ids(self) -> set[str]:
        return {s.id for s in self.sources}

    def manifest(self) -> dict[str, Any]:
        return {
            "route": self.route.id,
            "intent": self.route.intent,
            "asof": self.asof.isoformat(),
            "loaded": [{"path": f.path, "layer": f.layer, "tokens": f.tokens} for f in self.files],
            "missing": list(self.missing),
            "context_tokens_est": self.tokens,
            "budget_tokens": self.budget_tokens,
            "over_budget": self.over_budget,
            "corrections_loaded": list(self.corrections_selected),
            "corrections_skipped": list(self.corrections_skipped),
            "sources_admitted": [s.id for s in self.sources],
            "sources_excluded_after_asof": [s.id for s in self.excluded_future],
            "sources_undated": [s.id for s in self.undated],
        }


def assemble(
    task: str,
    asof: date,
    *,
    root: Path | None = None,
    config: RouterConfig | None = None,
    sources: list[Source] | None = None,
    include_optional: bool = False,
    budget_tokens: int = DEFAULT_BUDGET_TOKENS,
) -> Workspace:
    root = root or repo_root()
    config = config or load_router(root)
    route = match_route(task, config)

    plan = [(path, "rules") for path in config.always_load]
    plan += [(path, "skill") for path in route.required_skills]
    if include_optional:
        plan += [(path, "skill") for path in route.optional_skills]
    plan += [(path, "golden") for path in route.golden]

    workspace = Workspace(route=route, asof=asof, budget_tokens=budget_tokens)
    seen: set[str] = set()
    for rel, layer in plan:
        if rel in seen:
            continue
        seen.add(rel)
        file = root / rel
        if not file.is_file():
            workspace.missing.append(rel)
            continue
        text = file.read_text(encoding="utf-8")
        if rel == CORRECTIONS_FILE:
            memory = parse_memory(text)
            selected, skipped = memory.select(route.correction_tags)
            text = memory.render(selected)
            workspace.corrections_text = text
            workspace.corrections_selected = [entry.title for entry in selected]
            workspace.corrections_skipped = [entry.title for entry in skipped]
        workspace.files.append(LoadedFile(rel, layer, estimate_tokens(text)))

    for source in sources or []:
        if source.published is None:
            workspace.undated.append(source)
            workspace.sources.append(source)
        elif source.published > asof:
            workspace.excluded_future.append(source)
        else:
            workspace.sources.append(source)
    return workspace


def materialize(ws: Workspace, out_dir: Path | str) -> Path:
    """Write the workspace the model will see: manifest, as-of sources, route corrections.

    Sources published after ``asof`` are not written, so they cannot reach the model.
    """
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "manifest.json").write_text(
        json.dumps(ws.manifest(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    payload = {"asof": ws.asof.isoformat(), "sources": [s.to_dict() for s in ws.sources]}
    (out / "sources.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if ws.corrections_text is not None:
        (out / "corrections.md").write_text(ws.corrections_text, encoding="utf-8")
    return out
