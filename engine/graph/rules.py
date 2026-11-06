from typing import TYPE_CHECKING

from engine.generated.metamodel import KnowledgeType, Root, Skill
from engine.graph.references import (
    edge_targets,
    entity_ids,
    problem_at,
    references_of,
)
from engine.layout import (
    GOVERNANCE_FOLDER,
    NODES_FOLDER,
    POLICY_FOLDER,
    ROOT_NODE_FILE,
    SKILLS_FOLDER,
)
from engine.parser.result import FieldPath, ParsedNode, Problem

if TYPE_CHECKING:
    from collections.abc import Sequence
    from pathlib import Path


def check_identity(items: Sequence[ParsedNode]) -> list[Problem]:
    problems: list[Problem] = []
    first_seen: dict[str, tuple[ParsedNode, FieldPath]] = {}
    for item in items:
        for entity_id, field_path in entity_ids(item):
            if entity_id not in first_seen:
                first_seen[entity_id] = (item, field_path)
                continue
            seen_item, seen_path = first_seen[entity_id]
            location = f"{seen_item.path}:{seen_item.line_of(seen_path)}"
            message = f"The ID {entity_id} is already in use at {location}."
            problems.append(problem_at(item, field_path, "duplicate-id", message))
    return problems


def root_nodes(items: Sequence[ParsedNode]) -> list[ParsedNode]:
    return [item for item in items if isinstance(item.node, Root)]


def check_placement(items: Sequence[ParsedNode], repository: Path) -> list[Problem]:
    root_file = repository / ROOT_NODE_FILE
    problems = [_placement_problem(item, root_file, repository) for item in items]
    if not root_nodes(items):
        problems.append(Problem(root_file, 1, "root", "Add the root node to this file."))
    return [problem for problem in problems if problem is not None]


def _placement_problem(item: ParsedNode, root_file: Path, repository: Path) -> Problem | None:
    skills = repository / SKILLS_FOLDER
    policies = repository / POLICY_FOLDER
    nodes = repository / NODES_FOLDER
    if isinstance(item.node, Root):
        message = None if item.path == root_file else f"Move the root node to {root_file}."
    elif item.path == root_file:
        message = "Only the root node can use this file. Set kind to ka:Root or move this node."
    elif isinstance(item.node, Skill):
        message = None if item.path.is_relative_to(skills) else f"Move this skill to {skills}."
    elif item.path.is_relative_to(skills):
        message = f"Move this node out of {skills}."
    elif item.path.is_relative_to(repository / GOVERNANCE_FOLDER):
        message = None if item.path.is_relative_to(policies) else f"Move this node to {policies}."
    else:
        message = None if item.path.is_relative_to(nodes) else f"Move this node to {nodes}."
    return None if message is None else problem_at(item, ("kind",), "placement", message)


def check_references(items: Sequence[ParsedNode]) -> list[Problem]:
    known = {entity_id for item in items for entity_id, _ in entity_ids(item)}
    return [
        problem_at(
            reference.source,
            reference.field_path,
            "reference",
            f"{reference.field} names {reference.target!a}, and no node or directive has this ID.",
        )
        for item in items
        for reference in references_of(item)
        if reference.target not in known
    ]


def check_skills(items: Sequence[ParsedNode]) -> list[Problem]:
    return [
        problem_at(item, ("id",), "skill", "Add uses or applies, so the skill names what it needs.")
        for item in items
        if isinstance(item.node, Skill) and not (item.node.uses or item.node.applies)
    ]


def check_implements(items: Sequence[ParsedNode]) -> list[Problem]:
    return [
        problem_at(
            item,
            ("implements",),
            "implements",
            "Only workspace knowledge can use implements. Set knowledge_type to workspace.",
        )
        for item in items
        if edge_targets(item, "implements")
        and getattr(item.node, "knowledge_type", None) != KnowledgeType.workspace
    ]
