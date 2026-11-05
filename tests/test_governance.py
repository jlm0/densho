import os
import shutil
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest
from typer.testing import CliRunner

from knowledge_architecture.cli import app
from knowledge_architecture.directives import check_directives
from knowledge_architecture.governance import (
    GOVERNANCE_CODES,
    check_governance,
    check_items,
    pending_entities,
)
from knowledge_architecture.governance import base as base_module
from knowledge_architecture.governance.base import (
    MERGE_NOTE,
    NO_COMMIT_NOTE,
    NO_GIT_NOTE,
    NO_REPOSITORY_NOTE,
    read_base,
)
from knowledge_architecture.governance.changes import check_changes
from knowledge_architecture.governance.entities import governed_entities
from knowledge_architecture.graph import check_tree
from knowledge_architecture.language import check_language
from knowledge_architecture.parser import ParsedNode, parse_source, parse_tree

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable

    from typer.testing import Result

type Spec = dict[str, Any]

REPO = Path(__file__).resolve().parents[1]
RUNNER = CliRunner()
GIT = shutil.which("git") or "git"
GIT_IDENTITY = (
    "-c",
    "user.name=ka-test",
    "-c",
    "user.email=ka-test@example.invalid",
    "-c",
    "commit.gpgsign=false",
    "-c",
    "core.hooksPath=/dev/null",
)
NODE_EDGES = (
    "broader",
    "related",
    "informs",
    "depends_on",
    "governs",
    "implements",
    "uses",
    "applies",
)


def rule(directive_id: str, status: str = "proposed", **fields: object) -> Spec:
    return {"id": directive_id, "status": status, "scope": "subtree", **fields}


def stop(directive_id: str, status: str = "proposed", **fields: object) -> Spec:
    return {"directive": directive_id, "status": status, "reason": "A prototype.", **fields}


def node(node_id: str, status: str = "proposed", **fields: object) -> Spec:
    return {"id": node_id, "status": status, "kind": "ka:Domain", **fields}


def concept(node_id: str, *broader: str, status: str = "proposed", **fields: object) -> Spec:
    return {
        "id": node_id,
        "status": status,
        "kind": "ka:Concept",
        "broader": list(broader),
        **fields,
    }


def directive_lines(entry: Spec) -> list[str]:
    text = entry.get("text", f"Do the {entry['id']} thing.")
    lines = [f"- {text} ^{entry['id']}", f"  - scope: {entry['scope']}"]
    lines += [f"  - status: {entry['status']}", f"  - origin: {entry.get('origin', 'template')}"]
    for key in ("also_attached_to", "refines", "conflicts_with", "sources"):
        lines += [f"  - {key}: {value}" for value in entry.get(key, [])]
    return lines


def pointer_lines(spec: Spec) -> list[str]:
    lines: list[str] = []
    for target in spec.get("pointers", []):
        lines += ["  - kind: ka:TextPointer", f"    target: {target}"]
        lines.append(f"    trigger: {spec.get('trigger', 'You need it.')}")
    return lines


def exception_lines(spec: Spec) -> list[str]:
    lines: list[str] = []
    for entry in spec.get("exceptions", []):
        lines += [f"  - directive: {entry['directive']}", f"    reason: {entry['reason']}"]
        lines.append(f"    status: {entry['status']}")
    return ["exceptions:", *lines] if lines else []


def front_matter(spec: Spec) -> list[str]:
    lines = ["---", f"id: {spec['id']}", f"kind: {spec['kind']}"]
    lines += [f"title: {spec.get('title', spec['id'])}", f"status: {spec['status']}"]
    lines.append(f"origin: {spec.get('origin', 'template')}")
    if spec["kind"] != "ka:Root":
        lines.append(f"knowledge_type: {spec.get('knowledge_type', 'domain')}")
    if spec["kind"] == "ka:Skill":
        lines.append("description: Review a change. Use when a change lands.")
    for key in (*NODE_EDGES, "sources"):
        if spec.get(key) == []:
            lines.append(f"{key}: []")
        elif key in spec:
            lines += [f"{key}:", *[f"  - {value}" for value in spec[key]]]
    pointers = pointer_lines(spec)
    return [*lines, *(["pointers:", *pointers] if pointers else []), *exception_lines(spec), "---"]


def render(spec: Spec) -> str:
    lines = [*front_matter(spec), ""]
    if spec["kind"] not in {"ka:Root", "ka:Skill"}:
        lines += ["## Definition", "", spec.get("definition", "A meaning."), ""]
    if "rules" in spec:
        lines += ["## Directives", ""]
        for entry in spec["rules"]:
            lines += directive_lines(entry)
        lines.append("")
    if "body" in spec:
        lines += ["## Notes", "", spec["body"], ""]
    return "\n".join(lines)


def relative_file(spec: Spec) -> str:
    if "file" in spec:
        return spec["file"]
    if spec["kind"] == "ka:Root":
        return "knowledge/node.md"
    folder = "skills" if spec["kind"] == "ka:Skill" else "knowledge"
    return f"{folder}/{spec['id']}/node.md"


def parsed(*specs: Spec) -> list[ParsedNode]:
    items: list[ParsedNode] = []
    for spec in specs:
        result = parse_source(render(spec), Path(relative_file(spec)))
        assert isinstance(result, ParsedNode), result
        items.append(result)
    return items


def compare(before: Iterable[Spec], after: Iterable[Spec]) -> list[str]:
    found = check_changes(governed_entities(parsed(*before)), governed_entities(parsed(*after)))
    return [str(problem) for problem in found]


def codes(before: Iterable[Spec], after: Iterable[Spec]) -> list[str]:
    return [problem.split(": ")[1] for problem in compare(before, after)]


def line_of(spec: Spec, text: str) -> str:
    numbers = [n for n, line in enumerate(render(spec).split("\n"), 1) if text in line]
    return f"{relative_file(spec)}:{numbers[0]}"


@pytest.mark.parametrize(
    ("spec", "text", "label"),
    [
        (node("a", "accepted"), "status: accepted", "node a"),
        (node("b", rules=[rule("a", "accepted")]), "  - status: accepted", "directive a"),
        (node("b", exceptions=[stop("a", "accepted")]), "    status: accepted", "exception b a"),
    ],
)
def test_a_new_entity_must_start_as_proposed(spec: Spec, text: str, label: str) -> None:
    bare: Spec = {key: value for key, value in spec.items() if key not in {"rules", "exceptions"}}
    before = [] if label == "node a" else [bare]
    assert compare(before, [spec]) == [
        (
            f"{line_of(spec, text)}: new-status: HEAD does not have {label}. "
            "Set its status to proposed."
        )
    ]


def test_a_new_second_directive_reports_its_own_line() -> None:
    bare = node("a")
    spec = {**bare, "rules": [rule("b"), rule("c", "accepted")]}
    assert compare([bare], [spec]) == [
        (
            f"{line_of(spec, '  - status: accepted')}: new-status: HEAD does not have "
            "directive c. Set its status to proposed."
        )
    ]


def test_a_new_second_exception_reports_its_own_line() -> None:
    bare = node("a")
    spec = {**bare, "exceptions": [stop("b"), stop("c", "accepted")]}
    assert compare([bare], [spec]) == [
        (
            f"{line_of(spec, '    status: accepted')}: new-status: HEAD does not have "
            "exception a c. Set its status to proposed."
        )
    ]


