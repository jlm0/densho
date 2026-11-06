from dataclasses import dataclass
from typing import TYPE_CHECKING

from engine.generated.metamodel import Basis, KnowledgeType, Origin, Root, Status
from engine.governance.base import read_base
from engine.governance.changes import CHANGE_CODES, check_changes
from engine.governance.entities import governed_entities
from engine.graph.references import (
    edge_targets,
    entity_ids,
    exceptions_of,
    problem_at,
    references_of,
)
from engine.layout import POLICY_FOLDER
from engine.parser.node import node_folders, parse_tree

if TYPE_CHECKING:
    from collections.abc import Sequence
    from pathlib import Path

    from engine.generated.metamodel import Directive, DirectiveException, Node
    from engine.governance.entities import Entity
    from engine.graph.references import Reference
    from engine.parser.result import FieldPath, ParsedNode, Problem

    type GovernedModel = Node | Directive | DirectiveException

GOVERNANCE_CODES = (
    *CHANGE_CODES,
    "template-workspace",
    "deprecated-holder",
    "deprecated-reference",
    "rejected-reason",
    "rejected-holder",
    "rejected-reference",
    "rejected-root",
    "basis",
    "policy-governs",
    "base",
)
OPEN_STATUSES = frozenset({Status.proposed, Status.accepted})
RESTING_FIELDS = frozenset(
    {"broader", "uses", "depends_on", "implements", "also_attached_to", "refines"}
)


@dataclass(frozen=True, slots=True)
class GovernanceReport:
    count: int
    notes: list[str]
    problems: list[Problem]


def _template_workspace(items: Sequence[ParsedNode]) -> list[Problem]:
    problems: list[Problem] = []
    message = "The template ships no workspace knowledge. Set origin to project."
    for item in items:
        if getattr(item.node, "knowledge_type", None) != KnowledgeType.workspace:
            continue
        if item.node.origin == Origin.template:
            problems.append(problem_at(item, ("origin",), "template-workspace", message))
        problems.extend(
            problem_at(item, ("directives", index, "origin"), "template-workspace", message)
            for index, directive in enumerate(item.node.directives or [])
            if directive.origin == Origin.template
        )
    return problems


def _deprecated_holders(items: Sequence[ParsedNode]) -> list[Problem]:
    return [
        problem_at(
            item,
            ("directives", index, "status"),
            "deprecated-holder",
            f"This node is deprecated, but {directive.id} is {directive.status}. "
            "Deprecate the directive, or move it to a live node.",
        )
        for item in items
        if item.node.status == Status.deprecated
        for index, directive in enumerate(item.node.directives or [])
        if directive.status in OPEN_STATUSES
    ]


def _source_status(reference: Reference) -> Status:
    node = reference.source.node
    match reference.field_path:
        case ("directives", int(position), *_):
            return (node.directives or [])[position].status
        case ("exceptions", int(index), *_):
            return exceptions_of(reference.source)[index].status
        case _:
            return node.status


def _rejected_source(reference: Reference) -> bool:
    return Status.rejected in {reference.source.node.status, _source_status(reference)}


def _deprecated_references(items: Sequence[ParsedNode]) -> list[Problem]:
    deprecated = {
        entity.name
        for entity in governed_entities(items).values()
        if entity.status == Status.deprecated
    }
    return [
        problem_at(
            reference.source,
            reference.field_path,
            "deprecated-reference",
            f"{reference.field} names {reference.target}, which is deprecated. Remove it.",
        )
        for item in items
        for reference in references_of(item)
        if reference.field in RESTING_FIELDS
        and reference.target in deprecated
        and _source_status(reference) != Status.deprecated
        and not _rejected_source(reference)
    ]


def _held_entities(item: ParsedNode) -> list[tuple[FieldPath, str, GovernedModel]]:
    return [
        (("status",), "node", item.node),
        *(
            (("directives", index, "status"), "directive", directive)
            for index, directive in enumerate(item.node.directives or [])
        ),
        *(
            (("exceptions", index, "status"), "exception", exception)
            for index, exception in enumerate(exceptions_of(item))
        ),
    ]


