# Run Record Contract

Every run ends with one fenced `json` block that follows this contract. The prose report is for people; the run record is for checking. `irh check` runs the process gates on it, `irh score` scores it against the route's rubric, and `irh run` extracts the last `json` block of the model's output automatically.

Write the record from what the report actually contains. A record that claims more than the report delivers is a fabrication, and reviewers spot-check it against the prose.

## Fields

| Key | Type | Meaning | Checked by |
|---|---|---|---|
| `task` | string | The task as given | — |
| `asof` | `YYYY-MM-DD` | Decision date; nothing published later may be used | `TemporalGate` |
| `route` | string | Route id from `agent/router.md` | `IntentGate` |
| `intent` | string | Intent label of that route, e.g. `mapping 底稿` | `IntentGate` |
| `intent_excludes` | list of strings | Adjacent intents the Intent Gate ruled out ("it is not ..."); must cover the route's `Not` column | `IntentGate` |
| `loaded_files` | list of paths | Rules, skills and golden samples actually read | rubric: Route selection |
| `task_packet` | object | Keys: `background`, `core_question`, `reader_decision`, `deliverables`, `required_methods`, `evidence_standard`, `output_path`, `flip_conditions`, `confirmation`. Values are strings or lists of strings | `TaskPacketGate`, rubric |
| `taxonomy.primary_axis` | string | The single primary classification axis | `TaxonomyGate` |
| `taxonomy.categories` | list of `{name, definition}` | Every category, defined in reader-facing language | `TaxonomyGate` |
| `pool` | list of `{name, category, inclusion_reason, source_status}` | The project or sample pool, i.e. the final bottom table | `PoolGate`, `SummaryConsistencyGate` |
| `pool_locked` | bool | The pool was confirmed before profiles were written | `PoolGate` |
| `excluded_from_pool` | list of `{name, reason}` | Projects deliberately left out, each with a reason | `PoolGate` (coverage) |
| `profiles` | list of names | Entities that received a profile section | `PoolGate` |
| `sections` | list of strings | Section titles in report order | rubric: Coordinate system, Output shape |
| `claims` | list of `{text, origin, status, source_id or source_ids, kind}` | Key claims; see origins and statuses below | `EvidenceGate`, `TemporalGate` |
| `charts` | list of `{title, claim, metric_definition, sample_base}` | Every chart or HTML panel | `VisualizationGate` |
| `summary` | `{n_projects, by_category}` | Counts as printed in the report's summary | `SummaryConsistencyGate` |
| `plain_language_report` | bool | A plain-language report for the reviewer was written | rubric: Output shape |
| `final_recommendation` | bool | The output contains a final investment / FA recommendation | `IntentGate` |
| `recommendation_requested` | bool | The reviewer explicitly asked for one | `IntentGate` |
| `self_review` | `{missing_evidence, skill_gaps, memory_candidates, notes}` | Concrete gaps and memory candidates, each a list of strings | rubric: Self-improvement |

## Sources

The sources file given to `irh check` / `irh run` lists every document the task may use:

```json
{"id": "S-01", "title": "...", "origin": "news", "published": "2026-07-12", "ref": "...", "entities": ["星芽"], "event": "financing"}
```

- `published` decides admission: later than `asof` and the source is excluded from the workspace the model sees; `null` is admitted and flagged as undated.
- `entities` + `event: "financing"` drive the pool-coverage check: every project with a financing event in the admitted sources must be in `pool` or in `excluded_from_pool` with a reason. This is how early-stage projects that only appear in screenshots, interviews or BPs stop being silently dropped.
- A source's `origin` must name the document type (`news`, `official`, `filing`, `bp`, ...). `verified` is not a document type and gives no support on its own.

## Origins And Information Status

`origin` says where a claim comes from; `status` is the label printed in the report. The code caps the status at what the origin can justify, and `EvidenceGate` fails any claim whose asserted label had to be downgraded.

| Origin | Default status | Strongest allowed |
|---|---|---|
| `filing`, `registry`, `verified` | 核实 | 核实 |
| `news`, `official`, `paper` | 公开报道 | 公开报道 |
| `media` | 媒体口径 | 媒体口径 |
| `screenshot`, `rumor` | 市场线索待核验 | 市场线索待核验 |
| `bp`, `founder_claim`, `interview` | 待DD | 待DD |
| `inference` | 推演 | 推演 |
| anything else | 待DD | 待DD |

A weaker label is always allowed (for example `未公开` on an `official` source that does not disclose an amount). `kind` is `fact` (the default; needs a `source_id` or `source_ids`), `inference` or `unknown`.

With a sources file, the label is also checked against the sources the claim actually cites, so a claim cannot raise its label by declaring a stronger `origin` than its evidence:

- one cited source supports at most its own origin's ceiling (a BP stays `待DD` whatever the claim says);
- **cross-verification**: `核实` needs a `filing` / `registry` source, or two or more *different kinds* of public source (`news`, `official`, `paper`) that agree. Two news stories alone stay `公开报道`, since they often copy one press release.

The seven labels fold into four tiers: 已核实 (`核实`) / 公开报道 (`公开报道`, `媒体口径`) / 待DD (`待DD`, `市场线索待核验`, `未公开`) / 推演 (`推演`).

## Minimal Example

```json
{
  "task": "帮我做 AI 陪伴硬件赛道的 mapping，看哪些机构投了",
  "asof": "2026-09-30",
  "route": "mapping",
  "intent": "mapping 底稿",
  "intent_excludes": ["memo", "投资建议", "FA 匹配"],
  "loaded_files": ["skills/research-mapping/SKILL.md", "skills/track-analysis/SKILL.md", "agent/golden/mapping.md"],
  "task_packet": {
    "core_question": "AI 陪伴硬件按用户付费价值可分为哪几类，各类有哪些已融资项目与参与机构？",
    "reader_decision": "决定下一步对哪一类项目做 DD",
    "deliverables": ["Mapping 底稿", "给 reviewer 的通俗汇报"],
    "evidence_standard": "融资信息须有公开来源；BP 与访谈口径标待DD",
    "flip_conditions": ["某一类出现可核实的规模化出货数据"]
  },
  "taxonomy": {
    "primary_axis": "用户为之付费的核心价值",
    "categories": [{"name": "情感陪伴", "definition": "用户为关系与情绪回应付费"}]
  },
  "pool": [{"name": "星芽", "category": "情感陪伴", "inclusion_reason": "已披露 Pre-A 融资", "source_status": "公开报道"}],
  "pool_locked": true,
  "excluded_from_pool": [],
  "profiles": ["星芽"],
  "sections": ["Summary", "分类口径与边界", "项目池与 Mapping 总表", "项目画像", "信息来源与核验状态"],
  "claims": [{"text": "星芽完成 Pre-A 轮融资", "origin": "verified", "status": "核实", "source_ids": ["S-01", "S-12"]}],
  "charts": [],
  "summary": {"n_projects": 1, "by_category": {"情感陪伴": 1}},
  "plain_language_report": true,
  "final_recommendation": false,
  "recommendation_requested": false,
  "self_review": {"missing_evidence": ["星芽出货量待 DD"], "skill_gaps": [], "memory_candidates": []}
}
```

A complete passing record and a deliberately failing one live in `examples/ai-companion-hardware/`.
