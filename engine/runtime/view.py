from dataclasses import dataclass, replace
from enum import StrEnum
from typing import TYPE_CHECKING

from engine.generated.metamodel import (
    AlwaysPointer,
    Domain,
    Invocation,
    KnowledgeNode,
    PathPointer,
    Skill,
    SkillPointer,
    SkillType,
    Status,
    TaxonomyNode,
)
from engine.layout import POLICY_FOLDER
from engine.runtime.placement import Tree, flow_placement, skill_placement

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

    from engine.compiler.graph import CompiledGraph
    from engine.directives import AppliedDirective
    from engine.generated.metamodel import (
        CompiledResult,
        DirectiveException,
        Node,
    )
    from engine.parser.result import Script, StepFile
    from engine.runtime.placement import Placement


class LoadMechanism(StrEnum):
    ALWAYS = "always"
    PATH = "path"
    SKILL = "skill"
    TEXT = "text"


@dataclass(frozen=True, slots=True)
class NodeLink:
    id: str
    title: str
    path: str


@dataclass(frozen=True, slots=True)
class DirectiveLine:
    id: str
    text: str
    status: str


@dataclass(frozen=True, slots=True)
class DirectiveGroup:
    holder: NodeLink
    directives: tuple[DirectiveLine, ...]


@dataclass(frozen=True, slots=True)
class ExceptionLine:
    directive: str
    reason: str
    status: str
    holder: NodeLink | None = None


@dataclass(frozen=True, slots=True)
class ReadLine:
    holder: NodeLink
    directives: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class PointerLine:
    mechanism: LoadMechanism
    target: NodeLink
    trigger: str | None


@dataclass(frozen=True, slots=True)
class StepView:
    link: NodeLink
    flow: str
    number: int
    total: int
    groups: tuple[DirectiveGroup, ...]
    exceptions: tuple[ExceptionLine, ...]
    reads: tuple[ReadLine, ...]
    source: StepFile
    comes_from: tuple[NodeLink, ...]
    goes_to: tuple[NodeLink, ...]
    following: NodeLink | None
    pointers: tuple[PointerLine, ...]


@dataclass(frozen=True, slots=True)
class NodeView:
    link: NodeLink
    groups: tuple[DirectiveGroup, ...]
    exceptions: tuple[ExceptionLine, ...]
    definition: str | None
    body: str | None
    pointers: tuple[PointerLine, ...]
    description: str | None = None
    paths: tuple[str, ...] = ()
    invocation: str | None = None
    scripts: tuple[Script, ...] = ()
    comes_from: tuple[NodeLink, ...] = ()
    goes_to: tuple[NodeLink, ...] = ()
    reads: tuple[ReadLine, ...] = ()
    steps: tuple[StepView, ...] = ()


@dataclass(frozen=True, slots=True)
class DirectiveCounts:
    in_force: int
    other_directives: int
    other_exceptions: int


@dataclass(frozen=True, slots=True)
class RuntimeView:
    result: CompiledResult
    counts: DirectiveCounts
    root: NodeView
    domains: tuple[PointerLine, ...]
    governance: tuple[PointerLine, ...]
    references: tuple[PointerLine, ...]
    rows: tuple[PointerLine, ...]
    skills: tuple[NodeView, ...]
    rules: tuple[NodeView, ...]
    pages: tuple[NodeView, ...]


def pointer_mechanism(pointer: object) -> LoadMechanism:
    if isinstance(pointer, AlwaysPointer):
        return LoadMechanism.ALWAYS
    if isinstance(pointer, PathPointer):
        return LoadMechanism.PATH
    if isinstance(pointer, SkillPointer):
        return LoadMechanism.SKILL
    return LoadMechanism.TEXT


def _groups(
    entries: Sequence[AppliedDirective], links: Mapping[str, NodeLink]
) -> tuple[DirectiveGroup, ...]:
    grouped: dict[str, list[DirectiveLine]] = {}
    for entry in entries:
        directive = entry.directive
        line = DirectiveLine(directive.id, directive.text, Status(directive.status).value)
        grouped.setdefault(entry.holder, []).append(line)
    return tuple(DirectiveGroup(links[holder], tuple(lines)) for holder, lines in grouped.items())


def _pointers(node: Node, links: Mapping[str, NodeLink]) -> tuple[PointerLine, ...]:
    return tuple(
        PointerLine(pointer_mechanism(pointer), links[pointer.target], pointer.trigger)
        for pointer in node.pointers or []
    )


def _skill_pointers(node: Node, links: Mapping[str, NodeLink]) -> tuple[PointerLine, ...]:
    lines = _pointers(node, links)
    if not isinstance(node, Skill):
        return lines
    pointed = {line.target.id for line in lines}
    unpointed = [used for used in node.uses or [] if used not in pointed]
    return (*lines, *(PointerLine(LoadMechanism.TEXT, links[used], None) for used in unpointed))


def _tool_loaded_targets(nodes: Sequence[Node]) -> dict[str, set[str]]:
    paths: dict[str, set[str]] = {}
    always: set[str] = set()
    for node in nodes:
        for pointer in node.pointers or []:
            if isinstance(pointer, AlwaysPointer):
                always.add(pointer.target)
            elif isinstance(pointer, PathPointer):
                paths.setdefault(pointer.target, set()).update(pointer.paths)
    return {target: set() if target in always else paths[target] for target in {*paths, *always}}


def _entry_lines(
    domains: Sequence[Node], root_lines: Sequence[PointerLine], links: Mapping[str, NodeLink]
) -> list[PointerLine]:
    lines: list[PointerLine] = []
    for domain in domains:
        found = [line for line in root_lines if line.target.id == domain.id]
        lines += found or [PointerLine(LoadMechanism.TEXT, links[domain.id], None)]
    return lines


