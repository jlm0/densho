import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, cast

from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap, CommentedSeq
from ruamel.yaml.error import MarkedYAMLError, YAMLError

from knowledge_architecture.parser.result import FieldPath, Problem

if TYPE_CHECKING:
    from pathlib import Path

DELIMITER = "---"
FIRST_LINE = 2
MERGE_KEY = "<<"
DOCUMENT_END = re.compile(r"\.\.\.(\s|$)")
LONE_SURROGATE = re.compile(r"[\ud800-\udfff]")
SURROGATE_MESSAGE = "A YAML escape gives a character that is not valid. Write the character itself."


@dataclass(frozen=True, slots=True)
class FrontMatter:
    data: dict[str, object]
    locations: dict[FieldPath, int]
    body: str
    body_line: int


@dataclass(slots=True)
class _Converter:
    path: Path
    locations: dict[FieldPath, int] = field(default_factory=dict[FieldPath, int])
    problems: list[Problem] = field(default_factory=list[Problem])

    def plain(self, value: object, field_path: FieldPath) -> object:
        if isinstance(value, CommentedMap):
            return self._mapping(cast("Any", value), field_path)
        if isinstance(value, CommentedSeq):
            return self._sequence(cast("Any", value), field_path)
        if isinstance(value, str):
            if LONE_SURROGATE.search(value):
                line = self.locations[field_path]
                self.problems.append(Problem(self.path, line, "yaml", SURROGATE_MESSAGE))
            return str(value)
        return value

    def _mapping(self, mapping: Any, field_path: FieldPath) -> dict[str, object]:  # noqa: ANN401
        result: dict[str, object] = {}
        for key, item in mapping.items():
            line = FIRST_LINE + cast("int", mapping.lc.key(key)[0])
            if not isinstance(key, str):
                self.problems.append(Problem(self.path, line, "yaml", "Each key must be a string."))
                continue
            if LONE_SURROGATE.search(key):
                self.problems.append(Problem(self.path, line, "yaml", SURROGATE_MESSAGE))
                continue
            child = (*field_path, str(key))
            self.locations[child] = line
            result[str(key)] = self.plain(item, child)
        return result

    def _sequence(self, sequence: Any, field_path: FieldPath) -> list[object]:  # noqa: ANN401
        result: list[object] = []
        for index, item in enumerate(sequence):
            child = (*field_path, index)
            self.locations[child] = FIRST_LINE + cast("int", sequence.lc.item(index)[0])
            result.append(self.plain(item, child))
        return result


def _closing_line(lines: list[str], path: Path) -> int | Problem:
    if lines[0] != DELIMITER:
        return Problem(path, 1, "front-matter", "The file must start with a --- line.")
    if DELIMITER not in lines[1:]:
        return Problem(path, 1, "front-matter", "The front matter has no closing --- line.")
    close = lines.index(DELIMITER, 1)
    for number, line in enumerate(lines[1:close], start=FIRST_LINE):
        if DOCUMENT_END.match(line):
            return Problem(path, number, "front-matter", "Remove the ... line.")
    return close


def read_front_matter(text: str, path: Path) -> FrontMatter | list[Problem]:
    lines = text.split("\n")
    close = _closing_line(lines, path)
    if isinstance(close, Problem):
        return [close]

    loaded = _load("\n".join(lines[1:close]), path)
    if isinstance(loaded, Problem):
        return [loaded]
    if not isinstance(loaded, CommentedMap):
        return [Problem(path, 1, "front-matter", "The front matter must be a YAML mapping.")]

    converter = _Converter(path)
    data = cast("dict[str, object]", converter.plain(loaded, ()))
    if converter.problems:
        return converter.problems
    return FrontMatter(data, converter.locations, "\n".join(lines[close + 1 :]), close + 2)


def _load(source: str, path: Path) -> object:
    yaml: Any = YAML(typ="rt")
    try:
        feature_line = _forbidden_feature_line(source)
        if feature_line is not None:
            message = "The front matter must not use YAML tags, anchors, aliases, or merge keys."
            return Problem(path, FIRST_LINE + feature_line, "yaml-feature", message)
        return cast("object", yaml.load(source))
    except YAMLError as error:
        return _yaml_problem(error, path)
    except (ValueError, OverflowError, RecursionError) as error:
        line = FIRST_LINE + _unreadable_value_line(source)
        message = f"YAML cannot read a value: {_one_line(error)}"
        return Problem(path, line, "yaml", message)


def _one_line(error: BaseException) -> str:
    return " ".join(str(error).split())


def _unreadable_value_line(source: str) -> int:
    yaml: Any = YAML(typ="rt")
    for event in yaml.parse(source):
        value = getattr(event, "value", None)
        if isinstance(value, str) and event.implicit[0] and not _is_readable(value):
            return cast("int", event.start_mark.line)
    return 0


def _is_readable(value: str) -> bool:
    yaml: Any = YAML(typ="rt")
    try:
        yaml.load(value)
    except YAMLError, ValueError, OverflowError:
        return False
    return True


def _forbidden_feature_line(source: str) -> int | None:
    yaml: Any = YAML(typ="rt")
    for event in yaml.parse(source):
        if _uses_forbidden_feature(event):
            return cast("int", event.start_mark.line)
    return None


def _uses_forbidden_feature(event: object) -> bool:
    if getattr(event, "anchor", None) is not None or getattr(event, "tag", None) is not None:
        return True
    return getattr(event, "value", None) == MERGE_KEY and getattr(event, "implicit", (False,))[0]


def _yaml_problem(error: YAMLError, path: Path) -> Problem:
    if isinstance(error, MarkedYAMLError):
        marked: Any = error
        if marked.problem_mark is not None:
            return Problem(
                path,
                FIRST_LINE + cast("int", marked.problem_mark.line),
                "yaml",
                " ".join(str(marked.problem).split()),
            )
    return Problem(path, FIRST_LINE, "yaml", _one_line(error))
