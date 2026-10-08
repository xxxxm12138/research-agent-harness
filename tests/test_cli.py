from __future__ import annotations

import json

import pytest

from ir_harness import __version__
from ir_harness.cli import main


@pytest.fixture()
def run_cli(root, capsys):
    def _run(*args: str) -> tuple[int, str]:
        code = main(["--root", str(root), *args])
        return code, capsys.readouterr().out

    return _run


def test_version(capsys):
    with pytest.raises(SystemExit):
        main(["--version"])
    assert __version__ in capsys.readouterr().out


def test_route(run_cli, task):
    code, out = run_cli("route", task)
    assert code == 0
    assert "route    : mapping" in out


def test_route_without_signal_exits_2(run_cli):
    code, out = run_cli("route", "随便聊聊")
    assert code == 2
    assert "no route" in out


def test_assemble_json(run_cli, task, example_dir, tmp_path):
    sources = str(example_dir / "sources.json")
    out_dir = tmp_path / "ws"
    code, out = run_cli(
        "assemble",
        task,
        "--asof",
        "2026-09-30",
        "--sources",
        sources,
        "--json",
        "--out",
        str(out_dir),
    )
    manifest = json.loads(out)
    assert code == 0
    assert manifest["sources_excluded_after_asof"] == ["S-09"]
    assert len(manifest["corrections_skipped"]) == 1
    assert (out_dir / "sources.json").is_file()


def test_assemble_text(run_cli, task, example_dir):
    code, out = run_cli(
        "assemble", task, "--asof", "2026-09-30", "--sources", str(example_dir / "sources.json")
    )
    assert code == 0
    assert "excluded (after asof)  : S-09" in out
    assert "corrections            : 10 loaded, 1 skipped for this route" in out


def test_check_good_and_bad(run_cli, example_dir):
    sources = str(example_dir / "sources.json")
    code, out = run_cli("check", str(example_dir / "run.json"), "--sources", sources)
    assert code == 0
    assert "all gates passed" in out
    code, out = run_cli("check", str(example_dir / "run_bad.json"), "--sources", sources)
    assert code == 1
    assert "return to checkpoint 1: Task Understanding" in out


def test_score(run_cli, example_dir):
    code, out = run_cli("score", str(example_dir / "run.json"), "--judge", "Judgment quality=2")
    assert code == 0
    assert "Total 14/14 -> pass" in out
    sources = str(example_dir / "sources.json")
    code, out = run_cli("score", str(example_dir / "run_bad.json"), "--sources", sources)
    assert code == 1
    assert "2/4 claims sourced and correctly labelled" in out


def test_correction(run_cli):
    code, out = run_cli("correction", "这个分类严谨吗")
    assert code == 0
    assert "checkpoint: 3 (Classification Definitions)" in out


def test_validate_repo(run_cli):
    code, out = run_cli("validate")
    assert code == 0, out
    assert out.strip().endswith("OK")


def test_run_dry_run_writes_workspace_and_prints_pi_command(run_cli, task, example_dir, tmp_path):
    run_dir = tmp_path / "run"
    code, out = run_cli(
        "run",
        task,
        "--asof",
        "2026-09-30",
        "--sources",
        str(example_dir / "sources.json"),
        "--model",
        "anthropic/claude-x",
        "--out",
        str(run_dir),
        "--dry-run",
    )
    assert code == 0
    assert out.startswith("pi --model anthropic/claude-x")
    assert str(run_dir / "workspace" / "sources.json") in out
    assert (run_dir / "workspace" / "manifest.json").is_file()


def test_scan_tmp_dir(tmp_path, capsys):
    (tmp_path / "agent").mkdir()
    (tmp_path / "agent" / "router.md").write_text("# empty\n", encoding="utf-8")
    (tmp_path / "x.md").write_text("ACME inside\n", encoding="utf-8")
    terms = tmp_path / "terms.txt"
    terms.write_text("acme\n", encoding="utf-8")
    code = main(["--root", str(tmp_path), "scan", "--no-git", "--terms", str(terms)])
    out = capsys.readouterr().out
    assert code == 1
    assert "x.md:1: blocklisted-term" in out
