from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Annotated, cast

import typer

from engine.compiler import build_tree
from engine.compiler.output import NOTICES
from engine.directives import check_directives, resolve_directives
from engine.evaluation import EvalOptions, check_tasks, report_markdown, run_eval
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
from engine.template import adopt_template, history_drift, record_history, select_disciplines

if TYPE_CHECKING:
    from collections.abc import Sequence

    from engine.directives import AppliedDirective
    from engine.parser.result import Problem
    from engine.template import SelectionReport

REPOSITORY_HELP = "The folder that holds knowledge/."

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
    repository: Annotated[Path, typer.Argument(help=REPOSITORY_HELP)] = Path(),
) -> None:
    """Parse each node file, then check the whole graph."""
    items, problems = check_tree(repository)
    _finish(f"{len(items)} nodes checked", problems)


@app.command()
def language(
    repository: Annotated[Path, typer.Argument(help=REPOSITORY_HELP)] = Path(),
) -> None:
    """Check the language of each directive, trigger, and skill description."""
    count, problems = check_language(repository)
    _finish(f"{count} texts checked", problems)


@app.command()
def directives(
    repository: Annotated[Path, typer.Argument(help=REPOSITORY_HELP)] = Path(),
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
    repository: Annotated[Path, typer.Argument(help=REPOSITORY_HELP)] = Path(),
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
    repository: Annotated[Path, typer.Argument(help=REPOSITORY_HELP)] = Path(),
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
    repository: Annotated[Path, typer.Argument(help=REPOSITORY_HELP)] = Path(),
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
    repository: Annotated[Path, typer.Argument(help=REPOSITORY_HELP)] = Path(),
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
    repository: Annotated[Path, typer.Option(help=REPOSITORY_HELP)] = Path(),
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


def _echo_selection(selection: SelectionReport | None) -> None:
    if selection is None:
        return
    for note in selection.notes:
        typer.echo(f"note: {note}")
    for path in selection.removed:
        typer.echo(f"removed {path}")
    for entry in selection.pruned:
        typer.echo(f"removed the entry {entry}")


@app.command()
def select(
    repository: Annotated[Path, typer.Argument(help=REPOSITORY_HELP)] = Path(),
) -> None:
    """Remove the template disciplines that the install answer leaves out, and their edges."""
    report = select_disciplines(repository)
    _echo_selection(report)
    kept = "each discipline" if report.disciplines is None else ", ".join(report.disciplines)
    summary = f"kept {kept or 'no discipline'}, {len(report.removed)} paths removed"
    _finish(f"{summary}, {len(report.pruned)} entries removed", report.problems)


@app.command()
def adopt(
    repository: Annotated[Path, typer.Argument(help=REPOSITORY_HELP)] = Path(),
    *,
    keep_accepted: Annotated[
        bool,
        typer.Option(
            "--keep-accepted",
            help="At an install, keep each status that the template history holds as accepted.",
        ),
    ] = False,
) -> None:
    """Bring in template knowledge as the last commit requires, then write the runtime files."""
    report = adopt_template(repository, keep_accepted=keep_accepted)
    _echo_selection(report.selection)
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
    repository: Annotated[Path, typer.Argument(help=REPOSITORY_HELP)] = Path(),
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
            "--drift",
            help=(
                "Print how this tree differs from the history, and write nothing. "
                "Give a count for each discipline that the install answer leaves out."
            ),
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


@app.command(name="eval")
def evaluate(  # noqa: PLR0913
    repository: Annotated[Path, typer.Argument(help=REPOSITORY_HELP)] = Path(),
    *,
    check: Annotated[
        bool,
        typer.Option(
            "--check",
            help="Check each eval task, and grade its good and bad outputs. Make no model call.",
        ),
    ] = False,
    discipline: Annotated[
        str | None, typer.Option(help="Run the eval tasks of this discipline ID.")
    ] = None,
    task: Annotated[
        list[str] | None,
        typer.Option(help="Run only this task, with the canary. Repeat it for more tasks."),
    ] = None,
    runs: Annotated[int, typer.Option(help="The runs of each task in each condition.")] = 1,
    model: Annotated[str, typer.Option(help="The model of each run.")] = "sonnet",
    budget: Annotated[
        float, typer.Option(help="The most USD that the batch spends. No run starts past it.")
    ] = 5.0,
    run_budget: Annotated[
        float, typer.Option(help="The value of --max-budget-usd for each run, in USD.")
    ] = 0.5,
    timeout: Annotated[float, typer.Option(help="The seconds before a run stops.")] = 900.0,
    work: Annotated[
        Path | None,
        typer.Option(help="A new folder for the throwaway copies and the report."),
    ] = None,
    claude: Annotated[str, typer.Option(help="The claude program.")] = "claude",
    dry_run: Annotated[
        bool,
        typer.Option(
            "--dry-run",
            help="Build the conditions and probe each run folder. Make no model call.",
        ),
    ] = False,
) -> None:
    """Run eval tasks with and without the directives of a discipline. A person runs this."""
    if check == (discipline is not None):
        typer.echo("Use --check, or name a discipline with --discipline.")
        raise typer.Exit(2)
    if check:
        count, problems = check_tasks(repository)
        _finish(f"{count} eval tasks checked", problems)
        return
    options = EvalOptions(
        cast("str", discipline),
        tuple(task or ()),
        runs=runs,
        model=model,
        budget=budget,
        run_budget=run_budget,
        timeout=timeout,
        work=work,
        claude=claude,
        dry_run=dry_run,
    )
    report = run_eval(repository, options)
    if report.work is not None:
        typer.echo(report_markdown(report, datetime.now(UTC).date().isoformat()))
        typer.echo(f"The report is in {report.work}.")
    _finish(f"{len(report.runs)} runs, {report.cost:.4f} USD", report.problems)
