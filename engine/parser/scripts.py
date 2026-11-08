import hashlib
import json
from pathlib import Path, PurePath, PurePosixPath
from typing import TYPE_CHECKING

from engine.git import ignored_paths
from engine.layout import EVALS_FOLDER, KNOWLEDGE_FOLDER, SKILLS_FOLDER
from engine.parser.result import Problem, Script

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping, Sequence

SCRIPTS_FOLDER_NAME = "scripts"
SKILLS_IN_KNOWLEDGE = SKILLS_FOLDER.relative_to(KNOWLEDGE_FOLDER)
EVALS_IN_KNOWLEDGE = EVALS_FOLDER.relative_to(KNOWLEDGE_FOLDER)
EXECUTABLE_BITS = 0o111


def folder_of[PathT: PurePath](path: PathT, folders: Mapping[PathT, PathT]) -> PathT | None:
    return next((parent for parent in path.parents if parent in folders), None)


def script_folders[PathT: PurePath](
    node_files: Iterable[PathT], skills: PathT, name: str = SCRIPTS_FOLDER_NAME
) -> dict[PathT, PathT]:
    folders: dict[PathT, PathT] = {}
    for node_file in sorted(node_files, key=lambda path: (len(path.parts), path)):
        holder = node_file.parent
        if holder == skills or not holder.is_relative_to(skills):
            continue
        if folder_of(node_file, folders) is None:
            folders[holder / name] = node_file
    return folders


def scripts_digest(scripts: Sequence[Script]) -> str:
    listing = [
        [script.path.as_posix(), hashlib.sha256(script.data).hexdigest(), script.executable]
        for script in sorted(scripts)
    ]
    return hashlib.sha256(json.dumps(listing).encode("ascii")).hexdigest()


def read_scripts(
    root: Path, found: Mapping[Path, Sequence[Path]], problems: list[Problem]
) -> dict[Path, tuple[Script, ...]]:
    ignored = ignored_paths(root, [path for paths in found.values() for path in paths])
    scripts: dict[Path, tuple[Script, ...]] = {}
    for folder, paths in found.items():
        read = [
            script
            for path in paths
            if path not in ignored and (script := _read_script(path, folder, problems))
        ]
        scripts[folder] = tuple(sorted(read))
    return scripts


def _read_script(path: Path, folder: Path, problems: list[Problem]) -> Script | None:
    if not path.is_file():
        problems.append(Problem(path, 1, "read", "A script must be a regular file."))
        return None
    try:
        data = path.read_bytes()
        mode = path.stat().st_mode
    except OSError as error:
        problems.append(Problem(path, 1, "read", str(error)))
        return None
    relative = PurePosixPath(path.relative_to(folder).as_posix())
    return Script(relative, data, executable=bool(mode & EXECUTABLE_BITS))
