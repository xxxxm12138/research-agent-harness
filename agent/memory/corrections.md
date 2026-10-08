# Corrections Memory

Reviewer corrections that change future agent behavior. When entries conflict, the newest correction wins. Each dated entry ends with an `Applies to` tag; a task loads only the entries whose tags match its route (column `Corrections` in `agent/router.md`), plus every entry tagged `all`. New entries use the format at the end of this file (`ir_harness.corrections.append_card` writes it).

## Active Corrections

- Treat the research workspace as an AI-native environment whose purpose is to improve agent output quality, not as a tidy folder tree.
- When adding structure to an existing research workspace, add the control layer first. Do not move or rename existing folders in the first pass, so links, scripts and image references stay stable.
- "Training" means sample + rubric + correction memory + eval case for now; do not assume model fine-tuning.
- The research-intern subagent is the main entry point. `agent/` is its operating system and training environment.
- Use-time training follows the `10 分钟标准反馈` loop in `agent/training_loop.md`: a Run Review, a Correction Card when needed, and a Golden Candidate only for high-value outputs.
- The first training focus is "少问也懂我": reduce repeated clarification by preserving task intent, the reader's decision and correction rules.

### 2026-06-24 - Mapping output should be framework-first

- Trigger: The agent received a messy mapping task with screenshots, voice notes, one anchor financing case, and examples from another mapping report.
- Correction: Do not default to an investment memo or a single-company anchor report. When the reviewer asks for mapping, first confirm whether the desired artifact is a framework + table + case list.
- Future rule: For mapping reports, prefer `Summary -> Mapping 分类 -> one big table -> 机构画像 -> 项目画像` unless the reviewer explicitly asks for a memo, thesis or single-company conclusion. Keep cross-case judgment questions in the reviewer-facing briefing layer when the reviewer says they should not enter the formal report.
- Applies to: Mapping / 赛道分析

### 2026-06-24 - Mapping intent must be recognized before writing

- Trigger: The reviewer repeatedly corrected the agent during an AI 情绪经济 mapping task because the output drifted toward memo-like judgment, incomplete project selection and unclear classification logic.
- Correction: Treat `mapping / research / 梳理项目 / 看哪些机构投了` as a mapping 底稿 task by default. Identify the intended deliverable type before drafting.
- Future rule: Before any long-form output, classify the task as `mapping 底稿 / memo / pitch / CR / 口头汇报`. For mapping 底稿, produce Task Packet + 分类轴 + 项目池 + 样表 / 样例 + 来源策略 for the reviewer to check.
- Applies to: all

### 2026-06-24 - Classification needs one primary axis

- Trigger: The reviewer challenged overlapping categories such as AI 互动娱乐, AI 虚拟角色, hardware entry and content / production tools.
- Correction: Do not mix product form, technology route, financing stage, hardware form and user scenario in one taxonomy. Explain the chosen axis and handle edge cases explicitly.
- Future rule: For mapping classification, pick one primary axis. In the AI 情绪经济 case the accepted axis was `用户最终消费对象`: users consume either playable / remixable content units or a role / companionship / pan-psychology relationship. Hardware is an entry form, not a top-level category.
- Applies to: Mapping / 赛道分析

### 2026-06-24 - Project pool completeness comes before profile writing

- Trigger: The reviewer asked why several financed or reviewer-named projects were missing from the draft.
- Correction: Do not start detailed project profiles from a partial project list. Reviewer-named and financed projects first enter a project pool for checking.
- Future rule: For mapping work, first produce a project pool with inclusion reason, financing / source status and proposed category. Then write project profiles by category and sort within each category by disclosed financing amount where possible.
- Applies to: Mapping / 赛道分析

### 2026-06-24 - Institution portraits should be deal-led

- Trigger: The reviewer rejected broad institution write-ups and asked for each institution to be written through its related investments, amounts, process and logic.
- Correction: Do not write generic fund introductions unless they directly explain the relevant investment behavior.
- Future rule: Institution profiles contain only `机构属性`, `投资项目 - 金额`, `投资过程` and `可观察偏好`. Sort by fund scale, institution importance or an explicit reviewer-approved criterion. Avoid final FA matching unless asked.
- Applies to: Mapping

