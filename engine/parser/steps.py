import hashlib
import json
import re
from dataclasses import asdict
from typing import TYPE_CHECKING, cast

from engine import tree_copies
from engine.git import ignored_paths
from engine.parser.front_matter import DELIMITER, read_front_matter
from engine.parser.result import Branch, Page, Problem, StepCopies, StepFile, line_of
from engine.parser.sections import section_problems

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping, Sequence
    from pathlib import Path

    from engine.parser.result import FieldPath

STEPS_FOLDER_NAME = "steps"
STEP_SUFFIX = ".md"
COPY_SECTIONS = ("Procedure", "Output")
COPY_KEYS = ("title", "pages", "directives", "branches", "missing_rules")
PAGE_KEYS = ("target", "trigger")
BRANCH_KEYS = ("condition", "directives")
CONDITION_START = "If "
STEP_ID = re.compile(r"[a-z][a-z0-9]*(-[a-z0-9]+)*")
SINGLE_LINE = re.compile(r"\S(?: *\S)*")
CONTROL_CHARACTER = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]")


def step_files_digest(step_files: Sequence[StepFile]) -> str:
    listing = [_digest_entry(step) for step in sorted(step_files)]
    return hashlib.sha256(json.dumps(listing).encode("utf-8")).hexdigest()


def _digest_entry(step: StepFile) -> list[object]:
    entry: list[object] = [step.id, [list(section) for section in step.sections]]
    if step.copies is not None:
        entry.append(asdict(step.copies))
    return entry


def read_step_files(
    root: Path, found: Mapping[Path, Sequence[Path]], problems: list[Problem]
) -> dict[Path, tuple[StepFile, ...]]:
    ignored = ignored_paths(root, [path for paths in found.values() for path in paths])
    step_files: dict[Path, tuple[StepFile, ...]] = {}
    for folder, paths in found.items():
        read = [
            step
            for path in paths
            if path not in ignored and (step := _read_step(path, folder, problems))
        ]
        step_files[folder] = tuple(sorted(read))
    return step_files


def _place_problem(path: Path, folder: Path) -> tuple[str, str] | None:
    if path.parent != folder:
        return "step-file", "Put each step file directly in steps/."
    if path.suffix != STEP_SUFFIX or not STEP_ID.fullmatch(path.stem):
        return (
            "step-file",
            "Name each step file with the ID of its step and .md, such as unit-testing.md.",
        )
    if not path.is_file():
        return "read", "A step file must be a regular file."
    return None


def _read_step(path: Path, folder: Path, problems: list[Problem]) -> StepFile | None:
    place = _place_problem(path, folder)
    if place is not None:
        problems.append(Problem(path, 1, *place))
        return None
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        problems.append(Problem(path, 1, "encoding", "The file is not valid UTF-8."))
        return None
    except OSError as error:
        problems.append(Problem(path, 1, "read", str(error)))
        return None
    found = read_step_source(text, path)
    if isinstance(found, list):
        problems.extend(found)
        return None
    return found


def read_step_source(text: str, path: Path) -> StepFile | list[Problem]:
    control = sorted(
        {text.count("\n", 0, match.start()) + 1 for match in CONTROL_CHARACTER.finditer(text)}
    )
    if control:
        message = "Remove the control character from this line."
        return [Problem(path, line, "control-character", message) for line in control]
    if text.split("\n", 1)[0] != DELIMITER:
        sections = tree_copies.tree_step_sections(text, path)
        return sections if isinstance(sections, list) else StepFile(path.stem, sections)
    front = read_front_matter(text, path)
    if isinstance(front, list):
        return front
    copies = _copies(front.data, front.locations, path)
    sections = section_problems(front.body, path, COPY_SECTIONS, front.body_line)
    problems = [
        *(copies if isinstance(copies, list) else []),
        *(sections if isinstance(sections, list) else []),
    ]
    if problems or isinstance(copies, list) or isinstance(sections, list):
        return sorted(problems)
    return StepFile(path.stem, sections, copies, path, front.locations)


