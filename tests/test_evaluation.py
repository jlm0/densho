import getpass
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING, Any, cast

import pytest
from typer.testing import CliRunner

from engine.cli import app
from engine.evaluation import EvalOptions, check_tasks, run_eval
from engine.evaluation import harness as harness_module
from engine.evaluation.check import discipline_directives
from engine.evaluation.conditions import (
    NEUTRAL_EMAIL,
    NEUTRAL_NAME,
    WITH,
    WITHOUT,
    Condition,
    build_condition,
    canary_problems,
    commit_folder,
    guard_throwaway,
    in_force_ids,
    run_git,
)
from engine.evaluation.grader import grade
from engine.evaluation.harness import LOGIN_ARGUMENTS, LOGIN_CODE
from engine.evaluation.isolation import (
    Probe,
    RunFlags,
    glob_literal,
    identity_problems,
    instruction_excludes,
    memory_folder,
    memory_problems,
    probe_problems,
    read_probe,
    run_arguments,
    run_environment,
    table_rows,
)
from engine.evaluation.report import (
    ERROR,
    FAILED,
    PASSED,
    PROBED,
    SMALL_SAMPLE,
    Counts,
    EvalReport,
    RunRecord,
    directive_counts,
    is_candidate,
    report_data,
    report_markdown,
    signal_line,
)
from engine.evaluation.tasks import (
    BAD_FOLDER,
    FIXTURE_FOLDER,
    GOOD_FOLDER,
    MAX_FILE_BYTES,
    MAX_FILES,
    MAX_TASK_BYTES,
    REPLY_FILE,
    Task,
    load_task,
    load_tasks,
    read_files,
)
from engine.generated.metamodel import Discipline, Status
from engine.governance.entities import DIRECTIVE, governed_entities
from engine.governance.status_line import set_status_lines
from engine.layout import EVALS_FOLDER, KNOWLEDGE_FOLDER
from engine.parser.node import node_folders, parse_tree

if TYPE_CHECKING:
    from collections.abc import Mapping

    from engine.parser.result import Problem

REPO = Path(__file__).resolve().parents[1]
RUNNER = CliRunner()
USAGE_ERROR = 2
DISCIPLINE = "software-engineering"
LIVE = os.environ.get("DENSHO_EVAL_LIVE") == "1"
TASKS_PER_DISCIPLINE = 3
CANARY_RUNS = 2
SMOKE_RUNS = 6
STUB_TURNS = 2
ALPHA = """---
id: alpha
kind: densho:Discipline
title: Alpha
status: proposed
origin: template
knowledge_type: domain
broader:
  - domain
---

## Definition

The meaning of alpha.

## Directives

- Write yes in the file. ^say-yes
  - scope: subtree
  - basis: judgment
  - status: proposed
  - origin: template
- Write maybe in the file. ^say-maybe
  - scope: subtree
  - basis: judgment
  - status: rejected
  - rejection_reason: The team does not use it.
  - origin: template
"""
BETA = """---
id: beta
kind: densho:Discipline
title: Beta
status: proposed
origin: template
knowledge_type: domain
broader:
  - domain
---

## Definition

The meaning of beta.

## Directives

- Write beta in the file. ^say-beta
  - scope: subtree
  - basis: judgment
  - status: proposed
  - origin: template
"""
DOMAIN = """---
id: domain
kind: densho:Domain
title: Domain
status: proposed
origin: template
knowledge_type: domain
---

## Definition

The meaning of the domain.
"""
TASK = """title: Write yes
prompt: Write yes to out.md.
tools: [Read, Write]
targets:
  - directive: say-yes
    checks:
      - path: out.md
        contains: 'yes'
      - path: out.md
        lacks: 'never'
"""
CANARY = """title: Name the rule
canary: true
prompt: Name the rule.
tools: [Read]
targets:
  - directive: say-yes
    checks:
      - path: "@reply"
        contains: 'say-yes'
"""


def write_files(folder: Path, files: Mapping[str, str]) -> None:
    for name, text in files.items():
        path = folder / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


def write_task(  # noqa: PLR0913
    repository: Path,
    name: str,
    text: str = TASK,
    *,
    discipline: str = "alpha",
    good: Mapping[str, str] | None = None,
    bad: Mapping[str, str] | None = None,
    fixture: Mapping[str, str] | None = None,
) -> Path:
    folder = repository / EVALS_FOLDER / discipline / name
    folder.mkdir(parents=True)
    (folder / "task.yaml").write_text(text, encoding="utf-8")
    (folder / GOOD_FOLDER).mkdir()
    (folder / BAD_FOLDER).mkdir()
    write_files(folder / GOOD_FOLDER, {"out.md": "yes\n"} if good is None else good)
    write_files(folder / BAD_FOLDER, {"out.md": "no\n"} if bad is None else bad)
    if fixture is not None:
        (folder / FIXTURE_FOLDER).mkdir()
        write_files(folder / FIXTURE_FOLDER, fixture)
    return folder


@pytest.fixture
def small(tmp_path: Path) -> Path:
    write_files(
        tmp_path,
        {
            "knowledge/nodes/node.md": DOMAIN,
            "knowledge/nodes/alpha/node.md": ALPHA,
            "knowledge/nodes/beta/node.md": BETA,
        },
    )
    write_task(tmp_path, "canary", CANARY, good={"reply.md": "say-yes\n"}, bad={"reply.md": "x"})
    write_task(tmp_path, "write-yes")
    write_task(
        tmp_path, "canary", CANARY, discipline="beta", good={"reply.md": "say-yes"}, bad={"x": "x"}
    )
    shutil.rmtree(tmp_path / EVALS_FOLDER / "beta")
    return tmp_path


def problem_texts(problems: list[Problem]) -> list[str]:
    return [f"{problem.code}: {problem.message}" for problem in problems]


def test_the_template_tasks_pass_their_check() -> None:
    count, problems = check_tasks(REPO)
    assert problems == []
    assert count >= 3 * 4


def test_each_discipline_with_a_directive_has_a_canary_and_3_tasks() -> None:
    tasks, problems = load_tasks(REPO)
    assert problems == []
    items, parse_problems = parse_tree(node_folders(REPO))
    assert parse_problems == []
    holding = {
        item.node.id
        for item in items
        if isinstance(item.node, Discipline) and discipline_directives(items, item.node.id)
    }
    disciplines = {task.discipline for task in tasks}
    assert (
        disciplines
        == holding
        == {
            "software-engineering",
            "ui-ux-design",
            "product-strategy",
            "brand-design",
        }
    )
    for discipline in disciplines:
        own = [task for task in tasks if task.discipline == discipline]
        assert sum(task.canary for task in own) == 1
        assert len(own) - 1 >= TASKS_PER_DISCIPLINE


def sample(task: Task, name: str) -> tuple[dict[PurePosixPath, str], str]:
    fixture, _ = read_files(task.folder / FIXTURE_FOLDER)
    files, _ = read_files(task.folder / name)
    reply = files.pop(REPLY_FILE, "")
    return {**fixture, **files}, reply


@pytest.mark.parametrize("task", load_tasks(REPO)[0], ids=lambda task: cast("Task", task).name)
def test_each_grader_passes_the_good_output_and_fails_the_bad_output(task: Task) -> None:
    assert all(result.passed for result in grade(task, *sample(task, GOOD_FOLDER)))
    assert not any(result.passed for result in grade(task, *sample(task, BAD_FOLDER)))


@pytest.mark.parametrize("task", load_tasks(REPO)[0], ids=lambda task: cast("Task", task).name)
def test_each_grader_fails_an_empty_output(task: Task) -> None:
    fixture, _ = read_files(task.folder / FIXTURE_FOLDER)
    assert not any(result.passed for result in grade(task, fixture, ""))


def test_a_small_task_set_passes(small: Path) -> None:
    assert check_tasks(small) == (2, [])


@pytest.mark.parametrize(
    ("good", "bad", "message"),
    [
        ({"out.md": "no"}, None, "The good output fails the target say-yes."),
        (None, {"out.md": "yes"}, "The bad output passes the target say-yes."),
        ({"out.md": "yes never"}, None, "The good output fails the target say-yes."),
        ({}, None, "Add a file to good/."),
        ({"AGENTS.md": "x", "out.md": "yes"}, None, "Remove this file."),
        ({".claude/settings.json": "{}", "out.md": "yes"}, None, "Remove this file."),
        ({"sub/claude.md": "x", "out.md": "yes"}, None, "Remove this file."),
    ],
)
def test_a_bad_sample_fails_the_check(
    small: Path, good: dict[str, str] | None, bad: dict[str, str] | None, message: str
) -> None:
    write_task(small, "second", good=good, bad=bad)
    _, problems = check_tasks(small)
    assert any(message in text for text in problem_texts(problems)), problems


