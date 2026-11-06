from collections import defaultdict
from dataclasses import dataclass
from typing import TYPE_CHECKING

from engine.directives.reach import walk
from engine.graph.references import edge_targets
from engine.graph.rules import root_nodes

if TYPE_CHECKING:
    from collections.abc import Collection, Mapping, Sequence

    from engine.parser.result import ParsedNode


@dataclass(frozen=True, slots=True)
class TreeRow:
    node_id: str
    depth: int
    repeated: bool
    opens: bool
    closes: int


def children_by_broader(items: Sequence[ParsedNode]) -> dict[str, list[str]]:
    roots = [item.node.id for item in root_nodes(items)]
    children: defaultdict[str, list[str]] = defaultdict(list)
    for item in sorted(items, key=lambda entry: entry.node.id):
        node_id = item.node.id
        if node_id not in roots:
            for parent in edge_targets(item, "broader") or roots:
                children[parent].append(node_id)
    return dict(children)


def subtree_ids(node_id: str, children: Mapping[str, Sequence[str]]) -> set[str]:
    return set(walk({node_id}, children, ())[0])


def tree_rows(
    root_id: str, children: Mapping[str, Sequence[str]], left_out: Collection[str] = ()
) -> list[TreeRow]:
    visits: list[tuple[str, int, bool]] = []
    seen: set[str] = set()
    stack = [(root_id, 0)]
    while stack:
        node_id, depth = stack.pop()
        repeated = node_id in seen
        seen.add(node_id)
        visits.append((node_id, depth, repeated))
        if not repeated:
            below = [child for child in children.get(node_id, ()) if child not in left_out]
            stack.extend((child, depth + 1) for child in reversed(below))
    rows: list[TreeRow] = []
    for position, (node_id, depth, repeated) in enumerate(visits):
        next_depth = visits[position + 1][1] if position + 1 < len(visits) else 0
        rows.append(
            TreeRow(node_id, depth, repeated, next_depth > depth, max(depth - next_depth, 0))
        )
    return rows
