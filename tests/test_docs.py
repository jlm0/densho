# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportMissingTypeStubs=false, reportOptionalMemberAccess=false
import re
from dataclasses import replace
from pathlib import Path, PurePosixPath
from typing import get_args

import pytest
from linkml_runtime.utils.schemaview import SchemaView
from markdown_it import MarkdownIt
from rdflib import Graph, Variable
from ruamel.yaml import YAML

from engine.cli import app
from engine.compiler import BUILD_CODES, OUTPUT_FOLDER, file_names
from engine.directives import DIRECTIVE_CODES
from engine.evaluation.conditions import CANARY_CODE, CONDITION_CODE
from engine.evaluation.harness import LOGIN_CODE, RUN_CODE
from engine.evaluation.isolation import ISOLATION_CODES
from engine.evaluation.tasks import TASK_CODE
from engine.generated.metamodel import CompiledResult, Concept
from engine.governance import GOVERNANCE_CODES
from engine.governance.checks import RESTING_FIELDS
from engine.governance.entities import (
    DIRECTIVE_FIELDS_WITHOUT_REVIEW,
    EXCEPTION_FIELDS_WITHOUT_REVIEW,
    NODE_FIELDS_WITHOUT_REVIEW,
)
from engine.graph.structure import ACYCLIC_EDGES, MAX_POINTER_HOPS
from engine.interface import ACCEPT_CODES, VIEW_CODES, VIEW_FOLDER
from engine.language import check_items
from engine.language.profile import (
    LISTING_ENTRY_CAP,
    CheckCode,
    LanguageProfile,
    read_profile,
)
from engine.parser import ParsedNode, parse_source, parse_tree
from engine.runtime import REVIEW_FOLDER, RUNTIME_CODES, review_path
from engine.template import ADOPT_CODES, HISTORY_CODES, SELECT_CODES, Entry

REPO = Path(__file__).resolve().parents[1]
README = REPO / "README.md"
DOCS = REPO / "docs"
OVERVIEW = DOCS / "README.md"
FILES = sorted(DOCS.glob("*.md"))
PAGES = [path for path in FILES if path != OVERVIEW]
ANALOGY_LINE = re.compile(r"^> \*\*In the library:\*\* \S", re.MULTILINE)
STATUS_LINE = re.compile(r"^\*\*Status:\*\* (Built|Planned)\.", re.MULTILINE)
OVERVIEW_ROW = re.compile(
    r"^\| \[[^\]]+\]\((?P<page>[^)]+)\) *\|[^|]+\| (?P<status>\w+) *\|$", re.MULTILINE
)
VIEW = SchemaView(str(REPO / "knowledge/governance/schema/metamodel.yaml"))


def local_links(path: Path) -> list[str]:
    tokens = MarkdownIt("commonmark").parse(path.read_text(encoding="utf-8"))
    links = [
        str(child.attrGet("href"))
        for token in tokens
        for child in token.children or []
        if child.type == "link_open"
    ]
    return [link for link in links if "://" not in link and not link.startswith("mailto:")]


def heading_slugs(path: Path) -> set[str]:
    tokens = MarkdownIt("commonmark").parse(path.read_text(encoding="utf-8"))
    headings = [
        tokens[index + 1].content
        for index, token in enumerate(tokens)
        if token.type == "heading_open"
    ]
    return {"-".join(heading.casefold().split()) for heading in headings}


def broken_links(path: Path) -> list[str]:
    broken: list[str] = []
    for link in local_links(path):
        target, _, anchor = link.partition("#")
        resolved = (path.parent / target).resolve() if target else path
        if not resolved.exists() or (anchor and anchor not in heading_slugs(resolved)):
            broken.append(link)
    return broken


def test_the_link_check_finds_a_missing_file_and_a_missing_heading(tmp_path: Path) -> None:
    page = tmp_path / "page.md"
    page.write_text(
        "# Real heading\n\n[a](missing.md) [b](#no-heading) [c](#real-heading) "
        "[d](page.md) [e](https://example.com)\n",
        encoding="utf-8",
    )
    assert broken_links(page) == ["missing.md", "#no-heading"]


