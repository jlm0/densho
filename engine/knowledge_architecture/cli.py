from pathlib import Path
from typing import TYPE_CHECKING, Annotated

import typer

from knowledge_architecture.directives import check_directives, resolve_directives
from knowledge_architecture.graph import check_tree
from knowledge_architecture.language import check_language
from knowledge_architecture.parser import parse_tree

if TYPE_CHECKING:
    from collections.abc import Sequence

    from knowledge_architecture.parser.result import Problem

app = typer.Typer(add_completion=False, pretty_exceptions_enable=False, rich_markup_mode=None)


def _finish(summary: str, problems: Sequence[Problem]) -> None:
    for problem in problems:
        typer.echo(problem)
    typer.echo(f"{summary}, {len(problems)} problems")
    if problems:
        raise typer.Exit(1)


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
    for entry in applied:
        directive = entry.directive
        route = " -> ".join(entry.route)
        typer.echo(f"{directive.id} ({directive.scope}) from {route}: {directive.text}")
    _finish(f"{len(applied)} directives apply at {at}", [])
