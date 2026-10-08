# Agent Router

Use this file before selecting any Skill. Match task signals to the narrowest route that covers the request. If several routes apply, run them in priority order and keep each output independently useful.

This file is executable: `irh route "<task>"` parses the tables below, and `irh validate` fails if any path in them does not exist. Change routing by editing this file, not the code.

## Always Load

| File | Why |
|---|---|
| `agent/playbook.md` | Global operating rules, Intent Gate and stop conditions |
| `agent/checkpoint_workflow.md` | Mandatory checkpoints for ambiguous mapping, founder and visualization tasks |
| `agent/memory/user_judgment.md` | Stable reviewer preferences and intent-recognition defaults |
| `agent/memory/corrections.md` | Reviewer corrections that override old habits |
| `skills/style-replication/SKILL.md` | The reviewer's work style and quality bar |
| `skills/thinking-style-recognition/SKILL.md` | Question style, correction signals and intent inference |

## Routes

Signals match case-insensitively as substrings. The route with the most matched signals wins; table order breaks ties, which encodes the priority rule for mixed tasks (people before maps, maps before memos). `Not` lists the adjacent intents the Intent Gate must explicitly rule out. `Corrections` lists the `Applies to` tags whose entries in `agent/memory/corrections.md` are loaded for the route (entries tagged `all` always load).

| Route | Intent | Not | Task signals | Required skills | Optional skills | Golden | Rubric | Corrections | Output |
|---|---|---|---|---|---|---|---|---|---|
| `founder` | 人物/创业者迁移 mapping | memo, 趋势论证, 投资建议 | 创业者画像, 创业者迁移, 大厂出来创业, 背景迁移, 转移趋势, 创始人背景 | `skills/research-mapping/SKILL.md` `skills/founder-diligence/SKILL.md` `skills/track-analysis/SKILL.md` | `skills/landscape-visualization/SKILL.md` | `agent/golden/mapping.md` | `agent/evals/rubrics/mapping.md` | `Mapping` `人物背调` `可视化` | Task Packet + 样本池 + 背景分类口径 + 总表 + 人物事实画像 + 信息状态附录 (+ insight-led HTML) |
| `founder_dd` | 人物背调 | 投资建议 | 背调, 人物画像, 人物背景, 学术尽调, 团队评估, 创始人尽调 | `skills/founder-diligence/SKILL.md` | `skills/thinker/SKILL.md` | — | — | `人物背调` | `{人名}人物画像-{MMDD}.md` + 访谈问题 |
| `mapping` | mapping 底稿 | memo, 投资建议, FA 匹配 | mapping, research, 梳理项目, 看哪些机构投了, 项目池, 机构画像, 市场格局, pitch 前, pitch前, 项目画像 | `skills/research-mapping/SKILL.md` `skills/track-analysis/SKILL.md` | `skills/landscape-visualization/SKILL.md` | `agent/golden/mapping.md` | `agent/evals/rubrics/mapping.md` | `Mapping` `赛道分析` `可视化` | Task Packet + 分类轴 + 项目池 + 总表 + 机构画像 + 项目画像 + 信息来源与核验状态附录 |
| `track_analysis` | 赛道研判 / memo | mapping 底稿 | 赛道分析, 赛道研判, 竞争格局, 投资备忘录, ic memo, 怎么看这个赛道 | `skills/track-analysis/SKILL.md` `skills/thinker/SKILL.md` | — | — | — | `赛道分析` | `{赛道}赛道分析-{MMDD}.md` 或投资备忘录 |
| `screening` | 项目筛选 | memo | 项目筛选, 值不值得看, 过一下这个项目, /screen | `skills/deal-screening/SKILL.md` | `skills/track-analysis/SKILL.md` | — | — | `项目筛选` | Push Forward / Watch / Pass + 下一步动作 |
| `call_report` | CR | memo, 投资建议 | call report, /cr, 写cr, 写 cr, 会议纪要, 访谈纪要, 访谈记录 | `skills/call-report/SKILL.md` | — | — | — | `CR` | 标准 Call Report |
| `deal_modeling` | 交易建模 | — | cap table, captable, 交易建模, 估值模型, 股权结构, 股权计算, 稀释 | `skills/deal-modeling/SKILL.md` | — | — | — | `交易建模` | Excel 模型或计算说明 |
| `narrative` | pitch / 叙事 | mapping 底稿 | pitch, bp 卖点, bp卖点, 融资故事, storyline, 叙事, 对外材料 | `skills/narrative/SKILL.md` | `skills/research-mapping/SKILL.md` | — | — | `叙事` | 叙事结构稿 / BP storyline |

## Route Rules

0. Run the Intent Gate in `agent/playbook.md` before route selection. `mapping 底稿` is not a memo and not a final investment recommendation.
1. Pitch-prep mapping is the first training route. Prefer it when the task asks to understand a deal, lab, founder or track before a meeting.
2. For mapping 底稿, confirm the classification axis, project pool, sorting rule, institution-writing format and source strategy before writing the full report.
3. For founder / people migration mapping, confirm the sample pool, inclusion threshold, geography and time range, background taxonomy, sorting rule and source-status labels before writing profiles. Offer 2-3 sample profile paragraphs for style confirmation.
4. Do not treat a report as a fact source unless its path is named in the Task Packet or registered in a golden registry.
5. Confidential deal material (BP decks, call reports, management-interview notes, cap tables, term sheets, recordings) may inform structure but is never quoted into shared outputs and never enters this repository. See `docs/research-compliance.md`.
6. If the route is still unclear after reading the prompt and the available context, ask one concise clarifying question before writing long-form output, offering the candidate intents (for example "看看这个赛道" could be a mapping 底稿, a memo or a 口头汇报). `irh route` raises `RoutingError` in exactly this case; `agent/evals/cases/ambiguous_intent.md` tests it.
7. If a route needs external data that is unavailable, state the gap and continue only with labelled information status.

## Required Confirmation For Non-Trivial Work

Before drafting a substantive report, produce a Task Packet with `agent/task_packet_template.md` and wait for confirmation unless the user explicitly skips it. `TaskPacketGate` rejects run records that have no Task Packet.