def test_a_new_deprecated_entity_fails() -> None:
    assert codes([], [node("a", "deprecated")]) == ["new-status"]


def test_a_new_proposed_entity_passes() -> None:
    spec = node("a", rules=[rule("b")], exceptions=[stop("c")])
    assert compare([], [spec]) == []


def test_an_unchanged_tree_passes() -> None:
    spec = node("a", "accepted", rules=[rule("b", "accepted")], exceptions=[stop("c", "accepted")])
    assert compare([spec], [spec]) == []


def test_a_promotion_with_no_change_passes() -> None:
    before = node("a", rules=[rule("b")], exceptions=[stop("c")])
    after = node("a", "accepted", rules=[rule("b", "accepted")], exceptions=[stop("c", "accepted")])
    assert compare([before], [after]) == []


def test_a_promotion_that_changes_a_definition_fails() -> None:
    before = node("a")
    after = node("a", "accepted", definition="Another meaning.")
    assert compare([before], [after]) == [
        (
            f"{line_of(after, 'status: accepted')}: promotion-change: "
            "This commit accepts node a and "
            "changes definition. Commit the change as proposed, and accept it in a later commit."
        )
    ]


def test_a_promotion_that_changes_a_directive_fails() -> None:
    before = node("a", rules=[rule("b")])
    after = node("a", rules=[rule("b", "accepted", text="Do another thing.")])
    assert codes([before], [after]) == ["promotion-change"]


def test_a_promotion_that_changes_an_exception_reason_fails() -> None:
    before = node("a", exceptions=[stop("b")])
    changed = stop("b", "accepted")
    changed["reason"] = "Another reason."
    assert codes([before], [node("a", exceptions=[changed])]) == ["promotion-change"]


def test_a_promotion_names_each_changed_field() -> None:
    before = node("a", rules=[rule("b")])
    after = node("a", rules=[rule("b", "accepted", text="Do another thing.", scope="node")])
    assert "changes scope, text." in compare([before], [after])[0]


def test_a_change_to_an_accepted_entity_fails() -> None:
    before = node("a", "accepted")
    after = node("a", "accepted", definition="Another meaning.")
    assert compare([before], [after]) == [
        (
            f"{line_of(after, 'status: accepted')}: accepted-change: "
            "This commit changes definition "
            "on node a. Set its status to proposed."
        )
    ]


def test_a_change_to_an_accepted_directive_fails() -> None:
    before = node("a", rules=[rule("b", "accepted")])
    after = node("a", rules=[rule("b", "accepted", text="Do another thing.")])
    assert compare([before], [after]) == [
        (
            f"{line_of(after, '  - status: accepted')}: accepted-change: This commit changes text "
            "on directive b. Set its status to proposed."
        )
    ]


def test_a_change_to_an_accepted_exception_fails() -> None:
    changed = stop("b", "accepted")
    changed["reason"] = "Another reason."
    before = node("a", exceptions=[stop("b", "accepted")])
    after = node("a", exceptions=[changed])
    assert compare([before], [after]) == [
        (
            f"{line_of(after, '    status: accepted')}: accepted-change: "
            "This commit changes reason "
            "on exception a b. Set its status to proposed."
        )
    ]


def test_reopening_an_entity_allows_each_change() -> None:
    before = node("a", "accepted", rules=[rule("b", "accepted")])
    after = node("a", definition="New.", rules=[rule("b", text="Do another thing.", scope="node")])
    assert compare([before], [after]) == []


def test_each_change_to_a_proposal_passes() -> None:
    before = node("a", rules=[rule("b")])
    after = node("a", definition="New.", rules=[rule("b", text="Do another thing.")])
    assert compare([before], [after]) == []


@pytest.mark.parametrize(
    "field_change",
    [
        {"broader": ["c"]},
        {"related": ["c"]},
        {"informs": ["c"]},
        {"depends_on": ["c"]},
        {"governs": ["c"]},
        {"implements": ["c"]},
        {"definition": "New."},
        {"knowledge_type": "workspace"},
        {"kind": "ka:Discipline"},
    ],
    ids=lambda change: next(iter(change)),
)
def test_each_reviewed_node_field_reopens_the_review(field_change: Spec) -> None:
    before = concept("a", "b", status="accepted")
    assert codes([before], [{**before, **field_change}]) == ["accepted-change"]


@pytest.mark.parametrize("field_change", [{"uses": ["c"]}, {"applies": ["c"]}], ids=str)
def test_each_reviewed_skill_field_reopens_the_review(field_change: Spec) -> None:
    before: Spec = {"id": "a", "status": "accepted", "kind": "ka:Skill", "uses": ["b"]}
    assert codes([before], [{**before, **field_change}]) == ["accepted-change"]


def test_a_skill_description_reopens_the_review() -> None:
    before: Spec = {"id": "a", "status": "accepted", "kind": "ka:Skill", "uses": ["b"]}
    entities = governed_entities(parsed(before))
    assert "description" in entities["node", "a"].reviewed


@pytest.mark.parametrize(
    "field_change",
    [
        {"also_attached_to": ["c"]},
        {"refines": ["c"]},
        {"conflicts_with": ["c"]},
        {"scope": "node"},
        {"text": "Do another thing."},
    ],
    ids=lambda change: next(iter(change)),
)
def test_each_reviewed_directive_field_reopens_the_review(field_change: Spec) -> None:
    before = node("a", rules=[rule("b", "accepted")])
    after = node("a", rules=[rule("b", "accepted", **field_change)])
    assert codes([before], [after]) == ["accepted-change"]


def test_moving_a_directive_to_another_node_reopens_the_review() -> None:
    before = [node("a", rules=[rule("c", "accepted")]), node("b")]
    after = [node("a"), node("b", rules=[rule("c", "accepted")])]
    assert codes(before, after) == ["accepted-change"]


@pytest.mark.parametrize(
    "field_change",
    [
        {"title": "New"},
        {"body": "New text."},
        {"pointers": ["c"]},
        {"sources": ["docs/new.md"]},
    ],
    ids=lambda change: next(iter(change)),
)
def test_a_routine_node_field_needs_no_review(field_change: Spec) -> None:
    before = node("a", "accepted")
    assert compare([before], [{**before, **field_change}]) == []


def test_a_directive_source_needs_no_review() -> None:
    before = node("a", rules=[rule("b", "accepted")])
    after = node("a", rules=[rule("b", "accepted", sources=["docs/new.md"])])
    assert compare([before], [after]) == []


def test_a_new_exception_on_an_accepted_node_does_not_reopen_the_node() -> None:
    before = node("a", "accepted")
    after = node("a", "accepted", exceptions=[stop("b")])
    assert compare([before], [after]) == []


def test_a_new_proposed_directive_on_an_accepted_node_passes() -> None:
    before = node("a", "accepted")
    after = node("a", "accepted", rules=[rule("b")])
    assert compare([before], [after]) == []


def test_a_new_pointer_on_an_accepted_root_passes() -> None:
    root: Spec = {"id": "root", "status": "accepted", "kind": "ka:Root", "pointers": ["a"]}
    assert compare([root], [{**root, "pointers": ["a", "b"]}]) == []


def test_removing_a_reviewed_field_reopens_the_review() -> None:
    before = node("a", "accepted", related=["b"])
    assert codes([before], [node("a", "accepted")]) == ["accepted-change"]


