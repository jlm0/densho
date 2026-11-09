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
from engine.parser.scripts import SCRIPTS_FOLDER_NAME
from engine.parser.steps import STEP_SUFFIX, STEPS_FOLDER_NAME

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator, Mapping

    from engine.parser.result import Script
    from engine.runtime.view import (
        CopyStepView,
        DirectiveCounts,
        NodeLink,
        NodeView,
        RuntimeView,
        StepView,
    )

REVIEW_FOLDER = PurePosixPath("build/runtime-proposals")
ROOT_FILE = PurePosixPath("AGENTS.md")
RULES_FOLDER = PurePosixPath(".claude/rules/knowledge")
REFERENCES_FOLDER = PurePosixPath(".claude/references")
TOOL_FOLDER = ".claude"
SKILLS_FOLDER = PurePosixPath(".claude/skills")
SKILL_FILE_NAME = "SKILL.md"
SKILL_TEMPLATE = "skill.md.jinja"
STEP_TEMPLATE = "step_tree.md.jinja"
COPY_SKILL_TEMPLATE = "copy_skill.md.jinja"
COPY_STEP_TEMPLATE = "copy_step.md.jinja"
REVIEW_MARK = ".proposals"
IMPORTING_FILES = ("CLAUDE.md", ".claude/CLAUDE.md")
REPLACING_FILES = (*IMPORTING_FILES, "CLAUDE.local.md")
SKILL_KEPT_TOKENS = 5_000
CHARACTERS_PER_TOKEN = 3
SKILL_KEPT_CHARACTERS = SKILL_KEPT_TOKENS * CHARACTERS_PER_TOKEN
ON_DEMAND_CHARACTERS = 40_000
READ_TOKENS = 25_000
STEP_CHARACTERS = READ_TOKENS * CHARACTERS_PER_TOKEN
ROOT_LINES = 200
SKILL_LINES = 500


@dataclass(frozen=True, slots=True)
class RenderedFile:
    path: PurePosixPath
    text: str
    node_path: str
    whole_part: str
    limit: int | None
    line_limit: int | None = None


def _link_text(text: str) -> str:
    return text.replace("\\", "\\\\").replace("[", "\\[").replace("]", "\\]")


def _yaml_string(text: str) -> str:
    return json.dumps(text, ensure_ascii=False)


def _table_cell(text: str) -> str:
    return text.replace("|", "\\|")


def _code_list(names: Iterable[str]) -> str:
    return ", ".join(f"`{name}`" for name in names)


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
_ENVIRONMENT.filters["table_cell"] = _table_cell
_ENVIRONMENT.filters["code_list"] = _code_list
_IMPORT_PARSER = MarkdownIt("commonmark")


def _review_folders(path: PurePosixPath) -> PurePosixPath:
    parts = [part.removeprefix(".") if part == TOOL_FOLDER else part for part in path.parts]
    return PurePosixPath(*parts)


def review_path(path: PurePosixPath) -> PurePosixPath:
    named = _review_folders(path)
    return named.with_name(f"{named.stem}{REVIEW_MARK}{named.suffix}")


REVIEW_SKILLS_FOLDER = REVIEW_FOLDER / _review_folders(SKILLS_FOLDER)
OWNERS = (
    (SKILLS_FOLDER, SKILL_FILE_NAME),
    (REVIEW_SKILLS_FOLDER, review_path(PurePosixPath(SKILL_FILE_NAME)).name),
)


def marker_owner(path: PurePosixPath) -> PurePosixPath:
    for skills, name in OWNERS:
        if not path.is_relative_to(skills):
            continue
        match path.relative_to(skills).parts:
            case (skill, folder, _, *_) if folder == SCRIPTS_FOLDER_NAME:
                return skills / skill / name
            case _:
                pass
    return path


def _skill_file(node: NodeView) -> PurePosixPath:
    return SKILLS_FOLDER / node.link.id / SKILL_FILE_NAME


def _step_file(flow: str, step: str) -> PurePosixPath:
    return SKILLS_FOLDER / flow / STEPS_FOLDER_NAME / f"{step}{STEP_SUFFIX}"


def _step_source(node: NodeView, step: StepView | CopyStepView) -> str:
    folder = PurePosixPath(node.link.path).parent / STEPS_FOLDER_NAME
    return (folder / f"{step.link.id}{STEP_SUFFIX}").as_posix()


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


def copied_files(view: RuntimeView) -> dict[PurePosixPath, Script]:
    review = view.result == CompiledResult.proposals
    copies: dict[PurePosixPath, Script] = {}
    for node in view.skills:
        folder = _skill_file(node).parent / SCRIPTS_FOLDER_NAME
        if review:
            folder = REVIEW_FOLDER / _review_folders(folder)
        copies.update((folder / script.path, script) for script in node.scripts)
    return copies


