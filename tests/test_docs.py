# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportMissingTypeStubs=false, reportOptionalMemberAccess=false
import re
from pathlib import Path
from typing import get_args

import pytest
from linkml_runtime.utils.schemaview import SchemaView
from markdown_it import MarkdownIt

from knowledge_architecture.cli import app
from knowledge_architecture.generated.metamodel import Concept
from knowledge_architecture.graph.structure import ACYCLIC_EDGES, MAX_POINTER_HOPS
from knowledge_architecture.language import check_items
from knowledge_architecture.language.profile import (
    LISTING_ENTRY_CAP,
    CheckCode,
    LanguageProfile,
    read_profile,
)
from knowledge_architecture.parser import ParsedNode, parse_source

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
VIEW = SchemaView(str(REPO / "governance/schema/metamodel.yaml"))


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
    assert f"`ka:{name}`" in (DOCS / "schema.md").read_text(encoding="utf-8")


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
    profile = read_profile(REPO / "governance/language")
    assert isinstance(profile, LanguageProfile), profile
    return profile


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
    if example.endswith("changes code."):
        fields = f"knowledge_type: domain\nkind: ka:Skill\ndescription: {example}\nuses: [b]\n"
        return f"{LANGUAGE_NODE}{fields}---\n"
    if example in LANGUAGE_TRIGGERS:
        pointer = f'  - kind: ka:TextPointer\n    target: b\n    trigger: "{example}"\n'
        return f"{LANGUAGE_NODE}kind: ka:Root\npointers:\n{pointer}---\n"
    return (
        f"{LANGUAGE_NODE}kind: ka:Domain\nknowledge_type: domain\n---\n\n"
        "## Definition\n\nA.\n\n## Directives\n\n"
        f"- {example} ^b\n  - scope: node\n  - status: accepted\n  - origin: template\n"
    )


def test_the_language_page_has_examples() -> None:
    assert set(language_examples()) >= LANGUAGE_TRIGGERS
    assert any(example.endswith("changes code.") for example in language_examples())
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


def documented_commands() -> set[str]:
    texts = [path.read_text(encoding="utf-8") for path in [README, *FILES]]
    return {command for text in texts for command in re.findall(r"uv run ka (\w+)", text)}


def test_each_documented_command_exists() -> None:
    commands = {command.callback.__name__ for command in app.registered_commands}
    assert documented_commands()
    assert documented_commands() <= commands
