# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportMissingTypeStubs=false
import re
import shutil
import subprocess
from io import StringIO
from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING, Any, cast

import pytest
from ruamel.yaml import YAML
from typer.testing import CliRunner

from knowledge_architecture.cli import app
from knowledge_architecture.compiler import compile_items, compile_tree
from knowledge_architecture.parser import ParsedNode, parse_source
from knowledge_architecture.runtime import (
    MARKER,
    REVIEW_FOLDER,
    LoadMechanism,
    RuntimeView,
    build_view,
    claude_code,
    generate_runtime,
    is_generated,
    local_links,
    render_files,
    resolves,
    review_path,
)
from knowledge_architecture.runtime.claude_code import (
    ON_DEMAND_CHARACTERS,
    SKILL_KEPT_CHARACTERS,
    SKILL_KEPT_TOKENS,
    RenderedFile,
    size_problems,
    state_sentence,
)
from knowledge_architecture.runtime.files import apply_files
from knowledge_architecture.runtime.view import DirectiveCounts

if TYPE_CHECKING:
    from collections.abc import Iterable

REPO = Path(__file__).resolve().parents[1]
ENGINE = REPO / "engine/knowledge_architecture/runtime"
RUNNER = CliRunner()
GIT = shutil.which("git") or "git"
REVIEW = REVIEW_FOLDER.as_posix()
TREE_FOLDERS = ("knowledge", "skills", "governance")
SKILL_BODY = "## Procedure\n\n1. Read each directive that this skill lists.\n"
TOOL_KEPT_TOKENS = 5_000
LOW_CHARACTERS_PER_TOKEN = 3
TOOL_ON_DEMAND_CHARACTERS = 40_000
USAGE_ERROR = 2
RULE_LINE = "- Run the {0} check. ^{0}\n  - scope: {1}\n  - status: {2}\n  - origin: template\n"


def rule(directive_id: str, status: str = "accepted", scope: str = "subtree") -> str:
    return RULE_LINE.format(directive_id, scope, status)


def node(
    node_id: str,
    kind: str = "ka:Domain",
    *,
    front: str = "",
    rules: Iterable[str] = (),
    body: str = "",
) -> str:
    extra = "knowledge_type: domain\n" if kind != "ka:Root" else ""
    text = f"---\nid: {node_id}\nkind: {kind}\ntitle: {node_id}\nstatus: proposed\n"
    text += f"origin: template\n{extra}{front}---\n"
    if kind not in {"ka:Root", "ka:Skill"}:
        text += f"\n## Definition\n\nThe meaning of {node_id}.\n"
    joined = "".join(rules)
    if joined:
        text += f"\n## Directives\n\n{joined}"
    return f"{text}\n{body}" if body else text


def pointer(kind: str, target_id: str, *patterns: str) -> str:
    text = f"  - kind: ka:{kind}\n    target: {target_id}\n    trigger: You need {target_id}.\n"
    if patterns:
        text += "    paths:\n" + "".join(f'      - "{pattern}"\n' for pattern in patterns)
    return text


def pointers(*entries: str) -> str:
    return "pointers:\n" + "".join(entries)


SKILL_FRONT = "description: Review a sample. Use when a sample needs a review.\nuses: [gamma]\n"
SAMPLE = {
    "knowledge/node.md": node(
        "root",
        "ka:Root",
        front=pointers(
            pointer("TextPointer", "alpha"),
            pointer("PathPointer", "gamma", "src/**/*"),
            pointer("AlwaysPointer", "delta"),
            pointer("TextPointer", "policies"),
        ),
        body="## Architecture\n\nA fact that no file shows.\n",
    ),
    "knowledge/alpha/node.md": node(
        "alpha",
        front=pointers(pointer("TextPointer", "beta"), pointer("SkillPointer", "review")),
        rules=[rule("keep"), rule("wait", "proposed"), rule("faded", "deprecated", "node")],
    ),
    "knowledge/alpha/beta/node.md": node(
        "beta",
        "ka:Concept",
        front=(
            "broader: [alpha]\nexceptions:\n"
            "  - directive: wait\n    reason: A reason for wait.\n    status: proposed\n"
            "  - directive: keep\n    reason: A reason for keep.\n    status: accepted\n"
        ),
        rules=[rule("bound", scope="node")],
    ),
    "knowledge/gamma/node.md": node(
        "gamma",
        front=pointers(pointer("PathPointer", "delta", "lib/**/*")),
        rules=[rule("solid", scope="node")],
    ),
    "knowledge/delta/node.md": node("delta", body="## Notes\n\nThe body of delta.\n"),
    "governance/policies/node.md": node(
        "policies",
        front="governs: [policies, lifecycle]\n" + pointers(pointer("TextPointer", "lifecycle")),
    ),
    "governance/policies/lifecycle/node.md": node(
        "lifecycle", "ka:Concept", front="broader: [policies]\ngoverns: [lifecycle]\n"
    ),
    "skills/review/node.md": node(
        "review",
        "ka:Skill",
        front=SKILL_FRONT + pointers(pointer("TextPointer", "gamma")),
        rules=[rule("own-rule", scope="node")],
        body=SKILL_BODY,
    ),
}


def parsed(sources: dict[str, str]) -> list[ParsedNode]:
    items: list[ParsedNode] = []
    for relative, text in sources.items():
        result = parse_source(text, Path(relative))
        assert isinstance(result, ParsedNode), result
        items.append(result)
    return items


def view_of(sources: dict[str, str] | None = None, *, proposals: bool = False) -> RuntimeView:
    items = parsed(SAMPLE if sources is None else sources)
    return build_view(compile_items(items, Path(), proposals=proposals))


def rendered(
    sources: dict[str, str] | None = None, *, proposals: bool = False
) -> dict[str, RenderedFile]:
    view = view_of(sources, proposals=proposals)
    return {entry.path.as_posix(): entry for entry in render_files(view)}


def text_of(path: str, *, proposals: bool = False) -> str:
    return rendered(proposals=proposals)[path].text


def write_tree(repository: Path, sources: dict[str, str] | None = None) -> None:
    def no_branch_files(folder: str, names: list[str]) -> list[str]:
        return [name for name in names if Path(folder).name == "branches" and name != ".gitkeep"]

    shutil.copytree(
        REPO / "governance/language", repository / "governance/language", ignore=no_branch_files
    )
    (repository / "skills").mkdir(exist_ok=True)
    for relative, text in (SAMPLE if sources is None else sources).items():
        path = repository / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


def disk_files(repository: Path) -> dict[str, bytes]:
    return {
        path.relative_to(repository).as_posix(): path.read_bytes()
        for path in sorted(repository.rglob("*"))
        if path.is_file() and ".git" not in path.relative_to(repository).parts
    }


def git(repository: Path, *arguments: str) -> str:
    return subprocess.run(  # noqa: S603
        [GIT, "-C", str(repository), *arguments],
        capture_output=True,
        check=True,
        text=True,
    ).stdout


def committed_repository(folder: Path) -> Path:
    write_tree(folder)
    git(folder, "init", "-q", "--template=", "--initial-branch=main")
    git(folder, "config", "user.name", "Test")
    git(folder, "config", "user.email", "test@example.com")
    assert not generate_runtime(folder).problems
    git(folder, "add", "-A")
    git(folder, "commit", "-qm", "first")
    return folder


def codes(problems: Iterable[Any]) -> list[str]:
    return [problem.code for problem in problems]


