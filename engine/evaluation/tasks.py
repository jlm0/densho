import re
from dataclasses import dataclass, replace
from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING, cast

from engine.disciplines import ID_FORM
from engine.layout import EVALS_FOLDER
from engine.parser.front_matter import DELIMITER, read_front_matter
from engine.parser.result import FieldPath, Problem, line_of

if TYPE_CHECKING:
    from collections.abc import Iterator, Mapping

TASK_FILE = "task.yaml"
FIXTURE_FOLDER = "fixture"
GOOD_FOLDER = "good"
BAD_FOLDER = "bad"
SAMPLE_FOLDERS = (GOOD_FOLDER, BAD_FOLDER)
TASK_ENTRIES = frozenset({TASK_FILE, FIXTURE_FOLDER, *SAMPLE_FOLDERS})
REPLY_FILE = PurePosixPath("reply.md")
REPLY_PATH = "@reply"
TASK_CODE = "eval-task"
TASK_FIELDS = frozenset({"title", "prompt", "tools", "canary", "targets"})
TARGET_FIELDS = frozenset({"directive", "checks"})
CHECK_FIELDS = frozenset({"path", "contains", "lacks", "min", "max"})
TASK_TOOLS = ("Read", "Write", "Edit", "Glob", "Grep", "Bash")
LOADED_NAMES = frozenset(
    name.casefold() for name in ("CLAUDE.md", "CLAUDE.local.md", "AGENTS.md", ".claude", ".git")
) | {".mcp.json"}
MAX_PROMPT_CHARACTERS = 4_000
MAX_TASK_BYTES = 64 * 1024
MAX_FILE_BYTES = 256 * 1024
MAX_FILES = 200
CONTAINS = "contains"
LACKS = "lacks"


@dataclass(frozen=True, slots=True)
class Check:
    path: str
    kind: str
    pattern: re.Pattern[str]
    minimum: int
    maximum: int | None
    line: int


@dataclass(frozen=True, slots=True)
class Target:
    directive: str
    checks: tuple[Check, ...]
    line: int


@dataclass(frozen=True, slots=True)
class Task:
    discipline: str
    id: str
    folder: Path
    title: str
    prompt: str
    tools: tuple[str, ...]
    canary: bool
    targets: tuple[Target, ...]

    @property
    def file(self) -> Path:
        return self.folder / TASK_FILE

    @property
    def name(self) -> str:
        return f"{self.discipline}/{self.id}"


@dataclass(slots=True)
class _Reader:
    path: Path
    locations: Mapping[FieldPath, int]
    problems: list[Problem]

    def report(self, field_path: FieldPath, message: str) -> None:
        line = line_of(self.locations, field_path)
        self.problems.append(Problem(self.path, line, TASK_CODE, message))

    def text(self, data: Mapping[str, object], key: str, *, one_line: bool) -> str:
        value = data.get(key)
        if not isinstance(value, str) or not value.strip():
            self.report((key,), f"{key} must be a text that is not empty.")
            return ""
        if one_line and "\n" in value.strip():
            self.report((key,), f"{key} must be one line.")
        return value.strip()


def evals_folder(repository: Path) -> Path:
    return repository / EVALS_FOLDER


def discipline_folders(repository: Path) -> list[Path]:
    folder = evals_folder(repository)
    if not folder.is_dir() or folder.is_symlink():
        return []
    return sorted(path for path in folder.iterdir() if path.is_dir() and not path.is_symlink())


def _read_yaml(path: Path) -> tuple[dict[str, object], dict[FieldPath, int]] | list[Problem]:
    try:
        data = path.read_bytes()
    except OSError as error:
        return [Problem(path, 1, TASK_CODE, f"The file cannot be read: {error.strerror!a}.")]
    if len(data) > MAX_TASK_BYTES:
        return [Problem(path, 1, TASK_CODE, f"The file must hold at most {MAX_TASK_BYTES} bytes.")]
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return [Problem(path, 1, "encoding", "The file is not valid UTF-8.")]
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    if DELIMITER in lines:
        line = lines.index(DELIMITER) + 1
        return [Problem(path, line, TASK_CODE, "Remove the --- line.")]
    wrapped = read_front_matter("\n".join([DELIMITER, *lines, DELIMITER, ""]), path)
    if isinstance(wrapped, list):
        return [replace(problem, line=max(problem.line - 1, 1)) for problem in wrapped]
    return wrapped.data, {key: line - 1 for key, line in wrapped.locations.items()}


def _unknown_fields(
    reader: _Reader, data: Mapping[str, object], known: frozenset[str], root: FieldPath
) -> None:
    for key in sorted(set(data) - known):
        reader.report((*root, key), f"Remove the field {key!a}. Its fields are {sorted(known)}.")


def _count(reader: _Reader, value: object, field_path: FieldPath) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        reader.report(field_path, f"{field_path[-1]} must be a whole number of 0 or more.")
        return None
    return value


