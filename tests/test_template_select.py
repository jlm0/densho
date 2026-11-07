import shutil
from pathlib import Path

import pytest
from typer.testing import CliRunner

from engine.cli import app
from engine.compiler.tree import checked_tree
from engine.disciplines import read_answer
from engine.template import SELECT_CODES, adopt_template, select_disciplines

REPO = Path(__file__).resolve().parents[1]
RUNNER = CliRunner()
ANSWERS = ".copier-answers.yml"
NODES = {
    "knowledge/node.md": """---
id: root
kind: densho:Root
title: Root
status: proposed
origin: template
pointers:
  - kind: densho:TextPointer
    target: domain
    trigger: You need the domain.
---
""",
    "knowledge/nodes/domain/node.md": """---
id: domain
kind: densho:Domain
title: Domain
status: proposed
origin: template
knowledge_type: domain
pointers:
  - kind: densho:TextPointer
    target: alpha
    trigger: You need alpha.
  - kind: densho:TextPointer
    target: beta
    trigger: You need beta.
  - kind: densho:PathPointer
    target: gamma
    trigger: You change a gamma file.
    paths:
      - gamma/**/*
---

## Definition

The meaning of the domain.
""",
    "knowledge/nodes/domain/alpha/node.md": """---
id: alpha
kind: densho:Discipline
title: Alpha
status: proposed
origin: template
knowledge_type: domain
broader:
  - domain
informs:
  - beta
pointers:
  - kind: densho:TextPointer
    target: alpha-concept
    trigger: You need the alpha concept.
  - kind: densho:TextPointer
    target: alpha-other
    trigger: You need the other alpha concept.
  - kind: densho:SkillPointer
    target: use-both
    trigger: You review alpha and beta.
---

## Definition

The meaning of alpha.
""",
    "knowledge/nodes/domain/alpha/concept/node.md": """---
id: alpha-concept
kind: densho:Concept
title: Alpha concept
status: proposed
origin: template
knowledge_type: domain
broader:
  - alpha
related:
  - beta-concept
  - alpha-other
---

## Definition

The meaning of the alpha concept.

## Directives

- Run the alpha check. ^alpha-rule
  - scope: subtree
  - basis: judgment
  - status: proposed
  - origin: template
  - also_attached_to: beta-concept
  - also_attached_to: alpha-other
""",
    "knowledge/nodes/domain/alpha/other/node.md": """---
id: alpha-other
kind: densho:Concept
title: Alpha other
status: proposed
origin: template
knowledge_type: domain
broader:
  - alpha
---

## Definition

The meaning of the other alpha concept.
""",
    "knowledge/nodes/domain/beta/node.md": """---
id: beta
kind: densho:Discipline
title: Beta
status: proposed
origin: template
knowledge_type: domain
broader:
  - domain
pointers:
  - kind: densho:TextPointer
    target: beta-concept
    trigger: You need the beta concept.
---

## Definition

The meaning of beta.
""",
    "knowledge/nodes/domain/beta/concept/node.md": """---
id: beta-concept
kind: densho:Concept
title: Beta concept
status: proposed
origin: template
knowledge_type: domain
broader:
  - beta
---

## Definition

The meaning of the beta concept.

## Directives

- Run the beta check. ^beta-rule
  - scope: subtree
  - basis: judgment
  - status: proposed
  - origin: template
""",
    "knowledge/nodes/domain/gamma/node.md": """---
id: gamma
kind: densho:Discipline
title: Gamma
status: proposed
origin: template
knowledge_type: domain
broader:
  - domain
depends_on:
  - alpha-other
---

## Definition

The meaning of gamma.
""",
    "knowledge/skills/use-alpha/node.md": """---
id: use-alpha
kind: densho:Skill
title: Use alpha
status: proposed
origin: template
knowledge_type: domain
description: Review an alpha sample. Use when an alpha sample needs a review.
invocation: agent
uses:
  - alpha-concept
---
""",
    "knowledge/skills/use-both/node.md": """---
id: use-both
kind: densho:Skill
title: Use both
status: proposed
origin: template
knowledge_type: domain
description: Review a mixed sample. Use when a mixed sample needs a review.
invocation: agent
uses:
  - alpha-concept
  - beta-concept
---
""",
    "knowledge/skills/apply-beta/node.md": """---
id: apply-beta
kind: densho:Skill
title: Apply beta
status: proposed
origin: template
knowledge_type: domain
description: Check a beta sample. Use when a beta sample needs a check.
invocation: agent
applies:
  - beta-rule
---
""",
    "knowledge/skills/use-domain/node.md": """---
id: use-domain
kind: densho:Skill
title: Use the domain
status: proposed
origin: template
knowledge_type: domain
description: Check the graph. Use when a graph needs a check.
invocation: person
uses:
  - domain
---
""",
}
BETA_VOCABULARY = "knowledge/governance/language/branches/beta.yaml"
SCRIPT = "knowledge/skills/apply-beta/scripts/run.sh"


