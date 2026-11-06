from dataclasses import dataclass
from typing import TYPE_CHECKING, cast

from markdown_it import MarkdownIt

from engine.graph.references import exceptions_of

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence
    from pathlib import Path

    from pydantic import BaseModel

    from engine.generated.metamodel import Origin, Status
    from engine.parser.result import ParsedNode

type EntityKey = tuple[str, ...]

NODE = "node"
DIRECTIVE = "directive"
EXCEPTION = "exception"
NODE_FIELDS_WITHOUT_REVIEW = frozenset(
    {"id", "status", "origin", "title", "body", "pointers", "sources", "exceptions", "directives"}
)
DIRECTIVE_FIELDS_WITHOUT_REVIEW = frozenset({"id", "status", "origin", "sources"})
EXCEPTION_FIELDS_WITHOUT_REVIEW = frozenset({"directive", "status"})
_MARKDOWN = MarkdownIt("commonmark")


@dataclass(frozen=True, slots=True)
class Entity:
    key: EntityKey
    status: Status
    origin: Origin | None
    reviewed: Mapping[str, object]
    path: Path
    line: int

    @property
    def kind(self) -> str:
        return self.key[0]

    @property
    def name(self) -> str:
        return " ".join(self.key[1:])

    @property
    def label(self) -> str:
        return f"{self.kind} {self.name}"

    @property
    def holder(self) -> str:
        return str(self.reviewed["holder"]) if self.kind == DIRECTIVE else self.key[1]


def normal_text(value: str) -> str:
    return " ".join(_MARKDOWN.render(value).split())


def _normal(value: object) -> object:
    if isinstance(value, str):
        return normal_text(value)
    if isinstance(value, list):
        return sorted(cast("list[str]", value))
    return value


def _reviewed(model: BaseModel, without: frozenset[str]) -> dict[str, object]:
    fields = cast("dict[str, object]", model.model_dump(mode="json", exclude=set(without)))
    return {field: _normal(value) for field, value in fields.items() if value}


def governed_entities(items: Sequence[ParsedNode]) -> dict[EntityKey, Entity]:
    entities: dict[EntityKey, Entity] = {}
    for item in items:
        node = item.node
        key = (NODE, node.id)
        reviewed = _reviewed(node, NODE_FIELDS_WITHOUT_REVIEW)
        line = item.line_of(("status",))
        entities[key] = Entity(key, node.status, node.origin, reviewed, item.path, line)
        for position, directive in enumerate(node.directives or []):
            key = (DIRECTIVE, directive.id)
            reviewed = {
                **_reviewed(directive, DIRECTIVE_FIELDS_WITHOUT_REVIEW),
                "holder": node.id,
            }
            line = item.line_of(("directives", position, "status"))
            entities[key] = Entity(
                key, directive.status, directive.origin, reviewed, item.path, line
            )
        for index, exception in enumerate(exceptions_of(item)):
            key = (EXCEPTION, node.id, exception.directive)
            reviewed = _reviewed(exception, EXCEPTION_FIELDS_WITHOUT_REVIEW)
            line = item.line_of(("exceptions", index, "status"))
            entities[key] = Entity(key, exception.status, None, reviewed, item.path, line)
    return entities
