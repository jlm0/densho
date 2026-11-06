from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING

from engine.git import ignored_paths
from engine.parser.generated import is_generated
from engine.parser.result import Problem

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable, Mapping

    type Owner = Callable[[PurePosixPath], PurePosixPath]

READ_BITS = 0o444
READ_TO_EXECUTE = 2
EXECUTE_BITS = 0o111


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


def _relative(path: Path, repository: Path) -> PurePosixPath:
    return PurePosixPath(path.relative_to(repository).as_posix())


def _itself(path: PurePosixPath) -> PurePosixPath:
    return path


@dataclass(slots=True)
class _Ownership:
    repository: Path
    owner: Owner
    markers: dict[Path, bool]

    def marker_file(self, path: Path) -> Path:
        return self.repository / self.owner(_relative(path, self.repository))

    def has_marker(self, path: Path) -> bool:
        if path not in self.markers:
            self.markers[path] = (
                path.is_file()
                and not _passes_through_link(path, self.repository)
                and is_generated(path.read_bytes())
            )
        return self.markers[path]

    def owns(self, path: Path) -> bool:
        return self.has_marker(self.marker_file(path))


def _blocked(path: Path, ownership: _Ownership) -> Problem | None:
    if _passes_through_link(path, ownership.repository):
        return _not_generated(path, "This path holds a symbolic link.")
    if not path.exists():
        return None
    if not path.is_file():
        return _not_generated(path, "This path is not a file.")
    if not ownership.owns(path):
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
    candidates: Iterable[Path], expected: Iterable[Path], ownership: _Ownership
) -> list[Path]:
    known = set(expected)
    repository = ownership.repository
    stale = [
        path
        for path in candidates
        if path not in known
        and path.is_file()
        and not _passes_through_link(path, repository)
        and ownership.owns(path)
    ]
    copies = [path for path in stale if ownership.marker_file(path) != path]
    return sorted(set(stale) - ignored_paths(repository, copies))


def _with_mode(path: Path, *, executable: bool) -> bool:
    mode = path.stat().st_mode & 0o777
    wanted = mode | ((mode & READ_BITS) >> READ_TO_EXECUTE) if executable else mode & ~EXECUTE_BITS
    if bool(mode & EXECUTE_BITS) == executable:
        return False
    path.chmod(wanted)
    return True


def apply_files(
    repository: Path,
    files: Mapping[PurePosixPath, bytes],
    candidates: Iterable[Path],
    *,
    owner: Owner = _itself,
    executable: Mapping[PurePosixPath, bool] | None = None,
) -> ApplyResult:
    targets = {repository / path: (path, data) for path, data in files.items()}
    modes = executable or {}
    ownership = _Ownership(repository, owner, {})
    try:
        blocked = [_blocked(path, ownership) for path in sorted(targets)]
        problems = [problem for problem in blocked if problem is not None]
        if problems:
            return ApplyResult((), (), problems)
        removed: list[PurePosixPath] = []
        for path in _stale_files(candidates, targets, ownership):
            path.unlink()
            _remove_empty_parents(path, repository)
            removed.append(_relative(path, repository))
        written: list[PurePosixPath] = []
        for path, (relative, data) in sorted(targets.items()):
            changed = not path.exists() or path.read_bytes() != data
            if changed:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
            if relative in modes:
                changed = _with_mode(path, executable=modes[relative]) or changed
            if changed:
                written.append(relative)
    except OSError as error:
        return ApplyResult((), (), [_write_problem(repository, error)])
    return ApplyResult(tuple(written), tuple(removed), [])
