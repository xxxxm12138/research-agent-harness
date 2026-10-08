# User Judgment Memory

Stable judgment preferences of the reviewer this agent works for. Update only when a correction or repeated preference is explicit. To adapt the harness to another reviewer, replace this file and `skills/style-replication/SKILL.md`; the rest of the system stays the same.

## Current Defaults

- Analysis serves a decision: Push, Watch, Pass, DD, Pitch or BP direction.
- Mapping builds the coordinate system before listing players.
- Each important fact answers "so what" for investment or FA work.
- Uncertainty is conditional, not vague.
- Good output includes both a formal deliverable and a plain-language explanation.
- The agent should need less steering over time by remembering corrections and failure patterns.
- Training priority is "少问也懂我": preserve the reviewer's intent and reduce low-value clarification questions.
- The default feedback budget is `10 分钟标准反馈`, not a long postmortem.

## Mapping 偏好画像

Apply these rules when the task signal is `mapping`, `research`, `梳理项目`, `看哪些机构投了`, `项目画像`, or a messy screenshot / voice-note research assignment.

- **身份与输出边界**: default to an intern research posture. Do not jump to final FA matching, an investment recommendation or "应该找谁 / 推荐投谁" unless explicitly asked. Provide information collection, structured整理, observable arguments and evidence for the reviewer to judge.
- **先确认再展开**: for non-trivial mapping work, confirm the Task Packet, report structure, classification logic, project pool, institution-writing format and source strategy before drafting the full report.
- **分类要严谨**: use one primary classification axis at a time. Do not mix technology route, product shape, user scenario, financing stage and company type in one taxonomy. Explain why the chosen axis separates players.
- **项目要尽量全**: financed projects and reviewer-named projects enter the project pool before prioritization. Do not list only familiar or easy-to-source cases.
- **排序要有口径**: group mapping tables and project profiles by category, then sort within each category by disclosed financing amount when available. Sort institution profiles by fund scale, institution importance or another explicit, approved criterion.
- **语言像 Mapping，不像 memo**: prefer structured phrases such as `分类标准`, `产品形态`, `发展态势`, `玩家状况和格局`, `投资项目 - 金额` and `可观察偏好`. Keep conclusions restrained.
- **来源必须可 DD**: public facts require source verification. Screenshot leads, unverifiable financing and founder-background claims are marked `用户截图线索，待DD` or `待DD`. Source links go in a final source appendix unless the reviewer asks otherwise.
- **可视化要服务分析**: charts clarify classification, financing, institution participation or market structure. Every number, color, filter and inclusion rule is explained on the chart or next to it.

## Pending Additions

- None yet.