def front_matter(text: str) -> dict[str, Any]:
    closing = text.index("\n---\n", 4)
    return cast("dict[str, Any]", YAML(typ="safe").load(StringIO(text[4:closing])))


def test_each_pointer_kind_maps_to_one_load_mechanism() -> None:
    view = view_of()
    mechanisms = {line.target.id: line.mechanism for line in view.root.pointers}
    assert mechanisms == {
        "alpha": LoadMechanism.TEXT,
        "gamma": LoadMechanism.PATH,
        "delta": LoadMechanism.ALWAYS,
        "policies": LoadMechanism.TEXT,
    }
    alpha = next(entry for entry in view.folders if entry.link.id == "alpha")
    assert {line.target.id: line.mechanism for line in alpha.pointers} == {
        "beta": LoadMechanism.TEXT,
        "review": LoadMechanism.SKILL,
    }


def test_each_node_has_one_generated_file() -> None:
    assert sorted(rendered()) == [
        ".claude/rules/knowledge/delta.md",
        ".claude/rules/knowledge/gamma.md",
        ".claude/skills/review/SKILL.md",
        "AGENTS.md",
        "governance/policies/AGENTS.md",
        "governance/policies/lifecycle/AGENTS.md",
        "knowledge/alpha/AGENTS.md",
        "knowledge/alpha/beta/AGENTS.md",
    ]


def test_a_path_rule_holds_each_pattern_and_the_file_of_its_node() -> None:
    assert front_matter(text_of(".claude/rules/knowledge/gamma.md")) == {
        "paths": ["knowledge/gamma/node.md", "src/**/*"],
    }


def test_a_path_rule_merges_the_patterns_of_two_pointers() -> None:
    sources = {
        **SAMPLE,
        "knowledge/alpha/node.md": node(
            "alpha",
            front=pointers(
                pointer("PathPointer", "gamma", "lib/**/*"),
                pointer("TextPointer", "beta"),
                pointer("SkillPointer", "review"),
            ),
            rules=[rule("keep"), rule("wait", "proposed")],
        ),
    }
    text = rendered(sources)[".claude/rules/knowledge/gamma.md"].text
    assert front_matter(text)["paths"] == ["knowledge/gamma/node.md", "lib/**/*", "src/**/*"]


def test_an_always_pointer_gives_a_rule_with_no_paths_and_wins_over_a_path_pointer() -> None:
    text = text_of(".claude/rules/knowledge/delta.md")
    assert text.startswith(MARKER)
    assert "paths" not in text


def test_a_rule_holds_the_definition_and_the_body() -> None:
    text = text_of(".claude/rules/knowledge/delta.md")
    assert "## Definition\n\nThe meaning of delta.\n" in text
    assert "## Notes\n\nThe body of delta.\n" in text


def test_a_folder_file_leaves_the_definition_to_the_node_file() -> None:
    assert "The meaning of alpha" not in text_of("knowledge/alpha/AGENTS.md")


def test_a_pointer_to_the_root_gives_no_rule() -> None:
    sources = {
        **SAMPLE,
        "knowledge/delta/node.md": node(
            "delta", front=pointers(pointer("PathPointer", "root", "docs/**/*"))
        ),
    }
    assert ".claude/rules/knowledge/root.md" not in rendered(sources)


def test_a_skill_behind_a_path_pointer_receives_a_rule_and_a_skill_file() -> None:
    sources = {
        **SAMPLE,
        "knowledge/delta/node.md": node(
            "delta", front=pointers(pointer("PathPointer", "review", "docs/**/*"))
        ),
    }
    files = rendered(sources)
    assert ".claude/skills/review/SKILL.md" in files
    assert ".claude/rules/knowledge/review.md" in files


def test_a_policy_is_not_a_domain_in_the_root() -> None:
    text = text_of("AGENTS.md")
    domains = text[text.index("## Domains") : text.index("## Governance")]
    governance = text[text.index("## Governance") : text.index("## Skills")]
    assert "alpha" in domains
    assert "policies" not in domains
    assert "Read [policies](governance/policies/node.md)." in governance
    assert "Read [lifecycle](governance/policies/lifecycle/node.md)." in governance


def test_the_root_lists_a_domain_that_it_has_no_pointer_to() -> None:
    sources = {
        **SAMPLE,
        "knowledge/node.md": node(
            "root", "ka:Root", front=pointers(pointer("TextPointer", "policies"))
        ),
    }
    text = rendered(sources)["AGENTS.md"].text
    assert "- Read [alpha](knowledge/alpha/node.md).\n" in text


def test_the_root_names_each_skill_with_its_description() -> None:
    assert "- `review`: Review a sample. Use when a sample needs a review.\n" in text_of(
        "AGENTS.md"
    )


def test_the_root_leaves_out_an_empty_section() -> None:
    sources = {
        "knowledge/node.md": node(
            "root", "ka:Root", front=pointers(pointer("TextPointer", "lone"))
        ),
        "knowledge/lone/node.md": node("lone"),
    }
    text = rendered(sources)["AGENTS.md"].text
    assert "## Domains" in text
    for heading in ("## Governance", "## Skills", "## References", "## Architecture"):
        assert heading not in text


def test_the_root_holds_a_pointer_to_a_node_that_is_not_a_domain() -> None:
    text = text_of("AGENTS.md")
    assert "## References" not in text
    sources = {
        **SAMPLE,
        "knowledge/node.md": node(
            "root",
            "ka:Root",
            front=pointers(pointer("TextPointer", "alpha"), pointer("TextPointer", "beta")),
        ),
    }
    text = rendered(sources)["AGENTS.md"].text
    assert "## References\n\n- You need beta. Read [beta](knowledge/alpha/beta/node.md).\n" in text


@pytest.mark.parametrize(
    ("counts", "sentence"),
    [
        ((0, 0, 0), "No directive is in force."),
        (
            (0, 81, 1),
            (
                "No directive is in force. "
                "The graph holds 81 directives and 1 exception that are not in force."
            ),
        ),
        ((1, 1, 0), "1 directive is in force. The graph holds 1 directive that is not in force."),
        ((3, 0, 1), "3 directives are in force. The graph holds 1 exception that is not in force."),
        (
            (2, 2, 2),
            (
                "2 directives are in force. "
                "The graph holds 2 directives and 2 exceptions that are not in force."
            ),
        ),
    ],
)
def test_the_state_sentence_reads_the_counts(counts: tuple[int, int, int], sentence: str) -> None:
    assert state_sentence(DirectiveCounts(*counts)) == sentence


def test_the_root_counts_what_is_in_force_in_each_result() -> None:
    expected = (
        "4 directives are in force. "
        "The graph holds 2 directives and 1 exception that are not in force."
    )
    assert expected in text_of("AGENTS.md")
    assert expected in text_of(f"{REVIEW}/AGENTS.proposals.md", proposals=True)


def test_the_root_lists_a_directive_that_it_holds() -> None:
    root = node(
        "root",
        "ka:Root",
        front=pointers(pointer("TextPointer", "alpha")),
        rules=[rule("root-rule", scope="node")],
    )
    text = rendered({**SAMPLE, "knowledge/node.md": root})["AGENTS.md"].text
    assert "- Run the root-rule check. ^root-rule\n" in text


def test_the_default_result_holds_only_what_is_in_force() -> None:
    for entry in rendered().values():
        assert "^wait" not in entry.text
        assert "^faded" not in entry.text
        assert "(proposed)" not in entry.text
        assert "NOT IN FORCE" not in entry.text


