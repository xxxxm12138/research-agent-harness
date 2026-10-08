# Call Report Skill Evals

Skill-level evals for `skills/call-report/SKILL.md`, run in the style of a skill-creator benchmark: each scenario feeds a transcript to the agent with the Skill loaded and checks the output against named assertions.

The original transcripts are confidential meeting material and are not included, so the iteration-1 results cannot be reproduced from this repository. What is kept is the eval design: the scenarios and the assertions they test. To rerun, write fictional or de-identified transcripts for each scenario.

## Scenarios

| Eval | Scenario | Assertions |
|---|---|---|
| `eval-1-angel-no-competition` | Angel-round company, competition not discussed in the meeting | `three_chapters`, `no_advantage_chapter`, `no_competitor_subsection`, `no_pmf_judgment`, `has_track_reference` |
| `eval-2-team-history` | Angel round, team spun out of a parent company; team history and financing must be consistent | `has_team_history`, `financing_zero_one`, `financing_delivery`, `no_year_by_year_cv` |
| `eval-3-a-round-competition` | A-round company with discussed competitors | Checks the five-chapter structure and the competition section (3 assertions; the original assertion file was not kept) |

## Iteration 1

| Eval | Passed | Total |
|---|---|---|
| `eval-1-angel-no-competition` | 5 | 5 |
| `eval-2-team-history` | 4 | 4 |
| `eval-3-a-round-competition` | 3 | 3 |

Assertions were checked automatically on the generated `cr-output.md`. A perfect pass rate on 12 assertions says the structure rules are followed; it says nothing about factual accuracy against the recording, which still needs a human spot check.
