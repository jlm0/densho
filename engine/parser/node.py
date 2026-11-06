import re
from dataclasses import dataclass
from typing import TYPE_CHECKING, cast

from pydantic import BaseModel, ValidationError

from engine.generated.metamodel import (
    AlwaysPointer,
    Concept,
    Discipline,
    Domain,
    Node,
    PathPointer,
    PracticeArea,
    Root,
    Skill,
    SkillPointer,
    TextPointer,
)
from engine.layout import KNOWLEDGE_FOLDER, NODE_FILE_NAME
from engine.parser.body import read_body
from engine.parser.front_matter import read_front_matter
from engine.parser.result import FieldPath, ParsedNode, Problem, line_of

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping, Sequence
    from pathlib import Path

MARKDOWN_SUFFIXES = frozenset({".md", ".markdown", ".mdown", ".mkd"})
CONTROL_CHARACTER = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]")
NODE_CLASSES: tuple[type[Node], ...] = (Root, Domain, Discipline, PracticeArea, Concept, Skill)
POINTER_CLASSES: tuple[type[BaseModel], ...] = (
    AlwaysPointer,
    PathPointer,
    SkillPointer,
    TextPointer,
)
MARKDOWN_FIELDS = {
    "definition": "Put the definition in the ## Definition section.",
    "directives": "Put the directives in the ## Directives section.",
    "body": "Put the supporting text after the front matter.",
}


def _by_kind[ModelT: BaseModel](classes: Sequence[type[ModelT]]) -> dict[str, type[ModelT]]:
    return {f"ka:{model.__name__}": model for model in classes}


NODES_BY_KIND = _by_kind(NODE_CLASSES)
POINTERS_BY_KIND = _by_kind(POINTER_CLASSES)


@dataclass(frozen=True, slots=True)
class _Context:
    path: Path
    locations: Mapping[FieldPath, int]
    problems: list[Problem]

    def report(self, field_path: FieldPath, code: str, message: str) -> None:
        line = line_of(self.locations, field_path)
        self.problems.append(Problem(self.path, line, code, message))


def parse_source(text: str, path: Path) -> ParsedNode | list[Problem]:
    control_lines = {
        text.count("\n", 0, match.start()) + 1 for match in CONTROL_CHARACTER.finditer(text)
    }
    if control_lines:
        message = "Remove the control character from this line."
        return [Problem(path, line, "control-character", message) for line in sorted(control_lines)]
    front = read_front_matter(text, path)
    if isinstance(front, list):
        return front
    body = read_body(front.body, front.body_line, path)
    locations: dict[FieldPath, int] = {**front.locations, **body.locations}
    context = _Context(path, locations, list(body.problems))
    context.problems.extend(
        Problem(path, front.locations[key,], "markdown-field", message)
        for key, message in MARKDOWN_FIELDS.items()
        if key in front.data
    )

    data = {**front.data, **body.fields}
    model = _select(context, data.get("kind"), NODES_BY_KIND, (), "node")
    pointer_failed = _select_pointers(context, data)
    node = None
    if model is not None:
        node = _validate(context, model, data, (), skip_pointers=pointer_failed)
    if node is None or context.problems:
        return sorted(context.problems, key=lambda problem: problem.line)
    return ParsedNode(path, node, locations)


def universal_newlines(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def parse_file(path: Path) -> ParsedNode | list[Problem]:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return [Problem(path, 1, "encoding", "The file is not valid UTF-8.")]
    except OSError as error:
        return [Problem(path, 1, "read", str(error))]
    return parse_source(text, path)


def node_folders(repository: Path) -> list[Path]:
    return [repository / KNOWLEDGE_FOLDER]


def parse_tree(roots: Iterable[Path]) -> tuple[list[ParsedNode], list[Problem]]:
    nodes: list[ParsedNode] = []
    problems: list[Problem] = []
    for root in roots:
        if root.is_dir():
            _read_folder(root, nodes, problems)
        else:
            problems.append(Problem(root, 1, "folder", "The folder does not exist."))
    return nodes, problems


def _read_folder(root: Path, nodes: list[ParsedNode], problems: list[Problem]) -> None:
    def report_error(error: OSError) -> None:
        problems.append(Problem(root, 1, "read", str(error)))

    found = sorted(
        folder / name for folder, _, names in root.walk(on_error=report_error) for name in names
    )
    for path in found:
        if path.is_symlink():
            problems.append(Problem(path, 1, "symlink", "Replace the symbolic link with a file."))
        elif path.suffix.casefold() in MARKDOWN_SUFFIXES:
            _read_node_file(path, nodes, problems)


def _read_node_file(path: Path, nodes: list[ParsedNode], problems: list[Problem]) -> None:
    if path.name != NODE_FILE_NAME:
        message = f"A Markdown file in this folder must have the name {NODE_FILE_NAME}."
        problems.append(Problem(path, 1, "file-name", message))
        return
    parsed = parse_file(path)
    if isinstance(parsed, ParsedNode):
        nodes.append(parsed)
    else:
        problems.extend(parsed)


def _select[ModelT: BaseModel](
    context: _Context,
    kind: object,
    classes: Mapping[str, type[ModelT]],
    field_path: FieldPath,
    label: str,
) -> type[ModelT] | None:
    model = classes.get(kind) if isinstance(kind, str) else None
    if model is None:
        choices = ", ".join(classes)
        context.report((*field_path, "kind"), "kind", f"Set the {label} kind to: {choices}.")
    return model


def _select_pointers(context: _Context, data: dict[str, object]) -> bool:
    pointers = data.get("pointers")
    if not isinstance(pointers, list):
        return False
    entries = cast("list[object]", pointers)
    selected = [_read_pointer(context, entry, ("pointers", i)) for i, entry in enumerate(entries)]
    data["pointers"] = selected
    return None in selected


def _read_pointer(context: _Context, entry: object, field_path: FieldPath) -> BaseModel | None:
    if not isinstance(entry, dict):
        context.report(field_path, "kind", "A pointer must be a YAML mapping.")
        return None
    fields = cast("dict[str, object]", entry)
    model = _select(context, fields.get("kind"), POINTERS_BY_KIND, field_path, "pointer")
    if model is None:
        return None
    return _validate(context, model, fields, field_path)


def _validate[ModelT: BaseModel](
    context: _Context,
    model: type[ModelT],
    data: Mapping[str, object],
    field_path: FieldPath,
    *,
    skip_pointers: bool = False,
) -> ModelT | None:
    try:
        return model.model_validate(data)
    except ValidationError as error:
        for detail in error.errors():
            location: FieldPath = (*field_path, *detail["loc"])
            if skip_pointers and location[0] == "pointers":
                continue
            context.report(location, "schema", f"{_dotted(location)}: {detail['msg']}")
        return None


def _dotted(field_path: FieldPath) -> str:
    text = ""
    for part in field_path:
        if isinstance(part, int):
            text += f"[{part}]"
        else:
            text += f".{part}" if text else part
    return text
