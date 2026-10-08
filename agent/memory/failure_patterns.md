# Failure Patterns

Recurring agent misses. Convert repeated misses into playbook or Skill updates; when a pattern can be detected from the run record, add a gate or a rubric rule for it.

## Known Risk Patterns

| Pattern | Symptom | Prevention | Caught by |
|---|---|---|---|
| Route before context | The agent selects a Skill without checking task intent | Read `router.md`, then produce a Task Packet | `IntentGate`, rubric: Route selection |
| Report too early | Long-form output before confirmation | Confirm the Task Packet for non-trivial tasks | `TaskPacketGate` |
| Player list masquerading as mapping | Companies listed without axes | Force boundary and coordinate system first | `TaxonomyGate`, rubric: Coordinate system |
| Evidence-free judgment | Plausible claims without source, date or status | Attach evidence and status labels to key claims | `EvidenceGate` |
| Over-labelled evidence | A BP or interview figure presented as `核实` | Labels are capped by origin | `EvidenceGate` (downgrade) |
| Look-ahead leakage | A conclusion rests on material published after the decision date | Freeze the workspace at `asof` | `TemporalGate` |
| Generic conclusion | "值得关注" without a condition or next action | Require a Push / Watch / Pass / DD / Pitch implication where the intent needs one | rubric: Judgment quality |
| No learning loop | Corrections vanish after the task | Record reusable corrections here or in `corrections.md` | rubric: Self-improvement |
| Intent recognition by keyword only | The agent follows keywords but misses the correction trajectory or the real deliverable | Run the Intent Gate and checkpoint workflow; after a correction, emit Correction Capture and restart the checkpoint | `irh correction` |
| Founder profiles before sample pool | Portraits written before the people / project pool and information status were confirmed | Require the sample pool and category definitions first | `PoolGate`, `TaxonomyGate` |
| Decorative visualization | Charts appear before the insight, sample base, metric and underlying samples | Visualization Gate; hover or click exposes names, projects, financing and status | `VisualizationGate` |
| Stale summary counts | Summary numbers copied from an earlier draft | Recompute counts from the final table | `SummaryConsistencyGate` |

## New Pattern Template

```markdown
### YYYY-MM-DD - [pattern name]

- Seen in:
- What happened:
- Root cause:
- Prevention:
- Convert to playbook rule or gate? yes/no
```
