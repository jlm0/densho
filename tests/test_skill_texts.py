# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false
import re
import shutil
import subprocess
from dataclasses import dataclass, replace
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from ruamel.yaml import YAML
from typer.core import TyperGroup
from typer.main import get_command

from engine.cli import app
from engine.generated.metamodel import Invocation, Root, Skill
from engine.governance import check_items as check_governance_items
from engine.graph.rules import RESERVED_SKILL_NAMES
from engine.language import check_items
from engine.language.form import HARD_LEVEL
from engine.language.profile import LanguageProfile, read_profile
from engine.layout import GOVERNANCE_FOLDER
from engine.parser import ParsedNode, parse_source
from engine.parser.node import node_folders, parse_tree
from engine.runtime.claude_code import SKILL_KEPT_CHARACTERS, SKILL_LINES
from engine.vendor.ste_lint import lint

if TYPE_CHECKING:
    from collections.abc import Iterator

REPO = Path(__file__).resolve().parents[1]
GLOBAL_SKILLS = REPO / "global-skills"
ENGINE = REPO / "engine"
RULE_LINE = re.compile(r"^(?:- |\d+\. )(?P<text>.+)$")
SECTION = re.compile(r"^## (?P<name>.+)$")
FENCE = "```"
SKILL_NAME_FORM = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
MAX_NAME_CHARACTERS = 64
COMMAND = re.compile(
    r"(?:knowledge/\.ka/ka|uv run ka) (?P<name>[a-z]+)(?P<option> --[a-z]+(?:-[a-z]+)*)?"
)
HEADING_NAME = re.compile(r"`(?P<heading>### [^`]+)`")
SKELETON = re.compile(r"```markdown\n(?P<source>.+?)\n```", re.DOTALL)
PROBLEM_CODES = re.compile(r"### Problem codes\n(?P<table>.+?)\n### ", re.DOTALL)
TABLE_CODE = re.compile(r"^\| `(?P<code>[a-z-]+)` +\|", re.MULTILINE)
SEARCH = re.compile(r"^(?P<command>git grep .+)$", re.MULTILINE)
DOWNLOAD = re.compile(r"^curl .+$", re.MULTILINE)
PUBLIC_URL = "https://github.com/jlm0/knowledge-architecture"
REFERENCES = "\n## References\n"
SYNTHETIC_NODE_CODES = {"vocabulary-branch"}
PROMOTION_RULE = "Do not change a `status` to `accepted`."
PROPOSAL_RULE = "Set the `status` of each entity that you add to `proposed`."


@dataclass(frozen=True, slots=True)
class GlobalSkill:
    name: str
    rule_sections: tuple[str, ...]
    page: str
    min_rules: int
    required: dict[str, str]
    steps: tuple[str, ...]
    named_heading: str
    origin: str

    @property
    def path(self) -> Path:
        return GLOBAL_SKILLS / self.name / "SKILL.md"


MIGRATE = GlobalSkill(
    name="migrate-project",
    rule_sections=("Directives", "Migration"),
    page="docs/migration-and-reconciliation.md",
    min_rules=70,
    required={
        "secret": (
            "Do not copy secret material from a project into a node, the ledger, a command,"
            " or a reply."
        ),
        "promotion": PROMOTION_RULE,
        "proposal": PROPOSAL_RULE,
        "prose": "Do not convert a procedure or a reference into a directive.",
        "visible": "Keep each item that you do not convert in `knowledge-migration/ledger.md`.",
        "old text": (
            "Tell a person to remove the old text from `CLAUDE.md` after a person accepts its"
            " replacements."
        ),
        "review": (
            "Tell a person to review the proposals with the `review-proposals` skill of the"
            " project."
        ),
    },
    steps=("### Check the result\n\n", "### Report the migration\n\n"),
    named_heading="### Secret search",
    origin="project",
)
AUTHOR = GlobalSkill(
    name="author-domain",
    rule_sections=("Directives", "Procedure"),
    page="docs/seed-knowledge.md",
    min_rules=40,
    required={
        "promotion": PROMOTION_RULE,
        "proposal": PROPOSAL_RULE,
        "opened": "Open each source before you cite it.",
        "sourced": "Do not add a directive that no opened source states.",
        "own words": "Write each directive in your own words.",
        "contact": "Do not send a name or an email to a site.",
    },
    steps=("### Open the sources\n\n", "### Check the work\n\n"),
    named_heading="### Basis",
    origin="template",
)
SKILLS = (MIGRATE, AUTHOR)
PRESETS = {
    "propose-knowledge": Invocation.agent,
    "review-proposals": Invocation.person,
    "sync-template": Invocation.person,
    "evaluate-knowledge": Invocation.person,
}
ROOT_TRIGGER = "propose-corrections"
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


