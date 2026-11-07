import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING

from engine.evaluation.check import discipline_directives
from engine.generated.metamodel import Status
from engine.git import git_environment
from engine.governance.entities import DIRECTIVE, governed_entities
from engine.governance.status_line import set_status_lines
from engine.interface.accept import accept_entities
from engine.interface.tree import children_by_broader, subtree_ids
from engine.layout import EVALS_FOLDER, KNOWLEDGE_FOLDER
from engine.parser.node import node_folders, parse_tree
from engine.parser.result import Problem
from engine.runtime import generate_runtime

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping, Sequence

    from engine.governance.entities import Entity
    from engine.parser.result import ParsedNode

WITH = "with"
WITHOUT = "without"
CONDITIONS = (WITH, WITHOUT)
NEUTRAL_NAME = "eval"
NEUTRAL_EMAIL = "eval@example.invalid"
CONDITION_CODE = "eval-condition"
CANARY_CODE = "eval-canary"
IN_FORCE_LINE = re.compile(r"\^(?P<id>[a-z][a-z0-9]*(?:-[a-z0-9]+)*)[ \t]*$", re.MULTILINE)


@dataclass(frozen=True, slots=True)
class Condition:
    name: str
    discipline: str
    source: Path
    files: Mapping[PurePosixPath, bytes]
    directives: Mapping[str, Status]


def isolated_git_environment(git_config: Path) -> dict[str, str]:
    return {**git_environment(), "GIT_CONFIG_GLOBAL": str(git_config), "GIT_CONFIG_NOSYSTEM": "1"}


def run_git(folder: Path, git_config: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    program = shutil.which("git")
    if program is None:
        message = "The eval needs git on the PATH."
        raise FileNotFoundError(message)
    return subprocess.run(  # noqa: S603
        [program, "-C", str(folder), *arguments],
        capture_output=True,
        text=True,
        check=False,
        env=isolated_git_environment(git_config),
    )


def commit_folder(folder: Path, git_config: Path, message: str) -> list[Problem]:
    steps = (
        ("init", "-q", "--template=", "--initial-branch=main"),
        ("config", "user.name", NEUTRAL_NAME),
        ("config", "user.email", NEUTRAL_EMAIL),
        ("config", "commit.gpgsign", "false"),
        ("add", "-A"),
        ("commit", "-q", "--no-verify", "--allow-empty", "-m", message),
    )
    for step in steps:
        done = run_git(folder, git_config, *step)
        if done.returncode:
            detail = " ".join(done.stderr.split()) or f"exit {done.returncode}"
            text = f"git {step[0]} failed in the throwaway folder: {detail}"
            return [Problem(folder, 1, CONDITION_CODE, text)]
    return []


def inside(path: Path, folder: Path) -> bool:
    return path.resolve().is_relative_to(folder.resolve())


def guard_throwaway(source: Path, work: Path, repository: Path) -> None:
    if not inside(source, work) or source.resolve() == work.resolve():
        message = f"The eval changes only folders inside its work folder, not {source}."
        raise ValueError(message)
    if inside(repository, source) or inside(work, repository / KNOWLEDGE_FOLDER):
        message = f"The eval cannot change the project tree at {repository}."
        raise ValueError(message)


def _copy_knowledge(repository: Path, source: Path) -> None:
    evals = (repository / EVALS_FOLDER).resolve()

    def ignored(folder: str, names: list[str]) -> set[str]:
        return {name for name in names if (Path(folder) / name).resolve() == evals}

    shutil.copytree(
        repository / KNOWLEDGE_FOLDER, source / KNOWLEDGE_FOLDER, symlinks=True, ignore=ignored
    )


def _accepted_in(items: Sequence[ParsedNode], discipline: str) -> list[Entity]:
    branch = subtree_ids(discipline, children_by_broader(items))
    return [
        entity
        for entity in governed_entities(items).values()
        if entity.kind == DIRECTIVE and entity.holder in branch and entity.status == Status.accepted
    ]


def _set_proposed(entities: Iterable[Entity]) -> list[Problem]:
    by_file: dict[Path, list[Entity]] = {}
    for entity in entities:
        by_file.setdefault(entity.path, []).append(entity)
    problems: list[Problem] = []
    for path, group in sorted(by_file.items()):
        data, missed = set_status_lines(path.read_bytes(), group, Status.proposed)
        path.write_bytes(data)
        problems.extend(
            Problem(entity.path, entity.line, CONDITION_CODE, f"{entity.label} kept its status.")
            for entity in missed
        )
    return problems


def _prepared(source: Path, discipline: str, name: str, git_config: Path) -> list[Problem]:
    items, problems = parse_tree(node_folders(source))
    if problems:
        return problems
    if name == WITHOUT:
        problems = _set_proposed(_accepted_in(items, discipline))
        if problems:
            return problems
    problems = commit_folder(source, git_config, f"copy for the {name} condition")
    if problems or name == WITHOUT:
        return problems
    report = accept_entities(source, [], [discipline])
    return report.problems


def build_condition(
    repository: Path, work: Path, discipline: str, name: str, git_config: Path
) -> Condition | list[Problem]:
    source = work / "conditions" / name
    guard_throwaway(source, work, repository)
    _copy_knowledge(repository, source)
    problems = _prepared(source, discipline, name, git_config)
    if problems:
        return problems
    runtime = generate_runtime(source)
    if runtime.problems:
        return runtime.problems
    files = {path: (source / path).read_bytes() for path in runtime.files}
    items, problems = parse_tree(node_folders(source))
    if problems:
        return problems
    return Condition(name, discipline, source, files, discipline_directives(items, discipline))


def in_force_ids(files: Mapping[PurePosixPath, bytes]) -> set[str]:
    return {
        found["id"]
        for data in files.values()
        for found in IN_FORCE_LINE.finditer(data.decode("utf-8", errors="replace"))
    }


def canary_problems(
    with_condition: Condition,
    without_condition: Condition,
    targets: Iterable[str],
    canary_targets: Iterable[str],
) -> list[Problem]:
    problems: list[Problem] = []
    in_force = in_force_ids(with_condition.files)
    for directive in sorted(set(targets)):
        if directive not in in_force:
            message = f"The with condition does not hold {directive} in force."
            problems.append(Problem(with_condition.source, 1, CANARY_CODE, message))
    leaked = in_force_ids(without_condition.files) & set(without_condition.directives)
    for directive in sorted(leaked):
        message = f"The without condition holds {directive} in force."
        problems.append(Problem(without_condition.source, 1, CANARY_CODE, message))
    texts = [data.decode("utf-8", errors="replace") for data in without_condition.files.values()]
    for directive in sorted(set(canary_targets)):
        if any(re.search(rf"(?<![\w-]){re.escape(directive)}(?![\w-])", text) for text in texts):
            message = f"A without file names the canary target {directive}. Choose another target."
            problems.append(Problem(without_condition.source, 1, CANARY_CODE, message))
    return problems
