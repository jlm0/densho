import re
import shutil
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, cast

from engine.disciplines import memberships, read_answer
from engine.generated.metamodel import Origin, Skill
from engine.graph.references import edge_targets, references_of
from engine.language.profile import BRANCH_FOLDER, BRANCH_SUFFIX
from engine.layout import KNOWLEDGE_FOLDER, LANGUAGE_FOLDER, SKILLS_FOLDER
from engine.parser.node import node_folders, parse_source, parse_tree, universal_newlines
from engine.parser.result import ParsedNode, Problem

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping, Sequence
    from pathlib import Path

    from engine.graph.references import Reference
    from engine.parser.result import FieldPath

SELECT_CODES = ("select",)
PRUNED_FIELDS = frozenset({"informs", "related", "also_attached_to", "refines"})
POINTER_FIELD = "pointers"
DIRECTIVES_FIELD = "directives"
FRONT_MATTER_DELIMITER = "---"
LINE_BREAK = re.compile(r"(\r\n|\r|\n)")


@dataclass(frozen=True, slots=True)
class SelectionReport:
    disciplines: tuple[str, ...] | None
    removed: tuple[Path, ...]
    pruned: tuple[str, ...]
    notes: list[str]
    problems: list[Problem]


@dataclass(slots=True)
class _Plan:
    selected: set[str]
    removed: set[str]
    notes: list[str] = field(default_factory=list[str])


def _holders(items: Sequence[ParsedNode]) -> dict[str, str]:
    return {
        directive.id: item.node.id for item in items for directive in item.node.directives or []
    }


def _left_out(item: ParsedNode, membership: frozenset[str], selected: set[str]) -> bool:
    return item.node.origin == Origin.template and bool(membership) and not membership & selected


def _plan(items: Sequence[ParsedNode], answer: list[str]) -> _Plan:
    found = memberships(items)
    known = {name for names in found.values() for name in names}
    plan = _Plan({name for name in answer if name in known}, set())
    plan.notes += [
        f"The answer names {name}, and the template has no discipline with this ID."
        for name in answer
        if name not in known
    ]
    by_id = {item.node.id: item for item in items}
    while True:
        kept = [item for item in items if not _left_out(item, found[item.node.id], plan.selected)]
        needed = {
            (discipline, item.node.id, target)
            for item in kept
            for target in edge_targets(item, "depends_on")
            if target in by_id and _left_out(by_id[target], found[target], plan.selected)
            for discipline in found[target]
        }
        if not needed:
            break
        for discipline, source, target in sorted(needed):
            if discipline not in plan.selected:
                plan.selected.add(discipline)
                plan.notes.append(
                    f"The selection adds {discipline}, because {source} depends on {target}."
                )
    plan.removed = {item.node.id for item in items} - {item.node.id for item in kept}
    holders = _holders(items)
    for item in kept:
        if isinstance(item.node, Skill) and item.node.origin == Origin.template:
            targets = [*(item.node.uses or []), *(item.node.applies or [])]
            if any(holders.get(target, target) in plan.removed for target in targets):
                plan.removed.add(item.node.id)
    return plan


def _target_removed(reference: Reference, removed: set[str], holders: Mapping[str, str]) -> bool:
    return reference.target in removed or holders.get(reference.target) in removed


def _removal_path(reference: Reference) -> FieldPath:
    if reference.field == "target":
        return reference.field_path[:2]
    return reference.field_path


def _edge_problem(item: ParsedNode, reference: Reference) -> Problem:
    message = (
        f"{reference.field} names {reference.target}, which the selection leaves out. "
        f"Select the discipline of {reference.target}, or remove the {reference.field} entry."
    )
    return Problem(item.path, item.line_of(reference.field_path), "select", message)


def _closing_line(lines: Sequence[str]) -> int:
    if lines and lines[0] == FRONT_MATTER_DELIMITER and FRONT_MATTER_DELIMITER in lines[1:]:
        return lines.index(FRONT_MATTER_DELIMITER, 1) + 1
    return len(lines) + 1


def _top_level_lines(item: ParsedNode) -> list[int]:
    return [
        line
        for field_path, line in item.locations.items()
        if len(field_path) == 1 and isinstance(field_path[0], str)
    ]


def _span(item: ParsedNode, removal: FieldPath, lines: Sequence[str]) -> range | None:
    start = item.locations.get(removal)
    if start is None:
        return None
    if removal[0] != POINTER_FIELD:
        return range(start, start + 1)
    following = item.locations.get((POINTER_FIELD, cast("int", removal[-1]) + 1))
    if following is None:
        close = _closing_line(lines)
        following = min(
            [line for line in _top_level_lines(item) if start < line < close], default=close
        )
    return range(start, following)


