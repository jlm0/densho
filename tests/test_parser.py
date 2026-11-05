# pyright: reportUnknownMemberType=false
import tomllib
from pathlib import Path

import mdformat
import pytest
from markdown_it import MarkdownIt

from knowledge_architecture.generated.metamodel import (
    Concept,
    Discipline,
    Domain,
    PathPointer,
    PracticeArea,
    Root,
    Skill,
    TextPointer,
)
from knowledge_architecture.parser import ParsedNode, parse_file, parse_source, parse_tree
from knowledge_architecture.parser.__main__ import main

PATH = Path("knowledge/sample/node.md")
GOVERNED = "status: accepted\norigin: template\n"
KNOWLEDGE = f"{GOVERNED}knowledge_type: domain\n"

CONCEPT = """---
id: test-driven-development
kind: ka:Concept
title: Test-driven development
status: accepted
origin: template
knowledge_type: domain
sources: ["https://example.com/tdd"]
broader: [software-testing, quality]
pointers:
  - kind: ka:PathPointer
    target: pytest-usage
    trigger: You edit a test file.
    paths:
      - tests/**
      - src/*_test.py
  - kind: ka:TextPointer
    target: mutation-testing
    trigger: You need stronger tests.
---

## Definition

Write a failing test first.

Then write the code that passes it.

## Directives

- Write a failing test before you change behavior. ^write-test-first
  - scope: subtree
  - status: accepted
  - origin: template
  - sources: https://example.com/a
  - sources: https://example.com/b
  - also_attached_to: other-node
- Keep each test on one `behavior_name`. ^one-behavior
  - scope: node
  - status: proposed
  - origin: project

## References

See [the book](https://example.com/book).

```text
## Directives
- not a directive
```
"""

META = "  - scope: node\n  - status: accepted\n  - origin: project"


def with_directives(section: str) -> str:
    front = f"---\nid: sample\nkind: ka:Domain\ntitle: Sample\n{KNOWLEDGE}---\n"
    return f"{front}\n## Definition\n\nA sample.\n\n## Directives\n\n{section}\n"


def parsed(text: str) -> ParsedNode:
    result = parse_source(text, PATH)
    assert isinstance(result, ParsedNode), result
    return result


def concept_of(result: ParsedNode) -> Concept:
    assert isinstance(result.node, Concept)
    return result.node


def problems_of(text: str) -> list[tuple[str, int]]:
    result = parse_source(text, PATH)
    assert not isinstance(result, ParsedNode)
    return [(problem.code, problem.line) for problem in result]


def line_with(text: str, marker: str) -> int:
    for number, line in enumerate(text.split("\n"), start=1):
        if marker in line:
            return number
    message = f"No line holds {marker!r}"
    raise AssertionError(message)


def test_parses_every_part_of_a_node() -> None:
    node = parsed(CONCEPT).node
    assert isinstance(node, Concept)
    assert node.model_dump(exclude_none=True) == {
        "id": "test-driven-development",
        "kind": "ka:Concept",
        "title": "Test-driven development",
        "status": "accepted",
        "origin": "template",
        "knowledge_type": "domain",
        "sources": ["https://example.com/tdd"],
        "broader": ["software-testing", "quality"],
        "pointers": [
            {
                "kind": "ka:PathPointer",
                "target": "pytest-usage",
                "trigger": "You edit a test file.",
                "paths": ["tests/**", "src/*_test.py"],
            },
            {
                "kind": "ka:TextPointer",
                "target": "mutation-testing",
                "trigger": "You need stronger tests.",
            },
        ],
        "definition": "Write a failing test first.\n\nThen write the code that passes it.",
        "directives": [
            {
                "id": "write-test-first",
                "text": "Write a failing test before you change behavior.",
                "scope": "subtree",
                "status": "accepted",
                "origin": "template",
                "sources": ["https://example.com/a", "https://example.com/b"],
                "also_attached_to": ["other-node"],
            },
            {
                "id": "one-behavior",
                "text": "Keep each test on one `behavior_name`.",
                "scope": "node",
                "status": "proposed",
                "origin": "project",
            },
        ],
        "body": (
            "## References\n\nSee [the book](https://example.com/book).\n\n"
            "```text\n## Directives\n- not a directive\n```"
        ),
    }


def test_kind_selects_each_pointer_class() -> None:
    node = parsed(CONCEPT).node
    assert node.pointers is not None
    assert [type(pointer) for pointer in node.pointers] == [PathPointer, TextPointer]


@pytest.mark.parametrize(
    ("text", "model"),
    [
        pytest.param(
            f"---\nid: top\nkind: ka:Root\ntitle: Top\n{GOVERNED}pointers:\n"
            "  - kind: ka:AlwaysPointer\n    target: a\n    trigger: Each session.\n---\n",
            Root,
            id="root",
        ),
        pytest.param(
            f"---\nid: a\nkind: ka:Domain\ntitle: A\n{KNOWLEDGE}---\n\n## Definition\n\nA.\n",
            Domain,
            id="domain",
        ),
        pytest.param(
            f"---\nid: a\nkind: ka:Discipline\ntitle: A\n{KNOWLEDGE}broader: [b]\n---\n\n"
            "## Definition\n\nA.\n",
            Discipline,
            id="discipline",
        ),
        pytest.param(
            f"---\nid: a\nkind: ka:PracticeArea\ntitle: A\n{KNOWLEDGE}broader: [b]\n---\n\n"
            "## Definition\n\nA.\n",
            PracticeArea,
            id="practice-area",
        ),
        pytest.param(
            f"---\nid: a\nkind: ka:Skill\ntitle: A\n{KNOWLEDGE}description: Use it.\n"
            "uses: [b]\n---\n\n## Directives\n\n- Do it. ^do-it\n"
            f"{META}\n\n## Procedure\n\nStep one.\n",
            Skill,
            id="skill",
        ),
    ],
)
def test_kind_selects_each_node_class(text: str, model: type) -> None:
    assert type(parsed(text).node) is model


