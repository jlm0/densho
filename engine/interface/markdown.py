import re

from markdown_it import MarkdownIt

SAFE_SCHEMES = frozenset({"http", "https", "mailto"})
HEADING_TOKENS = frozenset({"heading_open", "heading_close"})
HEADING_SHIFT = 2
DEEPEST_HEADING = 6
_SCHEME = re.compile(r"([a-z][a-z0-9+.-]*):")


def is_safe_link(url: str) -> bool:
    match = _SCHEME.match(url.lower())
    return match is not None and match[1] in SAFE_SCHEMES


class _SafeMarkdown(MarkdownIt):
    def validateLink(self, url: str) -> bool:  # noqa: N802
        return is_safe_link(url)


_MARKDOWN = _SafeMarkdown("commonmark", {"html": False}).disable("image").enable("table")


def render_block(text: str) -> str:
    environment: dict[str, object] = {}
    tokens = _MARKDOWN.parse(text, environment)
    for token in tokens:
        if token.type in HEADING_TOKENS:
            level = int(token.tag.removeprefix("h")) + HEADING_SHIFT
            token.tag = f"h{min(level, DEEPEST_HEADING)}"
    return _MARKDOWN.renderer.render(tokens, _MARKDOWN.options, environment)


def render_inline(text: str) -> str:
    return _MARKDOWN.renderInline(text)
