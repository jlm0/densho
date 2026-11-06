# pyright: reportUnknownArgumentType=false, reportUnknownLambdaType=false
import shutil
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from typer.testing import CliRunner

from engine.cli import app
from engine.governance.base import Base
from engine.parser.generated import MARKER
from engine.parser.result import Problem
from engine.runtime.claude_code import add_root_import, instruction_notes
from engine.template import ADOPT_CODES, adopt_template
from engine.template import adopt as adopt_module

if TYPE_CHECKING:
    from collections.abc import Iterable

REPO = Path(__file__).resolve().parents[1]
RUNNER = CliRunner()
GIT = shutil.which("git") or "git"
ROOT_NODE = """---
id: root
kind: ka:Root
title: Root
status: proposed
origin: template
pointers:
  - kind: ka:TextPointer
    target: domain
    trigger: You need the domain.
---
"""
DOMAIN_NODE = """---
id: domain
kind: ka:Domain
title: Domain
status: accepted
origin: template
knowledge_type: domain
pointers:
  - kind: ka:TextPointer
    target: child
    trigger: You need the child.
---

## Definition

The meaning of the domain.

## Directives

- Run the check. ^run-it
  - scope: subtree
  - status: accepted
  - origin: template
- Run the other check. ^run-other
  - scope: subtree
  - status: proposed
  - origin: template
"""
CHILD_NODE = """---
id: child
kind: ka:Concept
title: Child
status: proposed
origin: template
knowledge_type: domain
broader:
  - domain
exceptions:
  - directive: run-it
    reason: A prototype.
    status: accepted
---

## Definition

The meaning of the child.
"""
DOMAIN_PATH = "knowledge/domain/node.md"
CHILD_PATH = "knowledge/domain/child/node.md"


def write_tree(folder: Path, domain: str = DOMAIN_NODE, child: str = CHILD_NODE) -> Path:
    def no_branch_files(parent: str, names: list[str]) -> list[str]:
        return [name for name in names if Path(parent).name == "branches" and name != ".gitkeep"]

    shutil.copytree(
        REPO / "governance/language", folder / "governance/language", ignore=no_branch_files
    )
    (folder / "knowledge/domain/child").mkdir(parents=True)
    (folder / "skills").mkdir()
    (folder / "knowledge/node.md").write_text(ROOT_NODE, encoding="utf-8")
    (folder / DOMAIN_PATH).write_text(domain, encoding="utf-8")
    (folder / CHILD_PATH).write_text(child, encoding="utf-8")
    return folder


def git(folder: Path, *arguments: str) -> None:
    subprocess.run(  # noqa: S603
        [GIT, "-C", str(folder), *arguments], capture_output=True, check=True
    )


def new_repository(folder: Path) -> Path:
    git(folder, "init", "-q", "--template=", "--initial-branch=main")
    git(folder, "config", "user.name", "Test")
    git(folder, "config", "user.email", "test@example.com")
    return folder


def with_history(folder: Path) -> Path:
    new_repository(folder)
    (folder / "README.md").write_text("A project.\n", encoding="utf-8")
    git(folder, "add", "-A")
    git(folder, "commit", "-qm", "first")
    return folder


def committed_tree(folder: Path, domain: str = DOMAIN_NODE) -> Path:
    new_repository(folder)
    write_tree(folder, domain)
    git(folder, "add", "-A")
    git(folder, "commit", "-qm", "first")
    return folder


def codes(problems: Iterable[Problem]) -> list[str]:
    return [problem.code for problem in problems]


def text_of(folder: Path, relative: str = DOMAIN_PATH) -> str:
    return (folder / relative).read_text(encoding="utf-8")


def set_text(folder: Path, old: str, new: str, relative: str = DOMAIN_PATH) -> None:
    text = text_of(folder, relative)
    assert old in text
    (folder / relative).write_text(text.replace(old, new), encoding="utf-8")


def labels(folder: Path) -> set[str]:
    return {entity.label for entity in adopt_template(folder).proposed}


