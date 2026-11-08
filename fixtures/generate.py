import os
import posixpath
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING, Annotated

import typer

from engine.git import git_environment, ignored_paths
from engine.interface import accept_entities
from engine.parser.result import Problem
from engine.runtime import generate_runtime, local_links
from engine.template import adopt_template

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping, Sequence

REPO = Path(__file__).resolve().parents[1]
FIXTURE = PurePosixPath("fixtures/project")
SKIPPED_SOURCE = PurePosixPath("fixtures")
ANSWERS = PurePosixPath(".copier-answers.yml")
OUTPUTS = (
    PurePosixPath("AGENTS.md"),
    ANSWERS,
    PurePosixPath(".claude/references"),
    PurePosixPath(".claude/rules/knowledge"),
    PurePosixPath(".claude/skills"),
)
RENAMED = {
    "AGENTS.md": "AGENTS.fixture.md",
    ".claude": "claude",
    ".copier-answers.yml": "copier-answers.yml",
}
ROOT_NODE = "root"
TEMPLATE_MARKER = "copier.yml"
WORKING_TREE = "working-tree"
PINNED_ANSWERS = {
    "_commit": WORKING_TREE,
    "_src_path": "https://github.com/jlm0/densho.git",
    "started_from": WORKING_TREE,
}
IDENTITY = {
    "GIT_AUTHOR_NAME": "Densho fixture",
    "GIT_AUTHOR_EMAIL": "fixture@densho.invalid",
    "GIT_AUTHOR_DATE": "2026-01-01T00:00:00Z",
    "GIT_COMMITTER_NAME": "Densho fixture",
    "GIT_COMMITTER_EMAIL": "fixture@densho.invalid",
    "GIT_COMMITTER_DATE": "2026-01-01T00:00:00Z",
}
EXECUTABLE_BITS = 0o111
EXECUTABLE_MODE = 0o755
PLAIN_MODE = 0o644
GIT = shutil.which("git") or "git"
FIXTURE_CODES = ("refused", "install", "pending", "changed", "not-staged", "write")


@dataclass(frozen=True, slots=True, order=True)
class Output:
    data: bytes
    executable: bool


type Snapshot = dict[PurePosixPath, Output]


@dataclass(frozen=True, slots=True)
class Generation:
    snapshot: Snapshot
    problems: list[Problem]


@dataclass(frozen=True, slots=True)
class FixtureReport:
    files: int
    written: tuple[PurePosixPath, ...]
    removed: tuple[PurePosixPath, ...]
    problems: list[Problem]


def isolated_environment() -> dict[str, str]:
    return {
        **git_environment(),
        **IDENTITY,
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_CONFIG_NOSYSTEM": "1",
    }


def _run(folder: Path, *arguments: str, isolated: bool = True) -> bytes | Problem:
    environment = isolated_environment() if isolated else git_environment()
    try:
        done = subprocess.run(  # noqa: S603
            arguments,
            cwd=folder,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            check=False,
            env=environment,
        )
    except OSError as error:
        return Problem(folder, 1, "install", f"{arguments[0]} cannot start: {error.strerror!a}.")
    if done.returncode:
        detail = " ".join(done.stderr.decode("utf-8", "replace").split())
        return Problem(folder, 1, "install", f"{' '.join(arguments)!a} failed: {detail!a}")
    return done.stdout


def _commit(folder: Path, message: str) -> Problem | None:
    steps = (
        (GIT, "init", "-q", "--template=", "--initial-branch=main"),
        (GIT, "add", "-A"),
        (GIT, "-c", "core.hooksPath=/dev/null", "commit", "-q", "-m", message),
    )
    for step in steps:
        done = _run(folder, *step)
        if isinstance(done, Problem):
            return done
    return None


def _listed(repository: Path, *arguments: str) -> list[PurePosixPath] | Problem:
    done = _run(repository, GIT, "ls-files", "-z", *arguments, isolated=False)
    if isinstance(done, Problem):
        return done
    return [PurePosixPath(os.fsdecode(name)) for name in done.split(b"\0") if name]


def template_source(repository: Path, folder: Path) -> Problem | None:
    names = _listed(repository, "--cached", "--others", "--exclude-standard")
    if isinstance(names, Problem):
        return names
    try:
        for name in names:
            if SKIPPED_SOURCE not in name.parents and (repository / name).is_file():
                target = folder / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(repository / name, target)
    except OSError as error:
        message = f"The script cannot copy the working tree: {error.strerror!a}."
        return Problem(repository, 1, "install", message)
    return _commit(folder, "the working tree")


