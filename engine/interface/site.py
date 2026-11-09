import base64
import hashlib
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING, cast

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from engine.compiler import checked_tree, compile_items
from engine.compiler.output import NOTICES
from engine.generated.metamodel import (
    CompiledResult,
    Concept,
    Directive,
    Discipline,
    Domain,
    PathPointer,
    PracticeArea,
    Root,
    Skill,
    Status,
    TaxonomyNode,
)
from engine.governance.entities import (
    DIRECTIVE,
    EXCEPTION,
    NODE,
    governed_entities,
)
from engine.graph.references import EDGE_FIELDS, exceptions_of
from engine.interface.accept import command_prefix, entity_name
from engine.interface.markdown import render_block, render_inline
from engine.interface.tree import (
    TreeRow,
    children_by_broader,
    subtree_ids,
    tree_rows,
)
from engine.parser.generated import MARKER
from engine.runtime import build_view, pointer_mechanism, render_files
from engine.runtime.claude_code import state_sentence
from engine.runtime.files import apply_files

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping, Sequence

    from engine.compiler import CompiledGraph
    from engine.directives import AppliedDirective
    from engine.generated.metamodel import DirectiveException, Node
    from engine.governance.entities import Entity, EntityKey
    from engine.parser.result import ParsedNode, Problem

VIEW_FOLDER = PurePosixPath("build/view")
VIEW_CODES = ("not-generated", "write")
INDEX_PAGE = PurePosixPath("index.html")
REVIEW_PAGE = PurePosixPath("review.html")
NODE_FOLDER = PurePosixPath("nodes")
REACH_LISTED = 8
OPEN_TREE_DEPTH = 2
TEMPLATES = Path(__file__).parent / "templates"
STYLE = (TEMPLATES / "style.css").read_text(encoding="utf-8")
STYLE_DIGEST = base64.b64encode(hashlib.sha256(STYLE.encode("utf-8")).digest()).decode("ascii")
CONTENT_POLICY = (
    f"default-src 'none'; style-src 'sha256-{STYLE_DIGEST}'; base-uri 'none'; form-action 'none'"
)
KIND_LABELS: Mapping[type, str] = {
    Root: "Root",
    Domain: "Domain",
    Discipline: "Discipline",
    PracticeArea: "Practice area",
    Concept: "Concept",
    Skill: "Skill",
}
DIRECTIVE_EDGES = ("also_attached_to", "refines", "conflicts_with")
DIRECTIVE_TARGET_FIELDS = frozenset(
    {"applies", "use_a_skill", "create_a_rule", "refines", "conflicts_with"}
)
FIELD_LABELS = {
    "broader": "Broader",
    "related": "Related",
    "informs": "Informs",
    "depends_on": "Depends on",
    "governs": "Governs",
    "implements": "Implements",
    "uses": "Uses",
    "applies": "Applies",
    "also_attached_to": "Also attached to",
    "refines": "Refines",
    "conflicts_with": "Conflicts with",
    "use_a_skill": "Use a skill",
    "create_a_rule": "Create a rule",
}

_ENVIRONMENT = Environment(
    loader=FileSystemLoader(TEMPLATES),
    autoescape=True,
    undefined=StrictUndefined,
    trim_blocks=True,
    lstrip_blocks=True,
    keep_trailing_newline=True,
)
_ENVIRONMENT.filters["block"] = render_block
_ENVIRONMENT.filters["inline"] = render_inline


@dataclass(frozen=True, slots=True)
class Target:
    label: str
    href: str


@dataclass(frozen=True, slots=True)
class EdgeRow:
    label: str
    targets: tuple[Target, ...]


@dataclass(frozen=True, slots=True)
class NodeLink:
    target: Target
    id: str
    kind: str
    status: str


@dataclass(frozen=True, slots=True)
class DirectiveEntry:
    id: str
    text: str
    status: str
    scope: str
    origin: str
    sources: tuple[str, ...]
    edges: tuple[EdgeRow, ...]