def test_an_empty_list_is_the_same_as_no_list() -> None:
    before = node("a", "accepted")
    assert compare([before], [{**before, "related": []}]) == []


def test_list_order_needs_no_review() -> None:
    before = concept("a", "b", "c", status="accepted")
    after = concept("a", "c", "b", status="accepted")
    assert compare([before], [after]) == []


def test_a_markdown_source_form_needs_no_review() -> None:
    before = node("a", "accepted", definition="A *real*  meaning.")
    after = node("a", "accepted", definition="A _real_ meaning.")
    assert compare([before], [after]) == []


def test_a_directive_markdown_source_form_needs_no_review() -> None:
    before = node("a", rules=[rule("b", "accepted", text="Do the *real* thing.")])
    after = node("a", rules=[rule("b", "accepted", text="Do the _real_ thing.")])
    assert compare([before], [after]) == []


def test_a_change_inside_a_code_span_reopens_the_review() -> None:
    before = node("a", rules=[rule("b", "accepted", text="Run `a  b`.")])
    after = node("a", rules=[rule("b", "accepted", text="Run `a  c`.")])
    assert codes([before], [after]) == ["accepted-change"]


def test_a_moved_file_is_not_a_new_entity() -> None:
    before = node("a", "accepted", rules=[rule("b", "accepted")])
    after = {**before, "file": "knowledge/moved/deep/node.md"}
    assert compare([before], [after]) == []


def test_a_deprecated_entity_cannot_jump_to_accepted() -> None:
    before = node("a", "deprecated")
    after = node("a", "accepted")
    assert compare([before], [after]) == [
        (
            f"{line_of(after, 'status: accepted')}: status-jump: Set node a to proposed first. "
            "HEAD has it as deprecated."
        )
    ]


def test_a_status_jump_with_a_change_gives_one_problem() -> None:
    before = node("a", "deprecated")
    after = node("a", "accepted", definition="New.")
    assert codes([before], [after]) == ["status-jump"]


@pytest.mark.parametrize(
    ("before", "after"),
    [
        ("deprecated", "proposed"),
        ("deprecated", "deprecated"),
        ("accepted", "deprecated"),
        ("accepted", "proposed"),
        ("proposed", "deprecated"),
        ("proposed", "proposed"),
    ],
)
def test_each_other_transition_passes_with_a_change(before: str, after: str) -> None:
    assert compare([node("a", before)], [node("a", after, definition="New.")]) == []


def test_a_change_to_the_origin_of_a_node_fails() -> None:
    before = node("a", "accepted")
    after = {**before, "origin": "project"}
    assert compare([before], [after]) == [
        (
            f"{line_of(after, 'status: accepted')}: origin-change: Keep the origin of node a. "
            "HEAD has template."
        )
    ]


def test_a_change_to_the_origin_of_a_directive_fails() -> None:
    before = node("a", rules=[rule("b")])
    after = node("a", rules=[rule("b", origin="project")])
    assert codes([before], [after]) == ["origin-change"]


def test_an_origin_change_on_an_accepted_directive_gives_one_problem() -> None:
    before = node("a", rules=[rule("b", "accepted")])
    after = node("a", rules=[rule("b", "accepted", origin="project")])
    assert codes([before], [after]) == ["origin-change"]


def test_an_origin_change_and_an_accepted_change_both_report() -> None:
    before = node("a", "accepted")
    after = {**before, "origin": "project", "definition": "New."}
    assert codes([before], [after]) == ["origin-change", "accepted-change"]


def test_removing_an_accepted_node_fails() -> None:
    before = node("a", "accepted")
    assert compare([before], []) == [
        (
            f"{line_of(before, 'status: accepted')}: removed-accepted: "
            "HEAD has node a as accepted. "
            "Set its status to deprecated in one commit, and remove it in a later commit."
        )
    ]


def test_removing_an_accepted_directive_fails() -> None:
    before = node("a", rules=[rule("b", "accepted")])
    assert codes([before], [node("a")]) == ["removed-accepted"]


def test_renaming_an_accepted_id_fails() -> None:
    assert codes([node("a", "accepted")], [node("b")]) == ["removed-accepted"]


def test_renaming_an_accepted_id_to_an_accepted_id_gives_both_problems() -> None:
    found = codes([node("a", "accepted")], [node("b", "accepted")])
    assert sorted(found) == ["new-status", "removed-accepted"]


@pytest.mark.parametrize("status", ["proposed", "deprecated"])
def test_removing_a_live_proposal_or_a_deprecated_entity_passes(status: str) -> None:
    assert compare([node("a", status, rules=[rule("b", status)])], []) == []


def test_removing_an_accepted_exception_passes() -> None:
    assert compare([node("a", exceptions=[stop("b", "accepted")])], [node("a")]) == []


def test_an_unreadable_base_file_skips_the_new_status_rule() -> None:
    spec = node("a", "accepted")
    current = governed_entities(parsed(spec))
    assert check_changes({}, current, {Path(relative_file(spec))}) == []
    assert check_changes({}, current, {Path("other.md")}) != []


def test_an_entity_label_names_each_part() -> None:
    entity = governed_entities(parsed(node("a", exceptions=[stop("b")])))["exception", "a", "b"]
    assert (entity.kind, entity.name, entity.label) == ("exception", "a b", "exception a b")


def test_an_exception_has_no_origin() -> None:
    entity = governed_entities(parsed(node("a", exceptions=[stop("b")])))["exception", "a", "b"]
    assert entity.origin is None


def statics(*specs: Spec, repository: Path | None = None) -> list[str]:
    return [str(problem) for problem in check_items(parsed(*specs), repository or Path())]


def static_codes(*specs: Spec) -> list[str]:
    return [problem.split(": ")[1] for problem in statics(*specs)]


WORKSPACE: Spec = {"knowledge_type": "workspace"}
PROJECT: Spec = {"origin": "project"}


def test_the_template_ships_no_workspace_node() -> None:
    spec = node("a", **WORKSPACE)
    assert statics(spec) == [
        (
            f"{line_of(spec, 'origin: template')}: template-workspace: The template ships no "
            "workspace knowledge. Set origin to project."
        )
    ]


def test_the_template_ships_no_directive_in_a_workspace_node() -> None:
    spec = node("a", **WORKSPACE, **PROJECT, rules=[rule("b")])
    assert statics(spec) == [
        (
            f"{line_of(spec, '  - origin: template')}: template-workspace: The template ships no "
            "workspace knowledge. Set origin to project."
        )
    ]


def test_each_template_directive_in_a_workspace_node_reports() -> None:
    spec = node("a", **WORKSPACE, rules=[rule("b"), rule("c", origin="project"), rule("d")])
    assert static_codes(spec) == ["template-workspace"] * 3


def test_a_second_template_directive_reports_its_own_line() -> None:
    spec = node("a", **WORKSPACE, **PROJECT, rules=[rule("b", origin="project"), rule("c")])
    assert [problem.rsplit(": ", 2)[0] for problem in statics(spec)] == [
        line_of(spec, "  - origin: template")
    ]


def test_project_workspace_knowledge_passes() -> None:
    assert statics(node("a", **WORKSPACE, **PROJECT, rules=[rule("b", origin="project")])) == []


def test_project_domain_knowledge_passes() -> None:
    assert statics(node("a", **PROJECT, rules=[rule("b", origin="project")])) == []