def render_files(view: RuntimeView) -> list[RenderedFile]:
    review = view.result == CompiledResult.proposals
    generated = generated_paths(view)

    def location(path: PurePosixPath) -> PurePosixPath:
        return REVIEW_FOLDER / review_path(path) if review else path

    def render(
        template: str,
        path: PurePosixPath,
        node: NodeView | StepView | CopyStepView,
        steps: Mapping[str, PurePosixPath] | None = None,
    ) -> str:
        folder = location(path).parent.as_posix()
        local = steps or {}

        def href(target: NodeLink) -> str:
            destination = location(generated[target.id]).as_posix()
            return posixpath.relpath(destination, start=folder)

        def step_href(target: NodeLink) -> str:
            if target.id not in local:
                return href(target)
            return posixpath.relpath(location(local[target.id]).as_posix(), start=folder)

        return _ENVIRONMENT.get_template(template).render(
            view=view,
            node=node,
            state=state_sentence(view.counts),
            href=href,
            step_href=step_href,
            marker=MARKER,
            notice=NOTICES[view.result] if review else None,
        )

    def on_demand(template: str, path: PurePosixPath, node: NodeView) -> RenderedFile:
        text = render(template, path, node)
        return RenderedFile(location(path), text, node.link.path, text, ON_DEMAND_CHARACTERS)

    def copy_skill(node: NodeView) -> list[RenderedFile]:
        path = _skill_file(node)
        head = replace(node, body=None, pointers=())
        steps = {
            step.link.id: _step_file(node.link.id, step.link.id)
            for step in node.copy_steps
            if step.has_file
        }
        skill_file = RenderedFile(
            location(path),
            render(COPY_SKILL_TEMPLATE, path, node, steps),
            node.link.path,
            render(COPY_SKILL_TEMPLATE, path, head, steps),
            SKILL_KEPT_CHARACTERS,
            SKILL_LINES,
        )
        step_files = [
            RenderedFile(
                location(steps[step.link.id]),
                text := render(COPY_STEP_TEMPLATE, steps[step.link.id], step, steps),
                _step_source(node, step),
                text,
                STEP_CHARACTERS,
            )
            for step in node.copy_steps
            if step.has_file
        ]
        return [skill_file, *step_files]

    def skill(node: NodeView) -> list[RenderedFile]:
        if node.copy_steps:
            return copy_skill(node)
        path = _skill_file(node)
        head = replace(node, body=None, pointers=())
        steps = {step.link.id: _step_file(node.link.id, step.link.id) for step in node.steps}
        skill_file = RenderedFile(
            location(path),
            render(SKILL_TEMPLATE, path, node, steps),
            node.link.path,
            render(SKILL_TEMPLATE, path, head, steps),
            SKILL_KEPT_CHARACTERS,
            SKILL_LINES,
        )
        step_files = [
            RenderedFile(
                location(steps[step.link.id]),
                text := render(STEP_TEMPLATE, steps[step.link.id], step, steps),
                _step_source(node, step),
                text,
                STEP_CHARACTERS,
            )
            for step in node.steps
        ]
        return [skill_file, *step_files]

    root_text = render("root.md.jinja", ROOT_FILE, view.root)
    root_path = view.root.link.path
    return [
        RenderedFile(location(ROOT_FILE), root_text, root_path, root_text, None, ROOT_LINES),
        *(entry for node in view.skills for entry in skill(node)),
        *(on_demand("rule.md.jinja", _rule_file(node), node) for node in view.rules),
        *(on_demand("reference.md.jinja", _reference_file(node), node) for node in view.pages),
    ]


def size_problems(rendered: Iterable[RenderedFile], repository: Path) -> list[Problem]:
    problems: list[Problem] = []
    for entry in rendered:
        if entry.limit is not None and len(entry.whole_part) > entry.limit:
            message = (
                f"{entry.path} needs {len(entry.whole_part)} characters in the part that must "
                f"stay whole, over the limit of {entry.limit}. "
                "Move knowledge out of this node, or attach fewer directives."
            )
            problems.append(Problem(repository / entry.node_path, 1, "size", message))
        lines = len(entry.text.split("\n")) - entry.text.endswith("\n")
        if entry.line_limit is not None and lines > entry.line_limit:
            message = (
                f"{entry.path} has {lines} lines, over the budget of {entry.line_limit}. "
                "Move knowledge out of this node, or attach fewer directives."
            )
            problems.append(Problem(repository / entry.node_path, 1, "size", message))
    return problems


def candidate_files(repository: Path) -> Iterator[Path]:
    yield repository / ROOT_FILE
    yield from (repository / RULES_FOLDER).rglob("*.md")
    yield from (repository / SKILLS_FOLDER).glob(f"*/{SKILL_FILE_NAME}")
    yield from (repository / SKILLS_FOLDER).glob(f"*/{SCRIPTS_FOLDER_NAME}/**/*")
    yield from (repository / SKILLS_FOLDER).glob(f"*/{STEPS_FOLDER_NAME}/*{STEP_SUFFIX}")
    yield from (repository / REFERENCES_FOLDER).glob("*.md")


def review_candidates(repository: Path) -> Iterator[Path]:
    yield from (repository / REVIEW_FOLDER).rglob("*.md")
    yield from (repository / REVIEW_SKILLS_FOLDER).glob(f"*/{SCRIPTS_FOLDER_NAME}/**/*")


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