@dataclass(frozen=True, slots=True)
class ExceptionEntry:
    directive: Target
    reason: str
    status: str


@dataclass(frozen=True, slots=True)
class PointerEntry:
    mechanism: str
    target: Target
    trigger: str | None
    paths: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class AppliedEntry:
    id: str
    text: str
    status: str
    scope: str
    holder: Target
    route: tuple[Target, ...]


@dataclass(frozen=True, slots=True)
class NodePage:
    link: NodeLink
    origin: str
    knowledge_type: str | None
    path: str
    definition: str | None
    description: str | None
    steps: tuple[str, ...]
    body: str | None
    sources: tuple[str, ...]
    trail: tuple[Target, ...]
    in_force: tuple[AppliedEntry, ...]
    on_acceptance: tuple[AppliedEntry, ...]
    stopped: tuple[Target, ...]
    directives: tuple[DirectiveEntry, ...]
    exceptions: tuple[ExceptionEntry, ...]
    deprecated: tuple[DirectiveEntry, ...]
    pointers: tuple[PointerEntry, ...]
    children: tuple[NodeLink, ...]
    edges: tuple[EdgeRow, ...]
    files: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class Reached:
    node_count: int
    nodes: tuple[Target, ...]
    file_count: int
    files: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class QueueDirective:
    entry: DirectiveEntry
    location: str
    reached: Reached


@dataclass(frozen=True, slots=True)
class QueueException:
    entry: ExceptionEntry
    location: str
    files: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class QueueGroup:
    page: NodePage
    node_location: str | None
    directives: tuple[QueueDirective, ...]
    exceptions: tuple[QueueException, ...]
    names: tuple[str, ...]
    branch_id: str | None
    branch_count: int


@dataclass(frozen=True, slots=True)
class BranchRow:
    link: NodeLink
    count: int


@dataclass(frozen=True, slots=True)
class TreeEntry:
    row: TreeRow
    link: NodeLink
    directive_count: int
    open: bool


@dataclass(frozen=True, slots=True)
class SkillEntry:
    link: NodeLink
    title: str
    description: str | None


@dataclass(frozen=True, slots=True)
class ViewReport:
    files: tuple[PurePosixPath, ...]
    written: tuple[PurePosixPath, ...]
    removed: tuple[PurePosixPath, ...]
    notes: list[str]
    problems: list[Problem]


def _page_file(node_id: str) -> PurePosixPath:
    return NODE_FOLDER / f"{node_id}.html"


def _node_href(node_id: str) -> str:
    return _page_file(node_id).name


def _directive_anchor(directive_id: str) -> str:
    return f"directive-{directive_id}"


@dataclass(frozen=True, slots=True)
class _Graph:
    nodes: Mapping[str, Node]
    in_force: CompiledGraph
    proposals: CompiledGraph
    items: Mapping[str, ParsedNode]
    entities: Mapping[EntityKey, Entity]
    children: Mapping[str, Sequence[str]]
    holders: Mapping[str, str]
    files_by_node: Mapping[str, tuple[str, ...]]
    repository: Path

    def node_target(self, node_id: str) -> Target:
        return Target(self.nodes[node_id].title, _node_href(node_id))

    def directive_target(self, directive_id: str) -> Target:
        anchor = _directive_anchor(directive_id)
        return Target(directive_id, f"{_node_href(self.holders[directive_id])}#{anchor}")

    def field_target(self, field: str, target: str) -> Target:
        if field in DIRECTIVE_TARGET_FIELDS:
            return self.directive_target(target)
        return self.node_target(target)

    def link(self, node_id: str) -> NodeLink:
        node = self.nodes[node_id]
        return NodeLink(
            self.node_target(node_id),
            node_id,
            KIND_LABELS[type(node)],
            Status(node.status).value,
        )

    def location(self, entity: Entity) -> str:
        relative = entity.path.relative_to(self.repository).as_posix()
        return f"{relative}:{entity.line}"


