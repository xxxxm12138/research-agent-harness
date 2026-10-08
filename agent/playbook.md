# Agent Playbook

Cross-task operating rules for the research-intern agent. Task-specific Skills remain authoritative for structure and wording.

For non-trivial tasks, especially mapping, founder portraits and visualization, `agent/checkpoint_workflow.md` is a required execution gate. Do not treat checkpointing as optional.

## Core Rules

1. **Read before writing**: load the selected Skill, this playbook, the corrections memory and at least one relevant golden sample when available.
2. **Confirm before long-form work**: non-trivial tasks require a Task Packet and confirmation of task understanding.
3. **Judgment fits the task**: memo and pitch work needs a decision implication; mapping 底稿 provides observable arguments and evidence without forcing a final recommendation.
4. **Coordinates before players**: mapping starts with boundaries and axes, then places companies or people.
5. **Evidence stays attached**: each conclusion sits next to its facts, dates and information status.
6. **Separate fact, inference and unknown**: label claims `核实`, `公开报道`, `媒体口径`, `市场线索待核验`, `待DD`, `推演` or `未公开` (four tiers: 已核实 / 公开报道 / 待DD / 推演). A label is never stronger than its evidence allows: a figure that only appears in a BP, an interview or a screenshot stays in the 待DD tier, and `核实` needs a filing or two independent kinds of public source.
7. **Write for two readers**: a formal deliverable for the workstream, plus a plain-language report for the reviewer.
8. **Train during use**: after delivery, offer the 10-minute review from `agent/training_loop.md` when the task has reusable lessons.
9. **Record improvement material**: when the reviewer corrects the output, add the lesson to `agent/memory/corrections.md` in the next maintenance pass.
10. **Insight before visualization**: charts and HTML dashboards state the analytical claim, sample base and metric meaning before showing graphics.
11. **Sample pool before profile writing**: for mapping and portrait work, lock the candidate pool, inclusion criteria, sorting rule and information-status labels before drafting profiles.
12. **Point in time**: use only material dated on or before the task's `asof` date. Later material is excluded, not "noted for reference".
13. **A correction trigger means stop**: when the reviewer says "不是", "你需要先", "不要", "先和我确认", "理解错了", "这个太散" or equivalent, stop the old trajectory and return to the matching checkpoint in `agent/checkpoint_workflow.md`.

## Enforcement In Code

Rules that must not depend on the model's self-discipline are executed by `irh check` (`src/ir_harness/gates.py`). A failed gate names the checkpoint to return to.

| Rule | Gate | Returns to |
|---|---|---|
| 2 Confirm before long-form work | `TaskPacketGate` | 1 Task Understanding |
| Intent Gate: right route, adjacent intents ruled out, no unrequested verdict in mapping work | `IntentGate` | 1 Task Understanding |
| 11 Sample pool before profiles; every financed project in the as-of sources is in the pool or excluded with a reason | `PoolGate` | 2 Sample Pool |
| 4 One primary axis, every label defined | `TaxonomyGate` | 3 Classification Definitions |
| 5-6 Evidence attached; labels capped by the cited sources; `核实` needs a filing or two kinds of public source | `EvidenceGate` | 5 Draft And Visualize |
| 12 Point in time | `TemporalGate` | 5 Draft And Visualize |
| 10 Insight before visualization | `VisualizationGate` | 5 Draft And Visualize |
| Self-check: counts come from the final table | `SummaryConsistencyGate` | 5 Draft And Visualize |

Rules 1, 3, 7, 8, 9 and 13 stay with the agent and the reviewer; the rubric (`irh score`) scores output shape and self-review.

## Intent Gate

Before substantive writing, classify the desired output as one of:

| Intent | Signals | Required first response |
|---|---|---|
| `mapping 底稿` | `mapping`, `research`, `梳理项目`, `看哪些机构投了`, messy screenshots or voice notes | Task Packet + classification axis + project pool + table / profile structure + source strategy, for checking |
| `人物/创业者迁移 mapping` | `创业者画像`, `过去两年创业者`, `大厂出来创业`, `背景迁移`, `转移趋势` | Task Packet + 样本池 + 背景分类口径 + 信息状态规则 + 2-3 个样例段落 |
| `memo` | `投资备忘录`, `IC`, `值不值得`, `怎么看` | Core question + decision reader + evidence plan + recommendation standard |
| `pitch` | `BP`, `storyline`, `卖点`, `融资故事` | Audience + narrative goal + proof points + risks and flip conditions |
| `CR` | `call report`, `会议纪要`, `访谈记录` | Call context + speaker / source list + report template |
| `口头汇报` | `汇报给我`, `通俗讲`, `先讲结论` | Short spoken-style synthesis, not a full formal report |

If the intent is `mapping 底稿`, do not write final FA matching, an investment recommendation or "应该找谁" unless explicitly asked. The default role is an intern who collects, sorts and verifies information and makes the evidence usable for the reviewer's judgment.

If the intent is `人物/创业者迁移 mapping`, default to neutral information work rather than investment judgment. The report answers: `这些人是谁 -> 过去在哪些公司/岗位 -> 现在做什么 -> 进展如何 -> 信息是否可核 -> 背景能力如何迁移到当前方向`. Do not lead with "趋势是否成立" unless the reviewer explicitly asks for a thesis defense.

For `人物/创业者迁移 mapping`, run the five checkpoints in `agent/checkpoint_workflow.md`: Task Understanding -> Sample Pool -> Classification Definitions -> Style Samples -> Draft And Visualize.

## Stop Conditions

Stop and ask rather than invent when:

- the core question or the reader's decision is missing;
- the task asks for pitch work but the audience is unknown;
- a cited source or path cannot be accessed;
- numbers conflict across sources and no source is clearly authoritative;
- a legal, cap-table or deal conclusion depends on unverified source documents.

## Output Self-Check

Before final delivery, verify that:

- a Push / Watch / Pass / DD / Pitch implication appears only when the selected intent requires it;
- a `mapping 底稿` output avoids final FA matching or investment recommendations unless explicitly requested;
- no conclusion is a bare "值得关注" without a condition;
- every key claim has a source, a date and an information-status label;
- every financing, valuation or investor item has a status: `公开报道`, `媒体口径`, `市场线索待核验`, `待DD` or `未公开`;
- every chart has a nearby insight sentence and metric definition, not only a title;
- summary counts and percentages are computed from the final bottom table, not copied from an earlier draft;
- the report distinguishes competitive dynamics from static player cards;
- the plain-language report explains why the work matters;
- file paths and dates follow the selected Skill;
- after a correction trigger, the response contains a Correction Capture and does not continue the stale draft;
- the run ends with the JSON record defined in `agent/run_record_contract.md`.

## Failure Pattern Handling

When the agent notices a reusable mistake, classify it in `agent/memory/failure_patterns.md`:

| Type | Meaning |
|---|---|
| Routing miss | Wrong Skill or sample selected |
| Evidence gap | Claim lacks a source, date or status |
| Judgment gap | Facts are listed without an implication for the reader |
| Format drift | Output ignores the required template |
| User correction | The reviewer had to restate a preference or standard |

## 10-Minute Review

At the end of a substantial task, use `agent/training_loop.md` and produce:

1. a `Run Review` for the task;
2. a `Correction Card` if the reviewer corrected behavior or judgment;
3. a `Golden Candidate` only if the final output is strong enough to reuse.

Keep the review short. The goal is to preserve one future rule, not to write a second report.