def rule_lines(
    body: str, sections: tuple[str, ...], first_line: int = 1
) -> Iterator[tuple[int, str]]:
    section = None
    fenced = False
    for line, content in enumerate(body.splitlines(), first_line):
        if content.startswith(FENCE):
            fenced = not fenced
        heading = SECTION.match(content)
        if heading and not fenced:
            section = heading["name"]
        rule = RULE_LINE.match(content)
        if rule and section in sections and not fenced:
            yield line, rule["text"]


def skill_source(text: str, skill: GlobalSkill) -> tuple[str, dict[int, int]]:
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
    for index, (line, rule) in enumerate(rule_lines(body, skill.rule_sections, first_line)):
        origin[len(lines) + 1] = line
        lines += [
            f"- {rule} ^rule-{index}",
            "  - scope: node",
            "  - basis: judgment",
            "  - status: proposed",
            "  - origin: template",
        ]
    return "\n".join(lines) + "\n", origin


def language_problems(
    text: str, skill: GlobalSkill, profile: LanguageProfile
) -> list[tuple[int, str, str]]:
    source, origin = skill_source(text, skill)
    parsed = parse_source(source, skill.path)
    assert isinstance(parsed, ParsedNode), parsed
    _, problems = check_items([parsed], profile)
    return [
        (origin.get(problem.line, problem.line), problem.code, problem.message)
        for problem in problems
        if problem.code not in SYNTHETIC_NODE_CODES
    ]


def language_codes(text: str, skill: GlobalSkill, profile: LanguageProfile) -> set[str]:
    return {code for _, code, _ in language_problems(text, skill, profile)}


def missing_rules(text: str, skill: GlobalSkill) -> list[str]:
    _, body, _ = read_skill(text)
    rules = {rule for _, rule in rule_lines(body, skill.rule_sections)}
    return [name for name, rule in skill.required.items() if rule not in rules]


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


def skeleton_result(text: str, skill: GlobalSkill) -> object:
    found = SKELETON.search(text)
    assert found is not None
    return parse_source(found["source"] + "\n", skill.path)


def size_problems(text: str, skill: GlobalSkill) -> list[str]:
    kept = text.index(REFERENCES) if REFERENCES in text else len(text)
    problems: list[str] = []
    if kept > SKILL_KEPT_CHARACTERS:
        problems.append("size")
    if FENCE in text[:kept] or REFERENCES not in text:
        problems.append("order")
    if any(f"\n## {section}\n" not in text[:kept] for section in skill.rule_sections):
        problems.append("section")
    if text.count("\n") > SKILL_LINES:
        problems.append("lines")
    return problems


def name_problems(name: str, folder: str) -> list[str]:
    problems: list[str] = []
    if name != folder:
        problems.append("folder")
    if not SKILL_NAME_FORM.fullmatch(name):
        problems.append("form")
    if len(name) > MAX_NAME_CHARACTERS:
        problems.append("length")
    if name.casefold() in RESERVED_SKILL_NAMES:
        problems.append("reserved")
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


def preset_problems(items: list[ParsedNode]) -> list[str]:
    found = {item.node.id: item.node for item in items if isinstance(item.node, Skill)}
    problems: list[str] = []
    for name, invocation in PRESETS.items():
        node = found.get(name)
        if node is None:
            problems.append(f"{name}: missing")
        elif node.invocation != invocation:
            problems.append(f"{name}: invocation")
    return problems


def root_trigger_problems(items: list[ParsedNode]) -> list[str]:
    roots = [item.node for item in items if isinstance(item.node, Root)]
    assert len(roots) == 1
    directives = {directive.id: directive for directive in roots[0].directives or []}
    directive = directives.get(ROOT_TRIGGER)
    if directive is None:
        return ["missing"]
    problems: list[str] = []
    if "`propose-knowledge`" not in directive.text:
        problems.append("skill")
    if directive.scope != "node":
        problems.append("scope")
    return problems


