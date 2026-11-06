import re

from markdown_it import MarkdownIt

CODE_WORD = "CODE"
WORD = re.compile(r"[^\W_][\w'\u2019-]*")
_MARKDOWN = MarkdownIt("commonmark")
_VISIBLE = frozenset({"text", "html_inline", "image"})


def read_prose(source: str) -> tuple[str, str]:
    masked: list[str] = []
    plain: list[str] = []
    for token in _MARKDOWN.parseInline(source)[0].children or []:
        if token.type == "code_inline":
            masked.append(CODE_WORD)
            plain.append(token.content)
        elif token.type in _VISIBLE:
            masked.append(token.content)
            plain.append(token.content)
    return "".join(masked), "".join(plain)


def words_of(text: str) -> list[str]:
    return WORD.findall(text.casefold())
