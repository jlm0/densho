from collections import defaultdict
from dataclasses import dataclass, replace
from typing import TYPE_CHECKING

from engine.compiler import checked_tree, compile_items
from engine.directives import check_items as check_directive_items
from engine.generated.metamodel import Status
from engine.governance.base import read_base
from engine.governance.changes import CLOSED_STATUSES
from engine.governance.checks import pulls_template
from engine.governance.entities import (
    DIRECTIVE,
    EXCEPTION,
    NODE,
    governed_entities,
)
from engine.governance.status_line import set_status_lines
from engine.interface.tree import children_by_broader, subtree_ids
from engine.layout import HISTORY_FILE, LAUNCHER
from engine.parser import ParsedNode, parse_source, universal_newlines
from engine.parser.result import Problem
from engine.runtime import build_view, render_files, rendered_problems

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping, Sequence
    from pathlib import Path

    from engine.governance.entities import Entity, EntityKey

ACCEPT_CODES = ("unknown-id", "not-proposed", "uncommitted", "no-history", "status-line", "write")
EXCEPTION_SEPARATOR = ":"
PROJECT_COMMAND = LAUNCHER.as_posix()
TEMPLATE_COMMAND = "uv run ka"


@dataclass(frozen=True, slots=True)
class AcceptReport:
    accepted: tuple[Entity, ...]
    not_proposed: int
    notes: list[str]
    problems: list[Problem]


@dataclass(frozen=True, slots=True)
class _Selection:
    targets: list[Entity]
    not_proposed: int
    problems: list[Problem]


def command_prefix(repository: Path) -> str:
    return PROJECT_COMMAND if (repository / PROJECT_COMMAND).is_file() else TEMPLATE_COMMAND


def entity_name(entity: Entity) -> str:
    return EXCEPTION_SEPARATOR.join(entity.key[1:])


def _named(name: str, entities: Mapping[EntityKey, Entity]) -> Entity | None:
    node_id, separator, directive_id = name.partition(EXCEPTION_SEPARATOR)
    if separator:
        return entities.get((EXCEPTION, node_id, directive_id))
    return entities.get((NODE, name)) or entities.get((DIRECTIVE, name))


def _unknown(repository: Path, name: str) -> Problem:
    message = f"No entity has the name {name!a}. Run the view, or ka governance --pending."
    return Problem(repository, 1, "unknown-id", message)


def _select(
    repository: Path,
    items: Sequence[ParsedNode],
    entities: Mapping[EntityKey, Entity],
    names: Sequence[str],
    subtrees: Sequence[str],
) -> _Selection:
    problems: list[Problem] = []
    selected: dict[EntityKey, Entity] = {}
    for name in names:
        entity = _named(name, entities)
        if entity is None:
            problems.append(_unknown(repository, name))
        elif entity.status in CLOSED_STATUSES:
            message = (
                f"{entity.label} is {Status(entity.status).value}. "
                "Commit it as proposed before you accept it."
            )
            problems.append(Problem(entity.path, entity.line, "not-proposed", message))
        else:
            selected[entity.key] = entity
    children = children_by_broader(items)
    known_nodes = {item.node.id for item in items}
    for node_id in subtrees:
        if node_id not in known_nodes:
            problems.append(_unknown(repository, node_id))
            continue
        branch = subtree_ids(node_id, children)
        selected.update(
            (entity.key, entity) for entity in entities.values() if entity.holder in branch
        )
    targets = [entity for entity in selected.values() if entity.status == Status.proposed]
    return _Selection(targets, len(selected) - len(targets), problems)


def _head_problems(
    targets: Iterable[Entity], base: Mapping[EntityKey, Entity], command: str
) -> list[Problem]:
    problems: list[Problem] = []
    for entity in targets:
        old = base.get(entity.key)
        if old is None:
            message = f"HEAD does not hold {entity.label}. Commit it, then run {command} accept."
            problems.append(Problem(entity.path, entity.line, "uncommitted", message))
        elif old.status in CLOSED_STATUSES:
            message = (
                f"HEAD has {entity.label} as {Status(old.status).value}. "
                "Commit it as proposed first."
            )
            problems.append(Problem(entity.path, entity.line, "not-proposed", message))
        elif old.reviewed != entity.reviewed:
            message = (
                f"{entity.label} differs from HEAD in a field that needs review. "
                f"Commit the change and review it, then run {command} accept."
            )
            problems.append(Problem(entity.path, entity.line, "uncommitted", message))
    return problems