def preset_candidates(items: list[ParsedNode]) -> set[str]:
    governance = [item.node for item in items if item.path.is_relative_to(REPO / GOVERNANCE_FOLDER)]
    nodes = {node.id for node in governance}
    directives = {directive.id for node in governance for directive in node.directives or []}
    return {
        item.node.id
        for item in items
        if isinstance(item.node, Skill)
        and set(item.node.uses or []) <= nodes
        and set(item.node.applies or []) <= directives
    }


def skeleton_source_problems(result: ParsedNode, skill: GlobalSkill) -> list[str]:
    if skill.origin != "template":
        return []
    problems: list[str] = []
    for directive in result.node.directives or []:
        if directive.basis in {None, "judgment"}:
            problems.append(f"{directive.id}: basis")
        if not directive.sources:
            problems.append(f"{directive.id}: sources")
    return problems


def download_problems(text: str) -> list[str]:
    commands = DOWNLOAD.findall(text)
    if not commands:
        return ["none"]
    return [
        command
        for command in commands
        if f"-A 'knowledge-architecture (+{PUBLIC_URL})'" not in command
    ]


def pull_problems(text: str) -> list[str]:
    problems: list[str] = []
    if "copier update" in text:
        problems.append("pull")
    if "`sync-template`" not in text:
        problems.append("preset")
    return problems


def model_invocation(skill_file: Path) -> object:
    front, _, _ = read_skill(skill_file.read_text(encoding="utf-8"))
    return front.get("disable-model-invocation")


@pytest.fixture(scope="module")
def profile() -> LanguageProfile:
    loaded = read_profile(REPO / "knowledge/governance/language")
    assert isinstance(loaded, LanguageProfile), loaded
    return loaded


@pytest.fixture(scope="module", params=SKILLS, ids=lambda skill: skill.name)
def skill(request: pytest.FixtureRequest) -> GlobalSkill:
    return request.param


@pytest.fixture(scope="module")
def text(skill: GlobalSkill) -> str:
    return skill.path.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def migrate_text() -> str:
    return MIGRATE.path.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def items() -> list[ParsedNode]:
    parsed, problems = parse_tree(node_folders(REPO))
    assert problems == []
    return parsed


@pytest.fixture
def search_folder(tmp_path: Path) -> Path:
    git = shutil.which("git")
    assert git is not None
    subprocess.run([git, "init", "-q"], cwd=tmp_path, check=True)  # noqa: S603
    for name, value in PLANTED_SECRETS.items():
        (tmp_path / name).write_text(f"clean line\n{value}", encoding="utf-8")
    (tmp_path / "clean.txt").write_text("Rotate the token before a release.\n", encoding="utf-8")
    return tmp_path


def test_the_global_skills_are_the_folders_in_the_global_folder() -> None:
    folders = sorted(path.name for path in GLOBAL_SKILLS.iterdir() if path.is_dir())
    assert folders == sorted(skill.name for skill in SKILLS)


def test_the_skill_passes_the_language_checks(
    text: str, skill: GlobalSkill, profile: LanguageProfile
) -> None:
    assert language_problems(text, skill, profile) == []


def test_the_rule_reader_covers_each_rule_section(text: str, skill: GlobalSkill) -> None:
    _, body, first_line = read_skill(text)
    lines = dict(rule_lines(body, skill.rule_sections, first_line))
    assert len(lines) > skill.min_rules
    for line, rule in lines.items():
        assert rule in text.splitlines()[line - 1]
    sections = {match["name"] for line in body.splitlines() if (match := SECTION.match(line))}
    assert set(skill.rule_sections) <= sections


@pytest.mark.parametrize(
    ("description", "code"),
    [
        ("Migrates things.", "description-form"),
        (f"{'word ' * 300}Use when a person asks for a pull.", "description-length"),
    ],
)
def test_a_bad_description_fails(
    text: str, skill: GlobalSkill, profile: LanguageProfile, description: str, code: str
) -> None:
    front, _, _ = read_skill(text)
    changed = text.replace(front["description"], description, 1)
    assert code in language_codes(changed, skill, profile)


@pytest.mark.parametrize(
    ("rule", "code"),
    [
        ("You should run the tests.", "opening"),
        ("Run the tests if needed.", "prohibited"),
        ("Keep each file under 200 lines.", "literal"),
        ("Build the package, run the tests, and push the branch.", "second-directive"),
    ],
)
def test_a_bad_rule_fails(
    text: str, skill: GlobalSkill, profile: LanguageProfile, rule: str, code: str
) -> None:
    changed = text.replace("## Directives\n\n", f"## Directives\n\n- {rule}\n", 1)
    assert code in language_codes(changed, skill, profile)


