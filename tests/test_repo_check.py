from __future__ import annotations

from ir_harness.repo_check import (
    dangling_references,
    eval_case_problems,
    load_eval_cases,
    skill_problems,
)


def test_repository_has_no_dangling_references(root):
    assert [str(p) for p in dangling_references(root)] == []


def test_every_skill_has_frontmatter(root):
    assert skill_problems(root) == []


def test_eval_cases_route_as_documented(root):
    cases = load_eval_cases(root)
    assert {c.route for c in cases} == {"mapping", "founder", "clarify"}
    assert all(c.task for c in cases)
    assert eval_case_problems(root) == []


def test_dangling_reference_detection(tmp_path):
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "real.md").write_text("ok\n", encoding="utf-8")
    (tmp_path / "README.md").write_text(
        "see `docs/real.md`, `docs/missing.md`, `docs/{name}.md`, [x](docs/gone.md), "
        "[web](https://example.com), `../outside.md`\n",
        encoding="utf-8",
    )
    found = [p.message for p in dangling_references(tmp_path)]
    assert found == [
        "dangling reference: docs/missing.md",
        "dangling reference: ../outside.md",
        "dangling reference: docs/gone.md",
    ]


def test_html_image_and_link_targets_are_checked(tmp_path):
    (tmp_path / "assets").mkdir()
    (tmp_path / "assets" / "hero.svg").write_text("<svg/>", encoding="utf-8")
    (tmp_path / "README.md").write_text(
        '<p align="center">\n'
        '  <img src="./assets/hero.svg" alt="ok">\n'
        "  <img\n"
        '    src="./assets/missing.svg" alt="spans two lines">\n'
        '  <a href="LICENSE"><img src="https://example.com/badge.svg" alt="badge"></a>\n'
        '  <a href="#quick-start">anchor</a>\n'
        "</p>\n"
        "see `assets/hero.svg` and `assets/nope.svg`\n",
        encoding="utf-8",
    )
    assert [str(p) for p in dangling_references(tmp_path)] == [
        "README.md:4: dangling reference: ./assets/missing.svg",
        "README.md:5: dangling reference: LICENSE",
        "README.md:8: dangling reference: assets/nope.svg",
    ]


def test_skill_without_frontmatter(tmp_path):
    skill = tmp_path / "skills" / "x" / "SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_text("# no frontmatter\n", encoding="utf-8")
    assert [p.message for p in skill_problems(tmp_path)] == ["missing frontmatter"]
    skill.write_text("---\nname: x\n---\nbody\n", encoding="utf-8")
    assert [p.message for p in skill_problems(tmp_path)] == ["frontmatter lacks 'description'"]


def test_clarify_case_fails_when_a_route_matches(tmp_path, root):
    cases = tmp_path / "agent" / "evals" / "cases"
    cases.mkdir(parents=True)
    (tmp_path / "agent" / "router.md").write_text(
        (root / "agent" / "router.md").read_text(encoding="utf-8"), encoding="utf-8"
    )
    (cases / "x.md").write_text(
        "# Case\n\n## Input To Agent\n\n```text\n帮我做个 mapping\n```\n\n"
        "## Machine-Checkable Expectations\n\n| Key | Value |\n|---|---|\n| route | `clarify` |\n",
        encoding="utf-8",
    )
    assert [p.message for p in eval_case_problems(tmp_path)] == [
        "routes to 'mapping', expected a question"
    ]
