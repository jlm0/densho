# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportMissingTypeStubs=false, reportOptionalMemberAccess=false
import copy
from pathlib import Path
from typing import Any

import pytest
from linkml_runtime.utils.schemaview import SchemaView
from rdflib import RDF, SH, BNode, Graph, Literal, URIRef

from engine.graph import check_graph, check_tree
from engine.graph.references import EDGE_FIELDS, references_of
from engine.graph.shapes import DENSHO, NODE_NAMESPACE, check_shapes, report_problems
from engine.graph.structure import MAX_POINTER_HOPS
from engine.parser import ParsedNode, parse_tree

type Fields = dict[str, Any]

REPO = Path(__file__).resolve().parents[1]
VIEW = SchemaView(str(REPO / "knowledge/governance/schema/metamodel.yaml"))
GOVERNED = {"status": "accepted", "origin": "template"}
KNOWLEDGE = {**GOVERNED, "knowledge_type": "domain"}
MISSING_ID = "and no node or directive has this ID."
NO_ROUTE = "No chain of pointers from the root node or a skill reaches this node."
NO_SKILL_EDGE = "Add uses or applies, so the skill names what it needs."
ROOT_MOVE = "Move the root node to knowledge/node.md."
SKILL_MOVE = "Move this skill to knowledge/skills."
DEPTH_LIMIT = 6


def text_pointer(target: str) -> Fields:
    return {"kind": "densho:TextPointer", "target": target, "trigger": "You need it."}


def skill_pointer(target: str) -> Fields:
    return {"kind": "densho:SkillPointer", "target": target, "trigger": "You need it."}


def directive(directive_id: str, **fields: object) -> Fields:
    return {"id": directive_id, "scope": "subtree", "basis": "judgment", **GOVERNED, **fields}


SAMPLE: dict[str, Fields] = {
    "root": {
        "file": "knowledge/node.md",
        "kind": "densho:Root",
        **GOVERNED,
        "pointers": [text_pointer("design"), skill_pointer("review")],
    },
    "design": {
        "file": "knowledge/nodes/design/node.md",
        "kind": "densho:Domain",
        **KNOWLEDGE,
        "pointers": [text_pointer("ui"), text_pointer("research")],
        "governs": ["root", "design"],
        "directives": [directive("use-a-verb"), directive("be-brief")],
    },
    "ui": {
        "file": "knowledge/nodes/design/ui/node.md",
        "kind": "densho:Discipline",
        **KNOWLEDGE,
        "broader": ["design"],
        "pointers": [text_pointer("visual"), text_pointer("motion")],
        "related": ["research"],
        "informs": ["research"],
    },
    "research": {
        "file": "knowledge/nodes/design/research/node.md",
        "kind": "densho:Discipline",
        **KNOWLEDGE,
        "broader": ["design"],
        "pointers": [text_pointer("ui")],
        "related": ["ui"],
        "informs": ["ui"],
    },
    "visual": {
        "file": "knowledge/nodes/design/ui/visual/node.md",
        "kind": "densho:PracticeArea",
        **KNOWLEDGE,
        "broader": ["ui", "design"],
        "pointers": [text_pointer("hierarchy")],
    },
    "motion": {
        "file": "knowledge/nodes/design/ui/motion/node.md",
        "kind": "densho:Concept",
        **KNOWLEDGE,
        "broader": ["ui"],
        "depends_on": ["hierarchy"],
    },
    "hierarchy": {
        "file": "knowledge/nodes/design/ui/visual/hierarchy/node.md",
        "kind": "densho:Concept",
        **KNOWLEDGE,
        "broader": ["visual"],
        "related": ["motion"],
        "directives": [directive("show-order", also_attached_to=["motion", "root"])],
    },
    "settings": {
        "file": "knowledge/nodes/settings/node.md",
        "kind": "densho:Concept",
        **GOVERNED,
        "knowledge_type": "workspace",
        "broader": ["hierarchy"],
        "implements": ["hierarchy"],
    },
    "review": {
        "file": "knowledge/skills/review/node.md",
        "kind": "densho:Skill",
        **KNOWLEDGE,
        "description": "Use this skill when you need it.",
        "invocation": "agent",
        "skill_type": "system",
        "uses": ["hierarchy"],
        "applies": ["use-a-verb"],
        "pointers": [text_pointer("settings")],
    },
}


def block(key: str, values: list[Any]) -> list[str]:
    lines = [f"{key}:"]
    for value in values:
        if isinstance(value, dict):
            pairs = [f"{name}: {item}" for name, item in value.items()]
            lines += [f"  - {pairs[0]}", *[f"    {pair}" for pair in pairs[1:]]]
        else:
            lines.append(f"  - {value}")
    return lines


def directive_lines(entry: Fields) -> list[str]:
    lines = [f"- Do the {entry['id']} thing. ^{entry['id']}"]
    for key, value in entry.items():
        if key != "id":
            parts = value if isinstance(value, list) else [value]
            lines += [f"  - {key}: {part}" for part in parts]
    return lines


def render(node_id: str, fields: Fields) -> str:
    front: Fields = {"id": node_id, "title": node_id.title(), **fields}
    directives: list[Fields] = front.pop("directives", [])
    body: str | None = front.pop("body", None)
    del front["file"]
    lines = ["---"]
    for key, value in front.items():
        lines += block(key, value) if isinstance(value, list) else [f"{key}: {value}"]
    lines += ["---", ""]
    if fields["kind"] not in {"densho:Root", "densho:Skill"}:
        lines += ["## Definition", "", f"The meaning of {node_id}.", ""]
    if directives:
        lines += ["## Directives", ""]
        for entry in directives:
            lines += directive_lines(entry)
        lines.append("")
    if body is not None:
        lines += [body, ""]
    return "\n".join(lines)


def write_tree(repository: Path, nodes: dict[str, Fields]) -> None:
    (repository / "knowledge").mkdir(exist_ok=True)
    for node_id, fields in nodes.items():
        path = repository / fields["file"]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render(node_id, fields), encoding="utf-8")


class Tree:
    def __init__(self, repository: Path) -> None:
        self.repository = repository
        self.nodes = copy.deepcopy(SAMPLE)

    def change(self, node_id: str, **fields: object) -> None:
        self.nodes[node_id].update(fields)

    def remove(self, node_id: str, field: str) -> None:
        del self.nodes[node_id][field]

    def problems(self) -> list[str]:
        write_tree(self.repository, self.nodes)
        return [str(problem) for problem in check_tree(Path())[1]]

    def codes(self) -> list[str]:
        return [problem.split(": ")[1] for problem in self.problems()]

    def lines(self, node_id: str, text: str) -> list[str]:
        write_tree(self.repository, self.nodes)
        path = self.nodes[node_id]["file"]
        lines = (self.repository / path).read_text(encoding="utf-8").split("\n")
        return [f"{path}:{number}" for number, line in enumerate(lines, 1) if text in line]

    def expect(self, node_id: str, text: str, code: str, message: str) -> str:
        return f"{self.lines(node_id, text)[-1]}: {code}: {message}"


