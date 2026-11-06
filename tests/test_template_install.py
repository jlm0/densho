# pyright: reportUnknownMemberType=false
import os
import re
import shutil
import subprocess
from pathlib import Path

import copier
import pytest
from jinja2 import Environment
from ruamel.yaml import YAML

from engine.interface import (
    VIEW_FOLDER,
    accept_entities,
    command_prefix,
    write_view,
)
from engine.parser.generated import is_generated
from engine.runtime import generate_runtime
from engine.template.history import HISTORY_FILE

REPO = Path(__file__).resolve().parents[1]
GIT = shutil.which("git") or "git"
UV = shutil.which("uv") or "uv"
SHA = "0123456789abcdef0123456789abcdef01234567"
PLANTED = (
    "planted-notes.md",
    ".planted-docs/plan.md",
    ".claude/rules/planted-local-rule.md",
    ".claude/settings.json",
    "engine/planted.py",
    "engine/schema/planted.yaml",
    "global-skills/planted/SKILL.md",
    "tests/planted.py",
    "docs/planted.md",
)
ALLOWED = (
    "AGENTS.md",
    ".copier-answers.yml",
    ".gitignore",
    ".pre-commit-config.yaml",
    "knowledge/node.md",
    "knowledge/.ka/ka",
    "knowledge/.ka/engine-constraints.txt",
    HISTORY_FILE.as_posix(),
    "knowledge/governance/schema/metamodel.yaml",
)
ALLOWED_FOLDERS = (
    ".claude/references/",
    ".claude/rules/knowledge/",
    ".claude/skills/",
    "knowledge/nodes/",
    "knowledge/skills/",
    "knowledge/governance/language/",
    "knowledge/governance/policies/",
)


def git(folder: Path, *arguments: str) -> str:
    return subprocess.run(  # noqa: S603
        [GIT, "-C", str(folder), *arguments], capture_output=True, check=True, text=True
    ).stdout


def working_tree_files() -> list[str]:
    listing = git(REPO, "ls-files", "-z", "--cached", "--others", "--exclude-standard")
    return [name for name in listing.split("\0") if name and (REPO / name).is_file()]


@pytest.fixture(scope="module")
def source(tmp_path_factory: pytest.TempPathFactory) -> Path:
    folder = tmp_path_factory.mktemp("template")
    for name in working_tree_files():
        target = folder / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(REPO / name, target)
    for name in PLANTED:
        target = folder / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("planted\n", encoding="utf-8")
    git(folder, "init", "-q", "--template=", "--initial-branch=main")
    git(folder, "config", "user.name", "Test")
    git(folder, "config", "user.email", "test@example.com")
    git(folder, "add", "-A")
    git(folder, "commit", "-qm", "the template")
    return folder


def install(source: Path, destination: Path) -> Path:
    copier.run_copy(
        str(source), destination, defaults=True, skip_tasks=True, vcs_ref="HEAD", quiet=True
    )
    return destination


@pytest.fixture(scope="module")
def installed(source: Path, tmp_path_factory: pytest.TempPathFactory) -> Path:
    return install(source, tmp_path_factory.mktemp("project"))


def files_of(folder: Path) -> list[str]:
    return sorted(
        path.relative_to(folder).as_posix() for path in folder.rglob("*") if path.is_file()
    )


def is_allowed(name: str) -> bool:
    return name in ALLOWED or name.startswith(ALLOWED_FOLDERS)


def test_an_install_holds_only_allowed_paths(installed: Path) -> None:
    names = files_of(installed)
    assert names
    assert [name for name in names if not is_allowed(name)] == []


def test_the_allowed_list_rejects_each_planted_path() -> None:
    for name in PLANTED:
        assert not is_allowed(name), name


@pytest.mark.parametrize("name", PLANTED)
def test_a_planted_path_does_not_reach_a_project(installed: Path, name: str) -> None:
    assert not (installed / name).exists()


@pytest.mark.parametrize(
    "name",
    [
        "engine",
        "tests",
        "docs",
        "build",
        "global-skills",
        "README.md",
        "pyproject.toml",
        "uv.lock",
    ],
)
def test_the_source_of_the_engine_does_not_reach_a_project(installed: Path, name: str) -> None:
    assert not (installed / name).exists()


def test_an_install_holds_each_allowed_file(installed: Path) -> None:
    for name in ALLOWED:
        assert (installed / name).is_file(), name


def test_an_install_holds_each_tracked_knowledge_file(source: Path, installed: Path) -> None:
    tracked = git(source, "ls-files").splitlines()
    wanted = [name for name in tracked if name.startswith(ALLOWED_FOLDERS)]
    assert wanted
    for name in wanted:
        assert (installed / name).read_bytes() == (source / name).read_bytes(), name


def test_no_generated_file_sits_in_the_source_folder(installed: Path) -> None:
    source = [name for name in files_of(installed) if name.startswith("knowledge/")]
    assert source
    assert [name for name in source if is_generated((installed / name).read_bytes())] == []