@pytest.mark.parametrize(
    ("field_path", "marker"),
    [
        pytest.param(("status",), "status: accepted", id="front-matter-key"),
        pytest.param(("broader", 1), "broader:", id="flow-list-item"),
        pytest.param(("pointers", 1), "kind: ka:TextPointer", id="pointer"),
        pytest.param(("pointers", 0, "trigger"), "You edit a test file", id="pointer-field"),
        pytest.param(("pointers", 0, "paths", 1), "src/*_test.py", id="block-list-item"),
        pytest.param(("definition",), "## Definition", id="definition"),
        pytest.param(("directives",), "## Directives", id="directives"),
        pytest.param(("directives", 1), "^one-behavior", id="directive"),
        pytest.param(("directives", 1, "id"), "^one-behavior", id="directive-id"),
        pytest.param(("directives", 0, "text"), "^write-test-first", id="directive-text"),
        pytest.param(("directives", 1, "status"), "status: proposed", id="directive-field"),
        pytest.param(("directives", 0, "sources"), "example.com/a", id="directive-list"),
        pytest.param(("directives", 0, "sources", 1), "example.com/b", id="directive-list-item"),
        pytest.param(("body",), "## References", id="body"),
        pytest.param(("directives", 0, "nothing", 3), "^write-test-first", id="nearest-parent"),
        pytest.param(("nothing",), "---", id="unknown-field"),
    ],
)
def test_reports_the_source_line_of_a_field(field_path: tuple[str | int, ...], marker: str) -> None:
    assert parsed(CONCEPT).line_of(field_path) == line_with(CONCEPT, marker)


@pytest.mark.parametrize(
    ("old", "new", "code", "marker"),
    [
        pytest.param("---\nid:", "id:", "front-matter", "id:", id="no-opening"),
        pytest.param("---\n\n## Def", "\n## Def", "front-matter", "---", id="no-closing"),
        pytest.param("kind: ka:Concept\n", "", "kind", "---", id="kind-missing"),
        pytest.param("ka:Concept", "ka:Thing", "kind", "ka:Thing", id="kind-unknown"),
        pytest.param("ka:Concept", "ka:Node", "kind", "ka:Node", id="kind-abstract-node"),
        pytest.param(
            "ka:Concept", "ka:KnowledgeNode", "kind", "ka:KnowledgeNode", id="kind-abstract"
        ),
        pytest.param(
            "ka:Concept", "ka:TaxonomyNode", "kind", "ka:TaxonomyNode", id="kind-abstract-taxonomy"
        ),
        pytest.param("ka:Concept", "skos:Concept", "kind", "skos:Concept", id="kind-class-uri"),
        pytest.param("ka:Concept", "ka:Directive", "kind", "ka:Directive", id="kind-directive"),
        pytest.param(
            "ka:Concept",
            "https://github.com/jlm0/knowledge-architecture/schema/Concept",
            "kind",
            "schema/Concept",
            id="kind-full-iri",
        ),
        pytest.param("ka:Concept", "[ka:Concept]", "kind", "[ka:Concept]", id="kind-list"),
        pytest.param("ka:Concept", "ka:Domain", "schema", "broader:", id="domain-with-broader"),
        pytest.param("status: accepted", "status: ok", "schema", "status: ok", id="bad-status"),
        pytest.param("origin: template", "origin: x", "schema", "origin: x", id="bad-origin"),
        pytest.param(
            "knowledge_type: domain",
            "knowledge_type: x",
            "schema",
            "knowledge_type:",
            id="bad-type",
        ),
        pytest.param("id: test-driven-development", "id: B_d", "schema", "id: B_d", id="bad-id"),
        pytest.param("status: accepted\n", "", "schema", "---", id="status-missing"),
        pytest.param("id: test-driven-development\n", "", "schema", "---", id="id-missing"),
        pytest.param("title: Test-driven development", "title:", "schema", "title:", id="no-title"),
        pytest.param(
            "title: Test-driven development",
            "title: 2024-01-02",
            "schema",
            "title:",
            id="date-title",
        ),
        pytest.param(
            "title: Test-driven development",
            "title: |\n  one\n  two",
            "schema",
            "title:",
            id="two-line-title",
        ),
        pytest.param(
            "origin: template\n", "origin: template\nx: y\n", "schema", "x: y", id="extra"
        ),
        pytest.param(
            "broader: [software-testing, quality]\n", "", "schema", "---", id="no-broader"
        ),
        pytest.param(
            "broader: [software-testing, quality]", "broader: []", "schema", "broader:", id="empty"
        ),
        pytest.param(
            "broader: [software-testing, quality]",
            "broader: [1]",
            "schema",
            "broader:",
            id="int-ref",
        ),
        pytest.param(
            "origin: template\n",
            "origin: template\ndefinition: x\n",
            "markdown-field",
            "definition: x",
            id="definition-in-front-matter",
        ),
        pytest.param(
            "origin: template\n",
            "origin: template\ndirectives: []\n",
            "markdown-field",
            "directives: []",
            id="directives-in-front-matter",
        ),
        pytest.param(
            "origin: template\n",
            "origin: template\nbody: x\n",
            "markdown-field",
            "body: x",
            id="body-in-front-matter",
        ),
        pytest.param(
            "    target: pytest-usage\n",
            "",
            "schema",
            "kind: ka:PathPointer",
            id="pointer-no-target",
        ),
        pytest.param(
            "kind: ka:PathPointer", "kind: ka:Nope", "kind", "ka:Nope", id="pointer-kind-unknown"
        ),
        pytest.param(
            "kind: ka:PathPointer", "kind: ka:Pointer", "kind", "ka:Pointer", id="pointer-abstract"
        ),
        pytest.param(
            "- kind: ka:PathPointer\n    target:",
            "- target:",
            "kind",
            "- target:",
            id="pointer-no-kind",
        ),
        pytest.param(
            "    paths:\n      - tests/**\n      - src/*_test.py\n",
            "",
            "schema",
            "kind: ka:PathPointer",
            id="path-pointer-no-paths",
        ),
        pytest.param(
            "    paths:\n      - tests/**\n      - src/*_test.py\n",
            "    paths: []\n",
            "schema",
            "paths: []",
            id="path-pointer-empty-paths",
        ),
        pytest.param(
            "kind: ka:PathPointer", "kind: ka:TextPointer", "schema", "paths:", id="text-with-paths"
        ),
        pytest.param(
            "  - kind: ka:TextPointer\n    target: mutation-testing\n"
            "    trigger: You need stronger tests.\n",
            "  - plain-text\n",
            "kind",
            "plain-text",
            id="pointer-not-mapping",
        ),
        pytest.param(
            "pointers:\n  - kind: ka:PathPointer\n    target: pytest-usage\n"
            "    trigger: You edit a test file.\n    paths:\n      - tests/**\n"
            "      - src/*_test.py\n  - kind: ka:TextPointer\n    target: mutation-testing\n"
            "    trigger: You need stronger tests.\n",
            "pointers: nothing\n",
            "schema",
            "pointers: nothing",
            id="pointers-not-list",
        ),
        pytest.param("## Definition", "## definition", "section", "## definition", id="lowercase"),
        pytest.param("## Definition", "## DEFINITION", "section", "## DEFINITION", id="uppercase"),
        pytest.param("## Definition", "## Definitions", "section", "## Definitions", id="plural"),
        pytest.param("## Definition", "## Definition:", "section", "## Definition:", id="colon"),
        pytest.param("## Definition", "# Definition", "section", "# Definition", id="h1"),
        pytest.param("## Directives", "## Directive", "section", "## Directive", id="singular"),
        pytest.param("## Directives", "## directives", "section", "## directives", id="lower"),
        pytest.param(
            "## Directives", "# Directives", "section", "# Directives", id="h1-directives"
        ),
        pytest.param(
            "Write a failing test first.\n\nThen write the code that passes it.\n",
            "",
            "schema",
            "## Definition",
            id="empty-definition",
        ),
        pytest.param(
            "## Definition\n\nWrite a failing test first.\n\n"
            "Then write the code that passes it.\n\n",
            "",
            "schema",
            "---",
            id="no-definition",
        ),
    ],
)
def test_reports_one_problem_at_its_line(old: str, new: str, code: str, marker: str) -> None:
    assert old in CONCEPT
    text = CONCEPT.replace(old, new, 1)
    assert problems_of(text) == [(code, line_with(text, marker))]


