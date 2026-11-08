from typing import TYPE_CHECKING

from engine.graph.rules import (
    check_identity,
    check_implements,
    check_placement,
    check_references,
    check_skills,
    root_nodes,
)
from engine.graph.shapes import check_shapes
from engine.graph.skills import check_skill_types
from engine.graph.structure import (
    check_associations,
    check_cycles,
    check_reachability,
)
from engine.parser.node import node_folders, parse_tree

if TYPE_CHECKING:
    from collections.abc import Sequence
    from pathlib import Path

    from engine.parser.result import ParsedNode, Problem


def check_graph(items: Sequence[ParsedNode], repository: Path) -> list[Problem]:
    if not items:
        return []
    identity = check_identity(items)
    problems = [
        *identity,
        *check_placement(items, repository),
        *check_skills(items),
        *check_implements(items),
    ]
    if not identity:
        references = check_references(items)
        problems += [*references, *check_associations(items), *check_cycles(items)]
        if not references and len(root_nodes(items)) == 1:
            problems += [
                *check_shapes(items),
                *check_reachability(items),
                *check_skill_types(items),
            ]
    return sorted(set(problems), key=_sort_key)


def _sort_key(problem: Problem) -> tuple[str, int, str, str]:
    return (str(problem.path), problem.line, problem.code, problem.message)


def check_tree(repository: Path) -> tuple[list[ParsedNode], list[Problem]]:
    items, problems = parse_tree(node_folders(repository))
    if problems:
        return items, problems
    return items, check_graph(items, repository)
