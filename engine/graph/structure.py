# pyright: reportUnknownMemberType=false
from typing import TYPE_CHECKING

import networkx as nx

from engine.generated.metamodel import Root, Skill, Status
from engine.graph.references import edge_targets, problem_at

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable, Sequence

    from engine.parser.result import ParsedNode, Problem

MAX_POINTER_HOPS = 6
ACYCLIC_EDGES = ("broader", "depends_on")


def _graph_of(
    items: Sequence[ParsedNode], targets_of: Callable[[ParsedNode], Iterable[str]]
) -> nx.DiGraph[str]:
    node_ids = [item.node.id for item in items]
    known = set(node_ids)
    graph: nx.DiGraph[str] = nx.DiGraph()
    graph.add_nodes_from(node_ids)
    graph.add_edges_from(
        (item.node.id, target) for item in items for target in targets_of(item) if target in known
    )
    return graph


def edge_graph(items: Sequence[ParsedNode], field: str) -> nx.DiGraph[str]:
    return _graph_of(items, lambda item: edge_targets(item, field))


def check_associations(items: Sequence[ParsedNode]) -> list[Problem]:
    broader = edge_graph(items, "broader")
    problems: list[Problem] = []
    for item in items:
        chain = nx.ancestors(broader, item.node.id) | nx.descendants(broader, item.node.id)
        problems.extend(
            problem_at(
                item,
                ("related", index),
                "association",
                f"related names {target}, which is in the broader chain of this node.",
            )
            for index, target in enumerate(edge_targets(item, "related"))
            if target in chain
        )
    return problems


def check_cycles(items: Sequence[ParsedNode]) -> list[Problem]:
    by_id = {item.node.id: item for item in items}
    problems: list[Problem] = []
    for field in ACYCLIC_EDGES:
        graph = edge_graph(items, field)
        for component in nx.strongly_connected_components(graph):
            start = min(component)
            if len(component) > 1 or graph.has_edge(start, start):
                problems.append(_cycle_problem(by_id[start], field, graph, component))
    return problems


def _cycle_problem(
    item: ParsedNode, field: str, graph: nx.DiGraph[str], component: set[str]
) -> Problem:
    start = item.node.id
    routes = [
        nx.shortest_path(graph, successor, start)
        for successor in graph.successors(start)
        if successor in component
    ]
    route = min(routes, key=lambda route: (len(route), route))
    index = edge_targets(item, field).index(route[0])
    chain = " -> ".join([start, *route])
    return problem_at(item, (field, index), "cycle", f"This {field} edge closes a cycle: {chain}.")


def check_reachability(items: Sequence[ParsedNode]) -> list[Problem]:
    live = [item for item in items if item.node.status != Status.rejected]
    entry_points = [item.node.id for item in live if isinstance(item.node, Root | Skill)]
    graph = _graph_of(live, lambda item: (pointer.target for pointer in item.node.pointers or []))
    routes = nx.multi_source_dijkstra_path(graph, entry_points)
    problems: list[Problem] = []
    for item in live:
        route = routes.get(item.node.id)
        if route is None:
            message = "No chain of pointers from the root node or a skill reaches this node."
            problems.append(problem_at(item, ("id",), "unreachable", message))
        elif len(route) - 1 > MAX_POINTER_HOPS:
            message = (
                f"The shortest pointer route takes {len(route) - 1} hops, and the limit is "
                f"{MAX_POINTER_HOPS}: {' -> '.join(route)}."
            )
            problems.append(problem_at(item, ("id",), "depth", message))
    return problems