def test_the_schema_folder_ships_only_the_metamodel(installed: Path) -> None:
    schema = installed / "knowledge/governance/schema"
    assert files_of(schema) == ["metamodel.yaml"]


def test_no_template_suffix_stays(installed: Path) -> None:
    assert [name for name in files_of(installed) if name.endswith(".jinja")] == []


def test_each_generated_file_keeps_the_marker(installed: Path) -> None:
    generated = [
        name
        for name in files_of(installed)
        if name.endswith(("AGENTS.md", "SKILL.md"))
        or name.startswith((".claude/rules/", ".claude/references/"))
    ]
    assert generated
    for name in generated:
        assert is_generated((installed / name).read_bytes()), name


def test_the_answers_record_the_template_base(source: Path, installed: Path) -> None:
    answers = YAML(typ="safe").load((installed / ".copier-answers.yml").read_text(encoding="utf-8"))
    head = git(source, "rev-parse", "HEAD").strip()
    assert answers["started_from"] == head
    assert head.startswith(answers["_commit"])
    assert answers["_src_path"] == source.as_posix()


def test_the_wrapper_pins_the_engine_to_the_commit(source: Path, installed: Path) -> None:
    head = git(source, "rev-parse", "HEAD").strip()
    wrapper = installed / "knowledge/.ka/ka"
    assert os.access(wrapper, os.X_OK)
    text = wrapper.read_text(encoding="utf-8")
    assert f'--from "git+file://{source.as_posix()}@{head}" ka "$@"' in text
    assert '--constraints "$(dirname "$0")/engine-constraints.txt"' in text
    assert "--python 3.14" in text
    assert text.startswith("#!/bin/sh\nif ! command -v uvx")


def test_the_hooks_need_no_python_in_the_project(installed: Path) -> None:
    config = YAML(typ="safe").load(
        (installed / ".pre-commit-config.yaml").read_text(encoding="utf-8")
    )
    assert [repo["repo"] for repo in config["repos"]] == ["local"]
    hooks = {hook["id"]: hook for hook in config["repos"][0]["hooks"]}
    assert set(hooks) == {"conflict-markers", "rejected-hunks", "knowledge-checks"}
    assert hooks["knowledge-checks"]["entry"] == "knowledge/.ka/ka runtime --verify"
    assert hooks["knowledge-checks"]["always_run"] is True
    assert hooks["knowledge-checks"]["verbose"] is True
    assert hooks["knowledge-checks"]["pass_filenames"] is False
    assert hooks["conflict-markers"]["language"] == "pygrep"
    assert hooks["rejected-hunks"]["language"] == "fail"


@pytest.mark.parametrize(
    ("line", "found"),
    [
        ("<<<<<<< before updating", True),
        (">>>>>>> after updating", True),
        ("<<<<<<<", False),
        ("======= a heading", False),
        ("  <<<<<<< indented", False),
    ],
)
def test_the_marker_hook_finds_a_conflict(installed: Path, line: str, *, found: bool) -> None:
    config = YAML(typ="safe").load(
        (installed / ".pre-commit-config.yaml").read_text(encoding="utf-8")
    )
    entry = config["repos"][0]["hooks"][0]["entry"]
    assert bool(re.search(entry, line)) is found


def test_the_rejected_hunk_hook_finds_a_file(installed: Path) -> None:
    config = YAML(typ="safe").load(
        (installed / ".pre-commit-config.yaml").read_text(encoding="utf-8")
    )
    pattern = config["repos"][0]["hooks"][1]["files"]
    assert re.search(pattern, "knowledge/node.md.rej")
    assert not re.search(pattern, "knowledge/node.md")


def test_the_ignore_file_covers_the_build_output(installed: Path) -> None:
    assert (installed / ".gitignore").read_text(encoding="utf-8") == "build/\n"


@pytest.mark.parametrize(
    "name",
    [
        "AGENTS.md",
        ".pre-commit-config.yaml",
        ".gitignore",
        ".claude/skills/review-screen-hierarchy/SKILL.md",
        ".claude/rules/knowledge/governance.md",
        ".claude/references/approval.md",
    ],
)
def test_an_install_keeps_an_own_file(source: Path, tmp_path: Path, name: str) -> None:
    own = tmp_path / name
    own.parent.mkdir(parents=True, exist_ok=True)
    own.write_text("Own text.\n", encoding="utf-8")
    install(source, tmp_path)
    assert own.read_text(encoding="utf-8") == "Own text.\n"


def test_an_install_keeps_other_tool_files(source: Path, tmp_path: Path) -> None:
    names = ("CLAUDE.md", ".claude/CLAUDE.md", ".claude/settings.json", ".claude/rules/own.md")
    for name in names:
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("Own text.\n", encoding="utf-8")
    install(source, tmp_path)
    for name in names:
        assert (tmp_path / name).read_text(encoding="utf-8") == "Own text.\n"


