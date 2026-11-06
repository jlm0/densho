# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportMissingTypeStubs=false
import hashlib
import json
import os
import random
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pyshacl
import pytest
from rdflib import BNode, Graph, Literal, Namespace
from rdflib.compare import isomorphic
from typer.testing import CliRunner

from engine.cli import app
from engine.compiler import (
    OUTPUT_FOLDER,
    CompiledGraph,
    build_tree,
    compile_items,
    compile_tree,
    file_names,
    render_output,
)
from engine.directives import resolve_directives
from engine.generated.metamodel import (
    CompiledResult,
    KnowledgeGraph,
    Status,
    TextPointer,
)
from engine.graph.rules import check_references
from engine.graph.shapes import GENERATED, rdf_graph
from engine.parser import ParsedNode, Problem, parse_source

if TYPE_CHECKING:
    from collections.abc import Iterable

REPO = Path(__file__).resolve().parents[1]
RUNNER = CliRunner()
GIT = shutil.which("git") or "git"
KA = Namespace("https://github.com/jlm0/knowledge-architecture/schema/")
IN_FORCE = CompiledResult.in_force
PROPOSALS = CompiledResult.proposals
TREE_FOLDERS = ("knowledge",)
EVERY_OUTPUT_FILE = {
    "graph.json",
    "graph.ttl",
    "digests.json",
    "graph.proposals.json",
    "graph.proposals.ttl",
    "digests.proposals.json",
}
REASON = "This node is a throwaway prototype."
BUILD_ONE_TREE = """
import sys
from pathlib import Path
from engine.compiler import build_tree
for proposals in (False, True):
    report = build_tree(Path(sys.argv[1]), proposals=proposals)
    assert not report.problems, report.problems
"""


def rule(directive_id: str, status: str = "accepted", scope: str = "subtree", **refs: str) -> str:
    lines = [f"- Run the {directive_id} check. ^{directive_id}", f"  - scope: {scope}"]
    lines += [f"  - status: {status}", "  - origin: template"]
    lines += [f"  - {field}: {target}" for field, target in refs.items()]
    return "\n".join(lines) + "\n"


def node(
    node_id: str,
    kind: str = "ka:Domain",
    *,
    status: str = "accepted",
    front: str = "",
    rules: Iterable[str] = (),
) -> str:
    extra = "knowledge_type: domain\n" if kind != "ka:Root" else ""
    head = f"---\nid: {node_id}\nkind: {kind}\ntitle: {node_id}\nstatus: {status}\n"
    text = f"{head}origin: template\n{extra}{front}---\n"
    if kind not in {"ka:Root", "ka:Skill"}:
        text += "\n## Definition\n\nA meaning.\n"
    joined = "".join(rules)
    return f"{text}\n## Directives\n\n{joined}" if joined else text


def pointers(*targets: str) -> str:
    lines = ["pointers:"]
    for target in targets:
        lines += ["  - kind: ka:TextPointer", f"    target: {target}"]
        lines.append(f"    trigger: You need {target}.")
    return "\n".join(lines) + "\n"


def exception(directive: str, status: str) -> str:
    return f"  - directive: {directive}\n    reason: {REASON}\n    status: {status}\n"


SAMPLE = {
    "knowledge/node.md": node(
        "root",
        "ka:Root",
        front=pointers("alpha", "beta", "delta", "gamma", "retired", "review"),
    ),
    "knowledge/nodes/alpha/node.md": node(
        "alpha",
        rules=[
            rule("keep"),
            rule("wait", "proposed"),
            rule("faded", "deprecated", "node"),
        ],
    ),
    "knowledge/nodes/alpha/beta/node.md": node(
        "beta",
        "ka:Concept",
        status="proposed",
        front=(
            "broader: [alpha]\nexceptions:\n"
            f"{exception('keep', 'proposed')}{exception('wait', 'accepted')}"
        ),
        rules=[rule("bound", scope="node", conflicts_with="spare")],
    ),
    "knowledge/nodes/delta/node.md": node("delta", rules=[rule("spare", "proposed", "node")]),
    "knowledge/nodes/gamma/node.md": node("gamma", rules=[rule("solid", scope="node")]),
    "knowledge/nodes/retired/node.md": node(
        "retired", "ka:Concept", status="deprecated", front="broader: [gamma]\n"
    ),
    "knowledge/skills/review/node.md": node(
        "review",
        "ka:Skill",
        status="proposed",
        front=(
            "description: Review a sample. Use when a sample needs a review.\n"
            "uses: [gamma]\napplies: [solid, spare]\n"
        ),
    ),
}


def parsed(sources: dict[str, str] | None = None) -> list[ParsedNode]:
    items: list[ParsedNode] = []
    for relative, text in (SAMPLE if sources is None else sources).items():
        result = parse_source(text, Path(relative))
        assert isinstance(result, ParsedNode), result
        items.append(result)
    return items


def compiled_sample(*, proposals: bool = False) -> CompiledGraph:
    return compile_items(parsed(), Path(), proposals=proposals)


def write_tree(repository: Path, sources: dict[str, str] | None = None) -> None:
    def no_branch_files(folder: str, names: list[str]) -> list[str]:
        return [name for name in names if Path(folder).name == "branches" and name != ".gitkeep"]

    shutil.copytree(
        REPO / "knowledge/governance/language",
        repository / "knowledge/governance/language",
        ignore=no_branch_files,
    )
    (repository / "knowledge").mkdir(parents=True, exist_ok=True)
    for relative, text in (SAMPLE if sources is None else sources).items():
        path = repository / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


