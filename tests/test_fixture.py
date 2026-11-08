import os
import shutil
import subprocess
import tempfile
from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING

import pytest
from typer.testing import CliRunner

from engine.interface.accept import AcceptReport
from engine.parser.result import Problem
from engine.runtime import link_target, local_links
from engine.template import AdoptReport
from fixtures import generate as fixture
from fixtures.generate import (
    ANSWERS,
    FIXTURE,
    FIXTURE_CODES,
    PINNED_ANSWERS,
    FixtureReport,
    Generation,
    Output,
    Snapshot,
    accept_everything,
    apply_snapshot,
    build_project,
    differences,
    fixture_path,
    fixture_snapshot,
    isolated_environment,
    moved_data,
    pin_answers,
    pin_snapshot,
    read_snapshot,
    refusal,
    template_refusal,
    template_source,
    unstaged,
    write_fixture,
)

if TYPE_CHECKING:
    from collections.abc import Callable

REPO = Path(__file__).resolve().parents[1]
GIT = shutil.which("git") or "git"
RUNNER = CliRunner()
TOOL_NAMES = frozenset({"agents.md", "claude.md", ".claude", ".copier-answers.yml"})
PERMISSIONS = 0o777
EXECUTABLE_MODE = 0o755
PLAIN_MODE = 0o644
ANSWER_TEXT = (
    "# Copier writes this file. Do not edit it.\n"
    "_commit: 0a1b2c3\n"
    "_src_path: /tmp/source\n"
    "disciplines:\n"
    "- ui-ux-design\n"
    "keep_template_status: false\n"
    "started_from: 0a1b2c3d4e5f\n"
)
SNAPSHOT: Snapshot = {
    PurePosixPath("AGENTS.md"): Output(b"# Root\n", executable=False),
    PurePosixPath(".claude/skills/a/SKILL.md"): Output(b"# Skill\n", executable=False),
    PurePosixPath(".claude/skills/a/scripts/run.sh"): Output(b"#!/bin/sh\n", executable=True),
}


def git(folder: Path, *arguments: str) -> str:
    return subprocess.run(  # noqa: S603
        [GIT, "-C", str(folder), *arguments],
        capture_output=True,
        check=True,
        text=True,
        env=isolated_environment(),
    ).stdout


def write(folder: Path, snapshot: Snapshot) -> None:
    for name, output in snapshot.items():
        path = folder / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(output.data)
        path.chmod(EXECUTABLE_MODE if output.executable else PLAIN_MODE)


def repository(tmp_path: Path) -> Path:
    folder = tmp_path / "repo"
    folder.mkdir()
    git(folder, "init", "-q", "--template=", "--initial-branch=main")
    return folder


def fake_template(tmp_path: Path) -> Path:
    template = tmp_path / "template"
    (template / "knowledge").mkdir(parents=True)
    (template / "copier.yml").write_text("_exclude: []\n", encoding="utf-8")
    (template / "knowledge/node.md").write_text("status: proposed\n", encoding="utf-8")
    return template


@pytest.mark.parametrize("check", [refusal, template_refusal])
def test_the_refusal_names_this_repository(check: Callable[[Path, Path], Problem | None]) -> None:
    problem = check(REPO, REPO)
    assert problem is not None
    assert problem.code == "refused"
    assert "outside the template" in problem.message


@pytest.mark.parametrize("check", [refusal, template_refusal])
def test_the_refusal_names_an_empty_folder_inside_the_template(
    tmp_path: Path, check: Callable[[Path, Path], Problem | None]
) -> None:
    inside = tmp_path / "template" / "inside"
    inside.mkdir(parents=True)
    problem = check(inside, tmp_path / "template")
    assert problem is not None
    assert "outside the template" in problem.message


def test_the_refusal_names_another_copy_of_the_template(tmp_path: Path) -> None:
    clone = fake_template(tmp_path / "clone")
    problem = template_refusal(clone, tmp_path / "template")
    assert problem is not None
    assert "is a template" in problem.message