def test_a_bad_step_fails(text: str, skill: GlobalSkill, profile: LanguageProfile) -> None:
    for heading in skill.steps:
        assert heading in text
        changed = text.replace(heading, f"{heading}1. Maybe run the tests.\n", 1)
        assert "opening" in language_codes(changed, skill, profile)


def test_a_problem_names_its_line_in_the_skill(
    text: str, skill: GlobalSkill, profile: LanguageProfile
) -> None:
    heading = skill.steps[-1]
    changed = text.replace(heading, f"{heading}1. Maybe run the tests.\n", 1)
    line = changed.splitlines().index("1. Maybe run the tests.") + 1
    assert (line, "opening") in [
        (found, code) for found, code, _ in language_problems(changed, skill, profile)
    ]


def test_a_fenced_line_is_not_a_rule() -> None:
    body = "## Directives\n\n```text\n- Maybe run the tests.\n```\n\n- Run the tests.\n"
    assert [rule for _, rule in rule_lines(body, ("Directives",))] == ["Run the tests."]


def test_a_fenced_heading_does_not_end_a_section() -> None:
    body = "## Directives\n\n```text\n## References\n```\n\n- Run the tests.\n"
    assert [rule for _, rule in rule_lines(body, ("Directives",))] == ["Run the tests."]


def test_a_rule_outside_the_rule_sections_is_not_a_rule() -> None:
    body = "## References\n\n- Maybe run the tests.\n"
    assert list(rule_lines(body, ("Directives",))) == []


def test_the_skill_holds_each_required_rule(text: str, skill: GlobalSkill) -> None:
    assert missing_rules(text, skill) == []


@pytest.mark.parametrize(
    ("skill_name", "name"),
    [(item.name, name) for item in SKILLS for name in item.required],
)
def test_a_removed_rule_fails(skill_name: str, name: str) -> None:
    skill = next(item for item in SKILLS if item.name == skill_name)
    text = skill.path.read_text(encoding="utf-8")
    changed = text.replace(f"{skill.required[name]}\n", "Run `ka runtime`.\n", 1)
    assert missing_rules(changed, skill) == [name]


def test_a_rule_outside_the_rule_sections_does_not_count(text: str, skill: GlobalSkill) -> None:
    rule = skill.required["promotion"]
    changed = text.replace(f"- {rule}\n", "", 1) + f"\n- {rule}\n"
    assert missing_rules(changed, skill) == ["promotion"]


def test_each_command_exists(text: str) -> None:
    assert COMMAND.search(text)
    assert unknown_commands(text) == []


@pytest.mark.parametrize(
    "bad",
    [
        "`knowledge/.ka/ka promote`",
        "`knowledge/.ka/ka runtime --force`",
        "`knowledge/.ka/ka history --missing`",
        "`uv run ka promote`",
        "`uv run ka directives --near`",
    ],
)
def test_an_unknown_command_fails(text: str, bad: str) -> None:
    assert unknown_commands(f"{text}\n{bad}\n") == [bad.strip("`")]


def test_each_problem_code_exists(migrate_text: str) -> None:
    assert unknown_problem_codes(migrate_text) == []


def test_an_empty_code_table_fails(migrate_text: str) -> None:
    changed = TABLE_CODE.sub("| x |", migrate_text)
    with pytest.raises(AssertionError):
        unknown_problem_codes(changed)


def test_an_unknown_problem_code_fails(migrate_text: str) -> None:
    changed = re.sub(r"\| `opening` +\|", "| `no-such-code` |", migrate_text, count=1)
    assert unknown_problem_codes(changed) == ["no-such-code"]


def test_each_named_heading_exists(text: str) -> None:
    assert HEADING_NAME.search(text)
    assert dangling_headings(text) == []


def test_a_dangling_heading_fails(text: str, skill: GlobalSkill) -> None:
    changed = text.replace(f"{skill.named_heading}\n", "### Renamed\n", 1)
    assert set(dangling_headings(changed)) == {skill.named_heading}


def test_the_skill_passes_the_style_lint(text: str) -> None:
    assert hard_style_problems(text) == []


def test_a_style_failure_fails_the_lint(text: str) -> None:
    assert hard_style_problems(f"{text}\nWe keep a robust thing here.\n") == ["marketing-adjective"]


def test_an_advisory_finding_does_not_fail_the_lint(text: str) -> None:
    assert hard_style_problems(f"{text}\nThe agent wrote this. The file was written twice.\n") == []