def _remove_entries(data: dict[str, object], removals: Iterable[FieldPath]) -> None:
    for removal in sorted(removals, reverse=True):
        match removal:
            case (str(), int(position), str(name), int(index)):
                directives = cast("list[dict[str, object]]", data[DIRECTIVES_FIELD])
                owner = directives[position]
            case (str(name), int(index)):
                owner = data
            case _:
                continue
        values = cast("list[object]", owner[name])
        del values[index]
        if not values:
            owner[name] = None


def _edited_text(item: ParsedNode, removals: list[FieldPath]) -> str | None:
    try:
        text = item.path.read_bytes().decode("utf-8")
    except OSError, UnicodeDecodeError:
        return None
    parts = LINE_BREAK.split(text)
    lines = universal_newlines(text).split("\n")
    doomed: set[int] = set()
    for removal in removals:
        span = _span(item, removal, lines)
        if span is None:
            return None
        doomed.update(span)
        owner = removal[:-1]
        siblings = sum(
            1 for path in item.locations if len(path) == len(removal) and path[:-1] == owner
        )
        if siblings == sum(1 for path in removals if path[:-1] == owner):
            doomed.add(item.locations[owner])
    kept = [part for index, part in enumerate(parts) if (index // 2) + 1 not in doomed]
    edited = "".join(kept)
    expected = item.node.model_dump(mode="json")
    _remove_entries(expected, removals)
    parsed = parse_source(universal_newlines(edited), item.path)
    if not isinstance(parsed, ParsedNode) or parsed.node.model_dump(mode="json") != expected:
        return None
    return edited


def _edits(
    items: Sequence[ParsedNode], plan: _Plan
) -> tuple[dict[Path, str], list[str], list[Problem]]:
    holders = _holders(items)
    removals: dict[Path, list[FieldPath]] = {}
    pruned: list[str] = []
    problems: list[Problem] = []
    by_path = {item.path: item for item in items}
    for item in items:
        if item.node.id in plan.removed:
            continue
        for reference in references_of(item):
            if not _target_removed(reference, plan.removed, holders):
                continue
            if reference.field in PRUNED_FIELDS or reference.field == "target":
                removals.setdefault(item.path, []).append(_removal_path(reference))
                name = "pointer" if reference.field == "target" else reference.field
                pruned.append(f"{item.node.id}: {name} {reference.target}")
            else:
                problems.append(_edge_problem(item, reference))
    edits: dict[Path, str] = {}
    for path, paths in removals.items():
        edited = _edited_text(by_path[path], paths)
        if edited is None:
            message = (
                "The command cannot remove an entry from this file. "
                "Write each list entry on its own line, then run the command again."
            )
            problems.append(Problem(path, by_path[path].line_of(paths[0]), "select", message))
        else:
            edits[path] = edited
    return edits, pruned, problems


def _doomed_paths(repository: Path, items: Sequence[ParsedNode], removed: set[str]) -> list[Path]:
    paths: list[Path] = []
    for item in items:
        if item.node.id not in removed:
            continue
        folder = item.path.parent
        paths.append(folder if folder.parent == repository / SKILLS_FOLDER else item.path)
    vocabularies = repository / LANGUAGE_FOLDER / BRANCH_FOLDER
    paths += [
        vocabularies / f"{node_id}{BRANCH_SUFFIX}"
        for node_id in sorted(removed)
        if (vocabularies / f"{node_id}{BRANCH_SUFFIX}").is_file()
    ]
    return sorted(paths)


def _remove_empty_folders(repository: Path, paths: Iterable[Path]) -> None:
    top = repository / KNOWLEDGE_FOLDER
    for path in paths:
        folder = path.parent
        while folder.is_relative_to(top) and folder != top:
            try:
                folder.rmdir()
            except OSError:
                break
            folder = folder.parent


def _write(repository: Path, doomed: Sequence[Path], edits: Mapping[Path, str]) -> list[Problem]:
    problems: list[Problem] = []
    for path in doomed:
        try:
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
        except OSError as error:
            message = f"The command cannot remove this path: {error.strerror!a}."
            problems.append(Problem(path, 1, "select", message))
    _remove_empty_folders(repository, doomed)
    for path, text in edits.items():
        try:
            path.write_bytes(text.encode("utf-8"))
        except OSError as error:
            message = f"The command cannot change this file: {error.strerror!a}."
            problems.append(Problem(path, 1, "select", message))
    return problems


def select_disciplines(repository: Path) -> SelectionReport:
    answer, problems = read_answer(repository)
    if problems or answer is None:
        return SelectionReport(None, (), (), [], problems)
    items, problems = parse_tree(node_folders(repository))
    if problems:
        return SelectionReport(None, (), (), [], problems)
    plan = _plan(items, answer)
    selected = tuple(sorted(plan.selected))
    edits, pruned, problems = _edits(items, plan)
    if problems:
        return SelectionReport(selected, (), (), plan.notes, problems)
    doomed = _doomed_paths(repository, items, plan.removed)
    problems = _write(repository, doomed, edits)
    return SelectionReport(selected, tuple(doomed), tuple(pruned), plan.notes, problems)
