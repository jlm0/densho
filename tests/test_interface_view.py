import base64
import hashlib
import json
import os
import re
import shutil
import subprocess
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit

import pytest
from typer.testing import CliRunner

from engine.cli import app
from engine.compiler import compile_tree
from engine.governance import pending_entities
from engine.interface import (
    REACH_LISTED,
    VIEW_FOLDER,
    is_safe_link,
    render_block,
    render_inline,
    render_site,
    write_view,
)
from engine.interface.tree import children_by_broader, subtree_ids, tree_rows
from engine.parser import ParsedNode, parse_source
from engine.parser.generated import MARKER, is_generated

REPO = Path(__file__).resolve().parents[1]
RUNNER = CliRunner()
GIT = shutil.which("git") or "git"
PWNED = "window.pwned=1"
PAYLOADS = (
    f"<script>{PWNED}</script>",
    f"<img src=x onerror={PWNED}>",
    f"<svg onload={PWNED}>",
    f'"><script>{PWNED}</script>',
    f"'><iframe src=javascript:{PWNED}>",
    f"<a href=javascript:{PWNED}>a</a>",
    f"[a](javascript:{PWNED})",
    f"[a](JaVaScRiPt:{PWNED})",
    f"[a](javascript&colon;{PWNED})",
    f"[a](java&#9;script:{PWNED})",
    f"[a](<java\tscript:{PWNED}>)",
    "[a](data:text/html;base64,PHNjcmlwdD4=)",
    "[a](data:image/png;base64,AAAA)",
    "[a](vbscript:msgbox)",
    "[a](file:///etc/passwd)",
    "[a](//evil.example/x)",
    "[a](\\\\evil.example/x)",
    "[a](../../../../etc/passwd)",
    f"<javascript:{PWNED}>",
    "![a](http://evil.example/p.png)",
    '[a](http://ok.example "x\\"><script>window.pwned=1</script>")',
    '[a](http://ok.example/"onmouseover="window.pwned=1)',
    "{{ 7 * 7 }} {% include 'x' %}",
)
FORBIDDEN_TAGS = frozenset(
    {
        "applet",
        "audio",
        "base",
        "button",
        "embed",
        "form",
        "frame",
        "iframe",
        "img",
        "input",
        "link",
        "math",
        "object",
        "script",
        "source",
        "svg",
        "textarea",
        "track",
        "video",
    }
)
FORBIDDEN_ATTRIBUTES = frozenset({"src", "srcdoc", "srcset", "style", "formaction", "background"})
INDEX_PAGE = PurePosixPath("index.html")
EXPECTED_META = 3
EXPECTED_STYLE = 1
SKILL_DESCRIPTION = "Review a sample. Use when a sample needs a review."


def node(
    node_id: str,
    kind: str = "ka:Domain",
    *,
    front: str = "",
    rules: str = "",
    body: str = "",
    **fields: str,
) -> str:
    extra = "knowledge_type: domain\n" if kind != "ka:Root" else ""
    title = fields.get("title", node_id.title())
    status = fields.get("status", "proposed")
    text = f"---\nid: {node_id}\nkind: {kind}\ntitle: {title}\n"
    text += f"status: {status}\norigin: template\n{extra}{front}---\n"
    if kind not in {"ka:Root", "ka:Skill"}:
        text += f"\n## Definition\n\nThe meaning of {node_id}.\n"
    if rules:
        text += f"\n## Directives\n\n{rules}"
    return f"{text}\n{body}" if body else text


def rule(
    directive_id: str,
    text: str = "Run the check.",
    *,
    status: str = "proposed",
    scope: str = "subtree",
    extra: str = "",
) -> str:
    return (
        f"- {text} ^{directive_id}\n  - scope: {scope}\n  - status: {status}\n"
        f"  - origin: template\n{extra}"
    )


def text_pointer(target: str) -> str:
    return f"  - kind: ka:TextPointer\n    target: {target}\n    trigger: You need {target}.\n"


def pointers(*targets: str) -> str:
    return "pointers:\n" + "".join(text_pointer(target) for target in targets)


SAMPLE = {
    "knowledge/node.md": node(
        "root",
        "ka:Root",
        title="The root",
        front=pointers("alpha", "gamma"),
        body="## Architecture\n\nA fact about the root.\n",
    ),
    "knowledge/nodes/alpha/node.md": node(
        "alpha",
        front=pointers("beta", "review"),
        rules=rule("keep") + rule("wait", "Run the other check."),
    ),
    "knowledge/nodes/alpha/beta/node.md": node(
        "beta",
        "ka:Concept",
        front=(
            "broader: [alpha]\nexceptions:\n"
            "  - directive: keep\n    reason: A reason for beta.\n    status: proposed\n"
        ),
        rules=rule("bound", "Run the third check.", scope="node"),
    ),
    "knowledge/nodes/gamma/node.md": node("gamma"),
    "knowledge/skills/review/node.md": node(
        "review",
        "ka:Skill",
        front=(
            "description: Review a sample. Use when a sample needs a review.\nuses: [beta]\n"
            + pointers("beta")
        ),
        body="## Procedure\n\n1. Read each directive.\n",
    ),
}


def parsed(sources: dict[str, str]) -> list[ParsedNode]:
    items: list[ParsedNode] = []
    for relative, text in sources.items():
        result = parse_source(text, Path(relative))
        assert isinstance(result, ParsedNode), (relative, result)
        items.append(result)
    return items


def site_of(sources: dict[str, str]) -> dict[str, str]:
    files = render_site(parsed(sources), Path())
    return {path.as_posix(): data.decode("utf-8") for path, data in files.items()}


def write_tree(repository: Path, sources: dict[str, str] | None = None) -> None:
    def no_branch_files(folder: str, names: list[str]) -> list[str]:
        return [name for name in names if Path(folder).name == "branches" and name != ".gitkeep"]

    shutil.copytree(
        REPO / "knowledge/governance/language",
        repository / "knowledge/governance/language",
        ignore=no_branch_files,
    )
    for relative, text in (SAMPLE if sources is None else sources).items():
        path = repository / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


def view_files(repository: Path) -> dict[str, bytes]:
    folder = repository / VIEW_FOLDER
    return {
        path.relative_to(folder).as_posix(): path.read_bytes()
        for path in folder.rglob("*")
        if path.is_file()
    }


