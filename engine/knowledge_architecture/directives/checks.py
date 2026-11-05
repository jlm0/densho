# pyright: reportUnknownMemberType=false
import re
from collections import defaultdict
from typing import TYPE_CHECKING

import networkx as nx

from knowledge_architecture.directives.reach import Reach, resolve_directives, walk
from knowledge_architecture.generated.metamodel import Status
from knowledge_architecture.graph import check_tree
from knowledge_architecture.graph.references import edge_targets, exceptions_of, problem_at
from knowledge_architecture.language.prose import read_prose

if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence
    from pathlib import Path

    from knowledge_architecture.parser.result import FieldPath, ParsedNode, Problem

DIRECTIVE_CODES = (
    "exception-unused",
    "exception-attached",
    "exception-repeated",
    "route-conflict",
    "conflict",
    "opposite",
    "refines-outside",
    "refines-cycle",
    "applies-deprecated",
)
NEGATION = re.compile(r"(?:^|(?<=, ))do not ")


def _sample(nodes: Iterable[str]) -> str:
    ordered = sorted(nodes)
    return ordered[0] if len(ordered) == 1 else f"{ordered[0]} and {len(ordered) - 1} more"


def _at(reach: Reach, *field_path: str | int) -> tuple[ParsedNode, FieldPath]:
    return reach.holder, ("directives", reach.position, *field_path)


def _exception_problems(items: Sequence[ParsedNode], by_id: dict[str, Reach]) -> list[Problem]:
    problems: list[Problem] = []
    for item in items:
        seen: set[str] = set()
        for index, exception in enumerate(exceptions_of(item)):
            directive_id = exception.directive
            reach = by_id[directive_id]
            code, message = None, ""
            if directive_id in seen:
                code = "exception-repeated"
                message = f"This node already has an exception for {directive_id}."
            elif exception.status == Status.deprecated:
                pass
            elif item.node.id in reach.attached:
                code = "exception-attached"
                message = (
                    f"This node attaches {directive_id} and also steps out of it. "
                    "Remove the exception or the attachment."
                )
            elif item.node.id not in reach.stopped_at:
                code = "exception-unused"
                message = (
                    f"This exception stops nothing, because no route brings {directive_id} "
                    "to this node. Remove it."
                )
            seen.add(directive_id)
            if code is not None:
                problems.append(problem_at(item, ("exceptions", index), code, message))
    return problems


def _route_conflicts(items: Sequence[ParsedNode], reaches: Sequence[Reach]) -> list[Problem]:
    by_node = {item.node.id: item for item in items}
    problems: list[Problem] = []
    for reach in reaches:
        unstopped, _ = walk(reach.attached, reach.children, ())
        conflicts: dict[str, str] = {}
        for parent in sorted(unstopped.keys() - reach.came_from.keys()):
            for child in reach.children.get(parent, ()):
                if child in reach.came_from and child not in reach.attached:
                    conflicts.setdefault(child, parent)
        for node_id, parent in conflicts.items():
            message = (
                f"{reach.directive.id} still reaches this node, but its route through {parent} "
                "stops. Add an exception here, or attach the directive to this node."
            )
            problems.append(problem_at(by_node[node_id], ("id",), "route-conflict", message))
    return problems


def _declared_conflicts(reaches: Sequence[Reach], by_id: dict[str, Reach]) -> list[Problem]:
    problems: list[Problem] = []
    for reach in reaches:
        for index, other in enumerate(reach.directive.conflicts_with or []):
            shared = reach.came_from.keys() & by_id[other].came_from.keys()
            if shared:
                message = (
                    f"This directive conflicts with {other}, and both apply at {_sample(shared)}. "
                    "Add an exception, or change the attachments."
                )
                item, field_path = _at(reach, "conflicts_with", index)
                problems.append(problem_at(item, field_path, "conflict", message))
    return problems


