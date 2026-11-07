import os
import shutil
import subprocess
from dataclasses import dataclass, field, replace
from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING

from engine.git import git_environment
from engine.layout import KNOWLEDGE_FOLDER, NODE_FILE_NAME, SKILLS_FOLDER
from engine.parser.node import parse_source, universal_newlines
from engine.parser.result import ParsedNode, Problem, Script
from engine.parser.scripts import folder_of, script_folders

if TYPE_CHECKING:
    from collections.abc import Mapping

EXECUTABLE_MODE = "100755"
FILE_MODES = frozenset({"100644", EXECUTABLE_MODE})
OBJECT_HEADER_PARTS = 3
NOT_A_REPOSITORY = "not a git repository"
NO_REPOSITORY_NOTE = "This folder is not a git repository, so the change rules did not run."
NO_GIT_NOTE = "The git program is not available, so the change rules did not run."
NO_COMMIT_NOTE = "The repository has no commit yet, so the change rules did not run."
MERGE_NOTE = "A merge is in progress, so the change rules did not run."


@dataclass(frozen=True, slots=True)
class Base:
    readable: bool = False
    empty: bool = False
    items: list[ParsedNode] = field(default_factory=list[ParsedNode])
    unreadable: frozenset[Path] = frozenset()
    notes: list[str] = field(default_factory=list[str])
    problems: list[Problem] = field(default_factory=list[Problem])


def _git(
    program: str, repository: Path, *arguments: str, stdin: bytes | None = None
) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(  # noqa: S603
        [program, "-C", str(repository), *arguments],
        input=stdin,
        capture_output=True,
        check=False,
        env=git_environment(),
    )


def _failure(repository: Path, detail: bytes) -> Base:
    message = " ".join(detail.decode("utf-8", "replace").split())
    return Base(problems=[Problem(repository, 1, "base", f"git cannot read HEAD: {message!a}")])


@dataclass(frozen=True, slots=True)
class _Blob:
    object_id: str
    path: PurePosixPath
    executable: bool


@dataclass(frozen=True, slots=True)
class _Listing:
    nodes: list[_Blob]
    scripts: dict[PurePosixPath, list[_Blob]]
    folders: dict[PurePosixPath, PurePosixPath]


def _listing(output: bytes) -> _Listing:
    blobs: list[_Blob] = []
    for entry in output.split(b"\0"):
        if not entry:
            continue
        details, _, name = entry.partition(b"\t")
        mode, _, object_id = details.decode("ascii").split(" ")
        if mode in FILE_MODES:
            path = PurePosixPath(os.fsdecode(name))
            blobs.append(_Blob(object_id, path, executable=mode == EXECUTABLE_MODE))
    node_files = [blob.path for blob in blobs if blob.path.name == NODE_FILE_NAME]
    folders = script_folders(node_files, SKILLS_FOLDER)
    listing = _Listing([], {folder: [] for folder in folders}, folders)
    for blob in blobs:
        folder = folder_of(blob.path, folders)
        if folder is not None:
            listing.scripts[folder].append(blob)
        elif blob.path.name == NODE_FILE_NAME:
            listing.nodes.append(blob)
    return listing


def _contents(output: bytes, count: int) -> list[bytes] | None:
    contents: list[bytes] = []
    start = 0
    for _ in range(count):
        end = output.index(b"\n", start)
        header = output[start:end].split(b" ")
        if len(header) != OBJECT_HEADER_PARTS:
            return None
        size = int(header[-1])
        contents.append(output[end + 1 : end + 1 + size])
        start = end + 1 + size + 1
    return contents


def _scripts_by_node(
    repository: Path, listing: _Listing, contents: Mapping[str, bytes]
) -> dict[Path, tuple[Script, ...]]:
    return {
        repository / listing.folders[folder]: tuple(
            sorted(
                Script(
                    PurePosixPath(blob.path.relative_to(folder).as_posix()),
                    contents[blob.object_id],
                    executable=blob.executable,
                )
                for blob in blobs
            )
        )
        for folder, blobs in listing.scripts.items()
    }