def test_the_skeleton_parses_as_a_proposed_node(text: str, skill: GlobalSkill) -> None:
    result = skeleton_result(text, skill)
    assert isinstance(result, ParsedNode), result
    assert result.node.status == "proposed"
    assert result.node.origin == skill.origin
    assert [directive.status for directive in result.node.directives or []] == ["proposed"]
    assert skeleton_source_problems(result, skill) == []


def test_the_skeleton_passes_the_governance_checks(text: str, skill: GlobalSkill) -> None:
    result = skeleton_result(text, skill)
    assert isinstance(result, ParsedNode), result
    assert [str(problem) for problem in check_governance_items([result], REPO)] == []


def test_the_migration_skeleton_cites_its_source_line_in_signals() -> None:
    result = skeleton_result(MIGRATE.path.read_text(encoding="utf-8"), MIGRATE)
    assert isinstance(result, ParsedNode), result
    assert [directive.sources for directive in result.node.directives or []] == [None]
    assert "## Signals\n\n- `use-whole-words`: 2026-11-06, migration. `rules/coding.md:14`." in (
        result.node.body or ""
    )


def test_a_template_skeleton_without_a_source_fails() -> None:
    text = AUTHOR.path.read_text(encoding="utf-8")
    changed = text.replace("  - sources: https://example.com/error-messages\n", "", 1)
    changed = changed.replace("  - basis: practitioner\n", "  - basis: judgment\n", 1)
    result = skeleton_result(changed, AUTHOR)
    assert isinstance(result, ParsedNode), result
    assert skeleton_source_problems(result, AUTHOR) == [
        "error-cause-and-next-step: basis",
        "error-cause-and-next-step: sources",
    ]


def test_a_broken_skeleton_fails(text: str, skill: GlobalSkill) -> None:
    found = SKELETON.search(text)
    assert found is not None
    broken = found["source"].replace("## Definition\n", "## Definitions\n", 1)
    assert broken != found["source"]
    result = skeleton_result(text.replace(found["source"], broken, 1), skill)
    assert not isinstance(result, ParsedNode)


def test_the_steps_stay_in_the_kept_size(text: str, skill: GlobalSkill) -> None:
    assert size_problems(text, skill) == []


def test_long_steps_fail_the_kept_size(text: str, skill: GlobalSkill) -> None:
    filler = "x" * SKILL_KEPT_CHARACTERS
    changed = text.replace("## Directives\n", f"{filler}\n## Directives\n", 1)
    assert size_problems(changed, skill) == ["size"]


def test_a_code_block_before_the_references_fails(text: str, skill: GlobalSkill) -> None:
    changed = text.replace("## Directives\n", f"{FENCE}\n## Directives\n", 1)
    assert size_problems(changed, skill) == ["order"]


def test_a_renamed_references_section_fails(text: str, skill: GlobalSkill) -> None:
    assert "order" in size_problems(text.replace(REFERENCES, "\n## Reference list\n", 1), skill)


def test_a_rule_section_after_the_references_fails(text: str, skill: GlobalSkill) -> None:
    section = f"\n## {skill.rule_sections[-1]}\n"
    changed = text.replace(section, "\n## Moved\n", 1) + section
    assert "section" in size_problems(changed, skill)


def test_a_skill_over_the_line_budget_fails(text: str, skill: GlobalSkill) -> None:
    changed = text + "\n" * (SKILL_LINES + 1 - text.count("\n"))
    assert size_problems(changed, skill) == ["lines"]
    assert size_problems(changed[:-1], skill) == []


def test_the_name_has_the_form_of_a_skill_name(text: str, skill: GlobalSkill) -> None:
    front, _, _ = read_skill(text)
    assert name_problems(front["name"], skill.path.parent.name) == []


@pytest.mark.parametrize(
    ("name", "folder", "code"),
    [
        (MIGRATE.name, "other-folder", "folder"),
        ("Migrate_It", "Migrate_It", "form"),
        ("a" * (MAX_NAME_CHARACTERS + 1), "a" * (MAX_NAME_CHARACTERS + 1), "length"),
        ("synced", "synced", "reserved"),
        ("anthropic-skills", "anthropic-skills", "reserved"),
    ],
)
def test_a_bad_name_fails(name: str, folder: str, code: str) -> None:
    assert name_problems(name, folder) == [code]


