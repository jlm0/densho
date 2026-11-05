from dataclasses import dataclass
from typing import TYPE_CHECKING, cast

from knowledge_architecture.parser.result import Problem

if TYPE_CHECKING:
    from collections.abc import Iterator

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


def references_of(item: ParsedNode) -> Iterator[Reference]:
    for field in EDGE_FIELDS:
        for index, target in enumerate(edge_targets(item, field)):
            yield Reference(item, field, (field, index), target)
    for index, pointer in enumerate(item.node.pointers or []):
        yield Reference(item, "target", ("pointers", index, "target"), pointer.target)
    for position, directive in enumerate(item.node.directives or []):
        for index, target in enumerate(directive.also_attached_to or []):
            field_path = ("directives", position, "also_attached_to", index)
            yield Reference(item, "also_attached_to", field_path, target)


def entity_ids(item: ParsedNode) -> Iterator[tuple[str, FieldPath]]:
    yield item.node.id, ("id",)
    for position, directive in enumerate(item.node.directives or []):
        yield directive.id, ("directives", position)