def _positive_form(text: str) -> tuple[str, bool]:
    _, plain = read_prose(text)
    normal = " ".join(plain.casefold().split())
    positive, count = NEGATION.subn("", normal, count=1)
    return positive, count == 1


def _opposites(reaches: Sequence[Reach]) -> list[Problem]:
    groups: defaultdict[str, dict[bool, list[Reach]]] = defaultdict(lambda: defaultdict(list))
    for reach in reaches:
        positive, negated = _positive_form(reach.directive.text)
        groups[positive][negated].append(reach)
    problems: list[Problem] = []
    for sides in groups.values():
        for negative in sides[True]:
            for other in sides[False]:
                shared = negative.came_from.keys() & other.came_from.keys()
                if shared:
                    message = (
                        f"This directive is the opposite of {other.directive.id}, and both apply "
                        f"at {_sample(shared)}."
                    )
                    item, field_path = _at(negative)
                    problems.append(problem_at(item, field_path, "opposite", message))
    return problems


def _refinements(reaches: Sequence[Reach], by_id: dict[str, Reach]) -> list[Problem]:
    problems: list[Problem] = []
    for reach in reaches:
        for index, other in enumerate(reach.directive.refines or []):
            outside = reach.came_from.keys() - by_id[other].came_from.keys()
            if outside:
                message = (
                    f"This directive refines {other}, but {other} does not apply at "
                    f"{_sample(outside)}, where this directive applies."
                )
                item, field_path = _at(reach, "refines", index)
                problems.append(problem_at(item, field_path, "refines-outside", message))
    return problems


def _refinement_cycles(reaches: Sequence[Reach], by_id: dict[str, Reach]) -> list[Problem]:
    graph: nx.DiGraph[str] = nx.DiGraph()
    graph.add_edges_from(
        (reach.directive.id, target)
        for reach in reaches
        for target in reach.directive.refines or []
    )
    problems: list[Problem] = []
    for component in nx.strongly_connected_components(graph):
        start = min(component)
        if len(component) > 1 or graph.has_edge(start, start):
            reach = by_id[start]
            targets = reach.directive.refines or []
            index = next(i for i, target in enumerate(targets) if target in component)
            message = f"The refines edges close a cycle through {', '.join(sorted(component))}."
            item, field_path = _at(reach, "refines", index)
            problems.append(problem_at(item, field_path, "refines-cycle", message))
    return problems


def _deprecated_applies(items: Sequence[ParsedNode], by_id: dict[str, Reach]) -> list[Problem]:
    return [
        problem_at(
            item,
            ("applies", index),
            "applies-deprecated",
            f"This skill applies {directive_id}, which is deprecated. Remove it from applies.",
        )
        for item in items
        for index, directive_id in enumerate(edge_targets(item, "applies"))
        if by_id[directive_id].directive.status == Status.deprecated
    ]


def _by_id(reaches: Sequence[Reach]) -> dict[str, Reach]:
    return {reach.directive.id: reach for reach in reaches}


def _state_problems(items: Sequence[ParsedNode], reaches: Sequence[Reach]) -> list[Problem]:
    by_id = _by_id(reaches)
    return [
        *_route_conflicts(items, reaches),
        *_declared_conflicts(reaches, by_id),
        *_opposites(reaches),
        *_refinements(reaches, by_id),
    ]


def check_items(items: Sequence[ParsedNode]) -> list[Problem]:
    in_force = resolve_directives(items).reaches
    projected = resolve_directives(items, proposals=True).reaches
    by_id = _by_id(projected)
    problems = {
        *_state_problems(items, in_force),
        *_state_problems(items, projected),
        *_exception_problems(items, by_id),
        *_refinement_cycles(projected, by_id),
        *_deprecated_applies(items, by_id),
    }
    return sorted(problems)


def check_directives(repository: Path) -> tuple[int, list[Problem]]:
    items, problems = check_tree(repository)
    if problems:
        return 0, problems
    count = sum(len(item.node.directives or []) for item in items)
    return count, check_items(items)
