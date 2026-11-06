from collections import defaultdict, deque
from dataclasses import dataclass
from typing import TYPE_CHECKING

from engine.generated.metamodel import DirectiveScope, Status
from engine.graph.references import edge_targets, exceptions_of
from engine.graph.rules import root_nodes

if TYPE_CHECKING:
    from collections.abc import Collection, Mapping, Sequence

    from engine.generated.metamodel import Directive
    from engine.parser.result import ParsedNode

type Children = Mapping[str, Sequence[str]]


@dataclass(frozen=True, slots=True)
class AppliedDirective:
    directive: Directive
    holder: str
    route: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class Reach:
    directive: Directive
    holder: ParsedNode
    position: int
    attached: frozenset[str]
    children: Children
    came_from: Mapping[str, str | None]
    stopped_at: frozenset[str]

    def route_to(self, node_id: str) -> tuple[str, ...]:
        route = [node_id]
        step = self.came_from[node_id]
        while step is not None:
            route.append(step)
            step = self.came_from[step]
        return tuple(reversed(route))


@dataclass(frozen=True, slots=True)
class Resolution:
    reaches: tuple[Reach, ...]

    def at(self, node_id: str) -> list[AppliedDirective]:
        applied = [
            AppliedDirective(reach.directive, reach.holder.node.id, reach.route_to(node_id))
            for reach in self.reaches
            if node_id in reach.came_from
        ]
        return sorted(applied, key=lambda entry: (-len(entry.route), entry.directive.id))


def walk(
    seeds: Collection[str], children: Children, stops: Collection[str]
) -> tuple[dict[str, str | None], set[str]]:
    came_from: dict[str, str | None] = dict.fromkeys(sorted(seeds))
    stopped: set[str] = set()
    queue = deque(came_from)
    while queue:
        current = queue.popleft()
        for child in children.get(current, ()):
            if child in came_from:
                continue
            if child in stops:
                stopped.add(child)
                continue
            came_from[child] = current
            queue.append(child)
    return came_from, stopped


def _links(items: Sequence[ParsedNode]) -> tuple[Children, Children]:
    roots = [item.node.id for item in root_nodes(items)]
    under: defaultdict[str, list[str]] = defaultdict(list)
    users: defaultdict[str, list[str]] = defaultdict(list)
    for item in sorted(items, key=lambda entry: entry.node.id):
        node_id = item.node.id
        for parent in edge_targets(item, "broader") or roots:
            under[parent].append(node_id)
        for used in edge_targets(item, "uses"):
            under[used].append(node_id)
            users[used].append(node_id)
    return under, users


def _stops_by_directive(
    items: Sequence[ParsedNode], live: Collection[Status]
) -> dict[str, set[str]]:
    stops: defaultdict[str, set[str]] = defaultdict(set)
    for item in items:
        for exception in exceptions_of(item):
            if exception.status in live:
                stops[exception.directive].add(item.node.id)
    return stops


def _skills_applying(items: Sequence[ParsedNode]) -> dict[str, set[str]]:
    skills: defaultdict[str, set[str]] = defaultdict(set)
    for item in items:
        for directive_id in edge_targets(item, "applies"):
            skills[directive_id].add(item.node.id)
    return skills


def live_statuses(*, proposals: bool) -> tuple[Status, ...]:
    return (Status.accepted, Status.proposed) if proposals else (Status.accepted,)


def resolve_directives(items: Sequence[ParsedNode], *, proposals: bool = False) -> Resolution:
    live = live_statuses(proposals=proposals)
    under, users = _links(items)
    stops = _stops_by_directive(items, live)
    applying = _skills_applying(items)
    reaches: list[Reach] = []
    for item in items:
        for position, directive in enumerate(item.node.directives or []):
            attached: set[str] = set()
            if directive.status in live:
                attached = {
                    item.node.id,
                    *(directive.also_attached_to or []),
                    *applying.get(directive.id, set()),
                }
            children = under if directive.scope == DirectiveScope.subtree else users
            came_from, stopped = walk(attached, children, stops.get(directive.id, set()))
            reaches.append(
                Reach(
                    directive,
                    item,
                    position,
                    frozenset(attached),
                    children,
                    came_from,
                    frozenset(stopped),
                )
            )
    return Resolution(tuple(reaches))
