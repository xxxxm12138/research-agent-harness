from __future__ import annotations

from datetime import date

import pytest

from ir_harness.corrections import (
    FORMAT_HEADING,
    CorrectionCard,
    append_card,
    capture,
    detect,
    parse_memory,
)


@pytest.mark.parametrize(
    ("feedback", "checkpoint"),
    [
        ("不是，你需要主动先和我确认任务需求", 1),
        ("为何没有拾光？凡是拿到融资的都列上", 2),
        ("这个分类严谨吗", 3),
        ("先写 2 个我看看", 4),
        ("我是实习生，不要下判断", 1),
        ("这个太散了", 5),
        ("这个图是什么意思", 5),
        ("理解错了", 1),
    ],
)
def test_detect_maps_feedback_to_checkpoint(feedback, checkpoint):
    detection = detect(feedback)
    assert detection is not None
    assert detection.signal.checkpoint == checkpoint


def test_specific_signal_beats_generic_words():
    detection = detect("不是，你需要主动先和我确认")
    assert detection.trigger == "先和我确认"


def test_no_signal():
    assert detect("很好，继续") is None
    assert capture("很好，继续") is None


def test_capture_renders_block():
    block = capture("为什么没有 X")
    assert block.startswith("## Correction Capture")
    assert "return to checkpoint: 2 (Sample Pool)" in block


def test_append_card(tmp_path):
    path = tmp_path / "corrections.md"
    card = CorrectionCard("先锁池", "漏项目", "补池", "画像前先锁项目池", "Mapping")
    append_card(path, card, on=date(2026, 9, 30))
    append_card(path, card, on=date(2026, 10, 1))
    text = path.read_text(encoding="utf-8")
    assert text.startswith("# Corrections Memory")
    assert "### 2026-09-30 - 先锁池" in text
    assert "### 2026-10-01 - 先锁池" in text
    assert "- Applies to: Mapping" in text


MEMORY = """# Corrections Memory

intro

## Active Corrections

- general rule

### 2026-01-01 - Mapping rule

- Future rule: one axis
- Applies to: Mapping / 赛道分析

### 2026-01-02 - Everywhere rule

- Applies to: all

### 2026-01-03 - CR rule

- Applies to: CR

## Format For Future Corrections

```markdown
### YYYY-MM-DD - [short title]

- Applies to:
```
"""


def test_parse_memory_ignores_headings_inside_code_fences():
    memory = parse_memory(MEMORY)
    assert [e.title for e in memory.entries] == [
        "2026-01-01 - Mapping rule",
        "2026-01-02 - Everywhere rule",
        "2026-01-03 - CR rule",
    ]
    assert memory.entries[0].applies_to == ("Mapping", "赛道分析")
    assert "general rule" in memory.preamble
    assert FORMAT_HEADING in memory.postamble


def test_select_by_route_tags_always_keeps_all():
    memory = parse_memory(MEMORY)
    selected, skipped = memory.select(["CR"])
    assert [e.title for e in selected] == ["2026-01-02 - Everywhere rule", "2026-01-03 - CR rule"]
    assert [e.title for e in skipped] == ["2026-01-01 - Mapping rule"]
    assert memory.select([])[1] == []
    text = memory.render(selected)
    assert "general rule" in text and "CR rule" in text and "Mapping rule" not in text
    assert text.rstrip().endswith("```")


def test_append_card_goes_before_the_format_section(tmp_path):
    path = tmp_path / "corrections.md"
    path.write_text(MEMORY, encoding="utf-8")
    append_card(path, CorrectionCard("新规则", "t", "c", "f", "CR"), on=date(2026, 2, 1))
    text = path.read_text(encoding="utf-8")
    assert text.index("### 2026-02-01 - 新规则") < text.index(FORMAT_HEADING)
    assert [e.title for e in parse_memory(text).entries][-1] == "2026-02-01 - 新规则"