def test_a_fixture_file_counts_in_the_samples(small: Path) -> None:
    write_task(small, "second", good={"other.md": "x"}, fixture={"out.md": "yes"})
    assert check_tasks(small) == (3, [])
    write_task(
        small, "third", good={"other.md": "x"}, bad={"other.md": "x"}, fixture={"out.md": "yes"}
    )
    _, problems = check_tasks(small)
    assert problem_texts(problems) == ["eval-task: The bad output passes the target say-yes."]


@pytest.mark.parametrize(
    ("name", "files"),
    [("reply", {"reply.md": "x"}), ("loaded", {"CLAUDE.md": "x"}), ("git", {".git/config": "x"})],
)
def test_a_bad_fixture_fails_the_check(small: Path, name: str, files: dict[str, str]) -> None:
    write_task(small, name, fixture=files)
    _, problems = check_tasks(small)
    assert any(name in str(problem.path) for problem in problems), problems


@pytest.mark.parametrize(
    ("old", "new", "message"),
    [
        ("say-yes", "say-beta", "No node in the subtree of alpha holds say-beta."),
        ("say-yes", "say-gone", "No node in the subtree of alpha holds say-gone."),
        ("say-yes", "say-maybe", "say-maybe is rejected. Remove the target."),
    ],
)
def test_a_bad_target_fails_the_check(small: Path, old: str, new: str, message: str) -> None:
    write_task(small, "second", TASK.replace(old, new))
    _, problems = check_tasks(small)
    assert f"eval-task: {message}" in problem_texts(problems)


def test_a_discipline_needs_one_canary(small: Path) -> None:
    write_task(small, "second-canary", CANARY, good={"reply.md": "say-yes"}, bad={"reply.md": "x"})
    _, problems = check_tasks(small)
    assert "eval-task: A discipline needs 1 canary task, and alpha has 2." in problem_texts(
        problems
    )
    shutil.rmtree(small / EVALS_FOLDER / "alpha" / "canary")
    shutil.rmtree(small / EVALS_FOLDER / "alpha" / "second-canary")
    _, problems = check_tasks(small)
    assert "eval-task: A discipline needs 1 canary task, and alpha has 0." in problem_texts(
        problems
    )


def test_a_folder_that_is_not_a_discipline_fails(small: Path) -> None:
    write_task(small, "canary", CANARY, discipline="gamma", good={"reply.md": "say-yes"})
    _, problems = check_tasks(small)
    assert "eval-task: gamma is not the ID of a densho:Discipline node." in problem_texts(problems)


def test_a_broken_node_stops_the_check(small: Path) -> None:
    (small / "knowledge/nodes/alpha/node.md").write_text("---\nid: alpha\n", encoding="utf-8")
    count, problems = check_tasks(small)
    assert count == 0
    assert problems


@pytest.mark.parametrize(
    ("old", "new", "message"),
    [
        ("title: Write yes\n", "title: Write yes\nextra: 1\n", "Remove the field 'extra'"),
        ("title: Write yes\n", "title: ''\n", "title must be a text that is not empty."),
        ("title: Write yes\n", "title: |\n  a\n  b\n", "title must be one line."),
        ("prompt: Write yes to out.md.\n", "prompt: 3\n", "prompt must be a text"),
        ("tools: [Read, Write]", "tools: Read", "tools must be a list"),
        ("tools: [Read, Write]", "tools: [Read, WebFetch]", "Name each tool once"),
        ("tools: [Read, Write]", "tools: [Read, Read]", "Name each tool once"),
        ("title: Write yes\n", "title: Write yes\ncanary: 1\n", "canary must be true or false."),
        ("targets:\n", "targets: []\nold:\n", "targets must be a list of 1 or more targets."),
        ("  - directive: say-yes\n", "  - directive: Say Yes\n", "directive must be the ID"),
        ("  - directive: say-yes\n", "  - directive: say-yes\n    extra: 1\n", "Remove the field"),
        ("    checks:\n", "    checks: []\n    old:\n", "checks must be a list of 1 or more"),
        ("      - path: out.md\n        contains: 'yes'\n", "      - x\n", "Each check must be a"),
        ("        contains: 'yes'\n", "        lacks: 'yes'\n", "A target needs a contains check."),
        ("        contains: 'yes'\n", "        contains: 'yes'\n        lacks: 'y'\n", "one of"),
        ("        lacks: 'never'\n", "        min: 1\n", "one of contains and lacks"),
        ("        contains: 'yes'\n", "        contains: '(['\n", "is not valid"),
        ("        contains: 'yes'\n", "        contains: ''\n", "must be a regular expression"),
        ("        contains: 'yes'\n", "        contains: 'yes'\n        min: 0\n", "min must be 1"),
        ("        contains: 'yes'\n", "        contains: 'y'\n        min: -1\n", "whole number"),
        ("        contains: 'yes'\n", "        contains: 'y'\n        min: true\n", "whole number"),
        (
            "        contains: 'yes'\n",
            "        contains: 'y'\n        min: 3\n        max: 2\n",
            "max",
        ),
        ("        contains: 'yes'\n", "        contains: 'y'\n        max: x\n", "whole number"),
        ("        lacks: 'never'\n", "        lacks: 'never'\n        min: 1\n", "cannot have min"),
        ("        lacks: 'never'\n", "        lacks: 'never'\n        max: 1\n", "cannot have max"),
        (
            "      - path: out.md\n        contains",
            "      - path: /out.md\n        contains",
            "path",
        ),
        ("      - path: out.md\n        contains", "      - path: a\\b\n        contains", "path"),
        (
            "      - path: out.md\n        contains",
            "      - path: ../out.md\n        contains",
            ". or",
        ),
        ("      - path: out.md\n        contains", "      - path: a//b\n        contains", ". or"),
        ("      - path: out.md\n        contains", "      - path: 3\n        contains", "path"),
        ("title: Write yes\n", "---\ntitle: Write yes\n", "Remove the --- line."),
        ("title: Write yes\n", "title: [\n", "eval-task"),
    ],
)
def test_a_bad_task_file_fails_to_load(tmp_path: Path, old: str, new: str, message: str) -> None:
    assert old in TASK
    folder = write_task(tmp_path, "task", TASK.replace(old, new, 1))
    loaded = load_task(folder)
    assert isinstance(loaded, list)
    assert any(message in text for text in problem_texts(loaded)) or message == "eval-task", loaded


def test_a_bad_task_problem_names_its_line(tmp_path: Path) -> None:
    folder = write_task(tmp_path, "task", TASK.replace("[Read, Write]", "[Read, Fetch]"))
    loaded = load_task(folder)
    assert isinstance(loaded, list)
    assert [(problem.path.name, problem.line) for problem in loaded] == [("task.yaml", 3)]


def test_a_duplicate_target_fails_to_load(tmp_path: Path) -> None:
    text = TASK + TASK[TASK.index("  - directive") :]
    loaded = load_task(write_task(tmp_path, "task", text))
    assert isinstance(loaded, list)
    assert "eval-task: Name say-yes in one target only." in problem_texts(loaded)


def test_a_long_prompt_fails_to_load(tmp_path: Path) -> None:
    text = TASK.replace("Write yes to out.md.", "a " * 2001)
    loaded = load_task(write_task(tmp_path, "task", text))
    assert isinstance(loaded, list)
    assert any("prompt must hold at most" in text for text in problem_texts(loaded))


def test_a_large_or_broken_task_file_fails_to_load(tmp_path: Path) -> None:
    folder = write_task(tmp_path, "large")
    (folder / "task.yaml").write_text(TASK + "#" * MAX_TASK_BYTES, encoding="utf-8")
    loaded = load_task(folder)
    assert isinstance(loaded, list)
    assert any("at most" in text for text in problem_texts(loaded))
    folder = write_task(tmp_path, "broken")
    (folder / "task.yaml").write_bytes(b"title: \xff\n")
    loaded = load_task(folder)
    assert isinstance(loaded, list)
    assert [problem.code for problem in loaded] == ["encoding"]


@pytest.mark.parametrize(
    ("change", "message"),
    [
        ("extra", "Remove 'notes.md'."),
        ("no-good", "Add the folder good/"),
        ("no-bad", "Add the folder bad/"),
        ("fixture-file", "fixture must be a folder."),
        ("no-task", "Add task.yaml as a regular file."),
        ("linked-task", "Add task.yaml as a regular file."),
        ("linked-good", "good must be a folder."),
    ],
)
def test_a_bad_task_folder_fails_to_load(tmp_path: Path, change: str, message: str) -> None:
    folder = write_task(tmp_path, "task")
    match change:
        case "extra":
            (folder / "notes.md").write_text("x", encoding="utf-8")
        case "no-good":
            shutil.rmtree(folder / GOOD_FOLDER)
        case "no-bad":
            shutil.rmtree(folder / BAD_FOLDER)
        case "fixture-file":
            (folder / FIXTURE_FOLDER).write_text("x", encoding="utf-8")
        case "no-task":
            (folder / "task.yaml").unlink()
        case "linked-task":
            (tmp_path / "real.yaml").write_text(TASK, encoding="utf-8")
            (folder / "task.yaml").unlink()
            (folder / "task.yaml").symlink_to(tmp_path / "real.yaml")
        case _:
            shutil.rmtree(folder / GOOD_FOLDER)
            (tmp_path / "real-good").mkdir()
            (folder / GOOD_FOLDER).symlink_to(tmp_path / "real-good")
    loaded = load_task(folder)
    assert isinstance(loaded, list)
    assert any(message in text for text in problem_texts(loaded)), loaded


