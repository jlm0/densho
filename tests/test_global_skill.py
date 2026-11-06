# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false
import re
import shutil
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from ruamel.yaml import YAML
from typer.core import TyperGroup
from typer.main import get_command

from engine.cli import app
from engine.language import check_items
from engine.language.form import HARD_LEVEL
from engine.language.profile import LanguageProfile, read_profile
from engine.parser import ParsedNode, parse_source
from engine.runtime.claude_code import SKILL_KEPT_CHARACTERS
from engine.vendor.ste_lint import lint

if TYPE_CHECKING:
    from collections.abc import Iterator

REPO = Path(__file__).resolve().parents[1]
SKILL_NAME = "migrate-and-reconcile-knowledge"
SKILL = REPO / "global-skills" / SKILL_NAME / "SKILL.md"
PAGE = REPO / "docs/migration-and-reconciliation.md"
ENGINE = REPO / "engine"
RULE_SECTIONS = ("Directives", "Migration", "Reconciliation")
RULE_LINE = re.compile(r"^(?:- |\d+\. )(?P<text>.+)$")
SECTION = re.compile(r"^## (?P<name>.+)$")
FENCE = "```"
MIN_RULES = 90
SKILL_NAME_FORM = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
MAX_NAME_CHARACTERS = 64
COMMAND = re.compile(r"knowledge/\.ka/ka (?P<name>[a-z]+)(?P<option> --[a-z]+)?")
HEADING_NAME = re.compile(r"`(?P<heading>### [^`]+)`")
SKELETON = re.compile(r"```markdown\n(?P<source>.+?)\n```", re.DOTALL)
PROBLEM_CODES = re.compile(r"### Problem codes\n(?P<table>.+?)\n### ", re.DOTALL)
TABLE_CODE = re.compile(r"^\| `(?P<code>[a-z-]+)` +\|", re.MULTILINE)
SEARCH = re.compile(r"^(?P<command>git grep .+)$", re.MULTILINE)
REFERENCES = "\n## References\n"
SYNTHETIC_NODE_CODES = {"vocabulary-branch"}
INSTALL_COMMAND = f"cp -R global-skills/{SKILL_NAME} ~/.claude/skills/"
REQUIRED_RULES = {
    "secret": (
        "Do not copy secret material from a project into a node, the ledger, a command, or a reply."
    ),
    "promotion": "Do not change a `status` to `accepted`.",
    "proposal": "Set the `status` of each entity that you add to `proposed`.",
    "prose": "Do not convert a procedure or a reference into a directive.",
    "visible": "Keep each item that you do not convert in `knowledge-migration/ledger.md`.",
    "optional": "Do not pull a template change until a person asks for the pull.",
}
PLANTED_SECRETS = {
    "aws.txt": "key AKIAIOSFODNN7EXAMPLE\n",
    "github.txt": "ghp_abcdefghijklmnopqrstuvwxyz\n",
    "anthropic.txt": "sk-abcdefghijklmnopqrstuvwxyz\n",
    "slack.txt": "xoxb-1234\n",
    "private.txt": "-----BEGIN RSA PRIVATE KEY-----\n",
    "password.txt": "password: example-not-a-real-value\n",
    "token.txt": "API_KEY=example-not-a-real-value\n",
    "email.txt": "contact jane.doe@example.com\n",
}


def read_skill(text: str) -> tuple[dict[str, str], str, int]:
    _, front, body = text.split("---\n", 2)
    loaded = YAML(typ="safe").load(front)
    return loaded, body, text.count("\n", 0, text.index(body)) + 1


def rule_lines(body: str, first_line: int = 1) -> Iterator[tuple[int, str]]:
    section = None
    fenced = False
    for line, content in enumerate(body.splitlines(), first_line):
        if content.startswith(FENCE):
            fenced = not fenced
        heading = SECTION.match(content)
        if heading and not fenced:
            section = heading["name"]
        rule = RULE_LINE.match(content)
        if rule and section in RULE_SECTIONS and not fenced:
            yield line, rule["text"]