@pytest.mark.parametrize(
    ("old", "new", "heading"),
    [
        pytest.param(
            "## Directives",
            "## Definition\n\nAgain.\n\n## Directives",
            "## Definition",
            id="definition",
        ),
        pytest.param(
            "## References",
            f"## Directives\n\n- Again. ^again\n{META}\n\n## References",
            "## Directives",
            id="directives",
        ),
        pytest.param(
            "See [the book]", "## Definition\n\nLate.\n\nSee [the book]", "## Definition", id="late"
        ),
    ],
)
def test_reports_a_second_or_late_section_at_its_heading(old: str, new: str, heading: str) -> None:
    text = CONCEPT.replace(old, new, 1)
    outside_code = text.split("```text")[0].split("\n")
    last = max(i for i, line in enumerate(outside_code, start=1) if line == heading)
    assert problems_of(text) == [("section", last)]


@pytest.mark.parametrize(
    ("text", "code", "line"),
    [
        pytest.param("", "front-matter", 1, id="empty-file"),
        pytest.param("﻿---\nid: a\n---\n", "front-matter", 1, id="byte-order-mark"),
        pytest.param("---\n---\n", "front-matter", 1, id="empty-front-matter"),
        pytest.param("---\n- a\n---\n", "front-matter", 1, id="list-front-matter"),
        pytest.param("---\nplain\n---\n", "front-matter", 1, id="scalar-front-matter"),
        pytest.param("---\nid: a\nid: b\n---\n", "yaml", 3, id="duplicate-key"),
        pytest.param("---\nid: a\nb: [1\n---\n", "yaml", 3, id="syntax-error"),
        pytest.param("---\nid: a\nb: \x01c\n---\n", "control-character", 3, id="control-character"),
        pytest.param("---\nid: a\n1: b\n---\n", "yaml", 3, id="integer-key"),
        pytest.param("---\nid: a\n[x]: b\n---\n", "yaml", 3, id="list-key"),
        pytest.param("---\nid: a\nb: &x c\n---\n", "yaml-feature", 3, id="anchor"),
        pytest.param("---\nid: a\nb: *missing\n---\n", "yaml-feature", 3, id="undefined-alias"),
        pytest.param("---\nb: &x c\nd: *x\n---\n", "yaml-feature", 2, id="alias"),
        pytest.param("---\nid: a\nb: !!str c\n---\n", "yaml-feature", 3, id="scalar-tag"),
        pytest.param("---\nid: a\nb: !!map {c: d}\n---\n", "yaml-feature", 3, id="map-tag"),
        pytest.param("---\nid: a\nb: !!seq [c]\n---\n", "yaml-feature", 3, id="list-tag"),
        pytest.param("---\nid: a\nb: !x y\n---\n", "yaml-feature", 3, id="custom-tag"),
        pytest.param("---\nid: a\n<<: {c: d}\n---\n", "yaml-feature", 3, id="merge-key"),
        pytest.param("---\nid: a\n...\n---\n", "front-matter", 3, id="document-end"),
        pytest.param("---\nid: a\n... # x\n---\n", "front-matter", 3, id="document-end-comment"),
        pytest.param("---\nid: a\nb: 2024-13-45\n---\n", "yaml", 3, id="impossible-date"),
        pytest.param(f"---\nid: a\nb: {'9' * 5000}\n---\n", "yaml", 3, id="huge-integer"),
        pytest.param(f"---\nid: {'[' * 600}{']' * 600}\n---\n", "yaml", 2, id="deep-flow-list"),
        pytest.param(f"---\nid: {'[' * 600}\n---\n", "yaml", 2, id="open-flow-list"),
        pytest.param("---\nid: a\nb: \ud7ff\uffff\n---\n", "yaml", 2, id="not-printable"),
    ],
)
def test_rejects_unreadable_front_matter(text: str, code: str, line: int) -> None:
    assert problems_of(text) == [(code, line)]


