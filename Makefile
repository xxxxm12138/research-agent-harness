.PHONY: install lint format test validate scan check demo

PY ?= python
E := examples/ai-companion-hardware
TASK := 帮我做 AI 陪伴硬件赛道的 mapping，看哪些机构投了

install:
	$(PY) -m pip install -e ".[dev]"

lint:
	ruff check .
	ruff format --check .

format:
	ruff format .
	ruff check --fix .

test:
	pytest

validate:
	irh validate

scan:
	irh scan

check: lint test validate scan

demo:
	irh route "$(TASK)"
	irh assemble "$(TASK)" --asof 2026-09-30 --sources $(E)/sources.json
	irh check $(E)/run.json --sources $(E)/sources.json
	-irh check $(E)/run_bad.json --sources $(E)/sources.json
	irh score $(E)/run.json --sources $(E)/sources.json