def skill_source(text: str) -> tuple[str, dict[int, int]]:
    front, body, first_line = read_skill(text)
    lines = [
        "---",
        f"id: {front['name']}",
        "kind: ka:Skill",
        "title: Skill",
        "status: proposed",
        "origin: template",
        "knowledge_type: domain",
        f"description: {front['description']}",
        "invocation: agent",
        "---",
        "",
        "## Directives",
        "",
    ]
    origin: dict[int, int] = {}
    for index, (line, rule) in enumerate(rule_lines(body, first_line)):
        origin[len(lines) + 1] = line
        lines += [
            f"- {rule} ^rule-{index}",
            "  - scope: node",
            "  - basis: judgment",
            "  - status: proposed",
            "  - origin: template",
        ]
    return "\n".join(lines) + "\n", origin


def language_problems(text: str, profile: LanguageProfile) -> list[tuple[int, str, str]]:
    source, origin = skill_source(text)
    parsed = parse_source(source, SKILL)
    assert isinstance(parsed, ParsedNode), parsed
    _, problems = check_items([parsed], profile)
    return [
        (origin.get(problem.line, problem.line), problem.code, problem.message)
        for problem in problems
        if problem.code not in SYNTHETIC_NODE_CODES
    ]


def language_codes(text: str, profile: LanguageProfile) -> set[str]:
    return {code for _, code, _ in language_problems(text, profile)}


def missing_rules(text: str) -> list[str]:
    _, body, _ = read_skill(text)
    rules = {rule for _, rule in rule_lines(body)}
    return [name for name, rule in REQUIRED_RULES.items() if rule not in rules]


def unknown_commands(text: str) -> list[str]:
    group = get_command(app)
    assert isinstance(group, TyperGroup)
    unknown: list[str] = []
    for found in COMMAND.finditer(text):
        command = group.commands.get(found["name"])
        if command is None:
            unknown.append(found[0])
            continue
        option = found["option"]
        names = {name for parameter in command.params for name in parameter.opts}
        if option and option.strip() not in names:
            unknown.append(found[0])
    return unknown


def engine_codes() -> set[str]:
    sources = "\n".join(path.read_text(encoding="utf-8") for path in ENGINE.rglob("*.py"))
    return set(re.findall(r'"([a-z]+(?:-[a-z]+)*)"', sources))


def unknown_problem_codes(text: str) -> list[str]:
    table = PROBLEM_CODES.search(text)
    assert table is not None
    codes = TABLE_CODE.findall(table["table"])
    assert codes
    known = engine_codes()
    return [code for code in codes if code not in known]


def dangling_headings(text: str) -> list[str]:
    headings = set(text.splitlines())
    return [name for name in HEADING_NAME.findall(text) if name not in headings]


def hard_style_problems(text: str) -> list[str]:
    findings = lint(text)[0]
    return [finding["rule"] for finding in findings if finding["level"] == HARD_LEVEL]


def skeleton_result(text: str) -> object:
    found = SKELETON.search(text)
    assert found is not None
    return parse_source(found["source"] + "\n", SKILL)


def size_problems(text: str) -> list[str]:
    kept = text.index(REFERENCES)
    problems: list[str] = []
    if kept > SKILL_KEPT_CHARACTERS:
        problems.append("size")
    if FENCE in text[:kept]:
        problems.append("order")
    return problems


def name_problems(name: str, folder: str) -> list[str]:
    problems: list[str] = []
    if name != folder:
        problems.append("folder")
    if not SKILL_NAME_FORM.fullmatch(name):
        problems.append("form")
    if len(name) > MAX_NAME_CHARACTERS:
        problems.append("length")
    return problems


def search_hits(text: str, folder: Path) -> list[str]:
    found = SEARCH.search(text)
    assert found is not None
    shell = shutil.which("sh")
    assert shell is not None
    done = subprocess.run(  # noqa: S603
        [shell, "-c", found["command"].replace("<paths>", ".")],
        cwd=folder,
        capture_output=True,
        text=True,
        check=False,
    )
    return done.stdout.splitlines()


@pytest.fixture(scope="module")
def profile() -> LanguageProfile:
    loaded = read_profile(REPO / "knowledge/governance/language")
    assert isinstance(loaded, LanguageProfile), loaded
    return loaded


@pytest.fixture(scope="module")
def text() -> str:
    return SKILL.read_text(encoding="utf-8")


