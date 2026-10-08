"""Command-line entry point: ``irh <command>`` (or ``python -m ir_harness``)."""

from __future__ import annotations

import argparse
import json
from datetime import date, datetime
from pathlib import Path
from typing import Any

from . import __version__
from .compliance import DEFAULT_TERMS_FILE, load_terms, scan
from .corrections import capture
from .gates import CHECKPOINTS, return_checkpoint, run_gates
from .paths import repo_root
from .pi_runner import PiUnavailableError, build_command, extract_run_record
from .pi_runner import run as run_pi
from .repo_check import (
    dangling_references,
    eval_case_problems,
    load_eval_cases,
    markdown_files,
    skill_problems,
)
from .router import RoutingError, load_router, match_route, missing_references
from .rubric import Judge, load_rubric, score
from .run_record import RunRecord
from .workspace import Source, Workspace, assemble, load_sources, materialize


def _print_json(obj: Any) -> None:
    print(json.dumps(obj, ensure_ascii=False, indent=2, default=str))


def _sources(path: str | None) -> list[Source]:
    return load_sources(Path(path)) if path else []


def _print_gates(run: RunRecord, ws: Workspace) -> int:
    results = run_gates(run, ws)
    for result in results:
        print(f"[{'PASS' if result.passed else 'FAIL'}] {result.gate}")
        for error in result.errors:
            print(f"       - {error}")
    checkpoint = return_checkpoint(results)
    if checkpoint is None:
        print("all gates passed")
        return 0
    print(f"return to checkpoint {checkpoint}: {CHECKPOINTS[checkpoint]}")
    return 1


def cmd_route(args: argparse.Namespace) -> int:
    try:
        route = match_route(args.task, load_router(args.root))
    except RoutingError as exc:
        print(f"no route: {exc}")
        return 2
    print(f"route    : {route.id}")
    print(f"intent   : {route.intent}")
    print(f"skills   : {', '.join(route.required_skills)}")
    print(f"optional : {', '.join(route.optional_skills) or '-'}")
    print(f"golden   : {', '.join(route.golden) or '-'}")
    print(f"rubric   : {route.rubric or '-'}")
    print(f"output   : {route.output}")
    return 0


def cmd_assemble(args: argparse.Namespace) -> int:
    ws = assemble(
        args.task,
        date.fromisoformat(args.asof),
        root=args.root,
        sources=_sources(args.sources),
        include_optional=args.include_optional,
        budget_tokens=args.budget,
    )
    manifest = ws.manifest()
    if args.out:
        materialize(ws, args.out)
    if args.json:
        _print_json(manifest)
        return 1 if ws.missing else 0
    print(f"route {manifest['route']} ({manifest['intent']}) | asof {manifest['asof']}")
    for item in manifest["loaded"]:
        print(f"  [{item['layer']:<6}] {item['path']}  ~{item['tokens']} tok")
    for path in manifest["missing"]:
        print(f"  [missing] {path}")
    flag = "  (over budget)" if ws.over_budget else ""
    print(f"context ~{ws.tokens} / {ws.budget_tokens} tokens{flag}")
    loaded, skipped = manifest["corrections_loaded"], manifest["corrections_skipped"]
    if loaded or skipped:
        print(
            f"corrections            : {len(loaded)} loaded, {len(skipped)} skipped for this route"
        )
    if args.sources:
        print(f"sources admitted       : {', '.join(manifest['sources_admitted']) or '-'}")
        excluded = ", ".join(manifest["sources_excluded_after_asof"]) or "-"
        print(f"excluded (after asof)  : {excluded}")
        print(f"undated (admitted)     : {', '.join(manifest['sources_undated']) or '-'}")
    if args.out:
        print(f"workspace written to   : {args.out}")
    return 1 if ws.missing else 0


def cmd_check(args: argparse.Namespace) -> int:
    run = RunRecord.load(args.run)
    ws = assemble(run.task, run.asof, root=args.root, sources=_sources(args.sources))
    return _print_gates(run, ws)


def _judge_from(pairs: list[str] | None) -> Judge | None:
    table: dict[str, int] = {}
    for item in pairs or []:
        name, _, value = item.rpartition("=")
        table[name.strip().lower()] = int(value)
    if not table:
        return None
    return lambda dimension, _run: table.get(dimension.strip().lower())


def cmd_score(args: argparse.Namespace) -> int:
    run = RunRecord.load(args.run)
    try:
        route = load_router(args.root).get(run.route)
    except KeyError as exc:
        print(exc)
        return 2
    if not route.rubric:
        print(f"route '{route.id}' has no rubric")
        return 2
    origins = {s.id: s.origin for s in _sources(args.sources)} if args.sources else None
    card = score(
        run,
        load_rubric(args.root / route.rubric),
        route=route,
        judge=_judge_from(args.judge),
        source_origins=origins,
    )
    print(card.to_markdown())
    return 1 if card.verdict == "fail" else 0


