"""Task routing, parsed directly from ``agent/router.md`` (docs as config).

The router table is what the agent reads *and* what this module executes, so the
documentation cannot drift from behaviour: ``irh validate`` fails when a path in
the table does not exist.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from .mdtable import backticked, parse_table, section
from .paths import repo_root

ROUTER_FILE = Path("agent") / "router.md"
_SIGNAL_SPLIT = re.compile(r"[,，、;；]")
EMPTY_CELLS = frozenset({"—", "-", ""})


class RoutingError(LookupError):
    """No route matched. Router rule: ask one concise clarifying question instead of guessing."""


@dataclass(frozen=True)
class Route:
    id: str
    intent: str
    signals: tuple[str, ...]
    required_skills: tuple[str, ...]
    optional_skills: tuple[str, ...] = ()
    golden: tuple[str, ...] = ()
    rubric: str | None = None
    output: str = ""
    not_intents: tuple[str, ...] = ()
    correction_tags: tuple[str, ...] = ()

    def score(self, task: str) -> int:
        """Number of this route's task signals that appear in ``task``."""
        text = task.lower()
        return sum(1 for signal in self.signals if signal in text)


@dataclass(frozen=True)
class RouterConfig:
    always_load: tuple[str, ...]
    routes: tuple[Route, ...]

    def get(self, route_id: str) -> Route:
        for route in self.routes:
            if route.id == route_id:
                return route
        raise KeyError(f"unknown route: {route_id}")


def _first_token(cell: str) -> str:
    tokens = backticked(cell)
    return tokens[0] if tokens else cell.strip()


def _split(cell: str) -> tuple[str, ...]:
    items = (item.strip() for item in _SIGNAL_SPLIT.split(cell))
    return tuple(item for item in items if item and item not in EMPTY_CELLS)


def load_router(root: Path | None = None) -> RouterConfig:
    root = root or repo_root()
    text = (root / ROUTER_FILE).read_text(encoding="utf-8")
    always = tuple(
        path
        for row in parse_table(section(text, "Always Load"))
        for path in backticked(row.get("File", ""))
    )
    routes: list[Route] = []
    for row in parse_table(section(text, "Routes")):
        rubric = backticked(row.get("Rubric", ""))
        routes.append(
            Route(
                id=_first_token(row.get("Route", "")),
                intent=row.get("Intent", "").strip(),
                signals=tuple(s.lower() for s in _split(row.get("Task signals", ""))),
                required_skills=tuple(backticked(row.get("Required skills", ""))),
                optional_skills=tuple(backticked(row.get("Optional skills", ""))),
                golden=tuple(backticked(row.get("Golden", ""))),
                rubric=rubric[0] if rubric else None,
                output=row.get("Output", "").strip(),
                not_intents=_split(row.get("Not", "")),
                correction_tags=tuple(backticked(row.get("Corrections", ""))),
            )
        )
    if not routes:
        raise ValueError(f"no routes parsed from {ROUTER_FILE}")
    return RouterConfig(always_load=always, routes=tuple(routes))


def match_route(task: str, config: RouterConfig) -> Route:
    """Pick the route with the most matched signals; table order breaks ties."""
    best: Route | None = None
    best_score = 0
    for route in config.routes:
        score = route.score(task)
        if score > best_score:
            best, best_score = route, score
    if best is None:
        raise RoutingError("no task signal matched; ask one concise clarifying question")
    return best


def referenced_files(config: RouterConfig) -> list[str]:
    refs = list(config.always_load)
    for route in config.routes:
        refs.extend(route.required_skills)
        refs.extend(route.optional_skills)
        refs.extend(route.golden)
        if route.rubric:
            refs.append(route.rubric)
    return sorted(set(refs))


def missing_references(root: Path | None = None) -> list[str]:
    """Paths named in the router that do not exist on disk."""
    root = root or repo_root()
    return [path for path in referenced_files(load_router(root)) if not (root / path).exists()]