@pytest.mark.parametrize("path", [README, *FILES], ids=lambda path: str(path.relative_to(REPO)))
def test_each_local_link_resolves(path: Path) -> None:
    assert broken_links(path) == []


def test_the_readme_links_to_the_overview() -> None:
    linked = {(REPO / link).resolve() for link in local_links(README)}
    assert OVERVIEW in linked


def test_the_overview_links_to_each_page() -> None:
    linked = {(DOCS / link).resolve() for link in local_links(OVERVIEW)}
    assert PAGES
    assert set(PAGES) <= linked


def page_status(text: str) -> str | None:
    if len(ANALOGY_LINE.findall(text)) != 1:
        return None
    statuses = STATUS_LINE.findall(text)
    return statuses[0] if len(statuses) == 1 else None


def overview_statuses(text: str) -> dict[str, str]:
    return {row["page"]: row["status"] for row in OVERVIEW_ROW.finditer(text)}


@pytest.mark.parametrize(
    "text",
    [
        "**Status:** Built.\n",
        "> **In the library:** a book.\n",
        "> **In the library:** a book.\n\n**Status:** Unknown.\n",
        "> **In the library:** a book.\n\n**Status:** Built.\n\n**Status:** Planned.\n",
        "> **In the library:** a book.\n\n> **In the library:** a shelf.\n\n**Status:** Built.\n",
    ],
)
def test_the_page_check_rejects_a_bad_page(text: str) -> None:
    assert page_status(text) is None


def test_the_page_check_reads_a_good_page() -> None:
    text = "> **In the library:** a book.\n\n**Status:** Planned. Not yet.\n"
    assert page_status(text) == "Planned"


@pytest.mark.parametrize("path", PAGES, ids=lambda path: path.name)
def test_each_page_has_one_analogy_and_one_status(path: Path) -> None:
    assert page_status(path.read_text(encoding="utf-8")) is not None


def test_the_overview_check_reads_the_rows() -> None:
    text = "| [A](a.md) | A book | Built |\n| [B](b.md)   | A shelf | Planned |\n| A | B | C |\n"
    assert overview_statuses(text) == {"a.md": "Built", "b.md": "Planned"}


def test_the_overview_shows_the_status_of_each_page() -> None:
    expected = {path.name: page_status(path.read_text(encoding="utf-8")) for path in PAGES}
    assert overview_statuses(OVERVIEW.read_text(encoding="utf-8")) == expected


def concrete_classes() -> list[str]:
    roots = [*VIEW.class_descendants("Node"), *VIEW.class_descendants("Pointer")]
    return [name for name in roots if not VIEW.get_class(name).abstract]


def edges() -> list[str]:
    return [name for name, slot in VIEW.all_slots().items() if slot.is_a == "edge"]


@pytest.mark.parametrize("name", concrete_classes())
def test_the_schema_page_names_each_kind(name: str) -> None:
    assert f"`densho:{name}`" in (DOCS / "schema.md").read_text(encoding="utf-8")


@pytest.mark.parametrize("name", edges())
def test_the_schema_page_names_each_edge(name: str) -> None:
    assert f"| `{name}`" in (DOCS / "schema.md").read_text(encoding="utf-8")


def test_the_schema_helpers_find_the_schema() -> None:
    assert "Concept" in concrete_classes()
    assert "broader" in edges()


def test_the_node_format_example_parses() -> None:
    text = (DOCS / "node-format.md").read_text(encoding="utf-8")
    example = text.split("```markdown\n")[1].split("\n```\n")[0]
    result = parse_source(f"{example}\n", Path("node.md"))
    assert isinstance(result, ParsedNode), result
    assert isinstance(result.node, Concept)


def graph_page() -> str:
    return (DOCS / "graph-checks.md").read_text(encoding="utf-8")


@pytest.mark.parametrize(
    "code",
    [
        "duplicate-id",
        "root",
        "placement",
        "reference",
        "type",
        "skill",
        "implements",
        "association",
        "cycle",
        "unreachable",
        "depth",
    ],
)
def test_the_graph_page_names_each_code(code: str) -> None:
    assert f"| `{code}`" in graph_page()


def test_the_graph_page_states_the_depth_limit() -> None:
    assert f"more than {MAX_POINTER_HOPS} hops" in graph_page()