def write_tree(folder: Path, answer: str | None) -> Path:
    def no_branch_files(parent: str, names: list[str]) -> list[str]:
        return [name for name in names if Path(parent).name == "branches" and name != ".gitkeep"]

    shutil.copytree(
        REPO / "knowledge/governance/language",
        folder / "knowledge/governance/language",
        ignore=no_branch_files,
    )
    for relative, text in NODES.items():
        (folder / relative).parent.mkdir(parents=True, exist_ok=True)
        (folder / relative).write_text(text, encoding="utf-8")
    (folder / BETA_VOCABULARY).write_text("approved_verbs: [run]\n", encoding="utf-8")
    (folder / SCRIPT).parent.mkdir(parents=True)
    (folder / SCRIPT).write_text("#!/bin/sh\n", encoding="utf-8")
    if answer is not None:
        (folder / ANSWERS).write_text(f"_commit: abc\n{answer}", encoding="utf-8")
    return folder


def text_of(folder: Path, relative: str) -> str:
    return (folder / relative).read_text(encoding="utf-8")


def snapshot(folder: Path) -> dict[str, bytes]:
    return {
        path.relative_to(folder).as_posix(): path.read_bytes()
        for path in sorted(folder.rglob("*"))
        if path.is_file()
    }


def node_ids(folder: Path) -> set[str]:
    return {
        line.removeprefix("id: ")
        for path in (folder / "knowledge").rglob("node.md")
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.startswith("id: ")
    }


ALL = {
    "root",
    "domain",
    "alpha",
    "alpha-concept",
    "alpha-other",
    "beta",
    "beta-concept",
    "gamma",
    "use-alpha",
    "use-both",
    "apply-beta",
    "use-domain",
}


def test_the_full_fixture_passes_each_check(tmp_path: Path) -> None:
    write_tree(tmp_path, None)
    assert checked_tree(tmp_path).problems == []


@pytest.mark.parametrize(
    "answer",
    [None, "started_from: abc\n", "disciplines: [alpha, beta, gamma]\n"],
)
def test_no_selection_changes_nothing(tmp_path: Path, answer: str | None) -> None:
    write_tree(tmp_path, answer)
    before = snapshot(tmp_path)
    report = select_disciplines(tmp_path)
    assert report.problems == []
    assert report.removed == ()
    assert report.pruned == ()
    assert snapshot(tmp_path) == before


@pytest.mark.parametrize("name", ["true", "null", "no", "on", "e5"])
def test_each_answer_reads_as_text(tmp_path: Path, name: str) -> None:
    (tmp_path / ANSWERS).write_text(f"disciplines: [{name}]\n", encoding="utf-8")
    assert read_answer(tmp_path) == ([name], [])


def test_a_missing_answer_keeps_each_discipline(tmp_path: Path) -> None:
    write_tree(tmp_path, None)
    assert select_disciplines(tmp_path).disciplines is None