@pytest.mark.parametrize(
    ("section", "code", "marker"),
    [
        pytest.param("", "directive", "## Directives", id="no-directives"),
        pytest.param("Plain text.", "directive", "Plain text", id="paragraph"),
        pytest.param("1. One ^one", "directive", "1. One", id="ordered-list"),
        pytest.param(f"### Sub\n\n- x ^a\n{META}", "directive", "### Sub", id="sub-heading"),
        pytest.param("<!-- note -->", "markdown", "<!-- note", id="html-comment"),
        pytest.param("> Quote ^a", "directive", "> Quote", id="block-quote"),
        pytest.param(f"- No id here\n{META}", "directive", "No id here", id="no-id"),
        pytest.param(f"- ^only-id\n{META}", "directive", "only-id", id="only-id"),
        pytest.param(f"- Text^glued\n{META}", "directive", "Text^glued", id="no-space-before-id"),
        pytest.param("- ", "directive", "- ", id="empty-bullet"),
        pytest.param(
            f"- - Nested ^a\n{META}", "directive", "- - Nested", id="bullet-starts-with-list"
        ),
        pytest.param("- ```\n  code\n  ```", "directive", "- ```", id="bullet-starts-with-code"),
        pytest.param(
            f"- Text ^a\n{META}\n  - `sources: a`", "directive", "`sources: a`", id="code-entry"
        ),
        pytest.param(f"- Text ^Bad_ID\n{META}", "schema", "Bad_ID", id="bad-id"),
        pytest.param(
            f"- Line one\n  line two ^a\n{META}", "directive", "Line one", id="two-line-text"
        ),
        pytest.param(f"- Do it.\n  ^a\n{META}", "directive", "Do it.", id="id-on-second-line"),
        pytest.param(f"- Do it.\t^a\n{META}", "directive", "Do it.", id="tab-before-id"),
        pytest.param(f"- Do it.{chr(0xA0)}^a\n{META}", "directive", "Do it.", id="nbsp-before-id"),
        pytest.param(f"- Do it.  ^a\n{META}", "directive", "Do it.", id="two-spaces-before-id"),
        pytest.param(
            f"- Text ^a\n{META}\n\n[note]: https://example.com",
            "directive",
            "[note]:",
            id="reference-after-list",
        ),
        pytest.param(
            f"[note]: https://example.com\n\n- Text ^a\n{META}",
            "directive",
            "[note]:",
            id="reference-before-list",
        ),
        pytest.param(
            f"- Text ^a\n\n  [note]: https://example.com\n\n{META}",
            "directive",
            "[note]:",
            id="reference-in-directive",
        ),
        pytest.param(
            f"- Text ^a\n{META}\n  - sources: a\n\n    [note]: https://example.com",
            "directive",
            "[note]:",
            id="reference-in-metadata",
        ),
        pytest.param(
            f"- Text ^a\n{META}\n  - sources: a*b*c", "directive", "sources:", id="emphasis"
        ),
        pytest.param(
            f"- Text ^a\n{META}\n  - sources: <https://a.b>", "directive", "sources:", id="autolink"
        ),
        pytest.param(
            f"- Text ^a\n{META}\n  - sources: `a` b", "directive", "sources:", id="code-then-text"
        ),
        pytest.param(
            f"- Text ^a\n{META}\n  - sources: b `a`", "directive", "sources:", id="text-then-code"
        ),
        pytest.param(f"- Text ^a\n{META}\n  - `sources`: a", "directive", "sources", id="code-key"),
        pytest.param(
            "- Text ^a\n  - status: accepted\n  - origin: project",
            "schema",
            "Text ^a",
            id="no-scope",
        ),
        pytest.param(
            "- Text ^a\n  - scope: node\n  - origin: project", "schema", "Text ^a", id="no-status"
        ),
        pytest.param(
            "- Text ^a\n  - scope: node\n  - status: accepted", "schema", "Text ^a", id="no-origin"
        ),
        pytest.param(
            "- Text ^a\n  - scope: everywhere\n  - status: accepted\n  - origin: project",
            "schema",
            "scope: everywhere",
            id="bad-scope",
        ),
        pytest.param(
            f"- Text ^a\n{META}\n  - scope: subtree",
            "directive",
            "scope: subtree",
            id="second-scope",
        ),
        pytest.param(
            f"- Text ^a\n{META}\n  - id: other", "directive", "id: other", id="metadata-id"
        ),
        pytest.param(
            f"- Text ^a\n{META}\n  - text: other", "directive", "text: other", id="metadata-text"
        ),
        pytest.param(
            f"- Text ^a\n{META}\n  - no separator", "directive", "no separator", id="no-colon"
        ),
        pytest.param(f"- Text ^a\n{META}\n  - sources:", "directive", "sources:", id="no-value"),
        pytest.param(f"- Text ^a\n{META}\n  - sources:x", "directive", "sources:x", id="no-space"),
        pytest.param(
            f"- Text ^a\n{META}\n  - sources: a\n    b", "directive", "sources: a", id="wrapped"
        ),
        pytest.param(
            f"- Text ^a\n{META}\n  - sources: a\n    - b: c", "directive", "sources: a", id="deep"
        ),
        pytest.param(
            f"- Text ^a\n{META}\n  - author: me", "schema", "author: me", id="unknown-key"
        ),
        pytest.param(
            f"- Text ^a\n{META}\n  - kind: ka:Directive", "schema", "ka:Directive", id="kind-key"
        ),
        pytest.param(
            f"- Text ^a\n\n  Extra.\n{META}", "directive", "Extra.", id="second-paragraph"
        ),
        pytest.param("- Text ^a\n\n  ```\n  code\n  ```", "directive", "```", id="code-block"),
        pytest.param(
            "- Text ^a\n  - scope: node\n\n  * status: proposed",
            "directive",
            "status: proposed",
            id="second-sub-list",
        ),
        pytest.param(
            f"- Text ^a\n{META}\n\n  Middle.\n\n  - sources: x",
            "directive",
            "Middle.",
            id="second-list",
        ),
    ],
)
def test_rejects_a_bad_directive(section: str, code: str, marker: str) -> None:
    text = with_directives(section)
    assert problems_of(text) == [(code, line_with(text, marker))]


