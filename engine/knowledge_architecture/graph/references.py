from dataclasses import dataclass
from typing import TYPE_CHECKING, cast

from knowledge_architecture.generated.metamodel import KnowledgeNode
from knowledge_architecture.parser.result import Problem

if TYPE_CHECKING:
    from collections.abc import Iterator

    from knowledge_architecture.generated.metamodel import DirectiveException
    from knowledge_architecture.parser.result import FieldPath, ParsedNode

EDGE_FIELDS = (
    "broader",
    "related",
    "informs",
    "depends_on",
    "governs",
    "implements",
    "uses",
    "applies",
)
DIRECTIVE_REFERENCE_FIELDS = ("also_attached_to", "refines", "conflicts_with")


@dataclass(frozen=True, slots=True)
class Reference:
    source: ParsedNode
    field: str
    field_path: FieldPath
    target: str


def problem_at(item: ParsedNode, field_path: FieldPath, code: str, message: str) -> Problem:
    return Problem(item.path, item.line_of(field_path), code, message)


def edge_targets(item: ParsedNode, field: str) -> list[str]:
    return cast("list[str] | None", getattr(item.node, field, None)) or []


def exceptions_of(item: ParsedNode) -> list[DirectiveException]:
    return (item.node.exceptions or []) if isinstance(item.node, KnowledgeNode) else []


def references_of(item: ParsedNode) -> Iterator[Reference]:
    for field in EDGE_FIELDS:
        for index, target in enumerate(edge_targets(item, field)):
            yield Reference(item, field, (field, index), target)
    for index, pointer in enumerate(item.node.pointers or []):
        yield Reference(item, "target", ("pointers", index, "target"), pointer.target)
    for index, exception in enumerate(exceptions_of(item)):
        field_path = ("exceptions", index, "directive")
        yield Reference(item, "directive", field_path, exception.directive)
    for position, directive in enumerate(item.node.directives or []):
        for field in DIRECTIVE_REFERENCE_FIELDS:
            for index, target in enumerate(getattr(directive, field) or []):
                yield Reference(item, field, ("directives", position, field, index), target)


def entity_ids(item: ParsedNode) -> Iterator[tuple[str, FieldPath]]:
    yield item.node.id, ("id",)
    for position, directive in enumerate(item.node.directives or []):
        yield directive.id, ("directives", position)
