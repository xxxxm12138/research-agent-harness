# Run Logs

Curated run notes for agent tasks that should become training material. Raw `irh run` outputs go to the top-level `runs/` folder, which is gitignored; only reviewed, de-identified logs belong here.

Create a run log when:

- the task received meaningful corrections;
- the output was scored with a rubric;
- the task might become a golden sample or an eval case;
- the route was ambiguous and the final route is worth preserving.

## Naming

`YYYY-MM-DD-{task-slug}.md`

## Suggested Contents

```markdown
# Run: [task] - [YYYY-MM-DD]

## Input

## Selected Route

## Files Read

## Output Paths

## Gate Result (`irh check`)

## Rubric Result (`irh score`)

## Run Review

- Route:
- Score:
- Best part:
- Main miss:
- Next rule:

## Corrections

## Correction Cards

- Trigger:
- Correction:
- Future rule:
- Applies to:

## Golden Candidate

- Input:
- Final output:
- Why golden:
- Reuse for:

## Reusable Lessons
```

Never log confidential deal terms, real company data from non-public material, or personal information here. Logs in this folder are published with the repository.