@pytest.mark.parametrize("content", [None, "notes.md"])
def test_the_refusal_names_a_missing_or_full_folder(tmp_path: Path, content: str | None) -> None:
    scratch = tmp_path / "scratch"
    if content:
        scratch.mkdir()
        (scratch / content).write_text("planted\n", encoding="utf-8")
    problem = refusal(scratch, tmp_path / "template")
    assert problem is not None
    assert "empty folder" in problem.message


def test_the_refusal_passes_an_empty_folder_outside_the_template(tmp_path: Path) -> None:
    scratch = tmp_path / "scratch"
    scratch.mkdir()
    assert refusal(scratch, tmp_path / "template") is None


def test_the_build_refuses_the_template_and_changes_nothing(tmp_path: Path) -> None:
    template = fake_template(tmp_path)
    before = sorted(template.rglob("*"))
    generation = build_project(template, template)
    assert [problem.code for problem in generation.problems] == ["refused"]
    assert generation.snapshot == {}
    assert sorted(template.rglob("*")) == before
    assert (template / "knowledge/node.md").read_text(encoding="utf-8") == "status: proposed\n"


def test_the_build_refuses_a_folder_inside_the_template_and_writes_nothing(
    tmp_path: Path,
) -> None:
    template = fake_template(tmp_path)
    inside = template / "scratch"
    inside.mkdir()
    generation = build_project(inside, template)
    assert [problem.code for problem in generation.problems] == ["refused"]
    assert list(inside.iterdir()) == []


