from dataclasses import dataclass
from typing import TYPE_CHECKING

from engine.compiler.graph import compile_items
from engine.compiler.output import (
    OUTPUT_FOLDER,
    link_problems,
    remove_output,
    render_output,
    write_output,
)
from engine.directives import check_items as check_directive_items
from engine.governance import check_governance
from engine.graph import check_tree
from engine.language import check_language
from engine.layout import KNOWLEDGE_FOLDER
from engine.parser.result import Problem

if TYPE_CHECKING:
    from collections.abc import Sequence
    from pathlib import Path

    from engine.compiler.graph import CompiledGraph
    from engine.compiler.output import BuildOutput
    from engine.parser.result import ParsedNode

BUILD_CODES = ("empty-tree", "path", "write")


@dataclass(frozen=True, slots=True)
class CheckedTree:
    items: Sequence[ParsedNode]
    notes: list[str]
    problems: list[Problem]


@dataclass(frozen=True, slots=True)
class CompileReport:
    compiled: CompiledGraph | None
    notes: list[str]
    problems: list[Problem]
    items: Sequence[ParsedNode] = ()


@dataclass(frozen=True, slots=True)
class BuildReport:
    compiled: CompiledGraph | None
    output: BuildOutput | None
    notes: list[str]
    problems: list[Problem]


def path_problems(items: Sequence[ParsedNode], repository: Path) -> list[Problem]:
    problems: list[Problem] = []
    for item in items:
        relative = item.path.relative_to(repository).as_posix()
        try:
            relative.encode("utf-8")
        except UnicodeEncodeError:
            message = f"The file name {relative!a} is not valid UTF-8. Rename the file."
            problems.append(Problem(repository, 1, "path", message))
    return problems


def checked_tree(repository: Path) -> CheckedTree:
    items, problems = check_tree(repository)
    if problems:
        return CheckedTree(items, [], problems)
    if not items:
        message = "The tree holds no node, so the build has nothing to compile."
        return CheckedTree(
            items, [], [Problem(repository / KNOWLEDGE_FOLDER, 1, "empty-tree", message)]
        )
    governance = check_governance(repository, items)
    _, language = check_language(repository, items)
    found = {
        *check_directive_items(items),
        *governance.problems,
        *language,
        *path_problems(items, repository),
    }
    return CheckedTree(items, governance.notes, sorted(found))


def compile_tree(repository: Path, *, proposals: bool = False) -> CompileReport:
    checked = checked_tree(repository)
    if checked.problems:
        return CompileReport(None, checked.notes, checked.problems)
    compiled = compile_items(checked.items, repository, proposals=proposals)
    return CompileReport(compiled, checked.notes, [], checked.items)


def build_tree(repository: Path, *, proposals: bool = False) -> BuildReport:
    folder = repository / OUTPUT_FOLDER
    report = compile_tree(repository, proposals=proposals)
    linked = link_problems(repository, folder)
    if linked:
        return BuildReport(None, None, report.notes, [*report.problems, *linked])
    if report.compiled is None:
        problems = [*report.problems, *remove_output(folder)]
        return BuildReport(None, None, report.notes, problems)
    output = render_output(report.compiled)
    problems = write_output(output, folder)
    if problems:
        return BuildReport(report.compiled, None, report.notes, problems)
    return BuildReport(report.compiled, output, report.notes, [])