def test_a_task_folder_name_must_be_an_id(tmp_path: Path) -> None:
    loaded = load_task(write_task(tmp_path, "Task_1"))
    assert isinstance(loaded, list)
    assert any("must be IDs" in text for text in problem_texts(loaded))


def test_a_file_in_a_discipline_folder_fails(small: Path) -> None:
    (small / EVALS_FOLDER / "alpha" / "notes.md").write_text("x", encoding="utf-8")
    _, problems = load_tasks(small)
    assert problem_texts(problems) == ["eval-task: A discipline folder holds only task folders."]


def test_the_loader_reads_each_field(small: Path) -> None:
    tasks, problems = load_tasks(small, "alpha")
    assert problems == []
    canary, task = tasks
    assert (canary.canary, task.canary) == (True, False)
    assert task.name == "alpha/write-yes"
    assert task.tools == ("Read", "Write")
    assert task.prompt == "Write yes to out.md."
    assert [(target.directive, len(target.checks)) for target in task.targets] == [("say-yes", 2)]
    assert [check.kind for check in task.targets[0].checks] == ["contains", "lacks"]
    assert load_tasks(small, "beta") == ([], [])


def test_read_files_skips_and_reports(tmp_path: Path) -> None:
    write_files(tmp_path, {"a.md": "a", ".git/x": "x", "AGENTS.md": "x", "sub/b.md": "b"})
    (tmp_path / "big.md").write_bytes(b"x" * (MAX_FILE_BYTES + 10))
    (tmp_path / "link.md").symlink_to(tmp_path / "a.md")
    (tmp_path / "linked").symlink_to(tmp_path / "sub")
    files, problems = read_files(tmp_path, skipped=frozenset({".git", "AGENTS.md"}))
    assert sorted(map(str, files)) == ["a.md", "big.md", "sub/b.md"]
    assert len(files[PurePosixPath("big.md")]) == MAX_FILE_BYTES
    assert sorted((problem.path.name, problem.code) for problem in problems) == [
        ("link.md", "symlink"),
        ("linked", "symlink"),
    ]


def test_read_files_keeps_at_most_the_file_limit(tmp_path: Path) -> None:
    write_files(tmp_path, {f"f{index:03}.md": "x" for index in range(205)})
    files, problems = read_files(tmp_path)
    assert len(files) == MAX_FILES
    assert problem_texts(problems) == ["eval-task: Keep at most 200 files."]


def graded(repository: Path, text: str, files: Mapping[str, str], reply: str = "") -> list[bool]:
    folder = write_task(repository, f"task-{len(list(repository.rglob('task.yaml')))}", text)
    loaded = load_task(folder)
    assert isinstance(loaded, Task), loaded
    paths = {PurePosixPath(name): value for name, value in files.items()}
    return [result.passed for result in grade(loaded, paths, reply)]


def one_check(path: str, check: str) -> str:
    return TASK.replace(
        "      - path: out.md\n        contains: 'yes'\n"
        "      - path: out.md\n        lacks: 'never'\n",
        f"      - path: {path}\n{check}",
    )


@pytest.mark.parametrize(
    ("path", "check", "files", "reply", "passed"),
    [
        ("out.md", "        contains: 'yes'\n", {"out.md": "yes"}, "", True),
        ("out.md", "        contains: 'yes'\n", {"out.md": "no"}, "", False),
        ("out.md", "        contains: 'yes'\n", {}, "", False),
        ("out.md", "        contains: 'yes'\n", {"other.md": "yes"}, "", False),
        ("out.md", "        contains: 'yes'\n        min: 2\n", {"out.md": "yes"}, "", False),
        ("out.md", "        contains: 'yes'\n        min: 2\n", {"out.md": "yes yes"}, "", True),
        ("out.md", "        contains: 'y'\n        max: 1\n", {"out.md": "y y"}, "", False),
        ("out.md", "        contains: 'y'\n        max: 2\n", {"out.md": "y y"}, "", True),
        ('"*.md"', "        contains: 'y'\n        min: 2\n", {"a.md": "y", "b.md": "y"}, "", True),
        ('"*.md"', "        contains: 'y'\n", {"sub/a.md": "y"}, "", False),
        ('"**/*.md"', "        contains: 'y'\n", {"sub/a.md": "y"}, "", True),
        ('"@reply"', "        contains: 'yes'\n", {"out.md": "yes"}, "yes", True),
        ('"@reply"', "        contains: 'yes'\n", {"out.md": "yes"}, "no", False),
        ("out.md", "        contains: '^b'\n", {"out.md": "a\nb"}, "", True),
    ],
)
def test_the_grader_counts_each_check(  # noqa: PLR0913
    tmp_path: Path, path: str, check: str, files: dict[str, str], reply: str, *, passed: bool
) -> None:
    assert graded(tmp_path, one_check(path, check), files, reply) == [passed]


def test_a_lacks_check_fails_on_a_match_and_on_no_output(tmp_path: Path) -> None:
    assert graded(tmp_path, TASK, {"out.md": "yes"}) == [True]
    assert graded(tmp_path, TASK, {"out.md": "yes never"}) == [False]
    text = TASK.replace(
        "      - path: out.md\n        lacks", "      - path: gone.md\n        lacks"
    )
    assert graded(tmp_path, text, {"out.md": "yes"}) == [False]


def test_a_failure_names_the_check_line(tmp_path: Path) -> None:
    folder = write_task(tmp_path, "task")
    loaded = load_task(folder)
    assert isinstance(loaded, Task)
    results = grade(loaded, {PurePosixPath("out.md"): "never"}, "")
    assert [result.failures for result in results] == [
        (
            "line 7: 0 matches in out.md, 1 needed",
            "line 9: 1 matches in out.md, 0 allowed",
        )
    ]


def test_the_parser_skips_the_eval_folder(small: Path) -> None:
    write_files(small, {"knowledge/evals/alpha/write-yes/good/notes.md": "# Not a node\n"})
    items, problems = parse_tree(node_folders(small))
    assert problems == []
    assert sorted(item.node.id for item in items) == ["alpha", "beta", "domain"]
    write_files(small, {"knowledge/nodes/evals/notes.md": "# Not a node\n"})
    _, problems = parse_tree(node_folders(small))
    assert [problem.code for problem in problems] == ["file-name"]


def probe_text(folder: Path, memory: list[str], skills: list[str], agents: list[str]) -> str:
    return "\n".join(
        [
            "## Context Usage",
            "",
            "### Memory Files",
            "",
            "| Type | Path | Tokens |",
            "|------|------|--------|",
            f"| Project | {folder / 'AGENTS.md'} | 14 |",
            *memory,
            "",
            "### Skills",
            "",
            "| Skill | Source | Tokens |",
            "|-------|--------|--------|",
            "| dataviz | Built-in | ~480 |",
            *skills,
            "",
            *(
                ["### Custom Agents", "", "| Agent | Source | Tokens |", "|---|---|---|"]
                if agents
                else []
            ),
            *agents,
        ]
    )


def init_event(tools: list[str], /, **changes: object) -> dict[str, object]:
    event: dict[str, object] = {
        "type": "system",
        "subtype": "init",
        "tools": tools,
        "mcp_servers": [],
        "plugins": [{"name": "cc-plugin-privacy", "path": "builtin"}],
        "output_style": "default",
    }
    return {**event, **changes}


@pytest.fixture
def run_folder(tmp_path: Path) -> Path:
    folder = tmp_path / "run"
    write_files(folder, {"AGENTS.md": "# Run\n", ".claude/skills/own/SKILL.md": "x"})
    return folder


def clean_probe(folder: Path) -> Probe:
    return Probe(
        init_event(["Read", "Skill"]), probe_text(folder, [], ["| own | Project | 9 |"], []), 0
    )


def test_a_clean_probe_passes(run_folder: Path) -> None:
    assert probe_problems(run_folder, clean_probe(run_folder), ("Read",)) == []


