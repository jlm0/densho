import json
import posixpath
from dataclasses import dataclass, replace
from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING
from urllib.parse import quote

from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape

from knowledge_architecture.compiler.output import NOTICES
from knowledge_architecture.generated.metamodel import CompiledResult
from knowledge_architecture.governance.base import TREE_FOLDERS
from knowledge_architecture.parser.generated import MARKER
from knowledge_architecture.parser.result import Problem

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator

    from knowledge_architecture.runtime.view import DirectiveCounts, NodeView, RuntimeView

REVIEW_FOLDER = PurePosixPath("build/runtime-proposals")
ROOT_FILE = PurePosixPath("AGENTS.md")
FOLDER_FILE_NAME = "AGENTS.md"
RULES_FOLDER = PurePosixPath(".claude/rules/knowledge")
TOOL_FOLDER = ".claude"
SKILLS_FOLDER = PurePosixPath(".claude/skills")
SKILL_FILE_NAME = "SKILL.md"
SKILL_TEMPLATE = "skill.md.jinja"
REVIEW_MARK = ".proposals"
REPLACING_FILES = ("CLAUDE.md", ".claude/CLAUDE.md", "CLAUDE.local.md")
SKILL_KEPT_TOKENS = 5_000
CHARACTERS_PER_TOKEN = 3
SKILL_KEPT_CHARACTERS = SKILL_KEPT_TOKENS * CHARACTERS_PER_TOKEN
ON_DEMAND_CHARACTERS = 40_000


@dataclass(frozen=True, slots=True)
class RenderedFile:
    path: PurePosixPath
    text: str
    node_path: str
    whole_part: str
    limit: int | None


def _link_text(text: str) -> str:
    return text.replace("\\", "\\\\").replace("[", "\\[").replace("]", "\\]")


def _yaml_string(text: str) -> str:
    return json.dumps(text, ensure_ascii=False)


def _count(number: int, noun: str) -> str:
    return f"{number} {noun}" if number == 1 else f"{number} {noun}s"


def state_sentence(counts: DirectiveCounts) -> str:
    if counts.in_force:
        verb = "is" if counts.in_force == 1 else "are"
        first = f"{_count(counts.in_force, 'directive')} {verb} in force."
    else:
        first = "No directive is in force."
    others = [
        _count(number, noun)
        for number, noun in (
            (counts.other_directives, "directive"),
            (counts.other_exceptions, "exception"),
        )
        if number
    ]
    if not others:
        return first
    verb = "is" if counts.other_directives + counts.other_exceptions == 1 else "are"
    return f"{first} The graph holds {' and '.join(others)} that {verb} not in force."


_ENVIRONMENT = Environment(
    loader=FileSystemLoader(Path(__file__).parent / "templates" / "claude_code"),
    autoescape=select_autoescape(enabled_extensions=(), default=False, default_for_string=False),
    undefined=StrictUndefined,
    trim_blocks=True,
    lstrip_blocks=True,
    keep_trailing_newline=True,
)
_ENVIRONMENT.filters["link_text"] = _link_text
_ENVIRONMENT.filters["yaml_string"] = _yaml_string


def review_path(path: PurePosixPath) -> PurePosixPath:
    parts = [part.removeprefix(".") if part == TOOL_FOLDER else part for part in path.parts]
    named = PurePosixPath(*parts)
    return named.with_name(f"{named.stem}{REVIEW_MARK}{named.suffix}")


def _skill_file(node: NodeView) -> PurePosixPath:
    return SKILLS_FOLDER / node.link.id / SKILL_FILE_NAME


def _rule_file(node: NodeView) -> PurePosixPath:
    return RULES_FOLDER / f"{node.link.id}.md"


def _folder_file(node: NodeView) -> PurePosixPath:
    return PurePosixPath(node.link.path).with_name(FOLDER_FILE_NAME)


def render_files(view: RuntimeView) -> list[RenderedFile]:
    review = view.result == CompiledResult.proposals

    def location(path: PurePosixPath) -> PurePosixPath:
        return REVIEW_FOLDER / review_path(path) if review else path

    def render(template: str, path: PurePosixPath, node: NodeView) -> str:
        folder = location(path).parent.as_posix()

        def link(target: str) -> str:
            return quote(posixpath.relpath(target, start=folder), safe="/")

        return _ENVIRONMENT.get_template(template).render(
            view=view,
            node=node,
            state=state_sentence(view.counts),
            link=link,
            marker=MARKER,
            notice=NOTICES[view.result] if review else None,
        )

    def on_demand(template: str, path: PurePosixPath, node: NodeView) -> RenderedFile:
        text = render(template, path, node)
        return RenderedFile(location(path), text, node.link.path, text, ON_DEMAND_CHARACTERS)

    def skill(node: NodeView) -> RenderedFile:
        path = _skill_file(node)
        head = replace(node, body=None, pointers=())
        return RenderedFile(
            location(path),
            render(SKILL_TEMPLATE, path, node),
            node.link.path,
            render(SKILL_TEMPLATE, path, head),
            SKILL_KEPT_CHARACTERS,
        )

    root_text = render("root.md.jinja", ROOT_FILE, view.root)
    return [
        RenderedFile(location(ROOT_FILE), root_text, view.root.link.path, root_text, None),
        *(skill(node) for node in view.skills),
        *(on_demand("rule.md.jinja", _rule_file(node), node) for node in view.rules),
        *(on_demand("folder.md.jinja", _folder_file(node), node) for node in view.folders),
    ]


def size_problems(rendered: Iterable[RenderedFile], repository: Path) -> list[Problem]:
    return [
        Problem(
            repository / entry.node_path,
            1,
            "size",
            f"{entry.path} needs {len(entry.whole_part)} characters in the part that must stay "
            f"whole, over the limit of {entry.limit}. "
            "Move knowledge out of this node, or attach fewer directives.",
        )
        for entry in rendered
        if entry.limit is not None and len(entry.whole_part) > entry.limit
    ]


def candidate_files(repository: Path) -> Iterator[Path]:
    yield repository / ROOT_FILE
    for folder in TREE_FOLDERS:
        yield from (repository / folder).rglob(FOLDER_FILE_NAME)
    yield from (repository / RULES_FOLDER).rglob("*.md")
    yield from (repository / SKILLS_FOLDER).glob(f"*/{SKILL_FILE_NAME}")


def review_candidates(repository: Path) -> Iterator[Path]:
    yield from (repository / REVIEW_FOLDER).rglob("*.md")


def instruction_notes(repository: Path) -> list[str]:
    return [
        f"{name} exists, so Claude Code reads it and does not read {ROOT_FILE}. "
        f"Add the line @{posixpath.relpath(ROOT_FILE, start=posixpath.dirname(name) or '.')} "
        f"to {name}."
        for name in REPLACING_FILES
        if (repository / name).exists()
    ]