@pytest.mark.parametrize("edge", ACYCLIC_EDGES)
def test_the_graph_page_names_each_acyclic_edge(edge: str) -> None:
    assert f"`{edge}` edges" in graph_page()


def language_page() -> str:
    return (DOCS / "language-checks.md").read_text(encoding="utf-8")


def language_profile() -> LanguageProfile:
    profile = read_profile(REPO / "knowledge/governance/language")
    assert isinstance(profile, LanguageProfile), profile
    return replace(profile, branches={}, branch_paths={})


@pytest.mark.parametrize(
    "code", [*get_args(CheckCode.__value__), "vocabulary-branch", "language-profile"]
)
def test_the_language_page_names_each_code(code: str) -> None:
    assert f"| `{code}`" in language_page()


def test_the_language_page_states_each_limit() -> None:
    grammar = language_profile().grammar
    page = language_page()
    assert f"in {grammar.directive.max_words} words or fewer" in page
    assert f"sentence of {grammar.trigger.max_words} words or fewer" in page
    limits = grammar.skill_description
    assert f"Each sentence has at most {limits.max_sentence_words} words" in page
    assert f"| {limits.max_characters} characters" in page
    assert f"| {limits.max_listing_characters:,} characters" in page
    assert f"| {LISTING_ENTRY_CAP:,} characters" in page


def language_examples() -> list[str]:
    blocks = language_page().split("```text\n")[1:]
    return [line for block in blocks for line in block.split("\n```")[0].splitlines()]


LANGUAGE_NODE = "---\nid: a\ntitle: A\nstatus: accepted\norigin: template\n"
LANGUAGE_TRIGGERS = {
    "You edit a test file.",
    "The build fails.",
    "`pytest` fails.",
    "A file is open.",
}


def language_example_source(example: str) -> str:
    if " Use when " in example:
        fields = (
            f"knowledge_type: domain\nkind: densho:Skill\ndescription: {example}\n"
            "invocation: agent\nskill_type: system\nuses: [b]\n"
        )
        return f"{LANGUAGE_NODE}{fields}---\n"
    if example in LANGUAGE_TRIGGERS:
        pointer = f'  - kind: densho:TextPointer\n    target: b\n    trigger: "{example}"\n'
        return f"{LANGUAGE_NODE}kind: densho:Root\npointers:\n{pointer}---\n"
    return (
        f"{LANGUAGE_NODE}kind: densho:Domain\nknowledge_type: domain\n---\n\n"
        "## Definition\n\nA.\n\n## Directives\n\n"
        f"- {example} ^b\n  - scope: node\n"
        "  - basis: judgment\n  - status: accepted\n  - origin: template\n"
    )


def test_the_language_page_has_examples() -> None:
    assert set(language_examples()) >= LANGUAGE_TRIGGERS
    assert any(example.endswith("changes code.") for example in language_examples())
    assert any(" Do not use it for " in example for example in language_examples())
    assert "Do not commit a secret." in language_examples()


@pytest.mark.parametrize("example", language_examples())
def test_each_language_example_passes_as_its_kind(example: str) -> None:
    result = parse_source(language_example_source(example), Path("node.md"))
    assert isinstance(result, ParsedNode), result
    assert check_items([result], language_profile())[1] == []


def test_the_node_format_example_passes_the_language_checks() -> None:
    text = (DOCS / "node-format.md").read_text(encoding="utf-8")
    example = text.split("```markdown\n")[1].split("\n```\n")[0]
    result = parse_source(f"{example}\n", Path("node.md"))
    assert isinstance(result, ParsedNode), result
    assert check_items([result], language_profile())[1] == []


def directive_page() -> str:
    return (DOCS / "directive-semantics.md").read_text(encoding="utf-8")


def directive_examples() -> list[str]:
    blocks = directive_page().split("```markdown\n")[1:]
    return [block.split("\n```\n")[0] for block in blocks]


DIRECTIVE_NODE = (
    "---\nid: a\nkind: densho:Domain\ntitle: A\nstatus: accepted\norigin: template\n"
    "knowledge_type: domain\n---\n\n## Definition\n\nA.\n\n"
)


