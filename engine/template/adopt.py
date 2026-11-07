from collections import defaultdict
from dataclasses import dataclass
from typing import TYPE_CHECKING

from engine.generated.metamodel import Status
from engine.governance.base import read_base
from engine.governance.changes import CLOSED_STATUSES
from engine.governance.entities import governed_entities
from engine.governance.history_lines import install_matches
from engine.governance.status_line import set_status_lines
from engine.parser.node import node_folders, parse_tree
from engine.parser.result import Problem
from engine.runtime import generate_runtime
from engine.runtime.claude_code import add_root_import
from engine.template.select import select_disciplines

if TYPE_CHECKING:
    from collections.abc import Collection, Iterable, Sequence
    from pathlib import Path

    from engine.governance.base import Base
    from engine.governance.entities import Entity, EntityKey
    from engine.parser.result import ParsedNode
    from engine.runtime import RuntimeReport
    from engine.template.select import SelectionReport

ADOPT_CODES = ("adopt", "import")
NOT_AN_INSTALL_NOTE = (
    "The last commit holds the template history, so this run is not an install. "
    "The command keeps no template status, because a pull cannot accept an entity."
)


@dataclass(frozen=True, slots=True)
class AdoptReport:
    proposed: tuple[Entity, ...]
    imported: tuple[str, ...]
    runtime: RuntimeReport | None
    notes: list[str]
    problems: list[Problem]
    selection: SelectionReport | None = None


def _arrives_as_proposed(old: Entity | None, new: Entity, *, kept: bool) -> bool:
    if new.status == Status.proposed:
        return False
    if old is None:
        return not (kept and new.status == Status.accepted)
    if old.reviewed != new.reviewed:
        return True
    return new.status == Status.accepted and old.status != Status.accepted


def _arrivals(base: Base, items: Sequence[ParsedNode], kept: Collection[EntityKey]) -> list[Entity]:
    known = governed_entities(base.items)
    return [
        entity
        for key, entity in governed_entities(items).items()
        if entity.path not in base.unreadable
        and _arrives_as_proposed(known.get(key), entity, kept=key in kept)
    ]


def _rewrite_file(path: Path, entities: Iterable[Entity]) -> list[Problem]:
    try:
        data, missed = set_status_lines(path.read_bytes(), entities, Status.proposed)
        path.write_bytes(data)
    except OSError as error:
        message = f"The command cannot change this file: {error.strerror!a}."
        return [Problem(path, 1, "adopt", message)]
    return [
        Problem(
            path, entity.line, "adopt", f"Set the status of {entity.label} to proposed by hand."
        )
        for entity in missed
    ]


def _set_proposed(entities: Iterable[Entity]) -> list[Problem]:
    by_file: defaultdict[Path, list[Entity]] = defaultdict(list)
    for entity in entities:
        by_file[entity.path].append(entity)
    return [
        problem for path, group in sorted(by_file.items()) for problem in _rewrite_file(path, group)
    ]


def _closed_notes(entities: Iterable[Entity]) -> list[str]:
    return [
        f"{entity.label} was {Status(entity.status).value} in the template. It is now proposed. "
        f"Set it to {Status(entity.status).value} again if the project does not want it."
        for entity in entities
        if entity.status in CLOSED_STATUSES
    ]


def _kept(
    repository: Path, items: Sequence[ParsedNode], *, keep_accepted: bool
) -> tuple[frozenset[EntityKey], list[str]]:
    if not keep_accepted:
        return frozenset(), []
    matches = install_matches(items, repository)
    if matches is None:
        return frozenset(), [NOT_AN_INSTALL_NOTE]
    return matches, []


def adopt_template(repository: Path, *, keep_accepted: bool = False) -> AdoptReport:
    imported, import_problems = add_root_import(repository)
    selection = select_disciplines(repository)
    if selection.problems:
        problems = [*import_problems, *selection.problems]
        return AdoptReport((), imported, None, [], problems, selection)
    items, parse_problems = parse_tree(node_folders(repository))
    if parse_problems:
        problems = [*import_problems, *parse_problems]
        return AdoptReport((), imported, None, [], problems, selection)
    base = read_base(repository)
    if base.problems:
        problems = [*import_problems, *base.problems]
        return AdoptReport((), imported, None, [], problems, selection)
    kept, kept_notes = _kept(repository, items, keep_accepted=keep_accepted)
    arrivals = _arrivals(base, items, kept) if base.readable or base.empty else []
    problems = [*import_problems, *_set_proposed(arrivals)]
    notes = [*kept_notes, *_closed_notes(arrivals)]
    if problems:
        return AdoptReport(tuple(arrivals), imported, None, notes, problems, selection)
    runtime = generate_runtime(repository)
    return AdoptReport(
        tuple(arrivals),
        imported,
        runtime,
        [*notes, *runtime.notes],
        runtime.problems,
        selection,
    )
