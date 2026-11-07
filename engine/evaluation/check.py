from typing import TYPE_CHECKING

from engine.evaluation.grader import grade
from engine.evaluation.tasks import (
    BAD_FOLDER,
    FIXTURE_FOLDER,
    GOOD_FOLDER,
    REPLY_FILE,
    TASK_CODE,
    discipline_folders,
    load_tasks,
    loaded_name_problems,
    read_files,
)
from engine.generated.metamodel import Discipline, Status
from engine.interface.tree import children_by_broader, subtree_ids
from engine.parser.node import node_folders, parse_tree
from engine.parser.result import Problem

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence
    from pathlib import Path, PurePosixPath

    from engine.evaluation.tasks import Task
    from engine.parser.result import ParsedNode

LIVE_STATUSES = frozenset({Status.proposed, Status.accepted})


def discipline_directives(items: Sequence[ParsedNode], discipline: str) -> dict[str, Status]:
    branch = subtree_ids(discipline, children_by_broader(items))
    return {
        directive.id: Status(directive.status)
        for item in items
        if item.node.id in branch
        for directive in item.node.directives or []
    }


def _sample(
    task: Task, fixture: Mapping[PurePosixPath, str], name: str, problems: list[Problem]
) -> tuple[dict[PurePosixPath, str], str] | None:
    folder = task.folder / name
    files, found = read_files(folder)
    problems.extend(found)
    problems.extend(loaded_name_problems(folder, files))
    if not files:
        message = f"Add a file to {name}/. Git does not keep an empty folder."
        problems.append(Problem(folder, 1, TASK_CODE, message))
        return None
    reply = files.pop(REPLY_FILE, "")
    return {**fixture, **files}, reply


def _sample_problems(task: Task) -> list[Problem]:
    problems: list[Problem] = []
    fixture, found = read_files(task.folder / FIXTURE_FOLDER)
    problems.extend(found)
    problems.extend(loaded_name_problems(task.folder / FIXTURE_FOLDER, fixture))
    if REPLY_FILE in fixture:
        message = f"Rename {REPLY_FILE}. A sample uses this name for the reply."
        problems.append(Problem(task.folder / FIXTURE_FOLDER / REPLY_FILE, 1, TASK_CODE, message))
    for name, expected in ((GOOD_FOLDER, True), (BAD_FOLDER, False)):
        sample = _sample(task, fixture, name, problems)
        if sample is None:
            continue
        lines = {target.directive: target.line for target in task.targets}
        for result in grade(task, *sample):
            if result.passed == expected:
                continue
            verb = "fails" if expected else "passes"
            detail = f" {'; '.join(result.failures)}." if result.failures else ""
            message = f"The {name} output {verb} the target {result.directive}.{detail}"
            problems.append(Problem(task.file, lines[result.directive], TASK_CODE, message))
    return problems


def _target_problems(task: Task, directives: Mapping[str, Status]) -> list[Problem]:
    problems: list[Problem] = []
    for target in task.targets:
        status = directives.get(target.directive)
        if status is None:
            message = f"No node in the subtree of {task.discipline} holds {target.directive}."
        elif status not in LIVE_STATUSES:
            message = f"{target.directive} is {status.value}. Remove the target."
        else:
            continue
        problems.append(Problem(task.file, target.line, TASK_CODE, message))
    return problems


def _discipline_problems(
    folder: Path, items: Sequence[ParsedNode], tasks: Sequence[Task]
) -> list[Problem]:
    known = {item.node.id for item in items if isinstance(item.node, Discipline)}
    if folder.name not in known:
        message = f"{folder.name} is not the ID of a densho:Discipline node."
        return [Problem(folder, 1, TASK_CODE, message)]
    canaries = [task for task in tasks if task.discipline == folder.name and task.canary]
    if len(canaries) != 1:
        message = f"A discipline needs 1 canary task, and {folder.name} has {len(canaries)}."
        return [Problem(folder, 1, TASK_CODE, message)]
    return []


def check_tasks(repository: Path) -> tuple[int, list[Problem]]:
    items, problems = parse_tree(node_folders(repository))
    if problems:
        return 0, problems
    tasks, problems = load_tasks(repository)
    for folder in discipline_folders(repository):
        problems.extend(_discipline_problems(folder, items, tasks))
    by_discipline: dict[str, dict[str, Status]] = {}
    for task in tasks:
        if task.discipline not in by_discipline:
            by_discipline[task.discipline] = discipline_directives(items, task.discipline)
        problems.extend(_target_problems(task, by_discipline[task.discipline]))
        problems.extend(_sample_problems(task))
    return len(tasks), sorted(set(problems))