class _Page(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.tags: list[tuple[str, dict[str, str]]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.tags.append((tag, {name: value or "" for name, value in attrs}))


def _href_finding(href: str, page: PurePosixPath, pages: set[PurePosixPath] | None) -> str | None:
    cleaned = re.sub(r"[\x00-\x20\x7f-\x9f]", "", href)
    parts = urlsplit(cleaned)
    if parts.scheme:
        return None if parts.scheme.lower() in {"http", "https", "mailto"} else f"href {href!r}"
    if not cleaned or cleaned.startswith("#"):
        return None
    if cleaned.startswith(("/", "\\")):
        return f"href {href!r}"
    if pages is None:
        return None
    target = PurePosixPath(os.path.normpath(page.parent / unquote(parts.path))).as_posix()
    return None if PurePosixPath(target) in pages else f"dead href {href!r}"


def unsafe_markup(
    html: str,
    page: PurePosixPath = INDEX_PAGE,
    pages: set[PurePosixPath] | None = None,
) -> list[str]:
    parser = _Page()
    parser.feed(html)
    findings: list[str] = []
    meta = [attrs for tag, attrs in parser.tags if tag == "meta"]
    styles = [tag for tag, _ in parser.tags if tag == "style"]
    if len(meta) != EXPECTED_META:
        findings.append(f"{len(meta)} meta tags")
    if len(styles) != EXPECTED_STYLE:
        findings.append(f"{len(styles)} style tags")
    for tag, attrs in parser.tags:
        if tag in FORBIDDEN_TAGS:
            findings.append(f"tag {tag}")
        for name, value in attrs.items():
            if name.startswith("on") or name in FORBIDDEN_ATTRIBUTES:
                findings.append(f"attribute {name}")
            if name == "href":
                finding = _href_finding(value, page, pages)
                if finding:
                    findings.append(finding)
    return findings


GOOD_HEAD = '<meta charset="utf-8"><meta name="v"><meta http-equiv="c"><style></style>'


@pytest.mark.parametrize(
    ("markup", "expected"),
    [
        ("<script>x</script>", "tag script"),
        ("<img src=x>", "tag img"),
        ("<iframe></iframe>", "tag iframe"),
        ("<svg></svg>", "tag svg"),
        ("<b onclick=x>a</b>", "attribute onclick"),
        ('<a style="x">a</a>', "attribute style"),
        ('<a href="javascript:x">a</a>', "href 'javascript:x'"),
        ('<a href="java&#9;script:x">a</a>', "href 'java\\tscript:x'"),
        ('<a href=" JAVASCRIPT:x">a</a>', "href ' JAVASCRIPT:x'"),
        ('<a href="data:text/html,x">a</a>', "href 'data:text/html,x'"),
        ('<a href="file:///etc/passwd">a</a>', "href 'file:///etc/passwd'"),
        ('<a href="//evil.example/x">a</a>', "href '//evil.example/x'"),
        ('<a href="\\\\evil.example/x">a</a>', "href '\\\\\\\\evil.example/x'"),
        ("<meta http-equiv=refresh>", "4 meta tags"),
        ("<style>x</style>", "2 style tags"),
    ],
)
def test_the_markup_check_finds_each_unsafe_form(markup: str, expected: str) -> None:
    assert expected in unsafe_markup(GOOD_HEAD + markup)


def test_the_markup_check_finds_a_dead_link() -> None:
    pages = {PurePosixPath("index.html")}
    assert unsafe_markup(GOOD_HEAD + '<a href="nodes/x.html">a</a>', pages=pages) == [
        "dead href 'nodes/x.html'"
    ]


def test_the_markup_check_passes_a_good_page() -> None:
    pages = {PurePosixPath("index.html"), PurePosixPath("nodes/a.html")}
    markup = '<a href="nodes/a.html#b">a</a><a href="https://example.com">b</a><a href="#c">c</a>'
    assert unsafe_markup(GOOD_HEAD + markup, pages=pages) == []


def hostile_tree(payload: str) -> dict[str, str]:
    flat = payload.replace("\t", " ")
    quoted = json.dumps(flat)
    code = flat.replace("`", "")
    return {
        "knowledge/node.md": node(
            "root",
            "ka:Root",
            title=quoted,
            front=(
                "pointers:\n  - kind: ka:TextPointer\n    target: alpha\n"
                f"    trigger: {quoted}\n"
                "  - kind: ka:PathPointer\n    target: review\n"
                f"    trigger: {quoted}\n    paths:\n      - {quoted}\n"
            ),
            body=f"Intro {payload} outro.\n",
        ),
        "knowledge/nodes/alpha/node.md": (
            f"---\nid: alpha\nkind: ka:Domain\ntitle: {quoted}\nstatus: proposed\n"
            f"origin: template\nknowledge_type: domain\nsources:\n  - {quoted}\n---\n\n"
            f"## Definition\n\nIntro {payload} outro.\n\n## Directives\n\n"
            + rule(
                "hostile-rule",
                f"Intro {flat} outro.",
                extra=f"  - sources: `{code}`\n",
            )
            + f"\n## Notes\n\nIntro {payload} outro.\n"
        ),
        "knowledge/nodes/alpha/beta/node.md": node(
            "beta",
            "ka:Concept",
            title=quoted,
            front=(
                "broader: [alpha]\nexceptions:\n  - directive: hostile-rule\n"
                f"    reason: {quoted}\n    status: proposed\n"
            ),
        ),
        "knowledge/skills/review/node.md": node(
            "review",
            "ka:Skill",
            title=quoted,
            front=f"description: {quoted}\nuses: [beta]\n",
            body=f"Intro {payload} outro.\n",
        ),
    }


@pytest.mark.parametrize("payload", PAYLOADS)
def test_each_page_stays_safe_under_a_hostile_value(payload: str) -> None:
    site = site_of(hostile_tree(payload))
    pages = {PurePosixPath(name) for name in site}
    assert len(pages) == len(hostile_tree(payload)) + 2
    for name, html in site.items():
        assert unsafe_markup(html, PurePosixPath(name), pages) == [], name


def test_a_hostile_value_appears_as_text() -> None:
    site = site_of(hostile_tree(PAYLOADS[0]))
    escaped = f"&lt;script&gt;{PWNED}&lt;/script&gt;"
    page = site["nodes/alpha.html"]
    assert page.count(escaped) >= len(("title", "heading", "definition", "text", "source", "body"))
    assert f"<script>{PWNED}" not in "".join(site.values())
    assert escaped in site["nodes/beta.html"]
    assert escaped in site["nodes/review.html"]
    assert escaped in site["review.html"]
    assert escaped in site["index.html"]


def test_a_hostile_value_that_passes_each_check_stays_safe(tmp_path: Path) -> None:
    image = f"<img src=x onerror={PWNED}>"
    sources = {
        "knowledge/node.md": node("root", "ka:Root", front=pointers("alpha")),
        "knowledge/nodes/alpha/node.md": (
            f"---\nid: alpha\nkind: ka:Domain\ntitle: {json.dumps(image)}\nstatus: proposed\n"
            "origin: template\nknowledge_type: domain\n---\n\n"
            f"## Definition\n\nA {image} value.\n\n"
            f"## Notes\n\nA [link](javascript:{PWNED}) and {image} here.\n"
        ),
    }
    write_tree(tmp_path, sources)
    result = RUNNER.invoke(app, ["view", str(tmp_path)])
    assert result.exit_code == 0, result.output
    files = view_files(tmp_path)
    pages = {PurePosixPath(name) for name in files}
    for name, data in files.items():
        assert unsafe_markup(data.decode("utf-8"), PurePosixPath(name), pages) == [], name
    assert b"&lt;img src=x onerror=" in files["nodes/alpha.html"]
    assert b"[link](javascript:" in files["nodes/alpha.html"]


def test_a_template_expression_in_a_value_stays_as_text() -> None:
    site = site_of(hostile_tree("{{ 7 * 7 }}"))
    assert "{{ 7 * 7 }}" in site["nodes/alpha.html"]
    assert ">49<" not in site["nodes/alpha.html"]


def test_each_field_reaches_the_page_that_the_hostile_test_reads() -> None:
    site = site_of(hostile_tree("PLANTED"))
    assert site["nodes/root.html"].count("PLANTED") >= len(("title", "trigger", "path", "body"))
    alpha = site["nodes/alpha.html"]
    assert "source: <code>PLANTED" in alpha
    assert "reference: <code>PLANTED" in alpha
    assert "does not apply here. PLANTED" in site["nodes/beta.html"]
    assert "<code>PLANTED</code>" in site["nodes/root.html"]
    assert "PLANTED" in site["nodes/review.html"]


def test_each_hostile_payload_changes_the_page() -> None:
    plain = site_of(hostile_tree("plain"))["nodes/alpha.html"]
    assert "plain" in plain
    assert all(site_of(hostile_tree(item))["nodes/alpha.html"] != plain for item in PAYLOADS)


@pytest.mark.parametrize(
    "url",
    [
        "http://example.com",
        "https://example.com/a?b=c#d",
        "HTTPS://EXAMPLE.COM",
        "mailto:a@example.com",
    ],
)
def test_a_safe_link_passes(url: str) -> None:
    assert is_safe_link(url)


@pytest.mark.parametrize(
    "url",
    [
        "",
        "relative/path.md",
        "../up.md",
        "/root/path",
        "//evil.example/x",
        "\\\\evil.example/x",
        "#anchor",
        "javascript:alert(1)",
        "JAVASCRIPT:alert(1)",
        " javascript:alert(1)",
        "\tjavascript:alert(1)",
        "java\tscript:alert(1)",
        "java\nscript:alert(1)",
        "java%09script:alert(1)",
        "\x01javascript:alert(1)",
        "vbscript:x",
        "data:text/html,x",
        "data:image/png;base64,AAAA",
        "file:///etc/passwd",
        "blob:x",
        "ftp://example.com",
        "tel:123",
        " https://example.com",
        "//evil.example/http:x",
        "relative/https:y",
        "1https://example.com",
    ],
)
def test_an_unsafe_link_fails(url: str) -> None:
    assert not is_safe_link(url)


def test_a_rejected_link_stays_as_its_source_text() -> None:
    assert "<a " not in render_inline("See [a](javascript:x).")
    assert "[a](javascript:x)" in render_inline("See [a](javascript:x).")
    assert "<a " not in render_block("See [a][r].\n\n[r]: javascript:x\n")
    assert "<a " not in render_inline("See <javascript:x>.")
    assert "<a " not in render_inline("See [a](relative/page.md).")


def test_an_autolink_and_a_reference_link_with_a_safe_scheme_render() -> None:
    assert '<a href="https://example.com">' in render_inline("See <https://example.com>.")
    assert '<a href="https://example.com">a</a>' in render_block(
        "See [a][r].\n\n[r]: https://example.com\n"
    )


def test_markdown_renders_inline_and_block_forms() -> None:
    assert render_inline("Run `pytest` now.") == "Run <code>pytest</code> now."
    assert "<strong>a</strong>" in render_block("**a**\n")
    table = render_block("| a | b |\n| - | - |\n| c | d |\n")
    assert "<table>" in table
    assert "<td>d</td>" in table


def test_raw_html_is_escaped_in_each_form() -> None:
    assert "<b>" not in render_inline("a <b>b</b>")
    assert "&lt;b&gt;" in render_inline("a <b>b</b>")
    assert "<div>" not in render_block("<div>a</div>\n")


def test_an_image_stays_out_of_the_page() -> None:
    assert "<img" not in render_block("![a](https://example.com/p.png)\n")
    assert "<img" not in render_inline("![a](https://example.com/p.png)")


@pytest.mark.parametrize(
    ("source", "tag"),
    [
        ("# a\n", "h3"),
        ("## a\n", "h4"),
        ("### a\n", "h5"),
        ("#### a\n", "h6"),
        ("##### a\n", "h6"),
        ("###### a\n", "h6"),
    ],
)
def test_a_body_heading_sits_under_the_page_heading(source: str, tag: str) -> None:
    assert render_block(source) == f"<{tag}>a</{tag}>\n"


def rows_of(children: dict[str, list[str]], root: str = "root") -> list[tuple[str, int, bool]]:
    return [(row.node_id, row.depth, row.repeated) for row in tree_rows(root, children)]


def test_the_tree_walks_in_order_and_marks_each_depth() -> None:
    children = {"root": ["a", "b"], "a": ["c"]}
    assert rows_of(children) == [
        ("root", 0, False),
        ("a", 1, False),
        ("c", 2, False),
        ("b", 1, False),
    ]


def test_the_tree_opens_and_closes_each_level() -> None:
    children = {"root": ["a", "b"], "a": ["c"]}
    rows = {row.node_id: row for row in tree_rows("root", children)}
    assert (rows["root"].opens, rows["root"].closes) == (True, 0)
    assert (rows["a"].opens, rows["a"].closes) == (True, 0)
    assert (rows["c"].opens, rows["c"].closes) == (False, 1)
    assert (rows["b"].opens, rows["b"].closes) == (False, 1)


def test_the_tree_closes_each_level_at_the_end() -> None:
    children = {"root": ["a"], "a": ["b"]}
    rows = tree_rows("root", children)
    assert rows[-1].closes == rows[-1].depth


def test_a_second_parent_shows_a_link_with_no_children() -> None:
    children = {"root": ["a", "b"], "a": ["c"], "b": ["c"], "c": ["d"]}
    assert rows_of(children) == [
        ("root", 0, False),
        ("a", 1, False),
        ("c", 2, False),
        ("d", 3, False),
        ("b", 1, False),
        ("c", 2, True),
    ]


def test_a_diamond_chain_grows_the_tree_by_a_constant() -> None:
    children: dict[str, list[str]] = {}
    layers = 40
    for layer in range(layers):
        children[f"n{layer}"] = [f"a{layer}", f"b{layer}"]
        children[f"a{layer}"] = [f"n{layer + 1}"]
        children[f"b{layer}"] = [f"n{layer + 1}"]
    rows = tree_rows("n0", children)
    assert len(rows) == len(("n", "a", "b", "repeat")) * layers + 1


def test_a_deep_chain_does_not_use_the_python_stack() -> None:
    depth = 5_000
    children = {f"n{index}": [f"n{index + 1}"] for index in range(depth)}
    assert len(tree_rows("n0", children)) == depth + 1
    assert len(subtree_ids("n0", children)) == depth + 1


def test_a_left_out_node_stays_out_of_the_tree() -> None:
    children = {"root": ["a", "skill"], "a": ["b"]}
    assert [row.node_id for row in tree_rows("root", children, left_out={"skill"})] == [
        "root",
        "a",
        "b",
    ]


def test_the_children_do_not_depend_on_the_order_of_the_files() -> None:
    items = parsed(SAMPLE)
    assert children_by_broader(list(reversed(items))) == children_by_broader(items)


def test_a_sibling_row_does_not_open_a_level() -> None:
    rows = {row.node_id: row for row in tree_rows("root", {"root": ["a", "b"]})}
    assert not rows["a"].opens
    assert rows["a"].closes == 0


def test_each_node_with_no_broader_sits_under_the_root() -> None:
    children = children_by_broader(parsed(SAMPLE))
    assert children["root"] == ["alpha", "gamma", "review"]
    assert children["alpha"] == ["beta"]
    assert "root" not in children["root"]


def test_the_tree_on_the_first_page_shows_each_node_and_each_skill() -> None:
    page = site_of(SAMPLE)["index.html"]
    for node_id in ("root", "alpha", "beta", "gamma", "review"):
        assert f'href="nodes/{node_id}.html"' in page
    assert page.index('nodes/alpha.html"') < page.index('nodes/beta.html"')
    tree, _, skills = page.partition("<h2>Skills</h2>")
    assert "nodes/review.html" not in tree
    assert "Review a sample." in skills


def test_the_tree_markup_balances() -> None:
    page = site_of(SAMPLE)["index.html"]
    tree = page.split('<ul class="tree">')[1].split("<h2>Skills</h2>")[0]
    for tag in ("ul", "li", "details", "summary"):
        assert tree.count(f"<{tag}") - tree.count(f"</{tag}>") == (-1 if tag == "ul" else 0), tag


def test_the_tree_opens_the_top_levels_only() -> None:
    sources = {
        **SAMPLE,
        "knowledge/nodes/alpha/beta/deep/node.md": node(
            "deep", "ka:Concept", front="broader: [beta]\n"
        ),
        "knowledge/nodes/alpha/beta/node.md": node(
            "beta", "ka:Concept", front="broader: [alpha]\n" + pointers("deep")
        ),
    }
    page = site_of(sources)["index.html"]
    assert page.count("<details open>") == len(("root", "alpha"))
    assert page.count("<details>") == len(("beta",))


def test_a_node_with_two_parents_says_that_it_is_listed_above() -> None:
    sources = {
        **SAMPLE,
        "knowledge/nodes/alpha/beta/node.md": node(
            "beta", "ka:Concept", front="broader: [alpha, gamma]\n"
        ),
    }
    sources["knowledge/skills/review/node.md"] = node(
        "review",
        "ka:Skill",
        front=f"description: {SKILL_DESCRIPTION}\nuses: [beta]\n",
    )
    page = site_of(sources)["index.html"]
    assert page.count('href="nodes/beta.html"') == len(("first", "second"))
    assert page.count("also listed above") == 1


def test_the_first_page_states_what_is_in_force() -> None:
    page = site_of(SAMPLE)["index.html"]
    assert "No directive is in force." in page
    assert "9 entities wait for review: 5 nodes, 3 directives, and 1 exception." in page
    assert 'href="review.html"' in page


def test_the_counts_use_each_singular() -> None:
    sources = {
        "knowledge/node.md": node("root", "ka:Root", front=pointers("alpha")),
        "knowledge/nodes/alpha/node.md": node("alpha", status="accepted"),
    }
    page = site_of(sources)["index.html"]
    assert "1 entity waits for review: 1 node, 0 directives, and 0 exceptions." in page


def test_no_proposal_shows_an_empty_queue() -> None:
    sources = {
        "knowledge/node.md": node("root", "ka:Root", front=pointers("alpha"), status="accepted"),
        "knowledge/nodes/alpha/node.md": node("alpha", status="accepted"),
    }
    site = site_of(sources)
    assert "No entity waits for review." in site["index.html"]
    assert "No entity waits for review." in site["review.html"]
    assert "<section" not in site["review.html"]


def test_a_node_page_shows_each_part() -> None:
    page = site_of(SAMPLE)["nodes/alpha.html"]
    assert "The meaning of alpha." in page
    assert "status-proposed" in page
    assert "Run the other check." in page
    assert 'id="directive-wait"' in page
    assert "You need beta." in page
    assert "loads by: text" in page
    assert 'href="beta.html"' in page
    assert "knowledge/nodes/alpha/node.md" in page
    assert ".claude/references/alpha.md" in page


def test_a_node_page_links_up_with_a_relative_path() -> None:
    page = site_of(SAMPLE)["nodes/alpha.html"]
    assert 'href="../index.html"' in page
    assert 'href="../review.html"' in page
    assert 'href="root.html"' in page


def test_the_trail_runs_from_the_root_to_the_parent() -> None:
    page = site_of(SAMPLE)["nodes/beta.html"]
    trail = page.split('<p class="trail">')[1].split("</p>")[0]
    assert trail.index("root.html") < trail.index("alpha.html")
    assert "beta.html" not in trail
    root = site_of(SAMPLE)["nodes/root.html"]
    assert '<p class="trail">' not in root


ACCEPTED_SAMPLE = {
    "knowledge/node.md": node("root", "ka:Root", front=pointers("alpha")),
    "knowledge/nodes/alpha/node.md": node(
        "alpha",
        front=pointers("beta"),
        rules=rule("firm", "Run the firm check.", status="accepted")
        + rule("fresh", "Run the fresh check.")
        + rule("faded", "Run the faded check.", status="deprecated"),
    ),
    "knowledge/nodes/alpha/beta/node.md": node(
        "beta",
        "ka:Concept",
        front=(
            "broader: [alpha]\nexceptions:\n"
            "  - directive: firm\n    reason: A reason for firm.\n    status: proposed\n"
        ),
    ),
}


def test_what_applies_keeps_each_group_apart() -> None:
    page = site_of(ACCEPTED_SAMPLE)["nodes/alpha.html"]
    in_force = page.split("<h3>In force</h3>")[1].split("<h3>")[0]
    later = page.split("<h3>In force only after acceptance</h3>")[1].split("<h2>")[0]
    assert "Run the firm check." in in_force
    assert "Run the fresh check." not in in_force
    assert "Run the fresh check." in later
    assert "Run the firm check." not in later
    assert "Not in force." in later


def test_what_applies_shows_the_route() -> None:
    page = site_of(ACCEPTED_SAMPLE)["nodes/beta.html"]
    entry = page.split("<h3>In force</h3>")[1].split("</li>")[0]
    assert "Run the firm check." in entry
    route = entry.split("route: ")[1]
    assert route.index("alpha.html") < route.index("beta.html")
    assert "&rarr;" in route
    assert 'held by <a href="alpha.html">' in entry


def test_a_proposed_exception_is_named_as_a_later_stop() -> None:
    page = site_of(ACCEPTED_SAMPLE)["nodes/beta.html"]
    stopped = page.split("<h3>Stopped here after acceptance</h3>")[1].split("</p>")[0]
    assert 'href="alpha.html#directive-firm"' in stopped
    assert "<h3>Stopped here" not in site_of(ACCEPTED_SAMPLE)["nodes/alpha.html"]


def test_no_directive_in_force_is_stated_on_the_page() -> None:
    assert "No directive is in force at this node." in site_of(SAMPLE)["nodes/alpha.html"]
    assert (
        "No directive is in force at this node."
        not in (site_of(ACCEPTED_SAMPLE)["nodes/alpha.html"])
    )


def test_a_deprecated_directive_stays_on_its_node_page_only_for_reference() -> None:
    site = site_of(ACCEPTED_SAMPLE)
    page = site["nodes/alpha.html"]
    section = page.split("<h2>Deprecated directives</h2>")[1].split("<h2>")[0]
    assert "Run the faded check." in section
    assert "Run the firm check." not in section
    assert "Run the fresh check." not in section
    assert "<h2>Deprecated directives</h2>" not in site["nodes/beta.html"]
    assert (
        "Run the faded check."
        not in page.split("<h2>What applies here</h2>")[1].split(
            "<h2>Directives this node holds</h2>"
        )[0]
    )
    assert "Run the faded check." not in site["review.html"]


def test_an_exception_on_a_deprecated_directive_still_renders() -> None:
    sources = {
        **ACCEPTED_SAMPLE,
        "knowledge/nodes/alpha/beta/node.md": node(
            "beta",
            "ka:Concept",
            front=(
                "broader: [alpha]\nexceptions:\n"
                "  - directive: faded\n    reason: A reason for faded.\n    status: proposed\n"
            ),
        ),
    }
    site = site_of(sources)
    assert 'href="alpha.html#directive-faded"' in site["nodes/beta.html"]
    assert 'href="nodes/alpha.html#directive-faded"' in site["review.html"]
    assert "beta:faded" in site["review.html"]


def test_each_edge_of_a_directive_and_a_node_links_to_its_target() -> None:
    sources = {
        "knowledge/node.md": node("root", "ka:Root", front=pointers("alpha", "gamma")),
        "knowledge/nodes/alpha/node.md": node(
            "alpha",
            front="related: [gamma]\n",
            rules=rule("base-rule")
            + rule(
                "narrow-rule",
                "Run the narrow check.",
                extra="  - also_attached_to: gamma\n  - refines: base-rule\n",
            ),
        ),
        "knowledge/nodes/gamma/node.md": node("gamma"),
        "knowledge/skills/review/node.md": node(
            "review",
            "ka:Skill",
            front=(
                "description: Review a sample. Use when a sample needs a review.\n"
                "uses: [gamma]\napplies: [base-rule]\n"
            ),
        ),
    }
    site = site_of(sources)
    alpha = site["nodes/alpha.html"]
    assert 'Also attached to: <a href="gamma.html">' in alpha
    assert 'Refines: <a href="alpha.html#directive-base-rule">' in alpha
    assert '<dt>Related</dt>\n<dd><a href="gamma.html">' in alpha
    skill = site["nodes/review.html"]
    assert '<dt>Uses</dt>\n<dd><a href="gamma.html">' in skill
    assert '<dt>Applies</dt>\n<dd><a href="alpha.html#directive-base-rule">' in skill
    review = site["review.html"]
    assert 'Refines: <a href="nodes/alpha.html#directive-base-rule">' in review


def test_a_path_pointer_shows_its_patterns() -> None:
    sources = {
        "knowledge/node.md": node(
            "root",
            "ka:Root",
            front=(
                "pointers:\n  - kind: ka:PathPointer\n    target: alpha\n"
                '    trigger: You need alpha.\n    paths:\n      - "src/**/*"\n'
            ),
        ),
        "knowledge/nodes/alpha/node.md": node("alpha"),
    }
    page = site_of(sources)["nodes/root.html"]
    assert "loads by: path" in page
    assert "<code>src/**/*</code>" in page


def test_the_generated_file_of_a_rule_and_a_skill_are_named() -> None:
    sources = {
        "knowledge/node.md": node(
            "root",
            "ka:Root",
            front=(
                "pointers:\n  - kind: ka:AlwaysPointer\n    target: alpha\n"
                "    trigger: You need alpha.\n"
            ),
        ),
        "knowledge/nodes/alpha/node.md": node("alpha"),
        "knowledge/skills/review/node.md": node(
            "review",
            "ka:Skill",
            front=f"description: {SKILL_DESCRIPTION}\nuses: [alpha]\n",
        ),
    }
    site = site_of(sources)
    assert ".claude/rules/knowledge/alpha.md" in site["nodes/alpha.html"]
    assert ".claude/skills/review/SKILL.md" in site["nodes/review.html"]
    assert "<code>AGENTS.md</code>" in site["nodes/root.html"]


def test_the_queue_lists_each_proposed_entity_under_its_node() -> None:
    page = site_of(SAMPLE)["review.html"]
    assert page.count("<section") == len(SAMPLE)
    alpha = page.split('id="node-alpha"')[1].split("</section>")[0]
    assert "Run the check." in alpha
    assert "Run the other check." in alpha
    assert "knowledge/nodes/alpha/node.md:" in alpha
    beta = page.split('id="node-beta"')[1].split("</section>")[0]
    assert "A reason for beta." in beta
    assert "Run the third check." in beta


def test_the_queue_keeps_a_branch_together() -> None:
    page = site_of(SAMPLE)["review.html"]
    order = [page.index(f'id="node-{name}"') for name in ("root", "alpha", "beta", "gamma")]
    assert order == sorted(order)
    assert page.index('id="node-gamma"') < page.index('id="node-review"')


def test_the_queue_names_the_command_for_each_group() -> None:
    page = site_of(SAMPLE)["review.html"]
    alpha = page.split('id="node-alpha"')[1].split("</section>")[0]
    assert "uv run ka accept alpha keep wait</code>" in alpha
    assert "uv run ka accept --subtree alpha</code>" in alpha
    assert "with 6 waiting" in alpha
    beta = page.split('id="node-beta"')[1].split("</section>")[0]
    assert "uv run ka accept beta bound beta:keep</code>" in beta
    assert "--subtree beta" not in beta
    assert "<code>uv run ka runtime</code>" in page


def test_the_queue_has_a_row_for_each_branch() -> None:
    page = site_of(SAMPLE)["review.html"]
    assert "uv run ka accept --subtree root</code>" in page
    branches = page.split("<h2>Branches</h2>")[1].split("<h2>By node</h2>")[0]
    assert "the whole graph, 9 waiting" in branches
    assert "--subtree alpha" in branches
    assert "6 waiting" in branches
    assert "--subtree gamma" in branches
    assert "--subtree review" not in branches


def test_the_queue_counts_only_what_waits() -> None:
    page = site_of(ACCEPTED_SAMPLE)["review.html"]
    branches = page.split("<h2>Branches</h2>")[1].split("<h2>By node</h2>")[0]
    assert "the whole graph, 5 waiting" in branches
    assert "4 waiting" in branches
    alpha = page.split('id="node-alpha"')[1].split("</section>")[0]
    assert "with 4 waiting" in alpha


def test_the_queue_leaves_out_an_accepted_exception() -> None:
    sources = {
        **ACCEPTED_SAMPLE,
        "knowledge/nodes/alpha/beta/node.md": node(
            "beta",
            "ka:Concept",
            front=(
                "broader: [alpha]\nexceptions:\n"
                "  - directive: firm\n    reason: A reason for firm.\n    status: accepted\n"
                "  - directive: fresh\n    reason: A reason for fresh.\n    status: proposed\n"
            ),
        ),
    }
    page = site_of(sources)["review.html"]
    beta = page.split('id="node-beta"')[1].split("</section>")[0]
    assert "A reason for fresh." in beta
    assert "A reason for firm." not in beta
    assert "accept beta beta:fresh</code>" in beta


def test_the_queue_shows_a_node_with_two_parents_once() -> None:
    sources = {
        **SAMPLE,
        "knowledge/nodes/alpha/beta/node.md": node(
            "beta", "ka:Concept", front="broader: [alpha, gamma]\n"
        ),
    }
    sources["knowledge/skills/review/node.md"] = node(
        "review", "ka:Skill", front=f"description: {SKILL_DESCRIPTION}\nuses: [beta]\n"
    )
    page = site_of(sources)["review.html"]
    assert page.count('id="node-beta"') == 1


def test_the_queue_leaves_out_a_node_with_nothing_proposed() -> None:
    sources = {
        "knowledge/node.md": node("root", "ka:Root", front=pointers("alpha")),
        "knowledge/nodes/alpha/node.md": node("alpha", status="accepted"),
    }
    page = site_of(sources)["review.html"]
    assert 'id="node-root"' in page
    assert 'id="node-alpha"' not in page


def test_a_proposed_directive_on_an_accepted_node_is_named_without_the_node() -> None:
    sources = {
        "knowledge/node.md": node("root", "ka:Root", front=pointers("alpha"), status="accepted"),
        "knowledge/nodes/alpha/node.md": node("alpha", status="accepted", rules=rule("wait")),
    }
    page = site_of(sources)["review.html"]
    assert "uv run ka accept wait</code>" in page
    assert "The status of this node covers" not in page


def test_a_proposed_node_states_that_acceptance_changes_no_file() -> None:
    page = site_of(SAMPLE)["review.html"]
    gamma = page.split('id="node-gamma"')[1].split("</section>")[0]
    assert "Acceptance changes no directive and no generated file." in gamma
    assert "knowledge/nodes/gamma/node.md:5" in gamma


def test_the_queue_states_what_a_directive_reaches() -> None:
    page = site_of(SAMPLE)["review.html"]
    entry = page.split('id="node-alpha"')[1].split("</li>")[0]
    assert "reaches 1 node:" in entry
    assert "1 generated file lists it:" in entry
    assert ".claude/references/alpha.md" in entry


def test_the_queue_counts_a_directive_with_several_nodes() -> None:
    page = site_of(SAMPLE)["review.html"]
    entries = page.split('id="node-alpha"')[1].split("</section>")[0]
    wait = entries.split("<code>wait</code>")[1].split("</li>")[0]
    assert "reaches 3 nodes:" in wait
    assert "2 generated files list it:" not in wait
    assert "3 generated files list it:" in wait
    assert "more" not in wait


def test_the_queue_states_the_effect_of_an_exception() -> None:
    page = site_of(SAMPLE)["review.html"]
    beta = page.split('id="node-beta"')[1].split("</section>")[0]
    entry = beta.split("<h4>Exceptions</h4>")[1]
    assert "on acceptance: stops the directive at this node" in entry
    assert ".claude/references/beta.md" in entry
    assert "knowledge/nodes/alpha/beta/node.md:" in entry


def test_the_queue_limits_the_list_of_what_a_directive_reaches() -> None:
    extra_count = REACH_LISTED + 4
    names = [f"leaf{chr(ord('a') + index)}" for index in range(extra_count)]
    sources = {
        "knowledge/node.md": node("root", "ka:Root", front=pointers("alpha")),
        "knowledge/nodes/alpha/node.md": node("alpha", front=pointers(*names), rules=rule("wide")),
    }
    for name in names:
        sources[f"knowledge/nodes/alpha/{name}/node.md"] = node(
            name, "ka:Concept", front="broader: [alpha]\n"
        )
    page = site_of(sources)["review.html"]
    entry = page.split("<code>wide</code>")[1].split("</li>")[0]
    assert f"reaches {extra_count + 1} nodes:" in entry
    reached = entry.split("reaches ")[1].split("</span>")[0]
    assert reached.count("<a ") == REACH_LISTED
    assert f"and {extra_count + 1 - REACH_LISTED} more" in reached
    listed = entry.split("generated files list it:")[1].split("</span>")[0]
    assert listed.count("<code>") == REACH_LISTED
    assert f"and {extra_count + 1 - REACH_LISTED} more" in listed


def test_the_queue_shows_the_pointers_and_the_body_of_a_node() -> None:
    page = site_of(SAMPLE)["review.html"]
    root = page.split('id="node-root"')[1].split("</section>")[0]
    assert "Pointers (2)" in root
    assert "You need alpha." in root
    assert "A fact about the root." in root
    skill = page.split('id="node-review"')[1].split("</section>")[0]
    assert "Read each directive." in skill
    assert "Review a sample." in skill


def test_the_queue_says_that_a_person_runs_the_command() -> None:
    page = site_of(SAMPLE)["review.html"]
    assert "This page cannot accept anything." in page
    assert "Run the command yourself" in page


def test_a_project_page_names_the_project_command(tmp_path: Path) -> None:
    write_tree(tmp_path)
    (tmp_path / "knowledge/.ka").mkdir(parents=True, exist_ok=True)
    (tmp_path / "knowledge/.ka/ka").write_text("#!/bin/sh\n", encoding="utf-8")
    report = write_view(tmp_path)
    assert report.problems == []
    page = (tmp_path / VIEW_FOLDER / "review.html").read_text(encoding="utf-8")
    assert "knowledge/.ka/ka accept --subtree alpha</code>" in page
    assert "<code>knowledge/.ka/ka runtime</code>" in page
    assert "uv run ka" not in page


def test_each_page_carries_the_marker_and_the_policy() -> None:
    files = render_site(parsed(SAMPLE), Path())
    for name, data in files.items():
        assert is_generated(data), name
        html = data.decode("utf-8")
        assert html.startswith(f"{MARKER}\n<!doctype html>"), name
        policy = re.search(r'http-equiv="Content-Security-Policy" content="([^"]*)"', html)
        assert policy is not None, name
        value = policy[1].replace("&#39;", "'")
        assert "default-src 'none'" in value
        assert "base-uri 'none'" in value
        assert "form-action 'none'" in value
        assert "unsafe-inline" not in value
        assert "script-src" not in value


def test_the_policy_holds_the_hash_of_the_style_block() -> None:
    html = site_of(SAMPLE)["index.html"]
    style = html.split("<style>")[1].split("</style>")[0]
    digest = base64.b64encode(hashlib.sha256(style.encode("utf-8")).digest()).decode("ascii")
    assert f"style-src &#39;sha256-{digest}&#39;" in html


def test_each_link_on_the_sample_resolves() -> None:
    site = site_of(SAMPLE)
    pages = {PurePosixPath(name) for name in site}
    assert {"index.html", "review.html", "nodes/alpha.html"} <= set(site)
    for name, html in site.items():
        assert unsafe_markup(html, PurePosixPath(name), pages) == [], name


def test_a_bad_page_name_cannot_come_from_a_node_id() -> None:
    source = node("alpha").replace("id: alpha", "id: ../../evil")
    assert not isinstance(parse_source(source, Path("node.md")), ParsedNode)


def test_the_command_writes_each_page_and_reports_them(tmp_path: Path) -> None:
    write_tree(tmp_path)
    result = RUNNER.invoke(app, ["view", str(tmp_path)])
    assert result.exit_code == 0, result.output
    assert f"Open {tmp_path / 'build/view/index.html'} in a browser." in result.output
    assert "7 pages, 7 written, 0 removed, 0 problems" in result.output
    assert set(view_files(tmp_path)) == {
        "index.html",
        "review.html",
        "nodes/root.html",
        "nodes/alpha.html",
        "nodes/beta.html",
        "nodes/gamma.html",
        "nodes/review.html",
    }


def test_a_second_run_writes_nothing(tmp_path: Path) -> None:
    write_tree(tmp_path)
    assert len(write_view(tmp_path).written) == len(SAMPLE) + 2
    report = write_view(tmp_path)
    assert report.written == ()
    assert report.removed == ()
    assert len(report.files) == len(SAMPLE) + 2


def test_the_output_stays_the_same_in_another_folder(tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "a folder/that is/deeper"
    for folder in (first, second):
        folder.mkdir(parents=True)
        write_tree(folder)
        assert write_view(folder).problems == []
    files = view_files(first)
    assert files == view_files(second)
    joined = b"".join(files.values())
    assert str(tmp_path).encode() not in joined
    assert b"/Users/" not in joined
    assert b"/private/" not in joined
    assert b"/tmp/" not in joined


def test_a_relative_folder_gives_the_same_output(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    for folder in (first, second):
        folder.mkdir()
        write_tree(folder)
    assert write_view(first).problems == []
    monkeypatch.chdir(second)
    assert write_view(Path()).problems == []
    assert view_files(first) == view_files(second)


def test_a_deleted_node_removes_its_page(tmp_path: Path) -> None:
    write_tree(tmp_path)
    assert write_view(tmp_path).problems == []
    assert (tmp_path / VIEW_FOLDER / "nodes/gamma.html").exists()
    shutil.rmtree(tmp_path / "knowledge/nodes/gamma")
    root = tmp_path / "knowledge/node.md"
    root.write_text(
        root.read_text(encoding="utf-8").replace(text_pointer("gamma"), ""), encoding="utf-8"
    )
    report = write_view(tmp_path)
    assert report.problems == []
    assert report.removed == (VIEW_FOLDER / "nodes/gamma.html",)
    assert not (tmp_path / VIEW_FOLDER / "nodes/gamma.html").exists()


def test_a_rejected_tree_removes_the_earlier_view(tmp_path: Path) -> None:
    write_tree(tmp_path)
    assert write_view(tmp_path).problems == []
    path = tmp_path / "knowledge/nodes/gamma/node.md"
    path.write_text("not a node\n", encoding="utf-8")
    result = RUNNER.invoke(app, ["view", str(tmp_path)])
    assert result.exit_code == 1
    assert "front-matter" in result.output
    assert "Open " not in result.output
    assert view_files(tmp_path) == {}


def test_a_language_problem_also_stops_the_view(tmp_path: Path) -> None:
    write_tree(tmp_path)
    path = tmp_path / "knowledge/nodes/gamma/node.md"
    path.write_text(
        node("gamma", rules=rule("bad-rule", "This sentence does not open with a verb.")),
        encoding="utf-8",
    )
    report = write_view(tmp_path)
    assert report.files == ()
    assert {problem.code for problem in report.problems} >= {"opening"}


def test_an_empty_tree_reports_empty_tree(tmp_path: Path) -> None:
    write_tree(tmp_path, {})
    report = write_view(tmp_path)
    assert [problem.code for problem in report.problems] == ["empty-tree"]


def test_a_file_without_the_marker_blocks_the_write(tmp_path: Path) -> None:
    write_tree(tmp_path)
    own = tmp_path / VIEW_FOLDER / "index.html"
    own.parent.mkdir(parents=True)
    own.write_text("mine\n", encoding="utf-8")
    report = write_view(tmp_path)
    assert [problem.code for problem in report.problems] == ["not-generated"]
    assert own.read_text(encoding="utf-8") == "mine\n"
    assert report.written == ()


def test_a_stale_file_without_the_marker_stays(tmp_path: Path) -> None:
    write_tree(tmp_path)
    own = tmp_path / VIEW_FOLDER / "nodes/mine.html"
    own.parent.mkdir(parents=True)
    own.write_text("mine\n", encoding="utf-8")
    assert write_view(tmp_path).problems == []
    assert own.read_text(encoding="utf-8") == "mine\n"


@pytest.mark.parametrize("name", ["build", "build/view"])
def test_a_file_in_place_of_a_folder_blocks_the_write(tmp_path: Path, name: str) -> None:
    write_tree(tmp_path)
    own = tmp_path / name
    own.parent.mkdir(exist_ok=True)
    own.write_text("mine\n", encoding="utf-8")
    report = write_view(tmp_path)
    assert report.problems
    assert report.written == ()
    assert own.read_text(encoding="utf-8") == "mine\n"


def test_a_symbolic_link_blocks_the_write(tmp_path: Path) -> None:
    repository = tmp_path / "repository"
    outside = tmp_path / "outside"
    repository.mkdir()
    outside.mkdir()
    write_tree(repository)
    (repository / "build").mkdir()
    (repository / VIEW_FOLDER).symlink_to(outside)
    report = write_view(repository)
    assert {problem.code for problem in report.problems} == {"not-generated"}
    assert list(outside.iterdir()) == []


def test_the_real_tree_gives_a_safe_site(tmp_path: Path) -> None:
    shutil.copytree(REPO / "knowledge", tmp_path / "knowledge")
    report = write_view(tmp_path)
    assert report.problems == []
    files = view_files(tmp_path)
    pages = {PurePosixPath(name) for name in files}
    for name, data in files.items():
        assert unsafe_markup(data.decode("utf-8"), PurePosixPath(name), pages) == [], name
    compiled = compile_tree(tmp_path, proposals=True).compiled
    assert compiled is not None
    assert len(files) == len(compiled.paths) + 2


def test_the_queue_count_equals_the_pending_list_on_the_real_tree(tmp_path: Path) -> None:
    shutil.copytree(REPO / "knowledge", tmp_path / "knowledge")
    assert write_view(tmp_path).problems == []
    pending, problems = pending_entities(tmp_path)
    assert problems == []
    page = (tmp_path / VIEW_FOLDER / "review.html").read_text(encoding="utf-8")
    assert f"{len(pending)} entities wait for review" in page
    for entity in pending:
        name = ":".join(entity.key[1:])
        assert re.search(rf"(accept|\s){re.escape(name)}[\s<]", page), name
    assert page.count("status line:") + page.count("Status line:") == len(pending)


def test_the_view_does_not_change_the_source_or_the_index(tmp_path: Path) -> None:
    write_tree(tmp_path)
    (tmp_path / ".gitignore").write_text("build/\n", encoding="utf-8")
    subprocess.run([GIT, "init", "-q", "--template=", str(tmp_path)], check=True)  # noqa: S603
    subprocess.run([GIT, "-C", str(tmp_path), "add", "-A"], check=True)  # noqa: S603
    before = {path: path.read_bytes() for path in tmp_path.rglob("node.md")}
    assert write_view(tmp_path).problems == []
    assert {path: path.read_bytes() for path in tmp_path.rglob("node.md")} == before
    status = subprocess.run(  # noqa: S603
        [GIT, "-C", str(tmp_path), "status", "--porcelain", "--untracked-files=all"],
        capture_output=True,
        check=True,
        text=True,
    ).stdout
    assert "build/" not in status
    assert all(line.startswith("A ") for line in status.splitlines())


def test_the_output_holds_no_time_stamp_or_a_script() -> None:
    joined = "".join(site_of(SAMPLE).values())
    assert "<script" not in joined
    assert not re.search(r"\b20\d\d-\d\d-\d\d\b", joined)


def test_a_deep_chain_renders() -> None:
    depth = 1_100
    sources = {
        "knowledge/node.md": node(
            "root",
            "ka:Root",
            front=pointers(*(f"n{index}" for index in range(depth))),
        ),
        "knowledge/nodes/n0/node.md": node("n0"),
    }
    for index in range(1, depth):
        sources[f"knowledge/nodes/n{index}/node.md"] = node(
            f"n{index}", "ka:Concept", front=f"broader: [n{index - 1}]\n"
        )
    files = render_site(parsed(sources), Path())
    assert len(files) == depth + 3
