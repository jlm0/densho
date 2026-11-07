from dataclasses import dataclass
from itertools import zip_longest
from typing import TYPE_CHECKING, cast

from engine.compiler.tree import path_problems
from engine.governance.base import read_head_file, tracked_files
from engine.governance.history_lines import (
    Entry,
    Recorded,
    digest,
    entity_lines,
    read_entries,
    replay,
)
from engine.layout import HISTORY_FILE, LANGUAGE_FOLDER
from engine.parser.node import node_folders, parse_tree
from engine.parser.result import Problem

if TYPE_CHECKING:
    from collections.abc import Mapping
    from pathlib import Path

    from engine.governance.history_lines import EntryKey

TEMPLATE_FILE = "copier.yml"
FILE = "file"
FILE_FIELD = "bytes"
HISTORY_CODES = ("history", "rewritten", "not-template", "changed", "not-staged", "write")
NO_INDEX_NOTE = "git cannot read an index in this folder, so the check of the index did not run."


@dataclass(frozen=True, slots=True)
class HistoryReport:
    change: int
    entries: tuple[Entry, ...]
    notes: list[str]
    problems: list[Problem]


def _language_entries(repository: Path) -> tuple[dict[EntryKey, Recorded], list[Problem]]:
    entries: dict[EntryKey, Recorded] = {}
    problems: list[Problem] = []
    for path in sorted((repository / LANGUAGE_FOLDER).rglob("*.yaml")):
        relative = path.relative_to(repository).as_posix()
        try:
            content = {FILE_FIELD: digest(path.read_bytes())}
        except OSError as error:
            message = f"The file cannot be read: {error.strerror!a}."
            problems.append(Problem(path, 1, "history", message))
            continue
        entries[FILE, relative] = Recorded(relative, None, content)
    return entries, problems


def _tree_state(repository: Path) -> tuple[dict[EntryKey, Recorded], list[Problem]]:
    items, problems = parse_tree(node_folders(repository))
    problems = [*problems, *path_problems(items, repository)]
    if problems:
        return {}, problems
    state = {key: recorded for item in items for _, key, recorded in entity_lines(item, repository)}
    files, problems = _language_entries(repository)
    return {**state, **files}, problems


def _changed_fields(old: Recorded, new: Recorded) -> list[str]:
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
    recorded: Mapping[EntryKey, Recorded], current: Mapping[EntryKey, Recorded], change: int
) -> list[Entry]:
    entries: list[Entry] = []
    for key in sorted(recorded.keys() | current.keys()):
        kind, name = key
        old, new = recorded.get(key), current.get(key)
        if new is None:
            gone = cast("Recorded", old)
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
    entries, problems = read_entries(path)
    if problems:
        return HistoryReport(0, (), [], problems)
    recorded, problems = replay(entries, path)
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
