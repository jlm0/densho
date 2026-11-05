# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportMissingTypeStubs=false, reportArgumentType=false, reportAttributeAccessIssue=false
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from typing import TYPE_CHECKING

import pyshacl
from linkml_runtime.dumpers import rdflib_dumper
from linkml_runtime.loaders import yaml_loader
from linkml_runtime.utils.schemaview import SchemaView
from pydantic import BaseModel, ValidationError
from rdflib import RDF, SH, BNode, Graph, Namespace, URIRef

from knowledge_architecture.generated import metamodel_rdf
from knowledge_architecture.generated.metamodel import KnowledgeGraph, Root
from knowledge_architecture.graph.references import problem_at

if TYPE_CHECKING:
    from collections.abc import Sequence

    from rdflib.term import Node as RdfTerm

    from knowledge_architecture.parser.result import FieldPath, ParsedNode, Problem

GENERATED = Path(__file__).resolve().parents[1] / "generated"
KA = Namespace("https://github.com/jlm0/knowledge-architecture/schema/")
NODE_NAMESPACE = "https://github.com/jlm0/knowledge-architecture/node/"


@dataclass(frozen=True, slots=True)
class _Entity:
    item: ParsedNode
    model: BaseModel
    field_path: FieldPath
    kind: str


@cache
def _schema_view() -> SchemaView:
    return SchemaView(str(GENERATED / "metamodel.yaml"))


@cache
def _turtle(name: str) -> Graph:
    return Graph().parse(GENERATED / name, format="turtle")


def _entities(items: Sequence[ParsedNode]) -> dict[str, _Entity]:
    entities: dict[str, _Entity] = {}
    for item in items:
        entities[item.node.id] = _Entity(item, item.node, (), item.node.kind)
        for position, directive in enumerate(item.node.directives or []):
            field_path = ("directives", position)
            entities[directive.id] = _Entity(item, directive, field_path, "ka:Directive")
    return entities


def rdf_graph(graph: KnowledgeGraph) -> Graph:
    data = graph.model_dump(exclude_none=True)
    loaded = yaml_loader.load(data, target_class=metamodel_rdf.KnowledgeGraph)
    return rdflib_dumper.as_rdf_graph(loaded, _schema_view(), prefix_map={"_base": NODE_NAMESPACE})


def check_shapes(items: Sequence[ParsedNode]) -> list[Problem]:
    root = next(item for item in items if isinstance(item.node, Root))
    others = [item.node for item in items if item is not root]
    try:
        graph = KnowledgeGraph.model_validate({"root": root.node, "nodes": others})
    except ValidationError as error:
        return [
            problem_at(root, ("id",), "schema", f"{detail['loc'][0]}: {detail['msg']}")
            for detail in error.errors()
        ]
    data = rdf_graph(graph)
    _, report, text = pyshacl.validate(
        data,
        shacl_graph=_turtle("metamodel.shacl.ttl"),
        ont_graph=_turtle("metamodel.owl.ttl"),
        inference="none",
    )
    if not isinstance(report, Graph):
        return [problem_at(root, ("id",), "shape", f"{text!a}")]
    return report_problems(report, data, items, root)


def report_problems(
    report: Graph, data: Graph, items: Sequence[ParsedNode], root: ParsedNode
) -> list[Problem]:
    entities = _entities(items)
    return [
        _result_problem(report, result, data, entities, root)
        for result in report.subjects(RDF.type, SH.ValidationResult)
    ]


def _result_problem(
    report: Graph,
    result: RdfTerm,
    data: Graph,
    entities: dict[str, _Entity],
    root: ParsedNode,
) -> Problem:
    focus = report.value(result, SH.focusNode)
    path = report.value(result, SH.resultPath)
    value = report.value(result, SH.value)
    entity = _focus_entity(focus, value, data, entities)
    target = entities.get(_local_id(value))
    if entity is None or target is None or not isinstance(path, URIRef):
        message = str(report.value(result, SH.resultMessage))
        return problem_at(root, ("id",), "shape", f"{message!a}")
    field = str(path).replace("#", "/").rpartition("/")[2]
    message = f"{field} cannot name {_local_id(value)}, which has kind {target.kind}."
    return problem_at(entity.item, _field_path(entity, field, value), "type", message)


def _local_id(term: RdfTerm | None) -> str:
    return str(term).removeprefix(NODE_NAMESPACE)


def _focus_entity(
    focus: RdfTerm | None, value: RdfTerm | None, data: Graph, entities: dict[str, _Entity]
) -> _Entity | None:
    if not isinstance(focus, BNode):
        return entities.get(_local_id(focus))
    holder = entities.get(_local_id(data.value(predicate=KA.pointers, object=focus)))
    if holder is None:
        return None
    kind = str(data.value(focus, RDF.type)).replace(str(KA), "ka:")
    for index, pointer in enumerate(holder.item.node.pointers or []):
        if pointer.target == _local_id(value) and pointer.kind == kind:
            return _Entity(holder.item, pointer, ("pointers", index), kind)
    return None


def _field_path(entity: _Entity, field: str, value: RdfTerm | None) -> FieldPath:
    values = getattr(entity.model, field, None)
    if isinstance(values, list):
        return (*entity.field_path, field, values.index(_local_id(value)))
    return (*entity.field_path, field)