def _informs(node: Node) -> list[str]:
    return (node.informs or []) if isinstance(node, TaxonomyNode) else []


def _informed_by(nodes: Sequence[Node]) -> dict[str, list[str]]:
    sources: dict[str, list[str]] = {}
    for node in nodes:
        for target in _informs(node):
            sources.setdefault(target, []).append(node.id)
    return sources


def _exceptions_of(node: Node) -> list[DirectiveException]:
    return (node.exceptions or []) if isinstance(node, KnowledgeNode) else []


def _counts(compiled: CompiledGraph, nodes: Sequence[Node]) -> DirectiveCounts:
    directives = compiled.directives.values()
    in_force = sum(directive.status == Status.accepted for directive in directives)
    proposed_exceptions = [
        exception
        for node in nodes
        for exception in _exceptions_of(node)
        if exception.status != Status.accepted
    ]
    return DirectiveCounts(
        in_force,
        len(directives) - in_force + compiled.left_out["directives"],
        len(proposed_exceptions) + compiled.left_out["exceptions"],
    )


def _exception_lines(
    placement: Placement, skill_id: str, links: Mapping[str, NodeLink]
) -> tuple[ExceptionLine, ...]:
    return tuple(
        ExceptionLine(
            entry.directive,
            entry.reason,
            Status(entry.status).value,
            None if holder == skill_id else links[holder],
        )
        for holder, entry in placement.exceptions
    )


def _read_lines(placement: Placement, links: Mapping[str, NodeLink]) -> tuple[ReadLine, ...]:
    return tuple(ReadLine(links[holder], directives) for holder, directives in placement.reads)


def build_view(compiled: CompiledGraph) -> RuntimeView:
    root = compiled.graph.root
    others: list[Node] = list(compiled.graph.nodes)
    nodes = [root, *others]
    by_id = {node.id: node for node in nodes}
    links = {node.id: NodeLink(node.id, node.title, compiled.paths[node.id]) for node in nodes}
    tool_loaded = _tool_loaded_targets(nodes)
    informed_by = _informed_by(nodes)
    tree = Tree(nodes)

    def view_of(node: Node, paths: Sequence[str] = ()) -> NodeView:
        return NodeView(
            links[node.id],
            _groups(compiled.applied[node.id], links),
            tuple(
                ExceptionLine(entry.directive, entry.reason, Status(entry.status).value)
                for entry in _exceptions_of(node)
            ),
            node.definition if isinstance(node, TaxonomyNode) else None,
            node.body,
            _skill_pointers(node, links),
            node.description if isinstance(node, Skill) else None,
            tuple(paths),
            Invocation(node.invocation).value if isinstance(node, Skill) else None,
            compiled.scripts.get(node.id, ()),
            tuple(links[source] for source in informed_by.get(node.id, [])),
            tuple(links[target] for target in _informs(node)),
        )

    def step_views(skill: Skill, steps: Mapping[str, Placement]) -> tuple[StepView, ...]:
        sources = {step.id: step for step in compiled.step_files.get(skill.id, ())}
        order = [step for step in skill.steps or [] if step in steps and step in sources]
        return tuple(
            StepView(
                link=links[step],
                flow=skill.id,
                number=index + 1,
                total=len(order),
                groups=_groups(steps[step].copies, links),
                exceptions=_exception_lines(steps[step], skill.id, links),
                reads=_read_lines(steps[step], links),
                source=sources[step],
                comes_from=tuple(links[source] for source in informed_by.get(step, [])),
                goes_to=tuple(links[target] for target in _informs(by_id[step])),
                following=links[order[index + 1]] if index + 1 < len(order) else None,
                pointers=_pointers(by_id[step], links),
            )
            for index, step in enumerate(order)
        )

    def skill_view(node: Skill) -> NodeView:
        base = view_of(node)
        if node.skill_type == SkillType.flow:
            flow = flow_placement(node, tree, compiled.applied)
            placement = flow.skill
            steps = step_views(node, flow.steps)
            pointers = _pointers(node, links)
        else:
            placement = skill_placement(node, tree, compiled.applied)
            steps = ()
            pointers = base.pointers
        return replace(
            base,
            pointers=pointers,
            groups=_groups(placement.copies, links),
            exceptions=_exception_lines(placement, node.id, links),
            reads=_read_lines(placement, links),
            steps=steps,
        )

    def rule_paths(node: Node) -> list[str]:
        patterns = tool_loaded[node.id]
        return sorted({*patterns, compiled.paths[node.id]}) if patterns else []

    domains = [node for node in others if isinstance(node, Domain)]
    policy_prefix = f"{POLICY_FOLDER}/"
    policies = [node for node in domains if compiled.paths[node.id].startswith(policy_prefix)]
    subjects = [node for node in domains if not compiled.paths[node.id].startswith(policy_prefix)]
    root_lines = _pointers(root, links)
    named = {node.id for node in domains}
    return RuntimeView(
        result=compiled.result,
        counts=_counts(compiled, nodes),
        root=view_of(root),
        domains=tuple(_entry_lines(subjects, root_lines, links)),
        governance=(
            *_entry_lines(policies, root_lines, links),
            *(line for policy in policies for line in _pointers(policy, links)),
        ),
        references=tuple(
            line
            for line in root_lines
            if line.target.id not in named and line.mechanism != LoadMechanism.SKILL
        ),
        rows=tuple(line for line in root_lines if line.mechanism == LoadMechanism.SKILL),
        skills=tuple(skill_view(node) for node in others if isinstance(node, Skill)),
        rules=tuple(view_of(node, rule_paths(node)) for node in others if node.id in tool_loaded),
        pages=tuple(
            view_of(node)
            for node in others
            if node.id not in tool_loaded and not isinstance(node, Skill)
        ),
    )
