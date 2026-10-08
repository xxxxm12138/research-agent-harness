# Training Loop: 边使用边训练

How the reviewer trains the research-intern agent during real work. This is not model fine-tuning: it is a repeatable loop of task -> output -> 10-minute review -> correction memory / run log / golden candidate. The same artifacts are exactly what a post-training pipeline would consume later (see `docs/benchmark-alignment.md`).

## Goal

Train the agent to "少问也懂我":

1. infer task intent from repeated patterns;
2. ask fewer low-value clarification questions;
3. preserve the reviewer's judgment preferences;
4. improve report quality through golden samples and rubrics;
5. turn corrections into future rules.

## The Four-Step Use Loop

### 1. Task Start: Task Packet First

For every non-trivial task, the agent must:

- read `agent/router.md`, `agent/playbook.md` and `agent/memory/corrections.md`;
- select the required Skill files and golden samples;
- produce a Task Packet before long-form writing;
- ask the reviewer to correct only the 1-3 highest-impact items.

The reviewer corrects decision-critical fields first:

- core question;
- reader and decision context;
- deliverable type;
- evidence standard;
- route or required sample.

### 2. During Work: Turn Corrections Into Training Signals

The most useful correction format is:

```text
这不是我要的，因为 X；下次遇到 Y 时先做 Z。
```

The agent treats this as a future memory candidate, not only a local rewrite instruction.

### 3. Task End: 10-Minute Review

After delivery, produce a short review with three outputs:

1. one thing that matched the reviewer's style or judgment;
2. one correction that should change future behavior;
3. one reusable next rule.

Use the cards below. Do not over-review ordinary tasks.

### 4. Weekly Promotion: Convert Work Into Training Assets

Once a week, review recent run logs:

- promote one excellent run to `agent/golden/`;
- promote one representative failure to `agent/evals/cases/`;
- merge repeated corrections into `agent/playbook.md` or the relevant `skills/*/SKILL.md`.

Only high-value tasks become golden samples. Ordinary tasks leave only a correction or a failure pattern.

## Feedback Cards

### Correction Card

Use when the reviewer corrects the agent's behavior or judgment. `ir_harness.corrections.append_card` writes this format.

```markdown
## Correction Card

- Trigger:
- Correction:
- Future rule:
- Applies to:
```

`Applies to` takes one or more of: `Mapping`, `人物背调`, `赛道分析`, `可视化`, `项目筛选`, `CR`, `交易建模`, `叙事`, `all`. The tag decides which future tasks load the card: each route in `agent/router.md` lists the tags it loads, and `all` loads everywhere. Tag narrowly; an over-broad `all` puts the rule into every context window.

### Run Review

Use after a delivered task when the reviewer has 10 minutes for feedback.

```markdown
## Run Review

- Route:
- Score:
- Best part:
- Main miss:
- Next rule:
```

`Score` uses the matching rubric when available; for mapping work, `irh score` applies `agent/evals/rubrics/mapping.md`.

### Golden Candidate

Use only when the final output is strong enough to teach future agents.

```markdown
## Golden Candidate

- Input:
- Final output:
- Why golden:
- Reuse for:
```

## Test Scenarios

Use these scenarios to check whether training is working:

| Scenario | Test | Passing signal |
|---|---|---|
| 少问测试 | Give a task similar to a prior mapping task | The agent reuses correction memory and asks fewer low-value questions |
| 路由测试 | Give mixed input: `背调 + mapping + BP 卖点` | The agent orders the subtasks and selects the right Skills |
| 质量测试 | Score real mapping tasks with the rubric | Three consecutive real tasks score `12+` |

## Promotion Rules

| Input | Destination | Condition |
|---|---|---|
| Reviewer correction | `agent/memory/corrections.md` | Stable preference or repeated correction |
| Repeated miss | `agent/memory/failure_patterns.md` | The same failure appears twice or is high-risk |
| Strong completed task | `agent/golden/` | Reusable structure, judgment and evidence quality |
| Representative failure | `agent/evals/cases/` | Useful to prevent future regressions |
| Repeated rule | `agent/playbook.md` or the relevant Skill | Applies across many future tasks |

## Default Budget

`10 分钟标准反馈`:

- 2 minutes: route and Task Packet check;
- 4 minutes: rubric score and main miss;
- 2 minutes: correction card;
- 2 minutes: decide whether to create a run log, golden sample or eval case.