@pytest.mark.parametrize("repository", [False, True])
def test_a_folder_with_no_commit_keeps_each_status(tmp_path: Path, *, repository: bool) -> None:
    write_tree(tmp_path)
    if repository:
        new_repository(tmp_path)
    before = text_of(tmp_path)
    report = adopt_template(tmp_path)
    assert not report.problems
    assert report.proposed == ()
    assert text_of(tmp_path) == before
    assert report.runtime is not None
    assert (tmp_path / "AGENTS.md").is_file()
    assert any("change rules did not run" in note for note in report.notes)


def test_a_repo_with_history_brings_each_entity_in_as_proposed(tmp_path: Path) -> None:
    with_history(tmp_path)
    write_tree(tmp_path)
    report = adopt_template(tmp_path)
    assert not report.problems
    assert {entity.label for entity in report.proposed} == {
        "node domain",
        "directive run-it",
        "exception child run-it",
    }
    assert text_of(tmp_path) == DOMAIN_NODE.replace("status: accepted", "status: proposed")
    assert text_of(tmp_path, CHILD_PATH) == CHILD_NODE.replace(
        "status: accepted", "status: proposed"
    )


def test_the_generated_files_follow_the_new_status(tmp_path: Path) -> None:
    with_history(tmp_path)
    write_tree(tmp_path)
    adopt_template(tmp_path)
    root = text_of(tmp_path, "AGENTS.md")
    assert MARKER in root
    assert "No directive is in force" in root


def test_a_second_run_changes_nothing(tmp_path: Path) -> None:
    with_history(tmp_path)
    write_tree(tmp_path)
    adopt_template(tmp_path)
    before = text_of(tmp_path)
    second = adopt_template(tmp_path)
    assert second.proposed == ()
    assert text_of(tmp_path) == before
    assert second.runtime is not None
    assert second.runtime.written == ()


def test_an_entity_in_the_last_commit_stays(tmp_path: Path) -> None:
    committed_tree(tmp_path)
    before = text_of(tmp_path)
    assert adopt_template(tmp_path).proposed == ()
    assert text_of(tmp_path) == before


def test_a_changed_field_returns_to_proposed(tmp_path: Path) -> None:
    committed_tree(tmp_path)
    set_text(tmp_path, "Run the check. ^run-it", "Run the new check. ^run-it")
    assert labels(tmp_path) == {"directive run-it"}
    block = text_of(tmp_path).split("^run-it")[1]
    assert block.startswith("\n  - scope: subtree\n  - status: proposed\n")


def test_a_change_with_no_review_keeps_the_status(tmp_path: Path) -> None:
    committed_tree(tmp_path)
    set_text(tmp_path, "title: Domain", "title: Area")
    assert labels(tmp_path) == set()
    assert "status: accepted\norigin" in text_of(tmp_path)


def test_a_promotion_in_a_pull_returns_to_proposed(tmp_path: Path) -> None:
    committed_tree(tmp_path)
    set_text(tmp_path, "  - status: proposed", "  - status: accepted")
    assert labels(tmp_path) == {"directive run-other"}
    assert text_of(tmp_path).count("  - status: proposed") == 1


def test_a_deprecated_status_with_no_change_stays(tmp_path: Path) -> None:
    committed_tree(tmp_path)
    set_text(tmp_path, "  - status: accepted", "  - status: deprecated")
    assert labels(tmp_path) == set()
    assert "  - status: deprecated" in text_of(tmp_path)


def test_a_jump_from_deprecated_returns_to_proposed(tmp_path: Path) -> None:
    committed_tree(tmp_path, DOMAIN_NODE.replace("  - status: accepted", "  - status: deprecated"))
    set_text(tmp_path, "  - status: deprecated", "  - status: accepted")
    assert labels(tmp_path) == {"directive run-it"}
    assert "  - status: proposed\n  - origin: template\n- Run the other" in text_of(tmp_path)


def test_a_status_that_returns_to_proposed_needs_no_edit(tmp_path: Path) -> None:
    committed_tree(tmp_path)
    set_text(tmp_path, "  - status: accepted", "  - status: proposed")
    assert labels(tmp_path) == set()


def test_a_new_deprecated_entity_arrives_with_a_note(tmp_path: Path) -> None:
    with_history(tmp_path)
    domain = DOMAIN_NODE.replace("  - status: accepted", "  - status: deprecated")
    write_tree(tmp_path, domain)
    report = adopt_template(tmp_path)
    assert "directive run-it" in {entity.label for entity in report.proposed}
    assert any(note.startswith("directive run-it was deprecated") for note in report.notes)
    assert not any("node domain" in note for note in report.notes)