def output_bytes(repository: Path) -> dict[str, bytes]:
    folder = repository / OUTPUT_FOLDER
    return {path.name: path.read_bytes() for path in sorted(folder.iterdir())}


def graph_document(compiled: CompiledGraph) -> dict[str, Any]:
    name = file_names(compiled.result)[0]
    return json.loads(render_output(compiled).files[name])


def turtle_of(compiled: CompiledGraph) -> bytes:
    return render_output(compiled).files[file_names(compiled.result)[1]]


def directive_ids(document: dict[str, Any]) -> set[str]:
    nodes = [document["graph"]["root"], *document["graph"]["nodes"]]
    return {entry["id"] for item in nodes for entry in item.get("directives", [])}


def node_in(document: dict[str, Any], node_id: str) -> dict[str, Any]:
    nodes = [document["graph"]["root"], *document["graph"]["nodes"]]
    return next(item for item in nodes if item["id"] == node_id)


def test_the_default_result_holds_only_directives_in_force() -> None:
    document = graph_document(compiled_sample())
    assert document["result"] == "in_force"
    assert document["graph"]["result"] == "in_force"
    assert directive_ids(document) == {"keep", "bound", "solid"}


def test_the_default_result_keeps_no_trace_of_a_left_out_directive() -> None:
    compiled = compiled_sample()
    output = render_output(compiled)
    for data in output.files.values():
        for directive_id in (b"wait", b"spare", b"faded"):
            assert directive_id not in data


def test_the_marked_result_adds_proposals_and_leaves_out_deprecated_directives() -> None:
    document = graph_document(compiled_sample(proposals=True))
    assert document["result"] == "proposals"
    assert document["graph"]["result"] == "proposals"
    assert directive_ids(document) == {"keep", "wait", "bound", "spare", "solid"}


@pytest.mark.parametrize("proposals", [False, True])
def test_each_entity_keeps_its_status(proposals: bool) -> None:  # noqa: FBT001
    document = graph_document(compiled_sample(proposals=proposals))
    assert node_in(document, "beta")["status"] == "proposed"
    assert node_in(document, "retired")["status"] == "deprecated"
    assert node_in(document, "alpha")["status"] == "accepted"
    assert node_in(document, "alpha")["directives"][0]["status"] == "accepted"
    if proposals:
        alpha = node_in(document, "alpha")["directives"]
        assert {entry["id"]: entry["status"] for entry in alpha} == {
            "keep": "accepted",
            "wait": "proposed",
        }
        beta = node_in(document, "beta")["exceptions"]
        assert {entry["directive"]: entry["status"] for entry in beta} == {
            "keep": "proposed",
            "wait": "accepted",
        }


def test_the_status_of_a_node_does_not_remove_it_from_either_result() -> None:
    for proposals in (False, True):
        document = graph_document(compiled_sample(proposals=proposals))
        ids = {item["id"] for item in document["graph"]["nodes"]}
        assert ids == {"alpha", "beta", "delta", "gamma", "retired", "review"}
        assert document["graph"]["root"]["id"] == "root"


def test_the_count_of_left_out_entities_matches_the_source() -> None:
    assert graph_document(compiled_sample())["left_out"] == {"directives": 3, "exceptions": 2}
    marked = graph_document(compiled_sample(proposals=True))
    assert marked["left_out"] == {"directives": 1, "exceptions": 0}


def test_each_result_filters_exceptions_by_status_and_by_directive() -> None:
    assert "exceptions" not in node_in(graph_document(compiled_sample()), "beta")
    marked = node_in(graph_document(compiled_sample(proposals=True)), "beta")
    assert {entry["directive"] for entry in marked["exceptions"]} == {"keep", "wait"}


def test_an_accepted_exception_for_an_accepted_directive_stays_in_force() -> None:
    sources = {
        **SAMPLE,
        "knowledge/nodes/alpha/beta/node.md": node(
            "beta",
            "ka:Concept",
            front=f"broader: [alpha]\nexceptions:\n{exception('keep', 'accepted')}",
        ),
    }
    document = graph_document(compile_items(parsed(sources), Path()))
    assert node_in(document, "beta")["exceptions"][0]["directive"] == "keep"
    assert document["left_out"]["exceptions"] == 0
    assert document["applied"]["beta"] == []


def test_a_deprecated_exception_stays_out_of_both_results() -> None:
    sources = {
        **SAMPLE,
        "knowledge/nodes/alpha/beta/node.md": node(
            "beta",
            "ka:Concept",
            front=f"broader: [alpha]\nexceptions:\n{exception('keep', 'deprecated')}",
        ),
    }
    for proposals in (False, True):
        document = graph_document(compile_items(parsed(sources), Path(), proposals=proposals))
        assert "exceptions" not in node_in(document, "beta")
        assert document["left_out"]["exceptions"] == 1


@pytest.mark.parametrize("proposals", [False, True])
def test_each_reference_in_the_output_resolves(proposals: bool) -> None:  # noqa: FBT001
    compiled = compile_items(parsed(), Path(), proposals=proposals)
    items = [
        ParsedNode(Path("output"), entry, {})
        for entry in (compiled.graph.root, *compiled.graph.nodes)
    ]
    assert check_references(items) == []


def test_a_reference_to_a_left_out_directive_goes_with_it() -> None:
    document = graph_document(compiled_sample())
    assert "conflicts_with" not in node_in(document, "beta")["directives"][0]
    assert node_in(document, "review")["applies"] == ["solid"]
    marked = graph_document(compiled_sample(proposals=True))
    assert node_in(marked, "beta")["directives"][0]["conflicts_with"] == ["spare"]
    assert node_in(marked, "review")["applies"] == ["solid", "spare"]