def test_a_project_directive_on_a_template_domain_node_passes() -> None:
    assert statics(node("a", rules=[rule("b", origin="project")])) == []


def test_a_template_root_has_no_knowledge_type_and_passes() -> None:
    root: Spec = {"id": "root", "status": "proposed", "kind": "ka:Root", "pointers": ["a"]}
    assert statics(root) == []


@pytest.mark.parametrize("status", ["proposed", "accepted"])
def test_a_deprecated_node_cannot_hold_a_live_directive(status: str) -> None:
    spec = node("a", "deprecated", rules=[rule("b", status)])
    assert statics(spec) == [
        (
            f"{line_of(spec, f'  - status: {status}')}: deprecated-holder: "
            "This node is deprecated, "
            f"but b is {status}. Deprecate the directive, or move it to a live node."
        )
    ]


def test_a_second_live_directive_reports_its_own_line() -> None:
    spec = node("a", "deprecated", rules=[rule("b", "deprecated"), rule("c")])
    assert [problem.split(": ")[0] for problem in statics(spec)] == [
        line_of(spec, "  - status: proposed")
    ]


def test_a_deprecated_node_can_hold_a_deprecated_directive() -> None:
    assert statics(node("a", "deprecated", rules=[rule("b", "deprecated")])) == []


@pytest.mark.parametrize("status", ["proposed", "accepted"])
def test_a_live_node_can_hold_a_deprecated_directive(status: str) -> None:
    assert statics(node("a", status, rules=[rule("b", "deprecated")])) == []


@pytest.mark.parametrize("field", ["broader", "depends_on", "implements"])
def test_a_live_node_cannot_rest_on_a_deprecated_node(field: str) -> None:
    target = node("old", "deprecated")
    edge: Spec = {} if field == "broader" else {field: ["other", "old"]}
    source = concept("new", "other", *(["old"] if field == "broader" else []), **edge)
    assert statics(target, source) == [
        (
            f"{line_of(source, '  - old')}: deprecated-reference: {field} names old, "
            "which is deprecated. Remove it."
        )
    ]


def test_a_skill_cannot_use_a_deprecated_node() -> None:
    target = node("old", "deprecated")
    source: Spec = {"id": "a", "status": "proposed", "kind": "ka:Skill", "uses": ["old"]}
    assert static_codes(target, source) == ["deprecated-reference"]


@pytest.mark.parametrize("field", ["also_attached_to", "refines"])
def test_a_live_directive_cannot_rest_on_a_deprecated_entity(field: str) -> None:
    target = node("old", "deprecated", rules=[rule("old-rule", "deprecated")])
    name = "old" if field == "also_attached_to" else "old-rule"
    attachment: Spec = {field: [name]}
    source = node("new", "accepted", rules=[rule("b", **attachment)])
    assert statics(target, source) == [
        (
            f"{line_of(source, f'  - {field}: {name}')}: deprecated-reference: "
            f"{field} names {name}, "
            "which is deprecated. Remove it."
        )
    ]


def test_the_second_directive_reports_its_own_status() -> None:
    target = node("old", "deprecated", rules=[rule("old-rule", "deprecated")])
    source = node(
        "new",
        rules=[rule("a", "deprecated", refines=["old-rule"]), rule("b", refines=["old-rule"])],
    )
    lines = render(source).split("\n")
    line = len(lines) - lines[::-1].index("  - refines: old-rule")
    assert statics(target, source) == [
        (
            f"{relative_file(source)}:{line}: deprecated-reference: refines names old-rule, "
            "which is deprecated. Remove it."
        )
    ]


def test_a_deprecated_node_can_rest_on_a_deprecated_node() -> None:
    assert statics(node("old", "deprecated"), concept("a", "old", status="deprecated")) == []


def test_a_deprecated_directive_can_rest_on_a_deprecated_directive() -> None:
    target = node("old", "deprecated", rules=[rule("old-rule", "deprecated")])
    source = node("new", rules=[rule("b", "deprecated", refines=["old-rule"])])
    assert statics(target, source) == []


@pytest.mark.parametrize("field", ["related", "informs", "governs"])
def test_a_relationship_edge_can_name_a_deprecated_node(field: str) -> None:
    edge: Spec = {field: ["old"]}
    assert statics(node("old", "deprecated"), concept("a", "b", **edge)) == []


def test_a_pointer_can_name_a_deprecated_node() -> None:
    assert statics(node("old", "deprecated"), node("a", pointers=["old"])) == []


def test_a_conflict_can_name_a_deprecated_directive() -> None:
    target = node("old", "deprecated", rules=[rule("old-rule", "deprecated")])
    assert statics(target, node("a", rules=[rule("b", conflicts_with=["old-rule"])])) == []


def test_a_live_entity_can_name_a_live_entity() -> None:
    assert (
        statics(node("a", "accepted"), concept("b", "a"), concept("c", "a", status="accepted"))
        == []
    )


def test_an_exception_does_not_make_a_directive_deprecated() -> None:
    target = node("a", rules=[rule("b")])
    other = node("c", exceptions=[stop("b", "deprecated")], rules=[rule("d", refines=["b"])])
    assert statics(target, other) == []


def test_an_unknown_reference_is_not_a_governance_problem() -> None:
    assert statics(concept("a", "missing")) == []


POLICY = "governance/policies"


def test_a_policy_must_name_what_it_governs() -> None:
    spec = node("a", file=f"{POLICY}/a/node.md")
    other = node("b", file=f"{POLICY}/b/node.md", governs=["a", "b"])
    assert statics(spec, other) == [
        (
            f"{POLICY}/a/node.md:{line_of(spec, 'id: a').split(':')[1]}: policy-governs: "
            "A policy names what it sets rules for. Add governs."
        )
    ]


def test_a_policy_must_have_a_governing_policy() -> None:
    spec = node("a", file=f"{POLICY}/a/node.md", governs=["root"])
    other = node("b", file=f"{POLICY}/b/node.md", governs=["b"])
    assert statics(spec, other) == [
        (
            f"{POLICY}/a/node.md:{line_of(spec, 'id: a').split(':')[1]}: policy-governs: "
            "No policy governs this policy. Add it to governs on a policy."
        )
    ]


def test_a_policy_that_governs_itself_passes() -> None:
    assert statics(node("a", file=f"{POLICY}/a/node.md", governs=["a"])) == []


def test_a_node_outside_the_policy_folder_does_not_count_as_a_governor() -> None:
    policy = node("a", file=f"{POLICY}/a/node.md", governs=["root"])
    outside = node("b", governs=["a"])
    assert static_codes(policy, outside) == ["policy-governs"]


def test_a_node_outside_the_policy_folder_needs_no_governs() -> None:
    assert statics(node("a")) == []


def test_the_policy_rule_reads_the_repository_path(tmp_path: Path) -> None:
    spec = node("a", file=str(tmp_path / POLICY / "a/node.md"))
    assert [line.split(": ")[1] for line in statics(spec, repository=tmp_path)] == [
        "policy-governs",
        "policy-governs",
    ]
    assert statics(spec, repository=Path("elsewhere")) == []


@pytest.fixture(autouse=True)
def clean_git_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    for key in list(os.environ):
        if key.startswith("GIT_"):
            monkeypatch.delenv(key)


def git(repository: Path, *arguments: str) -> None:
    subprocess.run(  # noqa: S603
        [GIT, *GIT_IDENTITY, "-C", str(repository), *arguments],
        check=True,
        capture_output=True,
    )