def test_the_page_names_the_install_command(skill: GlobalSkill) -> None:
    command = f"cp -R global-skills/{skill.name} ~/.claude/skills/"
    assert command in (REPO / skill.page).read_text(encoding="utf-8")


def test_the_search_prints_a_path_and_a_line_for_each_planted_value(
    migrate_text: str, search_folder: Path
) -> None:
    hits = search_hits(migrate_text, search_folder)
    assert sorted(hits) == sorted(f"{name}:2" for name in PLANTED_SECRETS)


def test_the_search_finds_no_clean_text(migrate_text: str, search_folder: Path) -> None:
    assert not any(hit.startswith("clean.txt") for hit in search_hits(migrate_text, search_folder))


def test_the_migration_leaves_the_pull_to_the_preset(migrate_text: str) -> None:
    assert pull_problems(migrate_text) == []


def test_a_migration_with_a_pull_fails(migrate_text: str) -> None:
    planted = migrate_text.replace("`sync-template`", "a later skill") + "\ncopier update --trust\n"
    assert pull_problems(planted) == ["pull", "preset"]


def test_the_presets_are_the_skills_that_draw_only_on_the_governance(
    items: list[ParsedNode],
) -> None:
    assert preset_candidates(items) == set(PRESETS)


def test_a_preset_that_uses_a_discipline_is_no_preset(items: list[ParsedNode]) -> None:
    changed = [
        replace(item, node=item.node.model_copy(update={"uses": ["ui-ux-design"]}))
        if item.node.id == "sync-template"
        else item
        for item in items
    ]
    assert preset_candidates(changed) == set(PRESETS) - {"sync-template"}
    applied = [
        replace(item, node=item.node.model_copy(update={"applies": ["plain-error-message"]}))
        if item.node.id == "review-proposals"
        else item
        for item in items
    ]
    assert preset_candidates(applied) == set(PRESETS) - {"review-proposals"}


def test_the_download_names_the_public_url() -> None:
    assert download_problems(AUTHOR.path.read_text(encoding="utf-8")) == []


def test_a_download_without_the_public_url_fails() -> None:
    text = AUTHOR.path.read_text(encoding="utf-8")
    assert download_problems(text.replace(f" (+{PUBLIC_URL})", "", 1)) != []
    assert download_problems(text.replace("curl ", "wget ")) == ["none"]


def test_each_preset_is_a_skill_with_its_invocation(items: list[ParsedNode]) -> None:
    assert preset_problems(items) == []


def test_a_missing_or_changed_preset_fails(items: list[ParsedNode]) -> None:
    kept = [item for item in items if item.node.id != "review-proposals"]
    assert preset_problems(kept) == ["review-proposals: missing"]
    changed = [
        replace(item, node=item.node.model_copy(update={"invocation": Invocation.agent}))
        if item.node.id == "sync-template"
        else item
        for item in items
    ]
    assert preset_problems(changed) == ["sync-template: invocation"]


@pytest.mark.parametrize("name", PRESETS)
def test_each_preset_names_only_known_commands_and_headings(name: str) -> None:
    text = (REPO / "knowledge/skills" / name / "node.md").read_text(encoding="utf-8")
    assert COMMAND.search(text)
    assert unknown_commands(text) == []
    assert dangling_headings(text) == []


@pytest.mark.parametrize(("name", "invocation"), PRESETS.items())
def test_a_person_preset_turns_off_model_invocation(name: str, invocation: Invocation) -> None:
    expected = True if invocation == Invocation.person else None
    assert model_invocation(REPO / ".claude/skills" / name / "SKILL.md") is expected


def test_the_root_trigger_names_the_preset(items: list[ParsedNode]) -> None:
    assert root_trigger_problems(items) == []


def test_a_root_trigger_with_another_scope_or_skill_fails(items: list[ParsedNode]) -> None:
    root = next(item for item in items if isinstance(item.node, Root))
    directives = root.node.directives or []
    trigger = next(directive for directive in directives if directive.id == ROOT_TRIGGER)
    for update, code in (
        ({"scope": "subtree"}, "scope"),
        ({"text": "Propose the change."}, "skill"),
    ):
        node = root.node.model_copy(
            update={
                "directives": [
                    trigger.model_copy(update=update) if directive is trigger else directive
                    for directive in directives
                ]
            }
        )
        assert root_trigger_problems([replace(root, node=node)]) == [code]
    empty = root.node.model_copy(update={"directives": []})
    assert root_trigger_problems([replace(root, node=empty)]) == ["missing"]
