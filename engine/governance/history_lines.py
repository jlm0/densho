import hashlib
import json
from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal, cast

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from engine.generated.metamodel import Status
from engine.governance.base import head_holds
from engine.governance.entities import DIRECTIVE, EXCEPTION, NODE, SCRIPTS_FIELD, normal_text
from engine.graph.references import exceptions_of
from engine.layout import HISTORY_FILE
from engine.parser.result import Problem
from engine.parser.scripts import scripts_digest

if TYPE_CHECKING:
    from collections.abc import Iterator, Mapping, Sequence
    from pathlib import Path

    from engine.governance.base import Base
    from engine.governance.entities import EntityKey
    from engine.parser.result import ParsedNode

type EntryKind = Literal["node", "directive", "exception", "file"]
type EntryKey = tuple[EntryKind, str]

DIGEST_LENGTH = 16
NODE_FIELDS_WITHOUT_DIGEST = frozenset({"id", "status", "origin", "directives", "exceptions"})
DIRECTIVE_FIELDS_WITHOUT_DIGEST = frozenset({"id", "status", "origin"})
EXCEPTION_FIELDS_WITHOUT_DIGEST = frozenset({"directive", "status"})


class Entry(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    change: int = Field(ge=1)
    kind: EntryKind
    id: str
    action: Literal["added", "changed", "removed"]
    fields: list[str]
    path: str
    status: str | None
    content: dict[str, str]


@dataclass(frozen=True, slots=True)
class Recorded:
    path: str
    status: str | None
    content: Mapping[str, str]


def _normal(value: object) -> object:
    if isinstance(value, str):
        return normal_text(value)
    if isinstance(value, list):
        return sorted((_normal(entry) for entry in cast("list[object]", value)), key=_canonical)
    if isinstance(value, dict):
        return {name: _normal(entry) for name, entry in cast("dict[str, object]", value).items()}
    return value


def _canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()[:DIGEST_LENGTH]


def field_digest(value: object) -> str:
    return digest(_canonical(_normal(value)).encode("ascii"))


def _content(model: BaseModel, without: frozenset[str], **extra: str) -> dict[str, str]:
    fields = cast("dict[str, object]", model.model_dump(mode="json", exclude=set(without)))
    return {
        name: field_digest(value) for name, value in sorted({**fields, **extra}.items()) if value
    }


def entity_lines(
    item: ParsedNode, repository: Path
) -> Iterator[tuple[EntityKey, EntryKey, Recorded]]:
    node = item.node
    path = item.path.relative_to(repository).as_posix()
    content = _content(node, NODE_FIELDS_WITHOUT_DIGEST)
    if item.scripts:
        scripts = scripts_digest(item.scripts)[:DIGEST_LENGTH]
        content = dict(sorted({**content, SCRIPTS_FIELD: scripts}.items()))
    yield (NODE, node.id), (NODE, node.id), Recorded(path, Status(node.status).value, content)
    for directive in node.directives or []:
        content = _content(directive, DIRECTIVE_FIELDS_WITHOUT_DIGEST, holder=node.id)
        recorded = Recorded(path, Status(directive.status).value, content)
        yield (DIRECTIVE, directive.id), (DIRECTIVE, directive.id), recorded
    for exception in exceptions_of(item):
        content = _content(exception, EXCEPTION_FIELDS_WITHOUT_DIGEST)
        recorded = Recorded(path, Status(exception.status).value, content)
        entity_key = (EXCEPTION, node.id, exception.directive)
        yield entity_key, (EXCEPTION, f"{node.id}/{exception.directive}"), recorded


def read_entries(path: Path) -> tuple[list[Entry], list[Problem]]:
    try:
        data = path.read_bytes()
    except FileNotFoundError:
        return [], []
    except OSError as error:
        message = f"The file cannot be read: {error.strerror!a}."
        return [], [Problem(path, 1, "history", message)]
    lines = data.split(b"\n")
    if lines.pop():
        message = "The last line has no line end."
        return [], [Problem(path, len(lines) + 1, "history", message)]
    entries: list[Entry] = []
    problems: list[Problem] = []
    for number, line in enumerate(lines, start=1):
        try:
            entries.append(Entry.model_validate_json(line))
        except ValidationError as error:
            detail = error.errors(include_url=False, include_input=False)[0]
            where = ".".join(map(str, detail["loc"]))
            message = f"{where}: {detail['msg']}" if where else detail["msg"]
            problems.append(Problem(path, number, "history", message))
    return entries, problems


def replay(entries: list[Entry], path: Path) -> tuple[dict[EntryKey, Recorded], list[Problem]]:
    state: dict[EntryKey, Recorded] = {}
    problems: list[Problem] = []
    last = 0
    for number, entry in enumerate(entries, start=1):
        key = (entry.kind, entry.id)
        if entry.change not in {last, last + 1}:
            message = f"The change number {entry.change} does not follow {last}."
            problems.append(Problem(path, number, "history", message))
        last = entry.change
        if (entry.action == "added") == (key in state):
            message = f"The action {entry.action} does not fit {entry.kind} {entry.id}."
            problems.append(Problem(path, number, "history", message))
        elif entry.action == "removed":
            del state[key]
        else:
            state[key] = Recorded(entry.path, entry.status, entry.content)
    return state, problems


def accepted_in_template(items: Sequence[ParsedNode], repository: Path) -> frozenset[EntityKey]:
    path = repository / HISTORY_FILE
    entries, problems = read_entries(path)
    if problems:
        return frozenset()
    recorded, problems = replay(entries, path)
    if problems:
        return frozenset()
    return frozenset(
        entity_key
        for item in items
        for entity_key, entry_key, current in entity_lines(item, repository)
        if (line := recorded.get(entry_key)) is not None
        and line.status == Status.accepted.value
        and line.content == current.content
    )


def install_matches(
    items: Sequence[ParsedNode], repository: Path, base: Base
) -> frozenset[EntityKey] | None:
    if head_holds(repository, HISTORY_FILE) is not False or base.items or base.unreadable:
        return None
    return accepted_in_template(items, repository)
