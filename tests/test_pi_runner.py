from __future__ import annotations

import json

import pytest

from ir_harness import pi_runner
from ir_harness.pi_runner import (
    PiCommand,
    PiUnavailableError,
    build_command,
    extract_run_record,
    task_message,
)
from ir_harness.workspace import materialize


def _values(argv: list[str], flag: str) -> list[str]:
    return [argv[i + 1] for i, arg in enumerate(argv) if arg == flag]


def test_build_command_maps_layers_to_pi_inputs(ws, root, task, tmp_path):
    workspace_dir = materialize(ws, tmp_path / "workspace")
    argv = list(
        build_command(ws, task, model="openai/gpt-x", root=root, workspace_dir=workspace_dir).argv
    )
    assert argv[:3] == ["pi", "--model", "openai/gpt-x"]
    assert argv[3:7] == ["--no-session", "--no-context-files", "--tools", "read"]
    prompts = _values(argv, "--append-system-prompt")
    assert len(prompts) == 6
    assert prompts[0].endswith("agent/playbook.md")
    assert str(workspace_dir / "corrections.md") in prompts
    assert not any(p.endswith("agent/memory/corrections.md") for p in prompts)
    skills = [s.split("/skills/")[-1] for s in _values(argv, "--skill")]
    assert skills == ["research-mapping/SKILL.md", "track-analysis/SKILL.md"]
    tail = argv[argv.index("-p") + 1 :]
    assert tail[0].startswith("@") and tail[0].endswith("agent/golden/mapping.md")
    assert tail[1].endswith("agent/run_record_contract.md")
    assert tail[2] == f"@{workspace_dir / 'sources.json'}"
    assert tail[-1] == task_message(task, ws)
    assert "2026-09-30" in tail[-1]


def test_model_never_sees_sources_after_asof(ws, tmp_path):
    workspace_dir = materialize(ws, tmp_path / "workspace")
    data = json.loads((workspace_dir / "sources.json").read_text(encoding="utf-8"))
    ids = {s["id"] for s in data["sources"]}
    assert "S-09" not in ids
    assert "S-01" in ids
    tiers = {s["id"]: s["tier"] for s in data["sources"]}
    assert tiers["S-02"] == "待DD"
    assert tiers["S-05"] == "待DD"


def test_without_workspace_dir_uses_repo_files(ws, root, task):
    argv = list(build_command(ws, task, model="m", root=root).argv)
    assert any(
        p.endswith("agent/memory/corrections.md") for p in _values(argv, "--append-system-prompt")
    )
    assert not any(a.endswith("sources.json") for a in argv)


def test_shell_quotes_arguments():
    assert PiCommand(("pi", "-p", "hello world")).shell() == "pi -p 'hello world'"


def test_extract_run_record_takes_last_json_block():
    text = 'intro\n```json\n{"a": 1}\n```\nmore\n```json\n{"route": "mapping"}\n```\n'
    assert extract_run_record(text) == {"route": "mapping"}


def test_extract_run_record_requires_a_block():
    with pytest.raises(ValueError):
        extract_run_record("no record here")


def test_run_reports_missing_pi(monkeypatch):
    monkeypatch.setattr(pi_runner.shutil, "which", lambda name: None)
    with pytest.raises(PiUnavailableError, match="npm install"):
        pi_runner.run(PiCommand(("pi", "-p", "x")))
