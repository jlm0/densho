# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportMissingTypeStubs=false, reportAttributeAccessIssue=false, reportOptionalMemberAccess=false
from pathlib import Path

import pytest
from linkml.generators.pythongen import PythonGenerator
from linkml_runtime.dumpers import rdflib_dumper
from linkml_runtime.loaders import yaml_loader
from linkml_runtime.utils.compile_python import compile_python
from linkml_runtime.utils.schemaview import SchemaView
from rdflib import RDF, SKOS, Graph, Namespace, URIRef

from knowledge_architecture.generated.metamodel import KnowledgeGraph

SCHEMA = Path(__file__).resolve().parents[1] / "governance/schema/metamodel.yaml"
KA = Namespace("https://github.com/jlm0/knowledge-architecture/schema/")
BASE = Namespace("https://example.org/node/")
DCTERMS = Namespace("http://purl.org/dc/terms/")

VIEW = SchemaView(str(SCHEMA))

GOVERNED = {"status": "accepted", "origin": "template"}
TAXONOMY = {**GOVERNED, "title": "Sample", "knowledge_type": "domain", "definition": "A sample."}

SAMPLE_GRAPH = {
    "root": {
        **GOVERNED,
        "id": "root",
        "kind": "ka:Root",
        "title": "Root",
        "pointers": [
            {"kind": "ka:AlwaysPointer", "target": "governance", "trigger": "At session start."},
            {"kind": "ka:TextPointer", "target": "design", "trigger": "When the task is design."},
            {"kind": "ka:SkillPointer", "target": "review", "trigger": "When X needs a review."},
        ],
    },
    "nodes": [
        {
            **TAXONOMY,
            "id": "governance",
            "kind": "ka:Domain",
            "governs": ["root", "governance"],
            "sources": ["governance/schema/metamodel.yaml"],
            "directives": [
                {**GOVERNED, "id": "use-a-verb", "text": "Start with a verb.", "scope": "subtree"},
            ],
        },
        {**TAXONOMY, "id": "design", "kind": "ka:Domain", "informs": ["governance"]},
        {**TAXONOMY, "id": "ui", "kind": "ka:Discipline", "broader": ["design"]},
        {**TAXONOMY, "id": "visual", "kind": "ka:PracticeArea", "broader": ["ui", "design"]},
        {**TAXONOMY, "id": "motion", "kind": "ka:Concept", "broader": ["ui"]},
        {
            **TAXONOMY,
            "id": "hierarchy",
            "kind": "ka:Concept",
            "broader": ["visual"],
            "related": ["motion"],
        },
        {
            **TAXONOMY,
            "id": "settings",
            "kind": "ka:Concept",
            "origin": "project",
            "knowledge_type": "workspace",
            "broader": ["hierarchy"],
            "implements": ["hierarchy"],
            "depends_on": ["motion"],
            "pointers": [
                {
                    "kind": "ka:PathPointer",
                    "target": "hierarchy",
                    "trigger": "When the task edits settings.",
                    "paths": ["src/settings/**"],
                },
            ],
        },
        {
            **GOVERNED,
            "id": "review",
            "kind": "ka:Skill",
            "title": "Review",
            "knowledge_type": "domain",
            "description": "Use this skill for a review.",
            "uses": ["hierarchy", "settings"],
            "applies": ["use-a-verb"],
        },
    ],
}


@pytest.fixture(scope="module")
def rdf() -> Graph:
    source = PythonGenerator(str(SCHEMA)).serialize()
    assert source is not None
    module = compile_python(source)
    graph = yaml_loader.load(SAMPLE_GRAPH, target_class=module.KnowledgeGraph)
    return rdflib_dumper.as_rdf_graph(graph, VIEW, prefix_map={"_base": str(BASE)})


def test_sample_graph_round_trips() -> None:
    graph = KnowledgeGraph.model_validate(SAMPLE_GRAPH)
    assert graph.model_dump(exclude_none=True) == SAMPLE_GRAPH


