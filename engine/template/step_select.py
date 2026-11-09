import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

from engine.generated.metamodel import Skill
from engine.parser.front_matter import DELIMITER
from engine.parser.node import universal_newlines
from engine.parser.result import Branch, Problem, StepCopies, StepFile
from engine.parser.steps import read_step_source

if TYPE_CHECKING:
    from collections.abc import Collection, Mapping, Sequence

    from engine.parser.result import FieldPath, ParsedNode

LIST_FIELDS = ("pages", "directives", "branches")
LINE_BREAK = re.compile(r"(\r\n|\r|\n)")
ENTRY_DEPTH = 2


@dataclass(slots=True)
class StepChanges:
    edits: dict[Path, str] = field(default_factory=dict[Path, str])
    pruned: list[str] = field(default_factory=list[str])
    problems: list[Problem] = field(default_factory=list[Problem])


def step_edits(
    items: Sequence[ParsedNode], removed: Collection[str], holders: Mapping[str, str]
) -> StepChanges:
    changes = StepChanges()
    for item in items:
        if not isinstance(item.node, Skill) or item.node.id in removed:
            continue
        for step in item.step_files:
            if step.copies is None or step.path is None:
                continue
            gone = {name for name, _ in step.copies.copied() if holders.get(name, name) in removed}
            pages = {page.target for page in step.copies.pages if page.target in removed}
            if gone or pages:
                _edit(step, step.copies, gone, pages, changes)
                label = f"{item.node.id}/{step.id}"
                changes.pruned += [f"{label}: directive {name}" for name in sorted(gone)]
                changes.pruned += [f"{label}: page {name}" for name in sorted(pages)]
    return changes


def _kept(copies: StepCopies, gone: Collection[str], pages: Collection[str]) -> StepCopies:
    branches = (
        Branch(branch.condition, tuple(name for name in branch.directives if name not in gone))
        for branch in copies.branches
    )
    return StepCopies(
        copies.title,
        tuple(page for page in copies.pages if page.target not in pages),
        tuple(name for name in copies.directives if name not in gone),
        tuple(branch for branch in branches if branch.directives),
        copies.missing_rules,
    )


def _doomed(
    step: StepFile, copies: StepCopies, gone: Collection[str], pages: Collection[str]
) -> list[FieldPath]:
    doomed: list[FieldPath] = [
        ("pages", index) for index, page in enumerate(copies.pages) if page.target in pages
    ]
    doomed += [
        ("directives", index) for index, name in enumerate(copies.directives) if name in gone
    ]
    for position, branch in enumerate(copies.branches):
        if all(name in gone for name in branch.directives):
            doomed.append(("branches", position))
            continue
        doomed += [
            ("branches", position, "directives", index)
            for index, name in enumerate(branch.directives)
            if name in gone
        ]
    kept = _kept(copies, gone, pages)
    doomed += [(name,) for name in LIST_FIELDS if getattr(copies, name) and not getattr(kept, name)]
    return [path for path in doomed if path in step.locations]


def _span(step: StepFile, field_path: FieldPath, lines: Sequence[str]) -> range:
    start = step.locations[field_path]
    if field_path[0] == "directives" or len(field_path) != ENTRY_DEPTH:
        return range(start, start + 1)
    close = lines.index(DELIMITER, 1) + 1 if DELIMITER in lines[1:] else len(lines) + 1
    following = step.locations.get((field_path[0], int(field_path[1]) + 1))
    tops = [line for path, line in step.locations.items() if len(path) == 1 and line > start]
    return range(start, following or min([*tops, close]))


def _edit(
    step: StepFile,
    copies: StepCopies,
    gone: Collection[str],
    pages: Collection[str],
    changes: StepChanges,
) -> None:
    path = step.path
    if path is None:
        return
    try:
        text = path.read_bytes().decode("utf-8")
    except OSError, UnicodeDecodeError:
        text = None
    source = universal_newlines(text or "")
    lines = source.split("\n")
    parts = LINE_BREAK.split(text or "")
    doomed = {
        line
        for field_path in _doomed(step, copies, gone, pages)
        for line in _span(step, field_path, lines)
    }
    edited = "".join(part for index, part in enumerate(parts) if (index // 2) + 1 not in doomed)
    parsed = read_step_source(universal_newlines(edited), path) if text is not None else None
    kept = _kept(copies, gone, pages)
    if isinstance(parsed, StepFile) and (parsed.copies, parsed.sections) == (kept, step.sections):
        changes.edits[path] = edited
        return
    message = (
        "The command cannot remove an entry from this step file. "
        "Write each list entry on its own line, then run the command again."
    )
    changes.problems.append(Problem(path, 1, "select", message))