def cmd_run(args: argparse.Namespace) -> int:
    root: Path = args.root
    asof = date.fromisoformat(args.asof)
    ws = assemble(args.task, asof, root=root, sources=_sources(args.sources))
    if ws.missing:
        print("missing workspace files: " + ", ".join(ws.missing))
        return 1
    run_dir = Path(args.out) if args.out else root / "runs" / _run_id(ws)
    workspace_dir = materialize(ws, run_dir / "workspace")
    cmd = build_command(ws, args.task, model=args.model, root=root, workspace_dir=workspace_dir)
    if args.dry_run:
        print(cmd.shell())
        print(f"# workspace: {workspace_dir}")
        return 0
    try:
        output = run_pi(cmd, timeout=args.timeout)
    except PiUnavailableError as exc:
        print(exc)
        return 2
    (run_dir / "output.md").write_text(output, encoding="utf-8")
    try:
        record = extract_run_record(output)
    except ValueError as exc:
        print(f"raw output saved to {run_dir / 'output.md'}; {exc}")
        return 1
    record.setdefault("task", args.task)
    record.setdefault("asof", args.asof)
    record.setdefault("route", ws.route.id)
    (run_dir / "run.json").write_text(
        json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"run saved to {run_dir}")
    return _print_gates(RunRecord.from_dict(record), ws)


def _run_id(ws: Workspace) -> str:
    return f"{datetime.now():%Y%m%d-%H%M%S}-{ws.route.id}"


def cmd_correction(args: argparse.Namespace) -> int:
    block = capture(args.text)
    print(block if block else "no correction signal detected")
    return 0


def cmd_scan(args: argparse.Namespace) -> int:
    root: Path = args.root
    terms_path = Path(args.terms) if args.terms else root / DEFAULT_TERMS_FILE
    terms = load_terms(terms_path) if terms_path.is_file() else []
    findings = scan(root, terms, use_git=not args.no_git)
    for finding in findings:
        print(f"{finding.path}:{finding.line}: {finding.kind} ({finding.excerpt})")
    print(f"{len(findings)} finding(s); {len(terms)} local blocklist term(s) checked")
    return 1 if findings else 0


def cmd_validate(args: argparse.Namespace) -> int:
    root: Path = args.root
    problems = [f"missing reference: {path}" for path in missing_references(root)]
    config = load_router(root)
    for route in config.routes:
        if route.rubric and (root / route.rubric).is_file():
            try:
                load_rubric(root / route.rubric)
            except ValueError as exc:
                problems.append(str(exc))
    problems += [str(p) for p in dangling_references(root)]
    problems += [str(p) for p in skill_problems(root)]
    problems += [str(p) for p in eval_case_problems(root)]
    for problem in problems:
        print(problem)
    status = "OK" if not problems else f"{len(problems)} problem(s)"
    cases = len(load_eval_cases(root))
    docs = sum(1 for _ in markdown_files(root))
    print(
        f"{len(config.routes)} routes, {len(config.always_load)} always-load files, "
        f"{cases} eval cases, {docs} markdown files: {status}"
    )
    return 1 if problems else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="irh", description="Investment-research agent harness")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("--root", type=Path, default=None, help="repo root (default: auto-detect)")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("route", help="show the route, skills and rubric a task maps to")
    p.add_argument("task")
    p.set_defaults(func=cmd_route)

    p = sub.add_parser("assemble", help="assemble the point-in-time workspace for a task")
    p.add_argument("task")
    p.add_argument("--asof", required=True, help="decision date, YYYY-MM-DD")
    p.add_argument("--sources", help="sources.json with origin and published date")
    p.add_argument("--include-optional", action="store_true")
    p.add_argument("--budget", type=int, default=60_000, help="context budget in tokens")
    p.add_argument("--json", action="store_true")
    p.add_argument("--out", help="write the workspace (manifest, as-of sources, corrections)")
    p.set_defaults(func=cmd_assemble)

    p = sub.add_parser("check", help="run the process gates on a run record")
    p.add_argument("run")
    p.add_argument("--sources")
    p.set_defaults(func=cmd_check)

    p = sub.add_parser("score", help="score a run record against its route's rubric")
    p.add_argument("run")
    p.add_argument("--sources", help="check evidence labels against the cited sources")
    p.add_argument("--judge", action="append", metavar="DIMENSION=SCORE")
    p.set_defaults(func=cmd_score)

    p = sub.add_parser("run", help="assemble, run through Pi, then gate the result")
    p.add_argument("task")
    p.add_argument("--asof", required=True)
    p.add_argument("--sources")
    p.add_argument("--model", default="deepseek/deepseek-chat", help="provider/model for Pi")
    p.add_argument("--timeout", type=int, default=900)
    p.add_argument("--out", help="run folder (default: runs/<timestamp>-<route>)")
    p.add_argument("--dry-run", action="store_true", help="write the workspace, print the command")
    p.set_defaults(func=cmd_run)

    p = sub.add_parser("correction", help="recognise a correction signal in user feedback")
    p.add_argument("text")
    p.set_defaults(func=cmd_correction)

    p = sub.add_parser("scan", help="compliance scan: secrets, leaks, file types, blocklist")
    p.add_argument("--terms", help=f"blocklist file (default: {DEFAULT_TERMS_FILE})")
    p.add_argument("--no-git", action="store_true", help="walk the tree instead of git files")
    p.set_defaults(func=cmd_scan)

    p = sub.add_parser("validate", help="check routing, rubrics, doc references and eval cases")
    p.set_defaults(func=cmd_validate)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    args.root = (args.root or repo_root()).resolve()
    return args.func(args)
