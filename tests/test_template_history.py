# pyright: reportUnknownArgumentType=false, reportUnknownLambdaType=false
import json
import re
import shutil
import subprocess
from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING

import pytest
from typer.testing import CliRunner

from engine.cli import app
from engine.governance.base import read_head_file
from engine.parser import ParsedNode, parse_source
from engine.template import (
    HISTORY_CODES,
    HISTORY_FILE,
    Entry,
    history_drift,
    record_history,
)
from engine.template import history as history_module

if TYPE_CHECKING:
    from collections.abc import Iterable

    from engine.parser.result import Problem

REPO = Path(__file__).resolve().parents[1]
RUNNER = CliRunner()
GIT = shutil.which("git") or "git"
USAGE_ERROR = 2
ROOT_NODE = """---
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
"""
DOMAIN_NODE = """---
id: domain
kind: densho:Domain
title: Domain
status: proposed
origin: template
knowledge_type: domain
sources:
  - first
  - second
exceptions:
  - directive: run-it
    reason: A prototype.
    status: proposed
---

## Definition

The meaning of the domain.

## Directives

- Run the check. ^run-it
  - scope: subtree
  - basis: judgment
  - status: proposed
  - origin: template
"""


def write_tree(folder: Path) -> Path:
    (folder / "knowledge/nodes/domain").mkdir(parents=True)
    (folder / "knowledge/governance/language/branches").mkdir(parents=True)
    (folder / "knowledge/governance/language/branches/.gitkeep").write_text("", encoding="utf-8")
    (folder / "knowledge/governance/language/vocabulary.yaml").write_text(
        "verbs: []\n", encoding="utf-8"
    )
    (folder / "knowledge/node.md").write_text(ROOT_NODE, encoding="utf-8")
    (folder / "knowledge/nodes/domain/node.md").write_text(DOMAIN_NODE, encoding="utf-8")
    (folder / "copier.yml").write_text("_min_copier_version: '9'\n", encoding="utf-8")
    return folder


def git(folder: Path, *arguments: str) -> None:
    subprocess.run(  # noqa: S603
        [GIT, "-C", str(folder), *arguments], capture_output=True, check=True
    )


def committed(folder: Path) -> Path:
    write_tree(folder)
    git(folder, "init", "-q", "--template=", "--initial-branch=main")
    git(folder, "config", "user.name", "Test")
    git(folder, "config", "user.email", "test@example.com")
    assert not record_history(folder).problems
    git(folder, "add", "-A")
    git(folder, "commit", "-qm", "first")
    return folder


def lines_of(folder: Path) -> list[Entry]:
    text = (folder / HISTORY_FILE).read_text(encoding="utf-8")
    return [Entry.model_validate_json(line) for line in text.splitlines()]


def by_id(entries: Iterable[Entry]) -> dict[str, Entry]:
    return {entry.id: entry for entry in entries}


def codes(problems: Iterable[Problem]) -> list[str]:
    return [problem.code for problem in problems]