def test_a_refines_edge_to_a_left_out_directive_goes_with_it() -> None:
    sources = {
        **SAMPLE,
        "knowledge/nodes/delta/node.md": node(
            "delta",
            rules=[
                rule("spare", "proposed", "node"),
                rule("narrow", scope="node", refines="spare"),
                rule("wide", scope="node"),
                rule("narrower", scope="node", refines="wide"),
            ],
        ),
    }
    document = graph_document(compile_items(parsed(sources), Path()))
    by_id = {entry["id"]: entry for entry in node_in(document, "delta")["directives"]}
    assert "refines" not in by_id["narrow"]
    assert by_id["narrower"]["refines"] == ["wide"]


@pytest.mark.parametrize("proposals", [False, True])
def test_the_applied_list_comes_from_the_same_state(proposals: bool) -> None:  # noqa: FBT001
    items = parsed()
    compiled = compile_items(items, Path(), proposals=proposals)
    resolution = resolve_directives(items, proposals=proposals)
    for node_id in {item.node.id for item in items}:
        expected = [
            (entry.directive.id, entry.holder, entry.route) for entry in resolution.at(node_id)
        ]
        actual = [
            (entry.directive.id, entry.holder, entry.route) for entry in compiled.applied[node_id]
        ]
        assert actual == expected
    assert set(compiled.applied) == {item.node.id for item in items}


def test_a_proposed_exception_changes_only_the_marked_result() -> None:
    assert [entry.directive.id for entry in compiled_sample().applied["beta"]] == ["keep", "bound"]
    marked = compiled_sample(proposals=True).applied["beta"]
    assert [entry.directive.id for entry in marked] == ["bound"]


def test_the_json_applied_list_names_each_directive_status_holder_and_route() -> None:
    entry = {
        "directive": "wait",
        "holder": "alpha",
        "route": ["alpha", "beta", "child"],
        "status": "proposed",
    }
    sources = {
        **SAMPLE,
        "knowledge/nodes/alpha/beta/node.md": node(
            "beta", "ka:Concept", front="broader: [alpha]\n"
        ),
        "knowledge/nodes/alpha/beta/child/node.md": node(
            "child", "ka:Concept", front="broader: [beta]\n"
        ),
    }
    document = graph_document(compile_items(parsed(sources), Path(), proposals=True))
    assert entry in document["applied"]["child"]


def test_an_applied_directive_is_the_filtered_directive() -> None:
    entry = compiled_sample().applied["beta"][1]
    assert entry.directive.id == "bound"
    assert entry.directive.conflicts_with is None


def test_the_paths_are_relative_to_the_repository(tmp_path: Path) -> None:
    write_tree(tmp_path)
    report = compile_tree(tmp_path)
    assert report.compiled is not None
    assert report.compiled.paths["beta"] == "knowledge/nodes/alpha/beta/node.md"
    assert report.compiled.paths["root"] == "knowledge/node.md"


def test_compile_tree_returns_the_compiled_graph_and_writes_nothing(tmp_path: Path) -> None:
    write_tree(tmp_path)
    report = compile_tree(tmp_path)
    assert report.problems == []
    assert report.compiled is not None
    assert isinstance(report.compiled.graph, KnowledgeGraph)
    assert report.compiled.result == IN_FORCE
    assert set(report.compiled.directives) == {"keep", "bound", "solid"}
    assert not (tmp_path / "build").exists()
    marked = compile_tree(tmp_path, proposals=True)
    assert marked.compiled is not None
    assert marked.compiled.result == PROPOSALS
    assert "wait" in marked.compiled.directives


def test_the_json_graph_loads_into_the_models_with_the_right_classes() -> None:
    document = graph_document(compiled_sample())
    graph = KnowledgeGraph.model_validate(document["graph"])
    kinds = {entry.id: type(entry).__name__ for entry in graph.nodes}
    assert kinds["alpha"] == "Domain"
    assert kinds["beta"] == "Concept"
    assert kinds["review"] == "Skill"
    assert isinstance(graph.root.pointers[0], TextPointer)


def test_the_model_rejects_an_unknown_result() -> None:
    document = graph_document(compiled_sample())
    document["graph"]["result"] = "maybe"
    with pytest.raises(ValueError, match="result"):
        KnowledgeGraph.model_validate(document["graph"])


@pytest.mark.parametrize("proposals", [False, True])
def test_the_json_graph_and_the_turtle_file_hold_the_same_triples(
    proposals: bool,  # noqa: FBT001
) -> None:
    compiled = compile_items(parsed(), Path(), proposals=proposals)
    document = graph_document(compiled)
    from_json = rdf_graph(KnowledgeGraph.model_validate(document["graph"]))
    from_turtle = Graph().parse(data=turtle_of(compiled), format="turtle")
    assert isomorphic(from_json, from_turtle)


@pytest.mark.parametrize("proposals", [False, True])
def test_the_output_passes_the_generated_shapes(proposals: bool) -> None:  # noqa: FBT001
    compiled = compile_items(parsed(), Path(), proposals=proposals)
    shapes = Graph().parse(GENERATED / "metamodel.shacl.ttl", format="turtle")
    ontology = Graph().parse(GENERATED / "metamodel.owl.ttl", format="turtle")
    data = Graph().parse(data=turtle_of(compiled), format="turtle")
    conforms, _, text = pyshacl.validate(
        data, shacl_graph=shapes, ont_graph=ontology, inference="none"
    )
    assert conforms, text
    subject = next(data.subjects(KA.result, None))
    data.set((subject, KA.result, Literal("maybe")))
    conforms, _, _ = pyshacl.validate(
        data, shacl_graph=shapes, ont_graph=ontology, inference="none"
    )
    assert not conforms