def write(repository: Path, *specs: Spec) -> None:
    for folder in ("knowledge", "skills"):
        (repository / folder).mkdir(exist_ok=True)
    for spec in specs:
        path = repository / relative_file(spec)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render(spec), encoding="utf-8")


def commit_all(repository: Path, message: str = "x") -> None:
    git(repository, "add", "-A")
    git(repository, "commit", "--allow-empty", "-q", "-m", message)


@pytest.fixture
def repository(tmp_path: Path) -> Path:
    git(tmp_path, "init", "-q", "--template=", "--initial-branch=main")
    (tmp_path / "knowledge").mkdir()
    (tmp_path / "skills").mkdir()
    return tmp_path


def base_ids(repository: Path) -> set[str]:
    return {item.node.id for item in read_base(repository).items}


def test_a_folder_with_no_repository_gives_a_note(tmp_path: Path) -> None:
    base = read_base(tmp_path)
    assert base.notes == [NO_REPOSITORY_NOTE]
    assert (base.items, base.problems) == ([], [])


def test_a_repository_with_no_commit_gives_a_note(repository: Path) -> None:
    assert read_base(repository).notes == [NO_COMMIT_NOTE]


def test_no_git_program_gives_a_note(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(shutil, "which", lambda _name: None)  # pyright: ignore[reportUnknownArgumentType, reportUnknownLambdaType]
    assert read_base(tmp_path).notes == [NO_GIT_NOTE]


def test_the_base_reads_each_node_at_head(repository: Path) -> None:
    write(repository, node("a"), concept("b", "a"))
    commit_all(repository)
    base = read_base(repository)
    assert {item.node.id for item in base.items} == {"a", "b"}
    assert base.items[0].path.is_relative_to(repository)
    assert (base.notes, base.problems, base.unreadable) == ([], [], frozenset())


def test_the_base_reads_head_and_not_the_working_tree(repository: Path) -> None:
    write(repository, node("a"))
    commit_all(repository)
    write(repository, node("a", title="Changed"), node("new"))
    base = read_base(repository)
    assert [item.node.title for item in base.items] == ["a"]


def test_the_base_reads_a_staged_deletion_as_still_at_head(repository: Path) -> None:
    write(repository, node("a"))
    commit_all(repository)
    git(repository, "rm", "-q", "knowledge/a/node.md")
    assert base_ids(repository) == {"a"}


def test_the_base_reads_each_tree_folder(repository: Path) -> None:
    write(
        repository,
        node("a"),
        {"id": "b", "status": "proposed", "kind": "ka:Skill", "uses": ["a"]},
        node("c", file="governance/policies/c/node.md"),
        node("d", file="elsewhere/d/node.md"),
    )
    commit_all(repository)
    assert base_ids(repository) == {"a", "b", "c"}


def test_the_base_skips_other_files(repository: Path) -> None:
    write(repository, node("a"))
    (repository / "knowledge/a/other.yaml").write_text("a: 1\n", encoding="utf-8")
    (repository / "knowledge/a/nodes.md").write_text("# Not a node\n", encoding="utf-8")
    commit_all(repository)
    base = read_base(repository)
    assert [item.node.id for item in base.items] == ["a"]
    assert base.notes == []


def test_the_base_skips_a_symbolic_link(repository: Path) -> None:
    write(repository, node("a"))
    link = repository / "knowledge/link/node.md"
    link.parent.mkdir()
    link.symlink_to("../a/node.md")
    commit_all(repository)
    base = read_base(repository)
    assert [item.node.id for item in base.items] == ["a"]
    assert base.notes == []


def test_the_base_reads_an_executable_file(repository: Path) -> None:
    write(repository, node("a"))
    (repository / "knowledge/a/node.md").chmod(0o755)
    commit_all(repository)
    assert base_ids(repository) == {"a"}


def test_the_base_skips_a_submodule_entry(repository: Path) -> None:
    write(repository, node("a"))
    commit_all(repository)
    object_id = subprocess.run(  # noqa: S603
        [GIT, "-C", str(repository), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    entry = f"160000,{object_id},knowledge/sub/node.md"
    git(repository, "update-index", "--add", "--cacheinfo", entry)
    git(repository, "commit", "-q", "-m", "x")
    base = read_base(repository)
    assert [item.node.id for item in base.items] == ["a"]
    assert base.notes == []


def test_the_base_reads_a_hostile_folder_name(repository: Path) -> None:
    write(repository, node("a", file="knowledge/a b\tc\ndé/node.md"))
    commit_all(repository)
    base = read_base(repository)
    assert [item.path for item in base.items] == [repository / "knowledge/a b\tc\ndé/node.md"]


def test_the_base_reads_a_subfolder_of_a_repository(repository: Path) -> None:
    project = repository / "projects/one"
    write(repository, node("outside"))
    project.mkdir(parents=True)
    write(project, node("inside"))
    commit_all(repository)
    base = read_base(project)
    assert {item.node.id for item in base.items} == {"inside"}
    assert base.items[0].path == project / "knowledge/inside/node.md"


def test_the_base_ignores_the_git_environment(
    repository: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    write(repository, node("a"))
    commit_all(repository)
    monkeypatch.setenv("GIT_DIR", str(repository / "missing"))
    monkeypatch.setenv("GIT_INDEX_FILE", str(repository / "missing-index"))
    monkeypatch.setenv("GIT_WORK_TREE", str(repository / "missing"))
    assert base_ids(repository) == {"a"}


def test_a_head_file_that_does_not_parse_gives_a_note(repository: Path) -> None:
    write(repository, node("a"))
    path = repository / "knowledge/bad/node.md"
    path.parent.mkdir()
    path.write_text("no front matter\n", encoding="utf-8")
    commit_all(repository)
    base = read_base(repository)
    assert base.unreadable == {path}
    assert base.notes == [
        f"The change rules skipped {path}, because the file at HEAD does not parse."
    ]
    assert [item.node.id for item in base.items] == ["a"]


def test_a_head_file_that_is_not_utf8_gives_a_note(repository: Path) -> None:
    path = repository / "knowledge/bad/node.md"
    path.parent.mkdir()
    path.write_bytes(b"\xff\xfe\x00binary")
    commit_all(repository)
    assert read_base(repository).unreadable == {path}


def test_each_unreadable_file_gets_a_note_in_order(repository: Path) -> None:
    for name in ("b", "a"):
        path = repository / f"knowledge/{name}/node.md"
        path.parent.mkdir()
        path.write_text("no front matter\n", encoding="utf-8")
    commit_all(repository)
    notes = read_base(repository).notes
    assert [note.split("/knowledge/")[1].split("/")[0] for note in notes] == ["a", "b"]


def test_an_empty_blob_is_a_note_and_not_a_crash(repository: Path) -> None:
    path = repository / "knowledge/empty/node.md"
    path.parent.mkdir()
    path.write_bytes(b"")
    write(repository, node("a"))
    commit_all(repository)
    assert read_base(repository).unreadable == {path}
    assert base_ids(repository) == {"a"}


def test_a_file_with_no_newline_at_the_end_keeps_its_last_character(repository: Path) -> None:
    write(repository, node("a"))
    path = repository / "knowledge/a/node.md"
    path.write_text(path.read_text(encoding="utf-8").rstrip("\n"), encoding="utf-8")
    commit_all(repository)
    assert read_base(repository).items[0].node.model_dump()["definition"] == "A meaning."


def test_git_messages_stay_in_english(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    program = tmp_path / "git"
    program.write_text(
        '#!/bin/sh\nif [ "$LC_ALL" = C ]; then echo "fatal: not a git repository" >&2\n'
        'else echo "fatal: kein Git-Repository" >&2; fi\nexit 128\n',
        encoding="utf-8",
    )
    program.chmod(0o755)
    monkeypatch.setenv("LC_ALL", "de_DE.UTF-8")

    def fake_which(_name: str) -> str:
        return str(program)

    monkeypatch.setattr(shutil, "which", fake_which)
    assert read_base(tmp_path).notes == [NO_REPOSITORY_NOTE]


def test_a_blob_with_a_newline_at_the_end_keeps_its_neighbours(repository: Path) -> None:
    write(repository, node("a"), node("b"), node("c"))
    commit_all(repository)
    assert base_ids(repository) == {"a", "b", "c"}


@pytest.mark.parametrize("status", ["accepted", "deprecated"])
def test_a_note_means_that_the_change_rules_did_not_run(repository: Path, status: str) -> None:
    write(repository, node("a", status))
    assert run_check(repository) == []


def test_a_folder_with_no_repository_skips_the_change_rules(tmp_path: Path) -> None:
    write(tmp_path, node("a", "accepted"))
    report = check_governance(tmp_path)
    assert (report.notes, report.problems) == ([NO_REPOSITORY_NOTE], [])


def test_a_merge_in_progress_skips_the_change_rules(repository: Path) -> None:
    write(repository, node("a"))
    commit_all(repository)
    git(repository, "checkout", "-q", "-b", "side")
    write(repository, node("a", definition="New."))
    commit_all(repository)
    write(repository, node("a", "accepted", definition="New."))
    commit_all(repository)
    git(repository, "checkout", "-q", "main")
    write(repository, node("c"))
    commit_all(repository)
    git(repository, "merge", "-q", "--no-commit", "--no-ff", "side")
    report = check_governance(repository)
    assert (report.notes, report.problems) == ([MERGE_NOTE], [])


def test_a_merge_in_progress_gives_a_note(repository: Path) -> None:
    write(repository, node("a"))
    commit_all(repository)
    git(repository, "checkout", "-q", "-b", "side")
    write(repository, node("b"))
    commit_all(repository)
    git(repository, "checkout", "-q", "main")
    write(repository, node("c"))
    commit_all(repository)
    git(repository, "merge", "-q", "--no-commit", "--no-ff", "side")
    base = read_base(repository)
    assert base.notes == [MERGE_NOTE]
    assert base.items == []


def test_a_missing_object_is_a_base_problem(repository: Path) -> None:
    write(repository, node("a"))
    commit_all(repository)
    object_id = subprocess.run(  # noqa: S603
        [GIT, "-C", str(repository), "rev-parse", "HEAD:knowledge/a/node.md"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    (repository / ".git/objects" / object_id[:2] / object_id[2:]).unlink()
    problems = read_base(repository).problems
    assert [str(problem) for problem in problems] == [
        f"{repository}:1: base: git cannot read HEAD: 'An object is missing.'"
    ]


def failing_git(failing_argument: str) -> Callable[..., subprocess.CompletedProcess[bytes]]:
    real = base_module._git  # noqa: SLF001  # pyright: ignore[reportPrivateUsage]

    def run(
        program: str, repository: Path, *arguments: str, stdin: bytes | None = None
    ) -> subprocess.CompletedProcess[bytes]:
        if failing_argument in arguments:
            return subprocess.CompletedProcess([], 128, b"", b"fatal:  a\n  \xffreason\n")
        return real(program, repository, *arguments, stdin=stdin)

    return run


@pytest.mark.parametrize("argument", ["--is-inside-work-tree", "ls-tree", "cat-file"])
def test_a_git_failure_is_a_base_problem(
    repository: Path, monkeypatch: pytest.MonkeyPatch, argument: str
) -> None:
    write(repository, node("a"))
    commit_all(repository)
    monkeypatch.setattr(base_module, "_git", failing_git(argument))
    problems = read_base(repository).problems
    assert [str(problem) for problem in problems] == [
        f"{repository}:1: base: git cannot read HEAD: 'fatal: a \\ufffdreason'"
    ]


def test_a_problem_at_the_base_fails_the_whole_check(
    repository: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    write(repository, node("a"))
    commit_all(repository)
    monkeypatch.setattr(base_module, "_git", failing_git("ls-tree"))
    assert [problem.code for problem in check_governance(repository).problems] == ["base"]


def run_check(repository: Path) -> list[str]:
    return [problem.code for problem in check_governance(repository).problems]


MUST_FAIL: dict[str, tuple[tuple[Spec, ...], tuple[Spec, ...]]] = {
    "new-status": ((), (node("a", "accepted"),)),
    "promotion-change": ((node("a"),), (node("a", "accepted", definition="New."),)),
    "accepted-change": ((node("a", "accepted"),), (node("a", "accepted", definition="New."),)),
    "status-jump": ((node("a", "deprecated"),), (node("a", "accepted"),)),
    "origin-change": ((node("a"),), (node("a", origin="project"),)),
    "removed-accepted": ((node("a", "accepted"), node("b")), (node("b"),)),
    "template-workspace": ((), (node("a", knowledge_type="workspace"),)),
    "deprecated-holder": (
        (node("a", rules=[rule("b")]),),
        (node("a", "deprecated", rules=[rule("b")]),),
    ),
    "deprecated-reference": (
        (node("a"), concept("b", "a")),
        (node("a", "deprecated"), concept("b", "a")),
    ),
    "policy-governs": (
        (),
        (
            node("a", file=f"{POLICY}/a/node.md", governs=["a", "root"]),
            node("b", file=f"{POLICY}/b/node.md"),
        ),
    ),
}


def clear_tree(repository: Path) -> None:
    for folder in ("knowledge", "skills", "governance"):
        shutil.rmtree(repository / folder, ignore_errors=True)


@pytest.mark.parametrize("code", MUST_FAIL)
def test_each_must_fail_input_gives_its_code_through_the_whole_check(
    repository: Path, code: str
) -> None:
    before, after = MUST_FAIL[code]
    write(repository, *before)
    commit_all(repository)
    clear_tree(repository)
    write(repository, *after)
    assert code in run_check(repository)


def test_each_code_has_a_must_fail_input() -> None:
    assert set(GOVERNANCE_CODES) == {*MUST_FAIL, "base"}


def test_a_tree_passes_the_whole_check_after_a_commit(repository: Path) -> None:
    write(repository, node("a", rules=[rule("b")]))
    commit_all(repository)
    report = check_governance(repository)
    assert (report.count, report.notes, report.problems) == (2, [], [])


def test_a_promotion_in_a_later_commit_passes_the_whole_check(repository: Path) -> None:
    write(repository, node("a", rules=[rule("b")]))
    commit_all(repository)
    write(repository, node("a", "accepted", rules=[rule("b", "accepted")]))
    assert run_check(repository) == []
    commit_all(repository)
    assert run_check(repository) == []


def test_a_first_commit_can_hold_accepted_entities(repository: Path) -> None:
    write(repository, node("a", "accepted", rules=[rule("b", "accepted")]))
    report = check_governance(repository)
    assert report.notes == [NO_COMMIT_NOTE]
    assert report.problems == []


def test_a_copy_into_a_repository_with_history_starts_as_proposed(repository: Path) -> None:
    commit_all(repository, "first")
    write(repository, node("a", "accepted", origin="template"))
    assert run_check(repository) == ["new-status"]


def test_a_template_entity_can_change_when_it_reopens(repository: Path) -> None:
    write(repository, node("a", "accepted", rules=[rule("b", "accepted")]))
    commit_all(repository)
    write(repository, node("a", definition="Our own.", rules=[rule("b", text="Do our thing.")]))
    assert run_check(repository) == []


def test_a_template_entity_can_leave_in_two_commits(repository: Path) -> None:
    write(repository, node("a", "accepted", rules=[rule("b", "accepted")]), node("c"))
    commit_all(repository)
    write(repository, node("a", "deprecated", rules=[rule("b", "deprecated")]))
    assert run_check(repository) == []
    commit_all(repository)
    shutil.rmtree(repository / "knowledge/a")
    assert run_check(repository) == []


def test_a_move_of_a_file_passes_the_whole_check(repository: Path) -> None:
    write(repository, node("a", "accepted"))
    commit_all(repository)
    shutil.rmtree(repository / "knowledge/a")
    write(repository, node("a", "accepted", file="knowledge/deep/er/node.md"))
    assert run_check(repository) == []


def test_a_head_file_that_no_longer_parses_does_not_block_a_change(repository: Path) -> None:
    path = repository / "knowledge/a/node.md"
    path.parent.mkdir()
    path.write_text("no front matter\n", encoding="utf-8")
    commit_all(repository)
    write(repository, node("a", "accepted"))
    report = check_governance(repository)
    assert report.problems == []
    assert report.notes == [
        f"The change rules skipped {path}, because the file at HEAD does not parse."
    ]


def test_a_parse_problem_stops_the_whole_check(repository: Path) -> None:
    path = repository / "knowledge/a/node.md"
    path.parent.mkdir()
    path.write_text("no front matter\n", encoding="utf-8")
    report = check_governance(repository)
    assert report.count == 0
    assert report.notes == []
    assert [problem.code for problem in report.problems] == ["front-matter"]


def test_the_report_counts_each_entity(repository: Path) -> None:
    write(repository, node("a", rules=[rule("b"), rule("c")], exceptions=[stop("d")]))
    assert check_governance(repository).count == len(["a", "b", "c", "d"])


def test_the_report_is_sorted(repository: Path) -> None:
    write(repository, node("b", "accepted"), node("a", "accepted"))
    commit_all(repository, "first")
    clear_tree(repository)
    write(repository, node("c", "accepted"), node("d", "accepted"))
    paths = [str(problem.path) for problem in check_governance(repository).problems]
    assert paths == sorted(paths)
    assert len(set(paths)) == len(["a", "b", "c", "d"])


def test_a_base_with_a_duplicate_id_does_not_crash(repository: Path) -> None:
    write(repository, node("a"), node("a", file="knowledge/copy/node.md"))
    commit_all(repository)
    assert run_check(repository) == []


def test_pending_lists_each_proposal_in_order(repository: Path) -> None:
    spec = node("a", rules=[rule("b"), rule("c", "accepted")], exceptions=[stop("d")])
    write(repository, spec, node("z", "accepted"), node("y", "deprecated"))
    entities, problems = pending_entities(repository)
    assert problems == []
    assert [entity.label for entity in entities] == ["node a", "exception a d", "directive b"]
    assert [entity.line for entity in entities] == sorted(entity.line for entity in entities)


def test_pending_orders_files_by_path(repository: Path) -> None:
    write(repository, node("b"), node("a"))
    entities, _ = pending_entities(repository)
    assert [entity.name for entity in entities] == ["a", "b"]


def test_pending_reads_the_path_before_the_line(repository: Path) -> None:
    write(repository, node("a", rules=[rule("c")]), node("b"))
    entities, _ = pending_entities(repository)
    assert [entity.name for entity in entities] == ["a", "c", "b"]


def test_pending_stops_on_a_parse_problem(repository: Path) -> None:
    path = repository / "knowledge/a/node.md"
    path.parent.mkdir()
    path.write_text("no front matter\n", encoding="utf-8")
    entities, problems = pending_entities(repository)
    assert entities == []
    assert [problem.code for problem in problems] == ["front-matter"]


def invoke(*arguments: str) -> Result:
    return RUNNER.invoke(app, list(arguments))


def test_the_command_passes_and_prints_a_summary(repository: Path) -> None:
    write(repository, node("a"))
    commit_all(repository)
    result = invoke("governance", str(repository))
    assert result.exit_code == 0
    assert result.output == "1 entities checked, 0 problems\n"


def test_the_command_prints_a_note(repository: Path) -> None:
    write(repository, node("a"))
    result = invoke("governance", str(repository))
    assert result.exit_code == 0
    assert result.output == f"note: {NO_COMMIT_NOTE}\n1 entities checked, 0 problems\n"


def test_the_command_fails_and_prints_each_location(repository: Path) -> None:
    write(repository, node("a", "accepted"))
    commit_all(repository)
    write(repository, node("a", "accepted", definition="New."))
    result = invoke("governance", str(repository))
    assert result.exit_code == 1
    assert f"{repository}/knowledge/a/node.md:5: accepted-change: " in result.output
    assert result.output.endswith("1 entities checked, 1 problems\n")


def test_the_command_reads_the_current_folder_by_default(
    repository: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    write(repository, node("a", "accepted", knowledge_type="workspace"))
    monkeypatch.chdir(repository)
    result = invoke("governance")
    assert result.exit_code == 1
    assert result.output.split("\n")[1].startswith("knowledge/a/node.md:")


def test_the_command_passes_on_an_empty_tree(repository: Path) -> None:
    result = invoke("governance", str(repository))
    assert result.exit_code == 0
    assert result.output == f"note: {NO_COMMIT_NOTE}\n0 entities checked, 0 problems\n"


def test_the_command_lists_what_waits_for_review(repository: Path) -> None:
    spec = node("a", rules=[rule("b")])
    write(repository, spec, node("c", "accepted"))
    result = invoke("governance", str(repository), "--pending")
    assert result.exit_code == 0
    assert result.output == (
        f"{repository}/{line_of(spec, 'status: proposed')}: node a\n"
        f"{repository}/{line_of(spec, '  - status: proposed')}: directive b\n"
        "2 entities wait for review, 0 problems\n"
    )


def test_the_pending_list_does_not_run_the_checks(repository: Path) -> None:
    write(repository, node("a", "accepted", knowledge_type="workspace"))
    result = invoke("governance", str(repository), "--pending")
    assert result.exit_code == 0
    assert result.output == "0 entities wait for review, 0 problems\n"


def test_the_pending_list_fails_on_a_parse_problem(repository: Path) -> None:
    path = repository / "knowledge/a/node.md"
    path.parent.mkdir()
    path.write_text("no front matter\n", encoding="utf-8")
    result = invoke("governance", str(repository), "--pending")
    assert result.exit_code == 1
    assert f"{path}:1: front-matter: " in result.output


def root_for(*targets: str) -> Spec:
    return {"id": "root", "status": "accepted", "kind": "ka:Root", "pointers": list(targets)}


def test_the_directive_list_shows_a_proposal(tmp_path: Path) -> None:
    write(
        tmp_path,
        root_for("a", "b"),
        node("a", "accepted", rules=[rule("x", "accepted"), rule("y", text="Do the new thing.")]),
        concept("b", "a", status="accepted"),
    )
    result = invoke("directives", str(tmp_path), "--at", "b")
    assert result.exit_code == 0, result.output
    assert result.output == (
        "x (subtree) from a -> b: Do the x thing.\n"
        "proposed: y (subtree) from a -> b: Do the new thing.\n"
        "1 directives apply at b, 1 proposed, 0 problems\n"
    )


def test_the_directive_list_shows_a_proposed_exception(tmp_path: Path) -> None:
    write(
        tmp_path,
        root_for("a", "b"),
        node("a", "accepted", rules=[rule("x", "accepted")]),
        concept("b", "a", status="accepted", exceptions=[stop("x")]),
    )
    result = invoke("directives", str(tmp_path), "--at", "b")
    assert result.exit_code == 0, result.output
    assert result.output == (
        "x (subtree) from a -> b: Do the x thing.\n"
        "proposed: an exception stops x here\n"
        "1 directives apply at b, 0 proposed, 0 problems\n"
    )


def repository_copy(tmp_path: Path) -> Path:
    for folder in ("knowledge", "skills", "governance"):
        shutil.copytree(REPO / folder, tmp_path / folder)
    return tmp_path


def test_the_repository_policies_pass_each_check() -> None:
    items = check_tree(REPO)
    assert items[1] == []
    assert check_directives(REPO)[1] == []
    assert check_language(REPO)[1] == []
    assert check_items(items[0], REPO) == []


def policy_items() -> list[ParsedNode]:
    items, problems = parse_tree([REPO / "governance/policies"])
    assert problems == []
    return items


def test_the_policies_join_the_graph() -> None:
    graph_ids = {item.node.id for item in check_tree(REPO)[0]}
    assert {item.node.id for item in policy_items()} <= graph_ids
    assert {"governance", "lifecycle", "approval", "change-rules"} <= graph_ids


def test_each_policy_is_template_domain_knowledge() -> None:
    for item in policy_items():
        assert item.node.origin == "template"
        assert getattr(item.node, "knowledge_type") == "domain"  # noqa: B009


def test_the_governance_domain_governs_itself_and_the_root() -> None:
    domain = next(item.node for item in policy_items() if item.node.id == "governance")
    governs = getattr(domain, "governs")  # noqa: B009
    assert {"governance", "root"} <= set(governs)


def test_the_policies_hold_no_email_address() -> None:
    for path in (REPO / "governance/policies").rglob("node.md"):
        assert "@" not in path.read_text(encoding="utf-8")


def break_a_policy(repository: Path, old: str, new: str) -> Path:
    path = repository / "governance/policies/lifecycle/node.md"
    text = path.read_text(encoding="utf-8")
    assert old in text
    path.write_text(text.replace(old, new), encoding="utf-8")
    return path


def test_the_parser_reads_a_broken_policy(tmp_path: Path) -> None:
    repository = repository_copy(tmp_path)
    path = break_a_policy(repository, "kind: ka:Concept", "kind: ka:Nothing")
    result = invoke("parse", str(repository / "knowledge"), str(repository / "governance"))
    assert result.exit_code == 1
    assert f"{path}:3: kind: " in result.output


def test_the_graph_check_reads_a_broken_policy(tmp_path: Path) -> None:
    repository = repository_copy(tmp_path)
    path = break_a_policy(repository, "  - governance\n", "  - missing\n")
    problems = check_tree(repository)[1]
    assert (path, "reference") in {(problem.path, problem.code) for problem in problems}


def test_the_graph_check_reads_a_misplaced_policy(tmp_path: Path) -> None:
    repository = repository_copy(tmp_path)
    (repository / "governance/policies/lifecycle").rename(repository / "governance/lifecycle")
    problems = check_tree(repository)[1]
    path = repository / "governance/lifecycle/node.md"
    assert (path, "placement") in {(problem.path, problem.code) for problem in problems}


def test_the_directive_check_reads_a_broken_policy(tmp_path: Path) -> None:
    repository = repository_copy(tmp_path)
    path = break_a_policy(
        repository,
        "  - scope: node\n",
        "  - scope: node\n  - conflicts_with: run-checks-before-commit\n",
    )
    problems = check_directives(repository)[1]
    assert (path, "conflict") in {(problem.path, problem.code) for problem in problems}


def test_the_language_check_reads_a_broken_policy(tmp_path: Path) -> None:
    repository = repository_copy(tmp_path)
    path = break_a_policy(
        repository,
        "Do not change the `origin` of a node or a directive.",
        "You should not change it.",
    )
    problems = check_language(repository)[1]
    assert (path, "opening") in {(problem.path, problem.code) for problem in problems}


def test_the_governance_check_reads_a_broken_policy(tmp_path: Path) -> None:
    repository = repository_copy(tmp_path)
    path = break_a_policy(repository, "status: proposed\norigin", "status: deprecated\norigin")
    problems = check_governance(repository).problems
    assert (path, "deprecated-holder") in {(problem.path, problem.code) for problem in problems}


def test_a_project_can_delete_the_policies(tmp_path: Path) -> None:
    repository = repository_copy(tmp_path)
    shutil.rmtree(repository / "governance/policies")
    shutil.rmtree(repository / "knowledge")
    shutil.rmtree(repository / "skills")
    (repository / "knowledge").mkdir()
    (repository / "skills").mkdir()
    for branch in (repository / "governance/language/branches").glob("*.yaml"):
        branch.unlink()
    folders = [str(repository / name) for name in ("knowledge", "skills", "governance")]
    assert invoke("parse", *folders).exit_code == 0
    assert check_tree(repository)[1] == []
    assert check_directives(repository)[1] == []
    assert check_language(repository)[1] == []
    assert check_governance(repository).problems == []


def test_a_project_can_point_the_root_at_its_own_domain(tmp_path: Path) -> None:
    repository = repository_copy(tmp_path)
    shutil.rmtree(repository / "governance/policies")
    shutil.rmtree(repository / "knowledge")
    shutil.rmtree(repository / "skills")
    (repository / "skills").mkdir()
    for branch in (repository / "governance/language/branches").glob("*.yaml"):
        branch.unlink()
    (repository / "knowledge/own").mkdir(parents=True)
    (repository / "knowledge/node.md").write_text(
        "---\nid: root\nkind: ka:Root\ntitle: Root\nstatus: proposed\norigin: project\n"
        "pointers:\n  - kind: ka:TextPointer\n    target: own\n    trigger: You need it.\n---\n",
        encoding="utf-8",
    )
    (repository / "knowledge/own/node.md").write_text(
        "---\nid: own\nkind: ka:Domain\ntitle: Own\nstatus: proposed\norigin: project\n"
        "knowledge_type: domain\n---\n\n## Definition\n\nA domain.\n",
        encoding="utf-8",
    )
    assert check_tree(repository)[1] == []
    assert check_directives(repository)[1] == []
    assert check_language(repository)[1] == []
    assert check_governance(repository).problems == []


def test_a_new_copy_without_policies_still_passes(tmp_path: Path) -> None:
    (tmp_path / "knowledge").mkdir()
    (tmp_path / "skills").mkdir()
    assert check_tree(tmp_path) == ([], [])
    assert check_governance(tmp_path).problems == []