def _edge_rows(entity: object, fields: Iterable[str], graph: _Graph) -> tuple[EdgeRow, ...]:
    rows: list[EdgeRow] = []
    for field in fields:
        targets = cast("list[str] | None", getattr(entity, field, None)) or []
        if targets:
            rows.append(
                EdgeRow(
                    FIELD_LABELS[field],
                    tuple(graph.field_target(field, target) for target in targets),
                )
            )
    return tuple(rows)


def _directive_entry(directive: Directive, graph: _Graph) -> DirectiveEntry:
    return DirectiveEntry(
        directive.id,
        directive.text,
        Status(directive.status).value,
        str(directive.scope),
        str(directive.origin),
        tuple(directive.sources or ()),
        _edge_rows(directive, DIRECTIVE_EDGES, graph),
    )


def _applied_entry(entry: AppliedDirective, graph: _Graph) -> AppliedEntry:
    directive = entry.directive
    return AppliedEntry(
        directive.id,
        directive.text,
        Status(directive.status).value,
        str(directive.scope),
        graph.node_target(entry.holder),
        tuple(graph.node_target(step) for step in entry.route),
    )


def _trail(node_id: str, graph: _Graph) -> tuple[Target, ...]:
    trail: list[Target] = []
    current = node_id
    while True:
        parents = cast("list[str] | None", getattr(graph.nodes[current], "broader", None))
        if not parents:
            break
        current = parents[0]
        trail.append(graph.node_target(current))
    root_id = graph.in_force.graph.root.id
    if root_id not in {node_id, current}:
        trail.append(graph.node_target(root_id))
    return tuple(reversed(trail))


def _pointers(node: Node, graph: _Graph) -> tuple[PointerEntry, ...]:
    return tuple(
        PointerEntry(
            pointer_mechanism(pointer).value,
            graph.node_target(pointer.target),
            pointer.trigger,
            tuple(pointer.paths) if isinstance(pointer, PathPointer) else (),
        )
        for pointer in node.pointers or []
    )


def _exception_entry(exception: DirectiveException, graph: _Graph) -> ExceptionEntry:
    return ExceptionEntry(
        graph.directive_target(exception.directive),
        exception.reason,
        Status(exception.status).value,
    )


def _deprecated_entries(node_id: str, graph: _Graph) -> tuple[DirectiveEntry, ...]:
    return tuple(
        _directive_entry(directive, graph)
        for directive in graph.items[node_id].node.directives or []
        if directive.status == Status.deprecated
    )


def _node_page(node_id: str, graph: _Graph) -> NodePage:
    node = graph.nodes[node_id]
    in_force = graph.in_force.applied[node_id]
    projected = graph.proposals.applied[node_id]
    in_force_ids = {entry.directive.id for entry in in_force}
    projected_ids = {entry.directive.id for entry in projected}
    return NodePage(
        link=graph.link(node_id),
        origin=str(node.origin),
        knowledge_type=cast("str | None", getattr(node, "knowledge_type", None)),
        path=graph.proposals.paths[node_id],
        definition=node.definition if isinstance(node, TaxonomyNode) else None,
        description=node.description if isinstance(node, Skill) else None,
        steps=tuple((node.steps or []) if isinstance(node, Skill) else ()),
        body=node.body,
        sources=tuple(node.sources or ()),
        trail=_trail(node_id, graph),
        in_force=tuple(_applied_entry(entry, graph) for entry in in_force),
        on_acceptance=tuple(
            _applied_entry(entry, graph)
            for entry in projected
            if entry.directive.id not in in_force_ids
        ),
        stopped=tuple(
            graph.directive_target(directive_id)
            for directive_id in sorted(in_force_ids - projected_ids)
        ),
        directives=tuple(_directive_entry(directive, graph) for directive in node.directives or []),
        exceptions=tuple(
            _exception_entry(exception, graph)
            for exception in exceptions_of(graph.items[node_id])
            if exception.status != Status.rejected
        ),
        deprecated=_deprecated_entries(node_id, graph),
        pointers=_pointers(node, graph),
        children=tuple(graph.link(child) for child in graph.children.get(node_id, ())),
        edges=_edge_rows(node, EDGE_FIELDS, graph),
        files=graph.files_by_node[node_id],
    )