@pytest.mark.parametrize(
    ("answer", "message"),
    [
        ("disciplines: [alpha\n", "The file is not valid YAML."),
        ("disciplines: alpha\n", "disciplines must be a list of discipline IDs."),
        ("disciplines: [alpha, 3]\n", "disciplines must be a list of discipline IDs."),
        ("disciplines: [alpha, [beta]]\n", "disciplines must be a list of discipline IDs."),
        ("disciplines: [Alpha]\n", "disciplines must be a list of discipline IDs."),
    ],
)
def test_a_bad_answer_is_a_problem(tmp_path: Path, answer: str, message: str) -> None:
    write_tree(tmp_path, answer)
    before = snapshot(tmp_path)
    report = select_disciplines(tmp_path)
    assert [(problem.code, problem.message) for problem in report.problems] == [("select", message)]
    assert snapshot(tmp_path) == before


def test_an_answers_file_that_is_not_text_is_a_problem(tmp_path: Path) -> None:
    write_tree(tmp_path, None)
    (tmp_path / ANSWERS).write_bytes(b"\xff\xfe")
    report = select_disciplines(tmp_path)
    assert [problem.message for problem in report.problems] == [
        "The file cannot be read as UTF-8 text."
    ]


def test_a_selection_keeps_only_the_selected_discipline(tmp_path: Path) -> None:
    write_tree(tmp_path, "disciplines:\n- alpha\n")
    report = select_disciplines(tmp_path)
    assert report.problems == []
    assert report.disciplines == ("alpha",)
    assert node_ids(tmp_path) == ALL - {"beta", "beta-concept", "gamma", "use-both", "apply-beta"}
    assert not (tmp_path / "knowledge/nodes/domain/beta").exists()
    assert not (tmp_path / "knowledge/skills/apply-beta").exists()
    assert not (tmp_path / BETA_VOCABULARY).exists()
    assert checked_tree(tmp_path).problems == []


def test_a_selection_removes_each_edge_to_a_node_outside_it(tmp_path: Path) -> None:
    write_tree(tmp_path, "disciplines: [alpha]\n")
    report = select_disciplines(tmp_path)
    assert sorted(report.pruned) == [
        "alpha-concept: also_attached_to beta-concept",
        "alpha-concept: related beta-concept",
        "alpha: informs beta",
        "alpha: pointer use-both",
        "domain: pointer beta",
        "domain: pointer gamma",
    ]
    alpha = text_of(tmp_path, "knowledge/nodes/domain/alpha/node.md")
    assert "informs" not in alpha
    assert "use-both" not in alpha
    assert "target: alpha-other\n    trigger: You need the other alpha concept.\n---" in alpha
    concept = text_of(tmp_path, "knowledge/nodes/domain/alpha/concept/node.md")
    assert "related:\n  - alpha-other\n---" in concept
    assert "  - origin: template\n  - also_attached_to: alpha-other\n" in concept
    domain = text_of(tmp_path, "knowledge/nodes/domain/node.md")
    assert "trigger: You need alpha.\n---" in domain


def test_a_selection_of_nothing_keeps_the_root_and_each_skill_with_no_discipline(
    tmp_path: Path,
) -> None:
    write_tree(tmp_path, "disciplines: []\n")
    report = select_disciplines(tmp_path)
    assert report.problems == []
    assert report.disciplines == ()
    assert node_ids(tmp_path) == {"root", "domain", "use-domain"}
    domain = text_of(tmp_path, "knowledge/nodes/domain/node.md")
    assert "pointers" not in domain
    assert "knowledge_type: domain\n---" in domain
    assert not (tmp_path / "knowledge/nodes/domain/alpha").exists()
    assert (tmp_path / "knowledge/nodes/domain").is_dir()
    assert checked_tree(tmp_path).problems == []


def test_a_dependency_adds_its_discipline_with_a_note(tmp_path: Path) -> None:
    write_tree(tmp_path, "disciplines: [gamma]\n")
    report = select_disciplines(tmp_path)
    assert report.problems == []
    assert report.disciplines == ("alpha", "gamma")
    assert report.notes == ["The selection adds alpha, because gamma depends on alpha-other."]
    assert "alpha-other" in node_ids(tmp_path)
    assert checked_tree(tmp_path).problems == []