@pytest.mark.parametrize(
    ("node", "rdf_class"),
    [
        ("root", KA.Root),
        ("governance", KA.Domain),
        ("ui", KA.Discipline),
        ("visual", KA.PracticeArea),
        ("hierarchy", KA.Concept),
        ("review", KA.Skill),
        ("use-a-verb", KA.Directive),
    ],
)
def test_rdf_types_each_entity(rdf: Graph, node: str, rdf_class: URIRef) -> None:
    assert (BASE[node], RDF.type, rdf_class) in rdf


@pytest.mark.parametrize(
    ("pointer_class", "target"),
    [
        (KA.AlwaysPointer, "governance"),
        (KA.TextPointer, "design"),
        (KA.SkillPointer, "review"),
        (KA.PathPointer, "hierarchy"),
    ],
)
def test_rdf_types_each_pointer(rdf: Graph, pointer_class: URIRef, target: str) -> None:
    assert (None, RDF.type, pointer_class) in rdf
    pointers = list(rdf.subjects(RDF.type, pointer_class))
    assert [rdf.value(pointer, KA.target) for pointer in pointers] == [BASE[target]]


@pytest.mark.parametrize(
    ("subject", "predicate", "target"),
    [
        ("visual", SKOS.broader, "ui"),
        ("visual", SKOS.broader, "design"),
        ("hierarchy", SKOS.related, "motion"),
        ("design", KA.informs, "governance"),
        ("settings", KA.depends_on, "motion"),
        ("settings", KA.implements, "hierarchy"),
        ("governance", KA.governs, "root"),
        ("governance", KA.governs, "governance"),
        ("review", KA.uses, "hierarchy"),
        ("review", KA.applies, "use-a-verb"),
    ],
)
def test_rdf_edge_uses_predicate(rdf: Graph, subject: str, predicate: URIRef, target: str) -> None:
    assert (BASE[subject], predicate, BASE[target]) in rdf


def test_rdf_keeps_source_and_labels(rdf: Graph) -> None:
    governance = BASE["governance"]
    assert rdf.value(governance, DCTERMS.source) is not None
    assert rdf.value(governance, SKOS.prefLabel) is not None
    assert rdf.value(governance, SKOS.definition) is not None


def test_schema_lists_each_edge_kind() -> None:
    edges = {name for name, slot in VIEW.all_slots().items() if slot.is_a == "edge"}
    assert edges == {
        "broader",
        "related",
        "informs",
        "depends_on",
        "governs",
        "implements",
        "uses",
        "applies",
    }


def test_schema_lists_each_abstract_class() -> None:
    abstract = {name for name, item in VIEW.all_classes().items() if item.abstract}
    assert abstract == {"GovernedEntity", "Node", "KnowledgeNode", "TaxonomyNode", "Pointer"}


def test_abstract_edge_has_an_object_range() -> None:
    assert VIEW.get_slot("edge").range == "GovernedEntity"


def test_related_edge_is_symmetric() -> None:
    assert VIEW.get_slot("related").symmetric is True


def test_taxonomy_nodes_are_skos_concepts() -> None:
    assert VIEW.get_class("TaxonomyNode").class_uri == "skos:Concept"


@pytest.mark.parametrize(
    ("class_name", "ranks"),
    [
        ("PracticeArea", {"Domain", "Discipline", "PracticeArea"}),
        ("Concept", {"Domain", "Discipline", "PracticeArea", "Concept"}),
    ],
)
def test_broader_declares_ranks(class_name: str, ranks: set[str]) -> None:
    options = VIEW.induced_slot("broader", class_name).any_of
    assert isinstance(options, list)
    assert {option.range for option in options} == ranks


def test_discipline_broader_names_a_domain() -> None:
    assert VIEW.induced_slot("broader", "Discipline").range == "Domain"


def test_skill_pointer_targets_a_skill() -> None:
    assert VIEW.induced_slot("target", "SkillPointer").range == "Skill"
