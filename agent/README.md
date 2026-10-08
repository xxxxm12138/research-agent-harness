# Agent OS

`agent/` is the control layer of the harness. It does no research itself: it tells the research-intern agent how to use the method layer in `skills/`, and the parts that must not depend on the model's self-discipline are executed by code in `src/ir_harness/`.

## Purpose

Train the research-intern agent toward a reviewer's quality bar through repeated interaction:

1. route messy tasks to the right method;
2. read the required Skill and golden samples before writing;
3. create a Task Packet before non-trivial work;
4. evaluate output against rubrics;
5. record corrections and failure patterns for future runs.

## Directory Map

| Path | Role | Used by |
|---|---|---|
| `router.md` | Task signal -> Skill -> golden sample -> rubric -> output | agent; parsed by `irh route` |
| `playbook.md` | Cross-task rules, Intent Gate, stop conditions, self-check | agent; enforced by `irh check` |
| `checkpoint_workflow.md` | Five checkpoints, Correction Capture, Visualization Gate | agent; gate failures point back here |
| `training_loop.md` | Use-time training loop and feedback cards | agent and reviewer |
| `task_packet_template.md` | Intake format before substantive work | agent; checked by `TaskPacketGate` |
| `run_record_contract.md` | The JSON record every run emits | agent; parsed by code |
| `golden/` | Registry of high-quality reference outputs by route | agent |
| `evals/` | Re-runnable eval cases and rubrics | reviewer; scored by `irh score` |
| `memory/` | Corrections, judgment preferences, failure patterns | agent (always loaded) |
| `runs/` | Curated run logs that may become eval cases or golden samples | reviewer |
| `subagents/` | The research-intern subagent definition | Claude Code / Cursor / Pi |

## Operating Contract

For non-trivial research tasks, the agent must:

1. read this README, `router.md`, `playbook.md` and `memory/corrections.md`;
2. select the task route and the required Skill files;
3. read at least one relevant golden sample when available;
4. produce a Task Packet and confirm task understanding;
5. write the formal output and a plain-language report;
6. emit the run record and self-check against the matching rubric;
7. run the 10-minute review in `training_loop.md` when the reviewer has feedback;
8. note any reusable correction or failure pattern.

## What Code Enforces

| Stage | Markdown source | Code | Command |
|---|---|---|---|
| Routing | `router.md` | `router.py` | `irh route` |
| Workspace assembly and point-in-time freeze | `router.md` (Always Load, Routes) | `workspace.py` | `irh assemble` |
| Information status | `playbook.md` rule 6, `run_record_contract.md` | `provenance.py` | used by `irh check` |
| Process gates | `playbook.md`, `checkpoint_workflow.md` | `gates.py` | `irh check` |
| Rubric scoring | `evals/rubrics/*.md` | `rubric.py` | `irh score` |
| Correction signals | `checkpoint_workflow.md`, `memory/corrections.md` | `corrections.py` | `irh correction` |
| Model execution | everything the route selects | `pi_runner.py` | `irh run` |
