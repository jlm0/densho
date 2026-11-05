from pathlib import Path
from typing import TYPE_CHECKING, Annotated

import typer

from knowledge_architecture.graph import check_tree
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