@pytest.mark.parametrize(
    ("change", "code"),
    [
        ({"memory": ["| User | /home/someone/.claude/CLAUDE.md | 9 |"]}, "memory-file"),
        ({"memory": ["| Project | ../AGENTS.md | 9 |"]}, "memory-file"),
        ({"skills": ["| mine | User | 9 |"]}, "skill"),
        ({"skills": ["| from-plugin | Plugin | 9 |"]}, "skill"),
        ({"skills": ["| other | Project | 9 |"]}, "skill"),
        ({"skills": ["| broken |"]}, "skill"),
        ({"agents": ["| reviewer | User | 9 |"]}, "agent"),
        ({"init": {"plugins": [{"name": "mine", "path": "/plugins/mine"}]}}, "plugin"),
        ({"init": {"mcp_servers": [{"name": "server"}]}}, "mcp"),
        ({"init": {"mcp_servers": None}}, "mcp"),
        ({"init": {"tools": ["Read", "Skill", "Bash"]}}, "tool"),
        ({"init": {"tools": ["Skill"]}}, "tool"),
        ({"init": {"output_style": "Explanatory"}}, "output-style"),
        ({"cost": 0.2}, "probe"),
        ({"cost": None}, "probe"),
    ],
)
def test_each_leak_fails_the_probe(run_folder: Path, change: dict[str, object], code: str) -> None:
    memory = cast("list[str]", change.get("memory", []))
    skills = ["| own | Project | 9 |", *cast("list[str]", change.get("skills", []))]
    agents = cast("list[str]", change.get("agents", []))
    init = init_event(["Read", "Skill"], **cast("dict[str, object]", change.get("init", {})))
    cost = cast("float | None", change.get("cost", 0))
    probe = Probe(init, probe_text(run_folder, memory, skills, agents), cost)
    assert [problem.code for problem in probe_problems(run_folder, probe, ("Read",))] == [code]


def test_a_probe_without_the_run_agents_file_fails(run_folder: Path) -> None:
    probe = clean_probe(run_folder)
    text = probe.context.replace(str(run_folder / "AGENTS.md"), str(run_folder / "OTHER.md"))
    found = probe_problems(run_folder, Probe(probe.init, text, 0), ("Read",))
    assert [problem.code for problem in found] == ["instructions"]


def test_a_probe_without_a_skill_table_fails(run_folder: Path) -> None:
    probe = clean_probe(run_folder)
    text = probe.context.replace("### Skills", "### Other")
    found = probe_problems(run_folder, Probe(probe.init, text, 0), ("Read",))
    assert [problem.code for problem in found] == ["skill"]
    assert probe_problems(run_folder, None, ("Read",))[0].code == "probe"


def test_read_probe_takes_the_init_and_the_result() -> None:
    init = json.dumps(init_event(["Read"]))
    result = json.dumps({"type": "result", "result": "text", "total_cost_usd": 0})
    probe = read_probe(f"not json\n[1]\n{init}\n{result}\n")
    assert probe is not None
    assert (probe.context, probe.cost, probe.init["tools"]) == ("text", 0, ["Read"])
    assert read_probe(init) is None
    assert read_probe(result) is None
    for value in ("0", True, None):
        changed = json.dumps({"type": "result", "result": "text", "total_cost_usd": value})
        probe = read_probe(f"{init}\n{changed}\n")
        assert probe is not None
        assert probe.cost is None


def test_table_rows_reads_one_section() -> None:
    text = "### A\n\n| H | I |\n|---|---|\n| a | b |\n\n### B\n\n| H |\n|---|\n"
    assert table_rows(text, "A") == [["a", "b"]]
    assert table_rows(text, "B") == []
    assert table_rows(text, "C") is None
    assert table_rows("### A\n", "A") == []


def test_glob_literal_escapes_each_glob_character() -> None:
    assert glob_literal("/a b/c*[d]{e}(f)!+@?") == "/a b/c[*][[]d[]][{]e[}][(]f[)][!][+][@][?]"


def test_the_excludes_name_each_folder_above_the_run(tmp_path: Path) -> None:
    folder = tmp_path / "x" / "run"
    home = tmp_path / "home"
    patterns = instruction_excludes(folder, home)
    for parent in (tmp_path.resolve(), (tmp_path / "x").resolve()):
        for name in ("CLAUDE.md", "CLAUDE.local.md", "AGENTS.md", ".claude/CLAUDE.md"):
            assert glob_literal(parent / name) in patterns
        assert f"{glob_literal(parent / '.claude/rules')}/**" in patterns
    assert glob_literal(home / ".claude/CLAUDE.md") in patterns
    assert f"{glob_literal(home / '.claude/rules')}/**" in patterns
    assert not any(pattern.startswith(glob_literal(folder.resolve())) for pattern in patterns)
    assert len(patterns) == len(set(patterns))


def test_the_run_arguments_isolate_the_run(tmp_path: Path) -> None:
    flags = RunFlags("claude", "sonnet", 0.3, ("Read", "Write"))
    arguments = run_arguments(flags, tmp_path, tmp_path / "home", probe=False)
    settings = json.loads(arguments[arguments.index("--settings") + 1])
    assert settings["autoMemoryEnabled"] is False
    assert settings["claudeMdExcludes"] == instruction_excludes(tmp_path, tmp_path / "home")
    arguments.remove(arguments[arguments.index("--settings") + 1])
    assert arguments == [
        "claude",
        "-p",
        "--output-format",
        "json",
        "--model",
        "sonnet",
        "--tools",
        "Read,Write,Skill",
        "--permission-mode",
        "acceptEdits",
        "--permission-prompts",
        "none",
        "--setting-sources",
        "project",
        "--settings",
        "--strict-mcp-config",
        "--no-session-persistence",
        "--max-budget-usd",
        "0.30",
    ]
    probe = run_arguments(flags, tmp_path, tmp_path / "home", probe=True)
    assert probe[2:5] == ["--output-format", "stream-json", "--verbose"]
    assert probe[-2:] == ["--max-budget-usd", "0.01"]