def test_the_marks_of_the_marked_result() -> None:
    output = render_output(compiled_sample(proposals=True))
    assert list(output.files) == [
        "graph.proposals.json",
        "graph.proposals.ttl",
        "digests.proposals.json",
    ]
    text = output.files["graph.proposals.json"].decode()
    assert text.startswith('{\n  "result": "proposals",\n  "notice": "NOT IN FORCE. ')
    turtle = output.files["graph.proposals.ttl"].decode()
    assert turtle.startswith("# proposals: NOT IN FORCE. ")
    assert 'ka:result "proposals"' in turtle
    manifest = json.loads(output.files["digests.proposals.json"])
    assert manifest["result"] == "proposals"


def test_the_marks_of_the_default_result() -> None:
    output = render_output(compiled_sample())
    assert list(output.files) == ["graph.json", "graph.ttl", "digests.json"]
    text = output.files["graph.json"].decode()
    assert text.startswith('{\n  "result": "in_force",\n  "notice": "This result holds only ')
    assert "NOT IN FORCE" not in text
    turtle = output.files["graph.ttl"].decode()
    assert turtle.startswith("# in_force: This result holds only ")
    assert 'ka:result "in_force"' in turtle
    assert json.loads(output.files["digests.json"])["result"] == "in_force"


def test_a_tree_with_no_proposal_still_gives_two_digests() -> None:
    sources = {
        "knowledge/node.md": node("root", "ka:Root", front=pointers("alpha")),
        "knowledge/nodes/alpha/node.md": node("alpha", rules=[rule("keep")]),
    }
    default = render_output(compile_items(parsed(sources), Path()))
    marked = render_output(compile_items(parsed(sources), Path(), proposals=True))
    assert default.digest != marked.digest


def test_the_digests_cover_the_file_bytes() -> None:
    output = render_output(compiled_sample())
    hashes = {
        name: hashlib.sha256(output.files[name]).hexdigest() for name in ("graph.json", "graph.ttl")
    }
    assert output.digests == {name: f"sha256:{value}" for name, value in hashes.items()}
    listing = f"{hashes['graph.json']}  graph.json\n{hashes['graph.ttl']}  graph.ttl\n"
    digest = f"sha256:{hashlib.sha256(listing.encode()).hexdigest()}"
    assert output.digest == digest
    manifest = json.loads(output.files["digests.json"])
    assert manifest == {"result": "in_force", "digest": digest, "files": output.digests}


def test_a_changed_text_changes_each_digest() -> None:
    first = render_output(compiled_sample())
    sources = {
        **SAMPLE,
        "knowledge/nodes/gamma/node.md": node(
            "gamma", rules=[rule("solid", scope="node").replace("Run the", "Check the")]
        ),
    }
    second = render_output(compile_items(parsed(sources), Path()))
    assert first.digest != second.digest
    assert first.digests["graph.json"] != second.digests["graph.json"]
    assert first.digests["graph.ttl"] != second.digests["graph.ttl"]


def test_the_order_of_the_items_does_not_change_the_bytes() -> None:
    items = parsed()
    expected = render_output(compile_items(items, Path(), proposals=True))
    generator = random.Random(5)  # noqa: S311
    for _ in range(10):
        generator.shuffle(items)
        actual = render_output(compile_items(items, Path(), proposals=True))
        assert actual.files == expected.files


def listed_tree(*order: int) -> dict[str, str]:
    pointer_targets = [
        f"  - kind: ka:TextPointer\n    target: {name}\n    trigger: You need {name}.\n"
        for name in ("alpha", "gamma")
    ]
    links = [pointer_targets[index] for index in order]
    edges = [("alpha", "gamma")[index] for index in order]
    sources_list = [("https://example.com/a", "https://example.com/b")[index] for index in order]
    file_patterns = [('"alpha/**"', '"gamma/**"')[index] for index in order]
    path_pointer = (
        "  - kind: ka:PathPointer\n    target: gamma\n    trigger: You change a file.\n"
        f"    paths: [{', '.join(file_patterns)}]\n"
    )
    rules = [rule("first", scope="node"), rule("second", scope="node")]
    return {
        "knowledge/node.md": node(
            "root", "ka:Root", front=f"pointers:\n{''.join(links)}{path_pointer}"
        ),
        "knowledge/nodes/alpha/node.md": node(
            "alpha", rules=[rules[index] for index in dict.fromkeys(order)]
        ),
        "knowledge/nodes/gamma/node.md": node("gamma"),
        "knowledge/nodes/beta/node.md": node(
            "beta",
            "ka:Concept",
            front=f"broader: [{', '.join(edges)}]\nsources: [{', '.join(sources_list)}]\n",
        ),
    }


def test_the_order_of_a_list_and_a_repeated_value_do_not_change_the_bytes() -> None:
    forward = render_output(compile_items(parsed(listed_tree(0, 1)), Path()))
    backward = render_output(compile_items(parsed(listed_tree(1, 0)), Path()))
    repeated = render_output(compile_items(parsed(listed_tree(0, 1, 0)), Path()))
    assert forward.files == backward.files
    assert forward.files == repeated.files


def test_the_directives_of_a_node_sort_by_id() -> None:
    sources = {
        **SAMPLE,
        "knowledge/nodes/delta/node.md": node(
            "delta",
            rules=[
                rule("zeta", scope="node", also_attached_to="gamma"),
                rule("alpha-rule", scope="node"),
            ],
        ),
    }
    document = graph_document(compile_items(parsed(sources), Path()))
    ids = [entry["id"] for entry in node_in(document, "delta")["directives"]]
    assert ids == ["alpha-rule", "zeta"]


