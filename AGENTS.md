# AGENTS.md

Guidance for coding agents (Claude Code, Codex, Pi and similar) working on this repository. `irh run` passes `--no-context-files`, so this file never leaks into research runs.

## Setup and checks

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"          # add ".[viz]" for the landscape scripts and their tests
make check                        # ruff, pytest, irh validate, irh scan
```

Run `make check` before every commit.

## How the repository is organised

- Rules live in markdown: `agent/` (control layer) and `skills/` (method layer). Code in `src/ir_harness/` parses them. To change routing, edit `agent/router.md`, not `router.py`; to change a rubric, edit `agent/evals/rubrics/*.md`.
- A rule that can be checked from the run record belongs in a gate (`gates.py`) and in the playbook's "Enforcement In Code" table, with a test.
- Every path a markdown file names must exist; `irh validate` fails otherwise.
- Eval cases carry a "Machine-Checkable Expectations" table; the test suite checks them against the router.

## Conventions

- Python 3.10+, standard library only in `src/` (optional extras stay optional), type hints, frozen dataclasses for value objects.
- ruff with line length 100; `ruff format` for formatting.
- Tests next to behaviour: each gate, scorer and parser has unit tests; examples are tested as data.
- Strings that look like secrets in tests are assembled at runtime so `irh scan` stays clean.

## Content rules

- Never add real deal material, real names from deal work, internal links, local absolute paths or API keys. Examples must be fictional and say so.
- Keep the information-status vocabulary consistent: `核实`, `公开报道`, `媒体口径`, `市场线索待核验`, `待DD`, `推演`, `未公开`.
- Run `irh scan` with the local, gitignored `.sensitive-terms.txt` before publishing.
