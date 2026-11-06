import re
from dataclasses import dataclass, field
from types import NoneType
from typing import TYPE_CHECKING, cast, get_args, get_origin

from markdown_it import MarkdownIt
from markdown_it.tree import SyntaxTreeNode

from engine.generated.metamodel import Directive
from engine.parser.result import FieldPath, Problem

if TYPE_CHECKING:
    from pathlib import Path

    from markdown_it.token import Token

DEFINITION = "Definition"
DIRECTIVES = "Directives"
SECTION_LEVEL = "h2"
SPLIT_LEVELS = frozenset({"h1", SECTION_LEVEL})
LOOKALIKES = {
    "definition": DEFINITION,
    "definitions": DEFINITION,
    "directive": DIRECTIVES,
    "directives": DIRECTIVES,
}
RANKS = {DEFINITION: 0, DIRECTIVES: 1}
OTHER_RANK = 2
NESTING_LIMIT = 16
FENCE_INDENT_LIMIT = 4
COMMENT_OR_NON_LETTER = re.compile(r"<!--.*?-->|[^a-z]")
DIRECTIVE_LINE = re.compile(r"(?P<text>.*\S) \^(?P<id>\S+)")
METADATA_ENTRY = re.compile(r"(?P<key>[^\s:]+): +(?P<value>.*)")
REPEATED_SPACES = re.compile(r" {2,}")


@dataclass(frozen=True, slots=True)
class Body:
    fields: dict[str, object]
    locations: dict[FieldPath, int]
    problems: list[Problem]


@dataclass(frozen=True, slots=True)
class _Section:
    name: str | None
    start: int
    content_start: int
    end: int
    tokens: list[Token]


@dataclass(slots=True)
class _Reader:
    path: Path
    first_line: int
    lines: list[str]
    fields: dict[str, object] = field(default_factory=dict[str, object])
    locations: dict[FieldPath, int] = field(default_factory=dict[FieldPath, int])
    problems: list[Problem] = field(default_factory=list[Problem])

    def line(self, index: int) -> int:
        return self.first_line + index

    def problem(self, index: int, code: str, message: str) -> None:
        self.problems.append(Problem(self.path, self.line(index), code, message))


def read_body(text: str, first_line: int, path: Path) -> Body:
    reader = _Reader(path, first_line, text.split("\n"))
    tokens = MarkdownIt("commonmark").parse(text)
    _check_markdown(tokens, reader)
    _check_lookalikes(tokens, reader)
    sections = _sections(tokens, reader.lines)
    _check_order(sections, reader)
    _check_swallowed_sections(tokens, sections, reader)
    for section in sections:
        if section.name == DEFINITION:
            content = reader.lines[section.content_start : section.end]
            reader.fields["definition"] = "\n".join(content).strip("\n")
            reader.locations["definition",] = reader.line(section.start)
        elif section.name == DIRECTIVES:
            _read_directives(section, reader)
    _read_other_content(sections, reader)
    return Body(reader.fields, reader.locations, reader.problems)


def _map_start(item: Token | SyntaxTreeNode) -> int:
    source_map = item.map
    return source_map[0] if source_map else 0


def _map_end(item: Token | SyntaxTreeNode) -> int:
    source_map = item.map
    return source_map[1] if source_map else 0


def _check_markdown(tokens: list[Token], reader: _Reader) -> None:
    deep = next((t for t in tokens if t.map is not None and t.level >= NESTING_LIMIT), None)
    if deep is not None:
        reader.problem(_map_start(deep), "markdown", "The Markdown nests too deep.")
    for token in tokens:
        if token.type == "html_block" or _has_html_comment(token):
            message = "Remove the raw HTML. A reader of the rendered file cannot see all of it."
            reader.problem(_map_start(token), "markdown", message)
        elif token.type == "fence" and token.level == 0 and not _is_closed(token, reader.lines):
            reader.problem(_map_start(token), "markdown", "The code fence has no closing line.")