def test_each_prefix_in_the_turtle_file_has_its_name() -> None:
    sources = {
        **SAMPLE,
        "knowledge/nodes/gamma/node.md": node(
            "gamma", front="sources:\n  - https://example.com/a\n"
        ),
    }
    turtle = turtle_of(compile_items(parsed(sources), Path())).decode()
    for line in (
        "@prefix dcterms: <http://purl.org/dc/terms/> .",
        "@prefix ka: <https://github.com/jlm0/knowledge-architecture/schema/> .",
        "@prefix node: <https://github.com/jlm0/knowledge-architecture/node/> .",
        "@prefix skos: <http://www.w3.org/2004/02/skos/core#> .",
    ):
        assert line in turtle
    assert turtle.count("@prefix") == 4  # noqa: PLR2004
    assert 'dcterms:source "https://example.com/a"' in turtle


def test_a_route_keeps_its_order() -> None:
    document = graph_document(compiled_sample())
    routes = {entry["directive"]: entry["route"] for entry in document["applied"]["beta"]}
    assert routes["keep"] == ["alpha", "beta"]
    sources = {
        **SAMPLE,
        "knowledge/nodes/zed/node.md": node("zed", rules=[rule("zed-rule")]),
        "knowledge/nodes/zed/ann/node.md": node("ann", "ka:Concept", front="broader: [zed]\n"),
    }
    document = graph_document(compile_items(parsed(sources), Path()))
    routes = {entry["directive"]: entry["route"] for entry in document["applied"]["ann"]}
    assert routes["zed-rule"] == ["zed", "ann"]


def test_the_applied_list_starts_with_the_longest_route() -> None:
    document = graph_document(compiled_sample())
    assert [entry["directive"] for entry in document["applied"]["beta"]] == ["keep", "bound"]


def test_each_turtle_run_labels_blank_nodes_the_same_way() -> None:
    compiled = compiled_sample(proposals=True)
    raw_first = {term for term in rdf_graph(compiled.graph).subjects() if isinstance(term, BNode)}
    raw_second = {term for term in rdf_graph(compiled.graph).subjects() if isinstance(term, BNode)}
    assert raw_first
    assert raw_first != raw_second
    first = turtle_of(compiled)
    assert first == turtle_of(compiled)
    assert b"_:" not in first


def test_identical_pointers_collapse_and_stay_cheap() -> None:
    copies = "".join(
        "  - kind: ka:TextPointer\n    target: alpha\n    trigger: You need it.\n"
        for _ in range(200)
    )
    sources = {
        "knowledge/node.md": node("root", "ka:Root", front=f"pointers:\n{copies}"),
        "knowledge/nodes/alpha/node.md": node("alpha"),
    }
    compiled = compile_items(parsed(sources), Path())
    output = render_output(compiled)
    assert len(compiled.graph.root.pointers) == 1
    assert output.files["graph.ttl"].count(b"ka:TextPointer") == 1


NASTY_TEXT = 'A "quoted" word, a \\ backslash, a """ run, and the end \\'
NASTY_SOURCES = {
    "knowledge/node.md": node("root", "ka:Root", front=pointers("alpha")),
    "knowledge/nodes/alpha/node.md": (
        "---\nid: alpha\nkind: ka:Domain\ntitle: 'Alpha — ✓ 🙂 ''quoted'''\nstatus: accepted\n"
        "origin: template\nknowledge_type: domain\n"
        "sources:\n  - 'https://example.com/a?b=\"c\"'\n---\n\n"
        f"## Definition\n\n{NASTY_TEXT}\n\nSécond paragraph\twith a tab.\n\n"
        "## Notes\n\n```text\n<tag> & {{ value }}\n```\n"
    ),
}


def test_hostile_text_stays_exact_through_json_and_turtle() -> None:
    compiled = compile_items(parsed(NASTY_SOURCES), Path())
    document = graph_document(compiled)
    alpha = document["graph"]["nodes"][0]
    assert NASTY_TEXT in alpha["definition"]
    assert "🙂" in alpha["title"]
    assert "🙂".encode() in render_output(compiled).files["graph.json"]
    from_json = rdf_graph(KnowledgeGraph.model_validate(document["graph"]))
    from_turtle = Graph().parse(data=turtle_of(compiled), format="turtle")
    assert isomorphic(from_json, from_turtle)