@pytest.mark.parametrize(
    "section",
    [
        pytest.param(f"- Text. ^a\n{META}", id="tight"),
        pytest.param(f"* Text. ^a\n{META}", id="other-marker"),
        pytest.param(f"- Text. ^a\n\n{META}", id="blank-before-sub-list"),
        pytest.param(
            "- Text. ^a\n    - scope: node\n    - status: accepted\n    - origin: project",
            id="four-space-indent",
        ),
    ],
)
def test_accepts_list_variants(section: str) -> None:
    directives = parsed(with_directives(section)).node.directives
    assert directives is not None
    assert (directives[0].id, directives[0].text, directives[0].scope) == ("a", "Text.", "node")


def test_only_the_last_caret_word_is_the_id() -> None:
    directives = parsed(with_directives(f"- Use ^caret and `^code` here. ^real-id\n{META}"))
    assert directives.node.directives is not None
    assert directives.node.directives[0].id == "real-id"
    assert directives.node.directives[0].text == "Use ^caret and `^code` here."


def test_reads_directives_from_lists_with_different_markers() -> None:
    node = parsed(with_directives(f"- One. ^one\n{META}\n\n* Two. ^two\n{META}")).node
    assert node.directives is not None
    assert [directive.id for directive in node.directives] == ["one", "two"]


def test_reports_each_problem_in_line_order() -> None:
    text = CONCEPT.replace("status: accepted", "status: ok", 1)
    text = text.replace("scope: subtree", "scope: everywhere")
    text = text.replace("^one-behavior", "no-id")
    assert problems_of(text) == [
        ("schema", line_with(text, "status: ok")),
        ("schema", line_with(text, "scope: everywhere")),
        ("directive", line_with(text, "no-id")),
    ]


def test_a_directive_without_metadata_reports_each_field_at_the_bullet() -> None:
    text = with_directives("- Text ^a")
    line = line_with(text, "Text ^a")
    assert problems_of(text) == [("schema", line), ("schema", line), ("schema", line)]


def test_a_bad_pointer_does_not_add_an_error_for_the_required_list() -> None:
    text = f"---\nid: top\nkind: ka:Root\ntitle: Top\n{GOVERNED}pointers:\n  - kind: ka:Nope\n---\n"
    assert problems_of(text) == [("kind", line_with(text, "ka:Nope"))]


def test_a_root_needs_a_pointer() -> None:
    text = f"---\nid: top\nkind: ka:Root\ntitle: Top\n{GOVERNED}pointers: []\n---\n"
    assert problems_of(text) == [("schema", line_with(text, "pointers:"))]


def test_a_yaml_problem_message_has_one_line() -> None:
    result = parse_source("---\nid: a\nb: \uffff\n---\n", PATH)
    assert not isinstance(result, ParsedNode)
    assert "\n" not in result[0].message


def test_reports_each_line_with_a_control_character() -> None:
    text = "---\nid: a\x00\n---\n\nText\x7f here.\n\n- a\x85b\n"
    assert problems_of(text) == [
        ("control-character", 2),
        ("control-character", line_with(text, "Text")),
        ("control-character", line_with(text, "- a")),
    ]


def test_an_unknown_kind_stops_the_field_checks_and_keeps_format_problems() -> None:
    text = CONCEPT.replace("ka:Concept", "ka:Thing").replace("status: accepted", "status: ok", 1)
    text = text.replace("^one-behavior", "no-id")
    assert problems_of(text) == [
        ("kind", line_with(text, "ka:Thing")),
        ("directive", line_with(text, "no-id")),
    ]


def test_a_problem_names_the_file_line_code_and_field() -> None:
    result = parse_source(CONCEPT.replace("scope: subtree", "scope: x"), PATH)
    assert not isinstance(result, ParsedNode)
    number = line_with(CONCEPT, "scope: subtree")
    assert str(result[0]).startswith(f"{PATH}:{number}: schema: directives[0].scope: ")


@pytest.mark.parametrize(
    ("kind", "extra"),
    [
        pytest.param(
            "ka:Root",
            "pointers:\n  - kind: ka:TextPointer\n    target: a\n    trigger: B.\n",
            id="root",
        ),
        pytest.param("ka:Skill", "knowledge_type: domain\ndescription: Use it.\n", id="skill"),
    ],
)
def test_a_node_without_a_definition_field_rejects_the_section(kind: str, extra: str) -> None:
    text = f"---\nid: a\nkind: {kind}\ntitle: A\n{GOVERNED}{extra}---\n\n## Definition\n\nA.\n"
    assert problems_of(text) == [("schema", line_with(text, "## Definition"))]


def test_a_wrong_level_heading_is_reported_with_the_missing_definition() -> None:
    text = CONCEPT.replace("## Definition", "### Definition", 1)
    assert ("section", line_with(text, "### Definition")) in problems_of(text)


def test_prose_before_the_sections_reports_each_section() -> None:
    text = CONCEPT.replace("## Definition", "Intro.\n\n## Definition", 1)
    assert problems_of(text) == [
        ("section", line_with(text, "## Definition")),
        ("section", line_with(text, "## Directives")),
    ]