@pytest.mark.parametrize("code", DIRECTIVE_CODES)
def test_the_directive_page_names_each_code(code: str) -> None:
    assert f"| `{code}`" in directive_page()


def test_the_directive_page_has_each_kind_of_example() -> None:
    examples = "\n".join(directive_examples())
    assert "exceptions:" in examples
    assert "refines:" in examples
    assert "conflicts_with:" in examples


@pytest.mark.parametrize("example", directive_examples())
def test_each_directive_example_parses_and_passes_the_language_checks(example: str) -> None:
    source = example if example.startswith("---") else f"{DIRECTIVE_NODE}{example}"
    result = parse_source(f"{source}\n", Path("node.md"))
    assert isinstance(result, ParsedNode), result
    assert check_items([result], language_profile())[1] == []


def governance_page() -> str:
    return (DOCS / "governance-workflow.md").read_text(encoding="utf-8")


def table_row(page: str, start: str) -> str:
    return next(line for line in page.splitlines() if line.startswith(start))


@pytest.mark.parametrize("code", GOVERNANCE_CODES)
def test_the_governance_page_names_each_code(code: str) -> None:
    assert f"| `{code}`" in governance_page()


def test_the_governance_page_names_each_field_without_review() -> None:
    page = governance_page()
    identity = {"id", "status", "origin", "directive"}
    rows = {
        "| Node ": NODE_FIELDS_WITHOUT_REVIEW,
        "| Directive ": DIRECTIVE_FIELDS_WITHOUT_REVIEW,
        "| Exception ": EXCEPTION_FIELDS_WITHOUT_REVIEW,
    }
    for start, fields in rows.items():
        column = table_row(page, start).rsplit("|", 2)[1]
        assert fields - identity
        for field in fields - identity:
            assert f"`{field}`" in column


def test_the_governance_page_names_each_resting_field() -> None:
    row = table_row(governance_page(), "| `deprecated-reference`")
    for field in RESTING_FIELDS:
        assert f"`{field}`" in row


def policy_ids() -> list[str]:
    items, problems = parse_tree([REPO / "knowledge/governance/policies"])
    assert problems == []
    return [item.node.id for item in items]


def test_the_governance_page_names_each_policy() -> None:
    assert policy_ids()
    for node_id in policy_ids():
        assert f"| `{node_id}`" in governance_page()


def test_the_governance_page_names_a_real_directive() -> None:
    items, _ = parse_tree([REPO / "knowledge/governance/policies"])
    directives = {directive.id for item in items for directive in item.node.directives or []}
    assert "no-personal-data" in directives
    assert "`no-personal-data`" in governance_page()


def documented_commands() -> set[str]:
    texts = [path.read_text(encoding="utf-8") for path in [README, *FILES]]
    pattern = r"(?:uv run densho|knowledge/\.densho/densho) (\w+)"
    return {command for text in texts for command in re.findall(pattern, text)}


def test_each_documented_command_exists() -> None:
    commands = {command.name or command.callback.__name__ for command in app.registered_commands}
    assert documented_commands()
    assert documented_commands() <= commands


COMPILED_PAGE = DOCS / "compiled-outputs.md"


@pytest.mark.parametrize("code", BUILD_CODES)
def test_the_compiled_page_names_each_code(code: str) -> None:
    assert f"`{code}`" in COMPILED_PAGE.read_text(encoding="utf-8")


@pytest.mark.parametrize("name", [name for result in CompiledResult for name in file_names(result)])
def test_the_compiled_page_names_each_output_file(name: str) -> None:
    assert f"`{name}`" in COMPILED_PAGE.read_text(encoding="utf-8")


INTERFACE_PAGE = DOCS / "human-interface.md"
RUNTIME_PAGE = DOCS / "runtime-files.md"


@pytest.mark.parametrize("code", RUNTIME_CODES)
def test_the_runtime_page_names_each_code(code: str) -> None:
    assert f"`{code}`" in RUNTIME_PAGE.read_text(encoding="utf-8")