def template_refusal(scratch: Path, template: Path) -> Problem | None:
    if scratch.resolve().is_relative_to(template.resolve()):
        message = "The scratch project must sit outside the template repository."
    elif (scratch / TEMPLATE_MARKER).exists():
        message = f"The scratch project holds {TEMPLATE_MARKER}, so it is a template."
    else:
        return None
    return Problem(scratch, 1, "refused", message)


def refusal(scratch: Path, template: Path) -> Problem | None:
    problem = template_refusal(scratch, template)
    if problem:
        return problem
    if not scratch.is_dir() or any(scratch.iterdir()):
        return Problem(scratch, 1, "refused", "The scratch project must be an empty folder.")
    return None


def pin_answers(data: bytes) -> bytes | str:
    text = data.decode("utf-8")
    for key, value in PINNED_ANSWERS.items():
        line = re.compile(rf"^{key}: .*$", re.MULTILINE)
        text, count = line.subn(f"{key}: {value}", text)
        if count != 1:
            return f"The answers file holds {count} lines for {key}. It must hold 1."
    return text.encode("utf-8")


def _files_under(folder: Path) -> list[Path]:
    return sorted(path for path in folder.rglob("*") if path.is_file() or path.is_symlink())


def _output(path: Path) -> Output:
    return Output(path.read_bytes(), bool(path.stat().st_mode & EXECUTABLE_BITS))


def read_snapshot(folder: Path) -> Snapshot:
    snapshot: Snapshot = {}
    for output in OUTPUTS:
        start = folder / output
        for path in _files_under(start) if start.is_dir() else [start]:
            if path.is_file() and not path.is_symlink():
                snapshot[PurePosixPath(path.relative_to(folder).as_posix())] = _output(path)
    return snapshot


def pin_snapshot(scratch: Path, snapshot: Snapshot) -> Generation:
    answers = snapshot.get(ANSWERS)
    if answers is None:
        return Generation(
            {}, [Problem(scratch / ANSWERS, 1, "install", "Copier wrote no answers.")]
        )
    pinned = pin_answers(answers.data)
    if isinstance(pinned, str):
        return Generation({}, [Problem(scratch / ANSWERS, 1, "install", pinned)])
    return Generation({**snapshot, ANSWERS: Output(pinned, answers.executable)}, [])


def fixture_path(path: PurePosixPath) -> PurePosixPath:
    first, *rest = path.parts
    return PurePosixPath(RENAMED.get(first, first), *rest)


def _moved_link(link: str, source: PurePosixPath) -> str:
    target, separator, anchor = link.partition("#")
    resolved = PurePosixPath(posixpath.normpath((source.parent / target).as_posix()))
    start = fixture_path(source).parent.as_posix()
    return posixpath.relpath(fixture_path(resolved).as_posix(), start) + separator + anchor


def moved_data(path: PurePosixPath, data: bytes) -> bytes:
    if path.suffix != ".md":
        return data
    text = data.decode("utf-8")
    for link in sorted(set(local_links(text))):
        moved = _moved_link(link, path)
        if moved != link:
            text = text.replace(f"]({link})", f"]({moved})")
    return text.encode("utf-8")


def fixture_snapshot(snapshot: Snapshot) -> Snapshot:
    return {
        fixture_path(name): Output(moved_data(name, output.data), output.executable)
        for name, output in snapshot.items()
    }


def accept_everything(scratch: Path, template: Path) -> list[Problem]:
    refused = template_refusal(scratch, template)
    if refused:
        return [refused]
    accepted = accept_entities(scratch, [], [ROOT_NODE])
    if accepted.problems:
        return accepted.problems
    runtime = generate_runtime(scratch, proposals=False, verify=False)
    if runtime.problems:
        return runtime.problems
    if runtime.pending:
        message = f"{runtime.pending} entities stay proposed after the accept."
        return [Problem(scratch, 1, "pending", message)]
    return []


def _copy(template: Path, scratch: Path) -> Problem | None:
    with tempfile.TemporaryDirectory() as temporary:
        source = Path(temporary) / "template"
        problem = template_source(template, source)
        if problem:
            return problem
        copier = (sys.executable, "-m", "copier", "copy", "--defaults", "--skip-tasks")
        done = _run(scratch, *copier, "--vcs-ref=HEAD", "--quiet", str(source), str(scratch))
        return done if isinstance(done, Problem) else None


