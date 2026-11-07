import re
from pathlib import PurePosixPath
from typing import TYPE_CHECKING
from urllib.parse import urlsplit

from engine.graph.references import problem_at

if TYPE_CHECKING:
    from collections.abc import Iterator, Sequence
    from pathlib import Path

    from engine.parser.result import FieldPath, ParsedNode, Problem

SOURCE_CODE = "source-form"
WEB_SCHEMES = frozenset({"https", "http"})
SCHEME = re.compile(r"[A-Za-z][A-Za-z0-9+.-]*://")
FORMS = "Write a URL, a path from the repository root, or a citation of two or more words."


def _url_message(value: str) -> str | None:
    parts = urlsplit(value)
    if parts.scheme.casefold() not in WEB_SCHEMES:
        return "Write the URL with https or http."
    if "@" in parts.netloc:
        return "Remove the user name and the password from the URL."
    if not parts.hostname:
        return "The URL names no host. Add the host."
    return None


def _path_message(value: str, repository: Path) -> str | None:
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or "\\" in value:
        return "Write the path from the repository root, with no `..`."
    if not (repository / path).is_file():
        return f"No file in the repository has this path. {FORMS}"
    return None


def _source_message(value: str, repository: Path) -> str | None:
    if SCHEME.match(value):
        return _url_message(value)
    if " " not in value and ("/" in value or "\\" in value):
        return _path_message(value, repository)
    if " " not in value:
        return FORMS
    return None


def _sources(item: ParsedNode) -> Iterator[tuple[FieldPath, str]]:
    held: list[tuple[FieldPath, list[str] | None]] = [
        (("sources",), item.node.sources),
        *(
            (("directives", index, "sources"), directive.sources)
            for index, directive in enumerate(item.node.directives or [])
        ),
    ]
    for field_path, values in held:
        for position, value in enumerate(values or []):
            yield (*field_path, position), value


def source_problems(items: Sequence[ParsedNode], repository: Path) -> list[Problem]:
    return [
        problem_at(item, field_path, SOURCE_CODE, message)
        for item in items
        for field_path, value in _sources(item)
        if (message := _source_message(value, repository)) is not None
    ]
