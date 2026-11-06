from dataclasses import dataclass
from typing import TYPE_CHECKING

from engine.generated.metamodel import KnowledgeType, Origin, Status
from engine.governance.base import read_base
from engine.governance.changes import CHANGE_CODES, check_changes
from engine.governance.entities import governed_entities
from engine.graph.references import edge_targets, problem_at, references_of
from engine.parser.node import POLICY_FOLDER, node_folders, parse_tree

if TYPE_CHECKING:
    from collections.abc import Sequence
    from pathlib import Path

    from engine.governance.entities import Entity
    from engine.graph.references import Reference
    from engine.parser.result import ParsedNode, Problem

GOVERNANCE_CODES = (
    *CHANGE_CODES,
    "template-workspace",
    "deprecated-holder",
    "deprecated-reference",
    "policy-governs",
    "base",
)
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
        if directive.status != Status.deprecated
    ]


def _source_status(reference: Reference) -> Status:
    node = reference.source.node
    match reference.field_path:
        case ("directives", int(position), *_):
            return (node.directives or [])[position].status
        case _:
            return node.status


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
