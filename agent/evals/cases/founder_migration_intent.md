# Eval Case: Founder Migration Mapping Intent

## Purpose

Test whether the research-intern agent identifies a founder / people migration mapping task, runs the checkpoints, and avoids writing a premature trend thesis or investment judgment.

The pattern comes from a real interaction: the reviewer provides screenshots or a rough table of AI founders, asks for a report on whether founder profiles are shifting, then corrects the agent to focus on factual portraits, the sample pool, valuation and investor data, and insight-led HTML.

## Input To Agent

```text
用实习生 agent 完成这个任务。

过去两年 AI 创业者画像，是否正在从"离大模型很近的人"，转向"离大模型没那么近，但有产品、数据、场景、商业化、组织/资本经验的人"。

重点不是判断是否，是做这些人的画像和发展梳理。落脚不是论证趋势成立，而是交付分析报告。

先中国，媒体传闻可以直接用。最新进展说得详细点：这个人做了啥、进展如何。

我还会给你一张表，里面有创始人、背景、创业方向、最新估值及投资方。
```

## Machine-Checkable Expectations

| Key | Value |
|---|---|
| route | `founder` |
| intent | 人物/创业者迁移 mapping |

## Expected Route

- Control files: `agent/router.md`, `agent/playbook.md`, `agent/checkpoint_workflow.md`, `agent/memory/user_judgment.md`, `agent/memory/corrections.md`
- Skills: `skills/research-mapping/SKILL.md`, `skills/founder-diligence/SKILL.md`, `skills/track-analysis/SKILL.md`; `skills/landscape-visualization/SKILL.md` if HTML or charts are requested
- Intent: `人物/创业者迁移 mapping`; not a memo, not a trend-thesis defense, not an investment recommendation

## Expected First Response Shape

The agent does not start the full report. It produces:

1. Intent Gate:
   - classifies the task as `人物/创业者迁移 mapping`;
   - says explicitly that it is not primarily a trend proof or an investment judgment;
   - names the deliverables: report + big table + profiles + optional HTML.
2. Checkpoint 1 - Task Understanding:
   - geography: China first;
   - time range: the past two years;
   - media rumors may be used but are labelled;
   - neutral, factual tone.
3. Checkpoint 2 - a proposed Sample Pool:
   - fields: person / project, current field, prior company / role, financing / valuation / investors, source status, inclusion reason;
   - names the reviewer supplied come first;
   - asks the reviewer to confirm or add people before profiles are written.
4. Checkpoint 3 - Classification Definitions:
   - background categories in reader-facing language;
   - labels such as `大厂应用产品/平台型背景` are explained;
   - source background, transferable ability and current field are kept apart.
5. Checkpoint 4 - Style Samples: 2-3 short sample profile paragraphs before full drafting.

## Passing Signals

- Confirms task requirements before writing.
- Produces a sample pool before profile writing.
- Separates `公开报道`, `媒体口径`, `市场线索待核验`, `待DD` and `未公开`.
- Keeps the fact chain: prior experience -> current project -> latest progress -> source status / unknowns.
- Does not praise founders or predict success unless asked.
- Does not lead with "the trend is true / false".
- For HTML: insight and sample base first, charts below; hover or click exposes names, projects and financing / valuation.
- Recomputes counts and percentages from the final table.
- Collects professional, public information only (see `skills/founder-diligence/SKILL.md`).

## Fail Conditions

- Starts with a full trend essay or investment memo.
- Treats media rumors as confirmed facts.
- Writes "画像判断" as success prediction or praise.
- Builds chart categories without defining the labels.
- Shows a visualization before explaining the analytical claim and metric.
- Does not stop and re-align when the reviewer says "不是", "你需要先", "不要" or "先和我确认".

## Correction Trigger Test

After the agent's first response, send this correction:

```text
不是，你需要主动先和我确认任务需求。这需要你先仔细解读我给你的需求和资料，和我对齐，然后给我例子。
```

Passing behaviour:

- The agent stops drafting.
- It outputs a `Correction Capture`.
- It states the corrected constraint.
- It returns to Checkpoint 1 or Checkpoint 2.
- It does not continue the stale draft.

`irh correction "<the text above>"` maps this feedback to checkpoint 1.
