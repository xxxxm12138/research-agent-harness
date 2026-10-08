# Agent Evals

Good research behaviour turned into repeatable checks. This is not a fine-tuning system: it is a sample + rubric + correction loop, and its artifacts are the raw material a benchmark or post-training set would be built from (`docs/benchmark-alignment.md`).

## v1 Evaluation Target

Mapping is the first target because it best reflects the reviewer's quality bar:

- build the coordinate system first;
- place players after the map exists;
- bind judgment to evidence;
- explain the "so what" for a real pitch or DD decision;
- produce both a formal output and a plain-language report.

## Layout

| Path | Content |
|---|---|
| `cases/` | Eval cases: a messy real-world input, the expected route and first response, passing signals, fail conditions. Each case has a machine-checkable expectation table that the test suite verifies against the router |
| `rubrics/` | 0-2 scoring rubrics parsed by `irh score` |

## How To Run

Manually:

1. Pick a case from `cases/`.
2. Give the case input to the research-intern agent.
3. Require a Task Packet, a task-confirmation message, a self-check, an output outline and the run record.
4. Run `irh check <run.json> --sources <sources.json>` for the process gates.
5. Run `irh score <run.json>` for the rubric (pass a judge score for Judgment quality).
6. Record recurring misses in `agent/memory/failure_patterns.md`.

Through Pi, `irh run "<case input>" --asof <date> --model <provider/model>` does steps 2-4 in one go, so the same case can be replayed across models.

## Training Effect Tests

Use these after several real tasks:

| Scenario | Test | Passing signal |
|---|---|---|
| 少问测试 | Give a task similar to a prior mapping task | The agent reuses correction memory and asks fewer low-value questions |
| 路由测试 | Give mixed input: `背调 + mapping + BP 卖点` | The agent orders the subtasks and selects the right Skills |
| 质量测试 | Score real mapping tasks with the rubric | Three consecutive real tasks score `12+` |
| 意图识别测试 | Run `cases/mapping_intent_messy_input.md` | The agent identifies `mapping 底稿`, confirms classification, pool and source strategy first, and avoids a final recommendation |
| 创业者画像迁移测试 | Run `cases/founder_migration_intent.md` | The agent identifies `人物/创业者迁移 mapping`, runs the checkpoints, confirms the sample pool and taxonomy first, and avoids a premature trend proof |
| 任务拆解测试 | Run `cases/pitch_mapping_decomposition.md` | The agent decomposes a messy pitch-prep request into a Task Packet and a priority order before writing |

## Pass Bar

For v1, an output passes when:

- no required route or Skill is missed;
- the Task Packet captures the decision, deliverables, evidence standard and flip conditions;
- the report outline follows the selected Skill;
- all process gates pass;
- the self-check names at least the main uncertainty and the next evidence gap.
