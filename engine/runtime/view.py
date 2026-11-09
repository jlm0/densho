from dataclasses import dataclass, replace
from enum import StrEnum
from typing import TYPE_CHECKING

from engine.generated.metamodel import (
    AlwaysPointer,
    Domain,
    Invocation,
    KnowledgeNode,
    PathPointer,
    Root,
    Skill,
    SkillPointer,
    SkillType,
    Status,
    TaxonomyNode,
)
from engine.layout import POLICY_FOLDER
from engine.tree_copies import Tree, flow_placement, skill_placement

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

    from engine.compiler.graph import CompiledGraph
    from engine.directives import AppliedDirective
    from engine.generated.metamodel import (
        CompiledResult,
        Directive,
        DirectiveException,
        Node,
    )
    from engine.parser.result import Script, StepCopies, StepFile
    from engine.tree_copies import Placement

STEP_FILE_DIRECTIVES = 5
CORRECT_OUTPUT = (
    "Before you start the next step, correct each part of the output that breaks a directive."
)


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
class BranchView:
    condition: str
    directives: tuple[DirectiveLine, ...]


@dataclass(frozen=True, slots=True)
class CopyStepView:
    link: NodeLink
    skill: NodeLink
    skill_type: str
    number: int
    total: int
    has_file: bool
    pages: tuple[PointerLine, ...]
    names_directives: bool
    directives: tuple[DirectiveLine, ...]
    branches: tuple[BranchView, ...]
    missing_rules: tuple[str, ...]
    procedure: str
    output: str
    following: int | None


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
    copy_steps: tuple[CopyStepView, ...] = ()
    skill_type: str | None = None
    run_lines: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class DirectiveCounts:
    in_force: int
    other_directives: int
    other_exceptions: int


@dataclass(frozen=True, slots=True)
class RootSections:
    each_task: tuple[DirectiveLine, ...]
    use_a_skill: tuple[DirectiveLine, ...]
    create_a_rule: tuple[DirectiveLine, ...]


@dataclass(frozen=True, slots=True)
class RuntimeView:
    result: CompiledResult
    counts: DirectiveCounts
    root: NodeView
    sections: RootSections
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


def _line(directive: Directive) -> DirectiveLine:
    return DirectiveLine(directive.id, directive.text, Status(directive.status).value)


def _lines(names: Sequence[str], directives: Mapping[str, Directive]) -> tuple[DirectiveLine, ...]:
    return tuple(_line(directives[name]) for name in names if name in directives)


def _root_sections(
    root: Node, applied: Sequence[AppliedDirective], directives: Mapping[str, Directive]
) -> RootSections:
    use_a_skill = (root.use_a_skill or []) if isinstance(root, Root) else []
    create_a_rule = (root.create_a_rule or []) if isinstance(root, Root) else []
    named = {*use_a_skill, *create_a_rule}
    return RootSections(
        tuple(_line(entry.directive) for entry in applied if entry.directive.id not in named),
        _lines(use_a_skill, directives),
        _lines(create_a_rule, directives),
    )


def run_lines(steps: Sequence[CopyStepView], *, lens: bool) -> tuple[str, ...]:
    several = len(steps) > 1
    place = "the step" if several else "the skill"
    act = "check the work against" if lens else "follow"
    candidates = (
        (several, "Run the steps in their order."),
        (several, "If the output of a step exists already, skip the step."),
        (any(step.has_file for step in steps), "If a step has a step file, read the step file."),
        (
            any(step.names_directives for step in steps),
            f"{act.capitalize()} each directive of {place}.",
        ),
        (
            any(step.branches for step in steps),
            f"If a branch heading matches the work, {act} each directive under it.",
        ),
        (
            any(step.pages for step in steps),
            "If you need the definition or the notes of a page, read the page.",
        ),
        (
            several and not lens,
            "After each step, check its output against each directive of the step.",
        ),
        (
            several and not lens,
            CORRECT_OUTPUT,
        ),
    )
    return tuple(line for wanted, line in candidates if wanted)


def _has_step_file(copies: StepCopies, total: int) -> bool:
    return total > 1 and (bool(copies.branches) or len(copies.copied()) > STEP_FILE_DIRECTIVES)


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

    directives = compiled.directives

    def copy_step_views(skill: Skill) -> tuple[CopyStepView, ...]:
        sources = {step.id: step for step in compiled.step_files.get(skill.id, ())}
        order = [sources[step] for step in skill.steps or [] if step in sources]
        views: list[CopyStepView] = []
        for index, step in enumerate(order):
            copies = step.copies
            if copies is None:
                continue
            branches = (
                BranchView(branch.condition, _lines(branch.directives, directives))
                for branch in copies.branches
            )
            views.append(
                CopyStepView(
                    link=NodeLink(step.id, copies.title, links[skill.id].path),
                    skill=links[skill.id],
                    skill_type=SkillType(skill.skill_type).value,
                    number=index + 1,
                    total=len(order),
                    has_file=_has_step_file(copies, len(order)),
                    pages=tuple(
                        PointerLine(LoadMechanism.TEXT, links[page.target], page.trigger)
                        for page in copies.pages
                        if page.target in links
                    ),
                    names_directives=bool(copies.directives),
                    directives=_lines(copies.directives, directives),
                    branches=tuple(branch for branch in branches if branch.directives),
                    missing_rules=copies.missing_rules,
                    procedure=step.section("Procedure"),
                    output=step.section("Output"),
                    following=index + 2 if index + 1 < len(order) else None,
                )
            )
        return tuple(views)

    def skill_view(node: Skill) -> NodeView:
        base = replace(view_of(node), skill_type=SkillType(node.skill_type).value)
        sources = compiled.step_files.get(node.id, ())
        if sources and all(step.copies is not None for step in sources):
            copy_steps = copy_step_views(node)
            return replace(
                base,
                groups=(),
                exceptions=(),
                pointers=_pointers(node, links),
                copy_steps=copy_steps,
                run_lines=run_lines(copy_steps, lens=node.skill_type == SkillType.lens),
            )
        if node.skill_type == SkillType.task:
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
        sections=_root_sections(root, compiled.applied[root.id], directives),
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
