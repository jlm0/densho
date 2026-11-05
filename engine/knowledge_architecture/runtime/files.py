from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING

from knowledge_architecture.parser.generated import is_generated
from knowledge_architecture.parser.result import Problem

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping


@dataclass(frozen=True, slots=True)
class ApplyResult:
    written: tuple[PurePosixPath, ...]
    removed: tuple[PurePosixPath, ...]
    problems: list[Problem]


def _write_problem(path: Path, error: OSError) -> Problem:
    return Problem(path, 1, "write", f"The generator cannot change this path: {error.strerror!a}.")


def _not_generated(path: Path, detail: str) -> Problem:
    return Problem(path, 1, "not-generated", f"{detail} Move it, then run the generator again.")


def _passes_through_link(path: Path, repository: Path) -> bool:
    return path.resolve() != repository.resolve() / path.relative_to(repository)


def _blocked(path: Path, repository: Path) -> Problem | None:
    if _passes_through_link(path, repository):
        return _not_generated(path, "This path holds a symbolic link.")
    if not path.exists():
        return None
    if not path.is_file():
        return _not_generated(path, "This path is not a file.")
    if not is_generated(path.read_bytes()):
        return _not_generated(path, "The generator did not write this file.")
    return None


def _remove_empty_parents(path: Path, repository: Path) -> None:
    for parent in path.parents:
        if repository in {parent.parent, parent}:
            return
        try:
            parent.rmdir()
        except OSError:
            return


def _stale_files(
    candidates: Iterable[Path], expected: Iterable[Path], repository: Path
) -> list[Path]:
    known = set(expected)
    return sorted(
        path
        for path in candidates
        if path not in known
        and path.is_file()
        and not _passes_through_link(path, repository)
        and is_generated(path.read_bytes())
    )


def apply_files(
    repository: Path, files: Mapping[PurePosixPath, bytes], candidates: Iterable[Path]
) -> ApplyResult:
    targets = {repository / path: (path, data) for path, data in files.items()}
    try:
        blocked = [_blocked(path, repository) for path in sorted(targets)]
        problems = [problem for problem in blocked if problem is not None]
        if problems:
            return ApplyResult((), (), problems)
        removed: list[PurePosixPath] = []
        for path in _stale_files(candidates, targets, repository):
            path.unlink()
            _remove_empty_parents(path, repository)
            removed.append(PurePosixPath(path.relative_to(repository).as_posix()))
        written: list[PurePosixPath] = []
        for path, (relative, data) in sorted(targets.items()):
            if path.exists() and path.read_bytes() == data:
                continue
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            written.append(relative)
    except OSError as error:
        return ApplyResult((), (), [_write_problem(repository, error)])
    return ApplyResult(tuple(written), tuple(removed), [])