def test_an_unknown_discipline_gets_a_note(tmp_path: Path) -> None:
    write_tree(tmp_path, "disciplines: [alpha, beta, gamma, delta]\n")
    report = select_disciplines(tmp_path)
    assert report.notes == [
        "The answer names delta, and the template has no discipline with this ID."
    ]
    assert report.removed == ()
    assert report.disciplines == ("alpha", "beta", "gamma")


def test_a_second_selection_changes_nothing(tmp_path: Path) -> None:
    write_tree(tmp_path, "disciplines: [alpha]\n")
    select_disciplines(tmp_path)
    before = snapshot(tmp_path)
    second = select_disciplines(tmp_path)
    assert second.problems == []
    assert second.removed == ()
    assert second.pruned == ()
    assert snapshot(tmp_path) == before


@pytest.mark.parametrize(
    ("relative", "old", "new", "field"),
    [
        (
            "knowledge/nodes/domain/alpha/other/node.md",
            "  - alpha\n",
            "  - alpha\n  - beta\n",
            "broader",
        ),
        (
            "knowledge/nodes/domain/alpha/other/node.md",
            "broader:\n  - alpha\n",
            (
                "broader:\n  - alpha\nexceptions:\n  - directive: beta-rule\n"
                "    reason: A test.\n    status: proposed\n"
            ),
            "directive",
        ),
        (
            "knowledge/nodes/domain/alpha/concept/node.md",
            "  - also_attached_to: alpha-other\n",
            "  - also_attached_to: alpha-other\n  - conflicts_with: beta-rule\n",
            "conflicts_with",
        ),
    ],
)
def test_an_edge_that_no_rule_removes_stops_the_selection(
    tmp_path: Path, relative: str, old: str, new: str, field: str
) -> None:
    write_tree(tmp_path, "disciplines: [alpha]\n")
    text = text_of(tmp_path, relative)
    assert old in text
    (tmp_path / relative).write_text(text.replace(old, new, 1), encoding="utf-8")
    before = snapshot(tmp_path)
    report = select_disciplines(tmp_path)
    assert [problem.code for problem in report.problems] == ["select"]
    assert report.problems[0].message.startswith(f"{field} names ")
    assert report.problems[0].path == tmp_path / relative
    assert snapshot(tmp_path) == before


def test_a_project_node_stays_and_stops_the_selection(tmp_path: Path) -> None:
    write_tree(tmp_path, "disciplines: [alpha]\n")
    relative = "knowledge/nodes/domain/beta/own/node.md"
    (tmp_path / relative).parent.mkdir()
    own = NODES["knowledge/nodes/domain/alpha/other/node.md"]
    own = own.replace("alpha-other", "beta-own").replace("origin: template", "origin: project")
    (tmp_path / relative).write_text(own.replace("  - alpha\n", "  - beta\n"), encoding="utf-8")
    before = snapshot(tmp_path)
    report = select_disciplines(tmp_path)
    assert [problem.message.split(",")[0] for problem in report.problems] == ["broader names beta"]
    assert snapshot(tmp_path) == before


def test_a_project_skill_stays_and_stops_the_selection(tmp_path: Path) -> None:
    write_tree(tmp_path, "disciplines: [alpha]\n")
    relative = "knowledge/skills/apply-beta/node.md"
    text = text_of(tmp_path, relative).replace("origin: template", "origin: project")
    (tmp_path / relative).write_text(text, encoding="utf-8")
    report = select_disciplines(tmp_path)
    assert [problem.message.split(",")[0] for problem in report.problems] == [
        "applies names beta-rule"
    ]


def test_a_flow_list_stops_the_selection(tmp_path: Path) -> None:
    write_tree(tmp_path, "disciplines: [alpha]\n")
    relative = "knowledge/nodes/domain/alpha/concept/node.md"
    text = text_of(tmp_path, relative)
    flow = text.replace(
        "related:\n  - beta-concept\n  - alpha-other\n", "related: [beta-concept, alpha-other]\n"
    )
    (tmp_path / relative).write_text(flow, encoding="utf-8")
    before = snapshot(tmp_path)
    report = select_disciplines(tmp_path)
    assert [(problem.path, problem.code) for problem in report.problems] == [
        (tmp_path / relative, "select")
    ]
    assert "Write each list entry on its own line" in report.problems[0].message
    assert snapshot(tmp_path) == before