@pytest.mark.parametrize(
    ("before", "after"),
    [
        ('status: "accepted"\n', 'status: "proposed"\n'),
        ("status: 'accepted'\n", "status: 'proposed'\n"),
        ("status:   accepted\n", "status:   proposed\n"),
    ],
)
def test_a_quoted_value_keeps_its_form(tmp_path: Path, before: str, after: str) -> None:
    with_history(tmp_path)
    domain = DOMAIN_NODE.replace("status: accepted\norigin", f"{before}origin", 1)
    write_tree(tmp_path, domain)
    assert not adopt_template(tmp_path).problems
    assert f"{after}origin" in text_of(tmp_path)


def test_a_flow_exception_changes_on_its_line(tmp_path: Path) -> None:
    with_history(tmp_path)
    block = "exceptions:\n  - directive: run-it\n    reason: A prototype.\n    status: accepted\n"
    flow = "exceptions: [{directive: run-it, reason: A prototype., status: accepted}]\n"
    write_tree(tmp_path, child=CHILD_NODE.replace(block, flow))
    assert not adopt_template(tmp_path).problems
    assert "status: proposed}]" in text_of(tmp_path, CHILD_PATH)


def test_a_word_in_another_key_does_not_change(tmp_path: Path) -> None:
    with_history(tmp_path)
    block = "exceptions:\n  - directive: run-it\n    reason: A prototype.\n    status: accepted\n"
    flow = "exceptions: [{directive: run-it, reason: 'x-status: accepted', status: accepted}]\n"
    write_tree(tmp_path, child=CHILD_NODE.replace(block, flow))
    assert not adopt_template(tmp_path).problems
    assert "reason: 'x-status: accepted', status: proposed}]" in text_of(tmp_path, CHILD_PATH)


def test_a_value_on_the_next_line_needs_a_person(tmp_path: Path) -> None:
    with_history(tmp_path)
    domain = DOMAIN_NODE.replace("status: accepted\norigin", "status:\n  accepted\norigin", 1)
    write_tree(tmp_path, domain)
    report = adopt_template(tmp_path)
    assert [(problem.code, problem.line) for problem in report.problems] == [("adopt", 5)]
    assert "node domain" in report.problems[0].message
    assert report.runtime is None
    assert not (tmp_path / "AGENTS.md").exists()


def test_a_crlf_file_keeps_its_line_ends(tmp_path: Path) -> None:
    with_history(tmp_path)
    write_tree(tmp_path)
    path = tmp_path / DOMAIN_PATH
    path.write_bytes(DOMAIN_NODE.replace("\n", "\r\n").encode())
    adopt_template(tmp_path)
    data = path.read_bytes()
    assert b"status: proposed\r\norigin" in data
    assert data.count(b"\r\n") == DOMAIN_NODE.count("\n")


def test_a_cr_file_keeps_its_line_ends(tmp_path: Path) -> None:
    with_history(tmp_path)
    write_tree(tmp_path)
    path = tmp_path / DOMAIN_PATH
    path.write_bytes(DOMAIN_NODE.replace("\n", "\r").encode())
    assert not adopt_template(tmp_path).problems
    data = path.read_bytes()
    assert b"status: proposed\rorigin" in data
    assert b"\n" not in data


def test_a_status_in_backticks_keeps_its_backticks(tmp_path: Path) -> None:
    with_history(tmp_path)
    line = "- status: accepted"
    assert line in DOMAIN_NODE
    write_tree(tmp_path, domain=DOMAIN_NODE.replace(line, "- status: `accepted`"))
    assert not adopt_template(tmp_path).problems
    assert "- status: `proposed`" in text_of(tmp_path, DOMAIN_PATH)


def test_a_longer_word_in_another_key_does_not_change(tmp_path: Path) -> None:
    with_history(tmp_path)
    block = "exceptions:\n  - directive: run-it\n    reason: A prototype.\n    status: accepted\n"
    flow = "exceptions: [{directive: run-it, reason: 'status: accepted-soon', status: accepted}]\n"
    write_tree(tmp_path, child=CHILD_NODE.replace(block, flow))
    assert not adopt_template(tmp_path).problems
    assert "reason: 'status: accepted-soon', status: proposed}]" in text_of(tmp_path, CHILD_PATH)


