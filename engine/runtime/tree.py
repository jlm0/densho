from dataclasses import dataclass, replace
from typing import TYPE_CHECKING

from engine.compiler import compile_tree
from engine.generated.metamodel import CompiledResult
from engine.governance.base import tracked_files
from engine.governance.entities import pending_count
from engine.parser.result import Problem
from engine.runtime.claude_code import (
    candidate_files,
    copied_files,
    instruction_notes,
    marker_owner,
    render_files,
    review_candidates,
    size_problems,
)
from engine.runtime.files import apply_files
from engine.runtime.links import link_target, local_links
from engine.runtime.view import build_view

if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence
    from pathlib import Path, PurePosixPath

    from engine.runtime.claude_code import RenderedFile

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
    pending: int | None = None


def _link_problems(
    rendered: RenderedFile, targets: frozenset[Path], repository: Path
) -> list[Problem]:
    folder = repository / rendered.path.parent
    return [
        Problem(
            repository / rendered.node_path,
            1,
            "link",
            f"{rendered.path} links to {link!a}, and the generator writes no file at this path.",
        )
        for link in local_links(rendered.text)
        if link_target(link, folder) not in targets
    ]


def rendered_problems(
    rendered: Sequence[RenderedFile],
    repository: Path,
    copies: Iterable[PurePosixPath] = (),
) -> list[Problem]:
    paths = [*(entry.path for entry in rendered), *copies]
    targets = frozenset((repository / path).resolve() for path in paths)
    return [
        *size_problems(rendered, repository),
        *(problem for entry in rendered for problem in _link_problems(entry, targets, repository)),
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
    applied = apply_files(repository, {}, candidates, owner=marker_owner)
    remaining = applied.problems if empty else [*problems, *applied.problems]
    return RuntimeReport(result, (), applied.written, applied.removed, notes, remaining)


def _generated(repository: Path, *, proposals: bool) -> RuntimeReport:
    result = CompiledResult.proposals if proposals else CompiledResult.in_force
    report = compile_tree(repository, proposals=proposals)
    if report.compiled is None:
        return _without_a_graph(repository, result, report.notes, report.problems)
    view = build_view(report.compiled)
    rendered = render_files(view)
    copies = copied_files(view)
    notes = [*report.notes, *instruction_notes(repository)]
    pending = pending_count(report.items)
    problems = rendered_problems(rendered, repository, copies)
    files = (*(entry.path for entry in rendered), *copies)
    if problems:
        return RuntimeReport(result, files, (), (), notes, sorted(problems), pending)
    contents = {
        **{entry.path: entry.text.encode("utf-8") for entry in rendered},
        **{path: script.data for path, script in copies.items()},
    }
    candidates = review_candidates(repository) if proposals else candidate_files(repository)
    applied = apply_files(
        repository,
        contents,
        candidates,
        owner=marker_owner,
        executable={path: script.executable for path, script in copies.items()},
    )
    return RuntimeReport(
        result, files, applied.written, applied.removed, notes, applied.problems, pending
    )


def generate_runtime(
    repository: Path, *, proposals: bool = False, verify: bool = False
) -> RuntimeReport:
    report = _generated(repository, proposals=proposals)
    return _verified(repository, report) if verify else report