def test_the_run_environment_holds_no_session_variable(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    for name in ("ANTHROPIC_API_KEY", "GIT_AUTHOR_NAME", "CLAUDECODE", "CLAUDE_CODE_SSE_PORT"):
        monkeypatch.setenv(name, "planted")
    monkeypatch.delenv("LOGNAME", raising=False)
    monkeypatch.setenv("USER", "account")
    monkeypatch.setenv("PATH", "/bin")
    environment = run_environment(tmp_path / "home", tmp_path / "gitconfig")
    assert environment == {
        "HOME": str(tmp_path / "home"),
        "USER": "account",
        "PATH": "/bin",
        "LANG": "en_US.UTF-8",
        "TERM": "dumb",
        "CLAUDE_CODE_DISABLE_AUTO_MEMORY": "1",
        "GIT_CONFIG_GLOBAL": str(tmp_path / "gitconfig"),
        "GIT_CONFIG_NOSYSTEM": "1",
    }


def test_an_auto_memory_folder_fails(tmp_path: Path) -> None:
    folder = tmp_path / "a.b" / "run"
    home = tmp_path / "home"
    assert memory_problems(folder, home) == []
    memory = memory_folder(folder, home)
    memory.mkdir(parents=True)
    assert [problem.code for problem in memory_problems(folder, home)] == ["auto-memory"]
    expected = home / ".claude/projects/-x-a-b-c-run/memory"
    assert memory_folder(Path("/x/a.b_c/run"), home) == expected


@pytest.fixture
def git_config(tmp_path: Path) -> Path:
    path = tmp_path / "gitconfig"
    path.write_text("[user]\n\tname = Someone\n\temail = someone@example.com\n", encoding="utf-8")
    return path


def test_a_throwaway_commit_has_the_neutral_identity(tmp_path: Path, git_config: Path) -> None:
    folder = tmp_path / "repo"
    write_files(folder, {"a.md": "a"})
    assert commit_folder(folder, git_config, "first") == []
    assert identity_problems(folder, git_config) == []
    log = run_git(folder, git_config, "log", "--format=%an %ae %cn %ce").stdout.split()
    assert log == [NEUTRAL_NAME, NEUTRAL_EMAIL, NEUTRAL_NAME, NEUTRAL_EMAIL]


def test_another_identity_fails(tmp_path: Path, git_config: Path) -> None:
    folder = tmp_path / "repo"
    write_files(folder, {"a.md": "a"})
    assert commit_folder(folder, git_config, "first") == []
    run_git(folder, git_config, "config", "user.name", "Someone")
    assert [problem.code for problem in identity_problems(folder, git_config)] == ["git-identity"]
    run_git(folder, git_config, "config", "user.name", NEUTRAL_NAME)
    write_files(folder, {"b.md": "b"})
    run_git(folder, git_config, "add", "-A")
    run_git(folder, git_config, "-c", "user.email=x@example.com", "commit", "-qm", "second")
    assert [problem.code for problem in identity_problems(folder, git_config)] == ["git-identity"]


def test_a_failed_git_step_is_a_problem(tmp_path: Path, git_config: Path) -> None:
    folder = tmp_path / "file"
    folder.write_text("x", encoding="utf-8")
    problems = commit_folder(folder, git_config, "first")
    assert [problem.code for problem in problems] == ["eval-condition"]


def test_the_guard_keeps_the_eval_in_its_work_folder(tmp_path: Path) -> None:
    work = tmp_path / "work"
    repository = tmp_path / "project"
    guard_throwaway(work / "conditions" / WITH, work, repository)
    for source in (tmp_path / "elsewhere", work, tmp_path):
        with pytest.raises(ValueError, match="work folder"):
            guard_throwaway(source, work, repository)
    with pytest.raises(ValueError, match="project tree"):
        guard_throwaway(work / "a", work, work / "a" / "project")
    with pytest.raises(ValueError, match="project tree"):
        guard_throwaway(
            repository / "knowledge/x/conditions/with", repository / "knowledge/x", repository
        )


def knowledge_snapshot() -> dict[Path, bytes]:
    return {
        path: path.read_bytes() for path in (REPO / KNOWLEDGE_FOLDER).rglob("*") if path.is_file()
    }


class BuiltConditions:
    def __init__(self, work: Path) -> None:
        self.work = work
        self.git_config = work / "gitconfig"
        self.git_config.write_text("", encoding="utf-8")
        self.built: dict[str, dict[str, Condition]] = {}

    def __getitem__(self, discipline: str) -> dict[str, Condition]:
        if discipline not in self.built:
            before = knowledge_snapshot()
            own = self.work / discipline
            own.mkdir()
            for name in (WITH, WITHOUT):
                condition = build_condition(REPO, own, discipline, name, self.git_config)
                assert isinstance(condition, Condition), condition
                self.built.setdefault(discipline, {})[name] = condition
            assert knowledge_snapshot() == before
        return self.built[discipline]


@pytest.fixture(scope="module")
def conditions(tmp_path_factory: pytest.TempPathFactory) -> BuiltConditions:
    return BuiltConditions(tmp_path_factory.mktemp("conditions"))


@pytest.mark.parametrize(
    "discipline", ["software-engineering", "ui-ux-design", "product-strategy", "brand-design"]
)
def test_the_conditions_differ_only_in_the_discipline(
    conditions: BuiltConditions, discipline: str
) -> None:
    found, absent = conditions[discipline][WITH], conditions[discipline][WITHOUT]
    own = set(found.directives)
    assert own == set(absent.directives)
    assert in_force_ids(found.files) >= {
        directive for directive, status in found.directives.items() if status.value == "accepted"
    }
    assert in_force_ids(absent.files) & own == set()
    assert in_force_ids(found.files) - own == in_force_ids(absent.files)
    assert all(status.value == "accepted" for status in found.directives.values())
    assert set(found.files) == set(absent.files)
    assert not any(path.parts[0] == "knowledge" for path in found.files)
    assert (found.source / KNOWLEDGE_FOLDER / "evals").exists() is False


@pytest.mark.parametrize(
    "discipline", ["software-engineering", "ui-ux-design", "product-strategy", "brand-design"]
)
def test_the_static_canary_passes_for_each_discipline(
    conditions: BuiltConditions, discipline: str
) -> None:
    tasks, _ = load_tasks(REPO, discipline)
    targets = [target.directive for task in tasks for target in task.targets]
    canary = [target.directive for task in tasks if task.canary for target in task.targets]
    found, absent = conditions[discipline][WITH], conditions[discipline][WITHOUT]
    assert canary_problems(found, absent, targets, canary) == []


def condition(name: str, files: dict[str, str], directives: dict[str, str]) -> Condition:
    return Condition(
        name,
        "alpha",
        Path(name),
        {PurePosixPath(path): text.encode() for path, text in files.items()},
        {key: Status(value) for key, value in directives.items()},
    )


def test_the_static_canary_finds_each_leak() -> None:
    found = condition(WITH, {"AGENTS.md": "- Write yes. ^say-yes\n"}, {"say-yes": "accepted"})
    absent = condition(WITHOUT, {"AGENTS.md": "# Nothing\n"}, {"say-yes": "proposed"})
    assert canary_problems(found, absent, ["say-yes"], ["say-yes"]) == []
    empty = condition(WITH, {"AGENTS.md": "# Nothing\n"}, {"say-yes": "accepted"})
    assert problem_texts(canary_problems(empty, absent, ["say-yes"], [])) == [
        "eval-canary: The with condition does not hold say-yes in force."
    ]
    leaked = condition(WITHOUT, {"a.md": "- Write yes. ^say-yes\n"}, {"say-yes": "proposed"})
    assert "eval-canary: The without condition holds say-yes in force." in problem_texts(
        canary_problems(found, leaked, ["say-yes"], [])
    )
    named = condition(WITHOUT, {"a.md": "See say-yes.\n"}, {"say-yes": "proposed"})
    assert problem_texts(canary_problems(found, named, ["say-yes"], ["say-yes"])) == [
        "eval-canary: A without file names the canary target say-yes. Choose another target."
    ]
    near = condition(WITHOUT, {"a.md": "See say-yes-more and do-say-yes.\n"}, {})
    assert canary_problems(found, near, ["say-yes"], ["say-yes"]) == []


STUB = """
import json
import os
import re
import sys
import time
from pathlib import Path

plan = json.loads(Path(__file__).with_name("plan.json").read_text(encoding="utf-8"))
arguments = sys.argv[1:]
prompt = sys.stdin.read()
if arguments == ["auth", "status"]:
    with Path(plan["log"]).with_name("logins.jsonl").open("a", encoding="utf-8") as log:
        entry = {"folder": str(Path.cwd()), "home": os.environ.get("HOME"),
                 "user": os.environ.get("USER"), "stdin": prompt}
        log.write(json.dumps(entry) + "\\n")
    print(json.dumps({"loggedIn": plan.get("login", 0) == 0, "email": PLANTED_EMAIL}))
    print(PLANTED_EMAIL, file=sys.stderr)
    raise SystemExit(plan.get("login", 0))
here = Path.cwd()
probe = "stream-json" in arguments
with Path(plan["log"]).open("a", encoding="utf-8") as log:
    log.write(json.dumps({"probe": probe, "folder": str(here)}) + "\\n")
tools = arguments[arguments.index("--tools") + 1].split(",")
if probe:
    skills = sorted(path.parent.name for path in (here / ".claude/skills").glob("*/SKILL.md"))
    rows = [f"| {name} | Project | 9 |" for name in skills] + plan.get("skills", [])
    context = "\\n".join(
        ["### Memory Files", "", "| Type | Path | Tokens |", "|---|---|---|"]
        + [f"| Project | {here / 'AGENTS.md'} | 14 |", ""]
        + ["### Skills", "", "| Skill | Source | Tokens |", "|---|---|---|"]
        + rows
    )
    init = {"type": "system", "subtype": "init", "tools": tools, "mcp_servers": [],
            "plugins": [], "output_style": "default"}
    print(json.dumps(init))
    print(json.dumps({"type": "result", "subtype": "success", "result": context,
                      "total_cost_usd": 0}))
    raise SystemExit(0)
texts = [path.read_text(encoding="utf-8") for path in (here / ".claude").rglob("*.md")]
texts.append((here / "AGENTS.md").read_text(encoding="utf-8"))
in_force = set(re.findall(r"\\^([a-z0-9-]+)[ \\t]*$", "\\n".join(texts), re.MULTILINE))
answer = next(entry for entry in plan["answers"] if entry["prompt"] == prompt)
mode = answer.get("mode", "obey")
if mode == "error":
    print(json.dumps({"type": "result", "subtype": "error_max_budget_usd", "is_error": True,
                      "total_cost_usd": plan["cost"]}))
    raise SystemExit(1)
if mode == "garbage":
    print("not json")
    raise SystemExit(0)
if mode == "sleep":
    time.sleep(5)
if mode == "flagged":
    print(json.dumps({"type": "result", "subtype": "success", "is_error": True, "result": "x" * 300,
                      "total_cost_usd": plan["cost"]}))
    raise SystemExit(0)
if mode == "memory":
    slug = re.sub("[^A-Za-z0-9]", "-", str(here.resolve()))
    (Path.home() / ".claude" / "projects" / slug / "memory").mkdir(parents=True)
sample = answer["good"] if mode == "same" or set(answer["targets"]) <= in_force else answer["bad"]
for name, text in sample["files"].items():
    path = here / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
print(json.dumps({"type": "result", "subtype": "success", "is_error": False,
                  "result": sample["reply"], "total_cost_usd": plan["cost"], "num_turns": 2,
                  "duration_ms": 1500, "modelUsage": {"claude-stub": {}}}))
"""
SMOKE_TASK = "commit-breaking-change"
PLANTED_EMAIL = "planted@example.invalid"


def sample_answer(task: Task, name: str) -> dict[str, object]:
    files, _ = read_files(task.folder / name)
    reply = files.pop(REPLY_FILE, "")
    return {"files": {str(path): text for path, text in files.items()}, "reply": reply}


def write_stub(folder: Path, modes: Mapping[str, str], **plan: object) -> Path:
    folder.mkdir(parents=True, exist_ok=True)
    tasks, _ = load_tasks(REPO, DISCIPLINE)
    answers = [
        {
            "prompt": task.prompt,
            "targets": [target.directive for target in task.targets],
            "good": sample_answer(task, GOOD_FOLDER),
            "bad": sample_answer(task, BAD_FOLDER),
            "mode": modes.get(task.id, "obey"),
        }
        for task in tasks
    ]
    data = {"log": str(folder / "calls.jsonl"), "cost": 0.01, "answers": answers, **plan}
    (folder / "plan.json").write_text(json.dumps(data), encoding="utf-8")
    stub = folder / "claude"
    script = STUB.replace("PLANTED_EMAIL", repr(PLANTED_EMAIL))
    stub.write_text(f"#!{sys.executable} -I\n{script}", encoding="utf-8")
    stub.chmod(0o755)
    return stub


def calls(stub: Path, name: str = "calls.jsonl") -> list[dict[str, object]]:
    log = stub.with_name(name)
    if not log.exists():
        return []
    return [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()]


@pytest.fixture
def prebuilt(conditions: BuiltConditions, monkeypatch: pytest.MonkeyPatch) -> list[str]:
    built: list[str] = []

    def fake(repository: Path, work: Path, discipline: str, name: str, git_config: Path) -> object:
        assert (repository, discipline) == (REPO, DISCIPLINE)
        assert git_config.read_text(encoding="utf-8") == ""
        guard_throwaway(work / "conditions" / name, work, repository)
        built.append(name)
        return conditions[DISCIPLINE][name]

    monkeypatch.setattr(harness_module, "build_condition", fake)
    return built


def options(stub: Path, work: Path, **changes: object) -> EvalOptions:
    values: dict[str, object] = {
        "tasks": (SMOKE_TASK,),
        "runs": 2,
        "budget": 1.0,
        "run_budget": 0.1,
        "work": work,
        "claude": str(stub),
        "home": work.parent / "home",
        **changes,
    }
    return EvalOptions(DISCIPLINE, **cast("dict[str, Any]", values))


def statuses(report: EvalReport) -> list[tuple[str, str, int, str]]:
    return [(run.task, run.condition, run.repeat, run.status) for run in report.runs]


def test_the_harness_runs_the_canary_first_and_interleaves(
    tmp_path: Path, prebuilt: list[str]
) -> None:
    stub = write_stub(tmp_path / "stub", {})
    work = tmp_path / "work"
    report = run_eval(REPO, options(stub, work))
    assert report.problems == []
    assert prebuilt == [WITH, WITHOUT]
    canary = "canary-commit-rules"
    assert statuses(report) == [
        (canary, WITH, 1, PASSED),
        (canary, WITHOUT, 1, FAILED),
        (SMOKE_TASK, WITH, 1, PASSED),
        (SMOKE_TASK, WITHOUT, 1, FAILED),
        (SMOKE_TASK, WITH, 2, PASSED),
        (SMOKE_TASK, WITHOUT, 2, FAILED),
    ]
    assert report.cost == pytest.approx(0.06)
    counts = directive_counts(report.runs)
    assert sorted(counts) == ["conventional-commit-format", "mark-breaking-change"]
    for entry in counts.values():
        assert (entry[WITH].passes, entry[WITH].runs) == (2, 2)
        assert (entry[WITHOUT].passes, entry[WITHOUT].runs) == (0, 2)
    seen = calls(stub)
    assert [call["probe"] for call in seen] == [True, False] * 6
    assert len({call["folder"] for call in seen}) == SMOKE_RUNS
    login = {
        "folder": str(work.resolve()),
        "home": str(tmp_path / "home"),
        "user": getpass.getuser(),
        "stdin": "",
    }
    assert calls(stub, "logins.jsonl") == [login]
    text = (work / "report.md").read_text(encoding="utf-8")
    assert SMALL_SAMPLE in text
    assert "No directive is a candidate." in text
    data = json.loads((work / "report.json").read_text(encoding="utf-8"))
    assert data["candidates"] == []
    assert data["directives"]["mark-breaking-change"][WITH] == {"passes": 2, "runs": 2, "errors": 0}
    for run in report.runs:
        folder = work / run.folder
        assert identity_problems(folder, work / "gitconfig") == []
        assert not (folder / "knowledge").exists()
        assert (folder / "AGENTS.md").is_file()
        assert (folder.parent / f"{folder.name}.probe.jsonl").is_file()
        assert (folder.parent / f"{folder.name}.result.json").is_file()
        assert run.models == ["claude-stub"]
        assert (folder / "CHANGE.md").is_file() is (run.task == SMOKE_TASK)
        assert run.turns == STUB_TURNS


def test_a_directive_that_helps_nothing_is_a_candidate(tmp_path: Path, prebuilt: list[str]) -> None:
    del prebuilt
    stub = write_stub(tmp_path / "stub", {SMOKE_TASK: "same"})
    work = tmp_path / "work"
    report = run_eval(REPO, options(stub, work, runs=1))
    assert report.problems == []
    data = json.loads((work / "report.json").read_text(encoding="utf-8"))
    assert data["candidates"] == ["conventional-commit-format", "mark-breaking-change"]
    text = (work / "report.md").read_text(encoding="utf-8")
    assert (
        "With the discipline in force, 1 of 1 runs passed. Without it, 1 of 1 runs passed." in text
    )


def test_an_error_run_is_no_pass_and_no_fail(tmp_path: Path, prebuilt: list[str]) -> None:
    del prebuilt
    stub = write_stub(tmp_path / "stub", {SMOKE_TASK: "error"})
    report = run_eval(REPO, options(stub, tmp_path / "work", runs=1))
    assert report.problems == []
    assert [run.status for run in report.runs[2:]] == [ERROR, ERROR]
    assert report.runs[2].detail == "claude ended with 'error_max_budget_usd'"
    entry = directive_counts(report.runs)["mark-breaking-change"]
    assert (entry[WITH].runs, entry[WITH].errors) == (0, 1)
    assert not is_candidate(entry)
    assert report.cost == pytest.approx(0.04)


@pytest.mark.parametrize(
    ("mode", "detail", "cost"),
    [
        ("garbage", "claude gave no JSON result, exit 0", 0.1),
        ("sleep", "the run passed 1 seconds", 0.1),
        ("flagged", f"claude ended with 'success': '{'x' * 200}'", 0.01),
    ],
)
def test_a_broken_run_is_an_error(
    tmp_path: Path, prebuilt: list[str], mode: str, detail: str, cost: float
) -> None:
    del prebuilt
    stub = write_stub(tmp_path / "stub", {SMOKE_TASK: mode})
    report = run_eval(REPO, options(stub, tmp_path / "work", runs=1, timeout=1.0))
    run = report.runs[2]
    assert (run.status, run.detail, run.cost) == (ERROR, detail, cost)


def test_a_canary_that_passes_without_the_knowledge_stops_the_batch(
    tmp_path: Path, prebuilt: list[str]
) -> None:
    del prebuilt
    stub = write_stub(tmp_path / "stub", {"canary-commit-rules": "same"})
    report = run_eval(REPO, options(stub, tmp_path / "work"))
    assert problem_texts(report.problems) == [
        "eval-canary: The canary canary-commit-rules must end failed in without, not passed."
    ]
    assert len(report.runs) == CANARY_RUNS
    assert len(calls(stub)) == 2 * CANARY_RUNS


def test_a_leak_stops_the_batch_before_a_paid_run(tmp_path: Path, prebuilt: list[str]) -> None:
    del prebuilt
    stub = write_stub(tmp_path / "stub", {}, skills=["| mine | User | 9 |"])
    report = run_eval(REPO, options(stub, tmp_path / "work"))
    assert [problem.code for problem in report.problems] == ["skill"]
    assert [call["probe"] for call in calls(stub)] == [True]
    assert report.cost == 0
    assert report.runs[0].detail == "the isolation probe failed"


def test_an_auto_memory_folder_stops_the_batch(tmp_path: Path, prebuilt: list[str]) -> None:
    del prebuilt
    stub = write_stub(tmp_path / "stub", {})
    work = tmp_path / "work"
    run = work.resolve() / "runs" / "canary-commit-rules" / "with-1"
    memory_folder(run, tmp_path / "home").mkdir(parents=True)
    report = run_eval(REPO, options(stub, work))
    assert [problem.code for problem in report.problems] == ["auto-memory"]
    assert [call["probe"] for call in calls(stub)] == [True]


def test_the_budget_stops_new_runs(tmp_path: Path, prebuilt: list[str]) -> None:
    del prebuilt
    stub = write_stub(tmp_path / "stub", {}, cost=0.1)
    report = run_eval(REPO, options(stub, tmp_path / "work", budget=0.25, runs=1))
    assert [run.status for run in report.runs] == [PASSED, FAILED, "not-run", "not-run"]
    assert report.runs[2].detail == "the batch budget does not cover another run"
    assert report.cost == pytest.approx(0.2)
    assert len(calls(stub)) == 2 * CANARY_RUNS


def test_a_dry_run_makes_only_free_probes(tmp_path: Path, prebuilt: list[str]) -> None:
    del prebuilt
    stub = write_stub(tmp_path / "stub", {})
    report = run_eval(REPO, options(stub, tmp_path / "work", dry_run=True, budget=0.1))
    assert report.problems == []
    assert {run.status for run in report.runs} == {PROBED}
    assert len(report.runs) == SMOKE_RUNS
    assert {call["probe"] for call in calls(stub)} == {True}
    assert report.cost == 0


def test_a_missing_claude_fails_the_login_check(tmp_path: Path, prebuilt: list[str]) -> None:
    del prebuilt
    report = run_eval(REPO, options(tmp_path / "gone", tmp_path / "work"))
    assert [problem.code for problem in report.problems] == [LOGIN_CODE]
    assert report.problems[0].message.startswith("The login check did not finish: ")


@pytest.mark.parametrize("changes", [{}, {"dry_run": True}])
def test_a_logged_out_claude_stops_the_batch_before_a_probe(
    tmp_path: Path,
    prebuilt: list[str],
    changes: dict[str, object],
    capfd: pytest.CaptureFixture[str],
) -> None:
    stub = write_stub(tmp_path / "stub", {}, login=1)
    work = tmp_path / "work"
    report = run_eval(REPO, options(stub, work, **changes))
    assert problem_texts(report.problems) == [
        "login: claude is not logged in with the run environment. Run claude auth status."
    ]
    assert prebuilt == []
    assert calls(stub) == []
    assert len(calls(stub, "logins.jsonl")) == 1
    assert report.runs == []
    for path in work.rglob("*"):
        if path.is_file():
            assert PLANTED_EMAIL not in path.read_text(encoding="utf-8")
    out, err = capfd.readouterr()
    assert PLANTED_EMAIL not in out + err


def test_a_login_check_that_hangs_stops_the_batch(
    tmp_path: Path, prebuilt: list[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    del prebuilt
    monkeypatch.setattr(harness_module, "PROBE_TIMEOUT", 0.5)
    stub = write_stub(tmp_path / "stub", {})
    stub.write_text("#!/bin/sh\nsleep 5\n", encoding="utf-8")
    report = run_eval(REPO, options(stub, tmp_path / "work"))
    assert [problem.code for problem in report.problems] == [LOGIN_CODE]
    assert "timed out" in report.problems[0].message


@pytest.mark.parametrize(
    ("changes", "message"),
    [
        ({"tasks": ("gone",)}, "eval-run: software-engineering has no task gone."),
        (
            {"runs": 0},
            "eval-run: Set 1 or more runs, and a batch budget of at least one run budget.",
        ),
        ({"run_budget": 0}, "eval-run: Set 1 or more runs"),
        ({"budget": 0.05}, "eval-run: Set 1 or more runs"),
    ],
)
def test_bad_options_stop_the_eval(
    tmp_path: Path, prebuilt: list[str], changes: dict[str, object], message: str
) -> None:
    report = run_eval(REPO, options(tmp_path / "claude", tmp_path / "work", **changes))
    assert any(text.startswith(message) for text in problem_texts(report.problems))
    assert prebuilt == []
    assert not (tmp_path / "work").exists()


def test_a_used_work_folder_stops_the_eval(tmp_path: Path, prebuilt: list[str]) -> None:
    work = tmp_path / "work"
    write_files(work, {"old.md": "x"})
    report = run_eval(REPO, options(tmp_path / "claude", work))
    assert problem_texts(report.problems) == ["eval-run: The work folder must be new or empty."]
    (tmp_path / "file").write_text("x", encoding="utf-8")
    report = run_eval(REPO, options(tmp_path / "claude", tmp_path / "file"))
    assert problem_texts(report.problems) == ["eval-run: The work folder must be new or empty."]
    assert prebuilt == []


def test_a_work_folder_in_the_knowledge_fails(tmp_path: Path) -> None:
    project = tmp_path / "project"
    shutil.copytree(REPO / KNOWLEDGE_FOLDER, project / KNOWLEDGE_FOLDER)
    work = project / KNOWLEDGE_FOLDER / "work"
    report = run_eval(project, options(write_stub(tmp_path / "stub", {}), work))
    assert [problem.code for problem in report.problems] == ["eval-run"]
    assert "cannot change the project tree" in report.problems[0].message
    assert not (work / "conditions").exists()


def test_a_task_problem_stops_the_eval(small: Path) -> None:
    write_task(small, "second", bad={"out.md": "yes"})
    report = run_eval(small, EvalOptions("alpha", work=small / "work"))
    assert any("bad output passes" in text for text in problem_texts(report.problems))
    assert not (small / "work").exists()


def test_a_discipline_without_a_canary_stops_the_eval(small: Path) -> None:
    report = run_eval(small, EvalOptions("beta", work=small / "work"))
    assert problem_texts(report.problems) == [
        "eval-run: beta has no canary task in knowledge/evals/."
    ]


def record(task: str, condition: str, status: str, **changes: object) -> RunRecord:
    values: dict[str, object] = {"targets": {"a": status == PASSED}, **changes}
    run = RunRecord(
        task, canary=False, condition=condition, repeat=1, directives=["a"], status=status
    )
    for key, value in values.items():
        setattr(run, key, value)
    return run


def test_the_counts_skip_the_canary_and_count_errors_apart() -> None:
    runs = [
        record("t", WITH, PASSED),
        record("t", WITH, ERROR),
        record("t", WITHOUT, FAILED),
        record("t", WITHOUT, "not-run"),
        record("t", WITHOUT, PROBED),
        record("canary", WITH, PASSED, canary=True),
    ]
    counts = directive_counts(runs)
    assert counts["a"][WITH] == Counts(1, 1, 1)
    assert counts["a"][WITHOUT] == Counts(0, 1, 0)
    assert counts["a"][WITH].text() == "1 of 1 passed, 1 error"
    assert Counts(1, 2, 2).text() == "1 of 2 passed, 2 errors"
    assert Counts(1, 2).text() == "1 of 2 passed"


@pytest.mark.parametrize(
    ("found", "absent", "candidate"),
    [
        (Counts(2, 2), Counts(0, 2), False),
        (Counts(1, 2), Counts(1, 2), True),
        (Counts(0, 2), Counts(1, 2), True),
        (Counts(1, 1), Counts(1, 2), False),
        (Counts(1, 2), Counts(1, 1), True),
        (Counts(0, 0), Counts(0, 2), False),
        (Counts(0, 2), Counts(0, 0), False),
        (Counts(0, 2, 1), Counts(0, 2), False),
        (Counts(0, 2), Counts(0, 2, 1), False),
    ],
)
def test_a_candidate_has_no_more_passes_with_the_knowledge(
    found: Counts, absent: Counts, *, candidate: bool
) -> None:
    assert is_candidate({WITH: found, WITHOUT: absent}) is candidate


def test_the_signal_line_has_the_fixed_form() -> None:
    counts = {WITH: Counts(1, 3), WITHOUT: Counts(2, 3)}
    assert signal_line("say-yes", counts, "2026-11-06") == (
        "- `say-yes`: 2026-11-06, eval. With the discipline in force, 1 of 3 runs passed. "
        "Without it, 2 of 3 runs passed."
    )


def test_the_report_states_each_part() -> None:
    from engine.parser.result import Problem  # noqa: PLC0415

    report = EvalReport(
        "alpha",
        "sonnet",
        runs=[
            record("t", WITH, PASSED, cost=0.25, models=["m"], turns=3, detail="a | b"),
            record("t", WITHOUT, PASSED, cost=0.5),
        ],
        problems=[Problem(Path("x"), 1, "eval-run", "A problem.")],
    )
    text = report_markdown(report, "2026-11-06")
    assert text.startswith("# Eval of alpha\n")
    assert "- Model: `sonnet`. Models in the results: m." in text
    assert "- Runs: 2, with 0 errors. Not run: 0." in text
    assert "- Cost: 0.7500 USD" in text
    assert "| `a` | t | 1 of 1 passed | 1 of 1 passed |" in text
    assert "- `a`: 2026-11-06, eval." in text
    assert "| t | with | 1 | passed | 0.2500 | 3 | a / b |" in text
    assert "## Problems\n\n- x:1: eval-run: A problem." in text
    data = report_data(report)
    assert data["cost_usd"] == pytest.approx(0.75)
    assert data["note"] == SMALL_SAMPLE
    assert data["candidates"] == ["a"]
    assert "## Problems" not in report_markdown(EvalReport("alpha", "sonnet"), "2026-11-06")


def test_the_command_needs_one_mode(small: Path) -> None:
    assert RUNNER.invoke(app, ["eval", str(small)]).exit_code == USAGE_ERROR
    both = RUNNER.invoke(app, ["eval", str(small), "--check", "--discipline", "alpha"])
    assert both.exit_code == USAGE_ERROR


def test_the_command_checks_the_tasks(small: Path) -> None:
    result = RUNNER.invoke(app, ["eval", str(small), "--check"])
    assert (result.exit_code, result.output) == (0, "2 eval tasks checked, 0 problems\n")
    write_task(small, "second", bad={"out.md": "yes"})
    result = RUNNER.invoke(app, ["eval", str(small), "--check"])
    assert result.exit_code == 1
    assert "The bad output passes the target say-yes." in result.output


def test_the_command_reports_a_stopped_eval(small: Path) -> None:
    result = RUNNER.invoke(app, ["eval", str(small), "--discipline", "beta"])
    assert result.exit_code == 1
    assert result.output.endswith("0 runs, 0.0000 USD, 1 problems\n")
    assert "The report is in" not in result.output


def test_the_command_writes_the_report(
    tmp_path: Path, prebuilt: list[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    del prebuilt
    stub = write_stub(tmp_path / "stub", {})
    monkeypatch.setattr(Path, "home", lambda: tmp_path / "home")
    work = tmp_path / "work"
    arguments = ["eval", str(REPO), "--discipline", DISCIPLINE, "--task", SMOKE_TASK]
    arguments += [
        "--claude",
        str(stub),
        "--work",
        str(work),
        "--budget",
        "1",
        "--run-budget",
        "0.1",
    ]
    result = RUNNER.invoke(app, arguments)
    assert result.exit_code == 0, result.output
    assert f"The report is in {work.resolve()}." in result.output
    assert result.output.endswith("4 runs, 0.0400 USD, 0 problems\n")


def live_run_folder(tmp_path: Path) -> tuple[Path, Path]:
    folder = tmp_path / "run"
    for name in ("AGENTS.md", ".claude/references", ".claude/rules/knowledge", ".claude/skills"):
        source = REPO / name
        target = folder / name
        target.parent.mkdir(parents=True, exist_ok=True)
        if source.is_dir():
            shutil.copytree(source, target)
        else:
            shutil.copy2(source, target)
    write_files(
        tmp_path, {"CLAUDE.md": "Planted instruction.\n", ".claude/rules/planted.md": "x\n"}
    )
    git_config = tmp_path / "gitconfig"
    git_config.write_text("", encoding="utf-8")
    assert commit_folder(folder, git_config, "live probe") == []
    return folder, git_config


def live_probe(folder: Path, git_config: Path, arguments: list[str]) -> Probe | None:
    done = subprocess.run(  # noqa: S603
        arguments,
        input="/context all",
        capture_output=True,
        text=True,
        cwd=folder,
        env=run_environment(Path.home(), git_config),
        timeout=120,
        check=False,
    )
    (folder.parent / "probe.jsonl").write_text(done.stdout, encoding="utf-8")
    return read_probe(done.stdout)


@pytest.mark.skipif(not LIVE, reason="DENSHO_EVAL_LIVE=1 runs the free probe of the real claude")
def test_the_live_probe_loads_only_the_run_folder(tmp_path: Path) -> None:
    folder, git_config = live_run_folder(tmp_path)
    flags = RunFlags(shutil.which("claude") or "claude", "sonnet", 0.01, ("Read",))
    probe = live_probe(folder, git_config, run_arguments(flags, folder, Path.home(), probe=True))
    assert probe_problems(folder, probe, ("Read",)) == []
    assert memory_problems(folder, Path.home()) == []
    assert identity_problems(folder, git_config) == []


@pytest.mark.skipif(not LIVE, reason="DENSHO_EVAL_LIVE=1 runs the free probe of the real claude")
def test_the_live_probe_without_the_isolation_flags_finds_the_leaks(tmp_path: Path) -> None:
    folder, git_config = live_run_folder(tmp_path)
    flags = RunFlags(shutil.which("claude") or "claude", "sonnet", 0.01, ("Read",))
    arguments = run_arguments(flags, folder, Path.home(), probe=True)
    settings = arguments.index("--settings")
    del arguments[settings : settings + 2]
    sources = arguments.index("--setting-sources")
    del arguments[sources : sources + 2]
    arguments.remove("--strict-mcp-config")
    probe = live_probe(folder, git_config, arguments)
    codes = {problem.code for problem in probe_problems(folder, probe, ("Read",))}
    (tmp_path / "codes.txt").write_text("\n".join(sorted(codes)) + "\n", encoding="utf-8")
    assert "memory-file" in codes
    assert memory_problems(folder, Path.home()) == []


def live_login(folder: Path, environment: Mapping[str, str]) -> int:
    done = subprocess.run(  # noqa: S603
        [shutil.which("claude") or "claude", *LOGIN_ARGUMENTS],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        cwd=folder,
        env=environment,
        timeout=60,
        check=False,
    )
    return done.returncode


@pytest.mark.skipif(
    not LIVE, reason="DENSHO_EVAL_LIVE=1 runs the free login check of the real claude"
)
def test_the_live_login_check_needs_the_account_name(tmp_path: Path) -> None:
    git_config = tmp_path / "gitconfig"
    git_config.write_text("", encoding="utf-8")
    environment = run_environment(Path.home(), git_config)
    assert live_login(tmp_path, environment) == 0
    del environment["USER"]
    assert live_login(tmp_path, environment) != 0


def test_an_auto_memory_folder_after_a_run_stops_the_batch(
    tmp_path: Path, prebuilt: list[str]
) -> None:
    del prebuilt
    stub = write_stub(tmp_path / "stub", {SMOKE_TASK: "memory"})
    report = run_eval(REPO, options(stub, tmp_path / "work"))
    assert [problem.code for problem in report.problems] == ["auto-memory"]
    assert len(report.runs) == CANARY_RUNS + 1


def test_the_grader_reads_no_runtime_file(tmp_path: Path) -> None:
    write_files(
        tmp_path,
        {"AGENTS.md": "x", ".claude/skills/a/SKILL.md": "x", ".git/HEAD": "x", "out.md": "x"},
    )
    files, problems = harness_module.run_files(tmp_path)
    assert (sorted(map(str, files)), problems) == (["out.md"], [])


def test_the_canary_runs_first(small: Path) -> None:
    write_task(small, "a-task")
    tasks, _ = load_tasks(small, "alpha")
    chosen, missing = harness_module.selected_tasks(tasks, ["write-yes", "gone"])
    assert ([task.id for task in chosen], missing) == (["canary", "write-yes"], ["gone"])
    chosen, _ = harness_module.selected_tasks(list(reversed(tasks)), [])
    assert [task.id for task in chosen] == ["canary", "a-task", "write-yes"]


def test_the_throwaway_git_reads_only_its_own_global_file(tmp_path: Path) -> None:
    folder = tmp_path / "repo"
    write_files(folder, {"a.md": "a"})
    git_config = tmp_path / "gitconfig"
    git_config.write_text("[alias]\n\tplanted = status\n", encoding="utf-8")
    assert commit_folder(folder, git_config, "first") == []
    assert run_git(folder, git_config, "config", "--get", "alias.planted").stdout == "status\n"


def test_the_without_condition_takes_an_accepted_directive_out_of_force(tmp_path: Path) -> None:
    project = tmp_path / "project"
    shutil.copytree(
        REPO / KNOWLEDGE_FOLDER,
        project / KNOWLEDGE_FOLDER,
        ignore=shutil.ignore_patterns("evals"),
    )
    items, problems = parse_tree(node_folders(project))
    assert problems == []
    entity = governed_entities(items)[(DIRECTIVE, "mark-breaking-change")]
    data, missed = set_status_lines(entity.path.read_bytes(), [entity], Status.accepted)
    assert missed == []
    entity.path.write_bytes(data)
    old = governed_entities(items)[(DIRECTIVE, "feat-type")]
    assert old.path == entity.path
    data, missed = set_status_lines(data, [old], Status.deprecated)
    assert missed == []
    entity.path.write_bytes(data)
    work = tmp_path / "work"
    work.mkdir()
    git_config = work / "gitconfig"
    git_config.write_text("", encoding="utf-8")
    absent = build_condition(project, work, DISCIPLINE, WITHOUT, git_config)
    assert isinstance(absent, Condition), absent
    assert absent.directives["mark-breaking-change"] == Status.proposed
    assert absent.directives["feat-type"] == Status.deprecated
    assert "mark-breaking-change" not in in_force_ids(absent.files)
    assert entity.path.read_bytes() == data


def test_a_leak_in_the_built_conditions_stops_the_batch(
    tmp_path: Path, conditions: BuiltConditions, monkeypatch: pytest.MonkeyPatch
) -> None:
    def leaking(
        repository: Path, work: Path, discipline: str, name: str, git_config: Path
    ) -> object:
        del repository, work, discipline, name, git_config
        return conditions[DISCIPLINE][WITH]

    monkeypatch.setattr(harness_module, "build_condition", leaking)
    stub = write_stub(tmp_path / "stub", {})
    report = run_eval(REPO, options(stub, tmp_path / "work"))
    assert report.problems
    assert {problem.code for problem in report.problems} == {"eval-canary"}
    assert report.runs == []
    assert calls(stub) == []