EXACT_JSON = """\
{
  "result": "in_force",
  "notice": "This result holds only the accepted directives and exceptions. It leaves out each proposal.",
  "format_version": 1,
  "left_out": {
    "directives": 1,
    "exceptions": 0
  },
  "paths": {
    "alpha": "knowledge/nodes/alpha/node.md",
    "beta": "knowledge/nodes/beta/node.md",
    "root": "knowledge/node.md"
  },
  "applied": {
    "alpha": [
      {
        "directive": "keep",
        "holder": "alpha",
        "route": [
          "alpha"
        ],
        "status": "accepted"
      }
    ],
    "beta": [],
    "root": []
  },
  "graph": {
    "nodes": [
      {
        "definition": "A meaning.",
        "directives": [
          {
            "id": "keep",
            "origin": "template",
            "scope": "node",
            "status": "accepted",
            "text": "Run the keep check."
          }
        ],
        "id": "alpha",
        "kind": "ka:Domain",
        "knowledge_type": "domain",
        "origin": "template",
        "status": "accepted",
        "title": "alpha"
      },
      {
        "definition": "A meaning.",
        "id": "beta",
        "kind": "ka:Domain",
        "knowledge_type": "domain",
        "origin": "template",
        "status": "accepted",
        "title": "beta"
      }
    ],
    "result": "in_force",
    "root": {
      "id": "root",
      "kind": "ka:Root",
      "origin": "template",
      "pointers": [
        {
          "kind": "ka:TextPointer",
          "target": "alpha",
          "trigger": "You need alpha."
        },
        {
          "kind": "ka:TextPointer",
          "target": "beta",
          "trigger": "You need beta."
        }
      ],
      "status": "accepted",
      "title": "root"
    }
  }
}
"""  # noqa: E501
EXACT_TURTLE = """\
# in_force: This result holds only the accepted directives and exceptions. It leaves out each proposal.

@prefix ka: <https://github.com/jlm0/knowledge-architecture/schema/> .
@prefix node: <https://github.com/jlm0/knowledge-architecture/node/> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .

node:keep a ka:Directive ;
    ka:origin "template" ;
    ka:scope "node" ;
    ka:status "accepted" ;
    ka:text "Run the keep check." .

node:root a ka:Root ;
    skos:prefLabel "root" ;
    ka:origin "template" ;
    ka:pointers [ a ka:TextPointer ;
            ka:target node:beta ;
            ka:trigger "You need beta." ],
        [ a ka:TextPointer ;
            ka:target node:alpha ;
            ka:trigger "You need alpha." ] ;
    ka:status "accepted" .

node:alpha a ka:Domain ;
    skos:definition "A meaning." ;
    skos:prefLabel "alpha" ;
    ka:directives node:keep ;
    ka:knowledge_type "domain" ;
    ka:origin "template" ;
    ka:status "accepted" .

node:beta a ka:Domain ;
    skos:definition "A meaning." ;
    skos:prefLabel "beta" ;
    ka:knowledge_type "domain" ;
    ka:origin "template" ;
    ka:status "accepted" .

[] a ka:KnowledgeGraph ;
    ka:nodes node:alpha,
        node:beta ;
    ka:result "in_force" ;
    ka:root node:root .

"""  # noqa: E501


@pytest.mark.parametrize(
    "value", ['"a\\x00b"', '"a\\x01b"', '"\\e[31m"', '"\\uFEFFx"', '"\\uFFFEx"', '"\\U0001F600"']
)
def test_an_escaped_value_survives_both_formats(value: str) -> None:
    sources = {
        "knowledge/node.md": node("root", "ka:Root", front=pointers("alpha")),
        "knowledge/nodes/alpha/node.md": node("alpha").replace("title: alpha", f"title: {value}"),
    }
    compiled = compile_items(parsed(sources), Path(), proposals=True)
    document = graph_document(compiled)
    from_json = rdf_graph(KnowledgeGraph.model_validate(document["graph"]))
    from_turtle = Graph().parse(data=turtle_of(compiled), format="turtle")
    assert isomorphic(from_json, from_turtle)
    assert document["graph"]["nodes"][0]["title"] == compiled.graph.nodes[0].title


def test_the_exact_bytes_of_a_small_tree() -> None:
    sources = {
        "knowledge/node.md": node("root", "ka:Root", front=pointers("alpha", "beta")),
        "knowledge/nodes/alpha/node.md": node(
            "alpha",
            rules=[rule("keep", scope="node"), rule("wait", "proposed", "node")],
        ),
        "knowledge/nodes/beta/node.md": node("beta"),
    }
    output = render_output(compile_items(parsed(sources), Path()))
    assert output.files["graph.json"].decode() == EXACT_JSON
    assert output.files["graph.ttl"].decode() == EXACT_TURTLE


def copy_real_tree(target: Path, *, reverse: bool = False) -> None:
    files = sorted(
        path
        for folder in TREE_FOLDERS
        for path in (REPO / folder).rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    )
    for path in reversed(files) if reverse else files:
        destination = target / path.relative_to(REPO)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, destination)


def build_in_a_new_process(repository: Path, seed: str) -> None:
    result = subprocess.run(  # noqa: S603
        [sys.executable, "-c", BUILD_ONE_TREE, str(repository)],
        capture_output=True,
        text=True,
        check=False,
        env={**os.environ, "PYTHONHASHSEED": seed},
    )
    assert result.returncode == 0, result.stderr


def test_the_real_tree_gives_the_same_bytes_across_seed_folder_and_file_order(
    tmp_path: Path,
) -> None:
    first = tmp_path / "first"
    second = tmp_path / "a deeper folder" / "second copy"
    third = tmp_path / "third"
    copy_real_tree(first)
    copy_real_tree(second, reverse=True)
    copy_real_tree(third)
    for path in (third / "knowledge").rglob("node.md"):
        os.utime(path, (1_000_000_000, 1_000_000_000))
    build_in_a_new_process(first, "0")
    build_in_a_new_process(second, "1")
    build_in_a_new_process(third, "424242")
    expected = output_bytes(first)
    assert set(expected) == EVERY_OUTPUT_FILE
    assert output_bytes(second) == expected
    assert output_bytes(third) == expected


def test_the_real_tree_compiles_and_the_result_matches_its_statuses(tmp_path: Path) -> None:
    copy_real_tree(tmp_path)
    default = compile_tree(tmp_path)
    marked = compile_tree(tmp_path, proposals=True)
    assert default.problems == []
    assert marked.problems == []
    assert default.compiled is not None
    assert marked.compiled is not None
    assert all(entry.status == Status.accepted for entry in default.compiled.directives.values())
    assert default.compiled.left_out["directives"] == len(marked.compiled.directives) - len(
        default.compiled.directives
    )