def test_each_directive_in_a_second_section_is_still_checked() -> None:
    text = CONCEPT.replace("scope: subtree", "scope: everywhere")
    text = text.replace(
        "## References", f"## Directives\n\n- Bad. ^Bad_ID\n{META}\n\n## References", 1
    )
    assert problems_of(text) == [
        ("schema", line_with(text, "scope: everywhere")),
        ("section", line_with(text, "- Bad.") - 2),
        ("schema", line_with(text, "- Bad.")),
    ]


def test_a_quoted_merge_key_is_plain_text() -> None:
    text = CONCEPT.replace("title: Test-driven development", 'title: "<<"', 1)
    assert parsed(text).node.title == "<<"


def test_directives_before_the_definition_are_reported() -> None:
    definition = "## Definition\n\nA sample.\n\n"
    directives = f"## Directives\n\n- Do. ^do\n{META}\n\n"
    text = f"---\nid: a\nkind: ka:Domain\ntitle: A\n{KNOWLEDGE}---\n\n{directives}{definition}"
    assert problems_of(text) == [("section", line_with(text, "## Definition"))]


def test_other_text_without_sections_is_the_body() -> None:
    text = (
        f"---\nid: top\nkind: ka:Root\ntitle: Top\n{GOVERNED}pointers:\n"
        "  - kind: ka:TextPointer\n    target: a\n    trigger: B.\n---\n\n\nPlain prose.\n\nMore.\n"
    )
    result = parsed(text)
    assert result.node.body == "Plain prose.\n\nMore."
    assert result.line_of(("body",)) == line_with(text, "Plain prose")


def test_a_section_name_in_a_closed_code_fence_is_not_a_section() -> None:
    text = CONCEPT.replace(
        "Then write the code that passes it.", "```text\n## Definition\n## Directives\n```"
    )
    result = parsed(text)
    assert result.node.directives is not None
    assert len(result.node.directives) == len(parsed(CONCEPT).node.directives or [])
    assert "```text\n## Definition" in concept_of(result).definition


@pytest.mark.parametrize(
    "heading",
    [
        "##Directives",
        "## **Directives**",
        "## Directive.",
        "## Directives <!-- x -->",
        "- ## Directives",
        "> ## Directives",
        "    ## Directives",
        "**Directives**",
        "Directives:",
        "### Directives",
    ],
)
def test_a_hidden_section_name_is_reported(heading: str) -> None:
    text = CONCEPT.replace("## Directives\n\n", f"{heading}\n\n", 1)
    assert ("section", line_with(text, heading)) in problems_of(text)


@pytest.mark.parametrize(
    ("before", "marker"),
    [
        pytest.param("<!-- todo", "<!-- todo", id="open-comment"),
        pytest.param("<!-- closed -->", "<!-- closed", id="closed-comment"),
        pytest.param("<div>", "<div>", id="html-block"),
        pytest.param("Prose <!-- hidden --> here.", "Prose", id="inline-comment"),
    ],
)
def test_markdown_that_can_hide_text_is_reported(before: str, marker: str) -> None:
    text = CONCEPT.replace("## Directives", f"{before}\n\n## Directives", 1)
    assert ("markdown", line_with(text, marker)) in problems_of(text)


@pytest.mark.parametrize(
    ("fence", "marker"),
    [
        pytest.param("```text\nopen fence", "```text", id="backtick-fence"),
        pytest.param("~~~\nopen fence", "~~~", id="tilde-fence"),
        pytest.param("````\n```", "````", id="short-closer"),
        pytest.param("```\n    ```", "```", id="indented-closer"),
        pytest.param("```\ncode\n``` x", "```", id="closer-with-text"),
        pytest.param("```\n~~~", "```", id="other-marker-closer"),
        pytest.param("```", "```", id="only-opener"),
    ],
)
def test_an_open_fence_is_reported(fence: str, marker: str) -> None:
    text = f"{with_directives(f'- Text ^a\n{META}')}\n## Notes\n\n{fence}\n"
    assert problems_of(text) == [("markdown", line_with(text, marker))]


def test_a_fence_that_hides_the_directives_section_is_reported() -> None:
    text = CONCEPT.replace("## Directives", "```text\nopen fence\n\n## Directives", 1)
    assert ("markdown", line_with(text, "## Directives")) in problems_of(text)


def test_a_fence_that_hides_the_definition_section_is_reported() -> None:
    text = f"---\nid: a\nkind: ka:Skill\ntitle: A\n{KNOWLEDGE}description: B.\nuses: [c]\n---\n\n"
    text += "```\n## Definition\n\nHidden.\n```\n"
    assert problems_of(text) == [("markdown", line_with(text, "## Definition"))]


def test_a_fence_in_a_quote_is_not_checked_for_section_names() -> None:
    parsed(CONCEPT.replace("## Directives", "> ```\n> code\n\n## Directives", 1))


def test_a_quoted_fence_can_show_a_section_the_file_does_not_have() -> None:
    text = f"---\nid: a\nkind: ka:Skill\ntitle: A\n{KNOWLEDGE}description: B.\nuses: [c]\n---\n\n"
    parsed(f"{text}> ```\n> ## Definition\n> ```\n")


def test_html_tags_in_prose_are_accepted() -> None:
    parsed(CONCEPT.replace("See [the book]", "Use List<String> and <b>bold</b>. See [the book]", 1))


def test_a_section_name_on_a_later_paragraph_line_is_reported_at_that_line() -> None:
    text = CONCEPT.replace("See [the book]", "First line\nDirectives:\n\nSee [the book]", 1)
    assert problems_of(text) == [("section", line_with(text, "Directives:"))]


def test_a_closed_fence_with_a_longer_closer_is_accepted() -> None:
    parsed(CONCEPT.replace("## Directives", "```\ncode\n`````\n\n## Directives", 1))


def test_a_fence_in_a_list_item_can_end_with_the_item() -> None:
    parsed(CONCEPT.replace("See [the book]", "- item\n  ```\n  code\n\nSee [the book]", 1))