def test_a_temporary_folder_inside_the_template_stops_the_script(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    template = fake_template(tmp_path)
    (template / "tmp").mkdir()
    monkeypatch.setattr(tempfile, "tempdir", str(template / "tmp"))
    generation = fixture.generate(template)
    assert [problem.code for problem in generation.problems] == ["refused"]
    assert list((template / "tmp").iterdir()) == []


def test_the_environment_drops_the_git_variables_of_a_hook(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GIT_INDEX_FILE", "/elsewhere/index")
    environment = isolated_environment()
    assert "GIT_INDEX_FILE" not in environment
    assert environment["GIT_CONFIG_GLOBAL"] == os.devnull
    assert environment["GIT_CONFIG_NOSYSTEM"] == "1"
    assert environment["GIT_AUTHOR_EMAIL"].endswith(".invalid")
    assert environment["GIT_COMMITTER_EMAIL"].endswith(".invalid")


def test_the_pin_replaces_each_value_of_the_install() -> None:
    pinned = pin_answers(ANSWER_TEXT.encode("utf-8"))
    assert isinstance(pinned, bytes)
    lines = pinned.decode("utf-8").splitlines()
    for key, value in PINNED_ANSWERS.items():
        assert f"{key}: {value}" in lines
    assert "- ui-ux-design" in lines
    assert "keep_template_status: false" in lines
    assert "0a1b2c3" not in pinned.decode("utf-8")


def test_the_pin_skips_a_nested_key() -> None:
    text = ANSWER_TEXT + "notes:\n  _commit: nested\n"
    pinned = pin_answers(text.encode("utf-8"))
    assert isinstance(pinned, bytes)
    assert pinned.decode("utf-8").endswith("notes:\n  _commit: nested\n")


@pytest.mark.parametrize(
    ("text", "count"),
    [
        (ANSWER_TEXT.replace("_commit: 0a1b2c3\n", ""), 0),
        (ANSWER_TEXT + "_commit: 0a1b2c3\n", 2),
        (ANSWER_TEXT.replace("_src_path: /tmp/source\n", ""), 0),
        (ANSWER_TEXT.replace("started_from:", "started:"), 0),
        (ANSWER_TEXT.replace("_src_path:", "_src.path:"), 0),
    ],
)
def test_the_pin_rejects_a_missing_or_repeated_key(text: str, count: int) -> None:
    message = pin_answers(text.encode("utf-8"))
    assert isinstance(message, str)
    assert f"holds {count} lines" in message


def test_the_snapshot_reads_only_the_outputs(tmp_path: Path) -> None:
    write(tmp_path, SNAPSHOT)
    (tmp_path / ANSWERS).write_text(ANSWER_TEXT, encoding="utf-8")
    (tmp_path / "knowledge").mkdir()
    (tmp_path / "knowledge/node.md").write_text("# Root\n", encoding="utf-8")
    (tmp_path / ".claude/settings.json").write_text("{}\n", encoding="utf-8")
    (tmp_path / ".claude/skills/a/link.md").symlink_to(tmp_path / "AGENTS.md")
    snapshot = read_snapshot(tmp_path)
    assert snapshot == {**SNAPSHOT, ANSWERS: Output(ANSWER_TEXT.encode("utf-8"), executable=False)}


def test_a_fresh_fixture_has_no_difference(tmp_path: Path) -> None:
    write(tmp_path, SNAPSHOT)
    assert differences(SNAPSHOT, tmp_path) == []


def test_a_stale_fixture_lists_each_difference(tmp_path: Path) -> None:
    write(tmp_path, SNAPSHOT)
    (tmp_path / "AGENTS.md").write_bytes(b"# Old root\n")
    (tmp_path / ".claude/skills/a/SKILL.md").unlink()
    (tmp_path / ".claude/skills/a/scripts/run.sh").chmod(0o644)
    (tmp_path / ".claude/skills/old").mkdir()
    (tmp_path / ".claude/skills/old/SKILL.md").write_bytes(b"# Old\n")
    assert differences(SNAPSHOT, tmp_path) == sorted(
        [*SNAPSHOT, PurePosixPath(".claude/skills/old/SKILL.md")]
    )


def test_a_link_at_a_fixture_path_is_a_difference(tmp_path: Path) -> None:
    write(tmp_path, SNAPSHOT)
    (tmp_path / "AGENTS.md").unlink()
    (tmp_path / "copy.md").write_bytes(b"# Root\n")
    (tmp_path / "AGENTS.md").symlink_to(tmp_path / "copy.md")
    assert differences(SNAPSHOT, tmp_path) == sorted(
        [PurePosixPath("AGENTS.md"), PurePosixPath("copy.md")]
    )


def test_a_file_that_git_ignores_is_not_a_difference(tmp_path: Path) -> None:
    folder = repository(tmp_path)
    (folder / ".gitignore").write_text(".DS_Store\n", encoding="utf-8")
    fixture_folder = folder / "fixture"
    write(fixture_folder, SNAPSHOT)
    (fixture_folder / ".DS_Store").write_bytes(b"\0")
    assert differences(SNAPSHOT, fixture_folder) == []


def test_the_apply_repairs_a_stale_fixture(tmp_path: Path) -> None:
    write(tmp_path, SNAPSHOT)
    (tmp_path / "AGENTS.md").unlink()
    (tmp_path / "copy.md").write_bytes(b"# Root\n")
    (tmp_path / "AGENTS.md").symlink_to(tmp_path / "copy.md")
    (tmp_path / ".claude/skills/a/SKILL.md").unlink()
    (tmp_path / ".claude/skills/a/scripts/run.sh").chmod(0o644)
    (tmp_path / ".claude/skills/old/deep").mkdir(parents=True)
    (tmp_path / ".claude/skills/old/deep/SKILL.md").write_bytes(b"# Old\n")
    names = differences(SNAPSHOT, tmp_path)
    written, removed = apply_snapshot(SNAPSHOT, tmp_path, names)
    assert sorted(written) == sorted(SNAPSHOT)
    assert sorted(removed) == [
        PurePosixPath(".claude/skills/old/deep/SKILL.md"),
        PurePosixPath("copy.md"),
    ]
    assert read_snapshot(tmp_path) == SNAPSHOT
    assert not (tmp_path / "AGENTS.md").is_symlink()
    assert (
        tmp_path / ".claude/skills/a/scripts/run.sh"
    ).stat().st_mode & PERMISSIONS == EXECUTABLE_MODE
    assert (tmp_path / "AGENTS.md").stat().st_mode & PERMISSIONS == PLAIN_MODE
    assert not (tmp_path / ".claude/skills/old").exists()
    assert differences(SNAPSHOT, tmp_path) == []


def test_the_index_check_names_each_file_that_git_does_not_hold(tmp_path: Path) -> None:
    folder = repository(tmp_path)
    write(folder / FIXTURE, SNAPSHOT)
    git(folder, "add", (FIXTURE / "AGENTS.md").as_posix())
    problems = unstaged(folder, SNAPSHOT)
    assert [problem.code for problem in problems] == ["not-staged", "not-staged"]
    assert {problem.path for problem in problems} == {
        folder / FIXTURE / name for name in SNAPSHOT if name != PurePosixPath("AGENTS.md")
    }


def test_the_index_check_reports_a_folder_with_no_repository(tmp_path: Path) -> None:
    problems = unstaged(tmp_path, SNAPSHOT)
    assert [problem.code for problem in problems] == ["install"]


def generating(
    snapshot: Snapshot, problems: list[Problem] | None = None
) -> Callable[[Path], Generation]:
    def generate(_template: Path) -> Generation:
        return Generation(snapshot, problems or [])

    return generate


def test_the_verify_fails_on_a_stale_fixture_and_repairs_it(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    folder = repository(tmp_path)
    write(folder / FIXTURE, SNAPSHOT)
    git(folder, "add", "-A")
    (folder / FIXTURE / "AGENTS.md").write_bytes(b"# Stale\n")
    monkeypatch.setattr(fixture, "generate", generating(SNAPSHOT))
    report = write_fixture(folder, verify=True)
    assert [(problem.path, problem.code) for problem in report.problems] == [
        (folder / FIXTURE / "AGENTS.md", "changed")
    ]
    assert report.written == (PurePosixPath("AGENTS.md"),)
    again = write_fixture(folder, verify=True)
    assert again.problems == []
    assert again.files == len(SNAPSHOT)


def test_the_verify_fails_on_a_new_file_that_git_does_not_hold(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    folder = repository(tmp_path)
    write(folder / FIXTURE, SNAPSHOT)
    monkeypatch.setattr(fixture, "generate", generating(SNAPSHOT))
    report = write_fixture(folder, verify=True)
    assert {problem.code for problem in report.problems} == {"not-staged"}
    assert len(report.problems) == len(SNAPSHOT)
    assert write_fixture(folder, verify=False).problems == []


def test_a_failed_generation_changes_no_fixture_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    folder = repository(tmp_path)
    write(folder / FIXTURE, SNAPSHOT)
    failure = Problem(tmp_path, 1, "install", "Copier failed.")
    monkeypatch.setattr(fixture, "generate", generating({}, [failure]))
    report = write_fixture(folder, verify=True)
    assert report.problems == [failure]
    assert read_snapshot(folder / FIXTURE) == SNAPSHOT


def test_a_blocked_fixture_folder_gives_a_write_problem(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    folder = repository(tmp_path)
    (folder / "fixtures").mkdir()
    (folder / FIXTURE).write_text("not a folder\n", encoding="utf-8")
    monkeypatch.setattr(fixture, "generate", generating(SNAPSHOT))
    report = write_fixture(folder, verify=False)
    assert [problem.code for problem in report.problems] == ["write"]


def test_the_template_source_holds_the_working_tree_without_the_fixtures(tmp_path: Path) -> None:
    folder = repository(tmp_path)
    (folder / ".gitignore").write_text("ignored.md\n", encoding="utf-8")
    (folder / ".git/info").mkdir(parents=True, exist_ok=True)
    (folder / ".git/info/exclude").write_text("local-notes.md\n", encoding="utf-8")
    planted = ("fixtures/project/AGENTS.md", "untracked.md", "ignored.md", "local-notes.md")
    for name in ("knowledge/node.md", *planted):
        (folder / name).parent.mkdir(parents=True, exist_ok=True)
        (folder / name).write_text("text\n", encoding="utf-8")
    git(folder, "add", ".gitignore", "knowledge/node.md", "fixtures/project/AGENTS.md")
    source = tmp_path / "source"
    assert template_source(folder, source) is None
    listed = git(source, "ls-files").split()
    assert listed == [".gitignore", "knowledge/node.md", "untracked.md"]
    assert not (source / "ignored.md").exists()
    assert not (source / "local-notes.md").exists()
    assert git(source, "log", "--format=%an <%ae>").strip() == (
        "Densho fixture <fixture@densho.invalid>"
    )


class FakeInstall:
    def __init__(self, adopt_problems: list[Problem]) -> None:
        self.adopt_problems = adopt_problems
        self.steps: list[str] = []

    def copy(self, _template: Path, _scratch: Path) -> Problem | None:
        self.steps.append("copy")
        return None

    def adopt(self, _scratch: Path) -> AdoptReport:
        self.steps.append("adopt")
        return AdoptReport((), (), None, [], self.adopt_problems)

    def commit(self, _scratch: Path, message: str) -> Problem | None:
        self.steps.append(f"commit: {message}")
        return None

    def accept(self, _scratch: Path, _template: Path) -> list[Problem]:
        self.steps.append("accept")
        return []

    def snapshot(self, _scratch: Path) -> Snapshot:
        self.steps.append("snapshot")
        return {ANSWERS: Output(ANSWER_TEXT.encode("utf-8"), executable=False)}


def fake_install(monkeypatch: pytest.MonkeyPatch, adopt_problems: list[Problem]) -> FakeInstall:
    install = FakeInstall(adopt_problems)
    monkeypatch.setattr(fixture, "_copy", install.copy)
    monkeypatch.setattr(fixture, "adopt_template", install.adopt)
    monkeypatch.setattr(fixture, "_commit", install.commit)
    monkeypatch.setattr(fixture, "accept_everything", install.accept)
    monkeypatch.setattr(fixture, "read_snapshot", install.snapshot)
    return install


def test_the_build_runs_each_install_step_in_order(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    install = fake_install(monkeypatch, [])
    scratch = tmp_path / "scratch"
    scratch.mkdir()
    generation = build_project(scratch, tmp_path / "template")
    assert generation.problems == []
    assert install.steps == ["copy", "adopt", "commit: feat: add Densho", "accept", "snapshot"]
    answers = generation.snapshot[PurePosixPath("copier-answers.yml")]
    assert answers.data == pin_answers(ANSWER_TEXT.encode("utf-8"))
    assert ANSWERS not in generation.snapshot


def test_a_failed_adopt_stops_the_build(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    failure = Problem(tmp_path, 1, "select", "A link blocks the selection.")
    install = fake_install(monkeypatch, [failure])
    scratch = tmp_path / "scratch"
    scratch.mkdir()
    assert build_project(scratch, tmp_path / "template").problems == [failure]
    assert install.steps == ["copy", "adopt"]


def test_the_answers_must_exist_and_hold_each_key(tmp_path: Path) -> None:
    missing = pin_snapshot(tmp_path, dict(SNAPSHOT))
    assert [problem.code for problem in missing.problems] == ["install"]
    broken = {**SNAPSHOT, ANSWERS: Output(b"disciplines: []\n", executable=False)}
    assert [problem.code for problem in pin_snapshot(tmp_path, broken).problems] == ["install"]
    good = {**SNAPSHOT, ANSWERS: Output(ANSWER_TEXT.encode("utf-8"), executable=False)}
    pinned = pin_snapshot(tmp_path, good)
    assert pinned.problems == []
    assert pinned.snapshot[ANSWERS].data == pin_answers(ANSWER_TEXT.encode("utf-8"))


class FakeRuntime:
    def __init__(self, problems: list[Problem], pending: int | None) -> None:
        self.problems = problems
        self.pending = pending


class FakeEngine:
    def __init__(self, accept_problems: list[Problem], runtime: FakeRuntime) -> None:
        self.accept_problems = accept_problems
        self.runtime = runtime
        self.calls: list[list[str]] = []

    def accept(self, _scratch: Path, names: list[str], subtrees: list[str]) -> AcceptReport:
        self.calls.append([*names, *subtrees])
        return AcceptReport((), 0, [], self.accept_problems)

    def generate_runtime(self, _scratch: Path, *, proposals: bool, verify: bool) -> FakeRuntime:
        assert not proposals
        assert not verify
        self.calls.append(["runtime"])
        return self.runtime


def fake_engine(
    monkeypatch: pytest.MonkeyPatch, accept_problems: list[Problem], runtime: FakeRuntime
) -> FakeEngine:
    engine = FakeEngine(accept_problems, runtime)
    monkeypatch.setattr(fixture, "accept_entities", engine.accept)
    monkeypatch.setattr(fixture, "generate_runtime", engine.generate_runtime)
    return engine


@pytest.mark.parametrize(("pending", "codes"), [(3, ["pending"]), (None, []), (0, [])])
def test_the_accept_must_leave_no_proposal(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, pending: int | None, codes: list[str]
) -> None:
    engine = fake_engine(monkeypatch, [], FakeRuntime([], pending))
    problems = accept_everything(tmp_path / "scratch", tmp_path / "template")
    assert [problem.code for problem in problems] == codes
    assert engine.calls == [["root"], ["runtime"]]


def test_a_failed_accept_stops_before_the_runtime(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    failure = Problem(tmp_path, 1, "no-history", "No commit.")
    engine = fake_engine(monkeypatch, [failure], FakeRuntime([], None))
    assert accept_everything(tmp_path / "scratch", tmp_path / "template") == [failure]
    assert engine.calls == [["root"]]


def test_a_failed_runtime_stops_the_build(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    failure = Problem(tmp_path, 1, "link", "A link fails.")
    fake_engine(monkeypatch, [], FakeRuntime([failure], 3))
    assert accept_everything(tmp_path / "scratch", tmp_path / "template") == [failure]


def test_the_accept_refuses_the_template_and_another_copy(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    engine = fake_engine(monkeypatch, [], FakeRuntime([], None))
    template = fake_template(tmp_path)
    clone = fake_template(tmp_path / "clone")
    for scratch in (template, template / "knowledge", clone):
        problems = accept_everything(scratch, template)
        assert [problem.code for problem in problems] == ["refused"]
    assert engine.calls == []


def test_the_command_prints_each_problem_and_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    problem = Problem(Path("fixtures/project/AGENTS.md"), 1, "changed", "It differed.")
    report = FixtureReport(3, (PurePosixPath("AGENTS.md"),), (PurePosixPath("old.md"),), [problem])

    def write_report(_repository: Path, *, verify: bool) -> FixtureReport:
        assert verify
        return report

    monkeypatch.setattr(fixture, "write_fixture", write_report)
    result = RUNNER.invoke(fixture.app, ["--verify"])
    assert result.exit_code == 1
    assert result.output.splitlines() == [
        "wrote fixtures/project/AGENTS.md",
        "removed fixtures/project/old.md",
        "fixtures/project/AGENTS.md:1: changed: It differed.",
        "fixture: 3 files, 1 written, 1 removed, 1 problems",
    ]


@pytest.mark.parametrize("code", FIXTURE_CODES)
def test_the_template_page_names_each_fixture_code(code: str) -> None:
    text = (REPO / "docs/template-packaging.md").read_text(encoding="utf-8")
    assert f"| `{code}`" in text


def tool_names(folder: Path) -> list[Path]:
    return sorted(path for path in folder.rglob("*") if path.name.casefold() in TOOL_NAMES)


@pytest.mark.parametrize(
    "name",
    [
        "AGENTS.md",
        "agents.MD",
        "CLAUDE.md",
        "Claude.md",
        ".claude",
        ".Claude",
        ".copier-answers.yml",
        ".Copier-Answers.YML",
    ],
)
@pytest.mark.parametrize("kind", ["file", "folder"])
def test_the_name_check_finds_each_name_that_a_tool_reads(
    tmp_path: Path, name: str, kind: str
) -> None:
    (tmp_path / "project/claude/skills").mkdir(parents=True)
    path = tmp_path / "project/claude/skills" / name
    if kind == "file":
        path.write_text("planted\n", encoding="utf-8")
    else:
        path.mkdir()
    assert tool_names(tmp_path) == [path]


def test_the_name_check_passes_the_fixture_names(tmp_path: Path) -> None:
    for name in ("AGENTS.fixture.md", "copier-answers.yml", "claude/skills/a/SKILL.md"):
        (tmp_path / name).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / name).write_text("text\n", encoding="utf-8")
    assert tool_names(tmp_path) == []


def test_the_fixture_holds_no_name_that_a_tool_reads() -> None:
    assert (REPO / FIXTURE).is_dir()
    assert tool_names(REPO / "fixtures") == []


def test_each_link_in_the_fixture_goes_to_a_fixture_file() -> None:
    folder = (REPO / FIXTURE).resolve()
    files = {path.resolve() for path in folder.rglob("*") if path.is_file()}
    count = 0
    for path in folder.rglob("*.md"):
        for link in local_links(path.read_text(encoding="utf-8")):
            count += 1
            assert link_target(link, path.parent) in files, f"{path}: {link}"
    assert count > len(files)


@pytest.mark.parametrize(
    ("name", "moved"),
    [
        ("AGENTS.md", "AGENTS.fixture.md"),
        (".copier-answers.yml", "copier-answers.yml"),
        (".claude/skills/a/SKILL.md", "claude/skills/a/SKILL.md"),
        (".claude", "claude"),
        ("README.md", "README.md"),
        ("docs/.claude/a.md", "docs/.claude/a.md"),
    ],
)
def test_the_fixture_path_renames_only_the_first_part(name: str, moved: str) -> None:
    assert fixture_path(PurePosixPath(name)) == PurePosixPath(moved)


ROOT_TEXT = (
    "# Root\n\nFrom [Densho](AGENTS.md):\n\n"
    "- Read [Approval](.claude/references/approval.md#directives).\n"
    "- [Governance](.claude/rules/knowledge/governance.md) loads by itself.\n"
    "- Keep `.claude/references/` and the text ](AGENTS.md as they are.\n"
)


def test_the_moved_root_links_to_the_moved_files() -> None:
    moved = moved_data(PurePosixPath("AGENTS.md"), ROOT_TEXT.encode("utf-8")).decode("utf-8")
    assert moved == (
        "# Root\n\nFrom [Densho](AGENTS.fixture.md):\n\n"
        "- Read [Approval](claude/references/approval.md#directives).\n"
        "- [Governance](claude/rules/knowledge/governance.md) loads by itself.\n"
        "- Keep `.claude/references/` and the text ](AGENTS.md as they are.\n"
    )


def test_a_moved_page_keeps_its_links_inside_the_folder() -> None:
    text = (
        "From [Densho](../../AGENTS.md):\n\n"
        "- [Approval](approval.md), [Skill](../skills/a/SKILL.md), "
        "[Rule](../rules/knowledge/governance.md)\n"
    )
    moved = moved_data(PurePosixPath(".claude/references/lifecycle.md"), text.encode("utf-8"))
    assert moved.decode("utf-8") == text.replace("../../AGENTS.md", "../../AGENTS.fixture.md")


def test_a_file_that_is_not_markdown_keeps_its_bytes() -> None:
    data = b"[a](AGENTS.md)\n\xff"
    assert moved_data(PurePosixPath(".claude/skills/a/scripts/run.sh"), data) == data


def test_the_fixture_snapshot_moves_each_file_and_keeps_its_mode() -> None:
    snapshot = {
        **SNAPSHOT,
        PurePosixPath("AGENTS.md"): Output(
            b"[Skill](.claude/skills/a/SKILL.md)\n", executable=False
        ),
        ANSWERS: Output(ANSWER_TEXT.encode("utf-8"), executable=False),
    }
    moved = fixture_snapshot(snapshot)
    assert sorted(moved) == sorted(fixture_path(name) for name in snapshot)
    assert moved[PurePosixPath("AGENTS.fixture.md")].data == b"[Skill](claude/skills/a/SKILL.md)\n"
    assert moved[PurePosixPath("claude/skills/a/scripts/run.sh")].executable
    assert moved[PurePosixPath("copier-answers.yml")].data == ANSWER_TEXT.encode("utf-8")
