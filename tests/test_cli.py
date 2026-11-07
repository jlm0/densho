import shutil
from pathlib import Path
from typing import TYPE_CHECKING

from typer.core import TyperGroup
from typer.main import get_command
from typer.testing import CliRunner

from engine.cli import app
from engine.language.profile import LanguageProfile, read_profile

if TYPE_CHECKING:
    import pytest

LANGUAGE = Path(__file__).resolve().parents[1] / "knowledge/governance/language"
PROFILE = read_profile(LANGUAGE)
assert isinstance(PROFILE, LanguageProfile)
GRAMMAR = PROFILE.grammar
RUNNER = CliRunner()
NODE = """---
id: sample
kind: ka:Domain
title: Sample
status: accepted
origin: template
knowledge_type: domain
---

## Definition

A sample.
"""
ROOT = """---
id: root
kind: ka:Root
title: Root
status: accepted
origin: template
pointers:
  - kind: ka:TextPointer
    target: sample
    trigger: You need the sample.
---
"""


def write_node(folder: Path, text: str = NODE) -> Path:
    folder.mkdir(parents=True)
    path = folder / "node.md"
    path.write_text(text, encoding="utf-8")
    return path


def test_parse_needs_a_folder() -> None:
    result = RUNNER.invoke(app, ["parse"])
    assert result.exit_code > 1
    assert "Usage" in result.output


def test_parse_passes_on_valid_nodes(tmp_path: Path) -> None:
    write_node(tmp_path / "a")
    result = RUNNER.invoke(app, ["parse", str(tmp_path)])
    assert result.exit_code == 0
    assert result.output == "1 nodes parsed, 0 problems\n"


def test_parse_fails_and_prints_each_location(tmp_path: Path) -> None:
    path = write_node(tmp_path / "a", NODE.replace("status: accepted", "status: ok"))
    result = RUNNER.invoke(app, ["parse", str(tmp_path)])
    assert result.exit_code == 1
    assert f"{path}:5: schema: status: " in result.output
    assert result.output.endswith("0 nodes parsed, 1 problems\n")


def test_parse_fails_on_a_missing_folder(tmp_path: Path) -> None:
    assert RUNNER.invoke(app, ["parse", str(tmp_path / "missing")]).exit_code == 1


def test_graph_passes_on_an_empty_tree(tmp_path: Path) -> None:
    (tmp_path / "knowledge").mkdir()
    result = RUNNER.invoke(app, ["graph", str(tmp_path)])
    assert result.exit_code == 0
    assert result.output == "0 nodes checked, 0 problems\n"


def test_graph_passes_on_a_valid_tree(tmp_path: Path) -> None:
    write_node(tmp_path / "knowledge", ROOT)
    write_node(tmp_path / "knowledge/nodes/sample")
    result = RUNNER.invoke(app, ["graph", str(tmp_path)])
    assert result.exit_code == 0, result.output
    assert result.output == "2 nodes checked, 0 problems\n"


def test_graph_fails_and_prints_each_location(tmp_path: Path) -> None:
    write_node(tmp_path / "knowledge", ROOT.replace("target: sample", "target: missing"))
    write_node(tmp_path / "knowledge/nodes/sample")
    result = RUNNER.invoke(app, ["graph", str(tmp_path)])
    assert result.exit_code == 1
    path = tmp_path / "knowledge/node.md"
    assert (
        f"{path}:9: reference: target names 'missing', and no node or directive has this ID.\n"
        in result.output
    )
    assert result.output.endswith("2 nodes checked, 1 problems\n")


