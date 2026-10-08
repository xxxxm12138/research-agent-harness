"""Repository consistency checks run by ``irh validate``.

Documentation is configuration here, so it gets the same treatment as code:

- every path a markdown file names (in backticks or as a relative link) must exist;
- every Skill has frontmatter with ``name`` and ``description``;
- every eval case's machine-checkable expectations agree with the router (an expected
  route of ``clarify`` means the router must refuse to guess).
"""

from __future__ import annotations

import re
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

from .mdtable import backticked, parse_table, section
from .router import RoutingError, load_router, match_route

REPO_DIRS = ("agent", "skills", "examples", "docs", "src", "pi", "tests", "tools", ".github")
SKIP_PARTS = frozenset({".git", ".venv", "venv", "node_modules", "build", "dist"})
SKIP_TOP = frozenset({"runs"})  # raw `irh run` outputs, gitignored
_BACKTICK = re.compile(r"`([^`\s]+)`")
_LINK = re.compile(r"\]\(([^)\s]+)\)")
_PLACEHOLDER = re.compile(r"[{}<>*\[\]|$]|\.\.\.|…|YYYY|MMDD")
_TEXT_BLOCK = re.compile(r"```text\n(.*?)\n```", re.DOTALL)
_FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
CLARIFY = "clarify"


@dataclass(frozen=True)
class Problem:
    path: str
    line: int
    message: str

    def __str__(self) -> str:
        where = f"{self.path}:{self.line}" if self.line else self.path
        return f"{where}: {self.message}"


def markdown_files(root: Path) -> Iterator[Path]:
    for path in sorted(root.rglob("*.md")):
        parts = path.relative_to(root).parts
        if parts[0] in SKIP_TOP or any(part in SKIP_PARTS for part in parts):
            continue
        yield path


def _target(token: str, md: Path, root: Path, *, link: bool) -> Path | None:
    token = token.split("#", 1)[0].rstrip(".,;:，。；：")
    if not token or _PLACEHOLDER.search(token) or "://" in token or token.startswith("mailto:"):
        return None
    if token.startswith(("./", "../")):
        return (md.parent / token).resolve()
    if token.split("/", 1)[0] in REPO_DIRS and "/" in token:
        return root / token
    if link:
        return (md.parent / token).resolve()
    return None


def dangling_references(root: Path) -> list[Problem]:
    problems: list[Problem] = []
    for md in markdown_files(root):
        rel = md.relative_to(root).as_posix()
        for number, line in enumerate(md.read_text(encoding="utf-8").splitlines(), start=1):
            refs = [(t, False) for t in _BACKTICK.findall(line)]
            refs += [(t, True) for t in _LINK.findall(line)]
            for token, is_link in refs:
                target = _target(token, md, root, link=is_link)
                if target is not None and not target.exists():
                    problems.append(Problem(rel, number, f"dangling reference: {token}"))
    return problems


def skill_problems(root: Path) -> list[Problem]:
    problems: list[Problem] = []
    for skill in sorted((root / "skills").glob("*/SKILL.md")):
        rel = skill.relative_to(root).as_posix()
        match = _FRONTMATTER.match(skill.read_text(encoding="utf-8"))
        if match is None:
            problems.append(Problem(rel, 1, "missing frontmatter"))
            continue
        keys = {
            line.split(":", 1)[0].strip() for line in match.group(1).splitlines() if ":" in line
        }
        for key in ("name", "description"):
            if key not in keys:
                problems.append(Problem(rel, 1, f"frontmatter lacks '{key}'"))
    return problems


@dataclass(frozen=True)
class EvalCase:
    path: str
    task: str
    route: str
    intent: str


def load_eval_cases(root: Path) -> list[EvalCase]:
    cases = []
    for path in sorted((root / "agent" / "evals" / "cases").glob("*.md")):
        text = path.read_text(encoding="utf-8")
        block = _TEXT_BLOCK.search(section(text, "Input To Agent"))
        rows = parse_table(section(text, "Machine-Checkable Expectations"))
        expected = {row.get("Key", "").strip(): row.get("Value", "").strip() for row in rows}
        route_tokens = backticked(expected.get("route", ""))
        cases.append(
            EvalCase(
                path=path.relative_to(root).as_posix(),
                task=block.group(1) if block else "",
                route=route_tokens[0] if route_tokens else expected.get("route", ""),
                intent=expected.get("intent", ""),
            )
        )
    return cases


def eval_case_problems(root: Path) -> list[Problem]:
    config = load_router(root)
    problems: list[Problem] = []
    for case in load_eval_cases(root):
        if not case.task or not case.route:
            problems.append(Problem(case.path, 0, "missing input block or expected route"))
            continue
        try:
            route = match_route(case.task, config)
        except RoutingError:
            if case.route != CLARIFY:
                problems.append(Problem(case.path, 0, f"matches no route (expected {case.route})"))
            continue
        if case.route == CLARIFY:
            problems.append(Problem(case.path, 0, f"routes to '{route.id}', expected a question"))
        elif route.id != case.route:
            problems.append(
                Problem(case.path, 0, f"routes to '{route.id}', expected '{case.route}'")
            )
        elif case.intent and route.intent != case.intent:
            problems.append(
                Problem(case.path, 0, f"intent '{route.intent}', expected '{case.intent}'")
            )
    return problems