class _Reader:
    def __init__(self, locations: Mapping[FieldPath, int], path: Path) -> None:
        self.locations = locations
        self.path = path
        self.problems: list[Problem] = []

    def report(self, field_path: FieldPath, message: str) -> None:
        line = line_of(self.locations, field_path)
        self.problems.append(Problem(self.path, line, "step-file", message))

    def text(self, value: object, field_path: FieldPath, name: str) -> str | None:
        if isinstance(value, str) and SINGLE_LINE.fullmatch(value):
            return value
        self.report(field_path, f"Write {name} as text on 1 line.")
        return None

    def identifier(self, value: object, field_path: FieldPath) -> str | None:
        if isinstance(value, str) and STEP_ID.fullmatch(value):
            return value
        self.report(field_path, "Write each ID in lowercase words joined by hyphens.")
        return None

    def entries(self, value: object, field_path: FieldPath, name: str) -> list[object]:
        if isinstance(value, list):
            return cast("list[object]", value)
        self.report(field_path, f"Write {name} as a list.")
        return []

    def mapping(
        self, value: object, field_path: FieldPath, keys: Sequence[str], name: str
    ) -> dict[str, object] | None:
        fields = cast("dict[str, object]", value) if isinstance(value, dict) else None
        if fields is None or sorted(fields) != sorted(keys):
            listed = " and ".join(keys)
            self.report(field_path, f"Give each entry of {name} exactly the keys {listed}.")
            return None
        return fields

    def page(self, value: object, field_path: FieldPath) -> Page | None:
        fields = self.mapping(value, field_path, PAGE_KEYS, "pages")
        if fields is None:
            return None
        target = self.identifier(fields["target"], (*field_path, "target"))
        trigger = self.text(fields["trigger"], (*field_path, "trigger"), "the trigger")
        return None if target is None or trigger is None else Page(target, trigger)

    def branch(self, value: object, field_path: FieldPath) -> Branch | None:
        fields = self.mapping(value, field_path, BRANCH_KEYS, "branches")
        if fields is None:
            return None
        place = (*field_path, "condition")
        condition = self.text(fields["condition"], place, "the condition")
        if condition is not None and (
            not condition.startswith(CONDITION_START) or condition.endswith(".")
        ):
            self.report(place, "Start the condition with If, and end it with no period.")
            condition = None
        names = _identifiers(self, fields["directives"], (*field_path, "directives"))
        if not names:
            self.report((*field_path, "directives"), "Name at least 1 directive in the branch.")
        return None if condition is None or not names else Branch(condition, names)

    def rule(self, value: object, field_path: FieldPath) -> str | None:
        return self.text(value, field_path, "each missing rule")

    def each[ItemT](
        self,
        data: Mapping[str, object],
        name: str,
        read: Callable[[object, FieldPath], ItemT | None],
    ) -> tuple[ItemT, ...]:
        if name not in data:
            return ()
        values = self.entries(data[name], (name,), name)
        found = [read(value, (name, index)) for index, value in enumerate(values)]
        return tuple(entry for entry in found if entry is not None)


def _copies(
    data: Mapping[str, object], locations: Mapping[FieldPath, int], path: Path
) -> StepCopies | list[Problem]:
    reader = _Reader(locations, path)
    for key in data:
        if key not in COPY_KEYS:
            listed = ", ".join(COPY_KEYS)
            reader.report((key,), f"A step file has no key {key}. Use only: {listed}.")
    if "title" not in data:
        reader.report((), "Give the step a title.")
    title = reader.text(data.get("title"), ("title",), "the title") if "title" in data else None
    core = _identifiers(reader, data["directives"], ("directives",)) if "directives" in data else ()
    copies = StepCopies(
        title or "",
        reader.each(data, "pages", reader.page),
        core,
        reader.each(data, "branches", reader.branch),
        reader.each(data, "missing_rules", reader.rule),
    )
    seen: set[str] = set()
    for name, field_path in copies.copied():
        if name in seen:
            reader.report(field_path, f"The step names {name} twice. Name it once.")
        seen.add(name)
    return reader.problems or copies


def _identifiers(reader: _Reader, value: object, field_path: FieldPath) -> tuple[str, ...]:
    values = reader.entries(value, field_path, "directives")
    found = [reader.identifier(entry, (*field_path, index)) for index, entry in enumerate(values)]
    return tuple(name for name in found if name is not None)