def test_the_review_result_marks_each_proposal() -> None:
    text = text_of(f"{REVIEW}/claude/skills/review/SKILL.proposals.md", proposals=True)
    assert "NOT IN FORCE" in text
    alpha = text_of(f"{REVIEW}/knowledge/alpha/AGENTS.proposals.md", proposals=True)
    assert "- Run the wait check. ^wait (proposed)\n" in alpha
    assert "- Run the keep check. ^keep\n" in alpha
    assert "^faded" not in alpha


def test_each_review_file_opens_with_the_notice() -> None:
    for entry in rendered(proposals=True).values():
        title_end = entry.text.index("\n# ") + 1
        following = entry.text[title_end:].split("\n")
        assert following[2].startswith("NOT IN FORCE.")


def test_an_exception_stops_a_directive_and_states_the_reason() -> None:
    text = text_of("knowledge/alpha/beta/AGENTS.md")
    assert "^keep" not in text.split("## Exceptions")[0]
    assert "- `keep` does not apply at this node. A reason for keep.\n" in text
    assert "A reason for wait" not in text
    review = text_of(f"{REVIEW}/knowledge/alpha/beta/AGENTS.proposals.md", proposals=True)
    assert "- `wait` does not apply at this node. A reason for wait. (proposed)\n" in review
    assert "^wait" not in review.split("## Exceptions")[0]


def test_a_node_with_no_directive_states_that_fact() -> None:
    assert "No directive is in force at this node.\n" in text_of(
        "knowledge/gamma/node.md".replace(
            "knowledge/gamma/node.md", ".claude/rules/knowledge/delta.md"
        )
    )
    review = text_of(f"{REVIEW}/claude/rules/knowledge/delta.proposals.md", proposals=True)
    assert "No directive applies at this node.\n" in review


def test_a_group_links_to_the_node_that_holds_the_directive() -> None:
    text = text_of(".claude/skills/review/SKILL.md")
    assert (
        "From [gamma](../../../knowledge/gamma/node.md):\n\n- Run the solid check. ^solid\n" in text
    )
    assert "From [review](../../../skills/review/node.md):\n\n- Run the own-rule check." in text


@pytest.mark.parametrize(
    ("path", "order"),
    [
        (
            ".claude/skills/review/SKILL.md",
            ["## Directives", "^own-rule", "## Procedure", "## References", "Read [gamma]"],
        ),
        (
            ".claude/rules/knowledge/gamma.md",
            ["## Directives", "^solid", "## Definition", "## References"],
        ),
        ("knowledge/alpha/AGENTS.md", ["## Directives", "^keep", "## References", "Read [beta]"]),
        ("AGENTS.md", ["## Directives", "## Architecture", "## Domains", "## Governance"]),
    ],
)
def test_each_file_puts_directives_then_procedures_then_references(
    path: str, order: list[str]
) -> None:
    text = text_of(path)
    places = [text.index(part) for part in order]
    assert places == sorted(places)


def test_each_generated_file_holds_the_marker() -> None:
    for entry in [*rendered().values(), *rendered(proposals=True).values()]:
        assert is_generated(entry.text.encode("utf-8")), entry.path


def test_a_pointer_line_follows_its_mechanism() -> None:
    references = rendered(
        {
            **SAMPLE,
            "knowledge/node.md": node(
                "root",
                "ka:Root",
                front=pointers(
                    pointer("TextPointer", "alpha"),
                    pointer("PathPointer", "beta", "src/**/*"),
                    pointer("AlwaysPointer", "lifecycle"),
                    pointer("SkillPointer", "review"),
                    pointer("TextPointer", "gamma"),
                ),
            ),
        }
    )["AGENTS.md"].text
    assert "- You need beta. [beta](knowledge/alpha/beta/node.md) loads by itself.\n" in references
    assert (
        "- You need lifecycle. [lifecycle](governance/policies/lifecycle/node.md) "
        "is always loaded.\n"
    ) in references
    assert "- You need review. Use the skill `review`.\n" in references
    assert "- You need gamma. Read [gamma](knowledge/gamma/node.md).\n" in references


def test_a_folder_file_lists_pointers_with_real_paths() -> None:
    text = text_of("knowledge/alpha/AGENTS.md")
    assert "- You need beta. Read [beta](beta/node.md).\n" in text
    assert "- You need review. Use the skill `review`.\n" in text


def test_a_review_link_resolves_from_the_review_folder() -> None:
    text = text_of(f"{REVIEW}/knowledge/alpha/AGENTS.proposals.md", proposals=True)
    assert "# [alpha](../../../../knowledge/alpha/node.md)\n" in text


def test_a_review_path_holds_no_name_that_the_tool_loads() -> None:
    assert review_path(PurePosixPath("AGENTS.md")).as_posix() == "AGENTS.proposals.md"
    assert (
        review_path(PurePosixPath(".claude/skills/a/SKILL.md")).as_posix()
        == "claude/skills/a/SKILL.proposals.md"
    )
    assert (
        review_path(PurePosixPath(".claude/rules/knowledge/a.md")).as_posix()
        == "claude/rules/knowledge/a.proposals.md"
    )
    assert (
        review_path(PurePosixPath(".claude/skills/.draft/SKILL.md")).as_posix()
        == "claude/skills/.draft/SKILL.proposals.md"
    )
    for path in rendered(proposals=True):
        parts = PurePosixPath(path).parts
        assert parts[:2] == REVIEW_FOLDER.parts
        assert not {".claude", "AGENTS.md", "CLAUDE.md", "SKILL.md"} & set(parts)


def test_a_skill_file_names_itself_and_keeps_its_description() -> None:
    text = text_of(".claude/skills/review/SKILL.md")
    assert front_matter(text) == {
        "name": "review",
        "description": "Review a sample. Use when a sample needs a review.",
    }
    assert text.startswith("---\n")


def test_the_skill_states_that_an_agent_can_invoke_it_again() -> None:
    text = text_of(".claude/skills/review/SKILL.md")
    assert text.index("invoke the skill again") < text.index("## Directives")


def test_a_title_makes_no_link() -> None:
    hostile = node("delta").replace("title: delta", 'title: "Fake](../../x) [a"')
    sources = {**SAMPLE, "knowledge/delta/node.md": hostile}
    text = rendered(sources)[".claude/rules/knowledge/delta.md"].text
    assert "# [Fake\\](../../x) \\[a](../../../knowledge/delta/node.md)\n" in text
    assert local_links(text) == ["../../../knowledge/delta/node.md"]


def test_a_backslash_in_a_title_stays_literal() -> None:
    hostile = node("delta").replace("title: delta", 'title: "a\\\\](b)"')
    sources = {**SAMPLE, "knowledge/delta/node.md": hostile}
    text = rendered(sources)[".claude/rules/knowledge/delta.md"].text
    assert local_links(text) == ["../../../knowledge/delta/node.md"]


def test_a_template_expression_in_a_node_stays_literal() -> None:
    sources = {
        **SAMPLE,
        "knowledge/delta/node.md": node("delta", body="## Notes\n\nKeep {{ 7 * 7 }} as text.\n"),
    }
    assert "Keep {{ 7 * 7 }} as text." in rendered(sources)[".claude/rules/knowledge/delta.md"].text