def _check_path(reader: _Reader, value: object, field_path: FieldPath) -> str | None:
    if value == REPLY_PATH:
        return REPLY_PATH
    if not isinstance(value, str) or not value or "\\" in value:
        reader.report(field_path, f"path must be {REPLY_PATH} or a glob with / only.")
        return None
    parts = value.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        reader.report(field_path, "path must be relative, with no empty part and no . or .. part.")
        return None
    return value


def _pattern(reader: _Reader, value: object, field_path: FieldPath) -> re.Pattern[str] | None:
    if not isinstance(value, str) or not value:
        reader.report(field_path, f"{field_path[-1]} must be a regular expression.")
        return None
    try:
        return re.compile(value, re.MULTILINE)
    except (re.error, OverflowError, RecursionError) as error:
        reader.report(field_path, f"The regular expression is not valid: {error}.")
        return None


def _limits(
    reader: _Reader, data: Mapping[str, object], kind: str, root: FieldPath
) -> tuple[int, int | None] | None:
    if kind == LACKS:
        for key in ("min", "max"):
            if key in data:
                reader.report((*root, key), f"A {LACKS} check cannot have {key}.")
        return 0, None
    minimum = _count(reader, data.get("min", 1), (*root, "min"))
    maximum = None if "max" not in data else _count(reader, data["max"], (*root, "max"))
    if minimum is None or ("max" in data and maximum is None):
        return None
    if minimum < 1:
        reader.report((*root, "min"), "min must be 1 or more.")
        return None
    if maximum is not None and maximum < minimum:
        reader.report((*root, "max"), "max must be min or more.")
        return None
    return minimum, maximum


def _check(reader: _Reader, value: object, root: FieldPath) -> Check | None:
    if not isinstance(value, dict):
        reader.report(root, "Each check must be a mapping.")
        return None
    data = cast("dict[str, object]", value)
    _unknown_fields(reader, data, CHECK_FIELDS, root)
    kinds = [kind for kind in (CONTAINS, LACKS) if kind in data]
    if len(kinds) != 1:
        reader.report(root, f"A check must have one of {CONTAINS} and {LACKS}.")
        return None
    kind = kinds[0]
    path = _check_path(reader, data.get("path"), (*root, "path"))
    pattern = _pattern(reader, data[kind], (*root, kind))
    limits = _limits(reader, data, kind, root)
    if path is None or pattern is None or limits is None:
        return None
    return Check(path, kind, pattern, *limits, line_of(reader.locations, root))


def _target(reader: _Reader, value: object, root: FieldPath) -> Target | None:
    if not isinstance(value, dict):
        reader.report(root, "Each target must be a mapping.")
        return None
    data = cast("dict[str, object]", value)
    _unknown_fields(reader, data, TARGET_FIELDS, root)
    directive = data.get("directive")
    if not isinstance(directive, str) or not ID_FORM.fullmatch(directive):
        reader.report((*root, "directive"), "directive must be the ID of a directive.")
        directive = None
    raw = data.get("checks")
    if not isinstance(raw, list) or not raw:
        reader.report((*root, "checks"), "checks must be a list of 1 or more checks.")
        return None
    entries = cast("list[object]", raw)
    found = [_check(reader, entry, (*root, "checks", index)) for index, entry in enumerate(entries)]
    checks = tuple(check for check in found if check is not None)
    if len(checks) != len(found) or directive is None:
        return None
    if not any(check.kind == CONTAINS for check in checks):
        reader.report((*root, "checks"), f"A target needs a {CONTAINS} check.")
        return None
    return Target(directive, checks, line_of(reader.locations, root))


def _targets(reader: _Reader, value: object) -> tuple[Target, ...]:
    if not isinstance(value, list) or not value:
        reader.report(("targets",), "targets must be a list of 1 or more targets.")
        return ()
    entries = cast("list[object]", value)
    targets: list[Target] = []
    seen: set[str] = set()
    for index, entry in enumerate(entries):
        target = _target(reader, entry, ("targets", index))
        if target is None:
            continue
        if target.directive in seen:
            reader.report(("targets", index), f"Name {target.directive} in one target only.")
        seen.add(target.directive)
        targets.append(target)
    return tuple(targets)


