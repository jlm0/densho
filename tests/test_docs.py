# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportMissingTypeStubs=false, reportOptionalMemberAccess=false
from pathlib import Path

import pytest
from linkml_runtime.utils.schemaview import SchemaView
from markdown_it import MarkdownIt

from knowledge_architecture.generated.metamodel import Concept
from knowledge_architecture.parser import ParsedNode, parse_source

REPO = Path(__file__).resolve().parents[1]
README = REPO / "README.md"
DOCS = REPO / "docs"
PAGES = sorted(DOCS.glob("*.md"))
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


@pytest.mark.parametrize("path", [README, *PAGES], ids=lambda path: path.name)
def test_each_local_link_resolves(path: Path) -> None:
    assert broken_links(path) == []


def test_the_readme_links_to_each_page() -> None:
    linked = {(REPO / link).resolve() for link in local_links(README)}
    assert PAGES
    assert set(PAGES) <= linked


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