def test_a_description_that_breaks_plain_yaml_stays_one_string() -> None:
    description = "'Review: \"a\" sample, #1. Use when\n  a sample: needs a review.'"
    front = f"description: {description}\nuses: [gamma]\n"
    sources = {**SAMPLE, "skills/review/node.md": node("review", "ka:Skill", front=front)}
    text = rendered(sources)[".claude/skills/review/SKILL.md"].text
    assert (
        front_matter(text)["description"]
        == 'Review: "a" sample, #1. Use when a sample: needs a review.'
    )


def test_a_description_keeps_each_character_that_is_not_ascii() -> None:
    front = "description: Review a café sample. Use when a sample needs a review.\nuses: [gamma]\n"
    sources = {**SAMPLE, "skills/review/node.md": node("review", "ka:Skill", front=front)}
    assert (
        "café" in rendered(sources)[".claude/skills/review/SKILL.md"].text.partition("\n---\n")[0]
    )


def test_a_glob_that_breaks_plain_yaml_stays_one_string() -> None:
    sources = {
        **SAMPLE,
        "knowledge/delta/node.md": node(
            "delta", front=pointers(pointer("PathPointer", "gamma", "*.md", "a: {b}/**/*"))
        ),
    }
    text = rendered(sources)[".claude/rules/knowledge/gamma.md"].text
    assert {"*.md", "a: {b}/**/*"} <= set(front_matter(text)["paths"])


def test_a_path_with_a_space_gives_a_link_that_resolves(tmp_path: Path) -> None:
    sources = dict(SAMPLE)
    sources["knowledge/my folder/gamma/node.md"] = sources.pop("knowledge/gamma/node.md")
    write_tree(tmp_path, sources)
    report = generate_runtime(tmp_path)
    assert not report.problems
    root = (tmp_path / "AGENTS.md").read_text(encoding="utf-8")
    assert "(knowledge/my%20folder/gamma/node.md)" in root


def test_the_same_tree_gives_the_same_files_in_any_order() -> None:
    forward = render_files(view_of())
    backward = dict(reversed(SAMPLE.items()))
    assert render_files(view_of(backward)) == forward


@pytest.mark.parametrize(
    "data",
    [
        f"{MARKER}\n# Title\n".encode(),
        f"---\npaths:\n  - a\n---\n{MARKER}\n# Title\n".encode(),
        f"{MARKER}".encode(),
    ],
)
def test_the_marker_makes_a_file_generated(data: bytes) -> None:
    assert is_generated(data)


@pytest.mark.parametrize(
    "data",
    [
        b"",
        b"# A hand-written file\n",
        f"# Title\n{MARKER}\n".encode(),
        f"{MARKER} more\n".encode(),
        f"---\nno closing line\n{MARKER}\n".encode(),
        b"---\npaths:\n  - a\n---\n",
        b"---\npaths:\n  - a\n---",
        f"---\na: b\n---\n# Title\n{MARKER}\n".encode(),
        b"\xff\xfe binary \x00",
    ],
)
def test_a_file_without_the_marker_in_place_is_not_generated(data: bytes) -> None:
    assert not is_generated(data)


def test_the_link_reader_finds_links_and_images_and_skips_others() -> None:
    text = (
        "[a](one.md) ![b](two.png) [c](https://example.com) [d](mailto:a@example.com) "
        "[e](#here) [f](three.md#part)\n\n<!-- [g](comment.md) -->\n"
    )
    assert local_links(text) == ["one.md", "two.png", "three.md#part"]


def test_a_link_must_resolve_inside_the_repository(tmp_path: Path) -> None:
    repository = tmp_path / "repo"
    (repository / "a b").mkdir(parents=True)
    (repository / "a b/node.md").write_text("x", encoding="utf-8")
    (tmp_path / "secret.md").write_text("x", encoding="utf-8")
    assert resolves("a%20b/node.md", repository, repository)
    assert resolves("a%20b/node.md#part", repository, repository)
    assert resolves("../a%20b/node.md", repository / "a b", repository)
    assert not resolves("missing.md", repository, repository)
    assert not resolves("../secret.md", repository, repository)
    assert not resolves(str(tmp_path / "secret.md"), repository, repository)
    assert not resolves("a%00b.md", repository, repository)


def test_a_broken_link_in_a_body_stops_the_run(tmp_path: Path) -> None:
    sources = {
        **SAMPLE,
        "knowledge/delta/node.md": node(
            "delta", body="## Notes\n\nSee [the other node](../gamma/node.md).\n"
        ),
    }
    write_tree(tmp_path, sources)
    report = generate_runtime(tmp_path)
    assert codes(report.problems) == ["link"]
    assert str(tmp_path / "knowledge/delta/node.md") in str(report.problems[0])
    assert ".claude/rules/knowledge/delta.md" in str(report.problems[0])
    assert not (tmp_path / "AGENTS.md").exists()


def file_of(whole: str, limit: int | None) -> RenderedFile:
    return RenderedFile(PurePosixPath("a.md"), "text", "knowledge/a/node.md", whole, limit)


def test_the_size_check_reads_the_limit_of_each_file(tmp_path: Path) -> None:
    over = file_of("x" * 11, 10)
    assert codes(size_problems([over], tmp_path)) == ["size"]
    assert str(tmp_path / "knowledge/a/node.md") in str(size_problems([over], tmp_path)[0])
    assert not size_problems([file_of("x" * 10, 10)], tmp_path)
    assert not size_problems([file_of("x" * 100_000, None)], tmp_path)


def test_the_limits_follow_the_tool() -> None:
    assert SKILL_KEPT_TOKENS == TOOL_KEPT_TOKENS
    assert SKILL_KEPT_CHARACTERS == TOOL_KEPT_TOKENS * LOW_CHARACTERS_PER_TOKEN
    assert ON_DEMAND_CHARACTERS == TOOL_ON_DEMAND_CHARACTERS
    files = rendered()
    assert files["AGENTS.md"].limit is None
    assert files[".claude/skills/review/SKILL.md"].limit == SKILL_KEPT_CHARACTERS
    assert files[".claude/rules/knowledge/gamma.md"].limit == ON_DEMAND_CHARACTERS
    assert files["knowledge/alpha/AGENTS.md"].limit == ON_DEMAND_CHARACTERS


def test_the_kept_part_of_a_skill_holds_the_directives_and_not_the_rest() -> None:
    entry = rendered()[".claude/skills/review/SKILL.md"]
    assert "^own-rule" in entry.whole_part
    assert "## Procedure" not in entry.whole_part
    assert "## References" not in entry.whole_part
    assert "## Procedure" in entry.text


def test_too_many_directives_at_a_skill_give_a_size_problem(tmp_path: Path) -> None:
    long_rules = [rule(f"rule-{number:03}", scope="node") for number in range(600)]
    sources = {
        **SAMPLE,
        "skills/review/node.md": node(
            "review", "ka:Skill", front=SKILL_FRONT, rules=long_rules, body=SKILL_BODY
        ),
    }
    entries = rendered(sources)
    assert codes(size_problems(entries.values(), tmp_path)) == ["size"]


def test_a_long_procedure_gives_no_size_problem(tmp_path: Path) -> None:
    body = SKILL_BODY + "\n## Notes\n\n" + "A long note. " * 2_000 + "\n"
    sources = {
        **SAMPLE,
        "skills/review/node.md": node("review", "ka:Skill", front=SKILL_FRONT, body=body),
    }
    entry = rendered(sources)[".claude/skills/review/SKILL.md"]
    assert len(entry.text) > SKILL_KEPT_CHARACTERS
    assert not size_problems([entry], tmp_path)


