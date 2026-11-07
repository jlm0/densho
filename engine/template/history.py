from collections import Counter
from dataclasses import dataclass
from itertools import zip_longest
from pathlib import PurePosixPath
from typing import TYPE_CHECKING, cast

from engine.compiler.tree import path_problems
from engine.disciplines import read_answer
from engine.governance.base import read_file_at, read_head_file, tracked_files
from engine.governance.history_lines import (
    Entry,
    Recorded,
    digest,
    entity_lines,
    field_digest,
    read_entries,
    replay,
)
from engine.layout import HISTORY_FILE, LANGUAGE_FOLDER
from engine.parser.node import node_folders, parse_tree
from engine.parser.result import Problem

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence
    from pathlib import Path

    from engine.governance.history_lines import EntryKey

TEMPLATE_FILE = "copier.yml"
PARENT = "HEAD~1"
DISCIPLINE_KIND = "ka:Discipline"
BRANCHES_FOLDER = LANGUAGE_FOLDER / "branches"
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


def _drift(repository: Path) -> tuple[HistoryReport, dict[EntryKey, Recorded]]:
    path = repository / HISTORY_FILE
    entries, problems = read_entries(path)
    if problems:
        return HistoryReport(0, (), [], problems), {}
    recorded, problems = replay(entries, path)
    if problems:
        return HistoryReport(0, (), [], problems), {}
    current, problems = _tree_state(repository)
    if problems:
        return HistoryReport(0, (), [], problems), {}
    change = entries[-1].change + 1 if entries else 1
    entries_now = tuple(_difference(recorded, current, change))
    return HistoryReport(change, entries_now, [], []), recorded


def history_drift(repository: Path) -> HistoryReport:
    report, recorded = _drift(repository)
    if report.problems:
        return report
    answer, problems = read_answer(repository)
    if problems:
        return HistoryReport(0, (), [], problems)
    kept, notes = _summarize_left_out(recorded, report.entries, answer)
    return HistoryReport(report.change, tuple(kept), notes, [])


def _left_out_folders(
    recorded: Mapping[EntryKey, Recorded], answer: Sequence[str]
) -> dict[str, PurePosixPath]:
    kind = field_digest(DISCIPLINE_KIND)
    return {
        name: PurePosixPath(state.path).parent
        for (entry_kind, name), state in recorded.items()
        if entry_kind == "node" and state.content.get("kind") == kind and name not in answer
    }


def _folder_owner(path: str, folders: Mapping[str, PurePosixPath]) -> str | None:
    location = PurePosixPath(path)
    owners = [(len(folder.parts), name) for name, folder in folders.items()]
    inside = [(depth, name) for depth, name in owners if location.is_relative_to(folders[name])]
    return max(inside)[1] if inside else None


def _owner(
    entry: Entry, folders: Mapping[str, PurePosixPath], node_owners: Mapping[str, str]
) -> str | None:
    if entry.action != "removed":
        return None
    if entry.kind == FILE:
        path = PurePosixPath(entry.path)
        return node_owners.get(path.stem) if path.parent == BRANCHES_FOLDER else None
    return _folder_owner(entry.path, folders)


def _summarize_left_out(
    recorded: Mapping[EntryKey, Recorded], entries: Sequence[Entry], answer: Sequence[str] | None
) -> tuple[list[Entry], list[str]]:
    if answer is None:
        return list(entries), []
    folders = _left_out_folders(recorded, answer)
    node_owners = {
        entry.id: owner
        for entry in entries
        if entry.kind == "node" and (owner := _owner(entry, folders, {})) is not None
    }
    counts: Counter[str] = Counter()
    kept: list[Entry] = []
    for entry in entries:
        owner = _owner(entry, folders, node_owners)
        if owner is None:
            kept.append(entry)
        else:
            counts[owner] += 1
    notes = [
        f"{counts[name]} entities of {name} are not in this tree, "
        "because disciplines leaves the discipline out."
        for name in sorted(counts)
    ]
    return kept, notes


def _first_difference(old: bytes, new: bytes) -> int:
    pairs = zip_longest(old.split(b"\n"), new.split(b"\n"))
    return next(number for number, (before, after) in enumerate(pairs, start=1) if before != after)


def _loses_lines(head: bytes, parent: bytes) -> bool:
    kept = set(head.split(b"\n"))
    return any(line not in kept for line in parent.split(b"\n"))


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
    parent = read_file_at(repository, PARENT, HISTORY_FILE)
    if parent is not None and _loses_lines(head, parent):
        if data.startswith(parent):
            return []
        message = (
            "The last commit removed history lines, as a git revert does. "
            f"Run git checkout {PARENT} -- {HISTORY_FILE}, then run the command again."
        )
        return [Problem(path, _first_difference(parent, data), "rewritten", message)]
    if data.startswith(head):
        return []
    message = "The history only grows. Restore this file from HEAD, then run the command again."
    return [Problem(path, _first_difference(head, data), "rewritten", message)]


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
    report, _ = _drift(repository)
    if report.problems:
        return report
    written = _append(repository, report.entries) if report.entries else []
    if written:
        return HistoryReport(report.change, (), [], written)
    return _verified(repository, report) if verify else report
