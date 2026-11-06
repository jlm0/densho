import re
from typing import TYPE_CHECKING
from urllib.parse import unquote

from markdown_it import MarkdownIt

if TYPE_CHECKING:
    from pathlib import Path

SCHEME = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")


def local_links(text: str) -> list[str]:
    targets: list[str] = []
    for token in MarkdownIt("commonmark").parse(text):
        for child in token.children or []:
            target = child.attrGet("href") if child.type == "link_open" else child.attrGet("src")
            if isinstance(target, str) and not SCHEME.match(target):
                targets.append(target)
    return [target for target in targets if target.partition("#")[0]]


def resolves(link: str, folder: Path, repository: Path) -> bool:
    try:
        resolved = (folder / unquote(link.partition("#")[0])).resolve()
        return resolved.is_relative_to(repository.resolve()) and resolved.exists()
    except OSError, ValueError:
        return False