def _reach_by_directive(compiled: CompiledGraph) -> dict[str, list[str]]:
    reach: dict[str, list[str]] = {}
    for node_id, entries in compiled.applied.items():
        for entry in entries:
            reach.setdefault(entry.directive.id, []).append(node_id)
    return reach


def _reached(node_ids: Sequence[str], graph: _Graph) -> Reached:
    files = sorted({name for node_id in node_ids for name in graph.files_by_node[node_id]})
    return Reached(
        len(node_ids),
        tuple(graph.node_target(node_id) for node_id in node_ids[:REACH_LISTED]),
        len(files),
        tuple(files[:REACH_LISTED]),
    )


def _queue_directive(
    directive: Directive, graph: _Graph, reach: Mapping[str, Sequence[str]]
) -> QueueDirective:
    entity = graph.entities[DIRECTIVE, directive.id]
    return QueueDirective(
        _directive_entry(directive, graph),
        graph.location(entity),
        _reached(reach.get(directive.id, ()), graph),
    )


def _queue_exception(node_id: str, exception: DirectiveException, graph: _Graph) -> QueueException:
    entity = graph.entities[EXCEPTION, node_id, exception.directive]
    return QueueException(
        _exception_entry(exception, graph), graph.location(entity), graph.files_by_node[node_id]
    )


def _queue_group(
    page: NodePage, graph: _Graph, reach: Mapping[str, Sequence[str]]
) -> QueueGroup | None:
    node_id = page.link.id
    node_entity = graph.entities[NODE, node_id]
    item = graph.items[node_id]
    directives = [
        directive for directive in item.node.directives or [] if directive.status == Status.proposed
    ]
    exceptions = [
        exception for exception in exceptions_of(item) if exception.status == Status.proposed
    ]
    node_proposed = node_entity.status == Status.proposed
    if not node_proposed and not directives and not exceptions:
        return None
    names = [
        *([node_id] if node_proposed else []),
        *(directive.id for directive in directives),
        *(entity_name(graph.entities[EXCEPTION, node_id, entry.directive]) for entry in exceptions),
    ]
    return QueueGroup(
        page,
        graph.location(node_entity) if node_proposed else None,
        tuple(_queue_directive(directive, graph, reach) for directive in directives),
        tuple(_queue_exception(node_id, exception, graph) for exception in exceptions),
        tuple(names),
        node_id if graph.children.get(node_id) else None,
        _branch_count(node_id, graph),
    )


def _branch_count(node_id: str, graph: _Graph) -> int:
    branch = subtree_ids(node_id, graph.children)
    return sum(
        entity.status == Status.proposed and entity.holder in branch
        for entity in graph.entities.values()
    )


def _files_by_node(compiled: CompiledGraph) -> dict[str, tuple[str, ...]]:
    rendered = render_files(build_view(compiled))
    by_path: dict[str, list[str]] = {}
    for entry in rendered:
        by_path.setdefault(entry.node_path, []).append(entry.path.as_posix())
    return {
        node_id: tuple(sorted(by_path.get(path, ()))) for node_id, path in compiled.paths.items()
    }


def _graph(items: Sequence[ParsedNode], repository: Path) -> _Graph:
    in_force = compile_items(items, repository)
    proposals = compile_items(items, repository, proposals=True)
    nodes: dict[str, Node] = {
        node.id: node for node in (proposals.graph.root, *proposals.graph.nodes)
    }
    holders = {
        directive.id: item.node.id for item in items for directive in item.node.directives or []
    }
    return _Graph(
        nodes=nodes,
        in_force=in_force,
        proposals=proposals,
        items={item.node.id: item for item in items},
        entities=governed_entities(items),
        children=children_by_broader(
            [item for item in items if item.node.status != Status.rejected]
        ),
        holders=holders,
        files_by_node=_files_by_node(in_force),
        repository=repository,
    )


