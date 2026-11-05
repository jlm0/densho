import hashlib
import json
from dataclasses import dataclass
from itertools import zip_longest
from pathlib import PurePosixPath
from typing import TYPE_CHECKING, Literal, cast

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from knowledge_architecture.compiler.tree import path_problems
from knowledge_architecture.generated.metamodel import Status
from knowledge_architecture.governance.base import read_head_file, tracked_files
from knowledge_architecture.governance.entities import DIRECTIVE, EXCEPTION, NODE, normal_text
from knowledge_architecture.graph.references import exceptions_of
from knowledge_architecture.parser.node import node_folders, parse_tree
from knowledge_architecture.parser.result import Problem

if TYPE_CHECKING:
    from collections.abc import Iterator, Mapping
    from pathlib import Path

    from knowledge_architecture.parser.result import ParsedNode

type EntryKind = Literal["node", "directive", "exception", "file"]
type EntryKey = tuple[EntryKind, str]

HISTORY_FILE = PurePosixPath(".ka/history.jsonl")
TEMPLATE_FILE = "copier.yml"
LANGUAGE_FOLDER = PurePosixPath("governance/language")
FILE = "file"
FILE_FIELD = "bytes"
DIGEST_LENGTH = 16
HISTORY_CODES = ("history", "rewritten", "not-template", "changed", "not-staged", "write")
NO_INDEX_NOTE = "git cannot read an index in this folder, so the check of the index did not run."
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
class _Recorded:
    path: str
    status: str | None
    content: Mapping[str, str]


@dataclass(frozen=True, slots=True)
class HistoryReport:
    change: int
    entries: tuple[Entry, ...]
    notes: list[str]
    problems: list[Problem]


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


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()[:DIGEST_LENGTH]


def _content(model: BaseModel, without: frozenset[str], **extra: str) -> dict[str, str]:
    fields = cast("dict[str, object]", model.model_dump(mode="json", exclude=set(without)))
    return {
        name: _digest(_canonical(_normal(value)).encode("ascii"))
        for name, value in sorted({**fields, **extra}.items())
        if value
    }


def _node_entries(item: ParsedNode, repository: Path) -> Iterator[tuple[EntryKey, _Recorded]]:
    node = item.node
    path = item.path.relative_to(repository).as_posix()
    content = _content(node, NODE_FIELDS_WITHOUT_DIGEST)
    yield (NODE, node.id), _Recorded(path, Status(node.status).value, content)
    for directive in node.directives or []:
        content = _content(directive, DIRECTIVE_FIELDS_WITHOUT_DIGEST, holder=node.id)
        yield (DIRECTIVE, directive.id), _Recorded(path, Status(directive.status).value, content)
    for exception in exceptions_of(item):
        content = _content(exception, EXCEPTION_FIELDS_WITHOUT_DIGEST)
        key = f"{node.id}/{exception.directive}"
        yield (EXCEPTION, key), _Recorded(path, Status(exception.status).value, content)


def _language_entries(repository: Path) -> tuple[dict[EntryKey, _Recorded], list[Problem]]:
    entries: dict[EntryKey, _Recorded] = {}
    problems: list[Problem] = []
    for path in sorted((repository / LANGUAGE_FOLDER).rglob("*.yaml")):
        relative = path.relative_to(repository).as_posix()
        try:
            content = {FILE_FIELD: _digest(path.read_bytes())}
        except OSError as error:
            message = f"The file cannot be read: {error.strerror!a}."
            problems.append(Problem(path, 1, "history", message))
            continue
        entries[FILE, relative] = _Recorded(relative, None, content)
    return entries, problems


def _tree_state(repository: Path) -> tuple[dict[EntryKey, _Recorded], list[Problem]]:
    items, problems = parse_tree(node_folders(repository))
    problems = [*problems, *path_problems(items, repository)]
    if problems:
        return {}, problems
    state = dict(entry for item in items for entry in _node_entries(item, repository))
    files, problems = _language_entries(repository)
    return {**state, **files}, problems


def _read_entries(path: Path) -> tuple[list[Entry], list[Problem]]:
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


def _replay(entries: list[Entry], path: Path) -> tuple[dict[EntryKey, _Recorded], list[Problem]]:
    state: dict[EntryKey, _Recorded] = {}
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
            state[key] = _Recorded(entry.path, entry.status, entry.content)
    return state, problems


