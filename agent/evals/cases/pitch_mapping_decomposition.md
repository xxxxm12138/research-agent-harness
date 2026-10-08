# Eval Case: Pitch-Prep Mapping - Task Decomposition

## Purpose

Test whether the research-intern agent turns a messy pitch-prep request into a Task Packet and a priority order before writing anything long. The input is fictionalised from a real pattern: an upcoming meeting, scattered material of uneven age, and an unclear label for the target.

## Input To Agent

```text
下周可能要见一个 AI 陪伴硬件方向的新团队，让我先做个 pitch 前 mapping。
材料很散：有一份旧的 AI 硬件赛道报告、创始人背调的初稿、几家海外消费硬件公司的公开资料，还有国内一些端侧 agent 项目。
我现在不确定应该先看海外还是国内，也不确定这个项目到底算 AI 硬件、端侧 agent 还是陪伴应用。
你先帮我拆一下任务，告诉我该怎么做、读哪些材料、产出什么。
```

## Machine-Checkable Expectations

| Key | Value |
|---|---|
| route | `mapping` |
| intent | mapping 底稿 |

## Expected Route

- Control files: `agent/router.md`, `agent/playbook.md`, `agent/memory/corrections.md`
- Skills: `skills/style-replication/SKILL.md`, `skills/research-mapping/SKILL.md`, `skills/track-analysis/SKILL.md`; `skills/founder-diligence/SKILL.md` if people diligence becomes P0
- Samples: `agent/golden/mapping.md`

## Expected Output Shape

The agent does not start the final report. It produces:

1. a Task Packet;
2. a confirmation of its task understanding;
3. a proposed priority order, likely `海外参照系 -> 国内分类轴 -> 人物/团队深调 -> 项目画像/BP 卖点`;
4. an evidence plan that says how old material will be dated and labelled;
5. formal output paths;
6. a reference to the self-check rubric.

## Fail Conditions

- Starts with a long report before the Task Packet is confirmed.
- Lists companies without defining the coordinate system.
- Treats AI 硬件, 端侧 agent and 陪伴应用 as interchangeable labels instead of testing which axis separates them.
- Omits flip conditions or the reader's decision.
- Does not include a plain-language report deliverable.
