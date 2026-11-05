from typing import TYPE_CHECKING

from knowledge_architecture.graph.rules import (
    check_identity,
    check_implements,
    check_placement,
    check_references,
    check_skills,
    root_nodes,
)
from knowledge_architecture.graph.shapes import check_shapes
from knowledge_architecture.graph.structure import (
    check_associations,
    check_cycles,
    check_reachability,
)
from knowledge_architecture.parser.node import parse_tree

if TYPE_CHECKING:
    from collections.abc import Sequence
    from pathlib import Path

    from knowledge_architecture.parser.result import ParsedNode, Problem


def check_graph(items: Sequence[ParsedNode], *, knowledge: Path, skills: Path) -> list[Problem]:
    if not items:
        return []
    identity = check_identity(items)
    problems = [
        *identity,
        *check_placement(items, knowledge=knowledge, skills=skills),
        *check_skills(items),
        *check_implements(items),
    ]
    if not identity:
        references = check_references(items)
        problems += [*references, *check_associations(items), *check_cycles(items)]
        if not references and len(root_nodes(items)) == 1:
            problems += [*check_shapes(items), *check_reachability(items)]
    return sorted(set(problems), key=_sort_key)


def _sort_key(problem: Problem) -> tuple[str, int, str, str]:
    return (str(problem.path), problem.line, problem.code, problem.message)


def check_tree(repository: Path) -> tuple[list[ParsedNode], list[Problem]]:
    knowledge, skills = repository / "knowledge", repository / "skills"
    items, problems = parse_tree([knowledge, skills])
    if problems:
        return items, problems
    return items, check_graph(items, knowledge=knowledge, skills=skills)
