from pathlib import Path
from typing import TYPE_CHECKING, Annotated

import typer

from knowledge_architecture.compiler import build_tree
from knowledge_architecture.compiler.output import NOTICES
from knowledge_architecture.directives import check_directives, resolve_directives
from knowledge_architecture.governance import check_governance, pending_entities
from knowledge_architecture.graph import check_tree
from knowledge_architecture.language import check_language
from knowledge_architecture.parser import parse_tree
from knowledge_architecture.runtime import generate_runtime

if TYPE_CHECKING:
    from collections.abc import Sequence

    from knowledge_architecture.directives import AppliedDirective
    from knowledge_architecture.parser.result import Problem

app = typer.Typer(add_completion=False, pretty_exceptions_enable=False, rich_markup_mode=None)


def _finish(summary: str, problems: Sequence[Problem]) -> None:
    for problem in problems:
        typer.echo(problem)
    typer.echo(f"{summary}, {len(problems)} problems")
    if problems:
        raise typer.Exit(1)


def _applied_line(entry: AppliedDirective) -> str:
    directive = entry.directive
    route = " -> ".join(entry.route)
    return f"{directive.id} ({directive.scope}) from {route}: {directive.text}"


@app.command()
def parse(
    folders: Annotated[list[Path], typer.Argument(help="The folders to read.")],
) -> None:
    """Parse each node file in the folders."""
    items, problems = parse_tree(folders)
    _finish(f"{len(items)} nodes parsed", problems)


@app.command()
def graph(
    repository: Annotated[
        Path, typer.Argument(help="The folder that holds knowledge/ and skills/.")
    ] = Path(),
) -> None:
    """Parse each node file, then check the whole graph."""
    items, problems = check_tree(repository)
    _finish(f"{len(items)} nodes checked", problems)


@app.command()
def language(
    repository: Annotated[
        Path, typer.Argument(help="The folder that holds governance/language/ and the nodes.")
    ] = Path(),
) -> None:
    """Check the language of each directive, trigger, and skill description."""
    count, problems = check_language(repository)
    _finish(f"{count} texts checked", problems)


@app.command()
def directives(
    repository: Annotated[
        Path, typer.Argument(help="The folder that holds knowledge/ and skills/.")
    ] = Path(),
    at: Annotated[
        str | None, typer.Option(help="List the directives that apply at this node ID.")
    ] = None,
) -> None:
    """Check how directives reach the nodes, or list what applies at one node."""
    if at is None:
        count, problems = check_directives(repository)
        _finish(f"{count} directives checked", problems)
        return
    items, problems = check_tree(repository)
    if problems:
        _finish("0 directives listed", problems)
    if at not in {item.node.id for item in items}:
        typer.echo(f"No node has the ID {at!a}.")
        raise typer.Exit(1)
    applied = resolve_directives(items).at(at)
    projected = resolve_directives(items, proposals=True).at(at)
    in_force = {entry.directive.id for entry in applied}
    kept = {entry.directive.id for entry in projected}
    waiting = [entry for entry in projected if entry.directive.id not in in_force]
    for entry in applied:
        typer.echo(_applied_line(entry))
    for entry in waiting:
        typer.echo(f"proposed: {_applied_line(entry)}")
    for directive_id in sorted(in_force - kept):
        typer.echo(f"proposed: an exception stops {directive_id} here")
    _finish(f"{len(applied)} directives apply at {at}, {len(waiting)} proposed", [])


@app.command()
def governance(
    repository: Annotated[
        Path, typer.Argument(help="The folder that holds knowledge/, skills/, and governance/.")
    ] = Path(),
    *,
    pending: Annotated[
        bool, typer.Option("--pending", help="List each proposed entity, and do not check.")
    ] = False,
) -> None:
    """Check the lifecycle and the change rules, or list what waits for review."""
    if pending:
        entities, problems = pending_entities(repository)
        for entity in entities:
            typer.echo(f"{entity.path}:{entity.line}: {entity.label}")
        _finish(f"{len(entities)} entities wait for review", problems)
        return
    report = check_governance(repository)
    for note in report.notes:
        typer.echo(f"note: {note}")
    _finish(f"{report.count} entities checked", report.problems)


@app.command()
def build(
    repository: Annotated[
        Path, typer.Argument(help="The folder that holds knowledge/, skills/, and governance/.")
    ] = Path(),
    *,
    proposals: Annotated[
        bool,
        typer.Option(
            "--proposals",
            help="Also hold the proposed directives, in separate files marked as not in force.",
        ),
    ] = False,
) -> None:
    """Run each check, then write the JSON and RDF output with digests."""
    report = build_tree(repository, proposals=proposals)
    for note in report.notes:
        typer.echo(f"note: {note}")
    summary = "0 nodes compiled"
    if report.compiled is not None and report.output is not None:
        result = report.output.result
        typer.echo(f"{result.value}: {NOTICES[result]}")
        for name, digest in report.output.digests.items():
            typer.echo(f"{name} {digest}")
        typer.echo(f"digest {report.output.digest}")
        graph = report.compiled.graph
        summary = (
            f"{len(graph.nodes) + 1} nodes and {len(report.compiled.directives)} directives "
            f"compiled, {report.compiled.left_out['directives']} directives left out"
        )
    _finish(summary, report.problems)


@app.command()
def runtime(
    repository: Annotated[
        Path, typer.Argument(help="The folder that holds knowledge/, skills/, and governance/.")
    ] = Path(),
    *,
    proposals: Annotated[
        bool,
        typer.Option(
            "--proposals",
            help="Write a review copy that also holds the proposals, in a folder under build/.",
        ),
    ] = False,
    verify: Annotated[
        bool,
        typer.Option(
            "--verify",
            help="Also fail when a file changed, or when the git index does not hold a file.",
        ),
    ] = False,
) -> None:
    """Run each check, then write the files that an agent tool loads."""
    if proposals and verify:
        typer.echo("--verify checks the committed files, so it cannot run with --proposals.")
        raise typer.Exit(2)
    report = generate_runtime(repository, proposals=proposals, verify=verify)
    for note in report.notes:
        typer.echo(f"note: {note}")
    for path in report.written:
        typer.echo(f"wrote {path}")
    for path in report.removed:
        typer.echo(f"removed {path}")
    summary = f"{report.result.value}: {len(report.files)} files, {len(report.written)} written"
    _finish(f"{summary}, {len(report.removed)} removed", report.problems)
