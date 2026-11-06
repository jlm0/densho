import json
import posixpath
from dataclasses import dataclass, replace
from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING

from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape
from markdown_it import MarkdownIt

from engine.compiler.output import NOTICES
from engine.generated.metamodel import CompiledResult
from engine.parser.generated import MARKER
from engine.parser.result import Problem

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator

    from engine.runtime.view import DirectiveCounts, NodeLink, NodeView, RuntimeView

REVIEW_FOLDER = PurePosixPath("build/runtime-proposals")
ROOT_FILE = PurePosixPath("AGENTS.md")
RULES_FOLDER = PurePosixPath(".claude/rules/knowledge")
REFERENCES_FOLDER = PurePosixPath(".claude/references")
TOOL_FOLDER = ".claude"
SKILLS_FOLDER = PurePosixPath(".claude/skills")
SKILL_FILE_NAME = "SKILL.md"
SKILL_TEMPLATE = "skill.md.jinja"
REVIEW_MARK = ".proposals"
IMPORTING_FILES = ("CLAUDE.md", ".claude/CLAUDE.md")
REPLACING_FILES = (*IMPORTING_FILES, "CLAUDE.local.md")
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
_IMPORT_PARSER = MarkdownIt("commonmark")


def review_path(path: PurePosixPath) -> PurePosixPath:
    parts = [part.removeprefix(".") if part == TOOL_FOLDER else part for part in path.parts]
    named = PurePosixPath(*parts)
    return named.with_name(f"{named.stem}{REVIEW_MARK}{named.suffix}")


def _skill_file(node: NodeView) -> PurePosixPath:
    return SKILLS_FOLDER / node.link.id / SKILL_FILE_NAME


def _rule_file(node: NodeView) -> PurePosixPath:
    return RULES_FOLDER / f"{node.link.id}.md"


def _reference_file(node: NodeView) -> PurePosixPath:
    return REFERENCES_FOLDER / f"{node.link.id}.md"


def generated_paths(view: RuntimeView) -> dict[str, PurePosixPath]:
    return {
        view.root.link.id: ROOT_FILE,
        **{node.link.id: _reference_file(node) for node in view.pages},
        **{node.link.id: _skill_file(node) for node in view.skills},
        **{node.link.id: _rule_file(node) for node in view.rules},
    }


def render_files(view: RuntimeView) -> list[RenderedFile]:
    review = view.result == CompiledResult.proposals
    generated = generated_paths(view)

    def location(path: PurePosixPath) -> PurePosixPath:
        return REVIEW_FOLDER / review_path(path) if review else path

    def render(template: str, path: PurePosixPath, node: NodeView) -> str:
        folder = location(path).parent.as_posix()

        def href(target: NodeLink) -> str:
            destination = location(generated[target.id]).as_posix()
            return posixpath.relpath(destination, start=folder)

        return _ENVIRONMENT.get_template(template).render(
            view=view,
            node=node,
            state=state_sentence(view.counts),
            href=href,
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
        *(on_demand("reference.md.jinja", _reference_file(node), node) for node in view.pages),
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
    yield from (repository / RULES_FOLDER).rglob("*.md")
    yield from (repository / SKILLS_FOLDER).glob(f"*/{SKILL_FILE_NAME}")
    yield from (repository / REFERENCES_FOLDER).glob("*.md")


def review_candidates(repository: Path) -> Iterator[Path]:
    yield from (repository / REVIEW_FOLDER).rglob("*.md")


def _import_line(name: str) -> str:
    return f"@{posixpath.relpath(ROOT_FILE, start=posixpath.dirname(name) or '.')}"


def _imports_root(text: str, line: str) -> bool:
    forms = {line, line.replace("@", "@./", 1)}
    return any(
        child.type == "text" and not forms.isdisjoint(child.content.split())
        for token in _IMPORT_PARSER.parse(text)
        for child in token.children or ()
    )


def _reads_root(repository: Path, name: str) -> bool:
    path = repository / name
    if path.resolve() == (repository / ROOT_FILE).resolve():
        return True
    try:
        text = path.read_text(encoding="utf-8")
    except OSError, UnicodeDecodeError:
        return False
    return _imports_root(text, _import_line(name))


def _replacing_files(repository: Path) -> list[str]:
    return [name for name in REPLACING_FILES if (repository / name).exists()]


def instruction_notes(repository: Path) -> list[str]:
    existing = _replacing_files(repository)
    if any(_reads_root(repository, name) for name in existing):
        return []
    return [
        f"{name} exists, so Claude Code reads it and does not read {ROOT_FILE}. "
        f"Add the line {_import_line(name)} to {name}."
        for name in existing
    ]


def add_root_import(repository: Path) -> tuple[tuple[str, ...], list[Problem]]:
    existing = _replacing_files(repository)
    target = next((name for name in IMPORTING_FILES if name in existing), None)
    if target is None or any(_reads_root(repository, name) for name in existing):
        return (), []
    path = repository / target
    if path.is_symlink():
        message = (
            f"This file is a symbolic link. Add the line {_import_line(target)} to its target."
        )
        return (), [Problem(path, 1, "import", message)]
    try:
        data = path.read_bytes()
        separator = b"\n" if data.endswith(b"\n") else b"\n\n"
        with path.open("ab") as stream:
            stream.write((separator if data else b"") + _import_line(target).encode() + b"\n")
    except OSError as error:
        message = f"The command cannot add the import: {error.strerror!a}."
        return (), [Problem(path, 1, "import", message)]
    return (target,), []