@pytest.mark.parametrize("limit", ["SKILL_KEPT_CHARACTERS", "ON_DEMAND_CHARACTERS"])
def test_a_size_problem_stops_the_run(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, limit: str
) -> None:
    write_tree(tmp_path)
    monkeypatch.setattr(claude_code, limit, 10)
    report = generate_runtime(tmp_path)
    assert "size" in codes(report.problems)
    assert report.written == ()
    assert not (tmp_path / "AGENTS.md").exists()


def test_a_run_writes_each_file_and_a_second_run_changes_nothing(tmp_path: Path) -> None:
    write_tree(tmp_path)
    first = generate_runtime(tmp_path)
    assert not first.problems
    assert set(first.written) == {PurePosixPath(path) for path in rendered()}
    assert first.files == tuple(PurePosixPath(path) for path in rendered())
    before = {path: tmp_path.joinpath(path).stat().st_mtime_ns for path in rendered()}
    second = generate_runtime(tmp_path)
    assert second.written == ()
    assert second.removed == ()
    assert before == {path: tmp_path.joinpath(path).stat().st_mtime_ns for path in rendered()}


def test_a_run_rewrites_a_hand_edit(tmp_path: Path) -> None:
    write_tree(tmp_path)
    generate_runtime(tmp_path)
    fresh = (tmp_path / "AGENTS.md").read_bytes()
    (tmp_path / "AGENTS.md").write_bytes(fresh + b"\n- A hand edit.\n")
    report = generate_runtime(tmp_path)
    assert report.written == (PurePosixPath("AGENTS.md"),)
    assert (tmp_path / "AGENTS.md").read_bytes() == fresh


def test_a_run_removes_its_own_stale_files_and_only_its_own(tmp_path: Path) -> None:
    write_tree(tmp_path)
    generate_runtime(tmp_path)
    hand_written = {
        ".claude/rules/hand-written.md": b"# Mine\n",
        ".claude/rules/knowledge/hand-written.md": b"# Mine\n",
        ".claude/skills/mine/SKILL.md": b"---\nname: mine\n---\n# Mine\n",
        "knowledge/alpha/beta/notes.txt": b"# Mine\n",
        "src/AGENTS.md": f"{MARKER}\n# Outside each scanned folder\n".encode(),
    }
    for relative, data in hand_written.items():
        tmp_path.joinpath(relative).parent.mkdir(parents=True, exist_ok=True)
        tmp_path.joinpath(relative).write_bytes(data)
    (tmp_path / ".claude/skills/review/extra.md").write_bytes(b"# Mine\n")
    without_review = {
        relative: text for relative, text in SAMPLE.items() if not relative.startswith("skills/")
    }
    without_review["knowledge/alpha/node.md"] = node(
        "alpha", front=pointers(pointer("TextPointer", "beta")), rules=[rule("keep")]
    )
    without_review["knowledge/alpha/beta/node.md"] = node(
        "beta", "ka:Concept", front="broader: [alpha]\n"
    )
    del without_review["knowledge/delta/node.md"]
    without_review["knowledge/node.md"] = node(
        "root",
        "ka:Root",
        front=pointers(
            pointer("TextPointer", "alpha"),
            pointer("TextPointer", "gamma"),
            pointer("TextPointer", "policies"),
        ),
    )
    without_review["knowledge/gamma/node.md"] = node("gamma")
    shutil.rmtree(tmp_path / "skills/review")
    (tmp_path / "skills").mkdir(exist_ok=True)
    (tmp_path / "knowledge/delta/node.md").unlink()
    for relative, text in without_review.items():
        tmp_path.joinpath(relative).write_text(text, encoding="utf-8")
    report = generate_runtime(tmp_path)
    assert not report.problems
    assert set(report.removed) == {
        PurePosixPath(".claude/rules/knowledge/delta.md"),
        PurePosixPath(".claude/rules/knowledge/gamma.md"),
        PurePosixPath(".claude/skills/review/SKILL.md"),
    }
    for relative, data in hand_written.items():
        assert tmp_path.joinpath(relative).read_bytes() == data
    assert (tmp_path / ".claude/skills/review/extra.md").exists()
    assert (tmp_path / "knowledge/gamma/AGENTS.md").exists()


def test_a_removal_prunes_empty_folders_and_keeps_a_top_folder(tmp_path: Path) -> None:
    for relative in ("knowledge/a/b/AGENTS.md", ".claude/skills/x/SKILL.md"):
        path = tmp_path / relative
        path.parent.mkdir(parents=True)
        path.write_text(f"{MARKER}\n", encoding="utf-8")
    keep = tmp_path / "knowledge/keep/AGENTS.md"
    keep.parent.mkdir()
    keep.write_text(f"{MARKER}\n", encoding="utf-8")
    result = apply_files(
        tmp_path,
        {PurePosixPath("knowledge/keep/AGENTS.md"): keep.read_bytes()},
        [tmp_path / "knowledge/a/b/AGENTS.md", tmp_path / ".claude/skills/x/SKILL.md", keep],
    )
    assert not result.problems
    assert not (tmp_path / "knowledge/a").exists()
    assert keep.exists()
    assert not (tmp_path / ".claude/skills").exists()
    assert (tmp_path / ".claude").is_dir()


def test_a_removal_keeps_a_folder_that_still_holds_a_file(tmp_path: Path) -> None:
    stale = tmp_path / "knowledge/a/b/AGENTS.md"
    stale.parent.mkdir(parents=True)
    stale.write_text(f"{MARKER}\n", encoding="utf-8")
    (tmp_path / "knowledge/a/note.md").write_text("x", encoding="utf-8")
    assert not apply_files(tmp_path, {}, [stale]).problems
    assert not (tmp_path / "knowledge/a/b").exists()
    assert (tmp_path / "knowledge/a/note.md").exists()


def test_a_stale_scan_skips_a_link_and_a_folder(tmp_path: Path) -> None:
    outside = tmp_path / "outside.md"
    outside.write_text(f"{MARKER}\n", encoding="utf-8")
    link = tmp_path / "AGENTS.md"
    link.symlink_to(outside)
    folder = tmp_path / "folder"
    folder.mkdir()
    result = apply_files(tmp_path, {}, [link, folder])
    assert not result.problems
    assert link.is_symlink()
    assert outside.exists()
    assert folder.is_dir()


def test_a_stale_scan_does_not_follow_a_linked_folder(tmp_path: Path) -> None:
    outside = tmp_path / "outside"
    outside.mkdir()
    file = outside / "SKILL.md"
    file.write_text(f"{MARKER}\n", encoding="utf-8")
    skills = tmp_path / ".claude/skills"
    skills.mkdir(parents=True)
    (skills / "shared").symlink_to(outside, target_is_directory=True)
    result = apply_files(tmp_path, {}, claude_code.candidate_files(tmp_path))
    assert not result.problems
    assert result.removed == ()
    assert file.exists()


def test_the_scan_finds_a_generated_file_in_each_place(tmp_path: Path) -> None:
    places = [
        "AGENTS.md",
        "knowledge/a/AGENTS.md",
        "skills/b/AGENTS.md",
        "governance/policies/c/AGENTS.md",
        ".claude/rules/knowledge/d.md",
        ".claude/rules/knowledge/deep/e.md",
        ".claude/skills/f/SKILL.md",
    ]
    outside = [
        "src/AGENTS.md",
        ".claude/rules/g.md",
        ".claude/skills/h/deep/SKILL.md",
        ".claude/skills/SKILL.md",
    ]
    for relative in [*places, *outside]:
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"{MARKER}\n", encoding="utf-8")
    result = apply_files(tmp_path, {}, claude_code.candidate_files(tmp_path))
    assert {path.as_posix() for path in result.removed} == set(places)
    for relative in outside:
        assert (tmp_path / relative).exists()