def _changed_fields(old: _Recorded, new: _Recorded) -> list[str]:
    names = {
        name
        for name in old.content.keys() | new.content.keys()
        if old.content.get(name) != new.content.get(name)
    }
    if old.path != new.path:
        names.add("path")
    if old.status != new.status:
        names.add("status")
    return sorted(names)


def _difference(
    recorded: Mapping[EntryKey, _Recorded], current: Mapping[EntryKey, _Recorded], change: int
) -> list[Entry]:
    entries: list[Entry] = []
    for key in sorted(recorded.keys() | current.keys()):
        kind, name = key
        old, new = recorded.get(key), current.get(key)
        if new is None:
            gone = cast("_Recorded", old)
            entries.append(
                Entry(
                    change=change,
                    kind=kind,
                    id=name,
                    action="removed",
                    fields=[],
                    path=gone.path,
                    status=gone.status,
                    content={},
                )
            )
            continue
        fields = [] if old is None else _changed_fields(old, new)
        if old is None or fields:
            entries.append(
                Entry(
                    change=change,
                    kind=kind,
                    id=name,
                    action="added" if old is None else "changed",
                    fields=fields,
                    path=new.path,
                    status=new.status,
                    content=dict(new.content),
                )
            )
    return entries


def history_drift(repository: Path) -> HistoryReport:
    path = repository / HISTORY_FILE
    entries, problems = _read_entries(path)
    if problems:
        return HistoryReport(0, (), [], problems)
    recorded, problems = _replay(entries, path)
    if problems:
        return HistoryReport(0, (), [], problems)
    current, problems = _tree_state(repository)
    if problems:
        return HistoryReport(0, (), [], problems)
    change = entries[-1].change + 1 if entries else 1
    return HistoryReport(change, tuple(_difference(recorded, current, change)), [], [])


def _rewritten(repository: Path) -> list[Problem]:
    path = repository / HISTORY_FILE
    head = read_head_file(repository, HISTORY_FILE)
    if head is None:
        return []
    try:
        data = path.read_bytes()
    except FileNotFoundError:
        data = b""
    except OSError:
        return []
    if data.startswith(head):
        return []
    pairs = zip_longest(head.split(b"\n"), data.split(b"\n"))
    line = next(number for number, (old, new) in enumerate(pairs, start=1) if old != new)
    message = "The history only grows. Restore this file from HEAD, then run the command again."
    return [Problem(path, line, "rewritten", message)]


def _append(repository: Path, entries: tuple[Entry, ...]) -> list[Problem]:
    path = repository / HISTORY_FILE
    text = "".join(f"{entry.model_dump_json()}\n" for entry in entries)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as stream:
            stream.write(text)
    except OSError as error:
        message = f"The command cannot change this path: {error.strerror!a}."
        return [Problem(path, 1, "write", message)]
    return []


def _verified(repository: Path, report: HistoryReport) -> HistoryReport:
    path = repository / HISTORY_FILE
    if report.entries:
        message = f"The command added change {report.change} to this file. Stage it."
        return HistoryReport(
            report.change, report.entries, report.notes, [Problem(path, 1, "changed", message)]
        )
    if not path.exists():
        return report
    tracked = tracked_files(repository)
    if tracked is None:
        return HistoryReport(report.change, (), [NO_INDEX_NOTE], [])
    if HISTORY_FILE.as_posix() in tracked:
        return report
    message = "The git index does not hold this file. Stage it."
    return HistoryReport(report.change, (), [], [Problem(path, 1, "not-staged", message)])


def record_history(repository: Path, *, verify: bool = False) -> HistoryReport:
    if not (repository / TEMPLATE_FILE).is_file():
        message = (
            f"This folder holds no {TEMPLATE_FILE}, so it is not the template. "
            "The history records template changes only."
        )
        return HistoryReport(
            0, (), [], [Problem(repository / HISTORY_FILE, 1, "not-template", message)]
        )
    rewritten = _rewritten(repository)
    if rewritten:
        return HistoryReport(0, (), [], rewritten)
    report = history_drift(repository)
    if report.problems:
        return report
    written = _append(repository, report.entries) if report.entries else []
    if written:
        return HistoryReport(report.change, (), [], written)
    return _verified(repository, report) if verify else report