def _waiting_sentence(pending: Sequence[Entity]) -> str:
    parts = [
        f"{count} {noun}" if count == 1 else f"{count} {noun}s"
        for noun, count in (
            ("node", sum(entity.kind == NODE for entity in pending)),
            ("directive", sum(entity.kind == DIRECTIVE for entity in pending)),
            ("exception", sum(entity.kind == EXCEPTION for entity in pending)),
        )
    ]
    verb = "entity waits" if len(pending) == 1 else "entities wait"
    return f"{len(pending)} {verb} for review: {parts[0]}, {parts[1]}, and {parts[2]}."


def _render(template: str, up: str, base: str, **values: object) -> bytes:
    text = _ENVIRONMENT.get_template(template).render(
        marker=MARKER,
        policy=CONTENT_POLICY,
        style=STYLE,
        up=up,
        base=base,
        **values,
    )
    return text.encode("utf-8")


def render_site(items: Sequence[ParsedNode], repository: Path) -> dict[PurePosixPath, bytes]:
    graph = _graph(items, repository)
    root_id = graph.in_force.graph.root.id
    skills = sorted(node.id for node in graph.nodes.values() if isinstance(node, Skill))
    rows = tree_rows(root_id, graph.children, left_out=skills)
    pages = {node_id: _node_page(node_id, graph) for node_id in graph.nodes}
    pending = [entity for entity in graph.entities.values() if entity.status == Status.proposed]
    reach = _reach_by_directive(graph.proposals)
    order = [*(row.node_id for row in rows if not row.repeated), *skills]
    groups = [
        group
        for node_id in order
        if (group := _queue_group(pages[node_id], graph, reach)) is not None
    ]
    command = command_prefix(repository)
    state = state_sentence(build_view(graph.in_force).counts)
    waiting = _waiting_sentence(pending)
    title = graph.nodes[root_id].title
    tree = [
        TreeEntry(
            row,
            graph.link(row.node_id),
            len(graph.nodes[row.node_id].directives or []),
            row.depth < OPEN_TREE_DEPTH,
        )
        for row in rows
    ]
    skill_entries = [
        SkillEntry(
            graph.link(skill),
            graph.nodes[skill].title,
            cast("Skill", graph.nodes[skill]).description,
        )
        for skill in skills
    ]
    branches = [
        BranchRow(graph.link(child), _branch_count(child, graph))
        for child in graph.children.get(root_id, ())
        if child not in skills
    ]
    files: dict[PurePosixPath, bytes] = {
        INDEX_PAGE: _render(
            "index.html.jinja",
            "",
            "nodes/",
            title=title,
            state=state,
            pending=len(pending),
            waiting=waiting,
            tree=tree,
            skills=skill_entries,
            root=graph.link(root_id),
        ),
        REVIEW_PAGE: _render(
            "review.html.jinja",
            "",
            "nodes/",
            title=title,
            state=state,
            pending=len(pending),
            waiting=waiting,
            notice=NOTICES[CompiledResult.proposals],
            command=command,
            groups=groups,
            branches=branches,
            root=graph.link(root_id),
            reach_listed=REACH_LISTED,
        ),
    }
    for node_id, page in pages.items():
        files[_page_file(node_id)] = _render(
            "node.html.jinja", "../", "", title=title, page=page, command=command
        )
    return files


def write_view(repository: Path) -> ViewReport:
    checked = checked_tree(repository)
    folder = repository / VIEW_FOLDER
    if checked.problems:
        applied = apply_files(repository, {}, folder.rglob("*.html"))
        return ViewReport(
            (),
            applied.written,
            applied.removed,
            checked.notes,
            [*checked.problems, *applied.problems],
        )
    site = render_site(checked.items, repository)
    files = {VIEW_FOLDER / path: data for path, data in site.items()}
    applied = apply_files(repository, files, folder.rglob("*.html"))
    return ViewReport(
        tuple(files), applied.written, applied.removed, checked.notes, applied.problems
    )
