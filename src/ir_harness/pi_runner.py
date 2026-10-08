"""Run an assembled workspace through the Pi agent harness, with the model as a parameter.

Code decides *what* the agent sees; Pi runs the agent loop; the model is swappable.
Workspace layers map onto Pi inputs:

- rules (control layer)             -> ``--append-system-prompt``
- skills (method layer)             -> ``--skill``
- golden samples, contract, sources -> ``@file`` attachments in the user message

With a materialized workspace folder, the corrections memory is replaced by the
route-filtered copy and the sources file contains only material dated on or before
``asof``.

``--no-context-files`` keeps runs deterministic: nothing is picked up implicitly
from AGENTS.md / CLAUDE.md beyond what the router selected.
"""

from __future__ import annotations

import json
import re
import shlex
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .corrections import CORRECTIONS_FILE
from .workspace import Workspace

PI_INSTALL_HINT = "npm install -g @earendil-works/pi-coding-agent"
CONTRACT_FILE = Path("agent") / "run_record_contract.md"
_JSON_BLOCK = re.compile(r"```json\s*\n(.*?)\n```", re.DOTALL)


class PiUnavailableError(RuntimeError):
    """The ``pi`` CLI is not installed or not on PATH."""


@dataclass(frozen=True)
class PiCommand:
    argv: tuple[str, ...]

    def shell(self) -> str:
        return shlex.join(self.argv)


def task_message(task: str, ws: Workspace) -> str:
    return (
        f"任务：{task}\n"
        f"时点（asof）：{ws.asof.isoformat()}，只能使用该日期及之前的材料。\n"
        f"路由：{ws.route.id}（{ws.route.intent}）。先给出 Task Packet；"
        "正式输出之后，按 run_record_contract.md 附一个 ```json 代码块。"
    )


def build_command(
    ws: Workspace,
    task: str,
    *,
    model: str,
    root: Path,
    workspace_dir: Path | None = None,
    tools: str = "read",
) -> PiCommand:
    """Build the ``pi`` invocation; ``workspace_dir`` is the output of ``materialize``."""
    argv = ["pi", "--model", model, "--no-session", "--no-context-files", "--tools", tools]
    filtered = workspace_dir / "corrections.md" if workspace_dir is not None else None
    for loaded in ws.files:
        if loaded.layer == "rules":
            path = root / loaded.path
            if loaded.path == CORRECTIONS_FILE and filtered is not None and filtered.is_file():
                path = filtered
            argv += ["--append-system-prompt", str(path)]
    for loaded in ws.files:
        if loaded.layer == "skill":
            argv += ["--skill", str(root / loaded.path)]
    argv.append("-p")
    attachments = [root / f.path for f in ws.files if f.layer == "golden"]
    if (root / CONTRACT_FILE).is_file():
        attachments.append(root / CONTRACT_FILE)
    if workspace_dir is not None and (workspace_dir / "sources.json").is_file():
        attachments.append(workspace_dir / "sources.json")
    argv += [f"@{path}" for path in attachments]
    argv.append(task_message(task, ws))
    return PiCommand(tuple(argv))


def run(cmd: PiCommand, *, timeout: int = 900, env: dict[str, str] | None = None) -> str:
    if shutil.which(cmd.argv[0]) is None:
        raise PiUnavailableError(f"'{cmd.argv[0]}' not found on PATH; install: {PI_INSTALL_HINT}")
    proc = subprocess.run(
        list(cmd.argv), capture_output=True, text=True, timeout=timeout, env=env, check=False
    )
    if proc.returncode != 0:
        raise RuntimeError(f"pi exited with {proc.returncode}: {proc.stderr.strip()[:500]}")
    return proc.stdout


def extract_run_record(text: str) -> dict[str, Any]:
    """Return the last ```json block of the model output as a dict."""
    blocks = _JSON_BLOCK.findall(text)
    if not blocks:
        raise ValueError("no ```json block in model output (see agent/run_record_contract.md)")
    return json.loads(blocks[-1])
