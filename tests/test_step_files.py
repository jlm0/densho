import os
import shutil
import subprocess
import threading
from pathlib import Path

import pytest

from engine.parser.node import parse_tree
from engine.parser.result import StepFile
from engine.parser.steps import STEP_SECTIONS, step_file_problems, step_files_digest

GOVERNED = "status: proposed\norigin: template\nknowledge_type: domain\n"
FLOW = (
    f"---\nid: flow\nkind: densho:Skill\ntitle: Flow\n{GOVERNED}"
    "description: Run the flow. Use when you run it.\ninvocation: agent\nskill_type: flow\n"
    "uses: [area]\nsteps: [first]\n---\n"
)
STEP = (
    "## Inputs\n\n- A request\n\n## Procedure\n\n1. Do it.\n\n"
    "## Output\n\nA result.\n\n## Exit gate\n\nIt holds.\n"
)
SOURCE = Path("knowledge/skills/flow/steps/first.md")


def git_environment() -> dict[str, str]:
    return {"PATH": os.environ.get("PATH", ""), "HOME": os.environ.get("HOME", "")}


def write_flow(root: Path, steps: dict[str, str | bytes]) -> Path:
    folder = root / "skills" / "flow"
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "node.md").write_text(FLOW, encoding="utf-8")
    for name, data in steps.items():
        path = folder / "steps" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(data, bytes):
            path.write_bytes(data)
        else:
            path.write_text(data, encoding="utf-8")
    return folder


def problems_of(text: str) -> list[tuple[int, str, str]]:
    found = step_file_problems(text, SOURCE)
    assert isinstance(found, list), found
    return [(problem.line, problem.code, problem.message) for problem in found]


def test_a_step_file_holds_its_four_sections() -> None:
    assert step_file_problems(STEP, SOURCE) == (
        ("Inputs", "- A request"),
        ("Procedure", "1. Do it."),
        ("Output", "A result."),
        ("Exit gate", "It holds."),
    )


def test_a_section_keeps_its_inner_lines() -> None:
    text = STEP.replace("1. Do it.\n", "1. Do it.\n\n   More.\n\n### Detail\n\nText.\n")
    found = step_file_problems(text, SOURCE)
    assert isinstance(found, tuple)
    assert dict(found)["Procedure"] == "1. Do it.\n\n   More.\n\n### Detail\n\nText."


ORDER = "Give the step file exactly these sections in this order: " + ", ".join(
    f"## {name}" for name in STEP_SECTIONS
)


@pytest.mark.parametrize(
    ("text", "line"),
    [
        (STEP.replace("## Output\n\nA result.\n\n", ""), 1),
        (STEP.replace("## Inputs", "## Input"), 1),
        ("## Procedure\n\n1. Do it.\n\n" + STEP.replace("## Procedure\n\n1. Do it.\n\n", ""), 1),
        (STEP + "\n## Notes\n\nMore.\n", 1),
        ("# Title\n\n" + STEP, 1),
        ("Text only.\n", 1),
        ("Intro.\n\n" + STEP.replace("## Inputs", "## Input"), 3),
    ],
)
def test_a_step_file_needs_the_four_sections_in_order(text: str, line: int) -> None:
    assert problems_of(text) == [(line, "step-file", f"{ORDER}.")]


def test_text_before_the_first_section_fails() -> None:
    message = "Put each line of the step file in a section: " + ORDER.split(": ", 1)[1] + "."
    assert problems_of("Intro.\n\n" + STEP) == [(1, "step-file", message)]


def test_blank_lines_before_the_first_section_pass() -> None:
    assert isinstance(step_file_problems("\n\n" + STEP, SOURCE), tuple)


@pytest.mark.parametrize(
    ("name", "line"), [("Inputs", 1), ("Procedure", 5), ("Output", 9), ("Exit gate", 13)]
)
def test_an_empty_section_fails_at_its_heading(name: str, line: int) -> None:
    found = step_file_problems(STEP, SOURCE)
    assert isinstance(found, tuple)
    text = STEP.replace(f"## {name}\n\n{dict(found)[name]}\n", f"## {name}\n\n   \n")
    assert problems_of(text) == [(line, "step-file", f"Write the text of ## {name}.")]


