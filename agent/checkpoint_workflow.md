# Checkpoint Workflow

Use this file when a task is non-trivial and easy to misread, especially mapping, founder portraits, market maps, report-to-HTML, or tasks that arrive as screenshots or voice notes.

The goal is to make the agent pause at the right time. If the task matches a trigger, these checkpoints are not optional prose. When `irh check` fails, its output names the checkpoint to return to (for example `return to checkpoint 2: Sample Pool`).

## Universal Intent Gate

Before writing long-form output, produce a short intent gate:

```markdown
## Intent Gate

- I classify this task as: [mapping 底稿 / 人物-创业者迁移 mapping / memo / pitch / CR / 口头汇报 / other]
- It is not: [1-2 adjacent intents to avoid]
- The expected deliverable is: [report / table / HTML / chart / briefing]
- I should first confirm: [the 2-4 decisions that affect correctness]
```

If the reviewer corrects the intent, update the intent gate and restart from the matching checkpoint.

## Founder / People Migration Mapping

Trigger phrases include `创业者画像`, `过去两年创业者`, `大厂出来创业`, `背景迁移`, `转移趋势`, `这些人画像`, `谁拿到融资`.

Run these checkpoints in order.

### Checkpoint 1 - Task Understanding

Confirm:

- research object and scope;
- time range and geography;
- whether media rumors and market leads may be used;
- whether the report is neutral information or investment judgment;
- final format: text report, table, HTML, chart, or all of them.

Do not write profiles yet.

### Checkpoint 2 - Sample Pool

Produce a candidate table:

| Person / project | Current field | Prior company / role | Financing / valuation | Source status | Inclusion reason |
|---|---|---|---|---|---|

Wait for confirmation or correction when the pool is uncertain or when names the reviewer supplied are central.

### Checkpoint 3 - Classification Definitions

Define each non-obvious label in reader-facing language:

- what it covers;
- typical companies or roles;
- the transferable capability it represents;
- how it differs from neighbouring categories.

Do not use internal shorthand such as `大厂产品平台` without a definition.

### Checkpoint 4 - Style Samples

Provide 2-3 sample profile paragraphs before full drafting. Each profile follows:

```text
prior experience -> current project -> latest progress -> source status / unknowns
```

Default tone: neutral facts. No praise, success prediction or investment recommendation unless asked.

### Checkpoint 5 - Draft And Visualize

After confirmation, write:

1. Summary with counts and percentages computed from the final bottom table.
2. Screening and sorting logic.
3. The big table.
4. Profile sections.
5. Source and DD-status appendix.
6. For HTML or charts: insight first, then chart evidence, with hover or click exposing sample names, projects, financing / valuation and source status.

## Correction Trigger

If the reviewer says any of:

- `不是`
- `你需要先`
- `不要`
- `先和我确认`
- `理解错了`
- `不是这个意思`
- `这个太散`
- `不要下判断`
- `先给 insight`

then stop drafting and respond with:

```markdown
## Correction Capture

- You corrected: [specific constraint]
- Updated understanding: [new task boundary]
- I will now return to checkpoint: [1/2/3/4/5]
- Next artifact: [Task Packet / sample pool / category definitions / sample paragraph / revised output]
```

Do not continue the old trajectory after a correction trigger. `irh correction "<feedback>"` maps a piece of feedback to its signal and checkpoint.

## Visualization Gate

Before finalizing an HTML page or chart:

- state the claim above the chart;
- state the sample base and the metric's meaning;
- check that labels are readable and categories are defined;
- compute counts from the final data table;
- make hover or click show the underlying samples when possible.