def _has_html_comment(token: Token) -> bool:
    return any(
        child.type == "html_inline" and child.content.startswith("<!--")
        for child in token.children or []
    )


def _is_closed(fence: Token, lines: list[str]) -> bool:
    start, end = _map_start(fence), _map_end(fence)
    closing = lines[end - 1]
    indent = len(closing) - len(closing.lstrip())
    marker = closing.strip()
    return (
        end - start > 1
        and indent < FENCE_INDENT_LIMIT
        and len(marker) >= len(fence.markup)
        and set(marker) == {fence.markup[0]}
    )


def _section_name(text: str) -> str | None:
    return LOOKALIKES.get(COMMENT_OR_NON_LETTER.sub("", text.casefold()))


def _check_lookalikes(tokens: list[Token], reader: _Reader) -> None:
    for index, token in enumerate(tokens):
        if token.type not in {"inline", "code_block"}:
            continue
        opener = tokens[index - 1]
        is_section = (
            opener.type == "heading_open"
            and opener.level == 0
            and opener.tag == SECTION_LEVEL
            and token.content in RANKS
        )
        if is_section:
            continue
        for offset, line in enumerate(token.content.split("\n")):
            expected = _section_name(line)
            if expected is not None:
                message = f"Use the exact heading ## {expected} at the top level."
                reader.problem(_map_start(token) + offset, "section", message)


def _sections(tokens: list[Token], lines: list[str]) -> list[_Section]:
    splits = [
        index
        for index, token in enumerate(tokens)
        if token.type == "heading_open" and token.level == 0 and token.tag in SPLIT_LEVELS
    ]
    first_end = _map_start(tokens[splits[0]]) if splits else len(lines)
    sections = [_Section(None, 0, 0, first_end, [])]
    for position, index in enumerate(splits):
        heading = tokens[index]
        following = splits[position + 1] if position + 1 < len(splits) else None
        sections.append(
            _Section(
                _section_name(tokens[index + 1].content),
                _map_start(heading),
                _map_end(heading),
                _map_start(tokens[following]) if following is not None else len(lines),
                tokens[index + 3 : following],
            )
        )
    return sections


def _has_content(section: _Section, lines: list[str]) -> bool:
    return bool("".join(lines[section.start : section.end]).strip())


def _check_order(sections: list[_Section], reader: _Reader) -> None:
    highest = -1
    for section in sections:
        if section.name is None and not _has_content(section, reader.lines):
            continue
        rank = RANKS[section.name] if section.name else OTHER_RANK
        if section.name and rank == highest:
            reader.problem(section.start, "section", f"The file has a second ## {section.name}.")
        elif section.name and rank < highest:
            reader.problem(
                section.start,
                "section",
                f"Move ## {section.name}. The order is ## Definition, ## Directives, other text.",
            )
        highest = max(highest, rank)


def _check_swallowed_sections(
    tokens: list[Token], sections: list[_Section], reader: _Reader
) -> None:
    present = {section.name for section in sections}
    for token in tokens:
        if token.type != "fence" or token.level != 0:
            continue
        for offset, line in enumerate(token.content.split("\n"), start=1):
            expected = _section_name(line) if line.lstrip().startswith("#") else None
            if expected is not None and expected not in present:
                message = f"This code fence holds ## {expected}, and the file has no such section."
                reader.problem(_map_start(token) + offset, "markdown", message)


def _read_other_content(sections: list[_Section], reader: _Reader) -> None:
    lines = reader.lines
    other = [s for s in sections if s.name is None and _has_content(s, lines)]
    if not other:
        return
    end = other[-1].end
    start = next(i for i in range(other[0].start, end) if lines[i].strip())
    reader.fields["body"] = "\n".join(lines[start:end]).rstrip("\n")
    reader.locations["body",] = reader.line(start)


def _has_uncovered_line(
    start: int, end: int, blocks: list[SyntaxTreeNode], reader: _Reader
) -> bool:
    covered = {line for block in blocks for line in range(_map_start(block), _map_end(block))}
    for index in range(start, min(end, len(reader.lines))):
        if reader.lines[index].strip() and index not in covered:
            reader.problem(index, "directive", "This text is not part of a directive.")
            return True
    return False


