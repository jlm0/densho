from collections import defaultdict, deque
from dataclasses import dataclass
from typing import TYPE_CHECKING, cast

from engine.generated.metamodel import Discipline, Domain, KnowledgeNode

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping, Sequence

    from engine.directives import AppliedDirective
    from engine.generated.metamodel import DirectiveException, Node, Skill

type Read = tuple[str, tuple[str, ...]]
type HeldException = tuple[str, DirectiveException]


@dataclass(frozen=True, slots=True)
class Placement:
    copies: tuple[AppliedDirective, ...]
    reads: tuple[Read, ...]
    exceptions: tuple[HeldException, ...]


@dataclass(frozen=True, slots=True)
class FlowPlacement:
    skill: Placement
    steps: Mapping[str, Placement]


class Tree:
    def __init__(self, nodes: Sequence[Node]) -> None:
        self.nodes = {node.id: node for node in nodes}
        self.children: defaultdict[str, list[str]] = defaultdict(list)
        self.parents: dict[str, list[str]] = {}
        for node in nodes:
            parents = cast("list[str] | None", getattr(node, "broader", None)) or []
            self.parents[node.id] = [parent for parent in parents if parent in self.nodes]
            for parent in self.parents[node.id]:
                self.children[parent].append(node.id)

    def subtree(self, start: str) -> list[str]:
        found = [start]
        seen = {start}
        waiting = deque([start])
        while waiting:
            for child in sorted(self.children[waiting.popleft()]):
                if child not in seen:
                    seen.add(child)
                    found.append(child)
                    waiting.append(child)
        return found

    def above(self, start: str) -> set[str]:
        seen = {start}
        waiting = [start]
        while waiting:
            for parent in self.parents.get(waiting.pop(), []):
                if parent not in seen:
                    seen.add(parent)
                    waiting.append(parent)
        return seen

    def homes(self, used: str) -> set[str]:
        above = self.above(used)
        disciplines = {node_id for node_id in above if isinstance(self.nodes[node_id], Discipline)}
        return disciplines or {
            node_id for node_id in above if isinstance(self.nodes[node_id], Domain)
        }

    def exceptions(self, node_ids: Iterable[str]) -> tuple[HeldException, ...]:
        return tuple(
            (node_id, exception)
            for node_id in node_ids
            for exception in _exceptions_of(self.nodes[node_id])
        )


def _exceptions_of(node: Node) -> list[DirectiveException]:
    return (node.exceptions or []) if isinstance(node, KnowledgeNode) else []


def _unique(entries: Iterable[AppliedDirective], left_out: set[str]) -> list[AppliedDirective]:
    kept: dict[str, AppliedDirective] = {}
    for entry in entries:
        if entry.directive.id not in left_out:
            kept.setdefault(entry.directive.id, entry)
    return list(kept.values())


def _reads(
    entries: Sequence[AppliedDirective], applied: Mapping[str, Sequence[AppliedDirective]]
) -> tuple[Read, ...]:
    by_holder: dict[str, list[str]] = {}
    for entry in entries:
        by_holder.setdefault(entry.holder, []).append(entry.directive.id)
    reads: list[Read] = []
    for holder, found in by_holder.items():
        held = {entry.directive.id for entry in applied.get(holder, ()) if entry.holder == holder}
        reads.append((holder, () if set(found) == held else tuple(sorted(found))))
    return tuple(reads)


def _placement(
    entries: Sequence[AppliedDirective],
    home: set[str],
    applied: Mapping[str, Sequence[AppliedDirective]],
    exceptions: tuple[HeldException, ...],
) -> Placement:
    copies = tuple(entry for entry in entries if entry.holder in home)
    others = [entry for entry in entries if entry.holder not in home]
    return Placement(copies, _reads(others, applied), exceptions)


def skill_placement(
    skill: Skill, tree: Tree, applied: Mapping[str, Sequence[AppliedDirective]]
) -> Placement:
    home = {skill.id}
    for used in skill.uses or []:
        if used in tree.nodes:
            for top in tree.homes(used):
                home.update(tree.subtree(top))
    entries = _unique(applied.get(skill.id, ()), set())
    return _placement(entries, home, applied, tree.exceptions([skill.id]))


def flow_placement(
    skill: Skill, tree: Tree, applied: Mapping[str, Sequence[AppliedDirective]]
) -> FlowPlacement:
    discipline = (skill.uses or [skill.id])[0]
    steps = [step for step in skill.steps or [] if step in tree.nodes]
    home = {skill.id, *tree.subtree(discipline)}
    below = {step: tree.subtree(step) for step in steps}
    in_steps = {node_id for nodes in below.values() for node_id in nodes}
    alongside = sorted(home - in_steps - {skill.id, discipline})
    stopped = {exception.directive for exception in _exceptions_of(skill)}
    step_ids = set(steps)
    held_by_steps = [
        entry for step in steps for entry in applied.get(step, ()) if entry.holder in step_ids
    ]
    first = _unique(
        [
            *applied.get(skill.id, ()),
            *applied.get(discipline, ()),
            *(entry for node_id in alongside for entry in applied.get(node_id, ())),
            *held_by_steps,
        ],
        stopped,
    )
    in_skill = {entry.directive.id for entry in first}
    placed = _placement(first, home, applied, tree.exceptions([skill.id, discipline, *alongside]))
    by_step = {
        step: _placement(
            _unique(
                (entry for node_id in below[step] for entry in applied.get(node_id, ())),
                stopped | in_skill,
            ),
            home,
            applied,
            tree.exceptions(below[step]),
        )
        for step in steps
    }
    return FlowPlacement(placed, by_step)