def test_the_review_scan_reads_only_the_review_folder(tmp_path: Path) -> None:
    inside = tmp_path / REVIEW_FOLDER / "a/AGENTS.proposals.md"
    outside = tmp_path / "AGENTS.md"
    inside.parent.mkdir(parents=True)
    inside.write_text(f"{MARKER}\n", encoding="utf-8")
    outside.write_text(f"{MARKER}\n", encoding="utf-8")
    result = apply_files(tmp_path, {}, claude_code.review_candidates(tmp_path))
    assert result.removed == (PurePosixPath(f"{REVIEW}/a/AGENTS.proposals.md"),)
    assert outside.exists()


def test_a_hand_written_file_in_a_node_folder_fails_the_parser(tmp_path: Path) -> None:
    write_tree(tmp_path)
    path = tmp_path / "knowledge/alpha/AGENTS.md"
    path.write_bytes(b"# Mine\n")
    report = generate_runtime(tmp_path)
    assert codes(report.problems) == ["file-name"]
    assert path.read_bytes() == b"# Mine\n"
    assert not (tmp_path / "AGENTS.md").exists()


@pytest.mark.parametrize("relative", ["AGENTS.md", ".claude/skills/review/SKILL.md"])
def test_a_hand_written_file_at_a_generated_path_stops_the_run(
    tmp_path: Path, relative: str
) -> None:
    write_tree(tmp_path)
    path = tmp_path / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"# Mine\n")
    report = generate_runtime(tmp_path)
    assert codes(report.problems) == ["not-generated"]
    assert str(path) in str(report.problems[0])
    assert path.read_bytes() == b"# Mine\n"
    others = set(rendered()) - {relative}
    assert not any((tmp_path / other).exists() for other in others)


def test_a_marker_removed_by_hand_stops_the_run(tmp_path: Path) -> None:
    write_tree(tmp_path)
    generate_runtime(tmp_path)
    path = tmp_path / "AGENTS.md"
    path.write_text(path.read_text(encoding="utf-8").replace(MARKER, ""), encoding="utf-8")
    assert codes(generate_runtime(tmp_path).problems) == ["not-generated"]


def test_a_link_at_a_generated_path_stops_the_run_and_the_target_stays(tmp_path: Path) -> None:
    write_tree(tmp_path)
    target_file = tmp_path / "mine.md"
    target_file.write_bytes(f"{MARKER}\n# Mine\n".encode())
    (tmp_path / "AGENTS.md").symlink_to(target_file)
    report = generate_runtime(tmp_path)
    assert codes(report.problems) == ["not-generated"]
    assert target_file.read_bytes() == f"{MARKER}\n# Mine\n".encode()


def test_a_dangling_link_at_a_generated_path_stops_the_run(tmp_path: Path) -> None:
    write_tree(tmp_path)
    (tmp_path / "AGENTS.md").symlink_to(tmp_path / "missing.md")
    assert codes(generate_runtime(tmp_path).problems) == ["not-generated"]
    assert not (tmp_path / "missing.md").exists()


def test_a_linked_folder_in_a_generated_path_stops_the_run(tmp_path: Path) -> None:
    write_tree(tmp_path)
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    (tmp_path / ".claude").symlink_to(elsewhere)
    report = generate_runtime(tmp_path)
    assert set(codes(report.problems)) == {"not-generated"}
    assert not list(elsewhere.iterdir())


def test_a_folder_at_a_generated_path_stops_the_run(tmp_path: Path) -> None:
    write_tree(tmp_path)
    (tmp_path / "AGENTS.md").mkdir()
    assert codes(generate_runtime(tmp_path).problems) == ["not-generated"]


def test_a_file_in_place_of_a_folder_reports_a_problem(tmp_path: Path) -> None:
    write_tree(tmp_path)
    (tmp_path / ".claude").write_text("x", encoding="utf-8")
    assert codes(generate_runtime(tmp_path).problems) == ["write"]


def test_a_rejected_tree_leaves_the_committed_files(tmp_path: Path) -> None:
    write_tree(tmp_path)
    generate_runtime(tmp_path)
    before = (tmp_path / "AGENTS.md").read_bytes()
    (tmp_path / "knowledge/gamma/node.md").write_text("no front matter\n", encoding="utf-8")
    report = generate_runtime(tmp_path)
    assert report.problems
    assert report.written == ()
    assert report.removed == ()
    assert (tmp_path / "AGENTS.md").read_bytes() == before
    assert (tmp_path / "knowledge/alpha/AGENTS.md").exists()


def test_a_rejected_tree_removes_the_review_result(tmp_path: Path) -> None:
    write_tree(tmp_path)
    assert not generate_runtime(tmp_path, proposals=True).problems
    review = tmp_path / REVIEW_FOLDER
    assert review.is_dir()
    (tmp_path / "knowledge/gamma/node.md").write_text("no front matter\n", encoding="utf-8")
    report = generate_runtime(tmp_path, proposals=True)
    assert report.problems
    assert PurePosixPath(f"{REVIEW}/AGENTS.proposals.md") in report.removed
    assert not list(review.rglob("*.md"))


def test_an_empty_tree_removes_each_generated_file_and_passes(tmp_path: Path) -> None:
    write_tree(tmp_path)
    assert not generate_runtime(tmp_path).problems
    (tmp_path / ".claude/rules").mkdir(parents=True, exist_ok=True)
    (tmp_path / ".claude/rules/hand-written.md").write_bytes(b"# Mine\n")
    for folder in ("knowledge", "skills"):
        for path in (tmp_path / folder).rglob("node.md"):
            path.unlink()
    for path in (tmp_path / "governance/policies").rglob("node.md"):
        path.unlink()
    report = generate_runtime(tmp_path)
    assert not report.problems
    assert report.files == ()
    assert not (tmp_path / "AGENTS.md").exists()
    assert not list((tmp_path / "knowledge").rglob("AGENTS.md"))
    assert (tmp_path / ".claude/rules/hand-written.md").read_bytes() == b"# Mine\n"
    assert not generate_runtime(tmp_path, verify=True).problems


def test_a_review_run_writes_only_under_the_review_folder(tmp_path: Path) -> None:
    write_tree(tmp_path)
    before = disk_files(tmp_path)
    report = generate_runtime(tmp_path, proposals=True)
    assert not report.problems
    after = disk_files(tmp_path)
    assert {path: after[path] for path in before} == before
    assert all(path.startswith(f"{REVIEW}/") for path in set(after) - set(before))
    assert len(set(after) - set(before)) == len(rendered())


def test_a_default_run_leaves_the_review_result(tmp_path: Path) -> None:
    write_tree(tmp_path)
    generate_runtime(tmp_path, proposals=True)
    review = tmp_path / REVIEW_FOLDER / "AGENTS.proposals.md"
    before = review.read_bytes()
    assert not generate_runtime(tmp_path).problems
    assert review.read_bytes() == before


