from dataclasses import dataclass
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
    Status,
    TaxonomyNode,
)
from engine.layout import POLICY_FOLDER

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

    from engine.compiler.graph import CompiledGraph
    from engine.directives import AppliedDirective
    from engine.generated.metamodel import (
        CompiledResult,
        DirectiveException,
        Node,
    )
    from engine.parser.result import Script


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


@dataclass(frozen=True, slots=True)
class PointerLine:
    mechanism: LoadMechanism
    target: NodeLink
    trigger: str | None


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


def build_view(compiled: CompiledGraph) -> RuntimeView:
    root = compiled.graph.root
    others: list[Node] = list(compiled.graph.nodes)
    nodes = [root, *others]
    links = {node.id: NodeLink(node.id, node.title, compiled.paths[node.id]) for node in nodes}
    tool_loaded = _tool_loaded_targets(nodes)

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
        references=tuple(line for line in root_lines if line.target.id not in named),
        skills=tuple(view_of(node) for node in others if isinstance(node, Skill)),
        rules=tuple(view_of(node, rule_paths(node)) for node in others if node.id in tool_loaded),
        pages=tuple(
            view_of(node)
            for node in others
            if node.id not in tool_loaded and not isinstance(node, Skill)
        ),
    )