def test_each_empty_section_fails() -> None:
    text = "## Inputs\n\n## Procedure\n\n## Output\n\n## Exit gate\n"
    assert [line for line, _, _ in problems_of(text)] == [1, 3, 5, 7]


def test_a_definition_or_directives_heading_fails() -> None:
    text = STEP + "\n## Directives\n\n- Do it. ^do-it\n"
    found = problems_of(text)
    assert (1, "step-file", f"{ORDER}.") in found
    assert (
        1,
        "step-file",
        "A step file holds no ## Definition and no ## Directives. Put them in a node.",
    ) in found


def test_a_control_character_fails_at_its_line() -> None:
    assert problems_of(STEP.replace("A result.", "A re\x07sult.")) == [
        (11, "control-character", "Remove the control character from this line.")
    ]


def test_a_markdown_problem_of_the_body_fails() -> None:
    found = problems_of(STEP.replace("1. Do it.\n", "```\n1. Do it.\n"))
    assert found
    assert {code for _, code, _ in found} <= {"markdown", "step-file"}


def test_a_markdown_problem_inside_a_section_fails_alone() -> None:
    text = STEP.replace("1. Do it.\n", "1. Do it.\n\n<div>Hidden.</div>\n")
    assert [(line, code) for line, code, _ in problems_of(text)] == [(9, "markdown")]


def test_a_heading_in_a_quote_is_no_section() -> None:
    text = STEP.replace("1. Do it.\n", "1. Do it.\n\n> ## Exit gate\n")
    found = step_file_problems(text, SOURCE)
    assert isinstance(found, tuple)
    assert dict(found)["Procedure"] == "1. Do it.\n\n> ## Exit gate"


def test_the_last_section_keeps_its_last_line_with_no_line_end() -> None:
    found = step_file_problems(STEP.rstrip("\n"), SOURCE)
    assert isinstance(found, tuple)
    assert dict(found)["Exit gate"] == "It holds."


def test_a_heading_in_a_code_fence_is_no_section() -> None:
    text = STEP.replace("1. Do it.\n", "```text\n## Output\n```\n")
    found = step_file_problems(text, SOURCE)
    assert isinstance(found, tuple)
    assert dict(found)["Procedure"] == "```text\n## Output\n```"


def test_parse_tree_reads_the_step_files_of_a_skill(tmp_path: Path) -> None:
    write_flow(tmp_path, {"first.md": STEP, "second.md": STEP.replace("A result.", "B.")})
    nodes, problems = parse_tree([tmp_path])
    assert problems == []
    assert [step.id for step in nodes[0].step_files] == ["first", "second"]
    assert nodes[0].step_files[1].section("Output") == "B."


def test_a_skill_with_no_steps_folder_has_no_step_files(tmp_path: Path) -> None:
    write_flow(tmp_path, {})
    nodes, problems = parse_tree([tmp_path])
    assert problems == []
    assert [item.step_files for item in nodes] == [()]


@pytest.mark.parametrize("end", ["\r\n", "\r"])
def test_a_step_file_reads_other_line_ends(tmp_path: Path, end: str) -> None:
    write_flow(tmp_path, {"first.md": STEP.replace("\n", end).encode()})
    nodes, problems = parse_tree([tmp_path])
    assert problems == []
    assert nodes[0].step_files[0].section("Output") == "A result."


@pytest.mark.parametrize(
    ("name", "message"),
    [
        ("deep/first.md", "Put each step file directly in steps/."),
        (
            "First.md",
            "Name each step file with the ID of its step and .md, such as unit-testing.md.",
        ),
        (
            "first.txt",
            "Name each step file with the ID of its step and .md, such as unit-testing.md.",
        ),
        (
            "first-.md",
            "Name each step file with the ID of its step and .md, such as unit-testing.md.",
        ),
    ],
)
def test_a_misplaced_or_misnamed_step_file_fails(tmp_path: Path, name: str, message: str) -> None:
    folder = write_flow(tmp_path, {name: STEP})
    nodes, problems = parse_tree([tmp_path])
    assert [(problem.path, problem.code, problem.message) for problem in problems] == [
        (folder / "steps" / name, "step-file", message)
    ]
    assert nodes[0].step_files == ()