def test_a_crlf_file_keeps_its_line_ends(tmp_path: Path) -> None:
    write_tree(tmp_path, "disciplines: [alpha]\n")
    relative = "knowledge/nodes/domain/alpha/node.md"
    (tmp_path / relative).write_bytes(text_of(tmp_path, relative).replace("\n", "\r\n").encode())
    assert select_disciplines(tmp_path).problems == []
    data = (tmp_path / relative).read_bytes()
    assert b"informs" not in data
    assert data.count(b"\n") == data.count(b"\r\n")


def test_a_dash_on_its_own_line_stops_the_selection(tmp_path: Path) -> None:
    write_tree(tmp_path, "disciplines: [alpha, gamma]\n")
    relative = "knowledge/nodes/domain/node.md"
    text = text_of(tmp_path, relative).replace(
        "  - kind: densho:PathPointer", "  -\n    kind: densho:PathPointer"
    )
    (tmp_path / relative).write_text(text, encoding="utf-8")
    before = snapshot(tmp_path)
    report = select_disciplines(tmp_path)
    assert [problem.code for problem in report.problems] == ["select"]
    assert snapshot(tmp_path) == before


def test_a_node_that_does_not_parse_stops_the_selection(tmp_path: Path) -> None:
    write_tree(tmp_path, "disciplines: [alpha]\n")
    (tmp_path / "knowledge/nodes/domain/beta/node.md").write_text("no front matter\n")
    before = snapshot(tmp_path)
    report = select_disciplines(tmp_path)
    assert report.problems
    assert report.disciplines is None
    assert snapshot(tmp_path) == before


def test_a_dependency_on_a_kept_node_adds_no_discipline(tmp_path: Path) -> None:
    write_tree(tmp_path, "disciplines: [gamma]\n")
    path = tmp_path / "knowledge/nodes/domain/alpha/other/node.md"
    path.write_text(
        text_of(tmp_path, "knowledge/nodes/domain/alpha/other/node.md").replace(
            "broader:\n  - alpha\n", "broader:\n  - alpha\n  - gamma\n"
        ),
        encoding="utf-8",
    )
    report = select_disciplines(tmp_path)
    assert report.disciplines == ("gamma",)
    assert report.notes == []
    assert [problem.message.split(",")[0] for problem in report.problems] == ["broader names alpha"]


def test_a_kept_node_inside_a_removed_folder_stays(tmp_path: Path) -> None:
    write_tree(tmp_path, "disciplines: [alpha]\n")
    shutil.move(
        tmp_path / "knowledge/nodes/domain/alpha/other",
        tmp_path / "knowledge/nodes/domain/beta/other",
    )
    assert select_disciplines(tmp_path).problems == []
    assert (tmp_path / "knowledge/nodes/domain/beta/other/node.md").is_file()
    assert not (tmp_path / "knowledge/nodes/domain/beta/node.md").exists()


def test_the_command_prints_each_step(tmp_path: Path) -> None:
    write_tree(tmp_path, "disciplines: [gamma]\n")
    result = RUNNER.invoke(app, ["select", str(tmp_path)])
    assert result.exit_code == 0
    assert "note: The selection adds alpha, because gamma depends on alpha-other." in result.output
    assert f"removed {tmp_path / 'knowledge/nodes/domain/beta/node.md'}" in result.output
    assert "removed the entry alpha: informs beta" in result.output
    assert "kept alpha, gamma, 5 paths removed, 5 entries removed, 0 problems" in result.output


def test_the_command_names_an_empty_selection(tmp_path: Path) -> None:
    write_tree(tmp_path, "disciplines: []\n")
    result = RUNNER.invoke(app, ["select", str(tmp_path)])
    assert "kept no discipline" in result.output
    write_tree(tmp_path / "other", None)
    result = RUNNER.invoke(app, ["select", str(tmp_path / "other")])
    assert "kept each discipline, 0 paths removed, 0 entries removed, 0 problems" in result.output


