from dataclasses import dataclass
from typing import TYPE_CHECKING

from engine.evaluation.tasks import CONTAINS, REPLY_PATH

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence
    from pathlib import PurePosixPath

    from engine.evaluation.tasks import Check, Target, Task


@dataclass(frozen=True, slots=True)
class TargetResult:
    directive: str
    passed: bool
    failures: tuple[str, ...]


def _texts(check: Check, files: Mapping[PurePosixPath, str], reply: str) -> list[str]:
    if check.path == REPLY_PATH:
        return [reply]
    return [text for path, text in sorted(files.items()) if path.full_match(check.path)]


def check_failure(check: Check, files: Mapping[PurePosixPath, str], reply: str) -> str | None:
    texts = _texts(check, files, reply)
    if not texts:
        return f"line {check.line}: no output matches {check.path}"
    count = sum(1 for text in texts for _ in check.pattern.finditer(text))
    if check.kind == CONTAINS:
        if count < check.minimum:
            return f"line {check.line}: {count} matches in {check.path}, {check.minimum} needed"
        if check.maximum is not None and count > check.maximum:
            return f"line {check.line}: {count} matches in {check.path}, {check.maximum} allowed"
        return None
    if count:
        return f"line {check.line}: {count} matches in {check.path}, 0 allowed"
    return None


def grade_target(target: Target, files: Mapping[PurePosixPath, str], reply: str) -> TargetResult:
    failures = tuple(
        failure
        for check in target.checks
        if (failure := check_failure(check, files, reply)) is not None
    )
    return TargetResult(target.directive, not failures, failures)


def grade(task: Task, files: Mapping[PurePosixPath, str], reply: str) -> Sequence[TargetResult]:
    return tuple(grade_target(target, files, reply) for target in task.targets)
