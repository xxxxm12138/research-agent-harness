"""Locate the repository root (the directory that contains ``agent/router.md``)."""

from __future__ import annotations

import os
from pathlib import Path

MARKER = Path("agent") / "router.md"


def repo_root(start: Path | None = None) -> Path:
    """Return the repo root: ``$IRH_ROOT`` if set, else the nearest parent holding the marker."""
    env = os.environ.get("IRH_ROOT")
    if env:
        return Path(env).resolve()
    for origin in (start or Path(__file__), Path.cwd()):
        here = origin.resolve()
        for candidate in (here, *here.parents):
            if (candidate / MARKER).is_file():
                return candidate
    raise FileNotFoundError(f"cannot locate repo root ({MARKER}); set IRH_ROOT")
