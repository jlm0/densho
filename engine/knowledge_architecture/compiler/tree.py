from dataclasses import dataclass
from typing import TYPE_CHECKING

from knowledge_architecture.compiler.graph import compile_items
from knowledge_architecture.compiler.output import (
    OUTPUT_FOLDER,
    remove_output,
    render_output,
    write_output,
)
from knowledge_architecture.directives import check_items as check_directive_items
from knowledge_architecture.governance import check_governance
from knowledge_architecture.graph import check_tree
from knowledge_architecture.language import check_language
from knowledge_architecture.parser.result import Problem

if TYPE_CHECKING:
    from collections.abc import Sequence
    from pathlib import Path

    from knowledge_architecture.compiler.graph import CompiledGraph
    from knowledge_architecture.compiler.output import BuildOutput
    from knowledge_architecture.parser.result import ParsedNode

BUILD_CODES = ("empty-tree", "path", "write")


@dataclass(frozen=True, slots=True)
class CompileReport:
    compiled: CompiledGraph | None
    notes: list[str]
    problems: list[Problem]


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


def compile_tree(repository: Path, *, proposals: bool = False) -> CompileReport:
    items, problems = check_tree(repository)
    if problems:
        return CompileReport(None, [], problems)
    if not items:
        message = "The tree holds no node, so the build has nothing to compile."
        return CompileReport(
            None, [], [Problem(repository / "knowledge", 1, "empty-tree", message)]
        )
    governance = check_governance(repository, items)
    _, language = check_language(repository, items)
    found = {
        *check_directive_items(items),
        *governance.problems,
        *language,
        *path_problems(items, repository),
    }
    if found:
        return CompileReport(None, governance.notes, sorted(found))
    compiled = compile_items(items, repository, proposals=proposals)
    return CompileReport(compiled, governance.notes, [])


def build_tree(repository: Path, *, proposals: bool = False) -> BuildReport:
    folder = repository / OUTPUT_FOLDER
    report = compile_tree(repository, proposals=proposals)
    if report.compiled is None:
        problems = [*report.problems, *remove_output(folder)]
        return BuildReport(None, None, report.notes, problems)
    output = render_output(report.compiled)
    problems = write_output(output, folder)
    if problems:
        return BuildReport(report.compiled, None, report.notes, problems)
    return BuildReport(report.compiled, output, report.notes, [])
