"""Correction signals (纠偏触发) and correction memory (纠错沉淀).

The reviewer's way of pushing back is itself a signal: "为何没有 X" checks pool
completeness, "这个分类严谨吗" checks the classification axis. Recognising the signal
tells the agent which checkpoint to return to, and a Correction Card turns the one-off
fix into a rule that later tasks load. Each memory entry carries an ``Applies to`` tag,
so a task loads only the corrections relevant to its route.
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from .checkpoints import CHECKPOINTS

CORRECTIONS_FILE = "agent/memory/corrections.md"
FORMAT_HEADING = "## Format For Future Corrections"


@dataclass(frozen=True)
class Signal:
    patterns: tuple[str, ...]
    checking: str
    checkpoint: int
    next_artifact: str


# Most specific first: generic words such as "不是" / "不要" only match last.
SIGNALS: tuple[Signal, ...] = (
    Signal(
        ("先和我确认", "和我确认", "先给我 check", "确认你的理解"),
        "whether the task frame is right before any long-form writing",
        1,
        "Task Packet and structure only",
    ),
    Signal(
        ("为何没有", "为什么没有", "凡是拿到融资", "漏了"),
        "whether the pool is complete before prioritising",
        2,
        "updated pool with inclusion rule and source status",
    ),
    Signal(
        ("为什么这么分", "分类严谨", "这个分类", "口径"),
        "whether there is one primary, non-overlapping classification axis",
        3,
        "primary axis, category definitions and edge cases",
    ),
    Signal(
        ("先写 2 个", "先写2个", "先写两个", "先给几个样例"),
        "style calibration on a small sample",
        4,
        "2-3 sample paragraphs",
    ),
    Signal(
        ("不要下判断", "我是实习生", "不需要给自己的判断"),
        "the output boundary: evidence, not a final recommendation",
        1,
        "draft without final investment / FA recommendation",
    ),
    Signal(
        ("这个太散", "太散", "先给 insight", "先给insight"),
        "insight-first structure",
        5,
        "insight-led revision",
    ),
    Signal(
        ("这个图是什么意思", "为什么没放"),
        "whether the chart logic is explainable and complete",
        5,
        "metric definitions, inclusion rules and readable labels",
    ),
    Signal(
        ("理解错了", "不是这个意思", "你需要先", "不是", "不要"),
        "task understanding",
        1,
        "rewritten Task Packet",
    ),
)


@dataclass(frozen=True)
class Detection:
    trigger: str
    signal: Signal


def detect(text: str) -> Detection | None:
    for signal in SIGNALS:
        for pattern in signal.patterns:
            if pattern in text:
                return Detection(pattern, signal)
    return None


def capture(text: str) -> str | None:
    """Render the Correction Capture block from checkpoint_workflow.md, or None."""
    detection = detect(text)
    if detection is None:
        return None
    checkpoint = detection.signal.checkpoint
    return "\n".join(
        [
            "## Correction Capture",
            "",
            f"- You corrected: {text.strip()}",
            f"- Signal: `{detection.trigger}` -> checking {detection.signal.checking}",
            f"- I will now return to checkpoint: {checkpoint} ({CHECKPOINTS[checkpoint]})",
            f"- Next artifact: {detection.signal.next_artifact}",
        ]
    )


@dataclass(frozen=True)
class CorrectionCard:
    title: str
    trigger: str
    correction: str
    future_rule: str
    applies_to: str = "all"

    def to_markdown(self, on: date | None = None) -> str:
        day = (on or date.today()).isoformat()
        return (
            f"### {day} - {self.title}\n\n"
            f"- Trigger: {self.trigger}\n"
            f"- Correction: {self.correction}\n"
            f"- Future rule: {self.future_rule}\n"
            f"- Applies to: {self.applies_to}\n"
        )


def append_card(path: Path | str, card: CorrectionCard, on: date | None = None) -> None:
    """Add a card to the corrections memory, before the format section when there is one."""
    path = Path(path)
    existing = path.read_text(encoding="utf-8") if path.exists() else "# Corrections Memory\n"
    block = card.to_markdown(on) + "\n"
    head, sep, tail = existing.partition("\n" + FORMAT_HEADING)
    if sep:
        updated = head.rstrip("\n") + "\n\n" + block + FORMAT_HEADING + tail
    else:
        updated = existing.rstrip("\n") + "\n\n" + block
    path.write_text(updated, encoding="utf-8")


# ---------------------------------------------------------------- memory filtering

_APPLIES = re.compile(r"^-\s*Applies to:\s*(.+)$", re.MULTILINE)
_TAG_SPLIT = re.compile(r"[/,，、]")


@dataclass(frozen=True)
class MemoryEntry:
    title: str
    applies_to: tuple[str, ...]
    text: str

    def applies(self, tags: Iterable[str]) -> bool:
        mine = {tag.lower() for tag in self.applies_to}
        return "all" in mine or bool(mine & {tag.lower() for tag in tags})


@dataclass(frozen=True)
class CorrectionsMemory:
    preamble: str
    entries: tuple[MemoryEntry, ...]
    postamble: str

    def select(self, tags: Iterable[str]) -> tuple[list[MemoryEntry], list[MemoryEntry]]:
        """Entries relevant to ``tags`` (always including ``all``); no tags selects everything."""
        tags = list(tags)
        if not tags:
            return list(self.entries), []
        selected = [e for e in self.entries if e.applies(tags)]
        skipped = [e for e in self.entries if not e.applies(tags)]
        return selected, skipped

    def render(self, entries: Iterable[MemoryEntry]) -> str:
        parts = [self.preamble.rstrip("\n"), *(e.text.rstrip("\n") for e in entries)]
        if self.postamble.strip():
            parts.append(self.postamble.rstrip("\n"))
        return "\n\n".join(part for part in parts if part) + "\n"


def parse_memory(text: str) -> CorrectionsMemory:
    """Split the memory file into preamble, dated ``###`` entries and trailing sections."""
    preamble: list[str] = []
    postamble: list[str] = []
    entries: list[list[str]] = []
    target = preamble
    in_fence = False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
        elif not in_fence and line.startswith("### "):
            entries.append([])
            target = entries[-1]
        elif not in_fence and line.startswith("## ") and entries:
            target = postamble
        target.append(line)
    parsed = []
    for lines in entries:
        body = "\n".join(lines)
        match = _APPLIES.search(body)
        tags = _TAG_SPLIT.split(match.group(1)) if match else ["all"]
        parsed.append(
            MemoryEntry(
                title=lines[0][4:].strip(),
                applies_to=tuple(tag.strip() for tag in tags if tag.strip()),
                text=body.strip("\n"),
            )
        )
    return CorrectionsMemory("\n".join(preamble), tuple(parsed), "\n".join(postamble))
