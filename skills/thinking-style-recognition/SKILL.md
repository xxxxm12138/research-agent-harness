---
name: thinking-style-recognition
description: Use when working with the reviewer on research, mapping, agent training, report revision or iterative correction, especially when they ask repeated "why / how / what is the logic" questions, challenge classifications, ask to confirm understanding, or expect the agent to infer intent from feedback.
---

# Thinking Style Recognition

Use this skill to infer the reviewer's real intent from how they ask and correct. The goal is not to mimic a personality; it is to route the task correctly, ask fewer low-value questions and produce output closer to the reviewer's judgment standard. `irh correction "<feedback>"` implements the signal table below.

## Core Pattern

The reviewer's questions usually test the agent's **reasoning contract**, not just the current paragraph. "为什么", "你的逻辑是什么", "和我确认理解" or "这样分类严谨吗" is a signal to pause production and expose the underlying axis, scope, ranking rule or evidence standard.

## Question Signals

| Reviewer signal | What they are really checking | Agent response |
|---|---|---|
| `和我确认你的理解` / `先给我 check` | Whether the task frame is right before writing | Output only structure, assumptions, sample rows or 2-3 examples. Do not write the full report. |
| `为什么这么分` / `这个分类严谨吗` | Whether the classification axis is single, useful and non-overlapping | State the primary axis, explain boundaries, handle edge cases, then ask for confirmation if still ambiguous. |
| `为何没有 X` / `凡是拿到融资的都列` | Whether the project pool is complete before prioritization | Stop profile writing. Produce or update the project pool, inclusion criteria, source status and sorting rule. |
| `我不需要给自己的判断` / `我是实习生` | Whether the output boundary is information work rather than a final recommendation | Remove the final FA / investment recommendation. Use `可观察到`, `公开报道显示`, `待DD`. |
| `像之前那份 Mapping` / `按照这个示例` | Whether the output should follow an existing structural grammar | Reuse the example's structure and tone: classification, big table, institution and project profiles, sources. |
| `这个图是什么意思` / `为什么没放 X` | Whether the visualization logic is explainable and complete | Add metric definitions, inclusion rules, labels and the cases the reviewer cares about; fix readability. |
| `联网核验` / `标注来源` | Whether facts are DD-ready | Verify public facts; mark screenshot or uncertain claims as `用户截图线索，待DD`; put sources at the end. |

## Thinking Style

- They work by **反复收紧边界**: start broad, challenge categories, remove overlap, then lock a usable axis.
- They prefer **先底表后结论**: project pool, table fields, sorting rules and source status exist before polished prose.
- They ask for **examples as tests**: "先写 2 个我看看" means a calibrated sample, not the whole section.
- They treat charts as **analysis surfaces**: every color, number, filter and omission needs a reason.
- They distinguish **research整理** from **judgment输出**: unless explicitly asked, the agent does not finish with "应该投 / 应该找谁".
- They value **口径比格式更重要**: a beautiful report with a weak taxonomy is wrong.
- They use corrections as **training data**: repeated corrections become future rules, not one-off edits.

## Default Response Strategy

1. Identify whether the reviewer is asking for production, calibration or correction.
2. For calibration or correction, answer the underlying logic first: axis, scope, sorting, source standard or output boundary.
3. For production, still surface the Task Packet for non-trivial work before drafting.
4. Keep the language close to intern research: concrete, structured, source-aware and restrained.
5. When unsure, prefer a small checkable artifact over a long polished draft.

## Avoid

- Defending a prior structure after the reviewer questions its logic; re-evaluate the axis instead.
- Answering only the literal surface issue when the question points to a deeper routing problem.
- Inventing a final opinion to make the output feel complete.
- Hiding uncertain facts inside confident prose.
- Asking broad "what do you want" questions when a reasonable checkable artifact can be produced instead.
