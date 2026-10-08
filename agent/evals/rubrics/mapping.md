# Rubric: Mapping

Score each dimension from 0 to 2. `irh score` scores six dimensions from the run record by rule; Judgment quality needs an LLM judge or a human reviewer and stays pending until one is supplied (`--judge "Judgment quality=2"`).

| Dimension | 0 | 1 | 2 |
|---|---|---|---|
| Route selection | Wrong Skill or no Skill | Correct main Skill, missing support Skill or sample | Loads `research-mapping`, the relevant support Skill and a golden sample |
| Task Packet | Missing or generic | Captures the task but misses the decision or evidence standard | Captures background, core question, decision, deliverables, evidence standard, paths and flip conditions |
| Coordinate system | Starts with a player list | Has axes, but they do not lead or do not drive judgment | Defines boundary, primary axis and category definitions before placing players |
| Evidence binding | Claims without sources | Some claims have sources and status labels | Key claims carry source, date and an origin-consistent status, and separate fact from inference |
| Judgment quality | Information summary only | Some "so what", weak flip conditions | Clear implication for the reader's decision, next action and observable flip conditions; for mapping 底稿, observable arguments without an unrequested verdict |
| Output shape | One report only | Formal output plus a partial summary | Formal deliverable plus a plain-language report for the reviewer |
| Self-improvement | No reflection | Mentions generic gaps | Names concrete missing evidence, a Skill gap or a memory-update candidate |

## Pass / Fail

- `12+`: Pass.
- `9-11`: Borderline; revise before delivery.
- `<9`: Fail; reroute and rewrite the Task Packet.

While Judgment quality is pending the verdict is `provisional`, unless the rule-scored total alone already passes or cannot reach the borderline band.

## Required Checks

The output must explicitly answer:

1. What is this track or project, and what is it not?
2. Which axes separate winners, substitutes and irrelevant comparables?
3. What would make the reader Push, Watch or Pass?
4. What evidence would change that stance?
5. What should be recorded for future agent improvement?