def _rewritten(targets: Iterable[Entity]) -> dict[Path, bytes]:
    by_file: defaultdict[Path, list[Entity]] = defaultdict(list)
    for entity in targets:
        by_file[entity.path].append(entity)
    rewrites: dict[Path, bytes] = {}
    for path, group in sorted(by_file.items()):
        rewrites[path], _ = set_status_lines(path.read_bytes(), group, Status.accepted)
    return rewrites


def _with_rewrites(items: Iterable[ParsedNode], rewrites: Mapping[Path, bytes]) -> list[ParsedNode]:
    result: list[ParsedNode] = []
    for item in items:
        data = rewrites.get(item.path)
        if data is None:
            result.append(item)
            continue
        parsed = parse_source(universal_newlines(data.decode("utf-8")), item.path)
        if isinstance(parsed, ParsedNode):
            result.append(replace(parsed, scripts=item.scripts))
        else:
            result.append(item)
    return result


def _edit_problems(targets: Iterable[Entity], after: Mapping[EntityKey, Entity]) -> list[Problem]:
    problems: list[Problem] = []
    for old in targets:
        if after.get(old.key) != replace(old, status=Status.accepted):
            message = (
                f"The command cannot change the status of {old.label} alone on this line. "
                "Move the status to a line of its own, or change it by hand."
            )
            problems.append(Problem(old.path, old.line, "status-line", message))
    return problems


def _result_problems(items: Sequence[ParsedNode], repository: Path) -> list[Problem]:
    rendered = render_files(build_view(compile_items(items, repository)))
    found = {
        *check_directive_items(items),
        *rendered_problems(rendered, repository),
    }
    return sorted(found)


def _write(
    rewrites: Mapping[Path, bytes], targets: Iterable[Entity]
) -> tuple[tuple[Entity, ...], list[Problem]]:
    written: set[Path] = set()
    problems: list[Problem] = []
    for path, data in rewrites.items():
        try:
            path.write_bytes(data)
        except OSError as error:
            message = f"The command cannot change this file: {error.strerror!a}."
            problems.append(Problem(path, 1, "write", message))
            break
        written.add(path)
    return tuple(entity for entity in targets if entity.path in written), problems


def _base_problems(repository: Path, targets: Iterable[Entity]) -> list[Problem]:
    base = read_base(repository)
    if not base.readable:
        message = (
            "A review approves the text that the last commit holds, and this folder has no "
            f"last commit to compare with. {' '.join(base.notes)}"
        )
        return [Problem(repository, 1, "no-history", message)]
    if pulls_template(repository):
        message = (
            "This folder holds a template pull with no commit, and a pull cannot accept an "
            "entity. Commit the pull, then run the command again."
        )
        return [Problem(repository / HISTORY_FILE, 1, "uncommitted", message)]
    return _head_problems(targets, governed_entities(base.items), command_prefix(repository))


def _planned_rewrites(
    repository: Path,
    items: Sequence[ParsedNode],
    targets: Sequence[Entity],
) -> tuple[dict[Path, bytes], list[Problem]]:
    try:
        rewrites = _rewritten(targets)
    except OSError as error:
        message = f"The command cannot read a node file: {error.strerror!a}."
        return {}, [Problem(repository, 1, "write", message)]
    new_items = _with_rewrites(items, rewrites)
    problems = _edit_problems(targets, governed_entities(new_items))
    return rewrites, problems or _result_problems(new_items, repository)


def accept_entities(
    repository: Path,
    names: Sequence[str],
    subtrees: Sequence[str] = (),
    *,
    dry_run: bool = False,
) -> AcceptReport:
    checked = checked_tree(repository)
    if checked.problems:
        return AcceptReport((), 0, checked.notes, checked.problems)
    entities = governed_entities(checked.items)
    selection = _select(repository, checked.items, entities, names, subtrees)
    targets = sorted(selection.targets, key=lambda entity: (str(entity.path), entity.line))
    problems = selection.problems or (_base_problems(repository, targets) if targets else [])
    if problems:
        return AcceptReport((), 0, checked.notes, problems)
    rewrites, problems = _planned_rewrites(repository, checked.items, targets)
    if problems:
        return AcceptReport((), 0, checked.notes, problems)
    if dry_run:
        return AcceptReport(tuple(targets), selection.not_proposed, checked.notes, [])
    accepted, problems = _write(rewrites, targets)
    return AcceptReport(accepted, selection.not_proposed, checked.notes, problems)