def _read_directives(section: _Section, reader: _Reader) -> None:
    directives = cast("list[dict[str, object]]", reader.fields.setdefault("directives", []))
    reader.locations["directives",] = reader.line(section.start)
    blocks = SyntaxTreeNode(section.tokens).children
    found_problem = _has_uncovered_line(section.content_start, section.end, blocks, reader)
    for block in blocks:
        if block.type == "html_block":
            found_problem = True
        elif block.type != "bullet_list":
            reader.problem(_map_start(block), "directive", "Write each directive as a bullet.")
            found_problem = True
        else:
            for item in block.children:
                directive = _read_directive(item, len(directives), reader)
                if directive is None:
                    found_problem = True
                else:
                    directives.append(directive)
    if not directives and not found_problem:
        reader.problem(section.start, "directive", "The section has no directives.")


def _read_directive(item: SyntaxTreeNode, index: int, reader: _Reader) -> dict[str, object] | None:
    blocks = item.children
    start = _map_start(item)
    if not blocks or blocks[0].type != "paragraph":
        reader.problem(start, "directive", "Start the directive with its text and ^id.")
        return None
    extra = blocks[1:]
    unexpected = [
        block for position, block in enumerate(extra) if position or block.type != "bullet_list"
    ]
    if unexpected:
        message = "A directive holds only its text and one sub-list."
        reader.problem(_map_start(unexpected[0]), "directive", message)
        return None
    if _has_uncovered_line(start, _map_end(item), blocks, reader):
        return None
    match = DIRECTIVE_LINE.fullmatch(blocks[0].children[0].content)
    if match is None:
        message = "Write the directive on one line and end it with a space and ^id."
        reader.problem(start, "directive", message)
        return None
    root: FieldPath = ("directives", index)
    reader.locations[root] = reader.line(start)
    directive: dict[str, object] = {"id": match["id"], "text": match["text"]}
    if extra:
        _read_metadata(extra[0], directive, root, reader)
    return directive


def _read_metadata(
    block: SyntaxTreeNode, directive: dict[str, object], root: FieldPath, reader: _Reader
) -> None:
    for entry in block.children:
        start = _map_start(entry)
        pair = _metadata_pair(entry)
        if pair is None:
            message = (
                "Write each sub-bullet as one key: value line. "
                "Put a value with Markdown characters in backticks."
            )
            reader.problem(start, "directive", message)
            continue
        if _has_uncovered_line(start, _map_end(entry), entry.children, reader):
            continue
        key, value = pair
        line = reader.line(start)
        if _is_list_field(key):
            values = cast("list[object]", directive.setdefault(key, []))
            reader.locations.setdefault((*root, key), line)
            reader.locations[*root, key, len(values)] = line
            values.append(value)
        elif key in directive:
            reader.problem(start, "directive", f"The directive sets {key} twice.")
        else:
            directive[key] = value
            reader.locations[*root, key] = line


def _metadata_pair(entry: SyntaxTreeNode) -> tuple[str, str] | None:
    blocks = entry.children
    if len(blocks) != 1 or blocks[0].type != "paragraph":
        return None
    parts = blocks[0].children[0].children
    if not parts or parts[0].type != "text":
        return None
    match = METADATA_ENTRY.fullmatch(parts[0].content)
    if match is None:
        return None
    rest = parts[1:]
    if match["value"] and not rest:
        return match["key"], REPEATED_SPACES.sub(" ", match["value"])
    if not match["value"] and len(rest) == 1 and rest[0].type == "code_inline":
        return match["key"], rest[0].content
    return None


def _is_list_field(key: str) -> bool:
    info = Directive.model_fields.get(key)
    if info is None:
        return False
    choices = get_args(info.annotation) or (info.annotation,)
    return any(get_origin(choice) is list for choice in choices if choice is not NoneType)
