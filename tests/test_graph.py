# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportMissingTypeStubs=false, reportOptionalMemberAccess=false
import copy
from pathlib import Path
from typing import Any

import pytest
from linkml_runtime.utils.schemaview import SchemaView
from rdflib import RDF, SH, BNode, Graph, Literal, URIRef

from engine.graph import check_graph, check_tree
from engine.graph.references import EDGE_FIELDS, references_of
from engine.graph.shapes import KA, NODE_NAMESPACE, check_shapes, report_problems
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
    return {"kind": "ka:TextPointer", "target": target, "trigger": "You need it."}


def skill_pointer(target: str) -> Fields:
    return {"kind": "ka:SkillPointer", "target": target, "trigger": "You need it."}


def directive(directive_id: str, **fields: object) -> Fields:
    return {"id": directive_id, "scope": "subtree", "basis": "judgment", **GOVERNED, **fields}


SAMPLE: dict[str, Fields] = {
    "root": {
        "file": "knowledge/node.md",
        "kind": "ka:Root",
        **GOVERNED,
        "pointers": [text_pointer("design"), skill_pointer("review")],
    },
    "design": {
        "file": "knowledge/nodes/design/node.md",
        "kind": "ka:Domain",
        **KNOWLEDGE,
        "pointers": [text_pointer("ui"), text_pointer("research")],
        "governs": ["root", "design"],
        "directives": [directive("use-a-verb"), directive("be-brief")],
    },
    "ui": {
        "file": "knowledge/nodes/design/ui/node.md",
        "kind": "ka:Discipline",
        **KNOWLEDGE,
        "broader": ["design"],
        "pointers": [text_pointer("visual"), text_pointer("motion")],
        "related": ["research"],
        "informs": ["research"],
    },
    "research": {
        "file": "knowledge/nodes/design/research/node.md",
        "kind": "ka:Discipline",
        **KNOWLEDGE,
        "broader": ["design"],
        "pointers": [text_pointer("ui")],
        "related": ["ui"],
        "informs": ["ui"],
    },
    "visual": {
        "file": "knowledge/nodes/design/ui/visual/node.md",
        "kind": "ka:PracticeArea",
        **KNOWLEDGE,
        "broader": ["ui", "design"],
        "pointers": [text_pointer("hierarchy")],
    },
    "motion": {
        "file": "knowledge/nodes/design/ui/motion/node.md",
        "kind": "ka:Concept",
        **KNOWLEDGE,
        "broader": ["ui"],
        "depends_on": ["hierarchy"],
    },
    "hierarchy": {
        "file": "knowledge/nodes/design/ui/visual/hierarchy/node.md",
        "kind": "ka:Concept",
        **KNOWLEDGE,
        "broader": ["visual"],
        "related": ["motion"],
        "directives": [directive("show-order", also_attached_to=["motion", "root"])],
    },
    "settings": {
        "file": "knowledge/nodes/settings/node.md",
        "kind": "ka:Concept",
        **GOVERNED,
        "knowledge_type": "workspace",
        "broader": ["hierarchy"],
        "implements": ["hierarchy"],
    },
    "review": {
        "file": "knowledge/skills/review/node.md",
        "kind": "ka:Skill",
        **KNOWLEDGE,
        "description": "Use this skill for a review.",
        "invocation": "agent",
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
    del front["file"]
    lines = ["---"]
    for key, value in front.items():
        lines += block(key, value) if isinstance(value, list) else [f"{key}: {value}"]
    lines += ["---", ""]
    if fields["kind"] not in {"ka:Root", "ka:Skill"}:
        lines += ["## Definition", "", f"The meaning of {node_id}.", ""]
    if directives:
        lines += ["## Directives", ""]
        for entry in directives:
            lines += directive_lines(entry)
        lines.append("")
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
        "kind": "ka:Root",
        **GOVERNED,
        "pointers": [text_pointer(target)],
    }


def test_a_second_root_fails_the_folder_check(tree: Tree) -> None:
    second_root(tree, "design")
    assert tree.problems() == [tree.expect("extra", "kind: ka:Root", "placement", ROOT_MOVE)]


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
    assert tree.problems() == [tree.expect("root", "kind: ka:Root", "placement", ROOT_MOVE)]


def test_the_root_cannot_be_under_skills(tree: Tree) -> None:
    tree.change("root", file="knowledge/skills/root/node.md")
    assert tree.problems() == [tree.expect("root", "kind: ka:Root", "placement", ROOT_MOVE)]


def test_only_the_root_can_use_the_root_file(tree: Tree) -> None:
    tree.change("root", file="knowledge/nodes/top/node.md")
    tree.change("design", file="knowledge/node.md")
    only_root = "Only the root node can use this file. Set kind to ka:Root or move this node."
    assert tree.problems() == [
        tree.expect("design", "kind: ka:Domain", "placement", only_root),
        tree.expect("root", "kind: ka:Root", "placement", ROOT_MOVE),
    ]


def test_a_skill_must_be_under_skills(tree: Tree) -> None:
    tree.change("review", file="knowledge/nodes/review/node.md")
    assert tree.problems() == [tree.expect("review", "kind: ka:Skill", "placement", SKILL_MOVE)]


def test_a_knowledge_node_cannot_be_under_skills(tree: Tree) -> None:
    tree.change("motion", file="knowledge/skills/motion/node.md")
    assert tree.problems() == [
        tree.expect(
            "motion", "kind: ka:Concept", "placement", "Move this node out of knowledge/skills."
        )
    ]


@pytest.mark.parametrize(
    "file",
    ["knowledge/motion/node.md", "knowledge/.ka/motion/node.md", "knowledge/x/nodes/node.md"],
)
def test_a_knowledge_node_must_be_under_nodes(tree: Tree, file: str) -> None:
    tree.change("motion", file=file)
    assert tree.problems() == [
        tree.expect("motion", "kind: ka:Concept", "placement", "Move this node to knowledge/nodes.")
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
            "kind: ka:Concept",
            "placement",
            "Move this node to knowledge/governance/policies.",
        )
    ]