def test_deep_nesting_is_reported() -> None:
    deep = "\n".join(f"{'  ' * depth}- level" for depth in range(10))
    text = CONCEPT.replace("## Directives", f"{deep}\n\n## Directives", 1)
    assert problems_of(text).count(("markdown", line_with(text, "- level") + 7)) == 1


def test_moderate_nesting_is_accepted() -> None:
    nested = "\n".join(f"{'  ' * depth}- level" for depth in range(4))
    parsed(CONCEPT.replace("## References", f"## References\n\n{nested}", 1))


def test_the_body_holds_every_other_section() -> None:
    text = CONCEPT.replace("## References", "## Procedure\n\nStep one.\n\n## References", 1)
    body = parsed(text).node.body or ""
    assert body.startswith("## Procedure\n\nStep one.\n\n## References")
    assert body.endswith("- not a directive\n```")


def test_a_heading_in_a_quote_does_not_split_a_section() -> None:
    text = CONCEPT.replace("Then write", "> ## Note\n\nThen write", 1)
    assert "> ## Note\n\nThen write" in concept_of(parsed(text)).definition


def test_a_rule_line_in_the_body_does_not_close_anything() -> None:
    result = parsed(CONCEPT.replace("## References", "## References\n\n---\n\nAfter."))
    assert "---\n\nAfter." in (result.node.body or "")


def test_an_underline_heading_is_a_section() -> None:
    text = CONCEPT.replace("## Definition\n\n", "Definition\n---\n\n", 1)
    result = parsed(text)
    assert concept_of(result).definition.startswith("Write a failing test first.")
    assert result.line_of(("definition",)) == line_with(text, "Definition")


def test_lines_stay_correct_after_unicode_line_separators_in_the_front_matter() -> None:
    text = CONCEPT.replace("title: Test-driven development", 'title: "a\\u2028b\\x85c"', 1)
    text = text.replace("status: accepted", "status: ok", 1)
    assert problems_of(text) == [
        ("schema", line_with(text, "title:")),
        ("schema", line_with(text, "status: ok")),
    ]
    raw = CONCEPT.replace("title: Test-driven development", 'title: "a' + chr(0x2028) + 'b"', 1)
    raw = raw.replace("status: accepted", "status: ok", 1)
    assert problems_of(raw) == [
        ("schema", line_with(raw, "title:")),
        ("schema", line_with(raw, "status: ok")),
    ]


def test_lines_stay_correct_after_unicode_line_separators_in_the_body() -> None:
    text = CONCEPT.replace("Then write", f"Then{chr(0x2028)} write{chr(0x2029)}")
    assert parsed(text).line_of(("directives", 1)) == line_with(text, "^one-behavior")


def test_comments_in_front_matter_are_ignored() -> None:
    text = CONCEPT.replace("origin: template\n", "# note\norigin: template # trailing\n", 1)
    result = parsed(text)
    assert result.line_of(("origin",)) == line_with(text, "origin: template")


REPO = Path(__file__).resolve().parents[1]
OPTIONS = tomllib.loads((REPO / ".mdformat.toml").read_text(encoding="utf-8"))
EXTENSIONS = ("gfm", "tables", "frontmatter")


def formatted(text: str) -> str:
    return mdformat.text(text, extensions=EXTENSIONS, options=OPTIONS)


def assert_same_html(first: str, second: str) -> None:
    assert first.split() == second.split()


def test_mdformat_leaves_the_format_unchanged() -> None:
    assert formatted(CONCEPT) == CONCEPT


def test_mdformat_does_not_change_the_parsed_node() -> None:
    front, section, rest = CONCEPT.partition("## Directives")
    bullets = rest.replace("- Write a failing", "* Write a failing").replace("  - ", "    - ")
    text = f"{front}{section}{bullets}"
    assert formatted(text) != text
    assert parsed(formatted(text)).node == parsed(text).node


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        pytest.param("tests/**", "tests/**", id="stars"),
        pytest.param("src/*_test.py", "src/*_test.py", id="star-underscore"),
        pytest.param("_private/x.md", "_private/x.md", id="leading-underscore"),
        pytest.param("a  b", "a b", id="two-spaces"),
        pytest.param("a &amp; b", "a & b", id="entity"),
        pytest.param("a & b", "a & b", id="ampersand"),
        pytest.param("[1] Book, p. 2", "[1] Book, p. 2", id="brackets"),
        pytest.param(
            "https://example.com/a_b?c=d&e=f", "https://example.com/a_b?c=d&e=f", id="url"
        ),
        pytest.param("`tests/**/x*`", "tests/**/x*", id="code-span"),
        pytest.param("`a  b`", "a  b", id="code-span-spaces"),
    ],
)
def test_mdformat_does_not_change_a_metadata_value(value: str, expected: str) -> None:
    text = with_directives(f"- Text ^a\n{META}\n  - sources: {value}")
    node = parsed(text).node
    assert node.directives is not None
    assert node.directives[0].sources == [expected]
    after = parsed(formatted(text)).node
    assert after.directives is not None
    assert after.directives[0].sources == [expected]


@pytest.mark.parametrize(
    "words",
    [
        "Match src/*_test.py and tests/** here.",
        "Keep _private names and `code_spans` as they are.",
        "Use __bold__ and _emphasis_ with care.",
        "Use a  b &amp; c [d] here.",
    ],
)
def test_mdformat_does_not_change_how_directive_text_renders(words: str) -> None:
    text = with_directives(f"- {words} ^a\n{META}")
    node = parsed(text).node
    after = parsed(formatted(text)).node
    assert node.directives is not None
    assert after.directives is not None
    renderer = MarkdownIt("commonmark")
    assert_same_html(
        renderer.renderInline(after.directives[0].text),
        renderer.renderInline(node.directives[0].text),
    )
    assert parsed(formatted(formatted(text))).node == after