def _tools(reader: _Reader, value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        reader.report(("tools",), f"tools must be a list of tools from {list(TASK_TOOLS)}.")
        return ()
    tools: list[str] = []
    for index, tool in enumerate(cast("list[object]", value)):
        if tool not in TASK_TOOLS or tool in tools:
            reader.report(("tools", index), f"Name each tool once, from {list(TASK_TOOLS)}.")
        else:
            tools.append(cast("str", tool))
    return tuple(tools)


def _parsed_task(folder: Path, data: dict[str, object], reader: _Reader) -> Task | None:
    _unknown_fields(reader, data, TASK_FIELDS, ())
    title = reader.text(data, "title", one_line=True)
    prompt = reader.text(data, "prompt", one_line=False)
    if len(prompt) > MAX_PROMPT_CHARACTERS:
        reader.report(("prompt",), f"prompt must hold at most {MAX_PROMPT_CHARACTERS} characters.")
    canary = data.get("canary", False)
    if not isinstance(canary, bool):
        reader.report(("canary",), "canary must be true or false.")
        canary = False
    tools = _tools(reader, data.get("tools"))
    targets = _targets(reader, data.get("targets"))
    if reader.problems:
        return None
    return Task(folder.parent.name, folder.name, folder, title, prompt, tools, canary, targets)


def _entry_problems(folder: Path) -> list[Problem]:
    problems: list[Problem] = []
    names = {path.name for path in folder.iterdir()}
    for name in sorted(names - TASK_ENTRIES):
        message = f"Remove {name!a}. A task folder holds only {sorted(TASK_ENTRIES)}."
        problems.append(Problem(folder / name, 1, TASK_CODE, message))
    for name in SAMPLE_FOLDERS:
        if name not in names:
            message = f"Add the folder {name}/ with a known {name} output."
            problems.append(Problem(folder, 1, TASK_CODE, message))
    for name in (FIXTURE_FOLDER, *SAMPLE_FOLDERS):
        path = folder / name
        if name in names and (path.is_symlink() or not path.is_dir()):
            problems.append(Problem(path, 1, TASK_CODE, f"{name} must be a folder."))
    return problems


def load_task(folder: Path) -> Task | list[Problem]:
    problems = _entry_problems(folder)
    if not ID_FORM.fullmatch(folder.name) or not ID_FORM.fullmatch(folder.parent.name):
        message = "The folder names must be IDs: knowledge/evals/<discipline-id>/<task-id>/."
        problems.append(Problem(folder, 1, TASK_CODE, message))
    path = folder / TASK_FILE
    if path.is_symlink() or not path.is_file():
        problems.append(Problem(path, 1, TASK_CODE, f"Add {TASK_FILE} as a regular file."))
        return problems
    loaded = _read_yaml(path)
    if isinstance(loaded, list):
        return [*problems, *loaded]
    data, locations = loaded
    reader = _Reader(path, locations, problems)
    task = _parsed_task(folder, data, reader)
    return task if task is not None and not problems else problems


def load_tasks(repository: Path, discipline: str | None = None) -> tuple[list[Task], list[Problem]]:
    tasks: list[Task] = []
    problems: list[Problem] = []
    for discipline_folder in discipline_folders(repository):
        if discipline is not None and discipline_folder.name != discipline:
            continue
        for folder in sorted(discipline_folder.iterdir()):
            if folder.is_symlink() or not folder.is_dir():
                message = "A discipline folder holds only task folders."
                problems.append(Problem(folder, 1, TASK_CODE, message))
                continue
            loaded = load_task(folder)
            if isinstance(loaded, Task):
                tasks.append(loaded)
            else:
                problems.extend(loaded)
    return tasks, sorted(problems)


def _walk_files(
    folder: Path, skipped: frozenset[str], problems: list[Problem]
) -> Iterator[tuple[PurePosixPath, Path]]:
    def report_error(error: OSError) -> None:
        problems.append(Problem(folder, 1, "read", str(error)))

    for parent, folders, names in folder.walk(on_error=report_error):
        top = parent == folder
        folders[:] = [name for name in sorted(folders) if not (top and name in skipped)]
        for name in sorted(names):
            if top and name in skipped:
                continue
            path = parent / name
            yield PurePosixPath(path.relative_to(folder).as_posix()), path


def read_files(
    folder: Path, *, skipped: frozenset[str] = frozenset()
) -> tuple[dict[PurePosixPath, str], list[Problem]]:
    files: dict[PurePosixPath, str] = {}
    problems: list[Problem] = []
    if not folder.is_dir() or folder.is_symlink():
        return files, problems
    for relative, path in _walk_files(folder, skipped, problems):
        if path.is_symlink() or not path.is_file():
            problems.append(Problem(path, 1, "symlink", "A task file must be a regular file."))
            continue
        if len(files) >= MAX_FILES:
            problems.append(Problem(folder, 1, TASK_CODE, f"Keep at most {MAX_FILES} files."))
            break
        try:
            with path.open("rb") as handle:
                data = handle.read(MAX_FILE_BYTES)
        except OSError as error:
            problems.append(Problem(path, 1, "read", str(error)))
            continue
        files[relative] = data.decode("utf-8", errors="replace")
    return files, problems


def loaded_name_problems(folder: Path, files: Mapping[PurePosixPath, str]) -> list[Problem]:
    return [
        Problem(
            folder / path,
            1,
            TASK_CODE,
            "Remove this file. A run loads it as an instruction or a setting.",
        )
        for path in sorted(files)
        if any(part.casefold() in LOADED_NAMES for part in path.parts)
    ]
