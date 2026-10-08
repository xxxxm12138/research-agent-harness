# Skills（方法层）

`skills/` is the executable method layer for the research-intern agent. Route through `agent/router.md` first (or `irh route "<task>"`), then read the required Skill files here. Each Skill has a frontmatter `name` / `description`, hard rules (铁律) and a common-mistakes table.

| Skill | Path | Trigger | Input | Output |
|---|---|---|---|---|
| style-replication 工作风格画像 | `skills/style-replication/SKILL.md` | always loaded | task context | style and quality bar |
| thinking-style-recognition 提问风格识别 | `skills/thinking-style-recognition/SKILL.md` | always loaded; repeated "why", corrections, calibration | questions and correction signals | intent inference and response boundary |
| research-mapping 投研 Mapping | `skills/research-mapping/SKILL.md` | mapping, research, 项目池, 机构画像, Pitch 前研究, BP 卖点 | messy task input, track / project context | mapping 底稿, BP storyline draft |
| track-analysis 赛道分析方法论 | `skills/track-analysis/SKILL.md` | 赛道分析, 竞争格局, 投资备忘录 | track question and evidence | track report or investment memo |
| founder-diligence 人物背调 | `skills/founder-diligence/SKILL.md` | 背调, 人物画像, 学术尽调, 团队评估 | person / team public material | 人物画像 + interview questions |
| call-report Call Report 写作规范 | `skills/call-report/SKILL.md` | call report, 会议纪要, 访谈记录 | transcript or notes | standard Call Report |
| deal-screening 项目筛选 | `skills/deal-screening/SKILL.md` | /screen, 值不值得看 | project facts and track context | Push Forward / Watch / Pass + next action |
| deal-modeling 交易建模 | `skills/deal-modeling/SKILL.md` | cap table, 估值模型, 股权结构 | legal documents, term sheet | Excel model or calculation note |
| landscape-visualization 市场格局可视化 | `skills/landscape-visualization/SKILL.md` | 市场格局图, 机构-项目统计图 | mapping bottom table (CSV) | multi-panel PNG / interactive HTML |
| narrative 叙事框架 | `skills/narrative/SKILL.md` | pitch, 叙事, 对外材料 | message and audience | narrative outline |
| thinker 磨刀石 | `skills/thinker/SKILL.md` | 质疑判断, 魔鬼拷问, ADAS | evidence and an initial hypothesis | internal critique (not usually delivered) |

## Usage Rules

1. Do not choose a Skill by filename alone; route through `agent/router.md`.
2. For mapping, load `research-mapping`, `track-analysis`, the always-load style files and the golden registry.
3. For judgment-heavy work, run `thinker` internally before final claims.
4. For deal or cap-table work, read the source legal documents first; confidential material never enters this repository.
5. If a Skill and `agent/memory/corrections.md` conflict, the correction memory wins unless the reviewer says otherwise.
6. Every path a Skill references must exist; `irh validate` checks this.