def test_the_command_fails_on_a_problem(tmp_path: Path) -> None:
    write_tree(tmp_path, "disciplines: alpha\n")
    result = RUNNER.invoke(app, ["select", str(tmp_path)])
    assert result.exit_code == 1
    assert ": select: " in result.output


def test_adopt_selects_before_it_sets_a_status(tmp_path: Path) -> None:
    write_tree(tmp_path, "disciplines: [alpha]\n")
    report = adopt_template(tmp_path)
    assert report.problems == []
    assert report.selection is not None
    assert report.selection.disciplines == ("alpha",)
    assert "beta" not in node_ids(tmp_path)
    assert not (tmp_path / ".claude/skills/use-both").exists()
    assert (tmp_path / ".claude/skills/use-alpha/SKILL.md").is_file()


def test_adopt_stops_on_a_selection_problem(tmp_path: Path) -> None:
    write_tree(tmp_path, "disciplines: alpha\n")
    report = adopt_template(tmp_path)
    assert [problem.code for problem in report.problems] == ["select"]
    assert report.runtime is None
    assert not (tmp_path / "AGENTS.md").exists()


def test_adopt_prints_the_selection(tmp_path: Path) -> None:
    write_tree(tmp_path, "disciplines: [gamma]\n")
    result = RUNNER.invoke(app, ["adopt", str(tmp_path)])
    assert result.exit_code == 0
    assert "note: The selection adds alpha, because gamma depends on alpha-other." in result.output
    assert "removed the entry domain: pointer beta" in result.output


def test_each_code_is_named() -> None:
    assert SELECT_CODES == ("select",)


def test_a_project_discipline_is_not_a_template_discipline(tmp_path: Path) -> None:
    write_tree(tmp_path, "disciplines: [alpha, beta, gamma, delta]\n")
    delta = tmp_path / "knowledge/nodes/domain/delta/node.md"
    delta.parent.mkdir()
    delta.write_text(
        text_of(tmp_path, "knowledge/nodes/domain/gamma/node.md")
        .replace("gamma", "delta")
        .replace("Gamma", "Delta")
        .replace("origin: template", "origin: project")
        .replace("depends_on:\n  - alpha-other\n", ""),
        encoding="utf-8",
    )
    report = select_disciplines(tmp_path)
    assert report.disciplines == ("alpha", "beta", "gamma")
    assert report.notes == [
        "The answer names delta, and the template has no discipline with this ID."
    ]


def test_the_last_pointer_before_another_key_keeps_that_key(tmp_path: Path) -> None:
    write_tree(tmp_path, "disciplines: [alpha]\n")
    path = tmp_path / "knowledge/nodes/domain/node.md"
    text = text_of(tmp_path, "knowledge/nodes/domain/node.md")
    text = text.replace("knowledge_type: domain\n", "").replace(
        "      - gamma/**/*\n---", "      - gamma/**/*\nknowledge_type: domain\n---"
    )
    path.write_text(text, encoding="utf-8")
    report = select_disciplines(tmp_path)
    assert report.problems == []
    domain = text_of(tmp_path, "knowledge/nodes/domain/node.md")
    assert "trigger: You need alpha.\nknowledge_type: domain\n---" in domain
    assert checked_tree(tmp_path).problems == []


def test_a_path_that_cannot_be_removed_is_a_problem(tmp_path: Path) -> None:
    write_tree(tmp_path, "disciplines: [alpha]\n")
    folder = tmp_path / "knowledge/nodes/domain/beta/concept"
    folder.chmod(0o555)
    try:
        report = select_disciplines(tmp_path)
    finally:
        folder.chmod(0o755)
    assert [(problem.path, problem.code) for problem in report.problems] == [
        (folder / "node.md", "select")
    ]
    assert report.problems[0].message.startswith("The command cannot remove this path:")
