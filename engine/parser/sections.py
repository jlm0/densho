from dataclasses import dataclass
from typing import TYPE_CHECKING

from markdown_it import MarkdownIt

from engine.parser.body import read_body
from engine.parser.result import Problem

if TYPE_CHECKING:
    from collections.abc import Sequence
    from pathlib import Path

    from markdown_it.token import Token

SECTION_TAG = "h2"
SPLIT_TAGS = frozenset({"h1", SECTION_TAG})

type Sections = tuple[tuple[str, str], ...]


@dataclass(frozen=True, slots=True)
class Owner:
    label: str
    code: str


STEP_FILE = Owner("step file", "step-file")


def section_order(names: Sequence[str]) -> str:
    return ", ".join(f"## {name}" for name in names)


def section_problems(
    text: str,
    path: Path,
    names: Sequence[str],
    first_line: int = 1,
    owner: Owner = STEP_FILE,
) -> Sections | list[Problem]:
    label, code = owner.label, owner.code
    order = section_order(names)
    offset = first_line - 1
    body = read_body(text, first_line, path)
    problems = list(body.problems)
    if {"definition", "directives"} & set(body.fields):
        message = f"The {label} holds no ## Definition and no ## Directives. Put them in a node."
        problems.append(Problem(path, first_line, code, message))
    lines = text.split("\n")
    tokens = MarkdownIt("commonmark").parse(text)
    heads = [
        index
        for index, token in enumerate(tokens)
        if token.type == "heading_open" and token.level == 0 and token.tag in SPLIT_TAGS
    ]
    found = [_heading(tokens, index) for index in heads]
    if found != list(names):
        line = _start(tokens[heads[0]]) + 1 + offset if heads else first_line
        message = f"Give the {label} exactly these sections in this order: {order}."
        problems.append(Problem(path, line, code, message))
    elif _has_text(lines[: _start(tokens[heads[0]])]):
        message = f"Put each line of the {label} in a section: {order}."
        problems.append(Problem(path, first_line, code, message))
    if problems:
        return sorted(problems)
    sections: list[tuple[str, str]] = []
    for position, index in enumerate(heads):
        end = _start(tokens[heads[position + 1]]) if position + 1 < len(heads) else len(lines)
        content = "\n".join(lines[_end(tokens[index]) : end]).strip("\n")
        if not content.strip():
            message = f"Write the text of ## {found[position]}."
            problems.append(Problem(path, _start(tokens[index]) + 1 + offset, code, message))
        sections.append((found[position], content))
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