def test_the_runtime_page_names_the_review_folder_and_each_review_name() -> None:
    text = RUNTIME_PAGE.read_text(encoding="utf-8")
    assert f"`{REVIEW_FOLDER.as_posix()}/`" in text
    names = (
        "AGENTS.md",
        ".claude/skills/<id>/SKILL.md",
        ".claude/rules/knowledge/<id>.md",
        ".claude/references/<id>.md",
    )
    for name in names:
        assert f"`{name}`" in text
        assert f"`{REVIEW_FOLDER.as_posix()}/{review_path(PurePosixPath(name))}`" in text


TEMPLATE_PAGE = DOCS / "template-packaging.md"


@pytest.mark.parametrize("code", [*ACCEPT_CODES, *VIEW_CODES])
def test_the_interface_page_names_each_code(code: str) -> None:
    assert f"`{code}`" in INTERFACE_PAGE.read_text(encoding="utf-8")


def test_the_interface_page_names_the_view_folder() -> None:
    assert f"`{VIEW_FOLDER}/" in INTERFACE_PAGE.read_text(encoding="utf-8")


@pytest.mark.parametrize(
    "sentence",
    [
        "A person runs this command.",
        "No check proves who ran it.",
    ],
)
def test_the_interface_page_states_who_runs_the_command(sentence: str) -> None:
    text = " ".join(INTERFACE_PAGE.read_text(encoding="utf-8").split())
    assert sentence in text


@pytest.mark.parametrize(
    "command",
    ["knowledge/.densho/densho view", "knowledge/.densho/densho accept", "uv run densho view"],
)
def test_the_interface_page_names_each_form_of_the_command(command: str) -> None:
    assert command in INTERFACE_PAGE.read_text(encoding="utf-8")


@pytest.mark.parametrize("code", [*ADOPT_CODES, *SELECT_CODES, *HISTORY_CODES])
def test_the_template_page_names_each_code(code: str) -> None:
    assert f"`{code}`" in TEMPLATE_PAGE.read_text(encoding="utf-8")


@pytest.mark.parametrize("key", Entry.model_fields)
def test_the_template_page_names_each_history_key(key: str) -> None:
    assert f"| `{key}`" in TEMPLATE_PAGE.read_text(encoding="utf-8")


def test_the_template_page_example_is_a_history_line() -> None:
    tokens = MarkdownIt("commonmark").parse(TEMPLATE_PAGE.read_text(encoding="utf-8"))
    examples = [token.content for token in tokens if token.info == "json"]
    assert len(examples) == 1
    assert Entry.model_validate_json(examples[0]).kind == "directive"


def test_the_template_page_names_each_path_that_a_project_receives() -> None:
    text = TEMPLATE_PAGE.read_text(encoding="utf-8")
    config = YAML(typ="safe").load((REPO / "copier.yml").read_text(encoding="utf-8"))
    allowed = [entry[2:] for entry in config["_exclude"] if entry.startswith("!/")]
    assert allowed
    assert [path for path in allowed if f"`{path}" not in text] == []


def test_the_compiled_page_names_the_output_folder() -> None:
    assert f"`{OUTPUT_FOLDER.as_posix()}/`" in COMPILED_PAGE.read_text(encoding="utf-8")


def test_the_compiled_page_query_runs_on_a_compiled_graph() -> None:
    blocks = [
        token.content
        for token in MarkdownIt("commonmark").parse(COMPILED_PAGE.read_text(encoding="utf-8"))
        if token.type == "fence" and token.info == "sparql"
    ]
    assert len(blocks) == 1
    data = Graph().parse(
        data="""
        @prefix densho: <https://github.com/jlm0/densho/schema/> .
        @prefix skos: <http://www.w3.org/2004/02/skos/core#> .
        densho:a skos:broader densho:b ; densho:status "accepted" .
        densho:c skos:broader densho:b ; densho:status "proposed" .
        """,
        format="turtle",
    )
    children = [binding[Variable("child")] for binding in data.query(blocks[0]).bindings]
    assert [str(child).rpartition("/")[2] for child in children] == ["a"]


EVAL_PAGE = DOCS / "evaluation.md"


@pytest.mark.parametrize(
    "code", [TASK_CODE, CONDITION_CODE, CANARY_CODE, RUN_CODE, LOGIN_CODE, *ISOLATION_CODES]
)
def test_the_eval_page_names_each_code(code: str) -> None:
    assert f"`{code}`" in EVAL_PAGE.read_text(encoding="utf-8")