@pytest.fixture
def search_folder(tmp_path: Path) -> Path:
    git = shutil.which("git")
    assert git is not None
    subprocess.run([git, "init", "-q"], cwd=tmp_path, check=True)  # noqa: S603
    for name, value in PLANTED_SECRETS.items():
        (tmp_path / name).write_text(f"clean line\n{value}", encoding="utf-8")
    (tmp_path / "clean.txt").write_text("Rotate the token before a release.\n", encoding="utf-8")
    return tmp_path


def test_the_skill_passes_the_language_checks(text: str, profile: LanguageProfile) -> None:
    assert language_problems(text, profile) == []


def test_the_rule_reader_covers_each_rule_section(text: str) -> None:
    _, body, first_line = read_skill(text)
    lines = dict(rule_lines(body, first_line))
    assert len(lines) > MIN_RULES
    for line, rule in lines.items():
        assert rule in text.splitlines()[line - 1]
    sections = {match["name"] for line in body.splitlines() if (match := SECTION.match(line))}
    assert set(RULE_SECTIONS) <= sections


@pytest.mark.parametrize(
    ("description", "code"),
    [
        ("Migrates things.", "description-form"),
        (f"{'word ' * 300}Use when a person asks for a pull.", "description-length"),
    ],
)
def test_a_bad_description_fails(
    text: str, profile: LanguageProfile, description: str, code: str
) -> None:
    front, _, _ = read_skill(text)
    changed = text.replace(front["description"], description, 1)
    assert code in language_codes(changed, profile)


@pytest.mark.parametrize(
    ("rule", "code"),
    [
        ("You should run the tests.", "opening"),
        ("Run the tests if needed.", "prohibited"),
        ("Keep each file under 200 lines.", "literal"),
        ("Build the package, run the tests, and push the branch.", "second-directive"),
    ],
)
def test_a_bad_rule_fails(text: str, profile: LanguageProfile, rule: str, code: str) -> None:
    changed = text.replace("## Directives\n\n", f"## Directives\n\n- {rule}\n", 1)
    assert code in language_codes(changed, profile)


@pytest.mark.parametrize("heading", ["### Check the result\n\n", "### Pull the changes\n\n"])
def test_a_bad_step_fails(text: str, profile: LanguageProfile, heading: str) -> None:
    changed = text.replace(heading, f"{heading}1. Maybe run the tests.\n", 1)
    assert "opening" in language_codes(changed, profile)


def test_a_problem_names_its_line_in_the_skill(text: str, profile: LanguageProfile) -> None:
    heading = "### Pull the changes\n\n"
    changed = text.replace(heading, f"{heading}1. Maybe run the tests.\n", 1)
    line = changed.splitlines().index("1. Maybe run the tests.") + 1
    assert (line, "opening") in [
        (found, code) for found, code, _ in language_problems(changed, profile)
    ]


def test_a_fenced_line_is_not_a_rule() -> None:
    body = "## Directives\n\n```text\n- Maybe run the tests.\n```\n\n- Run the tests.\n"
    assert [rule for _, rule in rule_lines(body)] == ["Run the tests."]


def test_a_fenced_heading_does_not_end_a_section() -> None:
    body = "## Directives\n\n```text\n## References\n```\n\n- Run the tests.\n"
    assert [rule for _, rule in rule_lines(body)] == ["Run the tests."]


def test_a_rule_outside_the_rule_sections_is_not_a_rule() -> None:
    body = "## References\n\n- Maybe run the tests.\n"
    assert list(rule_lines(body)) == []


def test_the_skill_holds_each_required_rule(text: str) -> None:
    assert missing_rules(text) == []


@pytest.mark.parametrize("name", REQUIRED_RULES)
def test_a_removed_rule_fails(text: str, name: str) -> None:
    changed = text.replace(f"{REQUIRED_RULES[name]}\n", "Run `ka runtime`.\n", 1)
    assert missing_rules(changed) == [name]


def test_a_rule_outside_the_rule_sections_does_not_count(text: str) -> None:
    rule = REQUIRED_RULES["secret"]
    changed = text.replace(f"- {rule}\n", "", 1) + f"\n- {rule}\n"
    assert missing_rules(changed) == ["secret"]


def test_each_command_exists(text: str) -> None:
    assert COMMAND.search(text)
    assert unknown_commands(text) == []


