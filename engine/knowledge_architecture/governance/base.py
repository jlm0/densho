import os
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from knowledge_architecture.parser.node import GOVERNANCE_FOLDER, NODE_FILE_NAME, parse_source
from knowledge_architecture.parser.result import ParsedNode, Problem

TREE_FOLDERS = ("knowledge", "skills", GOVERNANCE_FOLDER)
FILE_MODES = frozenset({"100644", "100755"})
OBJECT_HEADER_PARTS = 3
NOT_A_REPOSITORY = "not a git repository"
NO_REPOSITORY_NOTE = "This folder is not a git repository, so the change rules did not run."
NO_GIT_NOTE = "The git program is not available, so the change rules did not run."
NO_COMMIT_NOTE = "The repository has no commit yet, so the change rules did not run."
MERGE_NOTE = "A merge is in progress, so the change rules did not run."


@dataclass(frozen=True, slots=True)
class Base:
    readable: bool = False
    items: list[ParsedNode] = field(default_factory=list[ParsedNode])
    unreadable: frozenset[Path] = frozenset()
    notes: list[str] = field(default_factory=list[str])
    problems: list[Problem] = field(default_factory=list[Problem])


def _environment() -> dict[str, str]:
    variables = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    return {**variables, "LC_ALL": "C"}


def _git(
    program: str, repository: Path, *arguments: str, stdin: bytes | None = None
) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(  # noqa: S603
        [program, "-C", str(repository), *arguments],
        input=stdin,
        capture_output=True,
        check=False,
        env=_environment(),
    )


def _failure(repository: Path, detail: bytes) -> Base:
    message = " ".join(detail.decode("utf-8", "replace").split())
    return Base(problems=[Problem(repository, 1, "base", f"git cannot read HEAD: {message!a}")])


def _node_blobs(listing: bytes) -> list[tuple[str, str]]:
    blobs: list[tuple[str, str]] = []
    for entry in listing.split(b"\0"):
        if not entry:
            continue
        details, _, name = entry.partition(b"\t")
        mode, _, object_id = details.decode("ascii").split(" ")
        path = os.fsdecode(name)
        if mode in FILE_MODES and Path(path).name == NODE_FILE_NAME:
            blobs.append((object_id, path))
    return blobs


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


def _parse_blobs(repository: Path, blobs: list[tuple[str, bytes]]) -> Base:
    items: list[ParsedNode] = []
    unreadable: set[Path] = set()
    for path, content in blobs:
        location = repository / path
        try:
            parsed = parse_source(content.decode("utf-8"), location)
        except UnicodeDecodeError:
            unreadable.add(location)
            continue
        if isinstance(parsed, ParsedNode):
            items.append(parsed)
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
            return Base(notes=[NO_REPOSITORY_NOTE])
        return _failure(repository, inside.stderr)
    if _git(program, repository, "rev-parse", "--verify", "--quiet", "HEAD").returncode != 0:
        return Base(notes=[NO_COMMIT_NOTE])
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
    listing = _git(program, repository, "ls-tree", "-r", "-z", "HEAD", "--", *TREE_FOLDERS)
    if listing.returncode != 0:
        return _failure(repository, listing.stderr)
    blobs = _node_blobs(listing.stdout)
    request = "".join(f"{object_id}\n" for object_id, _ in blobs).encode("ascii")
    objects = _git(program, repository, "cat-file", "--batch", stdin=request)
    if objects.returncode != 0:
        return _failure(repository, objects.stderr)
    contents = _contents(objects.stdout, len(blobs))
    if contents is None:
        return _failure(repository, b"An object is missing.")
    return _parse_blobs(repository, [(path, contents[i]) for i, (_, path) in enumerate(blobs)])
