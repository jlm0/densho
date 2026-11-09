import os
import shutil
import subprocess
import threading
from pathlib import Path

import pytest

from engine.parser.node import parse_tree
from engine.parser.result import Branch, Page, Problem, StepCopies, StepFile
from engine.parser.steps import read_step_source, step_files_digest
from engine.tree_copies import TREE_SECTIONS

GOVERNED = "status: proposed\norigin: template\nknowledge_type: domain\n"
FLOW = (
    f"---\nid: flow\nkind: densho:Skill\ntitle: Flow\n{GOVERNED}"
    "description: Run the flow. Use when you run it.\ninvocation: agent\nskill_type: task\n"
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


def split_step(text: str, path: Path) -> tuple[tuple[str, str], ...] | list[Problem]:
    found = read_step_source(text, path)
    return found if isinstance(found, list) else found.sections


def problems_of(text: str) -> list[tuple[int, str, str]]:
    found = split_step(text, SOURCE)
    assert isinstance(found, list), found
    return [(problem.line, problem.code, problem.message) for problem in found]


def test_a_step_file_holds_its_four_sections() -> None:
    assert split_step(STEP, SOURCE) == (
        ("Inputs", "- A request"),
        ("Procedure", "1. Do it."),
        ("Output", "A result."),
        ("Exit gate", "It holds."),
    )


def test_a_section_keeps_its_inner_lines() -> None:
    text = STEP.replace("1. Do it.\n", "1. Do it.\n\n   More.\n\n### Detail\n\nText.\n")
    found = split_step(text, SOURCE)
    assert isinstance(found, tuple)
    assert dict(found)["Procedure"] == "1. Do it.\n\n   More.\n\n### Detail\n\nText."


ORDER = "Give the step file exactly these sections in this order: " + ", ".join(
    f"## {name}" for name in TREE_SECTIONS
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
    assert isinstance(split_step("\n\n" + STEP, SOURCE), tuple)


@pytest.mark.parametrize(
    ("name", "line"), [("Inputs", 1), ("Procedure", 5), ("Output", 9), ("Exit gate", 13)]
)
def test_an_empty_section_fails_at_its_heading(name: str, line: int) -> None:
    found = split_step(STEP, SOURCE)
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
        "The step file holds no ## Definition and no ## Directives. Put them in a node.",
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
    found = split_step(text, SOURCE)
    assert isinstance(found, tuple)
    assert dict(found)["Procedure"] == "1. Do it.\n\n> ## Exit gate"


def test_the_last_section_keeps_its_last_line_with_no_line_end() -> None:
    found = split_step(STEP.rstrip("\n"), SOURCE)
    assert isinstance(found, tuple)
    assert dict(found)["Exit gate"] == "It holds."


def test_a_heading_in_a_code_fence_is_no_section() -> None:
    text = STEP.replace("1. Do it.\n", "```text\n## Output\n```\n")
    found = split_step(text, SOURCE)
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


COPY = (
    "---\n"
    "title: Do the first step\n"
    "pages:\n"
    "  - target: area\n"
    "    trigger: You need the area.\n"
    "directives:\n"
    "  - do-it\n"
    "branches:\n"
    "  - condition: If the target is Android\n"
    "    directives:\n"
    "      - android-it\n"
    "missing_rules:\n"
    "  - No directive covers an empty result.\n"
    "---\n"
    "\n"
    "## Procedure\n"
    "\n"
    "1. Do it.\n"
    "\n"
    "## Output\n"
    "\n"
    "A result.\n"
)
COPIES = StepCopies(
    "Do the first step",
    (Page("area", "You need the area."),),
    ("do-it",),
    (Branch("If the target is Android", ("android-it",)),),
    ("No directive covers an empty result.",),
)


def read_copy(text: str) -> StepFile:
    found = read_step_source(text, SOURCE)
    assert isinstance(found, StepFile), found
    return found


def test_a_step_file_in_the_copy_form_holds_its_copies() -> None:
    step = read_copy(COPY)
    assert step.copies == COPIES
    assert step.sections == (("Procedure", "1. Do it."), ("Output", "A result."))
    assert step.path == SOURCE
    lines = COPY.split("\n")
    assert step.line_of(("directives", 0)) == lines.index("  - do-it") + 1
    assert step.line_of(("branches", 0, "directives", 0)) == lines.index("      - android-it") + 1


def test_the_copies_list_each_directive_with_its_place() -> None:
    assert COPIES.copied() == (
        ("do-it", ("directives", 0)),
        ("android-it", ("branches", 0, "directives", 0)),
    )


def test_a_copy_form_needs_only_a_title() -> None:
    text = "---\ntitle: One\n---\n\n## Procedure\n\n1. Do it.\n\n## Output\n\nIt.\n"
    assert read_copy(text).copies == StepCopies("One")


@pytest.mark.parametrize(
    ("old", "new", "line", "message"),
    [
        (
            "missing_rules:\n",
            "notes: x\nmissing_rules:\n",
            12,
            (
                "A step file has no key notes. Use only: title, pages, directives, branches, "
                "missing_rules."
            ),
        ),
        ("title: Do the first step\n", "", 1, "Give the step a title."),
        ("title: Do the first step\n", "title: [a]\n", 2, "Write the title as text on 1 line."),
        ("title: Do the first step\n", "title: '  a'\n", 2, "Write the title as text on 1 line."),
        ("title: Do the first step\n", "title: 'a  '\n", 2, "Write the title as text on 1 line."),
        ("  - do-it\n", "  - Do-It\n", 7, "Write each ID in lowercase words joined by hyphens."),
        ("  - do-it\n", "  - 7\n", 7, "Write each ID in lowercase words joined by hyphens."),
        ("directives:\n  - do-it\n", "directives: do-it\n", 6, "Write directives as a list."),
        (
            "pages:\n  - target: area\n    trigger: You need the area.\n",
            "pages: x\n",
            3,
            "Write pages as a list.",
        ),
        (
            "    trigger: You need the area.\n",
            "",
            4,
            "Give each entry of pages exactly the keys target and trigger.",
        ),
        (
            "    trigger: You need the area.\n",
            "    trigger: You need the area.\n    extra: x\n",
            4,
            "Give each entry of pages exactly the keys target and trigger.",
        ),
        (
            "  - target: area\n",
            "  - target: Area\n",
            4,
            "Write each ID in lowercase words joined by hyphens.",
        ),
        (
            "    trigger: You need the area.\n",
            '    trigger: "You\\nneed it."\n',
            5,
            "Write the trigger as text on 1 line.",
        ),
        (
            "  - condition: If the target is Android\n",
            "  - condition: When the target is Android\n",
            9,
            "Start the condition with If, and end it with no period.",
        ),
        (
            "  - condition: If the target is Android\n",
            "  - condition: If the target is Android.\n",
            9,
            "Start the condition with If, and end it with no period.",
        ),
        (
            "  - condition: If the target is Android\n",
            "  - condition: ''\n",
            9,
            "Write the condition as text on 1 line.",
        ),
        (
            "    directives:\n      - android-it\n",
            "    directives: []\n",
            10,
            "Name at least 1 directive in the branch.",
        ),
        (
            "  - condition: If the target is Android\n    directives:\n      - android-it\n",
            "  - If the target is Android\n",
            9,
            "Give each entry of branches exactly the keys condition and directives.",
        ),
        (
            (
                "branches:\n  - condition: If the target is Android\n    directives:\n"
                "      - android-it\n"
            ),
            "branches: x\n",
            8,
            "Write branches as a list.",
        ),
        (
            "  - No directive covers an empty result.\n",
            "  - [a]\n",
            13,
            "Write each missing rule as text on 1 line.",
        ),
        (
            "      - android-it\n",
            "      - do-it\n",
            11,
            "The step names do-it twice. Name it once.",
        ),
        ("  - do-it\n", "  - do-it\n  - do-it\n", 8, "The step names do-it twice. Name it once."),
    ],
)
def test_a_bad_copy_entry_fails_at_its_line(old: str, new: str, line: int, message: str) -> None:
    assert COPY.count(old) == 1
    assert problems_of(COPY.replace(old, new)) == [(line, "step-file", message)]


def test_a_branch_with_a_bad_condition_and_no_directive_reports_both() -> None:
    text = COPY.replace("If the target is Android\n", "On Android\n").replace(
        "    directives:\n      - android-it\n", "    directives: []\n"
    )
    assert [line for line, _, _ in problems_of(text)] == [9, 10]


COPY_ORDER = "Give the step file exactly these sections in this order: ## Procedure, ## Output."


@pytest.mark.parametrize(
    ("old", "new", "line", "message"),
    [
        ("## Procedure\n", "## Inputs\n", 16, COPY_ORDER),
        ("## Output\n\nA result.\n", "", 16, COPY_ORDER),
        ("1. Do it.\n", "", 16, "Write the text of ## Procedure."),
        ("A result.\n", "", 20, "Write the text of ## Output."),
    ],
)
def test_a_bad_copy_body_fails_at_its_line(old: str, new: str, line: int, message: str) -> None:
    assert problems_of(COPY.replace(old, new)) == [(line, "step-file", message)]


def test_text_before_the_first_copy_section_fails_at_the_body_line() -> None:
    message = "Put each line of the step file in a section: ## Procedure, ## Output."
    assert problems_of(COPY.replace("---\n\n## Procedure", "---\nIntro.\n\n## Procedure")) == [
        (15, "step-file", message)
    ]


def test_problems_of_the_copies_and_the_body_come_together() -> None:
    text = COPY.replace("title: Do the first step\n", "").replace("1. Do it.\n", "")
    assert [line for line, _, _ in problems_of(text)] == [1, 15]


def test_a_bad_front_matter_fails() -> None:
    found = problems_of(COPY.replace("title: Do the first step\n", "title: [\n"))
    assert found
    assert {code for _, code, _ in found} == {"yaml"}


def test_a_control_character_in_the_front_matter_fails() -> None:
    assert problems_of(COPY.replace("Do the first", "Do the\x07first")) == [
        (2, "control-character", "Remove the control character from this line.")
    ]


def test_the_digest_follows_the_copies() -> None:
    tree = StepFile("a", (("Procedure", "x"),))
    copied = StepFile("a", (("Procedure", "x"),), COPIES)
    assert step_files_digest([tree]) != step_files_digest([copied])
    changed = StepFile("a", (("Procedure", "x"),), StepCopies("Other"))
    assert step_files_digest([copied]) != step_files_digest([changed])


def test_parse_tree_reads_a_copy_form_step(tmp_path: Path) -> None:
    write_flow(tmp_path, {"first.md": COPY})
    nodes, problems = parse_tree([tmp_path])
    assert problems == []
    assert nodes[0].step_files[0].copies == COPIES