def test_graph_reads_the_current_folder_by_default(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    write_node(tmp_path / "knowledge/nodes/sample")
    result = RUNNER.invoke(app, ["graph"])
    assert result.exit_code == 1
    assert result.output.startswith("knowledge/node.md:1: root: ")


RULES = sum(
    len(rules)
    for rules in (
        GRAMMAR.directive_rules,
        GRAMMAR.trigger_rules,
        GRAMMAR.description_rules,
    )
)


def language_tree(repository: Path) -> None:
    shutil.copytree(
        LANGUAGE,
        repository / "knowledge/governance/language",
        ignore=shutil.ignore_patterns("branches"),
    )


def test_language_reads_the_grammar_rules_on_an_empty_tree(tmp_path: Path) -> None:
    language_tree(tmp_path)
    result = RUNNER.invoke(app, ["language", str(tmp_path)])
    assert result.exit_code == 0
    assert result.output == f"{RULES} texts checked, 0 problems\n"


def test_language_passes_on_good_text(tmp_path: Path) -> None:
    language_tree(tmp_path)
    write_node(tmp_path / "knowledge/nodes/a", ROOT)
    result = RUNNER.invoke(app, ["language", str(tmp_path)])
    assert result.exit_code == 0, result.output
    assert result.output == f"{RULES + 1} texts checked, 0 problems\n"


def test_language_fails_and_prints_each_location(tmp_path: Path) -> None:
    language_tree(tmp_path)
    path = write_node(tmp_path / "knowledge/nodes/a", ROOT.replace("You need", "Find"))
    result = RUNNER.invoke(app, ["language", str(tmp_path)])
    assert result.exit_code == 1
    assert f"{path}:10: trigger-form: " in result.output
    assert result.output.endswith(f"{RULES + 1} texts checked, 1 problems\n")


def test_language_reads_the_current_folder_by_default(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    language_tree(tmp_path)
    write_node(tmp_path / "knowledge/nodes/a", ROOT.replace("You need", "Find"))
    result = RUNNER.invoke(app, ["language"])
    assert result.exit_code == 1
    assert result.output.startswith("knowledge/nodes/a/node.md:10: trigger-form: ")


DIRECTIVE_NODE = (
    NODE
    + """
## Directives

- Run `pytest` before you commit. ^run-tests
  - scope: subtree
  - basis: judgment
  - status: accepted
  - origin: template
"""
)
CHILD = """---
id: child
kind: ka:Concept
title: Child
status: accepted
origin: template
knowledge_type: domain
broader: [sample]
exceptions:
  - directive: run-tests
    reason: This node holds a prototype.
    status: accepted
---

## Definition

A child.
"""
ROOT_WITH_CHILD = ROOT.replace(
    "    trigger: You need the sample.\n",
    "    trigger: You need the sample.\n"
    "  - kind: ka:TextPointer\n    target: child\n    trigger: You need the child.\n",
)


def directive_tree(repository: Path, child: str = CHILD) -> None:
    write_node(repository / "knowledge", ROOT_WITH_CHILD)
    write_node(repository / "knowledge/nodes/sample", DIRECTIVE_NODE)
    write_node(repository / "knowledge/nodes/sample/child", child)


def test_directives_passes_on_an_empty_tree(tmp_path: Path) -> None:
    (tmp_path / "knowledge").mkdir()
    result = RUNNER.invoke(app, ["directives", str(tmp_path)])
    assert result.exit_code == 0
    assert result.output == "0 directives checked, 0 problems\n"


def test_directives_passes_on_a_valid_tree(tmp_path: Path) -> None:
    directive_tree(tmp_path)
    result = RUNNER.invoke(app, ["directives", str(tmp_path)])
    assert result.exit_code == 0, result.output
    assert result.output == "1 directives checked, 0 problems\n"


def test_directives_fails_and_prints_each_location(tmp_path: Path) -> None:
    directive_tree(tmp_path, CHILD.replace("broader: [sample]", "broader: [other]"))
    other = NODE.replace("id: sample", "id: other")
    write_node(tmp_path / "knowledge/nodes/other", other)
    root = (tmp_path / "knowledge/node.md").read_text(encoding="utf-8")
    pointer = "  - kind: ka:TextPointer\n    target: other\n    trigger: You need the other.\n"
    (tmp_path / "knowledge/node.md").write_text(
        root.replace("pointers:\n", f"pointers:\n{pointer}"), encoding="utf-8"
    )
    result = RUNNER.invoke(app, ["directives", str(tmp_path)])
    assert result.exit_code == 1
    path = tmp_path / "knowledge/nodes/sample/child/node.md"
    assert f"{path}:10: exception-unused: This exception stops nothing" in result.output
    assert result.output.endswith("1 directives checked, 1 problems\n")


def test_directives_prints_a_graph_problem_and_stops(tmp_path: Path) -> None:
    directive_tree(tmp_path, CHILD.replace("broader: [sample]", "broader: [missing]"))
    result = RUNNER.invoke(app, ["directives", str(tmp_path)])
    assert result.exit_code == 1
    assert ": reference: broader names 'missing'" in result.output
    assert result.output.endswith("0 directives checked, 1 problems\n")


def test_directives_lists_what_applies_at_a_node(tmp_path: Path) -> None:
    directive_tree(tmp_path)
    result = RUNNER.invoke(app, ["directives", str(tmp_path), "--at", "sample"])
    assert result.exit_code == 0, result.output
    assert result.output == (
        "run-tests (subtree) from sample: Run `pytest` before you commit.\n"
        "1 directives apply at sample, 0 proposed, 0 problems\n"
    )


def test_directives_lists_nothing_at_a_node_that_steps_out(tmp_path: Path) -> None:
    directive_tree(tmp_path)
    result = RUNNER.invoke(app, ["directives", str(tmp_path), "--at", "child"])
    assert result.exit_code == 0, result.output
    assert result.output == "0 directives apply at child, 0 proposed, 0 problems\n"


def test_directives_prints_the_whole_route(tmp_path: Path) -> None:
    directive_tree(
        tmp_path, CHILD.split("exceptions:", maxsplit=1)[0] + "---\n\n## Definition\n\nA child.\n"
    )
    result = RUNNER.invoke(app, ["directives", str(tmp_path), "--at", "child"])
    assert "run-tests (subtree) from sample -> child: " in result.output


def test_directives_rejects_an_unknown_node(tmp_path: Path) -> None:
    directive_tree(tmp_path)
    result = RUNNER.invoke(app, ["directives", str(tmp_path), "--at", "no\x1bpe"])
    assert result.exit_code == 1
    assert result.output == "No node has the ID 'no\\x1bpe'.\n"


def test_directives_at_stops_on_a_graph_problem(tmp_path: Path) -> None:
    directive_tree(tmp_path, CHILD.replace("broader: [sample]", "broader: [missing]"))
    result = RUNNER.invoke(app, ["directives", str(tmp_path), "--at", "sample"])
    assert result.exit_code == 1
    assert ": reference: broader names 'missing'" in result.output
    assert "run-tests (" not in result.output


def _folder_options() -> list[tuple[str, str]]:
    command = get_command(app)
    assert isinstance(command, TyperGroup)
    return [
        (name, str(getattr(param, "help", None)))
        for name, sub in command.commands.items()
        for param in sub.params
        if param.name == "repository"
    ]


def test_each_command_with_a_folder_gives_the_same_help() -> None:
    found = _folder_options()
    assert {name for name, _ in found} == set(get_command_names()) - {"parse"}
    assert {text for _, text in found} == {"The folder that holds knowledge/."}


def test_the_help_of_each_command_names_no_old_folder() -> None:
    for name in get_command_names():
        output = RUNNER.invoke(app, [name, "--help"]).output
        assert "governance/language/ and" not in output, name
        assert "skills/, and governance/" not in output, name
        assert "holds the template." not in output, name


def get_command_names() -> list[str]:
    command = get_command(app)
    assert isinstance(command, TyperGroup)
    return sorted(command.commands)