def test_a_review_run_removes_its_stale_files(tmp_path: Path) -> None:
    write_tree(tmp_path)
    generate_runtime(tmp_path, proposals=True)
    stale = tmp_path / REVIEW_FOLDER / "knowledge/old/AGENTS.proposals.md"
    stale.parent.mkdir(parents=True)
    stale.write_text(f"{MARKER}\n", encoding="utf-8")
    report = generate_runtime(tmp_path, proposals=True)
    assert report.removed == (PurePosixPath(f"{REVIEW}/knowledge/old/AGENTS.proposals.md"),)
    assert not stale.exists()


def test_verify_passes_on_a_clean_repository(tmp_path: Path) -> None:
    committed_repository(tmp_path)
    report = generate_runtime(tmp_path, verify=True)
    assert report.problems == []
    assert report.notes == []


def test_verify_fails_on_a_hand_edit_and_rewrites_the_file(tmp_path: Path) -> None:
    committed_repository(tmp_path)
    path = tmp_path / "AGENTS.md"
    fresh = path.read_bytes()
    path.write_bytes(fresh + b"\nA hand edit.\n")
    report = generate_runtime(tmp_path, verify=True)
    assert codes(report.problems) == ["changed"]
    assert str(path) in str(report.problems[0])
    assert path.read_bytes() == fresh


def test_verify_fails_on_a_deleted_file_and_writes_it_again(tmp_path: Path) -> None:
    committed_repository(tmp_path)
    path = tmp_path / "knowledge/alpha/AGENTS.md"
    path.unlink()
    assert codes(generate_runtime(tmp_path, verify=True).problems) == ["changed"]
    assert path.exists()


def test_verify_fails_on_a_stale_file_and_removes_it(tmp_path: Path) -> None:
    committed_repository(tmp_path)
    stale = tmp_path / "knowledge/old/AGENTS.md"
    stale.parent.mkdir()
    stale.write_text(f"{MARKER}\n", encoding="utf-8")
    report = generate_runtime(tmp_path, verify=True)
    assert codes(report.problems) == ["changed"]
    assert "No node generates" in str(report.problems[0])
    assert not stale.exists()


def test_verify_fails_on_a_generated_file_outside_the_index(tmp_path: Path) -> None:
    committed_repository(tmp_path)
    git(tmp_path, "rm", "-q", "--cached", "AGENTS.md")
    report = generate_runtime(tmp_path, verify=True)
    assert codes(report.problems) == ["not-staged"]
    assert str(tmp_path / "AGENTS.md") in str(report.problems[0])
    git(tmp_path, "add", "AGENTS.md")
    assert not generate_runtime(tmp_path, verify=True).problems


def test_verify_reports_a_new_file_once(tmp_path: Path) -> None:
    committed_repository(tmp_path)
    (tmp_path / "knowledge/alpha/AGENTS.md").unlink()
    git(tmp_path, "rm", "-q", "--cached", "knowledge/alpha/AGENTS.md")
    assert codes(generate_runtime(tmp_path, verify=True).problems) == ["changed"]
    assert codes(generate_runtime(tmp_path, verify=True).problems) == ["not-staged"]


def test_verify_notes_a_folder_outside_git(tmp_path: Path) -> None:
    write_tree(tmp_path)
    generate_runtime(tmp_path)
    report = generate_runtime(tmp_path, verify=True)
    assert report.problems == []
    assert any("index" in note for note in report.notes)


def test_a_run_without_verify_does_not_fail_on_a_change(tmp_path: Path) -> None:
    write_tree(tmp_path)
    assert not generate_runtime(tmp_path).problems


def test_verify_does_not_read_the_index_after_a_problem(tmp_path: Path) -> None:
    committed_repository(tmp_path)
    (tmp_path / "AGENTS.md").write_bytes(b"# Mine\n")
    git(tmp_path, "rm", "-q", "--cached", "knowledge/alpha/AGENTS.md")
    assert codes(generate_runtime(tmp_path, verify=True).problems) == ["not-generated"]


def test_generated_files_reach_git_and_an_excluded_file_stays_ignored(tmp_path: Path) -> None:
    committed_repository(tmp_path)
    local = tmp_path / ".claude/rules/hand-written.md"
    local.write_bytes(b"# Mine\n")
    exclude = tmp_path / ".git/info/exclude"
    exclude.parent.mkdir(parents=True, exist_ok=True)
    exclude.write_text(".claude/rules/hand-written.md\n", encoding="utf-8")
    assert not generate_runtime(tmp_path, verify=True).problems
    assert local.read_bytes() == b"# Mine\n"
    assert git(tmp_path, "status", "--porcelain") == ""
    assert git(tmp_path, "check-ignore", ".claude/rules/hand-written.md").strip()
    tracked = set(git(tmp_path, "ls-files").splitlines())
    assert set(rendered()) <= tracked
    assert ".claude/rules/hand-written.md" not in tracked


@pytest.mark.parametrize(
    ("name", "line"),
    [
        ("CLAUDE.md", "@AGENTS.md"),
        (".claude/CLAUDE.md", "@../AGENTS.md"),
        ("CLAUDE.local.md", "@AGENTS.md"),
    ],
)
def test_a_note_names_a_file_that_replaces_the_root(tmp_path: Path, name: str, line: str) -> None:
    write_tree(tmp_path)
    assert not [note for note in generate_runtime(tmp_path).notes if "exists" in note]
    path = tmp_path / name
    path.parent.mkdir(exist_ok=True)
    path.write_text("x", encoding="utf-8")
    notes = [note for note in generate_runtime(tmp_path).notes if "exists" in note]
    assert len(notes) == 1
    assert notes[0].startswith(f"{name} exists")
    assert f"Add the line {line} to {name}." in notes[0]


def test_the_command_prints_each_change_and_a_summary(tmp_path: Path) -> None:
    write_tree(tmp_path)
    result = RUNNER.invoke(app, ["runtime", str(tmp_path)])
    assert result.exit_code == 0
    assert "wrote AGENTS.md\n" in result.output
    assert "in_force: 8 files, 8 written, 0 removed, 0 problems\n" in result.output
    result = RUNNER.invoke(app, ["runtime", str(tmp_path)])
    assert result.output.endswith("in_force: 8 files, 0 written, 0 removed, 0 problems\n")
    assert "wrote" not in result.output


def test_the_command_prints_a_removal_and_a_note(tmp_path: Path) -> None:
    write_tree(tmp_path)
    (tmp_path / "CLAUDE.md").write_text("x", encoding="utf-8")
    stale = tmp_path / "knowledge/old/AGENTS.md"
    stale.parent.mkdir()
    stale.write_text(f"{MARKER}\n", encoding="utf-8")
    result = RUNNER.invoke(app, ["runtime", str(tmp_path)])
    assert "removed knowledge/old/AGENTS.md\n" in result.output
    assert "note: CLAUDE.md exists" in result.output


def test_the_command_fails_on_a_problem(tmp_path: Path) -> None:
    write_tree(tmp_path)
    (tmp_path / "AGENTS.md").write_text("# Mine\n", encoding="utf-8")
    result = RUNNER.invoke(app, ["runtime", str(tmp_path)])
    assert result.exit_code == 1
    assert ": not-generated: " in result.output


def test_the_command_verify_option_fails_on_a_change(tmp_path: Path) -> None:
    write_tree(tmp_path)
    result = RUNNER.invoke(app, ["runtime", str(tmp_path), "--verify"])
    assert result.exit_code == 1
    assert ": changed: " in result.output