@pytest.mark.parametrize(
    "bad",
    [
        "`knowledge/.ka/ka promote`",
        "`knowledge/.ka/ka runtime --force`",
        "`knowledge/.ka/ka history --missing`",
    ],
)
def test_an_unknown_command_fails(text: str, bad: str) -> None:
    assert unknown_commands(f"{text}\n{bad}\n") == [bad.strip("`")]


def test_each_problem_code_exists(text: str) -> None:
    assert unknown_problem_codes(text) == []


def test_an_empty_code_table_fails(text: str) -> None:
    changed = TABLE_CODE.sub("| x |", text)
    with pytest.raises(AssertionError):
        unknown_problem_codes(changed)


def test_an_unknown_problem_code_fails(text: str) -> None:
    changed = re.sub(r"\| `opening` +\|", "| `no-such-code` |", text, count=1)
    assert unknown_problem_codes(changed) == ["no-such-code"]


def test_each_named_heading_exists(text: str) -> None:
    assert HEADING_NAME.search(text)
    assert dangling_headings(text) == []


def test_a_dangling_heading_fails(text: str) -> None:
    changed = text.replace("### Secret search\n", "### Search\n", 1)
    assert set(dangling_headings(changed)) == {"### Secret search"}


def test_the_skill_passes_the_style_lint(text: str) -> None:
    assert hard_style_problems(text) == []


def test_a_style_failure_fails_the_lint(text: str) -> None:
    assert hard_style_problems(f"{text}\nWe keep a robust thing here.\n") == ["marketing-adjective"]


def test_an_advisory_finding_does_not_fail_the_lint(text: str) -> None:
    assert hard_style_problems(f"{text}\nThe agent wrote this. The file was written twice.\n") == []


def test_the_skeleton_parses_as_a_proposed_node(text: str) -> None:
    result = skeleton_result(text)
    assert isinstance(result, ParsedNode), result
    assert result.node.status == "proposed"
    assert result.node.origin == "project"
    assert [directive.status for directive in result.node.directives or []] == ["proposed"]


def test_a_broken_skeleton_fails(text: str) -> None:
    result = skeleton_result(text.replace("## Definition\n\nHow", "## Definitions\n\nHow", 1))
    assert not isinstance(result, ParsedNode)


def test_the_steps_stay_in_the_kept_size(text: str) -> None:
    assert size_problems(text) == []
    assert "\n## Reconciliation\n" in text[: text.index(REFERENCES)]


def test_long_steps_fail_the_kept_size(text: str) -> None:
    filler = "x" * SKILL_KEPT_CHARACTERS
    assert size_problems(text.replace("## Reconciliation\n", f"{filler}\n", 1)) == ["size"]


def test_a_code_block_before_the_references_fails(text: str) -> None:
    assert size_problems(text.replace("## Reconciliation\n", f"{FENCE}\n", 1)) == ["order"]


def test_a_renamed_references_section_fails(text: str) -> None:
    assert "order" in size_problems(text.replace(REFERENCES, "\n## Reference list\n", 1))


def test_the_name_has_the_form_of_a_skill_name(text: str) -> None:
    front, _, _ = read_skill(text)
    assert name_problems(front["name"], SKILL.parent.name) == []


@pytest.mark.parametrize(
    ("name", "folder", "code"),
    [
        (SKILL_NAME, "other-folder", "folder"),
        ("Migrate_It", "Migrate_It", "form"),
        ("a" * (MAX_NAME_CHARACTERS + 1), "a" * (MAX_NAME_CHARACTERS + 1), "length"),
    ],
)
def test_a_bad_name_fails(name: str, folder: str, code: str) -> None:
    assert name_problems(name, folder) == [code]


def test_the_page_names_the_install_command() -> None:
    assert INSTALL_COMMAND in PAGE.read_text(encoding="utf-8")


def test_the_search_prints_a_path_and_a_line_for_each_planted_value(
    text: str, search_folder: Path
) -> None:
    hits = search_hits(text, search_folder)
    assert sorted(hits) == sorted(f"{name}:2" for name in PLANTED_SECRETS)


def test_the_search_finds_no_clean_text(text: str, search_folder: Path) -> None:
    assert not any(hit.startswith("clean.txt") for hit in search_hits(text, search_folder))