def _rejection_reasons(items: Sequence[ParsedNode]) -> list[Problem]:
    return [
        problem_at(
            item,
            field_path,
            "rejected-reason",
            f"This {label} is rejected. Add rejection_reason with the reason of the person.",
        )
        for item in items
        for field_path, label, entity in _held_entities(item)
        if entity.status == Status.rejected and not entity.rejection_reason
    ]


def _rejected_holders(items: Sequence[ParsedNode]) -> list[Problem]:
    problems: list[Problem] = []
    for item in items:
        if item.node.status != Status.rejected:
            continue
        if isinstance(item.node, Root):
            message = "The root holds the graph, so it cannot be rejected. Set it to proposed."
            problems.append(problem_at(item, ("status",), "rejected-root", message))
        problems.extend(
            problem_at(
                item,
                field_path,
                "rejected-holder",
                f"This node is rejected, but this {label} is {entity.status}. "
                f"Reject the {label}, or move it to a live node.",
            )
            for field_path, label, entity in _held_entities(item)[1:]
            if entity.status in OPEN_STATUSES
        )
    return problems


def _rejected_references(items: Sequence[ParsedNode]) -> list[Problem]:
    rejected = {
        entity_id
        for item in items
        for entity_id, field_path in entity_ids(item)
        if _entity_status(item, field_path) == Status.rejected
    }
    return [
        problem_at(
            reference.source,
            reference.field_path,
            "rejected-reference",
            f"{reference.field} names {reference.target}, which is rejected. Remove it.",
        )
        for item in items
        for reference in references_of(item)
        if reference.target in rejected and not _rejected_source(reference)
    ]


def _entity_status(item: ParsedNode, field_path: FieldPath) -> Status:
    match field_path:
        case ("directives", int(position)):
            return (item.node.directives or [])[position].status
        case _:
            return item.node.status


def _basis_problems(items: Sequence[ParsedNode]) -> list[Problem]:
    message = "This directive names no source. Set basis to judgment, or add a source."
    return [
        problem_at(item, ("directives", index, "basis"), "basis", message)
        for item in items
        for index, directive in enumerate(item.node.directives or [])
        if not directive.sources and directive.basis != Basis.judgment
    ]


def _policy_problems(items: Sequence[ParsedNode], repository: Path) -> list[Problem]:
    policies = [item for item in items if item.path.is_relative_to(repository / POLICY_FOLDER)]
    governed = {target for item in policies for target in edge_targets(item, "governs")}
    problems: list[Problem] = []
    for item in policies:
        if not edge_targets(item, "governs"):
            message = "A policy names what it sets rules for. Add governs."
            problems.append(problem_at(item, ("id",), "policy-governs", message))
        if item.node.id not in governed:
            message = "No policy governs this policy. Add it to governs on a policy."
            problems.append(problem_at(item, ("id",), "policy-governs", message))
    return problems


def check_items(items: Sequence[ParsedNode], repository: Path) -> list[Problem]:
    return [
        *_template_workspace(items),
        *_deprecated_holders(items),
        *_deprecated_references(items),
        *_rejection_reasons(items),
        *_rejected_holders(items),
        *_rejected_references(items),
        *_basis_problems(items),
        *_policy_problems(items, repository),
    ]


def check_governance(
    repository: Path, items: Sequence[ParsedNode] | None = None
) -> GovernanceReport:
    if items is None:
        items, problems = parse_tree(node_folders(repository))
        if problems:
            return GovernanceReport(0, [], problems)
    current = governed_entities(items)
    base = read_base(repository)
    found = {*check_items(items, repository), *base.problems}
    if base.readable:
        found.update(check_changes(governed_entities(base.items), current, base.unreadable))
    return GovernanceReport(len(current), base.notes, sorted(found))


def pending_entities(repository: Path) -> tuple[list[Entity], list[Problem]]:
    items, problems = parse_tree(node_folders(repository))
    if problems:
        return [], problems
    entities = governed_entities(items).values()
    pending = [entity for entity in entities if entity.status == Status.proposed]
    return sorted(pending, key=lambda entity: (str(entity.path), entity.line)), []