def test_the_command_proposals_option_writes_the_review_result(tmp_path: Path) -> None:
    write_tree(tmp_path)
    result = RUNNER.invoke(app, ["runtime", str(tmp_path), "--proposals"])
    assert result.exit_code == 0
    assert "proposals: 8 files, 8 written" in result.output
    assert (tmp_path / REVIEW_FOLDER / "AGENTS.proposals.md").exists()
    assert not (tmp_path / "AGENTS.md").exists()


def test_the_command_rejects_proposals_with_verify(tmp_path: Path) -> None:
    write_tree(tmp_path)
    result = RUNNER.invoke(app, ["runtime", str(tmp_path), "--proposals", "--verify"])
    assert result.exit_code == USAGE_ERROR
    assert not (tmp_path / REVIEW_FOLDER).exists()


def test_the_graph_logic_names_no_file_of_a_runtime() -> None:
    text = (ENGINE / "view.py").read_text(encoding="utf-8")
    for word in (".claude", "AGENTS.md", "SKILL.md", "CLAUDE.md"):
        assert word not in text


def test_the_target_module_alone_names_the_tool_paths() -> None:
    for path in ENGINE.glob("*.py"):
        if path.name != "claude_code.py":
            assert ".claude/" not in path.read_text(encoding="utf-8"), path


def real_output(*, proposals: bool = False) -> list[RenderedFile]:
    report = compile_tree(REPO, proposals=proposals)
    assert report.compiled is not None, report.problems
    return render_files(build_view(report.compiled))


def test_the_committed_files_match_a_fresh_generation() -> None:
    for entry in real_output():
        assert (REPO / entry.path).read_text(encoding="utf-8") == entry.text, entry.path


def test_each_generated_file_is_a_tracked_file() -> None:
    tracked = set(git(REPO, "ls-files").splitlines())
    assert {entry.path.as_posix() for entry in real_output()} <= tracked


def test_no_tracked_file_with_the_marker_lacks_a_node() -> None:
    expected = {entry.path.as_posix() for entry in real_output()}
    for relative in git(REPO, "ls-files").splitlines():
        path = REPO / relative
        if path.suffix == ".md" and is_generated(path.read_bytes()):
            assert relative in expected


def test_each_link_in_a_committed_file_resolves() -> None:
    count = 0
    for entry in real_output():
        path = REPO / entry.path
        links = local_links(path.read_text(encoding="utf-8"))
        assert links, entry.path
        for link in links:
            count += 1
            assert resolves(link, path.parent, REPO), f"{entry.path}: {link}"
    assert count >= len(real_output())


def test_each_link_in_a_review_file_resolves(tmp_path: Path) -> None:
    for folder in (*TREE_FOLDERS,):
        shutil.copytree(REPO / folder, tmp_path / folder)
    report = generate_runtime(tmp_path, proposals=True)
    assert not report.problems
    review = tmp_path / REVIEW_FOLDER
    files = list(review.rglob("*.md"))
    assert len(files) == len(report.files)
    for path in files:
        for link in local_links(path.read_text(encoding="utf-8")):
            assert resolves(link, path.parent, tmp_path), f"{path}: {link}"


def hook_config() -> dict[str, Any]:
    with (REPO / ".pre-commit-config.yaml").open(encoding="utf-8") as stream:
        return cast("dict[str, Any]", YAML(typ="safe").load(stream))


def test_the_other_hooks_exclude_each_generated_file_and_no_other_file() -> None:
    exclude = re.compile(hook_config()["exclude"])
    for entry in real_output():
        assert exclude.search(entry.path.as_posix()), entry.path
    for path in ("README.md", "docs/README.md", ".claude/rules/hand-written.md", "NOT_AGENTS.md"):
        assert not exclude.search(path), path


def test_the_hook_runs_on_each_commit_and_verifies() -> None:
    local = next(repo for repo in hook_config()["repos"] if repo["repo"] == "local")
    hook = next(entry for entry in local["hooks"] if entry["id"] == "runtime-files")
    assert hook["entry"] == "uv run --frozen ka runtime --verify"
    assert hook["always_run"] is True
    assert hook["pass_filenames"] is False


def test_the_real_root_names_the_domains_the_governance_and_each_skill() -> None:
    text = (REPO / "AGENTS.md").read_text(encoding="utf-8")
    assert (
        "Read [Digital product development](knowledge/digital-product-development/node.md)." in text
    )
    assert "[Governance](governance/policies/node.md) loads by itself." in text
    for policy in ("lifecycle", "approval", "change-rules", "language-rules", "schema-rules"):
        assert f"(governance/policies/{policy}/node.md)" in text
    for skill in ("design-settings-interface", "review-screen-hierarchy"):
        assert f"- `{skill}`: " in text


def test_the_real_root_holds_no_setup_and_no_command() -> None:
    text = (REPO / "AGENTS.md").read_text(encoding="utf-8")
    for word in ("uv run", "uv sync", "pre-commit", "pyproject", "ka build", "pytest"):
        assert word not in text


def test_the_real_root_states_that_no_directive_is_in_force() -> None:
    report = compile_tree(REPO)
    assert report.compiled is not None
    if report.compiled.directives:
        pytest.skip("A person accepted a directive.")
    text = (REPO / "AGENTS.md").read_text(encoding="utf-8")
    left_out = report.compiled.left_out
    assert left_out["directives"] > 0
    assert f"No directive is in force. The graph holds {left_out['directives']} directives" in text


def test_each_committed_file_holds_only_directives_in_force() -> None:
    report = compile_tree(REPO)
    assert report.compiled is not None
    in_force = set(report.compiled.directives)
    for entry in real_output():
        text = (REPO / entry.path).read_text(encoding="utf-8")
        assert set(re.findall(r" \^([a-z0-9-]+)(?: \(\w+\))?$", text, re.MULTILINE)) <= in_force
        assert "(proposed)" not in text
        assert "NOT IN FORCE" not in text


def test_the_review_result_of_the_real_seed_holds_each_applied_directive() -> None:
    report = compile_tree(REPO, proposals=True)
    assert report.compiled is not None
    compiled = report.compiled
    files = {entry.path.as_posix(): entry for entry in render_files(build_view(compiled))}
    skill = files[f"{REVIEW}/claude/skills/design-settings-interface/SKILL.proposals.md"]
    expected = {entry.directive.id for entry in compiled.applied["design-settings-interface"]}
    assert expected
    found = set(re.findall(r" \^([a-z0-9-]+) \(proposed\)$", skill.text, re.MULTILINE))
    assert found == expected
    assert "one-primary-action" not in found
    assert "- `one-primary-action` does not apply at this node." in skill.text
    assert skill.limit is not None
    assert len(skill.whole_part) <= skill.limit
    assert all(entry.text.count("NOT IN FORCE") == 1 for entry in files.values())


def test_the_real_review_result_lists_directives_at_a_leaf_with_its_inherited_ones() -> None:
    report = compile_tree(REPO, proposals=True)
    assert report.compiled is not None
    files = {entry.path.as_posix(): entry for entry in render_files(build_view(report.compiled))}
    leaf = "knowledge/digital-product-development/ui-ux-design/visual-design/visual-grouping"
    text = files[f"{REVIEW}/{leaf}/AGENTS.proposals.md"].text
    expected = {entry.directive.id for entry in report.compiled.applied["visual-grouping"]}
    found = set(re.findall(r" \^([a-z0-9-]+) \(proposed\)$", text, re.MULTILINE))
    assert found == expected
    assert "name-user-and-task" in found