def test_a_failed_import_stays_in_the_report_when_a_node_does_not_parse(tmp_path: Path) -> None:
    with_history(tmp_path)
    write_tree(tmp_path)
    (tmp_path / "knowledge/bad").mkdir()
    (tmp_path / "knowledge/bad/node.md").write_text("<<<<<<< before\n", encoding="utf-8")
    (tmp_path / "shared.md").write_text("Shared.\n", encoding="utf-8")
    (tmp_path / "CLAUDE.md").symlink_to("shared.md")
    found = {problem.code for problem in adopt_template(tmp_path).problems}
    assert "import" in found
    assert found != {"import"}


def test_a_node_that_does_not_parse_stops_each_later_step(tmp_path: Path) -> None:
    with_history(tmp_path)
    write_tree(tmp_path)
    (tmp_path / "knowledge/bad").mkdir()
    (tmp_path / "knowledge/bad/node.md").write_text("<<<<<<< before\n", encoding="utf-8")
    (tmp_path / "CLAUDE.md").write_text("Own text.\n", encoding="utf-8")
    before = text_of(tmp_path)
    report = adopt_template(tmp_path)
    assert report.problems
    assert report.runtime is None
    assert report.imported == ("CLAUDE.md",)
    assert text_of(tmp_path) == before
    assert not (tmp_path / "AGENTS.md").exists()


