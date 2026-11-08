import hashlib
import json
import re
from typing import TYPE_CHECKING

from markdown_it import MarkdownIt

from engine.git import ignored_paths
from engine.parser.body import read_body
from engine.parser.result import Problem, StepFile

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence
    from pathlib import Path

    from markdown_it.token import Token

STEPS_FOLDER_NAME = "steps"
STEP_SUFFIX = ".md"
STEP_SECTIONS = ("Inputs", "Procedure", "Output", "Exit gate")
STEP_ID = re.compile(r"[a-z][a-z0-9]*(-[a-z0-9]+)*")
CONTROL_CHARACTER = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]")
SECTION_TAG = "h2"
SPLIT_TAGS = frozenset({"h1", SECTION_TAG})
ORDER = ", ".join(f"## {name}" for name in STEP_SECTIONS)


def step_files_digest(step_files: Sequence[StepFile]) -> str:
    listing = [
        [step.id, [list(section) for section in step.sections]] for step in sorted(step_files)
    ]
    return hashlib.sha256(json.dumps(listing).encode("utf-8")).hexdigest()


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
    found = step_file_problems(text, path)
    if isinstance(found, list):
        problems.extend(found)
        return None
    return StepFile(path.stem, found)


def step_file_problems(text: str, path: Path) -> tuple[tuple[str, str], ...] | list[Problem]:
    control = sorted(
        {text.count("\n", 0, match.start()) + 1 for match in CONTROL_CHARACTER.finditer(text)}
    )
    if control:
        message = "Remove the control character from this line."
        return [Problem(path, line, "control-character", message) for line in control]
    body = read_body(text, 1, path)
    problems = list(body.problems)
    if {"definition", "directives"} & set(body.fields):
        message = "A step file holds no ## Definition and no ## Directives. Put them in a node."
        problems.append(Problem(path, 1, "step-file", message))
    lines = text.split("\n")
    tokens = MarkdownIt("commonmark").parse(text)
    heads = [
        index
        for index, token in enumerate(tokens)
        if token.type == "heading_open" and token.level == 0 and token.tag in SPLIT_TAGS
    ]
    names = [_heading(tokens, index) for index in heads]
    if names != list(STEP_SECTIONS):
        line = _start(tokens[heads[0]]) + 1 if heads else 1
        message = f"Give the step file exactly these sections in this order: {ORDER}."
        problems.append(Problem(path, line, "step-file", message))
    elif _has_text(lines[: _start(tokens[heads[0]])]):
        message = f"Put each line of the step file in a section: {ORDER}."
        problems.append(Problem(path, 1, "step-file", message))
    if problems:
        return sorted(problems)
    sections: list[tuple[str, str]] = []
    for position, index in enumerate(heads):
        end = _start(tokens[heads[position + 1]]) if position + 1 < len(heads) else len(lines)
        content = "\n".join(lines[_end(tokens[index]) : end]).strip("\n")
        if not content.strip():
            message = f"Write the text of ## {names[position]}."
            problems.append(Problem(path, _start(tokens[index]) + 1, "step-file", message))
        sections.append((names[position], content))
    return problems or tuple(sections)


def _heading(tokens: list[Token], index: int) -> str:
    opener = tokens[index]
    text = tokens[index + 1].content.strip()
    return text if opener.tag == SECTION_TAG else f"# {text}"


def _start(token: Token) -> int:
    return token.map[0] if token.map else 0


def _end(token: Token) -> int:
    return token.map[1] if token.map else 0


def _has_text(lines: Sequence[str]) -> bool:
    return any(line.strip() for line in lines)