@pytest.fixture
def tree(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Tree:
    monkeypatch.chdir(tmp_path)
    return Tree(tmp_path)


def test_the_sample_graph_passes(tree: Tree) -> None:
    assert tree.problems() == []


def test_the_sample_graph_parses_each_node(tree: Tree) -> None:
    write_tree(tree.repository, tree.nodes)
    items, problems = check_tree(Path())
    assert problems == []
    assert {item.node.id for item in items} == set(SAMPLE)


def test_an_empty_tree_passes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    write_tree(tmp_path, {})
    assert check_tree(Path()) == ([], [])


def test_check_graph_passes_with_no_nodes() -> None:
    assert check_graph([], Path()) == []


def test_a_missing_folder_is_a_parse_problem(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    assert [str(problem) for problem in check_tree(Path())[1]] == [
        "knowledge:1: folder: The folder does not exist."
    ]


def test_a_parse_problem_stops_the_graph_checks(tree: Tree) -> None:
    tree.change("motion", depends_on=["missing"], status="bad")
    problems = tree.problems()
    assert len(problems) == 1
    assert ": schema: status: " in problems[0]


def test_two_nodes_cannot_share_an_id(tree: Tree) -> None:
    write_tree(tree.repository, tree.nodes)
    copy_path = tree.repository / "knowledge/nodes/copy/node.md"
    copy_path.parent.mkdir(parents=True)
    original = tree.repository / "knowledge/nodes/design/ui/motion/node.md"
    copy_path.write_text(original.read_text(encoding="utf-8"), encoding="utf-8")
    message = "The ID motion is already in use at knowledge/nodes/copy/node.md:2."
    assert [str(problem) for problem in check_tree(Path())[1]] == [
        f"knowledge/nodes/design/ui/motion/node.md:2: duplicate-id: {message}"
    ]


def test_a_directive_cannot_share_the_id_of_a_node(tree: Tree) -> None:
    tree.change("design", directives=[directive("motion"), directive("use-a-verb")])
    location = tree.lines("design", "^motion")[0]
    assert tree.problems() == [
        tree.expect(
            "motion",
            "id: motion",
            "duplicate-id",
            f"The ID motion is already in use at {location}.",
        )
    ]


def test_two_directives_in_one_file_cannot_share_an_id(tree: Tree) -> None:
    tree.change("design", directives=[directive("use-a-verb"), directive("use-a-verb")])
    first, second = tree.lines("design", "^use-a-verb")
    assert tree.problems() == [
        f"{second}: duplicate-id: The ID use-a-verb is already in use at {first}."
    ]


def test_a_duplicate_id_stops_the_later_checks(tree: Tree) -> None:
    tree.change("design", directives=[directive("motion"), directive("use-a-verb")])
    tree.change("motion", depends_on=["missing"])
    assert tree.codes() == ["duplicate-id"]


def test_a_duplicate_id_does_not_stop_the_node_rules(tree: Tree) -> None:
    tree.change("design", directives=[directive("motion"), directive("use-a-verb")])
    tree.change("settings", knowledge_type="domain")
    tree.change("review", uses=[], applies=[])
    tree.change("visual", file="knowledge/skills/visual/node.md")
    assert sorted(tree.codes()) == ["duplicate-id", "implements", "placement", "skill"]


def remove_the_root(tree: Tree) -> None:
    tree.change("design", governs=["design"])
    tree.change("hierarchy", directives=[directive("show-order")])
    write_tree(tree.repository, tree.nodes)
    (tree.repository / "knowledge/node.md").unlink()


def test_a_graph_needs_a_root(tree: Tree) -> None:
    remove_the_root(tree)
    assert [str(problem) for problem in check_tree(Path())[1]] == [
        "knowledge/node.md:1: root: Add the root node to this file."
    ]


def second_root(tree: Tree, target: str) -> None:
    tree.nodes["extra"] = {
        "file": "knowledge/nodes/extra/node.md",
        "kind": "densho:Root",
        **GOVERNED,
        "pointers": [text_pointer(target)],
    }


def test_a_second_root_fails_the_folder_check(tree: Tree) -> None:
    second_root(tree, "design")
    assert tree.problems() == [tree.expect("extra", "kind: densho:Root", "placement", ROOT_MOVE)]


def test_a_second_root_stops_shapes_and_reachability(tree: Tree) -> None:
    second_root(tree, "design")
    tree.change("motion", related=["review"])
    tree.change("review", pointers=[])
    assert tree.codes() == ["placement"]


def test_a_wrong_root_count_does_not_stop_references_or_cycles(tree: Tree) -> None:
    second_root(tree, "missing")
    tree.change("motion", depends_on=["motion"])
    assert sorted(tree.codes()) == ["cycle", "placement", "reference"]


def test_a_missing_root_does_not_stop_references(tree: Tree) -> None:
    tree.change("motion", depends_on=["missing"])
    remove_the_root(tree)
    assert sorted(problem.code for problem in check_tree(Path())[1]) == ["reference", "root"]


def test_the_root_must_be_at_the_root_file(tree: Tree) -> None:
    tree.change("root", file="knowledge/nodes/top/node.md")
    assert tree.problems() == [tree.expect("root", "kind: densho:Root", "placement", ROOT_MOVE)]


def test_the_root_cannot_be_under_skills(tree: Tree) -> None:
    tree.change("root", file="knowledge/skills/root/node.md")
    assert tree.problems() == [tree.expect("root", "kind: densho:Root", "placement", ROOT_MOVE)]


def test_only_the_root_can_use_the_root_file(tree: Tree) -> None:
    tree.change("root", file="knowledge/nodes/top/node.md")
    tree.change("design", file="knowledge/node.md")
    only_root = "Only the root node can use this file. Set kind to densho:Root or move this node."
    assert tree.problems() == [
        tree.expect("design", "kind: densho:Domain", "placement", only_root),
        tree.expect("root", "kind: densho:Root", "placement", ROOT_MOVE),
    ]


def test_a_skill_must_be_under_skills(tree: Tree) -> None:
    tree.change("review", file="knowledge/nodes/review/node.md")
    assert tree.problems() == [tree.expect("review", "kind: densho:Skill", "placement", SKILL_MOVE)]


def test_a_knowledge_node_cannot_be_under_skills(tree: Tree) -> None:
    tree.change("motion", file="knowledge/skills/motion/node.md")
    assert tree.problems() == [
        tree.expect(
            "motion", "kind: densho:Concept", "placement", "Move this node out of knowledge/skills."
        )
    ]


@pytest.mark.parametrize(
    "file",
    ["knowledge/motion/node.md", "knowledge/.densho/motion/node.md", "knowledge/x/nodes/node.md"],
)
def test_a_knowledge_node_must_be_under_nodes(tree: Tree, file: str) -> None:
    tree.change("motion", file=file)
    assert tree.problems() == [
        tree.expect(
            "motion", "kind: densho:Concept", "placement", "Move this node to knowledge/nodes."
        )
    ]


def test_a_policy_node_joins_the_graph(tree: Tree) -> None:
    tree.change("motion", file="knowledge/governance/policies/motion/node.md")
    assert tree.problems() == []
    assert "motion" in {item.node.id for item in check_tree(Path())[0]}


def test_a_node_in_another_governance_folder_fails(tree: Tree) -> None:
    tree.change("motion", file="knowledge/governance/language/motion/node.md")
    assert tree.problems() == [
        tree.expect(
            "motion",
            "kind: densho:Concept",
            "placement",
            "Move this node to knowledge/governance/policies.",
        )
    ]


def test_a_node_beside_the_policy_folder_fails(tree: Tree) -> None:
    tree.change("motion", file="knowledge/governance/node.md")
    assert tree.codes() == ["placement"]


def test_a_skill_cannot_be_a_policy(tree: Tree) -> None:
    tree.change("review", file="knowledge/governance/policies/review/node.md")
    assert tree.problems() == [tree.expect("review", "kind: densho:Skill", "placement", SKILL_MOVE)]


def test_the_root_cannot_be_a_policy(tree: Tree) -> None:
    tree.change("root", file="knowledge/governance/policies/node.md")
    assert "placement" in tree.codes()


def test_a_parse_problem_in_a_policy_stops_the_graph_checks(tree: Tree) -> None:
    write_tree(tree.repository, tree.nodes)
    path = tree.repository / "knowledge/governance/policies/bad/node.md"
    path.parent.mkdir(parents=True)
    path.write_text("no front matter\n", encoding="utf-8")
    assert [problem.code for problem in check_tree(Path())[1]] == ["front-matter"]


def test_a_misnamed_file_under_governance_is_a_problem(tree: Tree) -> None:
    write_tree(tree.repository, tree.nodes)
    path = tree.repository / "knowledge/governance/schema/notes.md"
    path.parent.mkdir(parents=True)
    path.write_text("# Notes\n", encoding="utf-8")
    assert [problem.code for problem in check_tree(Path())[1]] == ["file-name"]


def test_a_missing_governance_folder_passes(tree: Tree) -> None:
    assert not (tree.repository / "knowledge/governance").exists()
    assert tree.problems() == []


def test_the_folder_check_reads_a_repository_path(tmp_path: Path) -> None:
    write_tree(tmp_path, copy.deepcopy(SAMPLE))
    assert check_tree(tmp_path)[1] == []


@pytest.mark.parametrize(
    ("node_id", "field", "value"),
    [
        ("motion", "broader", ["ui", "missing"]),
        ("motion", "related", ["missing"]),
        ("motion", "informs", ["missing"]),
        ("motion", "depends_on", ["missing"]),
        ("motion", "governs", ["missing"]),
        ("motion", "implements", ["missing"]),
        ("review", "uses", ["hierarchy", "missing"]),
        ("review", "applies", ["missing"]),
    ],
)
def test_each_edge_must_resolve(tree: Tree, node_id: str, field: str, value: list[str]) -> None:
    tree.change(node_id, **{field: value})
    message = f"{field} names 'missing', {MISSING_ID}"
    assert tree.expect(node_id, "  - missing", "reference", message) in tree.problems()


def test_a_pointer_target_must_resolve(tree: Tree) -> None:
    tree.change("visual", pointers=[text_pointer("hierarchy"), text_pointer("missing")])
    message = f"target names 'missing', {MISSING_ID}"
    assert tree.problems() == [tree.expect("visual", "target: missing", "reference", message)]


def test_a_directive_attachment_must_resolve(tree: Tree) -> None:
    attached = ["motion", "missing"]
    tree.change("hierarchy", directives=[directive("show-order", also_attached_to=attached)])
    message = f"also_attached_to names 'missing', {MISSING_ID}"
    assert tree.problems() == [
        tree.expect("hierarchy", "also_attached_to: missing", "reference", message)
    ]


@pytest.mark.parametrize(
    "value",
    ["foo:bar", "densho:Concept", "a b", "<x>", "Motion", "motion ", "http://example.com/x"],
)
def test_a_hostile_reference_is_a_problem_and_does_not_crash(tree: Tree, value: str) -> None:
    tree.change("motion", related=[f'"{value}"'])
    message = f"related names {value!a}, {MISSING_ID}"
    assert tree.problems() == [tree.expect("motion", f'  - "{value}"', "reference", message)]


@pytest.mark.parametrize(
    ("source", "shown"),
    [
        ('"a\\nb"', "'a\\nb'"),
        ('"\\e[31mred"', "'\\x1b[31mred'"),
        ('"caf\\u00e9"', "'caf\\xe9'"),
    ],
)
def test_a_reference_cannot_break_the_problem_line(tree: Tree, source: str, shown: str) -> None:
    tree.change("motion", related=[source])
    problems = tree.problems()
    assert len(problems) == 1
    assert "\n" not in problems[0]
    assert "\x1b" not in problems[0]
    assert f"related names {shown}," in problems[0]


def test_a_broken_reference_stops_shapes_and_reachability(tree: Tree) -> None:
    tree.change("root", pointers=[text_pointer("missing"), skill_pointer("review")])
    tree.change("motion", broader=["review"])
    assert tree.codes() == ["reference"]


def test_a_broken_reference_does_not_stop_cycles_or_associations(tree: Tree) -> None:
    tree.change("motion", depends_on=["motion", "missing"])
    tree.change("hierarchy", related=["visual"])
    assert sorted(tree.codes()) == ["association", "cycle", "reference"]


def test_the_sample_graph_has_each_reference_field(tree: Tree) -> None:
    add_task(tree, "visual")
    tree.change("root", use_a_skill=["use-a-verb"], create_a_rule=["be-brief"])
    write_tree(tree.repository, tree.nodes)
    items, _ = parse_tree([Path("knowledge")])
    found = {reference.field for item in items for reference in references_of(item)}
    assert found == {*EDGE_FIELDS, "target", "also_attached_to"}


def test_each_schema_edge_is_listed() -> None:
    edges = {name for name, slot in VIEW.all_slots().items() if slot.is_a == "edge"}
    assert set(EDGE_FIELDS) == edges


@pytest.mark.parametrize(
    ("node_id", "field", "target", "target_kind"),
    [
        ("ui", "broader", "settings", "densho:Concept"),
        ("research", "broader", "visual", "densho:PracticeArea"),
        ("visual", "broader", "settings", "densho:Concept"),
        ("visual", "broader", "root", "densho:Root"),
        ("motion", "broader", "review", "densho:Skill"),
        ("motion", "broader", "use-a-verb", "densho:Directive"),
        ("motion", "related", "review", "densho:Skill"),
        ("motion", "informs", "root", "densho:Root"),
        ("motion", "depends_on", "use-a-verb", "densho:Directive"),
        ("motion", "governs", "use-a-verb", "densho:Directive"),
        ("review", "uses", "review", "densho:Skill"),
        ("review", "applies", "hierarchy", "densho:Concept"),
    ],
)
def test_each_edge_range_comes_from_the_schema(
    tree: Tree, node_id: str, field: str, target: str, target_kind: str
) -> None:
    tree.change(node_id, **{field: [target]})
    message = f"{field} cannot name {target}, which has kind {target_kind}."
    assert tree.expect(node_id, f"  - {target}", "type", message) in tree.problems()


@pytest.mark.parametrize(
    ("node_id", "target"),
    [
        ("ui", "design"),
        ("visual", "design"),
        ("visual", "ui"),
        ("visual", "research"),
        ("motion", "design"),
        ("motion", "research"),
        ("motion", "visual"),
        ("settings", "motion"),
    ],
)
def test_broader_accepts_each_allowed_rank(tree: Tree, node_id: str, target: str) -> None:
    tree.change(node_id, broader=[target])
    assert "type" not in tree.codes()


def test_implements_has_a_taxonomy_range(tree: Tree) -> None:
    tree.change("settings", implements=["hierarchy", "review"])
    message = "implements cannot name review, which has kind densho:Skill."
    assert tree.problems() == [tree.expect("settings", "  - review", "type", message)]


def test_a_type_problem_names_the_right_list_item(tree: Tree) -> None:
    tree.change("visual", broader=["ui", "motion", "design"])
    tree.remove("hierarchy", "related")
    message = "broader cannot name motion, which has kind densho:Concept."
    assert tree.problems() == [tree.expect("visual", "  - motion", "type", message)]


def test_a_skill_pointer_must_target_a_skill(tree: Tree) -> None:
    tree.change(
        "visual",
        pointers=[text_pointer("hierarchy"), skill_pointer("hierarchy"), skill_pointer("review")],
    )
    second = tree.lines("visual", "target: hierarchy")[1]
    assert tree.problems() == [
        f"{second}: type: target cannot name hierarchy, which has kind densho:Concept."
    ]


def test_a_skill_pointer_can_target_a_skill(tree: Tree) -> None:
    tree.change("visual", pointers=[text_pointer("hierarchy"), skill_pointer("review")])
    assert tree.problems() == []


def test_a_text_pointer_cannot_target_a_directive(tree: Tree) -> None:
    tree.change("visual", pointers=[text_pointer("hierarchy"), text_pointer("use-a-verb")])
    message = "target cannot name use-a-verb, which has kind densho:Directive."
    assert tree.problems() == [tree.expect("visual", "target: use-a-verb", "type", message)]


def test_a_directive_cannot_attach_to_a_directive(tree: Tree) -> None:
    tree.change(
        "hierarchy",
        directives=[directive("show-order", also_attached_to=["motion", "use-a-verb"])],
    )
    message = "also_attached_to cannot name use-a-verb, which has kind densho:Directive."
    assert tree.problems() == [
        tree.expect("hierarchy", "also_attached_to: use-a-verb", "type", message)
    ]


def test_a_graph_needs_a_knowledge_node(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    write_tree(tmp_path, {"root": {**SAMPLE["root"], "pointers": [text_pointer("root")]}})
    message = "nodes: List should have at least 1 item after validation, not 0"
    assert [str(problem) for problem in check_tree(Path())[1]] == [
        f"knowledge/node.md:2: schema: {message}"
    ]


def test_a_skill_needs_uses_or_applies(tree: Tree) -> None:
    tree.remove("review", "uses")
    tree.remove("review", "applies")
    assert tree.problems() == [tree.expect("review", "id: review", "skill", NO_SKILL_EDGE)]


@pytest.mark.parametrize("name", ["synced", "anthropic-skills"])
def test_a_skill_with_a_reserved_name_fails(tree: Tree, name: str) -> None:
    tree.change("root", pointers=[text_pointer("design"), skill_pointer(name)])
    tree.change("review", id=name)
    message = (
        f"Claude Code reserves the skill name {name}, so the skill does not load. "
        "Choose another ID."
    )
    assert tree.problems() == [tree.expect("review", f"id: {name}", "skill", message)]


@pytest.mark.parametrize("name", ["synced-notes", "anthropic", "skills"])
def test_a_skill_name_near_a_reserved_name_passes(tree: Tree, name: str) -> None:
    tree.change("root", pointers=[text_pointer("design"), skill_pointer(name)])
    tree.change("review", id=name)
    assert tree.problems() == []


def test_empty_uses_and_applies_do_not_count(tree: Tree) -> None:
    tree.change("review", uses=[], applies=[])
    assert tree.problems() == [tree.expect("review", "id: review", "skill", NO_SKILL_EDGE)]


@pytest.mark.parametrize("field", ["uses", "applies"])
def test_one_of_uses_or_applies_is_enough(tree: Tree, field: str) -> None:
    tree.remove("review", field)
    assert tree.problems() == []


def test_implements_needs_workspace_knowledge(tree: Tree) -> None:
    tree.change("settings", knowledge_type="domain")
    message = "Only workspace knowledge can use implements. Set knowledge_type to workspace."
    assert tree.problems() == [tree.expect("settings", "implements:", "implements", message)]


def test_a_workspace_node_can_skip_implements(tree: Tree) -> None:
    tree.remove("settings", "implements")
    assert tree.problems() == []


@pytest.mark.parametrize(
    ("node_id", "target"),
    [
        ("hierarchy", "visual"),
        ("hierarchy", "design"),
        ("design", "hierarchy"),
        ("visual", "hierarchy"),
    ],
)
def test_related_cannot_join_a_broader_chain(tree: Tree, node_id: str, target: str) -> None:
    tree.change(node_id, related=[target])
    message = f"related names {target}, which is in the broader chain of this node."
    assert tree.problems() == [tree.expect(node_id, f"  - {target}", "association", message)]


def test_related_names_the_right_list_item(tree: Tree) -> None:
    tree.change("hierarchy", related=["motion", "visual"])
    message = "related names visual, which is in the broader chain of this node."
    lines = tree.lines("hierarchy", "  - visual")
    assert tree.problems() == [f"{lines[-1]}: association: {message}"]


def test_a_broken_reference_is_not_part_of_a_broader_chain(tree: Tree) -> None:
    tree.change("motion", broader=["ui", '"a b"'], related=['"a b"'])
    assert tree.codes() == ["reference", "reference"]


def test_a_node_can_name_itself_in_related(tree: Tree) -> None:
    tree.change("motion", related=["motion"])
    assert tree.problems() == []


def test_related_can_join_siblings_in_a_loop(tree: Tree) -> None:
    tree.change("motion", related=["hierarchy"])
    assert tree.problems() == []


def test_broader_cannot_form_a_cycle(tree: Tree) -> None:
    tree.change("hierarchy", broader=["settings"])
    tree.remove("settings", "implements")
    message = "This broader edge closes a cycle: hierarchy -> settings -> hierarchy."
    assert tree.problems() == [tree.expect("hierarchy", "  - settings", "cycle", message)]


def test_broader_cannot_name_itself(tree: Tree) -> None:
    tree.change("motion", broader=["ui", "motion"])
    message = "This broader edge closes a cycle: motion -> motion."
    assert tree.problems() == [tree.expect("motion", "  - motion", "cycle", message)]


def test_depends_on_cannot_form_a_cycle(tree: Tree) -> None:
    tree.change("motion", depends_on=["visual"])
    tree.change("visual", depends_on=["hierarchy"])
    tree.change("hierarchy", depends_on=["motion"])
    message = "This depends_on edge closes a cycle: hierarchy -> motion -> visual -> hierarchy."
    assert tree.problems() == [tree.expect("hierarchy", "  - motion", "cycle", message)]


def test_depends_on_cannot_name_itself(tree: Tree) -> None:
    tree.change("motion", depends_on=["motion"])
    message = "This depends_on edge closes a cycle: motion -> motion."
    assert tree.problems() == [tree.expect("motion", "  - motion", "cycle", message)]


def test_a_cycle_names_the_shortest_route_from_the_first_id(tree: Tree) -> None:
    tree.change("hierarchy", depends_on=["visual", "ui"])
    tree.change("visual", depends_on=["ui"])
    tree.change("ui", depends_on=["hierarchy"])
    tree.remove("motion", "depends_on")
    message = "This depends_on edge closes a cycle: hierarchy -> ui -> hierarchy."
    assert tree.problems() == [tree.expect("hierarchy", "  - ui", "cycle", message)]


def test_a_cycle_breaks_a_tie_by_id(tree: Tree) -> None:
    tree.change("hierarchy", depends_on=["visual", "ui"])
    tree.change("visual", depends_on=["hierarchy"])
    tree.change("ui", depends_on=["hierarchy"])
    tree.remove("motion", "depends_on")
    message = "This depends_on edge closes a cycle: hierarchy -> ui -> hierarchy."
    assert tree.problems() == [tree.expect("hierarchy", "  - ui", "cycle", message)]


def test_a_cycle_stays_inside_its_component(tree: Tree) -> None:
    tree.change("hierarchy", depends_on=["ui", "motion"])
    tree.change("motion", depends_on=["hierarchy"])
    tree.change("ui", depends_on=["visual"])
    message = "This depends_on edge closes a cycle: hierarchy -> motion -> hierarchy."
    assert tree.problems() == [tree.expect("hierarchy", "  - motion", "cycle", message)]


def test_each_separate_cycle_is_reported(tree: Tree) -> None:
    tree.change("motion", depends_on=["visual"])
    tree.change("visual", depends_on=["motion"])
    tree.change("hierarchy", depends_on=["ui"])
    tree.change("ui", depends_on=["hierarchy"])
    first = "This depends_on edge closes a cycle: hierarchy -> ui -> hierarchy."
    second = "This depends_on edge closes a cycle: motion -> visual -> motion."
    assert tree.problems() == [
        tree.expect("motion", "  - visual", "cycle", second),
        tree.expect("hierarchy", "  - ui", "cycle", first),
    ]


def test_edges_of_two_kinds_do_not_form_a_cycle(tree: Tree) -> None:
    tree.change("visual", depends_on=["motion"])
    tree.change("motion", broader=["visual"])
    assert "cycle" not in tree.codes()


@pytest.mark.parametrize("field", ["related", "informs"])
def test_other_edges_can_form_a_cycle(tree: Tree, field: str) -> None:
    tree.change("motion", **{field: ["research"]})
    tree.change("research", **{field: ["motion"]})
    assert tree.problems() == []


def test_governs_can_form_a_cycle(tree: Tree) -> None:
    tree.change("motion", governs=["research"])
    tree.change("research", governs=["motion"])
    assert tree.problems() == []


def test_a_node_can_govern_itself(tree: Tree) -> None:
    tree.change("motion", governs=["motion"])
    assert tree.problems() == []


def test_a_node_with_no_pointer_is_unreachable(tree: Tree) -> None:
    tree.change("review", pointers=[])
    assert tree.problems() == [tree.expect("settings", "id: settings", "unreachable", NO_ROUTE)]


def test_edges_do_not_make_a_node_reachable(tree: Tree) -> None:
    tree.change("visual", pointers=[])
    assert tree.problems() == [tree.expect("hierarchy", "id: hierarchy", "unreachable", NO_ROUTE)]


def test_a_skill_is_an_entry_point(tree: Tree) -> None:
    tree.change("root", pointers=[text_pointer("design")])
    assert tree.problems() == []


def test_a_skill_reaches_a_node_that_the_root_does_not(tree: Tree) -> None:
    tree.change("root", pointers=[text_pointer("settings"), skill_pointer("review")])
    tree.change("review", pointers=[text_pointer("design"), text_pointer("settings")])
    assert tree.problems() == []


def test_the_root_is_an_entry_point(tree: Tree) -> None:
    tree.change("root", pointers=[text_pointer("settings"), text_pointer("design")])
    tree.change("review", pointers=[])
    assert tree.problems() == []


def test_a_pointer_loop_with_no_entry_point_is_unreachable(tree: Tree) -> None:
    tree.change("design", pointers=[])
    problems = tree.problems()
    assert problems == [
        tree.expect(node_id, f"id: {node_id}", "unreachable", NO_ROUTE)
        for node_id in ("research", "motion", "ui", "hierarchy", "visual")
    ]


def chain_tree(tree: Tree, hops: int) -> None:
    previous = "root"
    for index in range(1, hops + 1):
        node_id = f"hop-{index}"
        tree.nodes[node_id] = {
            "file": f"knowledge/nodes/chain/{index}/node.md",
            "kind": "densho:Domain",
            **KNOWLEDGE,
        }
        tree.nodes[previous].setdefault("pointers", []).append(text_pointer(node_id))
        previous = node_id


def test_the_limit_is_six_hops() -> None:
    assert MAX_POINTER_HOPS == DEPTH_LIMIT


def test_six_hops_pass(tree: Tree) -> None:
    chain_tree(tree, DEPTH_LIMIT)
    assert tree.problems() == []


def test_seven_hops_fail(tree: Tree) -> None:
    chain_tree(tree, DEPTH_LIMIT + 1)
    message = (
        "The shortest pointer route takes 7 hops, and the limit is 6: "
        "root -> hop-1 -> hop-2 -> hop-3 -> hop-4 -> hop-5 -> hop-6 -> hop-7."
    )
    assert tree.problems() == [tree.expect("hop-7", "id: hop-7", "depth", message)]


def test_each_node_past_the_limit_fails(tree: Tree) -> None:
    chain_tree(tree, DEPTH_LIMIT + 2)
    assert [problem.split(":")[0] for problem in tree.problems() if ": depth: " in problem] == [
        "knowledge/nodes/chain/7/node.md",
        "knowledge/nodes/chain/8/node.md",
    ]


def test_a_shorter_route_from_a_skill_passes(tree: Tree) -> None:
    chain_tree(tree, DEPTH_LIMIT + 1)
    tree.nodes["review"]["pointers"].append(text_pointer("hop-7"))
    assert tree.problems() == []


def test_a_shorter_route_from_the_root_passes(tree: Tree) -> None:
    chain_tree(tree, DEPTH_LIMIT + 1)
    tree.nodes["root"]["pointers"].append(text_pointer("hop-7"))
    assert tree.problems() == []


def test_problems_come_in_path_and_line_order(tree: Tree) -> None:
    tree.change("hierarchy", depends_on=["missing"], related=["visual", "motion"])
    tree.change("motion", depends_on=["other-missing"])
    write_tree(tree.repository, tree.nodes)
    problems = check_tree(Path())[1]
    keys = [(str(problem.path), problem.line) for problem in problems]
    assert keys == sorted(keys)
    assert [problem.code for problem in problems] == ["reference", "association", "reference"]


def test_two_equal_results_give_one_problem(tree: Tree) -> None:
    tree.change("motion", related=["review", "review"])
    message = "related cannot name review, which has kind densho:Skill."
    first = tree.lines("motion", "  - review")[0]
    assert tree.problems() == [f"{first}: type: {message}"]


@pytest.mark.parametrize("field", ["title", "description"])
@pytest.mark.parametrize(
    "value",
    ['"densho:Concept"', '"<x> \\"q\\" é"', '"[a](b)"', '"http://x y"', '"{a}"', '"a @en"'],
)
def test_a_hostile_text_value_does_not_crash(tree: Tree, field: str, value: str) -> None:
    tree.change("root", pointers=[text_pointer("design")])
    tree.change("visual", pointers=[text_pointer("hierarchy"), skill_pointer("review")])
    tree.nodes["review"][field] = value
    assert tree.problems() == []


def test_a_hostile_source_does_not_crash(tree: Tree) -> None:
    tree.change("review", sources=['"foo:bar baz"', '"<not an iri>"'])
    assert tree.problems() == []


def test_a_hostile_trigger_and_path_do_not_crash(tree: Tree) -> None:
    pointer = {
        "kind": "densho:PathPointer",
        "target": "settings",
        "trigger": '"foo:bar <x>"',
        "paths": '["densho:y <z>"]',
    }
    tree.change("review", pointers=[pointer])
    assert tree.problems() == []


@pytest.mark.parametrize("field", ["related", "informs", "depends_on", "governs", "sources"])
def test_an_empty_list_does_not_crash(tree: Tree, field: str) -> None:
    tree.change("motion", **{field: []})
    assert tree.problems() == []


@pytest.mark.parametrize("value", ['"a\\x00b"', '"\\e[31m"', '"\\uFEFFx"', '"\\U0001F600"'])
def test_an_escaped_text_value_does_not_crash(tree: Tree, value: str) -> None:
    tree.change("motion", title=value, sources=[value])
    assert tree.problems() == []


def test_a_lone_surrogate_in_a_text_value_fails_with_a_problem(tree: Tree) -> None:
    tree.change("motion", title='"\\uD800"')
    assert [problem.split(": ")[1] for problem in tree.problems()] == ["yaml"]


def report_with(focus: URIRef | BNode | None, path: URIRef | None, value: URIRef | None) -> Graph:
    report = Graph()
    result = BNode()
    report.add((result, RDF.type, SH.ValidationResult))
    report.add((result, SH.resultMessage, Literal("Line one\nline two")))
    for predicate, term in ((SH.focusNode, focus), (SH.resultPath, path), (SH.value, value)):
        if term is not None:
            report.add((result, predicate, term))
    return report


@pytest.fixture
def parsed(tree: Tree) -> list[ParsedNode]:
    write_tree(tree.repository, tree.nodes)
    return parse_tree([Path("knowledge")])[0]


def root_of(items: list[ParsedNode]) -> ParsedNode:
    return next(item for item in items if item.node.id == "root")


BROADER = URIRef("http://www.w3.org/2004/02/skos/core#broader")
MOTION = URIRef(f"{NODE_NAMESPACE}motion")


@pytest.mark.parametrize(
    ("focus", "path", "value"),
    [
        (URIRef(f"{NODE_NAMESPACE}unknown"), BROADER, MOTION),
        (URIRef(f"{NODE_NAMESPACE}ui"), BROADER, URIRef(f"{NODE_NAMESPACE}unknown")),
        (URIRef(f"{NODE_NAMESPACE}ui"), None, MOTION),
        (BNode(), DENSHO.target, MOTION),
        (None, None, None),
    ],
)
def test_a_result_that_has_no_location_is_still_a_problem(
    parsed: list[ParsedNode],
    focus: URIRef | BNode | None,
    path: URIRef | None,
    value: URIRef | None,
) -> None:
    problems = report_problems(report_with(focus, path, value), Graph(), parsed, root_of(parsed))
    assert [str(problem) for problem in problems] == [
        "knowledge/node.md:2: shape: 'Line one\\nline two'"
    ]


def test_a_pointer_with_another_kind_has_no_location(parsed: list[ParsedNode]) -> None:
    focus = BNode()
    data = Graph()
    data.add((URIRef(f"{NODE_NAMESPACE}root"), DENSHO.pointers, focus))
    data.add((focus, RDF.type, DENSHO.PathPointer))
    report = report_with(focus, DENSHO.target, URIRef(f"{NODE_NAMESPACE}design"))
    problems = report_problems(report, data, parsed, root_of(parsed))
    assert [problem.code for problem in problems] == ["shape"]


def test_a_failed_shacl_run_is_a_problem(
    parsed: list[ParsedNode], monkeypatch: pytest.MonkeyPatch
) -> None:
    def failed(*_: object, **__: object) -> tuple[bool, Exception, str]:
        return False, RuntimeError("no"), "Validation Failure\nno"

    monkeypatch.setattr("pyshacl.validate", failed)
    assert [str(problem) for problem in check_shapes(parsed)] == [
        "knowledge/node.md:2: shape: 'Validation Failure\\nno'"
    ]


def test_shacl_does_not_change_the_cached_graphs(tree: Tree) -> None:
    assert tree.problems() == []
    tree.change("settings", implements=["review"])
    assert tree.codes() == ["type"]
    tree.change("settings", implements=["hierarchy"])
    assert tree.problems() == []


REJECTED = {"status": "rejected", "rejection_reason": "No need."}


def test_a_rejected_node_needs_no_route(tree: Tree) -> None:
    tree.nodes["old"] = {
        "file": "knowledge/nodes/design/old/node.md",
        "kind": "densho:Concept",
        **KNOWLEDGE,
        **REJECTED,
        "broader": ["design"],
    }
    assert tree.problems() == []


def test_a_rejected_skill_is_not_an_entry_point(tree: Tree) -> None:
    tree.change("review", **REJECTED)
    assert tree.problems() == [tree.expect("settings", "id: settings", "unreachable", NO_ROUTE)]


def test_a_pointer_from_a_rejected_node_reaches_nothing(tree: Tree) -> None:
    tree.change("visual", **REJECTED)
    assert tree.problems() == [tree.expect("hierarchy", "id: hierarchy", "unreachable", NO_ROUTE)]


STEP_TEXT = "## Inputs\n\nA.\n\n## Procedure\n\nB.\n\n## Output\n\nC.\n\n## Exit gate\n\nD.\n"
TASK_FILE = "knowledge/skills/task/node.md"
TASK_ROW = {"kind": "densho:SkillPointer", "target": "task", "trigger": "You change the ui."}
NO_ROW = (
    "Add a densho:SkillPointer to this skill on the root, "
    "so the skill table of AGENTS.md names its activity."
)


def add_task(tree: Tree, *steps: str) -> None:
    tree.nodes["task"] = {
        "file": TASK_FILE,
        "kind": "densho:Skill",
        **KNOWLEDGE,
        "description": "Run the ui task. Use when you change the ui.",
        "invocation": "agent",
        "skill_type": "task",
        "uses": ["ui"],
        "steps": list(steps),
    }
    tree.change("root", pointers=[*tree.nodes["root"]["pointers"], TASK_ROW])
    write_steps(tree, *steps)


def write_steps(tree: Tree, *steps: str) -> None:
    folder = tree.repository / "knowledge/skills/task/steps"
    folder.mkdir(parents=True, exist_ok=True)
    for step in steps:
        (folder / f"{step}.md").write_text(STEP_TEXT, encoding="utf-8")


def test_a_task_with_its_steps_passes(tree: Tree) -> None:
    add_task(tree, "visual", "motion")
    assert tree.problems() == []


def test_a_lens_with_a_row_passes(tree: Tree) -> None:
    tree.change("review", skill_type="lens")
    assert tree.problems() == []


@pytest.mark.parametrize("kind", ["task", "lens"])
def test_a_task_or_lens_skill_needs_agent_invocation(tree: Tree, kind: str) -> None:
    tree.change("review", skill_type=kind, invocation="person")
    if kind == "task":
        tree.change("review", uses=["ui"], applies=[], steps=["visual"])
        tree.nodes["review"]["file"] = "knowledge/skills/review/node.md"
        folder = tree.repository / "knowledge/skills/review/steps"
        folder.mkdir(parents=True)
        (folder / "visual.md").write_text(STEP_TEXT, encoding="utf-8")
    message = "A task or lens skill needs invocation: agent, so the agent starts it."
    assert tree.problems() == [tree.expect("review", "invocation: person", "skill", message)]


@pytest.mark.parametrize("kind", ["task", "lens"])
def test_a_task_or_lens_skill_needs_a_row(tree: Tree, kind: str) -> None:
    if kind == "task":
        add_task(tree, "visual")
        tree.change("root", pointers=[text_pointer("design"), skill_pointer("review")])
        tree.change("visual", pointers=[text_pointer("hierarchy"), skill_pointer("task")])
        assert tree.problems() == [tree.expect("task", "skill_type: task", "skill", NO_ROW)]
    else:
        tree.change("review", skill_type="lens")
        tree.change("root", pointers=[text_pointer("design")])
        tree.change("visual", pointers=[text_pointer("hierarchy"), skill_pointer("review")])
        assert tree.problems() == [tree.expect("review", "skill_type: lens", "skill", NO_ROW)]


def test_a_system_skill_needs_no_row_and_can_start_by_a_person(tree: Tree) -> None:
    tree.change("root", pointers=[text_pointer("design")])
    tree.change("visual", pointers=[text_pointer("hierarchy"), skill_pointer("review")])
    tree.change("review", invocation="person")
    assert tree.problems() == []


def test_a_row_needs_its_activity_in_the_description(tree: Tree) -> None:
    tree.change("review", description="Use this skill for a review.")
    message = (
        "The description of review does not name this activity. "
        "Put the activity in its Use when sentence."
    )
    assert tree.problems() == [tree.expect("root", "trigger: You need it.", "skill", message)]


def test_a_row_activity_drops_its_capital_and_its_period(tree: Tree) -> None:
    tree.change("review", description="Use this skill when You need it.")
    assert tree.codes() == ["skill"]
    tree.change("review", description="Use this skill when you need it")
    assert tree.problems() == []


def test_a_text_pointer_to_a_skill_is_no_row(tree: Tree) -> None:
    other = {"kind": "densho:TextPointer", "target": "review", "trigger": "You plan a release."}
    tree.change("root", pointers=[*tree.nodes["root"]["pointers"], other])
    assert tree.problems() == []


def test_a_row_to_a_node_that_is_no_skill_is_a_type_problem_only(tree: Tree) -> None:
    tree.change(
        "root", pointers=[text_pointer("design"), skill_pointer("review"), skill_pointer("ui")]
    )
    assert tree.codes() == ["type"]


def test_a_system_skill_has_no_steps(tree: Tree) -> None:
    tree.change("review", steps=["visual"])
    message = "A system skill has no steps. Remove steps, or set skill_type to task."
    assert tree.problems() == [tree.expect("review", "steps:", "step", message)]


def test_a_system_skill_has_no_step_files(tree: Tree) -> None:
    folder = tree.repository / "knowledge/skills/review/steps"
    folder.mkdir(parents=True)
    (folder / "visual.md").write_text(STEP_TEXT, encoding="utf-8")
    message = "A system skill has no step files. Remove steps/, or set skill_type to task."
    assert tree.problems() == [tree.expect("review", "skill_type: system", "step", message)]


def test_a_lens_in_the_tree_form_fails(tree: Tree) -> None:
    tree.change("review", skill_type="lens", steps=["visual"])
    folder = tree.repository / "knowledge/skills/review/steps"
    folder.mkdir(parents=True)
    (folder / "visual.md").write_text(STEP_TEXT, encoding="utf-8")
    message = "Write the step files of a lens in the copy form, with front matter."
    assert tree.problems() == [tree.expect("review", "steps:", "step", message)]


def test_a_step_file_with_no_entry_in_steps_fails_for_a_lens(tree: Tree) -> None:
    tree.change("review", skill_type="lens")
    folder = tree.repository / "knowledge/skills/review/steps"
    folder.mkdir(parents=True)
    (folder / "visual.md").write_text(STEP_TEXT, encoding="utf-8")
    message = "No entry in steps of review names this step file. Add one, or remove the file."
    assert tree.problems() == [f"knowledge/skills/review/steps/visual.md:1: step: {message}"]


def test_a_task_needs_steps(tree: Tree) -> None:
    add_task(tree)
    message = "Name the steps of the task in steps, in their order."
    assert tree.problems() == [tree.expect("task", "skill_type: task", "step", message)]


def test_a_task_uses_exactly_one_node(tree: Tree) -> None:
    add_task(tree, "visual")
    tree.change("task", uses=["ui", "design"])
    message = "A task skill with the copy by tree uses exactly 1 node: its discipline."
    assert tree.problems() == [tree.expect("task", "uses:", "step", message)]


def test_a_task_with_no_uses_reports_it_at_the_skill(tree: Tree) -> None:
    add_task(tree, "visual")
    tree.change("task", uses=[], applies=["use-a-verb"])
    message = "A task skill with the copy by tree uses exactly 1 node: its discipline."
    assert tree.problems() == [tree.expect("task", "uses:", "step", message)]


def test_a_task_names_a_step_once(tree: Tree) -> None:
    add_task(tree, "visual", "visual")
    assert tree.problems() == [
        tree.expect("task", "  - visual", "step", "steps names visual twice.")
    ]


@pytest.mark.parametrize("step", ["hierarchy", "research"])
def test_a_step_sits_directly_under_the_discipline(tree: Tree, step: str) -> None:
    add_task(tree, step)
    message = f"{step} is not under ui. Name a node whose broader names ui."
    assert tree.problems() == [tree.expect("task", f"  - {step}", "step", message)]


def test_a_step_that_is_no_taxonomy_node_is_reported(tree: Tree) -> None:
    add_task(tree, "visual", "review")
    write_steps(tree, "review")
    message = "review is not under ui. Name a node whose broader names ui."
    assert tree.problems() == [tree.expect("task", "  - review", "step", message)]


def test_a_step_comes_before_each_step_it_informs(tree: Tree) -> None:
    add_task(tree, "visual", "motion")
    tree.change("motion", informs=["visual"])
    message = "motion informs visual, so motion comes before visual in steps."
    assert tree.problems() == [tree.expect("task", "  - motion", "step", message)]
    tree.change("task", steps=["motion", "visual"])
    assert tree.problems() == []


def test_a_step_needs_its_step_file(tree: Tree) -> None:
    add_task(tree, "visual")
    tree.change("task", steps=["visual", "motion"])
    message = "Add the step file steps/motion.md."
    assert tree.problems() == [tree.expect("task", "  - motion", "step", message)]


def test_a_step_file_needs_its_step(tree: Tree) -> None:
    add_task(tree, "visual", "motion")
    tree.change("task", steps=["visual"])
    message = "No entry in steps of task names this step file. Add one, or remove the file."
    assert tree.problems() == [f"knowledge/skills/task/steps/motion.md:1: step: {message}"]


def test_a_task_with_two_uses_still_checks_its_steps(tree: Tree) -> None:
    add_task(tree, "visual", "visual")
    tree.change("task", uses=["ui", "design"])
    assert tree.codes() == ["step", "step"]


SKILL_BODY = "## Exit checklist\n\n- [ ] It holds.\n\n## Output\n\nA result."
COPY_BODY = "\n## Procedure\n\n1. Do it.\n\n## Output\n\nA result.\n"


def copy_step(*directives: str, pages: tuple[str, ...] = (), branch: tuple[str, ...] = ()) -> str:
    lines = ["---", "title: Do the step"]
    if pages:
        lines.append("pages:")
        for page in pages:
            lines += [f"  - target: {page}", "    trigger: You need it."]
    if directives:
        lines += ["directives:", *[f"  - {name}" for name in directives]]
    if branch:
        lines += ["branches:", "  - condition: If the target is Android", "    directives:"]
        lines += [f"      - {name}" for name in branch]
    return "\n".join([*lines, "---", COPY_BODY])


def add_copy_task(tree: Tree, steps: dict[str, str], **fields: object) -> None:
    tree.nodes["task"] = {
        "file": TASK_FILE,
        "kind": "densho:Skill",
        **KNOWLEDGE,
        "description": "Run the ui task. Use when you change the ui.",
        "invocation": "agent",
        "skill_type": "task",
        "uses": ["ui"],
        "steps": list(steps),
        "body": SKILL_BODY,
        **fields,
    }
    tree.change("root", pointers=[*tree.nodes["root"]["pointers"], TASK_ROW])
    folder = tree.repository / "knowledge/skills/task/steps"
    folder.mkdir(parents=True, exist_ok=True)
    for name, text in steps.items():
        (folder / f"{name}.md").write_text(text, encoding="utf-8")


def step_line(name: str, text: str) -> str:
    path = Path("knowledge/skills/task/steps") / f"{name}.md"
    lines = path.read_text(encoding="utf-8").split("\n")
    return f"{path.as_posix()}:{lines.index(text) + 1}"


def test_a_task_with_copies_passes(tree: Tree) -> None:
    add_copy_task(
        tree,
        {
            "frame": copy_step("use-a-verb", pages=("hierarchy",), branch=("be-brief",)),
            "build": copy_step("use-a-verb"),
        },
        uses=["ui", "design"],
    )
    assert tree.problems() == []


def test_a_lens_with_copies_passes(tree: Tree) -> None:
    tree.change("review", skill_type="lens", steps=["check"], body=SKILL_BODY)
    folder = tree.repository / "knowledge/skills/review/steps"
    folder.mkdir(parents=True)
    (folder / "check.md").write_text(copy_step("be-brief"), encoding="utf-8")
    assert tree.problems() == []


def test_a_copy_of_an_unknown_id_fails_at_its_line(tree: Tree) -> None:
    add_copy_task(tree, {"frame": copy_step("use-a-verb", branch=("no-such",))})
    message = (
        "No directive has the ID no-such. A selection can remove the node that holds it. "
        "Name a directive of the graph, or remove the ID."
    )
    assert tree.problems() == [f"{step_line('frame', '      - no-such')}: step: {message}"]


def test_a_copy_of_a_rejected_directive_fails(tree: Tree) -> None:
    rejected = directive("be-brief", **REJECTED)
    tree.change("design", directives=[directive("use-a-verb"), rejected])
    add_copy_task(tree, {"frame": copy_step("be-brief")})
    message = "be-brief is rejected. Remove the ID."
    assert tree.problems() == [f"{step_line('frame', '  - be-brief')}: step: {message}"]


@pytest.mark.parametrize("page", ["nothing", "review", "use-a-verb"])
def test_a_page_that_is_not_a_node_fails(tree: Tree, page: str) -> None:
    add_copy_task(tree, {"frame": copy_step("use-a-verb", pages=(page,))})
    message = f"No page has the ID {page}. Name a node that is not a skill and not rejected."
    assert tree.problems() == [f"{step_line('frame', f'  - target: {page}')}: step: {message}"]


def test_a_page_that_is_rejected_fails(tree: Tree) -> None:
    tree.change("settings", **REJECTED)
    add_copy_task(tree, {"frame": copy_step("use-a-verb", pages=("settings",))})
    message = "No page has the ID settings. Name a node that is not a skill and not rejected."
    expected = f"{step_line('frame', '  - target: settings')}: step: {message}"
    assert expected in tree.problems()


def test_each_directive_of_the_skill_is_in_a_step(tree: Tree) -> None:
    add_copy_task(
        tree,
        {"frame": copy_step("own-rule")},
        directives=[directive("own-rule"), directive("other-rule", scope="node")],
    )
    message = "No step of task names other-rule. Add it to a step."
    assert tree.problems() == [tree.expect("task", "^other-rule", "step", message)]


@pytest.mark.parametrize(
    "body",
    [
        "## Output\n\nA result.",
        "## Exit checklist\n\n- [ ] It holds.",
        "## Exit checklist\n\n- [ ] It holds.\n\n## Output\n\nA result.\n\n## Notes\n\nMore.",
    ],
)
def test_the_body_of_a_task_with_copies_needs_its_two_sections(tree: Tree, body: str) -> None:
    add_copy_task(tree, {"frame": copy_step("use-a-verb")}, body=body)
    message = (
        "Give the body of the skill exactly these sections in this order: "
        "## Exit checklist, ## Output."
    )
    line = tree.lines("task", "## ")[0]
    assert tree.problems() == [f"{line}: step: {message}"]


def test_an_empty_body_section_fails_at_its_heading(tree: Tree) -> None:
    add_copy_task(
        tree, {"frame": copy_step("use-a-verb")}, body="## Exit checklist\n\n## Output\n\nA."
    )
    expected = tree.expect(
        "task", "## Exit checklist", "step", "Write the text of ## Exit checklist."
    )
    assert tree.problems() == [expected]


def test_a_skill_with_both_step_forms_fails(tree: Tree) -> None:
    add_copy_task(tree, {"frame": copy_step("use-a-verb"), "visual": STEP_TEXT})
    message = "Write each step file of the skill in the same form: each with front matter, or none."
    assert tree.problems() == [tree.expect("task", "steps:", "step", message)]


def test_a_directive_in_two_root_sections_fails(tree: Tree) -> None:
    tree.change("root", use_a_skill=["use-a-verb"], create_a_rule=["be-brief", "use-a-verb"])
    message = "use-a-verb is in a root section already. Name it in 1 section only."
    assert tree.problems() == [tree.expect("root", "  - use-a-verb", "skill", message)]


def test_a_root_section_names_a_directive_once(tree: Tree) -> None:
    tree.change("root", use_a_skill=["use-a-verb", "use-a-verb"])
    message = "use-a-verb is in a root section already. Name it in 1 section only."
    assert tree.problems() == [tree.expect("root", "  - use-a-verb", "skill", message)]


def test_a_root_section_names_only_a_directive(tree: Tree) -> None:
    tree.change("root", create_a_rule=["design"])
    assert tree.codes() == ["type"]
