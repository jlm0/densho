from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping
    from pathlib import Path, PurePosixPath

    from engine.generated.metamodel import Node

type FieldPath = tuple[str | int, ...]


@dataclass(frozen=True, slots=True, order=True)
class Problem:
    path: Path
    line: int
    code: str
    message: str

    def __str__(self) -> str:
        return f"{self.path}:{self.line}: {self.code}: {self.message}"


@dataclass(frozen=True, slots=True, order=True)
class Script:
    path: PurePosixPath
    data: bytes
    executable: bool


@dataclass(frozen=True, slots=True, order=True)
class StepFile:
    id: str
    sections: tuple[tuple[str, str], ...]

    def section(self, name: str) -> str:
        return dict(self.sections)[name]


@dataclass(frozen=True, slots=True)
class ParsedNode:
    path: Path
    node: Node
    locations: Mapping[FieldPath, int]
    scripts: tuple[Script, ...] = ()
    step_files: tuple[StepFile, ...] = ()

    def line_of(self, field_path: FieldPath) -> int:
        return line_of(self.locations, field_path)


def line_of(locations: Mapping[FieldPath, int], field_path: FieldPath) -> int:
    for end in range(len(field_path), -1, -1):
        line = locations.get(field_path[:end])
        if line is not None:
            return line
    return 1
