"""Pre-publication compliance scan.

Four checks over the files that would be published:

- secrets: API keys, cloud and GitHub tokens, private keys;
- confidential file types: BP decks, transcripts and deal spreadsheets never belong here;
- leaks: absolute home-directory paths and links to private documents or artifacts;
- a *local* blocklist of real names kept in ``.sensitive-terms.txt``. The blocklist is
  gitignored, so the names themselves never enter the repository.

Inside a git work tree only tracked and not-ignored files are scanned (what a push
would publish); elsewhere the whole tree is walked.
"""

from __future__ import annotations

import re
import subprocess
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from pathlib import Path

SECRET_PATTERNS: dict[str, re.Pattern[str]] = {
    "api-key": re.compile(r"\bsk-(?:ant-)?[A-Za-z0-9_-]{20,}"),
    "aws-access-key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "github-token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b"),
    "private-key": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
}
LEAK_PATTERNS: dict[str, re.Pattern[str]] = {
    "local-path": re.compile(r"(?<![\w.~$])/(?:Users|home)/[A-Za-z0-9._-]+/"),
    "private-link": re.compile(
        r"https?://(?:[\w-]+\.)*(?:feishu\.cn|larksuite\.com|claude\.ai/(?:code/)?artifact)\S*",
        re.IGNORECASE,
    ),
}
CONFIDENTIAL_SUFFIXES = frozenset(
    {".pdf", ".doc", ".docx", ".ppt", ".pptx", ".xls", ".xlsx", ".zip", ".tar", ".m4a", ".mp3"}
)
SKIP_DIRS = frozenset(
    {".git", "__pycache__", ".venv", "venv", ".pytest_cache", ".ruff_cache", "build", "dist"}
)
DEFAULT_TERMS_FILE = ".sensitive-terms.txt"
REGEX_PREFIX = "re:"


@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    kind: str
    excerpt: str


def load_terms(path: Path | str) -> list[str]:
    """One term per line; blank lines and ``#`` comments are ignored.

    A plain line matches case-insensitively as a substring. A line starting with ``re:``
    is a case-sensitive regular expression, e.g. ``re:\\bAcme\\b`` for a name that is
    also a common word.
    """
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    return [ln.strip() for ln in lines if ln.strip() and not ln.lstrip().startswith("#")]


def compile_terms(terms: Iterable[str]) -> list[re.Pattern[str]]:
    patterns = []
    for term in terms:
        term = term.strip()
        if not term:
            continue
        if term.startswith(REGEX_PREFIX):
            patterns.append(re.compile(term[len(REGEX_PREFIX) :]))
        else:
            patterns.append(re.compile(re.escape(term), re.IGNORECASE))
    return patterns


def _mask(value: str) -> str:
    return value[:3] + "…" if len(value) > 4 else "…"


def _git_files(root: Path) -> list[Path] | None:
    """Tracked plus untracked-but-not-ignored files, or None outside a git work tree."""
    try:
        proc = subprocess.run(
            [
                "git",
                "-C",
                str(root),
                "ls-files",
                "-z",
                "--cached",
                "--others",
                "--exclude-standard",
            ],
            capture_output=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    names = proc.stdout.decode("utf-8").split("\0")
    return sorted({root / name for name in names if name})


def _walk(root: Path) -> list[Path]:
    files = []
    for path in sorted(root.rglob("*")):
        parts = path.relative_to(root).parts
        if any(part in SKIP_DIRS or part.endswith(".egg-info") for part in parts):
            continue
        files.append(path)
    return files


def iter_files(root: Path, *, use_git: bool = True) -> Iterator[Path]:
    candidates = (_git_files(root) if use_git else None) or _walk(root)
    for path in candidates:
        if path.is_file() and path.name != DEFAULT_TERMS_FILE:
            yield path


def scan(root: Path | str, terms: Iterable[str] = (), *, use_git: bool = True) -> list[Finding]:
    root = Path(root)
    blocklist = compile_terms(terms)
    findings: list[Finding] = []
    for path in iter_files(root, use_git=use_git):
        rel = path.relative_to(root).as_posix()
        if path.suffix.lower() in CONFIDENTIAL_SUFFIXES:
            findings.append(Finding(rel, 0, "confidential-file-type", path.suffix))
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for number, line in enumerate(text.splitlines(), start=1):
            for kind, pattern in {**SECRET_PATTERNS, **LEAK_PATTERNS}.items():
                for match in pattern.finditer(line):
                    findings.append(Finding(rel, number, kind, _mask(match.group())))
            for pattern in blocklist:
                match = pattern.search(line)
                if match:
                    findings.append(Finding(rel, number, "blocklisted-term", _mask(match.group())))
    return findings