def _parse_blobs(repository: Path, listing: _Listing, contents: Mapping[str, bytes]) -> Base:
    items: list[ParsedNode] = []
    unreadable: set[Path] = set()
    scripts = _scripts_by_node(repository, listing, contents)
    for blob in listing.nodes:
        location = repository / blob.path
        try:
            text = contents[blob.object_id].decode("utf-8")
        except UnicodeDecodeError:
            unreadable.add(location)
            continue
        parsed = parse_source(universal_newlines(text), location)
        if isinstance(parsed, ParsedNode):
            items.append(replace(parsed, scripts=scripts.get(location, ())))
        else:
            unreadable.add(location)
    notes = [
        f"The change rules skipped {path}, because the file at HEAD does not parse."
        for path in sorted(unreadable)
    ]
    return Base(readable=True, items=items, unreadable=frozenset(unreadable), notes=notes)


def _stopped_state(program: str, repository: Path) -> Base | None:
    inside = _git(program, repository, "rev-parse", "--is-inside-work-tree")
    if inside.returncode != 0:
        if NOT_A_REPOSITORY in inside.stderr.decode("utf-8", "replace"):
            return Base(empty=True, notes=[NO_REPOSITORY_NOTE])
        return _failure(repository, inside.stderr)
    if _git(program, repository, "rev-parse", "--verify", "--quiet", "HEAD").returncode != 0:
        return Base(empty=True, notes=[NO_COMMIT_NOTE])
    if _git(program, repository, "rev-parse", "--verify", "--quiet", "MERGE_HEAD").returncode == 0:
        return Base(notes=[MERGE_NOTE])
    return None


def read_base(repository: Path) -> Base:
    program = shutil.which("git")
    if program is None:
        return Base(notes=[NO_GIT_NOTE])
    stopped = _stopped_state(program, repository)
    if stopped is not None:
        return stopped
    listing = _git(
        program, repository, "ls-tree", "-r", "-z", "HEAD", "--", KNOWLEDGE_FOLDER.as_posix()
    )
    if listing.returncode != 0:
        return _failure(repository, listing.stderr)
    found = _listing(listing.stdout)
    wanted = sorted(
        {blob.object_id for blob in found.nodes}
        | {blob.object_id for blobs in found.scripts.values() for blob in blobs}
    )
    request = "".join(f"{object_id}\n" for object_id in wanted).encode("ascii")
    objects = _git(program, repository, "cat-file", "--batch", stdin=request)
    if objects.returncode != 0:
        return _failure(repository, objects.stderr)
    contents = _contents(objects.stdout, len(wanted))
    if contents is None:
        return _failure(repository, b"An object is missing.")
    return _parse_blobs(repository, found, dict(zip(wanted, contents, strict=True)))


def tracked_files(repository: Path) -> frozenset[str] | None:
    program = shutil.which("git")
    if program is None:
        return None
    listing = _git(program, repository, "ls-files", "-z")
    if listing.returncode != 0:
        return None
    return frozenset(os.fsdecode(name) for name in listing.stdout.split(b"\0") if name)


def read_file_at(repository: Path, revision: str, path: PurePosixPath) -> bytes | None:
    program = shutil.which("git")
    if program is None:
        return None
    shown = _git(program, repository, "show", f"{revision}:./{path}")
    return shown.stdout if shown.returncode == 0 else None


def read_head_file(repository: Path, path: PurePosixPath) -> bytes | None:
    return read_file_at(repository, "HEAD", path)


def head_holds(repository: Path, path: PurePosixPath) -> bool | None:
    program = shutil.which("git")
    if program is None:
        return None
    return _git(program, repository, "cat-file", "-e", f"HEAD:./{path}").returncode == 0