def test_parse_file_keeps_lines_with_windows_line_endings(tmp_path: Path) -> None:
    path = tmp_path / "node.md"
    path.write_bytes(CONCEPT.replace("\n", "\r\n").encode())
    result = parse_file(path)
    assert isinstance(result, ParsedNode)
    assert result.line_of(("directives", 1)) == line_with(CONCEPT, "^one-behavior")
    assert concept_of(result).definition == concept_of(parsed(CONCEPT)).definition


def test_parse_file_rejects_invalid_utf8(tmp_path: Path) -> None:
    path = tmp_path / "node.md"
    path.write_bytes(b"---\nid: \xff\n---\n")
    result = parse_file(path)
    assert not isinstance(result, ParsedNode)
    assert [(problem.path, problem.code) for problem in result] == [(path, "encoding")]


def test_parse_file_reports_a_missing_file(tmp_path: Path) -> None:
    result = parse_file(tmp_path / "node.md")
    assert not isinstance(result, ParsedNode)
    assert [problem.code for problem in result] == ["read"]


def write_node(folder: Path, text: str = CONCEPT) -> Path:
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "node.md"
    path.write_text(text, encoding="utf-8")
    return path


def test_parse_tree_finds_nested_nodes_in_a_fixed_order(tmp_path: Path) -> None:
    second = write_node(tmp_path / "b")
    first = write_node(tmp_path / "a" / "deep")
    nodes, problems = parse_tree([tmp_path])
    assert problems == []
    assert [node.path for node in nodes] == [first, second]


def test_parse_tree_sorts_what_the_folder_walk_returns(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    first, second = write_node(tmp_path / "a"), write_node(tmp_path / "b")

    def reverse_walk(root: Path, **_: object) -> list[tuple[Path, list[str], list[str]]]:
        return [(root / "b", [], ["node.md"]), (root / "a", [], ["node.md"])]

    monkeypatch.setattr(Path, "walk", reverse_walk)
    nodes, _ = parse_tree([tmp_path])
    assert [node.path for node in nodes] == [first, second]


def test_parse_tree_returns_good_nodes_and_problems(tmp_path: Path) -> None:
    good = write_node(tmp_path / "a")
    bad = write_node(tmp_path / "b", CONCEPT.replace("status: accepted", "status: ok", 1))
    nodes, problems = parse_tree([tmp_path])
    assert [node.path for node in nodes] == [good]
    assert [(problem.path, problem.code) for problem in problems] == [(bad, "schema")]


@pytest.mark.parametrize(
    "name", ["Node.md", "NODE.MD", "nodes.md", "README.md", "notes.markdown", "a.mdown", "a.mkd"]
)
def test_parse_tree_rejects_other_markdown_files(tmp_path: Path, name: str) -> None:
    (tmp_path / "a").mkdir()
    path = tmp_path / "a" / name
    path.write_text(CONCEPT, encoding="utf-8")
    nodes, problems = parse_tree([tmp_path])
    assert nodes == []
    assert [(problem.path, problem.code) for problem in problems] == [(path, "file-name")]


def test_parse_tree_ignores_other_files(tmp_path: Path) -> None:
    (tmp_path / ".gitkeep").write_text("", encoding="utf-8")
    (tmp_path / "image.png").write_bytes(b"x")
    assert parse_tree([tmp_path]) == ([], [])


def test_parse_tree_rejects_a_file_link(tmp_path: Path) -> None:
    target = write_node(tmp_path / "real")
    (tmp_path / "linked").mkdir()
    link = tmp_path / "linked" / "node.md"
    link.symlink_to(target)
    nodes, problems = parse_tree([tmp_path])
    assert [node.path for node in nodes] == [target]
    assert [(problem.path, problem.code) for problem in problems] == [(link, "symlink")]


def test_parse_tree_rejects_a_dangling_link(tmp_path: Path) -> None:
    link = tmp_path / "node.md"
    link.symlink_to(tmp_path / "missing.md")
    nodes, problems = parse_tree([tmp_path])
    assert nodes == []
    assert [(problem.path, problem.code) for problem in problems] == [(link, "symlink")]


def test_parse_tree_rejects_a_folder_link(tmp_path: Path) -> None:
    target = write_node(tmp_path / "outside" / "real").parent
    root = tmp_path / "root"
    root.mkdir()
    link = root / "linked"
    link.symlink_to(target, target_is_directory=True)
    nodes, problems = parse_tree([root])
    assert nodes == []
    assert [(problem.path, problem.code) for problem in problems] == [(link, "symlink")]


def test_parse_tree_reports_an_unreadable_folder(tmp_path: Path) -> None:
    locked = tmp_path / "locked"
    locked.mkdir()
    locked.chmod(0o000)
    try:
        _, problems = parse_tree([tmp_path])
    finally:
        locked.chmod(0o700)
    assert [problem.code for problem in problems] == ["read"]


def test_parse_tree_ignores_a_folder_with_the_node_file_name(tmp_path: Path) -> None:
    (tmp_path / "node.md").mkdir()
    assert parse_tree([tmp_path]) == ([], [])


def test_parse_tree_reports_a_missing_folder(tmp_path: Path) -> None:
    _, problems = parse_tree([tmp_path / "missing"])
    assert [problem.code for problem in problems] == ["folder"]


def test_main_needs_a_folder(capsys: pytest.CaptureFixture[str]) -> None:
    assert main([]) > 1
    assert "Usage" in capsys.readouterr().err


def test_main_passes_on_valid_nodes(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    write_node(tmp_path / "a")
    assert main([str(tmp_path)]) == 0
    assert capsys.readouterr().out == "1 nodes parsed, 0 problems\n"


def test_main_fails_and_prints_each_location(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    text = CONCEPT.replace("status: accepted", "status: ok", 1)
    path = write_node(tmp_path / "a", text)
    assert main([str(tmp_path)]) == 1
    out = capsys.readouterr().out
    assert f"{path}:{line_with(text, 'status: ok')}: schema: status: " in out
    assert out.endswith("0 nodes parsed, 1 problems\n")


def test_main_fails_on_a_missing_folder(tmp_path: Path) -> None:
    assert main([str(tmp_path / "missing")]) == 1