def replace(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    assert old in text
    path.write_text(text.replace(old, new), encoding="utf-8")


def domain_file(folder: Path) -> Path:
    return folder / "knowledge/nodes/domain/node.md"


def test_the_first_change_adds_each_entity(tmp_path: Path) -> None:
    report = record_history(write_tree(tmp_path))
    assert not report.problems
    assert report.entries == tuple(lines_of(tmp_path))
    assert {entry.change for entry in report.entries} == {1}
    assert {entry.action for entry in report.entries} == {"added"}
    assert {entry.fields == [] for entry in report.entries} == {True}
    keys = [(entry.kind, entry.id) for entry in report.entries]
    assert keys == sorted(keys)
    assert keys == [
        ("directive", "run-it"),
        ("exception", "domain/run-it"),
        ("file", "knowledge/governance/language/vocabulary.yaml"),
        ("node", "domain"),
        ("node", "root"),
    ]


def test_an_entry_holds_the_path_and_the_status(tmp_path: Path) -> None:
    entries = by_id(record_history(write_tree(tmp_path)).entries)
    assert entries["run-it"].path == "knowledge/nodes/domain/node.md"
    assert entries["run-it"].status == "proposed"
    assert entries["domain/run-it"].path == "knowledge/nodes/domain/node.md"
    assert entries["domain/run-it"].status == "proposed"
    assert entries["root"].path == "knowledge/node.md"
    file_entry = entries["knowledge/governance/language/vocabulary.yaml"]
    assert file_entry.path == "knowledge/governance/language/vocabulary.yaml"
    assert file_entry.status is None


def test_content_leaves_out_status_id_and_origin(tmp_path: Path) -> None:
    entries = by_id(record_history(write_tree(tmp_path)).entries)
    assert set(entries["domain"].content) == {
        "definition",
        "kind",
        "knowledge_type",
        "sources",
        "title",
    }
    assert set(entries["run-it"].content) == {"basis", "holder", "scope", "text"}
    assert set(entries["domain/run-it"].content) == {"reason"}
    assert set(entries["knowledge/governance/language/vocabulary.yaml"].content) == {"bytes"}
    assert all(len(digest) == 16 for digest in entries["domain"].content.values())  # noqa: PLR2004


def test_a_second_run_adds_nothing(tmp_path: Path) -> None:
    write_tree(tmp_path)
    record_history(tmp_path)
    before = (tmp_path / HISTORY_FILE).read_bytes()
    report = record_history(tmp_path)
    assert report.entries == ()
    assert not report.problems
    assert (tmp_path / HISTORY_FILE).read_bytes() == before


@pytest.mark.parametrize(
    ("old", "new", "entity", "fields"),
    [
        ("The meaning of the domain.", "Another meaning.", "domain", ["definition"]),
        ("Run the check. ^run-it", "Run the other check. ^run-it", "run-it", ["text"]),
        ("  - scope: subtree", "  - scope: node", "run-it", ["scope"]),
        ("reason: A prototype.", "reason: A draft.", "domain/run-it", ["reason"]),
        ("title: Domain", "title: Area", "domain", ["title"]),
        ("  - second\n", "  - third\n", "domain", ["sources"]),
    ],
)
def test_a_change_names_its_field(
    tmp_path: Path, old: str, new: str, entity: str, fields: list[str]
) -> None:
    write_tree(tmp_path)
    first = by_id(record_history(tmp_path).entries)[entity]
    replace(domain_file(tmp_path), old, new)
    report = record_history(tmp_path)
    assert [entry.id for entry in report.entries] == [entity]
    entry = report.entries[0]
    assert entry.change == 2  # noqa: PLR2004
    assert entry.action == "changed"
    assert entry.fields == fields
    assert entry.content != first.content
    assert report.entries == tuple(lines_of(tmp_path)[-1:])


def test_a_status_change_keeps_the_content(tmp_path: Path) -> None:
    write_tree(tmp_path)
    first = by_id(record_history(tmp_path).entries)["run-it"]
    replace(domain_file(tmp_path), "  - status: proposed", "  - status: accepted")
    entry = record_history(tmp_path).entries[0]
    assert (entry.id, entry.fields, entry.status) == ("run-it", ["status"], "accepted")
    assert entry.content == first.content


def test_a_moved_file_changes_only_the_path(tmp_path: Path) -> None:
    write_tree(tmp_path)
    first = by_id(record_history(tmp_path).entries)
    (tmp_path / "knowledge/nodes/moved").mkdir(parents=True)
    domain_file(tmp_path).rename(tmp_path / "knowledge/nodes/moved/node.md")
    entries = by_id(record_history(tmp_path).entries)
    assert set(entries) == {"domain", "run-it", "domain/run-it"}
    for name, entry in entries.items():
        assert entry.fields == ["path"]
        assert entry.path == "knowledge/nodes/moved/node.md"
        assert entry.content == first[name].content


def test_a_directive_on_another_node_changes_its_holder(tmp_path: Path) -> None:
    write_tree(tmp_path)
    record_history(tmp_path)
    block = (
        "- Run the check. ^run-it\n  - scope: subtree\n  - basis: judgment\n  - status: proposed\n"
    )
    block += "  - origin: template\n"
    replace(domain_file(tmp_path), block, "")
    replace(domain_file(tmp_path), "## Directives\n\n", "")
    replace(
        domain_file(tmp_path),
        "exceptions:\n  - directive: run-it\n    reason: A prototype.\n    status: proposed\n",
        "",
    )
    root = tmp_path / "knowledge/node.md"
    root.write_text(f"{ROOT_NODE}\n## Directives\n\n{block}", encoding="utf-8")
    entries = by_id(record_history(tmp_path).entries)
    assert entries["run-it"].fields == ["holder", "path"]
    assert entries["domain/run-it"].action == "removed"


def test_a_field_that_appears_or_goes_is_named(tmp_path: Path) -> None:
    write_tree(tmp_path)
    record_history(tmp_path)
    replace(domain_file(tmp_path), "sources:\n  - first\n  - second\n", "")
    gone = next(entry for entry in record_history(tmp_path).entries if entry.id == "domain")
    assert "sources" in gone.fields
    assert "sources" not in gone.content
    replace(
        domain_file(tmp_path),
        "knowledge_type: domain\n",
        "knowledge_type: domain\nsources:\n  - third\n",
    )
    back = next(entry for entry in record_history(tmp_path).entries if entry.id == "domain")
    assert "sources" in back.fields
    assert "sources" in back.content


def test_a_formatter_adds_no_line(tmp_path: Path) -> None:
    write_tree(tmp_path)
    record_history(tmp_path)
    replace(domain_file(tmp_path), "  - first\n  - second\n", "  - second\n  - first\n")
    replace(domain_file(tmp_path), "The meaning of the domain.", "The meaning\nof the   domain.")
    assert record_history(tmp_path).entries == ()


def test_the_order_of_pointers_adds_no_line(tmp_path: Path) -> None:
    write_tree(tmp_path)
    pointers = (
        "pointers:\n"
        "  - kind: densho:TextPointer\n    target: domain\n    trigger: You need it.\n"
        "  - kind: densho:TextPointer\n    target: root\n    trigger: You need that.\n"
    )
    swapped = (
        "pointers:\n"
        "  - kind: densho:TextPointer\n    target: root\n    trigger: You need that.\n"
        "  - kind: densho:TextPointer\n    target: domain\n    trigger: You need it.\n"
    )
    root = tmp_path / "knowledge/node.md"
    front = ROOT_NODE.split("pointers:", maxsplit=1)[0]
    root.write_text(f"{front}{pointers}---\n", encoding="utf-8")
    record_history(tmp_path)
    root.write_text(f"{front}{swapped}---\n", encoding="utf-8")
    assert record_history(tmp_path).entries == ()


def test_a_removed_entity_then_added_again(tmp_path: Path) -> None:
    write_tree(tmp_path)
    record_history(tmp_path)
    saved = domain_file(tmp_path).read_text(encoding="utf-8")
    shutil.rmtree(tmp_path / "knowledge/nodes/domain")
    entries = by_id(record_history(tmp_path).entries)
    assert set(entries) == {"domain", "run-it", "domain/run-it"}
    gone = entries["domain"]
    assert (gone.action, gone.fields, gone.content) == ("removed", [], {})
    assert gone.path == "knowledge/nodes/domain/node.md"
    assert gone.status == "proposed"
    (tmp_path / "knowledge/nodes/domain").mkdir(parents=True)
    domain_file(tmp_path).write_text(saved, encoding="utf-8")
    entries = by_id(record_history(tmp_path).entries)
    assert entries["domain"].action == "added"
    assert entries["domain"].change == 3  # noqa: PLR2004


def test_a_language_file_is_a_file_entry(tmp_path: Path) -> None:
    write_tree(tmp_path)
    record_history(tmp_path)
    branch = tmp_path / "knowledge/governance/language/branches/domain.yaml"
    branch.write_text("verbs: [sort]\n", encoding="utf-8")
    entries = by_id(record_history(tmp_path).entries)
    assert set(entries) == {"knowledge/governance/language/branches/domain.yaml"}
    vocabulary = tmp_path / "knowledge/governance/language/vocabulary.yaml"
    vocabulary.write_text("verbs: [run]\n", encoding="utf-8")
    entry = record_history(tmp_path).entries[0]
    assert (entry.kind, entry.action, entry.fields) == ("file", "changed", ["bytes"])
    branch.unlink()
    assert record_history(tmp_path).entries[0].action == "removed"


def test_an_unreadable_language_file_is_a_problem(tmp_path: Path) -> None:
    write_tree(tmp_path)
    locked = tmp_path / "knowledge/governance/language/vocabulary.yaml"
    locked.chmod(0o000)
    try:
        report = record_history(tmp_path)
    finally:
        locked.chmod(0o644)
    assert [(problem.path, problem.code) for problem in report.problems] == [(locked, "history")]
    assert not (tmp_path / HISTORY_FILE).exists()


def test_each_write_has_one_number(tmp_path: Path) -> None:
    write_tree(tmp_path)
    record_history(tmp_path)
    replace(domain_file(tmp_path), "title: Domain", "title: Area")
    replace(tmp_path / "knowledge/node.md", "title: Root", "title: Top")
    assert [entry.change for entry in record_history(tmp_path).entries] == [2, 2]
    replace(tmp_path / "knowledge/node.md", "title: Top", "title: Peak")
    assert [entry.change for entry in record_history(tmp_path).entries] == [3]


def test_a_tree_that_does_not_parse_writes_nothing(tmp_path: Path) -> None:
    write_tree(tmp_path)
    domain_file(tmp_path).write_text("not a node\n", encoding="utf-8")
    report = record_history(tmp_path)
    assert report.problems
    assert report.entries == ()
    assert not (tmp_path / HISTORY_FILE).exists()


def test_a_path_that_is_not_utf8_is_a_problem(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    write_tree(tmp_path)
    parsed = parse_source(ROOT_NODE, tmp_path / "knowledge/node.md")
    assert isinstance(parsed, ParsedNode)
    renamed = ParsedNode(tmp_path / "knowledge/nodes/\udcff/node.md", parsed.node, parsed.locations)
    monkeypatch.setattr(history_module, "parse_tree", lambda _: ([renamed], []))
    report = record_history(tmp_path)
    assert codes(report.problems) == ["path"]
    assert not (tmp_path / HISTORY_FILE).exists()


def test_a_project_cannot_write_the_history(tmp_path: Path) -> None:
    write_tree(tmp_path)
    (tmp_path / "copier.yml").unlink()
    for report in (record_history(tmp_path), record_history(tmp_path, verify=True)):
        assert codes(report.problems) == ["not-template"]
        assert report.problems[0].path == tmp_path / HISTORY_FILE
    assert not (tmp_path / HISTORY_FILE).exists()


def test_drift_runs_in_a_project_and_writes_nothing(tmp_path: Path) -> None:
    write_tree(tmp_path)
    record_history(tmp_path)
    (tmp_path / "copier.yml").unlink()
    before = (tmp_path / HISTORY_FILE).read_bytes()
    (tmp_path / "knowledge/nodes/moved").mkdir(parents=True)
    domain_file(tmp_path).rename(tmp_path / "knowledge/nodes/moved/node.md")
    replace(tmp_path / "knowledge/nodes/moved/node.md", "title: Domain", "title: Area")
    report = history_drift(tmp_path)
    assert report.change == 2  # noqa: PLR2004
    entries = by_id(report.entries)
    assert entries["domain"].fields == ["path", "title"]
    assert entries["domain"].path == "knowledge/nodes/moved/node.md"
    assert (tmp_path / HISTORY_FILE).read_bytes() == before


def test_drift_with_no_history_lists_each_entity(tmp_path: Path) -> None:
    write_tree(tmp_path)
    report = history_drift(tmp_path)
    assert report.change == 1
    assert {entry.action for entry in report.entries} == {"added"}
    assert not (tmp_path / HISTORY_FILE).exists()


DROPPED_NOTE = (
    "4 entities of dropped are not in this tree, because disciplines leaves the discipline out."
)


def taxonomy_node(node_id: str, kind: str, broader: str, directive: str = "") -> str:
    rules = (
        f"\n## Directives\n\n- Run the check. ^{directive}\n  - scope: subtree\n"
        "  - basis: judgment\n  - status: proposed\n  - origin: template\n"
        if directive
        else ""
    )
    return (
        f"---\nid: {node_id}\nkind: {kind}\ntitle: {node_id.title()}\nstatus: proposed\n"
        f"origin: template\nknowledge_type: domain\nbroader:\n  - {broader}\n---\n\n"
        f"## Definition\n\nThe meaning of {node_id}.\n{rules}"
    )


def write_disciplines(folder: Path) -> None:
    nodes = folder / "knowledge/nodes/domain"
    files = {
        "kept/node.md": taxonomy_node("kept", "densho:Discipline", "domain"),
        "kept/near/node.md": taxonomy_node("near", "densho:Concept", "kept"),
        "dropped/node.md": taxonomy_node("dropped", "densho:Discipline", "domain", "check-dropped"),
        "dropped/far/node.md": taxonomy_node("far", "densho:Concept", "dropped"),
    }
    for name, text in files.items():
        (nodes / name).parent.mkdir(parents=True, exist_ok=True)
        (nodes / name).write_text(text, encoding="utf-8")
    branches = folder / "knowledge/governance/language/branches"
    for name in ("kept", "dropped"):
        (branches / f"{name}.yaml").write_text("verbs: []\n", encoding="utf-8")


def select_kept(folder: Path, answer: str | None = "disciplines: [kept]\n") -> None:
    (folder / "copier.yml").unlink()
    shutil.rmtree(folder / "knowledge/nodes/domain/dropped")
    (folder / "knowledge/governance/language/branches/dropped.yaml").unlink()
    if answer is not None:
        (folder / ".copier-answers.yml").write_text(answer, encoding="utf-8")


def test_drift_counts_the_entities_of_a_left_out_discipline(tmp_path: Path) -> None:
    write_tree(tmp_path)
    write_disciplines(tmp_path)
    assert not record_history(tmp_path).problems
    select_kept(tmp_path)
    (tmp_path / "knowledge/nodes/domain/kept/near/node.md").unlink()
    report = history_drift(tmp_path)
    assert report.problems == []
    assert report.notes == [
        "4 entities of dropped are not in this tree, because disciplines leaves the discipline out."
    ]
    assert [(entry.id, entry.action) for entry in report.entries] == [("near", "removed")]


def test_drift_with_no_answer_lists_each_removal(tmp_path: Path) -> None:
    write_tree(tmp_path)
    write_disciplines(tmp_path)
    assert not record_history(tmp_path).problems
    select_kept(tmp_path, None)
    report = history_drift(tmp_path)
    assert report.notes == []
    assert sorted(entry.id for entry in report.entries) == [
        "check-dropped",
        "dropped",
        "far",
        "knowledge/governance/language/branches/dropped.yaml",
    ]


def test_drift_lists_a_change_inside_a_left_out_discipline(tmp_path: Path) -> None:
    write_tree(tmp_path)
    write_disciplines(tmp_path)
    assert not record_history(tmp_path).problems
    (tmp_path / "copier.yml").unlink()
    (tmp_path / ".copier-answers.yml").write_text("disciplines: [kept]\n", encoding="utf-8")
    replace(tmp_path / "knowledge/nodes/domain/dropped/far/node.md", "title: Far", "title: Near")
    report = history_drift(tmp_path)
    assert report.notes == []
    assert [(entry.id, entry.action) for entry in report.entries] == [("far", "changed")]


def test_drift_fails_on_a_bad_answer(tmp_path: Path) -> None:
    write_tree(tmp_path)
    record_history(tmp_path)
    (tmp_path / ".copier-answers.yml").write_text("disciplines: kept\n", encoding="utf-8")
    assert codes(history_drift(tmp_path).problems) == ["select"]


def test_the_command_prints_the_count_of_each_left_out_discipline(tmp_path: Path) -> None:
    write_tree(tmp_path)
    write_disciplines(tmp_path)
    assert not record_history(tmp_path).problems
    select_kept(tmp_path)
    result = RUNNER.invoke(app, ["history", str(tmp_path), "--drift"])
    assert result.exit_code == 0
    assert result.output.splitlines() == [
        f"note: {DROPPED_NOTE}",
        "0 entities differ from the history, 0 problems",
    ]


def test_drift_counts_a_nested_discipline_apart(tmp_path: Path) -> None:
    write_tree(tmp_path)
    write_disciplines(tmp_path)
    nodes = tmp_path / "knowledge/nodes/domain/dropped"
    (nodes / "inner/leaf").mkdir(parents=True)
    (nodes / "inner/node.md").write_text(
        taxonomy_node("inner", "densho:Discipline", "dropped"), encoding="utf-8"
    )
    (nodes / "inner/leaf/node.md").write_text(
        taxonomy_node("leaf", "densho:Concept", "inner"), encoding="utf-8"
    )
    assert not record_history(tmp_path).problems
    select_kept(tmp_path)
    report = history_drift(tmp_path)
    assert report.notes == [
        DROPPED_NOTE,
        "2 entities of inner are not in this tree, because disciplines leaves the discipline out.",
    ]
    assert report.entries == ()


def test_record_writes_each_removal_when_the_answer_leaves_a_discipline_out(
    tmp_path: Path,
) -> None:
    write_tree(tmp_path)
    write_disciplines(tmp_path)
    assert not record_history(tmp_path).problems
    shutil.rmtree(tmp_path / "knowledge/nodes/domain/dropped")
    (tmp_path / "knowledge/governance/language/branches/dropped.yaml").unlink()
    (tmp_path / ".copier-answers.yml").write_text("disciplines: [kept]\n", encoding="utf-8")
    report = record_history(tmp_path)
    assert (report.notes, report.problems) == ([], [])
    removed = sorted(entry.id for entry in lines_of(tmp_path) if entry.action == "removed")
    assert removed == [
        "check-dropped",
        "dropped",
        "far",
        "knowledge/governance/language/branches/dropped.yaml",
    ]


def test_verify_writes_the_change_then_fails(tmp_path: Path) -> None:
    committed(tmp_path)
    replace(domain_file(tmp_path), "title: Domain", "title: Area")
    report = record_history(tmp_path, verify=True)
    assert codes(report.problems) == ["changed"]
    assert report.problems[0].path == tmp_path / HISTORY_FILE
    assert "change 2" in report.problems[0].message
    assert lines_of(tmp_path)[-1].id == "domain"
    second = record_history(tmp_path, verify=True)
    assert not second.problems
    assert second.entries == ()


def test_verify_fails_when_the_index_lacks_the_file(tmp_path: Path) -> None:
    write_tree(tmp_path)
    git(tmp_path, "init", "-q", "--template=", "--initial-branch=main")
    assert codes(record_history(tmp_path, verify=True).problems) == ["changed"]
    report = record_history(tmp_path, verify=True)
    assert codes(report.problems) == ["not-staged"]
    assert report.problems[0].path == tmp_path / HISTORY_FILE
    git(tmp_path, "add", str(HISTORY_FILE))
    assert not record_history(tmp_path, verify=True).problems


def test_verify_notes_a_folder_with_no_git(tmp_path: Path) -> None:
    write_tree(tmp_path)
    record_history(tmp_path)
    report = record_history(tmp_path, verify=True)
    assert not report.problems
    assert report.notes == [history_module.NO_INDEX_NOTE]


def test_plain_run_does_not_check_the_index(tmp_path: Path) -> None:
    write_tree(tmp_path)
    git(tmp_path, "init", "-q", "--template=", "--initial-branch=main")
    record_history(tmp_path)
    assert not record_history(tmp_path).problems


def test_verify_passes_an_empty_tree_with_no_file(tmp_path: Path) -> None:
    (tmp_path / "knowledge").mkdir()
    (tmp_path / "copier.yml").write_text("{}\n", encoding="utf-8")
    report = record_history(tmp_path, verify=True)
    assert not report.problems
    assert not (tmp_path / HISTORY_FILE).exists()


def test_a_file_cut_inside_a_line_fails_at_the_next_line(tmp_path: Path) -> None:
    committed(tmp_path)
    path = tmp_path / HISTORY_FILE
    first = path.read_text(encoding="utf-8").splitlines()[0]
    path.write_text(first, encoding="utf-8")
    report = record_history(tmp_path)
    assert [(problem.code, problem.line) for problem in report.problems] == [("rewritten", 2)]


def test_verify_in_a_repository_passes_with_no_nodes_and_no_file(tmp_path: Path) -> None:
    (tmp_path / "knowledge").mkdir()
    (tmp_path / "copier.yml").write_text("{}\n", encoding="utf-8")
    git(tmp_path, "init", "-q")
    report = record_history(tmp_path, verify=True)
    assert report.problems == []
    assert not (tmp_path / HISTORY_FILE).exists()


def test_verify_keeps_a_problem_of_the_tree(tmp_path: Path) -> None:
    write_tree(tmp_path)
    git(tmp_path, "init", "-q")
    record_history(tmp_path)
    replace(domain_file(tmp_path), "id: domain\n", "id: Not An ID\n")
    report = record_history(tmp_path, verify=True)
    assert report.problems
    assert "not-staged" not in codes(report.problems)


REVERT_MESSAGE = (
    "The last commit removed history lines, as a git revert does. "
    f"Run git checkout HEAD~1 -- {HISTORY_FILE}, then run the command again."
)


def commit_title(folder: Path, old: str, new: str) -> None:
    replace(domain_file(folder), f"title: {old}", f"title: {new}")
    assert not record_history(folder).problems
    git(folder, "add", "-A")
    git(folder, "commit", "-qm", new)


def test_a_revert_of_the_last_change_fails_the_next_check(tmp_path: Path) -> None:
    committed(tmp_path)
    commit_title(tmp_path, "Domain", "Area")
    before = (tmp_path / HISTORY_FILE).read_bytes()
    git(tmp_path, "revert", "--no-edit", "HEAD")
    report = record_history(tmp_path, verify=True)
    assert [(problem.code, problem.message) for problem in report.problems] == [
        ("rewritten", REVERT_MESSAGE)
    ]
    assert report.problems[0].line == len(before.split(b"\n")) - 1
    git(tmp_path, "checkout", "HEAD~1", "--", str(HISTORY_FILE))
    (entry,) = record_history(tmp_path).entries
    assert (entry.id, entry.action, entry.fields) == ("domain", "changed", ["title"])
    assert (tmp_path / HISTORY_FILE).read_bytes().startswith(before)
    git(tmp_path, "add", "-A")
    git(tmp_path, "commit", "-qm", "record the revert")
    assert record_history(tmp_path, verify=True).problems == []


def test_a_commit_that_removes_an_older_line_fails_and_takes_the_restore(
    tmp_path: Path,
) -> None:
    committed(tmp_path)
    commit_title(tmp_path, "Domain", "Area")
    commit_title(tmp_path, "Area", "Field")
    full = (tmp_path / HISTORY_FILE).read_bytes()
    lines = full.split(b"\n")
    middle = next(index for index, line in enumerate(lines) if b'"change":2' in line)
    (tmp_path / HISTORY_FILE).write_bytes(b"\n".join(lines[:middle] + lines[middle + 1 :]))
    git(tmp_path, "commit", "-qam", "damage")
    assert codes(record_history(tmp_path, verify=True).problems) == ["rewritten"]
    git(tmp_path, "checkout", "HEAD~1", "--", str(HISTORY_FILE))
    assert (tmp_path / HISTORY_FILE).read_bytes() == full
    assert record_history(tmp_path).problems == []
    git(tmp_path, "commit", "-qam", "restore")
    assert record_history(tmp_path, verify=True).problems == []


def test_a_commit_that_keeps_each_parent_line_passes(tmp_path: Path) -> None:
    committed(tmp_path)
    commit_title(tmp_path, "Domain", "Area")
    commit_title(tmp_path, "Area", "Field")
    assert record_history(tmp_path, verify=True).problems == []


def test_a_rewritten_line_fails_at_its_line(tmp_path: Path) -> None:
    committed(tmp_path)
    path = tmp_path / HISTORY_FILE
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    lines[2] = lines[2].replace('"action":"added"', '"action":"added" ')
    path.write_text("".join(lines), encoding="utf-8")
    for report in (record_history(tmp_path), record_history(tmp_path, verify=True)):
        assert [(problem.code, problem.line) for problem in report.problems] == [("rewritten", 3)]


def test_a_shorter_file_fails(tmp_path: Path) -> None:
    committed(tmp_path)
    path = tmp_path / HISTORY_FILE
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    path.write_text("".join(lines[:-1]), encoding="utf-8")
    report = record_history(tmp_path, verify=True)
    assert [(problem.code, problem.line) for problem in report.problems] == [
        ("rewritten", len(lines))
    ]


def test_a_removed_file_fails(tmp_path: Path) -> None:
    committed(tmp_path)
    (tmp_path / HISTORY_FILE).unlink()
    report = record_history(tmp_path, verify=True)
    assert codes(report.problems) == ["rewritten"]
    assert not (tmp_path / HISTORY_FILE).exists()


def test_a_directory_at_the_history_path_is_a_problem(tmp_path: Path) -> None:
    committed(tmp_path)
    path = tmp_path / HISTORY_FILE
    path.unlink()
    path.mkdir()
    report = record_history(tmp_path, verify=True)
    assert codes(report.problems) == ["history"]


def test_read_head_file_needs_a_commit_and_a_file(tmp_path: Path) -> None:
    assert read_head_file(tmp_path, HISTORY_FILE) is None
    git(tmp_path, "init", "-q", "--template=", "--initial-branch=main")
    assert read_head_file(tmp_path, HISTORY_FILE) is None


def test_read_head_file_needs_git(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    committed(tmp_path)
    monkeypatch.setattr("shutil.which", lambda _: None)
    assert read_head_file(tmp_path, HISTORY_FILE) is None


def test_read_head_file_reads_from_a_subfolder(tmp_path: Path) -> None:
    committed(tmp_path)
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub/note.txt").write_text("note\n", encoding="utf-8")
    git(tmp_path, "add", "-A")
    git(tmp_path, "commit", "-qm", "note")
    assert read_head_file(tmp_path / "sub", PurePosixPath("note.txt")) == b"note\n"


@pytest.mark.parametrize(
    ("text", "line"),
    [
        ("not json\n", 1),
        ('{"change":1}\n', 1),
        ("\n", 1),
    ],
)
def test_a_bad_line_is_a_problem(tmp_path: Path, text: str, line: int) -> None:
    write_tree(tmp_path)
    (tmp_path / "knowledge/.densho").mkdir()
    (tmp_path / HISTORY_FILE).write_text(text, encoding="utf-8")
    for report in (record_history(tmp_path), history_drift(tmp_path)):
        assert [(problem.code, problem.line) for problem in report.problems] == [("history", line)]
    assert (tmp_path / HISTORY_FILE).read_text(encoding="utf-8") == text


def entry_line(**fields: object) -> str:
    base: dict[str, object] = {
        "change": 1,
        "kind": "node",
        "id": "root",
        "action": "added",
        "fields": [],
        "path": "knowledge/node.md",
        "status": "proposed",
        "content": {},
    }
    return json.dumps({**base, **fields}) + "\n"


@pytest.mark.parametrize(
    "line",
    [
        entry_line(extra=1),
        entry_line(change="1"),
        entry_line(change=0),
        entry_line(kind="other"),
        entry_line(action="other"),
        entry_line(fields="title"),
        entry_line(content={"title": 1}),
    ],
)
def test_the_entry_shape_is_strict(tmp_path: Path, line: str) -> None:
    write_tree(tmp_path)
    (tmp_path / "knowledge/.densho").mkdir()
    (tmp_path / HISTORY_FILE).write_text(line, encoding="utf-8")
    assert codes(history_drift(tmp_path).problems) == ["history"]


def test_the_problem_names_the_field(tmp_path: Path) -> None:
    write_tree(tmp_path)
    (tmp_path / "knowledge/.densho").mkdir()
    (tmp_path / HISTORY_FILE).write_text(entry_line(kind="other"), encoding="utf-8")
    assert history_drift(tmp_path).problems[0].message.startswith("kind: ")


@pytest.mark.parametrize(
    ("lines", "line"),
    [
        ([entry_line(change=2)], 1),
        ([entry_line(), entry_line(id="other", change=3)], 2),
        ([entry_line(), entry_line(change=2)], 2),
        ([entry_line(action="changed")], 1),
        ([entry_line(action="removed")], 1),
        ([entry_line(), entry_line(change=2, action="removed"), entry_line(action="removed")], 3),
    ],
)
def test_a_replay_that_does_not_fit_is_a_problem(
    tmp_path: Path, lines: list[str], line: int
) -> None:
    write_tree(tmp_path)
    (tmp_path / "knowledge/.densho").mkdir()
    (tmp_path / HISTORY_FILE).write_text("".join(lines), encoding="utf-8")
    report = history_drift(tmp_path)
    assert (report.problems[0].code, report.problems[0].line) == ("history", line)
    assert report.entries == ()


def test_a_lower_number_does_not_follow(tmp_path: Path) -> None:
    write_tree(tmp_path)
    (tmp_path / "knowledge/.densho").mkdir()
    lines = [entry_line(), entry_line(id="b", change=2), entry_line(id="c", change=1)]
    (tmp_path / HISTORY_FILE).write_text("".join(lines), encoding="utf-8")
    report = history_drift(tmp_path)
    assert [(problem.code, problem.line) for problem in report.problems] == [("history", 3)]
    assert "1 does not follow 2" in report.problems[0].message


def test_a_line_that_is_not_json_has_a_clean_message(tmp_path: Path) -> None:
    write_tree(tmp_path)
    (tmp_path / "knowledge/.densho").mkdir()
    (tmp_path / HISTORY_FILE).write_text("not json\n", encoding="utf-8")
    assert history_drift(tmp_path).problems[0].message.startswith("Invalid JSON")


def test_a_last_line_with_no_end_is_a_problem(tmp_path: Path) -> None:
    write_tree(tmp_path)
    (tmp_path / "knowledge/.densho").mkdir()
    text = entry_line() + entry_line(id="b").strip()
    (tmp_path / HISTORY_FILE).write_text(text, encoding="utf-8")
    report = record_history(tmp_path)
    assert [(problem.code, problem.line) for problem in report.problems] == [("history", 2)]


def test_a_file_at_the_folder_path_is_a_problem(tmp_path: Path) -> None:
    write_tree(tmp_path)
    (tmp_path / "knowledge/.densho").write_text("a file", encoding="utf-8")
    report = record_history(tmp_path)
    assert codes(report.problems) == ["history"]
    assert (tmp_path / "knowledge/.densho").read_text(encoding="utf-8") == "a file"


def test_a_read_only_folder_is_a_write_problem(tmp_path: Path) -> None:
    write_tree(tmp_path)
    (tmp_path / "knowledge/.densho").mkdir()
    (tmp_path / "knowledge/.densho").chmod(0o555)
    try:
        report = record_history(tmp_path)
    finally:
        (tmp_path / "knowledge/.densho").chmod(0o755)
    assert codes(report.problems) == ["write"]


def test_a_read_only_file_is_a_write_problem(tmp_path: Path) -> None:
    write_tree(tmp_path)
    record_history(tmp_path)
    replace(domain_file(tmp_path), "title: Domain", "title: Area")
    (tmp_path / HISTORY_FILE).chmod(0o444)
    try:
        report = record_history(tmp_path)
    finally:
        (tmp_path / HISTORY_FILE).chmod(0o644)
    assert codes(report.problems) == ["write"]
    assert report.problems[0].path == tmp_path / HISTORY_FILE


def test_the_command_prints_a_summary(tmp_path: Path) -> None:
    write_tree(tmp_path)
    result = RUNNER.invoke(app, ["history", str(tmp_path)])
    assert result.exit_code == 0
    assert "5 entities differ from the history, 0 problems" in result.output
    assert '"id"' not in result.output


def test_the_drift_command_writes_nothing_and_needs_no_template_file(tmp_path: Path) -> None:
    write_tree(tmp_path)
    record_history(tmp_path)
    before = (tmp_path / HISTORY_FILE).read_bytes()
    (tmp_path / "copier.yml").unlink()
    replace(domain_file(tmp_path), "title: Domain", "title: Area")
    result = RUNNER.invoke(app, ["history", str(tmp_path), "--drift"])
    assert result.exit_code == 0
    assert (tmp_path / HISTORY_FILE).read_bytes() == before


def test_the_command_prints_each_drift_line(tmp_path: Path) -> None:
    write_tree(tmp_path)
    record_history(tmp_path)
    replace(domain_file(tmp_path), "title: Domain", "title: Area")
    result = RUNNER.invoke(app, ["history", str(tmp_path), "--drift"])
    assert result.exit_code == 0
    first = result.output.splitlines()[0]
    assert Entry.model_validate_json(first).id == "domain"
    assert "1 entities differ from the history, 0 problems" in result.output


def test_the_command_fails_on_a_change_with_verify(tmp_path: Path) -> None:
    write_tree(tmp_path)
    result = RUNNER.invoke(app, ["history", str(tmp_path), "--verify"])
    assert result.exit_code == 1
    assert ": changed: " in result.output


def test_the_command_prints_a_note(tmp_path: Path) -> None:
    write_tree(tmp_path)
    record_history(tmp_path)
    result = RUNNER.invoke(app, ["history", str(tmp_path), "--verify"])
    assert result.exit_code == 0
    assert f"note: {history_module.NO_INDEX_NOTE}" in result.output


def test_the_command_rejects_two_modes(tmp_path: Path) -> None:
    write_tree(tmp_path)
    result = RUNNER.invoke(app, ["history", str(tmp_path), "--verify", "--drift"])
    assert result.exit_code == USAGE_ERROR
    assert not (tmp_path / HISTORY_FILE).exists()


def test_each_code_is_named() -> None:
    assert set(HISTORY_CODES) == {
        "history",
        "rewritten",
        "not-template",
        "changed",
        "not-staged",
        "write",
    }


def test_the_repo_history_matches_the_tree() -> None:
    report = history_drift(REPO)
    assert not report.problems
    assert report.entries == ()


def test_the_repo_history_names_each_directive_by_id() -> None:
    entries = lines_of(REPO)
    directives = {entry.id for entry in entries if entry.kind == "directive"}
    assert "limit-color-palette" in directives
    assert all(entry.id for entry in entries)


SKILL_NODE = """---
id: review
kind: densho:Skill
title: Review
status: proposed
origin: template
knowledge_type: domain
description: Review a sample. Use when a sample needs a review.
invocation: agent
uses:
  - domain
---
"""
SCRIPTS_DIGEST_LENGTH = 16


def write_skill(folder: Path, scripts: dict[str, bytes]) -> Path:
    skill = folder / "knowledge/skills/review"
    skill.mkdir(parents=True, exist_ok=True)
    (skill / "node.md").write_text(SKILL_NODE, encoding="utf-8")
    for name, data in scripts.items():
        path = skill / "scripts" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    return skill / "scripts"


def test_the_scripts_of_a_skill_are_one_field(tmp_path: Path) -> None:
    write_tree(tmp_path)
    scripts = write_skill(tmp_path, {"check.py": b"print(1)\n"})
    first = by_id(record_history(tmp_path).entries)["review"]
    assert "scripts" in first.content
    assert list(first.content) == sorted(first.content)
    assert re.fullmatch(f"[0-9a-f]{{{SCRIPTS_DIGEST_LENGTH}}}", str(first.content["scripts"]))
    (scripts / "check.py").write_bytes(b"print(2)\n")
    (changed,) = record_history(tmp_path).entries
    assert (changed.id, changed.fields) == ("review", ["scripts"])
    assert changed.content["scripts"] != first.content["scripts"]
    (scripts / "check.py").chmod(0o755)
    (mode,) = record_history(tmp_path).entries
    assert (mode.id, mode.fields) == ("review", ["scripts"])
    assert record_history(tmp_path).entries == ()
    (scripts / "check.py").unlink()
    (gone,) = record_history(tmp_path).entries
    assert (gone.id, gone.fields) == ("review", ["scripts"])
    assert "scripts" not in gone.content


def test_a_skill_with_no_scripts_has_no_scripts_field(tmp_path: Path) -> None:
    write_tree(tmp_path)
    write_skill(tmp_path, {})
    assert "scripts" not in by_id(record_history(tmp_path).entries)["review"].content