def test_the_output_holds_no_absolute_path_and_no_time_stamp(tmp_path: Path) -> None:
    write_tree(tmp_path)
    assert build_tree(tmp_path).problems == []
    assert build_tree(tmp_path, proposals=True).problems == []
    for data in output_bytes(tmp_path).values():
        assert str(tmp_path).encode() not in data
        assert not re.search(rb"\d{4}-\d{2}-\d{2}", data)
    document = json.loads(output_bytes(tmp_path)["graph.json"])
    assert all(not Path(value).is_absolute() for value in document["paths"].values())


def test_build_writes_the_default_result_and_prints_its_digests(tmp_path: Path) -> None:
    write_tree(tmp_path)
    result = RUNNER.invoke(app, ["build", str(tmp_path)])
    assert result.exit_code == 0, result.output
    written = output_bytes(tmp_path)
    assert set(written) == {"graph.json", "graph.ttl", "digests.json"}
    manifest = json.loads(written["digests.json"])
    lines = result.output.splitlines()
    assert lines[-5].startswith("in_force: This result holds only ")
    assert lines[-4] == f"graph.json {manifest['files']['graph.json']}"
    assert lines[-3] == f"graph.ttl {manifest['files']['graph.ttl']}"
    assert lines[-2] == f"digest {manifest['digest']}"
    assert lines[-1] == "7 nodes and 3 directives compiled, 3 directives left out, 0 problems"
    for name, value in manifest["files"].items():
        assert value == f"sha256:{hashlib.sha256(written[name]).hexdigest()}"


def test_build_proposals_writes_the_marked_result_and_leaves_the_default_alone(
    tmp_path: Path,
) -> None:
    write_tree(tmp_path)
    assert RUNNER.invoke(app, ["build", str(tmp_path)]).exit_code == 0
    default = output_bytes(tmp_path)
    result = RUNNER.invoke(app, ["build", str(tmp_path), "--proposals"])
    assert result.exit_code == 0, result.output
    written = output_bytes(tmp_path)
    assert {name: written[name] for name in default} == default
    assert set(written) - set(default) == {
        "graph.proposals.json",
        "graph.proposals.ttl",
        "digests.proposals.json",
    }
    manifest = json.loads(written["digests.proposals.json"])
    assert manifest["digest"] != json.loads(written["digests.json"])["digest"]
    lines = result.output.splitlines()
    assert lines[-5].startswith("proposals: NOT IN FORCE. ")
    assert lines[-2] == f"digest {manifest['digest']}"
    assert lines[-1] == "7 nodes and 5 directives compiled, 1 directives left out, 0 problems"