### 2026-06-24 - Visualizations must expose their analysis logic

- Trigger: The reviewer asked what an unlabeled `C` meant, why a group of relevant institutions was absent, and noted that dark text was unreadable on dark heatmap cells.
- Correction: Charts cannot be decorative or opaque. Labels, legends, inclusion rules and contrast must let a reader understand the analytical claim.
- Future rule: For market landscape charts, explain metric meaning and selection rules near the chart. Do not mechanically show only a Top 10 if that hides reviewer-relevant institutions; use a documented focus list when needed. Ensure high-contrast text on colored cells.
- Applies to: Mapping / 可视化

### 2026-06-24 - Sources and DD status must be explicit

- Trigger: The reviewer asked for online verification and source labels; many facts came from screenshots, voice notes or public reports of uneven reliability.
- Correction: Do not present screenshot leads, unverifiable financing or founder background as confirmed facts.
- Future rule: Public facts need source verification. Company self-reported data (BP, founder statements, interviews) is always labelled `待DD` until a third party confirms it; screenshot leads are `市场线索待核验`. Sources go in a final `信息来源与核验状态` appendix so the body stays readable.
- Applies to: all

### 2026-06-25 - Founder migration mapping must start with alignment and a sample pool

- Trigger: During a founder-background migration task, the agent began writing before aligning the deliverable, then needed repeated corrections on scope, sample list, tone, sorting logic and chart framing.
- Correction: For founder / people migration mapping, do not start by proving a trend or praising founders. First confirm the actual deliverable, then list and reconcile the people / project pool, inclusion threshold, sorting rule, geography and time range, and whether media rumors may be used.
- Future rule: Start with `任务需求确认 -> 样本池 -> 分类口径 -> 2-3 个样例画像 -> 确认 -> 正文/HTML`. Profiles follow the fact chain `创业前经历 -> 当前项目 -> 最新进展 -> 信息状态/待核验点`. Avoid final investment judgment unless asked.
- Applies to: Mapping / 人物背调 / 可视化

### 2026-06-25 - Mapping visuals need claims, not only charts

- Trigger: A founder-background HTML page first showed several charts without enough explanation; the reviewer asked for insight first, then chart evidence, with hover details for people, projects and financing.
- Correction: A visualization is not the deliverable by itself. It states the analytical claim, sample base, metric definition and what the reader should infer before showing the chart.
- Future rule: For HTML and chart outputs, order sections as `核心发现/统计口径 -> 底表 -> 图表证据`. Heatmaps, Sankey diagrams and matrices expose underlying samples on hover or click: names, projects, financing / valuation and source-status labels.
- Applies to: Mapping / 可视化

### 2026-06-25 - Background labels must be reader-legible

- Trigger: The label `大厂产品平台` was unclear and had to be rewritten as `大厂应用产品/平台型背景` with examples and boundaries.
- Correction: Classification labels cannot be internal shorthand. Name them in report language and define them with included examples and excluded neighbouring categories.
- Future rule: Every non-obvious category needs a short definition: what it covers, typical companies or roles, the capability it represents and how it differs from neighbouring categories.
- Applies to: Mapping / 人物背调 / 可视化

### 2026-08-31 - CR 正文不要写「会议称」

- Trigger: The reviewer corrected Call Report wording: CR 正文不要出现「会议称」.
- Correction: Do not use meta attribution such as `会议称`, `口述` or `待核` as asides in the CR body. Write the meeting facts as the report itself.
- Future rule: In Call Reports, state numbers, team, product and financing in declarative sentences without prefixes such as `会议称`. Flag conflicts between oral and public information only when asked, as a short factual contrast.
- Applies to: CR

## Format For Future Corrections

```markdown
### YYYY-MM-DD - [short title]

- Trigger:
- Correction:
- Future rule:
- Applies to:
```
