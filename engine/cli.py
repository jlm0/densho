from pathlib import Path
from typing import TYPE_CHECKING, Annotated

import typer

from engine.compiler import build_tree
from engine.compiler.output import NOTICES
from engine.directives import check_directives, resolve_directives
from engine.governance import check_governance, pending_entities
from engine.graph import check_tree
from engine.interface import (
    VIEW_FOLDER,
    accept_entities,
    command_prefix,
    write_view,
)
from engine.language import check_language
from engine.parser import parse_tree
from engine.runtime import generate_runtime
from engine.template import adopt_template, history_drift, record_history

if TYPE_CHECKING:
    from collections.abc import Sequence

    from engine.directives import AppliedDirective
    from engine.parser.result import Problem

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
    if report.pending is not None:
        listing = f"{command_prefix(repository)} governance --pending"
        typer.echo(f"{report.pending} entities wait for review. Run {listing} to list them.")
    summary = f"{report.result.value}: {len(report.files)} files, {len(report.written)} written"
    _finish(f"{summary}, {len(report.removed)} removed", report.problems)


@app.command()
def view(
    repository: Annotated[
        Path, typer.Argument(help="The folder that holds knowledge/, skills/, and governance/.")
    ] = Path(),
) -> None:
    """Run each check, then write a read-only site for people to build/view/."""
    report = write_view(repository)
    for note in report.notes:
        typer.echo(f"note: {note}")
    if report.files:
        typer.echo(f"Open {repository / VIEW_FOLDER / 'index.html'} in a browser.")
    summary = f"{len(report.files)} pages, {len(report.written)} written"
    _finish(f"{summary}, {len(report.removed)} removed", report.problems)


@app.command()
def accept(
    names: Annotated[
        list[str] | None,
        typer.Argument(
            help="The IDs to accept. An ID names one node or one directive. "
            "An exception has the name <node>:<directive>."
        ),
    ] = None,
    subtree: Annotated[
        list[str] | None,
        typer.Option(
            help="Accept this node, each node under it, and each directive and exception on them."
        ),
    ] = None,
    repository: Annotated[
        Path, typer.Option(help="The folder that holds knowledge/, skills/, and governance/.")
    ] = Path(),
    *,
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", help="List what the command would accept, and write nothing."),
    ] = False,
) -> None:
    """Set named proposals to accepted, and write no commit. A person runs this command."""
    if not names and not subtree:
        typer.echo("Name an ID, or use --subtree with a node ID.")
        raise typer.Exit(2)
    report = accept_entities(repository, names or [], subtree or [], dry_run=dry_run)
    for note in report.notes:
        typer.echo(f"note: {note}")
    verb = "would be" if dry_run else "is now"
    for entity in report.accepted:
        typer.echo(f"{entity.path}:{entity.line}: {entity.label} {verb} accepted")
    if report.accepted and not dry_run:
        command = command_prefix(repository)
        typer.echo(
            "This command wrote no commit. Read git diff, "
            f"run {command} runtime, stage the files, and commit them."
        )
    count = f"{len(report.accepted)} entities {'to accept' if dry_run else 'accepted'}"
    _finish(f"{count}, {report.not_proposed} not proposed", report.problems)


@app.command()
def adopt(
    repository: Annotated[
        Path, typer.Argument(help="The folder that holds the installed knowledge.")
    ] = Path(),
) -> None:
    """Bring in template knowledge as the last commit requires, then write the runtime files."""
    report = adopt_template(repository)
    for note in report.notes:
        typer.echo(f"note: {note}")
    for name in report.imported:
        typer.echo(f"added the import of the root to {name}")
    for entity in report.proposed:
        typer.echo(f"{entity.path}:{entity.line}: {entity.label} was {entity.status}, now proposed")
    written = len(report.runtime.written) if report.runtime else 0
    summary = f"{len(report.proposed)} entities set to proposed, {written} files written"
    _finish(summary, report.problems)


@app.command()
def history(
    repository: Annotated[
        Path, typer.Argument(help="The folder that holds the template.")
    ] = Path(),
    *,
    verify: Annotated[
        bool,
        typer.Option(
            "--verify",
            help="Also fail when the command wrote a change, or when the index lacks the file.",
        ),
    ] = False,
    drift: Annotated[
        bool,
        typer.Option(
            "--drift", help="Print how this tree differs from the history, and write nothing."
        ),
    ] = False,
) -> None:
    """Record template changes for agents, or list how this tree differs from the history."""
    if verify and drift:
        typer.echo("--drift writes nothing, so it cannot run with --verify.")
        raise typer.Exit(2)
    report = history_drift(repository) if drift else record_history(repository, verify=verify)
    for note in report.notes:
        typer.echo(f"note: {note}")
    if drift:
        for entry in report.entries:
            typer.echo(entry.model_dump_json())
    _finish(f"{len(report.entries)} entities differ from the history", report.problems)
