# Changelog

## Unreleased

### Added

- README visuals in `assets/readme/`: hero, gate-check proof board, task pipeline and information-status ladder (static SVG, system fonts).

### Changed

- `irh validate` also checks the `src` / `href` targets of HTML tags in markdown, so README images cannot dangle.

## 0.1.0 — 2026-10-08

First public version, restructured from a private research workspace.

### Added

- **Control layer** (`agent/`): router table parsed by code (routes, adjacent intents to rule out, correction tags), playbook with an enforcement map, five-checkpoint workflow, Task Packet template, run-record contract, golden registry, four eval cases with machine-checkable expectations, mapping rubric, corrections / judgment / failure-pattern memory, research-intern subagent.
- **Method layer** (`skills/`): 11 skills. `research-mapping`, `founder-diligence` and `style-replication` were rewritten (v2) for publication from their templates, routing rules, corrections and eval cases.
- **Code layer** (`src/ir_harness`):
  - routing with a clarifying-question fallback;
  - point-in-time workspace assembly with route-filtered corrections, written to its own folder;
  - information-status labels in four tiers, capped by the cited sources, with a cross-verification rule;
  - eight process gates, including pool coverage and look-ahead checks;
  - rubric scoring with rule-scored and judge dimensions;
  - correction signals and correction-memory filtering;
  - pre-publication compliance scan;
  - Pi runner and the `irh` CLI.
- Fictional end-to-end example (`examples/ai-companion-hardware/`), docs, Pi adapter, CI on Python 3.10–3.12.

### Changed from the private workspace

- Real projects, people, institutions and deal figures replaced by fictional examples; firm-specific names removed.
- `track-analysis`: valuation example corrected (≈700x P/S, not 7000x PE) and a note on multiple conventions added.
- `landscape-visualization`: institution lists and map coordinates moved from code to a JSON config; HTML output escapes all data.
- `tools/docx_to_text.py`: rewritten on the standard library, keeping document order and tables.
- Third-party sources credited in `narrative` and `thinker`.