def test_build_reads_the_current_folder_by_default(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    write_tree(tmp_path)
    monkeypatch.chdir(tmp_path)
    assert RUNNER.invoke(app, ["build"]).exit_code == 0
    assert (tmp_path / "build/compiled/graph.json").is_file()


def test_build_prints_a_note_from_the_governance_checks(tmp_path: Path) -> None:
    write_tree(tmp_path)
    result = RUNNER.invoke(app, ["build", str(tmp_path)])
    assert "note: This folder is not a git repository" in result.output


def test_build_prints_a_note_also_when_a_check_fails(tmp_path: Path) -> None:
    write_tree(tmp_path)
    (tmp_path / "knowledge/nodes/gamma/node.md").write_text(
        node("gamma", rules=[rule("solid", scope="node").replace("Run the", "Try to run the")]),
        encoding="utf-8",
    )
    result = RUNNER.invoke(app, ["build", str(tmp_path)])
    assert result.exit_code == 1
    assert "note: This folder is not a git repository" in result.output


def broken(path: str, old: str, new: str) -> dict[str, str]:
    return {**SAMPLE, path: SAMPLE[path].replace(old, new)}


FAILING_TREES = {
    "parse": (
        "knowledge/nodes/alpha/node.md",
        broken("knowledge/nodes/alpha/node.md", "id: alpha\n", ""),
    ),
    "graph": (
        "knowledge/node.md",
        broken("knowledge/node.md", "target: alpha", "target: missing"),
    ),
    "directives": (
        "knowledge/nodes/gamma/node.md",
        {
            **SAMPLE,
            "knowledge/nodes/delta/node.md": node(
                "delta",
                front="exceptions:\n" + exception("solid", "accepted"),
                rules=[rule("spare", "proposed", "node")],
            ),
        },
    ),
    "governance": (
        "knowledge/nodes/alpha/node.md",
        broken(
            "knowledge/nodes/alpha/node.md", "knowledge_type: domain", "knowledge_type: workspace"
        ),
    ),
    "language": (
        "knowledge/nodes/gamma/node.md",
        broken(
            "knowledge/nodes/gamma/node.md", "Run the solid check.", "Try to run the solid check."
        ),
    ),
}
FAILING_CODES = {
    "parse": "schema",
    "graph": "reference",
    "directives": "exception-unused",
    "governance": "template-workspace",
    "language": "opening",
}


@pytest.mark.parametrize("name", FAILING_TREES)
def test_each_check_stops_the_build_and_removes_the_earlier_output(
    tmp_path: Path, name: str
) -> None:
    write_tree(tmp_path)
    assert RUNNER.invoke(app, ["build", str(tmp_path)]).exit_code == 0
    assert RUNNER.invoke(app, ["build", str(tmp_path), "--proposals"]).exit_code == 0
    assert len(output_bytes(tmp_path)) == len(EVERY_OUTPUT_FILE)
    _, sources = FAILING_TREES[name]
    shutil.rmtree(tmp_path / "knowledge")
    write_tree(tmp_path, sources)
    for arguments in (["build", str(tmp_path)], ["build", str(tmp_path), "--proposals"]):
        result = RUNNER.invoke(app, arguments)
        assert result.exit_code == 1, result.output
        assert re.search(rf"^.*:\d+: {FAILING_CODES[name]}: ", result.output, re.MULTILINE), (
            result.output
        )
        assert result.output.splitlines()[-1].startswith("0 nodes compiled, ")
        assert output_bytes(tmp_path) == {}


def run_git(repository: Path, *arguments: str) -> None:
    identity = ("-c", "user.name=Test", "-c", "user.email=test@example.com")
    subprocess.run(  # noqa: S603
        [GIT, "-C", str(repository), *identity, *arguments], check=True, capture_output=True
    )


def test_a_change_rule_stops_the_build_in_a_repository(tmp_path: Path) -> None:
    write_tree(tmp_path)
    run_git(tmp_path, "init", "--quiet")
    run_git(tmp_path, "add", "knowledge/node.md", "knowledge/governance")
    run_git(tmp_path, "commit", "--quiet", "-m", "start")
    result = RUNNER.invoke(app, ["build", str(tmp_path)])
    assert result.exit_code == 1
    assert ": new-status: " in result.output
    assert not (tmp_path / OUTPUT_FOLDER).exists()


def test_the_build_reads_the_tree_once(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    def fail(_folders: object) -> None:
        pytest.fail("A check parsed the tree again.")

    write_tree(tmp_path)
    monkeypatch.setattr("engine.governance.checks.parse_tree", fail)
    monkeypatch.setattr("engine.language.checks.parse_tree", fail)
    assert compile_tree(tmp_path).problems == []


def test_a_missing_language_folder_stops_the_build(tmp_path: Path) -> None:
    write_tree(tmp_path)
    shutil.rmtree(tmp_path / "knowledge/governance")
    result = RUNNER.invoke(app, ["build", str(tmp_path)])
    assert result.exit_code == 1
    assert not (tmp_path / OUTPUT_FOLDER).exists()


def test_an_empty_tree_reports_that_it_has_nothing_to_compile(tmp_path: Path) -> None:
    write_tree(tmp_path, {})
    result = RUNNER.invoke(app, ["build", str(tmp_path)])
    assert result.exit_code == 1
    path = tmp_path / "knowledge"
    assert f"{path}:1: empty-tree: " in result.output
    assert result.output.endswith("0 nodes compiled, 1 problems\n")
    assert not (tmp_path / OUTPUT_FOLDER).exists()


def test_a_lone_surrogate_in_a_node_stops_the_build_with_a_problem(tmp_path: Path) -> None:
    sources = broken("knowledge/nodes/alpha/node.md", "title: alpha", 'title: "\\ud800"')
    write_tree(tmp_path, sources)
    result = RUNNER.invoke(app, ["build", str(tmp_path)])
    assert result.exit_code == 1
    assert isinstance(result.exception, SystemExit)
    assert ": yaml: A YAML escape gives a character that is not valid." in result.output
    assert not (tmp_path / OUTPUT_FOLDER).exists()


def test_a_file_name_that_is_not_utf_8_stops_the_build_with_a_problem(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    write_tree(tmp_path)
    good = [ParsedNode(tmp_path / item.path, item.node, item.locations) for item in parsed()]
    bad = next(item for item in good if item.node.id == "delta")
    renamed = ParsedNode(tmp_path / "knowledge/nodes/\udcff/node.md", bad.node, bad.locations)
    items = [renamed if item is bad else item for item in good]

    def checked(_repository: Path) -> tuple[list[ParsedNode], list[Problem]]:
        return items, []

    monkeypatch.setattr("engine.compiler.tree.check_tree", checked)
    result = RUNNER.invoke(app, ["build", str(tmp_path)])
    assert result.exit_code == 1, result.output
    assert (
        f"{tmp_path}:1: path: The file name 'knowledge/nodes/\\udcff/node.md' is not "
        in result.output
    )
    assert not (tmp_path / OUTPUT_FOLDER).exists()


def test_a_blocked_output_folder_reports_a_problem(tmp_path: Path) -> None:
    write_tree(tmp_path)
    (tmp_path / "build").write_text("not a folder", encoding="utf-8")
    result = RUNNER.invoke(app, ["build", str(tmp_path)])
    assert result.exit_code == 1
    assert f"{tmp_path / OUTPUT_FOLDER}:1: write: " in result.output
    assert result.output.splitlines()[-1] == "0 nodes compiled, 1 problems"


def test_a_blocked_output_file_reports_a_problem(tmp_path: Path) -> None:
    write_tree(tmp_path)
    (tmp_path / OUTPUT_FOLDER / "graph.ttl").mkdir(parents=True)
    result = RUNNER.invoke(app, ["build", str(tmp_path)])
    assert result.exit_code == 1
    assert f"{tmp_path / OUTPUT_FOLDER}:1: write: " in result.output
    assert not (tmp_path / OUTPUT_FOLDER / "digests.json").exists()


def test_a_blocked_folder_also_reports_when_a_check_fails(tmp_path: Path) -> None:
    write_tree(tmp_path, FAILING_TREES["graph"][1])
    (tmp_path / "build").write_text("not a folder", encoding="utf-8")
    result = RUNNER.invoke(app, ["build", str(tmp_path)])
    assert result.exit_code == 1
    assert ": reference: " in result.output
    assert f"{tmp_path / OUTPUT_FOLDER}:1: write: " in result.output
