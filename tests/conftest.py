from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from ir_harness.router import RouterConfig, load_router
from ir_harness.run_record import RunRecord
from ir_harness.workspace import Source, Workspace, assemble, load_sources

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "ai-companion-hardware"
TASK = "帮我做 AI 陪伴硬件赛道的 mapping，看哪些机构投了"
ASOF = date(2026, 9, 30)


@pytest.fixture(scope="session")
def root() -> Path:
    return ROOT


@pytest.fixture(scope="session")
def example_dir() -> Path:
    return EXAMPLE


@pytest.fixture(scope="session")
def task() -> str:
    return TASK


@pytest.fixture(scope="session")
def asof() -> date:
    return ASOF


@pytest.fixture(scope="session")
def cfg() -> RouterConfig:
    return load_router(ROOT)


@pytest.fixture(scope="session")
def sources() -> list[Source]:
    return load_sources(EXAMPLE / "sources.json")


@pytest.fixture()
def ws(cfg: RouterConfig, sources: list[Source]) -> Workspace:
    return assemble(TASK, ASOF, root=ROOT, config=cfg, sources=sources)


@pytest.fixture()
def good_run() -> RunRecord:
    return RunRecord.load(EXAMPLE / "run.json")


@pytest.fixture()
def bad_run() -> RunRecord:
    return RunRecord.load(EXAMPLE / "run_bad.json")
