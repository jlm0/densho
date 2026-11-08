import json
from dataclasses import dataclass, replace
from typing import TYPE_CHECKING, cast

from engine.directives import AppliedDirective, live_statuses, resolve_directives
from engine.generated.metamodel import (
    CompiledResult,
    KnowledgeGraph,
    Root,
    Skill,
    Status,
)
from engine.graph.references import exceptions_of
from engine.graph.rules import root_nodes

if TYPE_CHECKING:
    from collections.abc import Collection, Mapping, Sequence
    from pathlib import Path

    from engine.generated.metamodel import (
        Directive,
        DirectiveException,
        Node,
    )
    from engine.parser.result import ParsedNode, Script, StepFile


@dataclass(frozen=True, slots=True)
class CompiledGraph:
    result: CompiledResult
    graph: KnowledgeGraph
    paths: Mapping[str, str]
    applied: Mapping[str, tuple[AppliedDirective, ...]]
    left_out: Mapping[str, int]
    scripts: Mapping[str, tuple[Script, ...]]
    step_files: Mapping[str, tuple[StepFile, ...]]

    @property
    def directives(self) -> dict[str, Directive]:
        return _directives_of(self.graph)


def _directives_of(graph: KnowledgeGraph) -> dict[str, Directive]:
    nodes = [graph.root, *graph.nodes]
    return {directive.id: directive for node in nodes for directive in node.directives or []}


def _among(targets: list[str] | None, kept: Collection[str]) -> list[str]:
    return [target for target in targets or [] if target in kept]


def _filtered_directive(directive: Directive, kept: Collection[str]) -> Directive:
    return directive.model_copy(
        update={
            "refines": _among(directive.refines, kept),
            "conflicts_with": _among(directive.conflicts_with, kept),
        }
    )


def _kept_exceptions(
    item: ParsedNode, kept: Collection[str], live: Collection[Status]
) -> list[DirectiveException]:
    return [
        exception
        for exception in exceptions_of(item)
        if exception.status in live and exception.directive in kept
    ]


def _filtered_node(item: ParsedNode, kept: Collection[str], live: Collection[Status]) -> Node:
    node = item.node
    update: dict[str, object] = {
        "directives": [
            _filtered_directive(directive, kept)
            for directive in node.directives or []
            if directive.id in kept
        ],
        "exceptions": _kept_exceptions(item, kept, live),
    }
    if isinstance(node, Skill):
        update["applies"] = _among(node.applies, kept)
    return node.model_copy(update=update)


def _list_key(entry: object) -> tuple[str, str]:
    entity_id = cast("dict[str, object]", entry).get("id", "") if isinstance(entry, dict) else ""
    return str(entity_id), json.dumps(entry, sort_keys=True)


ORDERED_FIELDS = frozenset({"steps"})


def normal_form(value: object) -> object:
    if isinstance(value, dict):
        fields = cast("dict[str, object]", value)
        return {
            field: fields[field] if field in ORDERED_FIELDS else normal_form(fields[field])
            for field in sorted(fields)
            if fields[field] != []
        }
    if isinstance(value, list):
        entries = [normal_form(entry) for entry in cast("list[object]", value)]
        by_key = {_list_key(entry): entry for entry in entries}
        return [by_key[key] for key in sorted(by_key)]
    return value


def _dumped(node: Node) -> object:
    return normal_form(node.model_dump(mode="json"))


def _kept_node(item: ParsedNode) -> bool:
    return item.node.status != Status.rejected or isinstance(item.node, Root)


def compile_items(
    items: Sequence[ParsedNode], repository: Path, *, proposals: bool = False
) -> CompiledGraph:
    live = live_statuses(proposals=proposals)
    result = CompiledResult.proposals if proposals else CompiledResult.in_force
    ordered = sorted((item for item in items if _kept_node(item)), key=lambda item: item.node.id)
    directives = [
        directive
        for item in ordered
        for directive in item.node.directives or []
        if directive.status != Status.rejected
    ]
    kept = frozenset(directive.id for directive in directives if directive.status in live)
    filtered = {item.node.id: _filtered_node(item, kept, live) for item in ordered}
    root_id = root_nodes(ordered)[0].node.id
    graph = KnowledgeGraph.model_validate(
        {
            "result": result,
            "root": _dumped(filtered[root_id]),
            "nodes": [_dumped(node) for node_id, node in filtered.items() if node_id != root_id],
        }
    )
    exception_count = sum(
        exception.status != Status.rejected for item in ordered for exception in exceptions_of(item)
    )
    kept_exceptions = sum(len(_kept_exceptions(item, kept, live)) for item in ordered)
    resolution = resolve_directives(items, proposals=proposals)
    by_id = _directives_of(graph)
    return CompiledGraph(
        result=result,
        graph=graph,
        paths={item.node.id: item.path.relative_to(repository).as_posix() for item in ordered},
        applied={
            item.node.id: tuple(
                replace(entry, directive=by_id[entry.directive.id])
                for entry in resolution.at(item.node.id)
            )
            for item in ordered
        },
        left_out={
            "directives": len(directives) - len(kept),
            "exceptions": exception_count - kept_exceptions,
        },
        scripts={item.node.id: item.scripts for item in ordered if item.scripts},
        step_files={item.node.id: item.step_files for item in ordered if item.step_files},
    )
