from dataclasses import dataclass, replace
from typing import TYPE_CHECKING

from knowledge_architecture.compiler import compile_tree
from knowledge_architecture.generated.metamodel import CompiledResult
from knowledge_architecture.governance.base import tracked_files
from knowledge_architecture.parser.result import Problem
from knowledge_architecture.runtime.claude_code import (
    candidate_files,
    instruction_notes,
    render_files,
    review_candidates,
    size_problems,
)
from knowledge_architecture.runtime.files import apply_files
from knowledge_architecture.runtime.links import local_links, resolves
from knowledge_architecture.runtime.view import build_view

if TYPE_CHECKING:
    from pathlib import Path, PurePosixPath

    from knowledge_architecture.runtime.claude_code import RenderedFile

RUNTIME_CODES = ("not-generated", "link", "size", "changed", "not-staged", "write")
NO_INDEX_NOTE = "git cannot read an index in this folder, so the check of the index did not run."


@dataclass(frozen=True, slots=True)
class RuntimeReport:
    result: CompiledResult
    files: tuple[PurePosixPath, ...]
    written: tuple[PurePosixPath, ...]
    removed: tuple[PurePosixPath, ...]
    notes: list[str]
    problems: list[Problem]


def _link_problems(rendered: RenderedFile, repository: Path) -> list[Problem]:
    folder = repository / rendered.path.parent
    return [
        Problem(
            repository / rendered.node_path,
            1,
            "link",
            f"{rendered.path} links to {link!a}, and this path does not exist in the repository.",
        )
        for link in local_links(rendered.text)
        if not resolves(link, folder, repository)
    ]


def _changed_problems(repository: Path, report: RuntimeReport) -> list[Problem]:
    rewritten = "This file differed from a fresh generation. The generator rewrote it. Stage it."
    removed = "No node generates this file now. The generator removed it. Stage the removal."
    return [
        *(Problem(repository / path, 1, "changed", rewritten) for path in report.written),
        *(Problem(repository / path, 1, "changed", removed) for path in report.removed),
    ]


def _verified(repository: Path, report: RuntimeReport) -> RuntimeReport:
    if report.problems:
        return report
    changed = _changed_problems(repository, report)
    tracked = tracked_files(repository)
    if tracked is None:
        return replace(report, notes=[*report.notes, NO_INDEX_NOTE], problems=changed)
    message = "The git index does not hold this generated file. Stage it."
    not_staged = [
        Problem(repository / path, 1, "not-staged", message)
        for path in report.files
        if path.as_posix() not in tracked and path not in report.written
    ]
    return replace(report, problems=[*changed, *not_staged])


def _without_a_graph(
    repository: Path, result: CompiledResult, notes: list[str], problems: list[Problem]
) -> RuntimeReport:
    review = result == CompiledResult.proposals
    empty = all(problem.code == "empty-tree" for problem in problems)
    if not review and not empty:
        return RuntimeReport(result, (), (), (), notes, problems)
    candidates = review_candidates(repository) if review else candidate_files(repository)
    applied = apply_files(repository, {}, candidates)
    remaining = applied.problems if empty else [*problems, *applied.problems]
    return RuntimeReport(result, (), applied.written, applied.removed, notes, remaining)


def _generated(repository: Path, *, proposals: bool) -> RuntimeReport:
    result = CompiledResult.proposals if proposals else CompiledResult.in_force
    report = compile_tree(repository, proposals=proposals)
    if report.compiled is None:
        return _without_a_graph(repository, result, report.notes, report.problems)
    rendered = render_files(build_view(report.compiled))
    notes = [*report.notes, *instruction_notes(repository)]
    problems = [
        *size_problems(rendered, repository),
        *(problem for entry in rendered for problem in _link_problems(entry, repository)),
    ]
    files = tuple(entry.path for entry in rendered)
    if problems:
        return RuntimeReport(result, files, (), (), notes, sorted(problems))
    contents = {entry.path: entry.text.encode("utf-8") for entry in rendered}
    candidates = review_candidates(repository) if proposals else candidate_files(repository)
    applied = apply_files(repository, contents, candidates)
    return RuntimeReport(result, files, applied.written, applied.removed, notes, applied.problems)


def generate_runtime(
    repository: Path, *, proposals: bool = False, verify: bool = False
) -> RuntimeReport:
    report = _generated(repository, proposals=proposals)
    return _verified(repository, report) if verify else report