def test_an_unreadable_base_stops_each_later_step(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    write_tree(tmp_path)
    before = text_of(tmp_path)
    failure = Base(problems=[Problem(tmp_path, 1, "base", "git failed")])
    monkeypatch.setattr(adopt_module, "read_base", lambda _: failure)
    report = adopt_template(tmp_path)
    assert codes(report.problems) == ["base"]
    assert report.runtime is None
    assert text_of(tmp_path) == before


def test_a_file_that_does_not_parse_at_the_last_commit_stays(tmp_path: Path) -> None:
    with_history(tmp_path)
    write_tree(tmp_path)
    path = tmp_path / DOMAIN_PATH
    good = path.read_text(encoding="utf-8")
    path.write_text("not a node\n", encoding="utf-8")
    git(tmp_path, "add", "-A")
    git(tmp_path, "commit", "-qm", "bad node")
    path.write_text(good, encoding="utf-8")
    assert adopt_template(tmp_path).proposed == ()
    assert text_of(tmp_path) == good


def test_a_read_only_node_is_a_problem(tmp_path: Path) -> None:
    with_history(tmp_path)
    write_tree(tmp_path)
    path = tmp_path / DOMAIN_PATH
    path.chmod(0o444)
    try:
        report = adopt_template(tmp_path)
    finally:
        path.chmod(0o644)
    assert [(problem.path, problem.code) for problem in report.problems] == [(path, "adopt")]
    assert report.runtime is None


def test_a_hand_written_agents_file_stays(tmp_path: Path) -> None:
    with_history(tmp_path)
    write_tree(tmp_path)
    (tmp_path / "AGENTS.md").write_text("Mine.\n", encoding="utf-8")
    report = adopt_template(tmp_path)
    assert codes(report.problems) == ["not-generated"]
    assert text_of(tmp_path, "AGENTS.md") == "Mine.\n"


def test_each_entity_in_one_file_changes(tmp_path: Path) -> None:
    with_history(tmp_path)
    write_tree(tmp_path)
    second = "knowledge/second/node.md"
    (tmp_path / "knowledge/second").mkdir()
    text = DOMAIN_NODE.replace("id: domain", "id: second").replace("run-it", "run-two")
    text = text.replace("run-other", "run-three").replace("Run the", "Start the")
    text = text.replace("pointers:\n  - kind: ka:TextPointer\n    target: child\n", "")
    text = text.replace("    trigger: You need the child.\n", "")
    (tmp_path / second).write_text(text, encoding="utf-8")
    set_text(
        tmp_path,
        "trigger: You need the domain.\n",
        "trigger: You need the domain.\n  - kind: ka:TextPointer\n"
        "    target: second\n    trigger: You need the second.\n",
        "knowledge/node.md",
    )
    report = adopt_template(tmp_path)
    assert not report.problems
    assert "status: accepted" not in text_of(tmp_path)
    assert "status: accepted" not in text_of(tmp_path, second)


def test_the_command_prints_each_step(tmp_path: Path) -> None:
    with_history(tmp_path)
    write_tree(tmp_path)
    (tmp_path / "CLAUDE.md").write_text("Own text.\n", encoding="utf-8")
    result = RUNNER.invoke(app, ["adopt", str(tmp_path)])
    assert result.exit_code == 0
    assert "added the import of the root to CLAUDE.md" in result.output
    assert f"{tmp_path / DOMAIN_PATH}:5: node domain was accepted, now proposed" in result.output
    assert "3 entities set to proposed, 3 files written, 0 problems" in result.output


def test_the_command_prints_a_note(tmp_path: Path) -> None:
    write_tree(tmp_path)
    result = RUNNER.invoke(app, ["adopt", str(tmp_path)])
    assert result.exit_code == 0
    assert "note: This folder is not a git repository" in result.output


def test_the_command_fails_on_a_problem(tmp_path: Path) -> None:
    write_tree(tmp_path)
    (tmp_path / "AGENTS.md").write_text("Mine.\n", encoding="utf-8")
    result = RUNNER.invoke(app, ["adopt", str(tmp_path)])
    assert result.exit_code == 1
    assert ": not-generated: " in result.output


def test_each_code_is_named() -> None:
    assert ADOPT_CODES == ("adopt", "import")


def test_no_instruction_file_needs_no_import(tmp_path: Path) -> None:
    assert add_root_import(tmp_path) == ((), [])
    assert instruction_notes(tmp_path) == []


@pytest.mark.parametrize(
    ("before", "after"),
    [
        ("Own text.\n", "Own text.\n\n@AGENTS.md\n"),
        ("Own text.", "Own text.\n\n@AGENTS.md\n"),
        ("", "@AGENTS.md\n"),
    ],
)
def test_the_import_goes_at_the_end(tmp_path: Path, before: str, after: str) -> None:
    (tmp_path / "CLAUDE.md").write_text(before, encoding="utf-8")
    assert add_root_import(tmp_path) == (("CLAUDE.md",), [])
    assert text_of(tmp_path, "CLAUDE.md") == after
    assert add_root_import(tmp_path) == ((), [])
    assert text_of(tmp_path, "CLAUDE.md") == after
    assert instruction_notes(tmp_path) == []


def test_the_import_in_a_tool_folder_resolves_from_the_file(tmp_path: Path) -> None:
    (tmp_path / ".claude").mkdir()
    (tmp_path / ".claude/CLAUDE.md").write_text("Own text.\n", encoding="utf-8")
    assert add_root_import(tmp_path) == ((".claude/CLAUDE.md",), [])
    assert text_of(tmp_path, ".claude/CLAUDE.md") == "Own text.\n\n@../AGENTS.md\n"
    assert instruction_notes(tmp_path) == []


def test_one_import_covers_both_files(tmp_path: Path) -> None:
    (tmp_path / ".claude").mkdir()
    (tmp_path / ".claude/CLAUDE.md").write_text("Other.\n", encoding="utf-8")
    (tmp_path / "CLAUDE.md").write_text("Own.\n", encoding="utf-8")
    assert add_root_import(tmp_path)[0] == ("CLAUDE.md",)
    assert text_of(tmp_path, ".claude/CLAUDE.md") == "Other.\n"


def test_an_import_in_the_tool_folder_is_enough(tmp_path: Path) -> None:
    (tmp_path / ".claude").mkdir()
    (tmp_path / ".claude/CLAUDE.md").write_text("@../AGENTS.md\n", encoding="utf-8")
    (tmp_path / "CLAUDE.md").write_text("Own.\n", encoding="utf-8")
    assert add_root_import(tmp_path) == ((), [])
    assert text_of(tmp_path, "CLAUDE.md") == "Own.\n"


def test_a_local_file_is_not_changed_and_gets_a_note(tmp_path: Path) -> None:
    (tmp_path / "CLAUDE.local.md").write_text("Mine.\n", encoding="utf-8")
    assert add_root_import(tmp_path) == ((), [])
    assert text_of(tmp_path, "CLAUDE.local.md") == "Mine.\n"
    notes = instruction_notes(tmp_path)
    assert len(notes) == 1
    assert "Add the line @AGENTS.md to CLAUDE.local.md" in notes[0]


def test_a_local_file_with_an_import_is_enough(tmp_path: Path) -> None:
    (tmp_path / "CLAUDE.local.md").write_text("@AGENTS.md\n", encoding="utf-8")
    (tmp_path / "CLAUDE.md").write_text("Own.\n", encoding="utf-8")
    assert add_root_import(tmp_path) == ((), [])
    assert instruction_notes(tmp_path) == []


def test_each_file_with_no_import_gets_a_note(tmp_path: Path) -> None:
    (tmp_path / ".claude").mkdir()
    (tmp_path / ".claude/CLAUDE.md").write_text("Other.\n", encoding="utf-8")
    (tmp_path / "CLAUDE.md").write_text("Own.\n", encoding="utf-8")
    notes = instruction_notes(tmp_path)
    assert "Add the line @AGENTS.md to CLAUDE.md" in notes[0]
    assert "Add the line @../AGENTS.md to .claude/CLAUDE.md" in notes[1]


@pytest.mark.parametrize(
    "text",
    [
        "Read `@AGENTS.md` first.\n",
        "```text\n@AGENTS.md\n```\n",
        "<!-- @AGENTS.md -->\n",
        "@AGENTS.md.old\n",
        "See x@AGENTS.md here.\n",
    ],
)
def test_a_mention_is_not_an_import(tmp_path: Path, text: str) -> None:
    (tmp_path / "CLAUDE.md").write_text(text, encoding="utf-8")
    assert add_root_import(tmp_path)[0] == ("CLAUDE.md",)
    assert text_of(tmp_path, "CLAUDE.md") == f"{text}\n@AGENTS.md\n"


@pytest.mark.parametrize(
    "text",
    [
        "@AGENTS.md\n",
        "@./AGENTS.md\n",
        "Read @AGENTS.md first.\n",
        "- Rules\n- @AGENTS.md\n",
    ],
)
def test_an_import_counts_in_each_form(tmp_path: Path, text: str) -> None:
    (tmp_path / "CLAUDE.md").write_text(text, encoding="utf-8")
    assert add_root_import(tmp_path) == ((), [])
    assert text_of(tmp_path, "CLAUDE.md") == text


def test_a_link_to_the_root_counts_as_an_import(tmp_path: Path) -> None:
    (tmp_path / "AGENTS.md").write_text("Root.\n", encoding="utf-8")
    (tmp_path / "CLAUDE.md").symlink_to("AGENTS.md")
    assert add_root_import(tmp_path) == ((), [])
    assert text_of(tmp_path, "AGENTS.md") == "Root.\n"
    assert instruction_notes(tmp_path) == []


def test_a_link_to_another_file_is_a_problem(tmp_path: Path) -> None:
    (tmp_path / "shared.md").write_text("Shared.\n", encoding="utf-8")
    (tmp_path / "CLAUDE.md").symlink_to("shared.md")
    imported, problems = add_root_import(tmp_path)
    assert imported == ()
    assert [(problem.path, problem.code) for problem in problems] == [
        (tmp_path / "CLAUDE.md", "import")
    ]
    assert text_of(tmp_path, "shared.md") == "Shared.\n"


def test_a_folder_at_the_name_is_a_problem(tmp_path: Path) -> None:
    (tmp_path / "CLAUDE.md").mkdir()
    imported, problems = add_root_import(tmp_path)
    assert imported == ()
    assert codes(problems) == ["import"]


def test_a_file_that_is_not_utf8_gets_the_import(tmp_path: Path) -> None:
    (tmp_path / "CLAUDE.md").write_bytes(b"\xff\xfe\n")
    assert add_root_import(tmp_path)[0] == ("CLAUDE.md",)
    assert (tmp_path / "CLAUDE.md").read_bytes() == b"\xff\xfe\n\n@AGENTS.md\n"
