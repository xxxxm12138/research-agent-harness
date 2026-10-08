# Eval Case: Ambiguous Intent - "看看这个赛道"

## Purpose

The same short instruction can mean a mapping 底稿, an investment memo or a spoken briefing. Misjudging the deliverable is the most common failure, so when no route signal decides it, the agent must ask one concise question instead of guessing.

## Input To Agent

```text
帮我看看这个赛道（附一张 AI 陪伴硬件的产品截图）
```

## Machine-Checkable Expectations

| Key | Value |
|---|---|
| route | `clarify` |

`clarify` means no route may match: `irh route` must raise `RoutingError`, which the agent turns into a clarifying question.

## Expected First Response Shape

One short message that:

1. names the candidate deliverables in plain words: mapping 底稿（分类 + 总表 + 画像，不下结论）/ 投资备忘录（给 Push / Watch / Pass）/ 口头汇报（几段话讲清楚）;
2. states the one decision that tells them apart: what the reader will decide after reading;
3. proposes a default the reviewer can accept with one word (for example: "默认按 mapping 底稿先出分类轴和项目池给你确认").

## Passing Signals

- Asks exactly one question, with a default.
- Does not start research or writing before the answer.
- After the answer, produces the Task Packet of the chosen route.

## Fail Conditions

- Picks a deliverable silently and writes a long report.
- Asks a broad "你想要什么" without candidate intents.
- Asks several rounds of questions before producing anything checkable.