@pytest.fixture
def project(installed: Path, tmp_path: Path) -> Path:
    folder = tmp_path / "project"
    shutil.copytree(installed, folder)
    git(folder, "init", "-q", "--template=", "--initial-branch=main")
    git(folder, "config", "user.name", "Test")
    git(folder, "config", "user.email", "test@example.com")
    assert generate_runtime(folder).problems == []
    git(folder, "add", "-A")
    git(folder, "commit", "-qm", "the install", "--no-verify")
    return folder


def test_a_project_gets_a_view_that_git_ignores(project: Path) -> None:
    report = write_view(project)
    assert report.problems == []
    assert (project / VIEW_FOLDER / "index.html").is_file()
    assert git(project, "status", "--porcelain", "--untracked-files=all") == ""


def test_a_project_page_names_the_command_of_the_project(project: Path) -> None:
    assert command_prefix(project) == "knowledge/.ka/ka"
    assert write_view(project).problems == []
    page = (project / VIEW_FOLDER / "review.html").read_text(encoding="utf-8")
    assert "knowledge/.ka/ka accept --subtree digital-product-development</code>" in page
    assert "uv run ka accept" not in page
    assert "uv run ka runtime" not in page


def test_a_project_accepts_a_proposal_and_writes_no_commit(project: Path) -> None:
    head = git(project, "rev-parse", "HEAD")
    report = accept_entities(project, ["visual-grouping"])
    assert report.problems == []
    assert [entity.label for entity in report.accepted] == ["node visual-grouping"]
    assert git(project, "rev-parse", "HEAD") == head
    changed = git(project, "diff", "--name-only").split()
    assert len(changed) == 1
    assert changed[0].endswith("visual-grouping/node.md")
    diff = git(project, "diff", "--unified=0", "--no-color").splitlines()
    assert [line for line in diff if line[:1] in {"+", "-"} and line[:3] not in {"+++", "---"}] == [
        "-status: proposed",
        "+status: accepted",
    ]


def test_a_project_is_told_of_the_commands() -> None:
    settings = YAML(typ="safe").load((REPO / "copier.yml").read_text(encoding="utf-8"))
    message = settings["_message_after_copy"]
    assert "knowledge/.ka/ka view" in message
    assert "knowledge/.ka/ka accept" in message
    assert "A person" in message


def test_the_task_runs_only_on_a_copy() -> None:
    config = YAML(typ="safe").load((REPO / "copier.yml").read_text(encoding="utf-8"))
    assert config["_tasks"] == [
        {"command": ["knowledge/.ka/ka", "adopt"], "when": "{{ _copier_operation == 'copy' }}"}
    ]


def test_the_template_ships_no_instruction_file(source: Path, installed: Path) -> None:
    assert not (installed / "CLAUDE.md").exists()
    assert not (installed / ".claude/CLAUDE.md").exists()
    assert not (source / "CLAUDE.md").exists()


@pytest.fixture
def wrapper_template() -> str:
    return (REPO / "knowledge/.ka/ka.jinja").read_text(encoding="utf-8")


@pytest.mark.parametrize(
    ("source_path", "url"),
    [
        ("https://github.com/example/repo.git", "https://github.com/example/repo.git"),
        ("gh:example/repo", "https://github.com/example/repo"),
        ("git@github.com:example/repo.git", "ssh://git@github.com/example/repo.git"),
        ("ssh://git@host/example/repo.git", "ssh://git@host/example/repo.git"),
        ("/srv/a template/repo", "file:///srv/a%20template/repo"),
    ],
)
def test_the_wrapper_reads_each_source_form(
    wrapper_template: str, source_path: str, url: str
) -> None:
    text = Environment(autoescape=False, keep_trailing_newline=True).from_string(  # noqa: S701
        wrapper_template
    )
    rendered = text.render(
        _copier_answers={"_src_path": source_path}, _copier_conf={"vcs_ref_hash": SHA}
    )
    assert f'--from "git+{url}@{SHA}" ka "$@"\n' in rendered


def test_the_constraints_match_the_lock() -> None:
    exported = subprocess.run(  # noqa: S603
        [
            UV,
            "export",
            "--frozen",
            "--no-dev",
            "--no-emit-project",
            "--no-hashes",
            "--no-annotate",
            "--no-header",
            "--quiet",
        ],
        cwd=REPO,
        capture_output=True,
        check=True,
        text=True,
    ).stdout
    assert (REPO / "knowledge/.ka/engine-constraints.txt").read_text(encoding="utf-8") == exported


def test_the_constraints_hold_the_language_model_and_no_dev_tool() -> None:
    text = (REPO / "knowledge/.ka/engine-constraints.txt").read_text(encoding="utf-8")
    assert "en-core-web-sm @ https://" in text
    assert "spacy==" in text
    assert not re.search(r"^(copier|pyright|ruff|linkml)==", text, re.MULTILINE)
