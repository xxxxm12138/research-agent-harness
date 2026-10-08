from __future__ import annotations

import shutil
import subprocess

import pytest

from ir_harness.compliance import DEFAULT_TERMS_FILE, compile_terms, load_terms, scan

# Secret-looking strings are assembled at runtime so this file never matches the scanner.
FAKE_KEY = "sk-" + "x" * 32
FAKE_HOME = "/" + "Users" + "/someone/"
FAKE_LINK = "https://example." + "feishu.cn/docx/abc"


def kinds(findings):
    return sorted({f.kind for f in findings})


def test_detects_secrets_leaks_and_file_types(tmp_path):
    (tmp_path / "a.md").write_text(f"key={FAKE_KEY}\npath {FAKE_HOME}x\n{FAKE_LINK}\n", "utf-8")
    (tmp_path / "deck.pptx").write_bytes(b"binary")
    findings = scan(tmp_path, use_git=False)
    assert kinds(findings) == ["api-key", "confidential-file-type", "local-path", "private-link"]
    key = next(f for f in findings if f.kind == "api-key")
    assert (key.path, key.line) == ("a.md", 1)
    assert FAKE_KEY not in key.excerpt


def test_tilde_and_env_paths_are_not_flagged(tmp_path):
    (tmp_path / "a.md").write_text("~/.pi/agent/models.json and $HOME/mnt/x\n", "utf-8")
    assert scan(tmp_path, use_git=False) == []


def test_blocklist_plain_and_regex(tmp_path):
    (tmp_path / "a.md").write_text("met GLOBEX Capital\nAcmeville is fine\nsaw Acme\n", "utf-8")
    findings = scan(tmp_path, ["globex capital", r"re:\bAcme\b"], use_git=False)
    assert [(f.kind, f.line) for f in findings] == [
        ("blocklisted-term", 1),
        ("blocklisted-term", 3),
    ]


def test_terms_file_and_skip_dirs_are_ignored(tmp_path):
    (tmp_path / DEFAULT_TERMS_FILE).write_text("# comment\nACME\n\n", "utf-8")
    (tmp_path / ".venv").mkdir()
    (tmp_path / ".venv" / "x.md").write_text("ACME", "utf-8")
    terms = load_terms(tmp_path / DEFAULT_TERMS_FILE)
    assert terms == ["ACME"]
    assert scan(tmp_path, terms, use_git=False) == []


def test_compile_terms_skips_blanks():
    assert len(compile_terms(["", "  ", "a", "re:b"])) == 2


@pytest.mark.skipif(shutil.which("git") is None, reason="git not installed")
def test_git_mode_ignores_gitignored_files(tmp_path):
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    (tmp_path / ".gitignore").write_text(".env\n", "utf-8")
    (tmp_path / ".env").write_text(f"KEY={FAKE_KEY}\n", "utf-8")
    (tmp_path / "ok.md").write_text("clean\n", "utf-8")
    assert scan(tmp_path) == []
    assert kinds(scan(tmp_path, use_git=False)) == ["api-key"]