def build_project(scratch: Path, template: Path) -> Generation:
    problem = refusal(scratch, template) or _copy(template, scratch)
    if problem:
        return Generation({}, [problem])
    adopted = adopt_template(scratch)
    if adopted.problems:
        return Generation({}, adopted.problems)
    problem = _commit(scratch, "feat: add Densho")
    if problem:
        return Generation({}, [problem])
    problems = accept_everything(scratch, template)
    if problems:
        return Generation({}, problems)
    pinned = pin_snapshot(scratch, read_snapshot(scratch))
    if pinned.problems:
        return pinned
    return Generation(fixture_snapshot(pinned.snapshot), [])


def generate(template: Path) -> Generation:
    with tempfile.TemporaryDirectory() as temporary:
        scratch = Path(temporary) / "project"
        scratch.mkdir()
        return build_project(scratch, template)


def differences(snapshot: Mapping[PurePosixPath, Output], folder: Path) -> list[PurePosixPath]:
    present = {
        PurePosixPath(path.relative_to(folder).as_posix()): path for path in _files_under(folder)
    }
    changed = [
        name
        for name, output in snapshot.items()
        if name not in present or present[name].is_symlink() or _output(present[name]) != output
    ]
    extra = [path for name, path in present.items() if name not in snapshot]
    ignored = ignored_paths(folder, extra)
    stale = [
        PurePosixPath(path.relative_to(folder).as_posix()) for path in extra if path not in ignored
    ]
    return sorted([*changed, *stale])


def apply_snapshot(
    snapshot: Mapping[PurePosixPath, Output], folder: Path, names: Sequence[PurePosixPath]
) -> tuple[tuple[PurePosixPath, ...], tuple[PurePosixPath, ...]]:
    written: list[PurePosixPath] = []
    removed: list[PurePosixPath] = []
    for name in names:
        path = folder / name
        if path.is_symlink() or path.is_file():
            path.unlink()
        output = snapshot.get(name)
        if output is None:
            removed.append(name)
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(output.data)
        path.chmod(EXECUTABLE_MODE if output.executable else PLAIN_MODE)
        written.append(name)
    for directory in sorted(folder.rglob("*"), reverse=True):
        if directory.is_dir() and not directory.is_symlink() and not any(directory.iterdir()):
            directory.rmdir()
    return tuple(written), tuple(removed)


def unstaged(repository: Path, names: Iterable[PurePosixPath]) -> list[Problem]:
    staged = _listed(repository, "--", FIXTURE.as_posix())
    if isinstance(staged, Problem):
        return [staged]
    return [
        Problem(
            repository / FIXTURE / name, 1, "not-staged", "The git index does not hold this file."
        )
        for name in names
        if FIXTURE / name not in staged
    ]


def write_fixture(repository: Path, *, verify: bool) -> FixtureReport:
    generation = generate(repository)
    if generation.problems:
        return FixtureReport(0, (), (), generation.problems)
    folder = repository / FIXTURE
    try:
        folder.mkdir(parents=True, exist_ok=True)
        names = differences(generation.snapshot, folder)
        written, removed = apply_snapshot(generation.snapshot, folder, names)
    except OSError as error:
        message = f"The script cannot change the fixture: {error.strerror!a}."
        return FixtureReport(
            len(generation.snapshot), (), (), [Problem(folder, 1, "write", message)]
        )
    problems: list[Problem] = []
    if verify:
        changed = "The fixture differed from a fresh generation. Stage the result."
        problems.extend(Problem(folder / name, 1, "changed", changed) for name in names)
        problems.extend(unstaged(repository, generation.snapshot))
    return FixtureReport(len(generation.snapshot), written, removed, sorted(problems))


app = typer.Typer(add_completion=False, pretty_exceptions_enable=False, rich_markup_mode=None)


@app.command()
def main(
    *,
    verify: Annotated[
        bool,
        typer.Option(
            "--verify",
            help="Also fail when a file changed, or when the git index does not hold a file.",
        ),
    ] = False,
) -> None:
    """Install the working tree into a scratch project, accept each entity, and copy the output."""
    report = write_fixture(REPO, verify=verify)
    for name in report.written:
        typer.echo(f"wrote {FIXTURE / name}")
    for name in report.removed:
        typer.echo(f"removed {FIXTURE / name}")
    for problem in report.problems:
        typer.echo(problem)
    summary = f"fixture: {report.files} files, {len(report.written)} written"
    typer.echo(f"{summary}, {len(report.removed)} removed, {len(report.problems)} problems")
    if report.problems:
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