def test_a_node_beside_the_policy_folder_fails(tree: Tree) -> None:
    tree.change("motion", file="knowledge/governance/node.md")
    assert tree.codes() == ["placement"]


def test_a_skill_cannot_be_a_policy(tree: Tree) -> None:
    tree.change("review", file="knowledge/governance/policies/review/node.md")
    assert tree.problems() == [tree.expect("review", "kind: ka:Skill", "placement", SKILL_MOVE)]


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
    ["foo:bar", "ka:Concept", "a b", "<x>", "Motion", "motion ", "http://example.com/x"],
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
        ("ui", "broader", "settings", "ka:Concept"),
        ("research", "broader", "visual", "ka:PracticeArea"),
        ("visual", "broader", "settings", "ka:Concept"),
        ("visual", "broader", "root", "ka:Root"),
        ("motion", "broader", "review", "ka:Skill"),
        ("motion", "broader", "use-a-verb", "ka:Directive"),
        ("motion", "related", "review", "ka:Skill"),
        ("motion", "informs", "root", "ka:Root"),
        ("motion", "depends_on", "use-a-verb", "ka:Directive"),
        ("motion", "governs", "use-a-verb", "ka:Directive"),
        ("review", "uses", "review", "ka:Skill"),
        ("review", "applies", "hierarchy", "ka:Concept"),
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
    message = "implements cannot name review, which has kind ka:Skill."
    assert tree.problems() == [tree.expect("settings", "  - review", "type", message)]


def test_a_type_problem_names_the_right_list_item(tree: Tree) -> None:
    tree.change("visual", broader=["ui", "motion", "design"])
    tree.remove("hierarchy", "related")
    message = "broader cannot name motion, which has kind ka:Concept."
    assert tree.problems() == [tree.expect("visual", "  - motion", "type", message)]


def test_a_skill_pointer_must_target_a_skill(tree: Tree) -> None:
    tree.change(
        "visual",
        pointers=[text_pointer("hierarchy"), skill_pointer("hierarchy"), skill_pointer("review")],
    )
    second = tree.lines("visual", "target: hierarchy")[1]
    assert tree.problems() == [
        f"{second}: type: target cannot name hierarchy, which has kind ka:Concept."
    ]


def test_a_skill_pointer_can_target_a_skill(tree: Tree) -> None:
    tree.change("visual", pointers=[text_pointer("hierarchy"), skill_pointer("review")])
    assert tree.problems() == []


def test_a_text_pointer_cannot_target_a_directive(tree: Tree) -> None:
    tree.change("visual", pointers=[text_pointer("hierarchy"), text_pointer("use-a-verb")])
    message = "target cannot name use-a-verb, which has kind ka:Directive."
    assert tree.problems() == [tree.expect("visual", "target: use-a-verb", "type", message)]


def test_a_directive_cannot_attach_to_a_directive(tree: Tree) -> None:
    tree.change(
        "hierarchy",
        directives=[directive("show-order", also_attached_to=["motion", "use-a-verb"])],
    )
    message = "also_attached_to cannot name use-a-verb, which has kind ka:Directive."
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
            "kind": "ka:Domain",
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
    message = "related cannot name review, which has kind ka:Skill."
    first = tree.lines("motion", "  - review")[0]
    assert tree.problems() == [f"{first}: type: {message}"]


@pytest.mark.parametrize("field", ["title", "description"])
@pytest.mark.parametrize(
    "value",
    ['"ka:Concept"', '"<x> \\"q\\" é"', '"[a](b)"', '"http://x y"', '"{a}"', '"a @en"'],
)
def test_a_hostile_text_value_does_not_crash(tree: Tree, field: str, value: str) -> None:
    tree.nodes["review"][field] = value
    assert tree.problems() == []


def test_a_hostile_source_does_not_crash(tree: Tree) -> None:
    tree.change("review", sources=['"foo:bar baz"', '"<not an iri>"'])
    assert tree.problems() == []


def test_a_hostile_trigger_and_path_do_not_crash(tree: Tree) -> None:
    pointer = {
        "kind": "ka:PathPointer",
        "target": "settings",
        "trigger": '"foo:bar <x>"',
        "paths": '["ka:y <z>"]',
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
        (BNode(), KA.target, MOTION),
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
    data.add((URIRef(f"{NODE_NAMESPACE}root"), KA.pointers, focus))
    data.add((focus, RDF.type, KA.PathPointer))
    report = report_with(focus, KA.target, URIRef(f"{NODE_NAMESPACE}design"))
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
        "kind": "ka:Concept",
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