def test_a_bad_step_file_reports_its_problems_and_is_left_out(tmp_path: Path) -> None:
    folder = write_flow(tmp_path, {"first.md": "Text only.\n", "second.md": STEP})
    nodes, problems = parse_tree([tmp_path])
    assert [(problem.path, problem.code) for problem in problems] == [
        (folder / "steps" / "first.md", "step-file")
    ]
    assert [step.id for step in nodes[0].step_files] == ["second"]


def test_a_step_file_that_is_not_utf8_fails(tmp_path: Path) -> None:
    folder = write_flow(tmp_path, {"first.md": b"## Inputs\n\n\xff\n"})
    _, problems = parse_tree([tmp_path])
    assert [(problem.path, problem.code) for problem in problems] == [
        (folder / "steps" / "first.md", "encoding")
    ]


def test_a_link_inside_steps_fails(tmp_path: Path) -> None:
    folder = write_flow(tmp_path, {"first.md": STEP})
    link = folder / "steps" / "second.md"
    link.symlink_to(folder / "steps" / "first.md")
    nodes, problems = parse_tree([tmp_path])
    assert [(problem.path, problem.code) for problem in problems] == [(link, "symlink")]
    assert [step.id for step in nodes[0].step_files] == ["first"]


def test_a_step_file_that_is_not_a_regular_file_fails(tmp_path: Path) -> None:
    folder = write_flow(tmp_path, {})
    pipe = folder / "steps" / "pipe.md"
    pipe.parent.mkdir(parents=True)
    os.mkfifo(pipe)
    writer = threading.Thread(target=lambda: os.close(os.open(pipe, os.O_WRONLY)), daemon=True)
    writer.start()
    try:
        nodes, problems = parse_tree([tmp_path])
    finally:
        reader = os.open(pipe, os.O_RDONLY | os.O_NONBLOCK)
        writer.join(timeout=10)
        os.close(reader)
    assert [(problem.path, problem.code, problem.message) for problem in problems] == [
        (pipe, "read", "A step file must be a regular file.")
    ]
    assert nodes[0].step_files == ()


@pytest.mark.parametrize("holder", [Path("nodes/a"), Path("skills")])
def test_a_steps_folder_outside_a_skill_is_not_exempt(tmp_path: Path, holder: Path) -> None:
    write_flow(tmp_path, {})
    path = tmp_path / holder / "steps" / "first.md"
    path.parent.mkdir(parents=True)
    path.write_text(STEP, encoding="utf-8")
    nodes, problems = parse_tree([tmp_path])
    assert [(problem.path, problem.code) for problem in problems] == [(path, "file-name")]
    assert [item.step_files for item in nodes] == [()]


def test_a_git_ignored_step_file_is_left_out(tmp_path: Path) -> None:
    subprocess.run(  # noqa: S603
        [shutil.which("git") or "git", "init", "-q", "--template="],
        cwd=tmp_path,
        check=True,
        env=git_environment(),
    )
    (tmp_path / ".gitignore").write_text("draft.md\n", encoding="utf-8")
    write_flow(tmp_path / "knowledge", {"first.md": STEP, "draft.md": "Not a step.\n"})
    nodes, problems = parse_tree([tmp_path / "knowledge"])
    assert problems == []
    assert [step.id for step in nodes[0].step_files] == ["first"]


def test_the_digest_follows_the_content_and_not_the_order() -> None:
    first = StepFile("a", (("Inputs", "x"),))
    second = StepFile("b", (("Inputs", "y"),))
    assert step_files_digest([first, second]) == step_files_digest([second, first])
    changed = StepFile("b", (("Inputs", "z"),))
    assert step_files_digest([first, second]) != step_files_digest([first, changed])
    renamed = StepFile("c", (("Inputs", "y"),))
    assert step_files_digest([first, second]) != step_files_digest([first, renamed])
