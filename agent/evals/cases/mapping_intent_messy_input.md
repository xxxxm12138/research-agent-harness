# Eval Case: Mapping Intent - Messy Input

## Purpose

Test whether the research-intern agent recognises the intended artifact before writing: this is a mapping 底稿 task, not an investment memo, a final FA-matching recommendation or a single-company pitch.

The pattern comes from a real interaction (messy screenshots, one anchor financing lead, a request to "research" a direction, and an explicit intern boundary). Company names below are fictional; they are the same fictional set used in `examples/ai-companion-hardware/`.

## Input To Agent

```text
我在群里看到「栖语」据说在融 A 轮（截图），做的是语音陪伴吊坠。
还有一些截图：过去投过 AI 陪伴 / AI 硬件入口的创业者和机构，里面有星芽、澄心、脉知、拾光、回声，还有 AI 录音卡、指环、桌面机器人这些形态。

你帮我做一下 research，看看这个方向的项目怎么分，哪些项目拿到融资，哪些机构在看。
我不是要你最后判断该找哪家机构，我是实习生，先把信息收集、整理、分类、做表格和画像。
结构参考之前那份 Mapping。
```

## Machine-Checkable Expectations

| Key | Value |
|---|---|
| route | `mapping` |
| intent | mapping 底稿 |

## Expected Route

- Control files: `agent/router.md`, `agent/playbook.md`, `agent/memory/user_judgment.md`, `agent/memory/corrections.md`
- Skills: `skills/style-replication/SKILL.md`, `skills/research-mapping/SKILL.md`, `skills/track-analysis/SKILL.md`; `skills/landscape-visualization/SKILL.md` if charts are requested
- Samples: `agent/golden/mapping.md`

## Expected First Response Shape

The agent does not start the final report. It produces:

1. a Task Packet;
2. an intent classification: `mapping 底稿`, not `memo` or `FA 匹配建议`;
3. a proposed primary classification axis and why it separates the players (hardware form is an entry form, not a category);
4. an initial project pool grouped by proposed category, including every named and financed project;
5. the proposed mapping table fields;
6. the institution profile format: `机构属性 / 投资项目 - 金额 / 投资过程 / 可观察偏好`;
7. a source and DD strategy;
8. only high-value confirmation questions.

## Passing Signals

- Recognises the intern role and avoids a final investment recommendation.
- Uses one primary classification axis instead of mixing technology, hardware form, financing stage and user scenario.
- Puts every named project in the pool before prioritising.
- Proposes category-level sorting, then sorting by financing amount within each category.
- Marks screenshot-only or unverifiable claims as `市场线索待核验` / `用户截图线索，待DD`.
- If visualizing, explains each chart's metric, inclusion rule and reading method.

## Fail Conditions

- Starts with a long memo or thesis before the Task Packet is confirmed.
- Recommends which institution to contact without being asked.
- Creates overlapping top-level categories without explaining the primary axis.
- Omits named or financed projects because they are harder to verify.
- Writes generic fund introductions instead of deal-led institution portraits.
- Presents screenshot leads, financing amounts or founder background as confirmed facts.

## Automated Check

`examples/ai-companion-hardware/run.json` is a passing record for this case and `run_bad.json` a failing one:

```bash
irh check examples/ai-companion-hardware/run.json --sources examples/ai-companion-hardware/sources.json      # all gates pass
irh check examples/ai-companion-hardware/run_bad.json --sources examples/ai-companion-hardware/sources.json  # returns to checkpoint 1
```
