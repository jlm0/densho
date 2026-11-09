# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportMissingTypeStubs=false
import posixpath
import re
import shutil
import subprocess
from dataclasses import replace
from io import StringIO
from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING, Any, cast

import pytest
from ruamel.yaml import YAML
from typer.testing import CliRunner

from engine.cli import app
from engine.compiler import compile_items, compile_tree
from engine.generated.metamodel import Skill
from engine.governance import pending_entities
from engine.parser import ParsedNode, parse_source
from engine.parser.result import StepFile
from engine.parser.steps import read_step_source
from engine.runtime import (
    MARKER,
    REVIEW_FOLDER,
    LoadMechanism,
    RuntimeView,
    build_view,
    claude_code,
    generate_runtime,
    is_generated,
    link_target,
    local_links,
    render_files,
    review_path,
)
from engine.runtime.claude_code import (
    ON_DEMAND_CHARACTERS,
    SKILL_KEPT_CHARACTERS,
    SKILL_KEPT_TOKENS,
    RenderedFile,
    size_problems,
    state_sentence,
)
from engine.runtime.files import apply_files
from engine.runtime.view import DirectiveCounts, NodeView, StepView
from engine.tree_copies import Tree

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping, Sequence

    from engine.directives import AppliedDirective

REPO = Path(__file__).resolve().parents[1]
ENGINE = REPO / "engine/runtime"
RUNNER = CliRunner()
GIT = shutil.which("git") or "git"
REVIEW = REVIEW_FOLDER.as_posix()
SKILL_BODY = "## Procedure\n\n1. Read each directive that this skill lists.\n"
TOOL_KEPT_TOKENS = 5_000
LOW_CHARACTERS_PER_TOKEN = 3
TOOL_ON_DEMAND_CHARACTERS = 40_000
ROOT_LINES = 200
SKILL_LINES = 500
USAGE_ERROR = 2
FENCED_BLOCK = re.compile(r"^```[^\n]*\n.*?^```$", re.MULTILINE | re.DOTALL)
DIRECTIVE_ID = re.compile(r" \^([a-z0-9-]+)(?: \(\w+\))?$", re.MULTILINE)
COMPACTION_SENTENCE = re.compile(r"\bIf compaction (?:cuts|removes)\b")
ROOT_COMPACTION_LINE = (
    "If compaction cuts or removes a skill, invoke the skill again. "
    "If only a person can start that skill, ask the person to invoke it again."
)
RULE_LINE = (
    "- Run the {0} check. ^{0}\n  - scope: {1}\n  - basis: judgment\n  - status: {2}\n"
    "  - origin: template\n"
)


def outside_code_blocks(text: str) -> str:
    return FENCED_BLOCK.sub("", text)


def listed_directives(text: str) -> set[str]:
    return set(DIRECTIVE_ID.findall(outside_code_blocks(text)))


def rule(directive_id: str, status: str = "accepted", scope: str = "subtree") -> str:
    return RULE_LINE.format(directive_id, scope, status)


def node(
    node_id: str,
    kind: str = "densho:Domain",
    *,
    front: str = "",
    rules: Iterable[str] = (),
    body: str = "",
) -> str:
    extra = "knowledge_type: domain\n" if kind != "densho:Root" else ""
    text = f"---\nid: {node_id}\nkind: {kind}\ntitle: {node_id}\nstatus: proposed\n"
    text += f"origin: template\n{extra}{front}---\n"
    if kind not in {"densho:Root", "densho:Skill"}:
        text += f"\n## Definition\n\nThe meaning of {node_id}.\n"
    joined = "".join(rules)
    if joined:
        text += f"\n## Directives\n\n{joined}"
    return f"{text}\n{body}" if body else text


def pointer(kind: str, target_id: str, *patterns: str) -> str:
    text = f"  - kind: densho:{kind}\n    target: {target_id}\n    trigger: You need {target_id}.\n"
    if patterns:
        text += "    paths:\n" + "".join(f'      - "{pattern}"\n' for pattern in patterns)
    return text


def pointers(*entries: str) -> str:
    return "pointers:\n" + "".join(entries)


SKILL_FRONT = (
    "description: Review a sample. Use when a sample needs a review.\n"
    "invocation: agent\nskill_type: system\nuses: [gamma]\n"
)
SAMPLE = {
    "knowledge/node.md": node(
        "root",
        "densho:Root",
        front=pointers(
            pointer("TextPointer", "alpha"),
            pointer("PathPointer", "gamma", "src/**/*"),
            pointer("AlwaysPointer", "delta"),
            pointer("TextPointer", "policies"),
        ),
        body="## Architecture\n\nA fact that no file shows.\n",
    ),
    "knowledge/nodes/alpha/node.md": node(
        "alpha",
        front=pointers(pointer("TextPointer", "beta"), pointer("SkillPointer", "review")),
        rules=[rule("keep"), rule("wait", "proposed"), rule("faded", "deprecated", "node")],
    ),
    "knowledge/nodes/alpha/beta/node.md": node(
        "beta",
        "densho:Concept",
        front=(
            "broader: [alpha]\nexceptions:\n"
            "  - directive: wait\n    reason: A reason for wait.\n    status: proposed\n"
            "  - directive: keep\n    reason: A reason for keep.\n    status: accepted\n"
        ),
        rules=[rule("bound", scope="node")],
    ),
    "knowledge/nodes/gamma/node.md": node(
        "gamma",
        front=pointers(pointer("PathPointer", "delta", "lib/**/*")),
        rules=[rule("solid", scope="node")],
    ),
    "knowledge/nodes/delta/node.md": node("delta", body="## Notes\n\nThe body of delta.\n"),
    "knowledge/governance/policies/node.md": node(
        "policies",
        front="governs: [policies, lifecycle]\n" + pointers(pointer("TextPointer", "lifecycle")),
    ),
    "knowledge/governance/policies/lifecycle/node.md": node(
        "lifecycle", "densho:Concept", front="broader: [policies]\ngoverns: [lifecycle]\n"
    ),
    "knowledge/skills/review/node.md": node(
        "review",
        "densho:Skill",
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
        REPO / "knowledge/governance/language",
        repository / "knowledge/governance/language",
        ignore=no_branch_files,
    )
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
    alpha = next(entry for entry in view.pages if entry.link.id == "alpha")
    assert {line.target.id: line.mechanism for line in alpha.pointers} == {
        "beta": LoadMechanism.TEXT,
        "review": LoadMechanism.SKILL,
    }


def test_each_node_has_one_generated_file() -> None:
    assert sorted(rendered()) == [
        ".claude/references/alpha.md",
        ".claude/references/beta.md",
        ".claude/references/lifecycle.md",
        ".claude/references/policies.md",
        ".claude/rules/knowledge/delta.md",
        ".claude/rules/knowledge/gamma.md",
        ".claude/skills/review/SKILL.md",
        "AGENTS.md",
    ]


def test_no_generated_file_sits_in_the_source_folder() -> None:
    for proposals in (False, True):
        for path in rendered(proposals=proposals):
            assert "knowledge" not in PurePosixPath(path).parts[:1], path


def test_a_path_rule_holds_each_pattern_and_the_file_of_its_node() -> None:
    assert front_matter(text_of(".claude/rules/knowledge/gamma.md")) == {
        "paths": ["knowledge/nodes/gamma/node.md", "src/**/*"],
    }


def test_a_path_rule_merges_the_patterns_of_two_pointers() -> None:
    sources = {
        **SAMPLE,
        "knowledge/nodes/alpha/node.md": node(
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
    assert front_matter(text)["paths"] == ["knowledge/nodes/gamma/node.md", "lib/**/*", "src/**/*"]


def test_an_always_pointer_gives_a_rule_with_no_paths_and_wins_over_a_path_pointer() -> None:
    text = text_of(".claude/rules/knowledge/delta.md")
    assert text.startswith(MARKER)
    assert "paths" not in text


def test_a_rule_holds_the_definition_and_the_body() -> None:
    text = text_of(".claude/rules/knowledge/delta.md")
    assert "## Definition\n\nThe meaning of delta.\n" in text
    assert "## Notes\n\nThe body of delta.\n" in text


def test_a_reference_page_holds_the_definition_and_the_body() -> None:
    sources = {
        **SAMPLE,
        "knowledge/nodes/alpha/beta/node.md": node(
            "beta",
            "densho:Concept",
            front="broader: [alpha]\n",
            body="## Notes\n\nThe body of beta.\n",
        ),
    }
    text = rendered(sources)[".claude/references/beta.md"].text
    assert "## Definition\n\nThe meaning of beta.\n" in text
    assert "## Notes\n\nThe body of beta.\n" in text
    assert "status:" not in text
    assert "origin:" not in text


def test_a_pointer_to_the_root_gives_no_rule() -> None:
    sources = {
        **SAMPLE,
        "knowledge/nodes/delta/node.md": node(
            "delta", front=pointers(pointer("PathPointer", "root", "docs/**/*"))
        ),
    }
    assert ".claude/rules/knowledge/root.md" not in rendered(sources)


def test_a_skill_behind_a_path_pointer_receives_a_rule_and_a_skill_file() -> None:
    sources = {
        **SAMPLE,
        "knowledge/nodes/delta/node.md": node(
            "delta", front=pointers(pointer("PathPointer", "review", "docs/**/*"))
        ),
    }
    files = rendered(sources)
    assert ".claude/skills/review/SKILL.md" in files
    assert ".claude/rules/knowledge/review.md" in files


def test_a_policy_is_not_a_domain_in_the_root() -> None:
    text = text_of("AGENTS.md")
    domains = text[text.index("## Domains") : text.index("## Governance")]
    governance = text[text.index("## Governance") :]
    assert "alpha" in domains
    assert "policies" not in domains
    assert "Read [policies](.claude/references/policies.md)." in governance
    assert "Read [lifecycle](.claude/references/lifecycle.md)." in governance


def test_the_root_lists_a_domain_that_it_has_no_pointer_to() -> None:
    sources = {
        **SAMPLE,
        "knowledge/node.md": node(
            "root", "densho:Root", front=pointers(pointer("TextPointer", "policies"))
        ),
    }
    text = rendered(sources)["AGENTS.md"].text
    assert "- Read [alpha](.claude/references/alpha.md).\n" in text


def test_the_root_names_each_skill_with_its_description() -> None:
    assert "- `review`: Review a sample. Use when a sample needs a review.\n" in text_of(
        "AGENTS.md"
    )


def test_the_root_leaves_out_an_empty_section() -> None:
    sources = {
        "knowledge/node.md": node(
            "root", "densho:Root", front=pointers(pointer("TextPointer", "lone"))
        ),
        "knowledge/nodes/lone/node.md": node("lone"),
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
            "densho:Root",
            front=pointers(pointer("TextPointer", "alpha"), pointer("TextPointer", "beta")),
        ),
    }
    text = rendered(sources)["AGENTS.md"].text
    assert "## References\n\n- You need beta. Read [beta](.claude/references/beta.md).\n" in text


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
        "densho:Root",
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
    alpha = text_of(f"{REVIEW}/claude/references/alpha.proposals.md", proposals=True)
    assert "- Run the wait check. ^wait (proposed)\n" in alpha
    assert "- Run the keep check. ^keep\n" in alpha
    assert "^faded" not in alpha


def test_each_review_file_opens_with_the_notice() -> None:
    for entry in rendered(proposals=True).values():
        title_end = entry.text.index("\n# ") + 1
        following = entry.text[title_end:].split("\n")
        assert following[2].startswith("NOT IN FORCE.")


def test_an_exception_stops_a_directive_and_states_the_reason() -> None:
    text = text_of(".claude/references/beta.md")
    assert "^keep" not in text.split("## Exceptions")[0]
    assert "- `keep` does not apply at this node. A reason for keep.\n" in text
    assert "A reason for wait" not in text
    review = text_of(f"{REVIEW}/claude/references/beta.proposals.md", proposals=True)
    assert "- `wait` does not apply at this node. A reason for wait. (proposed)\n" in review
    assert "^wait" not in review.split("## Exceptions")[0]


def test_a_node_with_no_directive_states_that_fact() -> None:
    assert "No directive is in force at this node.\n" in text_of(".claude/rules/knowledge/delta.md")
    review = text_of(f"{REVIEW}/claude/rules/knowledge/delta.proposals.md", proposals=True)
    assert "No directive applies at this node.\n" in review


def test_a_group_links_to_the_node_that_holds_the_directive() -> None:
    text = text_of(".claude/skills/review/SKILL.md")
    assert (
        "From [gamma](../../rules/knowledge/gamma.md):\n\n- Run the solid check. ^solid\n" in text
    )
    assert "From [review](SKILL.md):\n\n- Run the own-rule check." in text
    beta = text_of(".claude/references/beta.md")
    assert "From [alpha](alpha.md):\n\n- Run the bound check." not in beta
    assert "From [beta](beta.md):\n\n- Run the bound check. ^bound\n" in beta


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
        (
            ".claude/references/alpha.md",
            ["## Directives", "^keep", "## Definition", "## References", "Read [beta]"],
        ),
        (
            "AGENTS.md",
            [
                "## Rules for each task",
                "## Use a skill",
                "## Create a rule",
                "## Skills",
                "## Domains",
                "## Governance",
            ],
        ),
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
                "densho:Root",
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
    assert (
        "- You need beta. [beta](.claude/rules/knowledge/beta.md) loads by itself.\n" in references
    )
    lifecycle = "[lifecycle](.claude/rules/knowledge/lifecycle.md) is always loaded.\n"
    assert f"- You need lifecycle. {lifecycle}" in references
    assert "| You need review. | `review` |\n" in references
    assert "Use the skill `review`" not in references
    assert "- You need gamma. Read [gamma](.claude/references/gamma.md).\n" in references


def test_a_reference_page_links_the_generated_file_of_each_pointer() -> None:
    text = text_of(".claude/references/alpha.md")
    assert "- You need beta. Read [beta](beta.md).\n" in text
    assert "- You need review. Use the skill `review`.\n" in text
    rule = text_of(".claude/rules/knowledge/gamma.md")
    assert "[delta](delta.md) loads by itself.\n" in rule


def test_each_link_goes_to_a_generated_file_and_no_link_goes_to_a_node_file() -> None:
    for proposals in (False, True):
        files = rendered(proposals=proposals)
        for path, entry in files.items():
            folder = PurePosixPath(path).parent
            for link in local_links(entry.text):
                target = posixpath.normpath((folder / link).as_posix())
                assert target in files, (path, link)
                assert not target.endswith("node.md"), (path, link)


def test_a_review_link_resolves_from_the_review_folder() -> None:
    root = text_of(f"{REVIEW}/AGENTS.proposals.md", proposals=True)
    assert "Read [alpha](claude/references/alpha.proposals.md).\n" in root
    alpha = text_of(f"{REVIEW}/claude/references/alpha.proposals.md", proposals=True)
    assert "# alpha\n" in alpha
    assert "Read [beta](beta.proposals.md).\n" in alpha


COMES_FROM = "## Comes from\n\nThe output of each node in this list is an input of this node.\n\n"
GOES_TO = "## Goes to\n\nThe output of this node is an input of each node in this list.\n\n"
FLOW = {
    "knowledge/node.md": node(
        "root", "densho:Root", front=pointers(pointer("TextPointer", "product"))
    ),
    "knowledge/nodes/product/node.md": node(
        "product",
        front=pointers(pointer("TextPointer", "strategy"), pointer("TextPointer", "design")),
    ),
    "knowledge/nodes/product/strategy/node.md": node(
        "strategy",
        "densho:Discipline",
        front="broader: [product]\n"
        + pointers(pointer("TextPointer", "research"), pointer("TextPointer", "positioning")),
    ),
    "knowledge/nodes/product/strategy/research/node.md": node(
        "research", "densho:PracticeArea", front="broader: [strategy]\ninforms: [positioning]\n"
    ),
    "knowledge/nodes/product/strategy/positioning/node.md": node(
        "positioning",
        "densho:PracticeArea",
        front="broader: [strategy]\ninforms: [identity]\n"
        + pointers(pointer("TextPointer", "statement")),
        body="## Notes\n\nThe body of positioning.\n",
    ),
    "knowledge/nodes/product/strategy/positioning/statement/node.md": node(
        "statement", "densho:Concept", front="broader: [positioning]\n"
    ),
    "knowledge/nodes/product/design/node.md": node(
        "design",
        "densho:Discipline",
        front="broader: [product]\n" + pointers(pointer("TextPointer", "identity")),
    ),
    "knowledge/nodes/product/design/identity/node.md": node(
        "identity", "densho:PracticeArea", front="broader: [design]\n"
    ),
}


def flow_page(node_id: str, sources: dict[str, str] | None = None) -> str:
    return rendered(FLOW if sources is None else sources)[f".claude/references/{node_id}.md"].text


def test_a_page_lists_the_node_before_it_and_the_node_after_it() -> None:
    expected = f"{COMES_FROM}- [research](research.md)\n\n{GOES_TO}- [identity](identity.md)\n"
    assert expected in flow_page("positioning")


def test_an_informs_edge_across_two_disciplines_shows_on_both_pages() -> None:
    assert f"{GOES_TO}- [identity](identity.md)\n" in flow_page("positioning")
    identity = flow_page("identity")
    assert identity.endswith(
        f"The meaning of identity.\n\n{COMES_FROM}- [positioning](positioning.md)\n"
    )
    assert "## Goes to" not in identity


def test_a_node_that_only_informs_lists_only_the_node_after_it() -> None:
    research = flow_page("research")
    assert research.endswith(
        f"The meaning of research.\n\n{GOES_TO}- [positioning](positioning.md)\n"
    )
    assert "## Comes from" not in research


def test_a_node_with_no_informs_edge_prints_neither_section() -> None:
    files = {**rendered(FLOW), **rendered()}
    for path in (
        ".claude/references/product.md",
        ".claude/references/strategy.md",
        ".claude/references/statement.md",
        ".claude/references/alpha.md",
        ".claude/rules/knowledge/gamma.md",
        ".claude/skills/review/SKILL.md",
        "AGENTS.md",
    ):
        assert "## Comes from" not in files[path].text, path
        assert "## Goes to" not in files[path].text, path


def test_the_flow_sits_after_the_body_and_before_the_references() -> None:
    text = flow_page("positioning")
    order = ["## Directives", "## Definition", "## Notes", "## Comes from", "## Goes to"]
    places = [text.index(part) for part in [*order, "## References"]]
    assert places == sorted(places)


def test_the_flow_lists_each_node_in_id_order() -> None:
    sources = {
        **FLOW,
        "knowledge/nodes/product/strategy/research/node.md": node(
            "research",
            "densho:PracticeArea",
            front="broader: [strategy]\ninforms: [positioning, identity]\n",
        ),
    }
    backward = dict(reversed(sources.items()))
    for tree in (sources, backward):
        research = flow_page("research", tree)
        assert f"{GOES_TO}- [identity](identity.md)\n- [positioning](positioning.md)\n" in research
        identity = flow_page("identity", tree)
        assert (
            f"{COMES_FROM}- [positioning](positioning.md)\n- [research](research.md)\n" in identity
        )


def test_a_flow_link_goes_to_the_rule_of_a_node_with_a_rule() -> None:
    sources = {
        **FLOW,
        "knowledge/nodes/product/design/node.md": node(
            "design",
            "densho:Discipline",
            front="broader: [product]\n" + pointers(pointer("PathPointer", "identity", "src/**/*")),
        ),
    }
    files = rendered(sources)
    positioning = files[".claude/references/positioning.md"].text
    assert f"{GOES_TO}- [identity](../rules/knowledge/identity.md)\n" in positioning
    rule = files[".claude/rules/knowledge/identity.md"].text
    assert rule.endswith(f"{COMES_FROM}- [positioning](../../references/positioning.md)\n")


def test_the_review_copy_holds_the_flow_with_links_into_the_copy() -> None:
    files = rendered(FLOW, proposals=True)
    positioning = files[f"{REVIEW}/claude/references/positioning.proposals.md"].text
    expected = (
        f"{COMES_FROM}- [research](research.proposals.md)\n\n"
        f"{GOES_TO}- [identity](identity.proposals.md)\n"
    )
    assert expected in positioning


def test_a_rejected_node_is_not_in_the_flow() -> None:
    rejected = node(
        "research", "densho:PracticeArea", front="broader: [strategy]\ninforms: [positioning]\n"
    ).replace("status: proposed\n", "status: rejected\nrejection_reason: A person said no.\n")
    sources = {
        **FLOW,
        "knowledge/nodes/product/strategy/node.md": node(
            "strategy",
            "densho:Discipline",
            front="broader: [product]\n" + pointers(pointer("TextPointer", "positioning")),
        ),
        "knowledge/nodes/product/strategy/research/node.md": rejected,
    }
    positioning = flow_page("positioning", sources)
    assert "## Comes from" not in positioning
    assert f"{GOES_TO}- [identity](identity.md)\n" in positioning


def test_a_title_in_the_flow_makes_no_link() -> None:
    hostile = FLOW["knowledge/nodes/product/strategy/positioning/node.md"].replace(
        "title: positioning", 'title: "Fake](../../x) [a"'
    )
    sources = {**FLOW, "knowledge/nodes/product/strategy/positioning/node.md": hostile}
    for page in ("research", "identity"):
        text = flow_page(page, sources)
        assert "- [Fake\\](../../x) \\[a](positioning.md)\n" in text, page
        assert local_links(text) == ["positioning.md"], page


def test_the_runtime_writes_the_flow_of_a_checked_tree(tmp_path: Path) -> None:
    write_tree(tmp_path, FLOW)
    for proposals in (False, True):
        report = generate_runtime(tmp_path, proposals=proposals)
        assert not report.problems, report.problems
    identity = (tmp_path / ".claude/references/identity.md").read_text(encoding="utf-8")
    assert identity.endswith(f"{COMES_FROM}- [positioning](positioning.md)\n")
    review = tmp_path / REVIEW_FOLDER / "claude/references/identity.proposals.md"
    assert f"{COMES_FROM}- [positioning](positioning.proposals.md)\n" in review.read_text(
        encoding="utf-8"
    )


def test_a_skill_links_each_node_that_it_uses() -> None:
    front = (
        "description: Review a sample. Use when a sample needs a review.\n"
        "invocation: agent\nskill_type: system\nuses: [gamma, beta]\n"
    )
    sources = {
        **SAMPLE,
        "knowledge/skills/review/node.md": node(
            "review",
            "densho:Skill",
            front=front + pointers(pointer("TextPointer", "gamma")),
            body=SKILL_BODY,
        ),
    }
    text = rendered(sources)[".claude/skills/review/SKILL.md"].text
    references = text[text.index("## References") :]
    assert references.splitlines()[2:] == [
        "- You need gamma. Read [gamma](../../rules/knowledge/gamma.md).",
        "- Read [beta](../../references/beta.md).",
    ]


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


def test_a_title_makes_no_link() -> None:
    hostile = node("delta").replace("title: delta", 'title: "Fake](../../x) [a"')
    sources = {**SAMPLE, "knowledge/nodes/delta/node.md": hostile}
    text = rendered(sources)[".claude/rules/knowledge/delta.md"].text
    assert "# Fake\\](../../x) \\[a\n" in text
    assert local_links(text) == []


def test_a_backslash_in_a_title_stays_literal() -> None:
    hostile = node("delta").replace("title: delta", 'title: "a\\\\](b)"')
    sources = {**SAMPLE, "knowledge/nodes/delta/node.md": hostile}
    text = rendered(sources)[".claude/rules/knowledge/delta.md"].text
    assert local_links(text) == []


def test_a_template_expression_in_a_node_stays_literal() -> None:
    sources = {
        **SAMPLE,
        "knowledge/nodes/delta/node.md": node(
            "delta", body="## Notes\n\nKeep {{ 7 * 7 }} as text.\n"
        ),
    }
    assert "Keep {{ 7 * 7 }} as text." in rendered(sources)[".claude/rules/knowledge/delta.md"].text


def test_a_description_that_breaks_plain_yaml_stays_one_string() -> None:
    description = "'Review: \"a\" sample, #1. Use when\n  a sample: needs a review.'"
    front = f"description: {description}\ninvocation: agent\nskill_type: system\nuses: [gamma]\n"
    sources = {
        **SAMPLE,
        "knowledge/skills/review/node.md": node("review", "densho:Skill", front=front),
    }
    text = rendered(sources)[".claude/skills/review/SKILL.md"].text
    assert (
        front_matter(text)["description"]
        == 'Review: "a" sample, #1. Use when a sample: needs a review.'
    )


def test_a_description_keeps_each_character_that_is_not_ascii() -> None:
    front = (
        "description: Review a café sample. Use when a sample needs a review.\n"
        "invocation: agent\nskill_type: system\nuses: [gamma]\n"
    )
    sources = {
        **SAMPLE,
        "knowledge/skills/review/node.md": node("review", "densho:Skill", front=front),
    }
    assert (
        "café" in rendered(sources)[".claude/skills/review/SKILL.md"].text.partition("\n---\n")[0]
    )


def test_a_glob_that_breaks_plain_yaml_stays_one_string() -> None:
    sources = {
        **SAMPLE,
        "knowledge/nodes/delta/node.md": node(
            "delta", front=pointers(pointer("PathPointer", "gamma", "*.md", "a: {b}/**/*"))
        ),
    }
    text = rendered(sources)[".claude/rules/knowledge/gamma.md"].text
    assert {"*.md", "a: {b}/**/*"} <= set(front_matter(text)["paths"])


def test_a_path_with_a_space_gives_a_link_that_resolves(tmp_path: Path) -> None:
    sources = dict(SAMPLE)
    sources["knowledge/nodes/my folder/gamma/node.md"] = sources.pop(
        "knowledge/nodes/gamma/node.md"
    )
    write_tree(tmp_path, sources)
    report = generate_runtime(tmp_path)
    assert not report.problems
    root = (tmp_path / "AGENTS.md").read_text(encoding="utf-8")
    assert "[gamma](.claude/rules/knowledge/gamma.md) loads by itself." in root
    rule = (tmp_path / ".claude/rules/knowledge/gamma.md").read_text(encoding="utf-8")
    assert '  - "knowledge/nodes/my folder/gamma/node.md"\n' in rule


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


def test_a_link_target_resolves_from_its_folder(tmp_path: Path) -> None:
    resolved = tmp_path.resolve()
    assert link_target("a%20b/c.md", tmp_path) == resolved / "a b/c.md"
    assert link_target("a%20b/c.md#part", tmp_path) == resolved / "a b/c.md"
    assert link_target("../c.md", tmp_path / "a") == resolved / "c.md"
    assert link_target(str(tmp_path / "c.md"), tmp_path / "a") == resolved / "c.md"
    assert link_target("a%00b.md", tmp_path) is None


@pytest.mark.parametrize(
    ("link", "expected"),
    [
        ("gamma.md", []),
        ("../../references/alpha.md#definition", []),
        ("../../../AGENTS.md", []),
        ("../../../knowledge/nodes/gamma/node.md", ["link"]),
        ("../../../README.md", ["link"]),
        ("missing.md", ["link"]),
        ("../../../../outside.md", ["link"]),
    ],
)
def test_a_body_link_must_go_to_a_generated_file(
    tmp_path: Path, link: str, expected: list[str]
) -> None:
    sources = {
        **SAMPLE,
        "knowledge/nodes/delta/node.md": node("delta", body=f"## Notes\n\nSee [it]({link}).\n"),
    }
    write_tree(tmp_path, sources)
    (tmp_path / "README.md").write_text("# Read me\n", encoding="utf-8")
    (tmp_path.parent / "outside.md").write_text("x", encoding="utf-8")
    report = generate_runtime(tmp_path)
    assert codes(report.problems) == expected
    for problem in report.problems:
        assert "the generator writes no file at this path" in str(problem)


def test_a_broken_link_in_a_body_stops_the_run(tmp_path: Path) -> None:
    sources = {
        **SAMPLE,
        "knowledge/nodes/delta/node.md": node(
            "delta", body="## Notes\n\nSee [the other node](../gamma/node.md).\n"
        ),
    }
    write_tree(tmp_path, sources)
    report = generate_runtime(tmp_path)
    assert codes(report.problems) == ["link"]
    assert str(tmp_path / "knowledge/nodes/delta/node.md") in str(report.problems[0])
    assert ".claude/rules/knowledge/delta.md" in str(report.problems[0])
    assert not (tmp_path / "AGENTS.md").exists()


def file_of(whole: str, limit: int | None) -> RenderedFile:
    return RenderedFile(PurePosixPath("a.md"), "text", "knowledge/nodes/a/node.md", whole, limit)


def test_the_size_check_reads_the_limit_of_each_file(tmp_path: Path) -> None:
    over = file_of("x" * 11, 10)
    assert codes(size_problems([over], tmp_path)) == ["size"]
    assert str(tmp_path / "knowledge/nodes/a/node.md") in str(size_problems([over], tmp_path)[0])
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
    assert files[".claude/references/alpha.md"].limit == ON_DEMAND_CHARACTERS


def test_the_kept_part_of_a_skill_holds_the_directives_and_not_the_rest() -> None:
    entry = rendered()[".claude/skills/review/SKILL.md"]
    assert "^own-rule" in entry.whole_part
    assert "## Procedure" not in entry.whole_part
    assert "## References" not in entry.whole_part
    assert "## Procedure" in entry.text


def test_too_many_directives_at_a_skill_give_a_size_problem(tmp_path: Path) -> None:
    long_rules = [rule(f"rule-{number:03}", scope="node") for number in range(440)]
    sources = {
        **SAMPLE,
        "knowledge/skills/review/node.md": node(
            "review", "densho:Skill", front=SKILL_FRONT, rules=long_rules, body=SKILL_BODY
        ),
    }
    entries = rendered(sources)
    entry = entries[".claude/skills/review/SKILL.md"]
    assert len(entry.text.splitlines()) <= SKILL_LINES
    problems = size_problems(entries.values(), tmp_path)
    assert codes(problems) == ["size"]
    assert "characters in the part that must stay whole" in problems[0].message


def skill_with_body_lines(count: int) -> dict[str, str]:
    body = SKILL_BODY + "\n## Notes\n\n" + "".join(f"- Note {n}.\n" for n in range(count))
    return {
        **SAMPLE,
        "knowledge/skills/review/node.md": node(
            "review", "densho:Skill", front=SKILL_FRONT, body=body
        ),
    }


def test_a_skill_file_at_its_line_budget_passes(tmp_path: Path) -> None:
    entries = rendered(skill_with_body_lines(1))
    lines = len(entries[".claude/skills/review/SKILL.md"].text.splitlines())
    entries = rendered(skill_with_body_lines(SKILL_LINES - lines + 1))
    assert len(entries[".claude/skills/review/SKILL.md"].text.splitlines()) == SKILL_LINES
    assert not size_problems(entries.values(), tmp_path)


def test_a_skill_file_over_its_line_budget_fails(tmp_path: Path) -> None:
    entries = rendered(skill_with_body_lines(1))
    lines = len(entries[".claude/skills/review/SKILL.md"].text.splitlines())
    entries = rendered(skill_with_body_lines(SKILL_LINES - lines + 2))
    problems = size_problems(entries.values(), tmp_path)
    assert [(problem.code, problem.path.name) for problem in problems] == [("size", "node.md")]
    assert f"has {SKILL_LINES + 1} lines, over the budget of {SKILL_LINES}" in problems[0].message
    assert problems[0].path == tmp_path / "knowledge/skills/review/node.md"


def root_with_rule_lines(count: int) -> dict[str, str]:
    root = node(
        "root",
        "densho:Root",
        front=pointers(
            pointer("TextPointer", "alpha"),
            pointer("PathPointer", "gamma", "src/**/*"),
            pointer("AlwaysPointer", "delta"),
            pointer("TextPointer", "policies"),
        ),
        rules=[rule(f"note-{n}", scope="node") for n in range(count)],
    )
    return {**SAMPLE, "knowledge/node.md": root}


def test_the_root_at_its_line_budget_passes(tmp_path: Path) -> None:
    lines = len(rendered(root_with_rule_lines(1))["AGENTS.md"].text.splitlines())
    entries = rendered(root_with_rule_lines(ROOT_LINES - lines + 1))
    assert len(entries["AGENTS.md"].text.splitlines()) == ROOT_LINES
    assert not size_problems(entries.values(), tmp_path)


def test_the_root_over_its_line_budget_fails(tmp_path: Path) -> None:
    lines = len(rendered(root_with_rule_lines(1))["AGENTS.md"].text.splitlines())
    entries = rendered(root_with_rule_lines(ROOT_LINES - lines + 2))
    problems = size_problems(entries.values(), tmp_path)
    assert [problem.code for problem in problems] == ["size"]
    assert f"AGENTS.md has {ROOT_LINES + 1} lines, over the budget of {ROOT_LINES}" in (
        problems[0].message
    )
    assert problems[0].path == tmp_path / "knowledge/node.md"


def test_a_line_separator_in_a_skill_body_does_not_end_a_line(tmp_path: Path) -> None:
    body = f"{SKILL_BODY}\n## Notes\n\n- {'Note.\u2028' * SKILL_LINES}\n"
    entries = rendered(
        {
            **SAMPLE,
            "knowledge/skills/review/node.md": node(
                "review", "densho:Skill", front=SKILL_FRONT, body=body
            ),
        }
    )
    assert entries[".claude/skills/review/SKILL.md"].text.count("\u2028") == SKILL_LINES
    assert not size_problems(entries.values(), tmp_path)


def test_a_reference_page_has_no_line_budget(tmp_path: Path) -> None:
    alpha = SAMPLE["knowledge/nodes/alpha/node.md"].rstrip("\n")
    body = "\n\n## Notes\n\n" + "".join(f"- Note {n}.\n" for n in range(SKILL_LINES * 2))
    entries = rendered({**SAMPLE, "knowledge/nodes/alpha/node.md": alpha + body})
    assert len(entries[".claude/references/alpha.md"].text.splitlines()) > SKILL_LINES
    assert not size_problems(entries.values(), tmp_path)


def test_a_long_procedure_gives_no_size_problem(tmp_path: Path) -> None:
    body = SKILL_BODY + "\n## Notes\n\n" + "A long note. " * 2_000 + "\n"
    sources = {
        **SAMPLE,
        "knowledge/skills/review/node.md": node(
            "review", "densho:Skill", front=SKILL_FRONT, body=body
        ),
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
        "knowledge/nodes/alpha/beta/notes.txt": b"# Mine\n",
        "src/AGENTS.md": f"{MARKER}\n# Outside each scanned folder\n".encode(),
        ".claude/references/deep/mine.md": f"{MARKER}\n# Below the scanned folder\n".encode(),
    }
    for relative, data in hand_written.items():
        tmp_path.joinpath(relative).parent.mkdir(parents=True, exist_ok=True)
        tmp_path.joinpath(relative).write_bytes(data)
    (tmp_path / ".claude/skills/review/extra.md").write_bytes(b"# Mine\n")
    without_review = {
        relative: text
        for relative, text in SAMPLE.items()
        if not relative.startswith("knowledge/skills/")
    }
    without_review["knowledge/nodes/alpha/node.md"] = node(
        "alpha", front=pointers(pointer("TextPointer", "beta")), rules=[rule("keep")]
    )
    without_review["knowledge/nodes/alpha/beta/node.md"] = node(
        "beta", "densho:Concept", front="broader: [alpha]\n"
    )
    del without_review["knowledge/nodes/delta/node.md"]
    without_review["knowledge/node.md"] = node(
        "root",
        "densho:Root",
        front=pointers(
            pointer("TextPointer", "alpha"),
            pointer("TextPointer", "gamma"),
            pointer("TextPointer", "policies"),
        ),
    )
    without_review["knowledge/nodes/gamma/node.md"] = node("gamma")
    shutil.rmtree(tmp_path / "knowledge/skills/review")
    (tmp_path / "knowledge/nodes/delta/node.md").unlink()
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
    assert (tmp_path / ".claude/references/gamma.md").exists()


def test_a_removal_prunes_empty_folders_and_keeps_a_top_folder(tmp_path: Path) -> None:
    for relative in ("build/a/b/AGENTS.md", ".claude/skills/x/SKILL.md"):
        path = tmp_path / relative
        path.parent.mkdir(parents=True)
        path.write_text(f"{MARKER}\n", encoding="utf-8")
    keep = tmp_path / "build/keep/AGENTS.md"
    keep.parent.mkdir()
    keep.write_text(f"{MARKER}\n", encoding="utf-8")
    result = apply_files(
        tmp_path,
        {PurePosixPath("build/keep/AGENTS.md"): keep.read_bytes()},
        [tmp_path / "build/a/b/AGENTS.md", tmp_path / ".claude/skills/x/SKILL.md", keep],
    )
    assert not result.problems
    assert not (tmp_path / "build/a").exists()
    assert keep.exists()
    assert not (tmp_path / ".claude/skills").exists()
    assert (tmp_path / ".claude").is_dir()


def test_a_removal_keeps_a_folder_that_still_holds_a_file(tmp_path: Path) -> None:
    stale = tmp_path / "build/a/b/AGENTS.md"
    stale.parent.mkdir(parents=True)
    stale.write_text(f"{MARKER}\n", encoding="utf-8")
    (tmp_path / "build/a/note.md").write_text("x", encoding="utf-8")
    assert not apply_files(tmp_path, {}, [stale]).problems
    assert not (tmp_path / "build/a/b").exists()
    assert (tmp_path / "build/a/note.md").exists()


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
        ".claude/references/a.md",
        ".claude/rules/knowledge/d.md",
        ".claude/rules/knowledge/deep/e.md",
        ".claude/skills/f/SKILL.md",
    ]
    outside = [
        "src/AGENTS.md",
        "knowledge/nodes/a/AGENTS.md",
        "knowledge/skills/b/AGENTS.md",
        "knowledge/governance/policies/c/AGENTS.md",
        ".claude/references/deep/b.md",
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


@pytest.mark.parametrize("data", [b"# Mine\n", f"{MARKER}\n# Old folder file\n".encode()])
def test_any_other_file_in_a_node_folder_fails_the_parser(tmp_path: Path, data: bytes) -> None:
    write_tree(tmp_path)
    path = tmp_path / "knowledge/nodes/alpha/AGENTS.md"
    path.write_bytes(data)
    report = generate_runtime(tmp_path)
    assert codes(report.problems) == ["file-name"]
    assert path.read_bytes() == data
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
    (tmp_path / "knowledge/nodes/gamma/node.md").write_text("no front matter\n", encoding="utf-8")
    report = generate_runtime(tmp_path)
    assert report.problems
    assert report.written == ()
    assert report.removed == ()
    assert (tmp_path / "AGENTS.md").read_bytes() == before
    assert (tmp_path / ".claude/references/alpha.md").exists()


def test_a_rejected_tree_removes_the_review_result(tmp_path: Path) -> None:
    write_tree(tmp_path)
    assert not generate_runtime(tmp_path, proposals=True).problems
    review = tmp_path / REVIEW_FOLDER
    assert review.is_dir()
    (tmp_path / "knowledge/nodes/gamma/node.md").write_text("no front matter\n", encoding="utf-8")
    report = generate_runtime(tmp_path, proposals=True)
    assert report.problems
    assert PurePosixPath(f"{REVIEW}/AGENTS.proposals.md") in report.removed
    assert not list(review.rglob("*.md"))


def test_an_empty_tree_removes_each_generated_file_and_passes(tmp_path: Path) -> None:
    write_tree(tmp_path)
    assert not generate_runtime(tmp_path).problems
    (tmp_path / ".claude/rules").mkdir(parents=True, exist_ok=True)
    (tmp_path / ".claude/rules/hand-written.md").write_bytes(b"# Mine\n")
    for path in (tmp_path / "knowledge").rglob("node.md"):
        path.unlink()
    report = generate_runtime(tmp_path)
    assert not report.problems
    assert report.files == ()
    assert not (tmp_path / "AGENTS.md").exists()
    assert not (tmp_path / ".claude/references").exists()
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
    stale = tmp_path / REVIEW_FOLDER / "claude/references/old.proposals.md"
    stale.write_text(f"{MARKER}\n", encoding="utf-8")
    report = generate_runtime(tmp_path, proposals=True)
    assert report.removed == (PurePosixPath(f"{REVIEW}/claude/references/old.proposals.md"),)
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
    path = tmp_path / ".claude/references/alpha.md"
    path.unlink()
    assert codes(generate_runtime(tmp_path, verify=True).problems) == ["changed"]
    assert path.exists()


def test_verify_fails_on_a_stale_file_and_removes_it(tmp_path: Path) -> None:
    committed_repository(tmp_path)
    stale = tmp_path / ".claude/references/old.md"
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
    (tmp_path / ".claude/references/alpha.md").unlink()
    git(tmp_path, "rm", "-q", "--cached", ".claude/references/alpha.md")
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
    git(tmp_path, "rm", "-q", "--cached", ".claude/references/alpha.md")
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
    stale = tmp_path / ".claude/references/old.md"
    stale.parent.mkdir(parents=True)
    stale.write_text(f"{MARKER}\n", encoding="utf-8")
    result = RUNNER.invoke(app, ["runtime", str(tmp_path)])
    assert "removed .claude/references/old.md\n" in result.output
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


def flow_section(text: str, heading: str) -> str:
    return text.partition(f"\n{heading}\n")[2].partition("\n## ")[0]


def test_each_informs_edge_of_the_real_seed_shows_on_both_pages() -> None:
    report = compile_tree(REPO)
    assert report.compiled is not None
    view = build_view(report.compiled)
    texts = {entry.path: entry.text for entry in render_files(view)}
    paths = claude_code.generated_paths(view)
    edges = [
        (node.id, target)
        for node in report.compiled.graph.nodes
        for target in getattr(node, "informs", None) or []
    ]
    assert edges
    for source, target in edges:
        source_path, target_path = paths[source], paths[target]
        forward = posixpath.relpath(target_path, source_path.parent)
        back = posixpath.relpath(source_path, target_path.parent)
        assert f"]({forward})\n" in flow_section(texts[source_path], "## Goes to"), source
        assert f"]({back})\n" in flow_section(texts[target_path], "## Comes from"), target


def test_the_committed_files_match_a_fresh_generation() -> None:
    for entry in real_output():
        assert (REPO / entry.path).read_text(encoding="utf-8") == entry.text, entry.path


def test_each_generated_file_is_a_tracked_file() -> None:
    tracked = set(git(REPO, "ls-files").splitlines())
    assert {entry.path.as_posix() for entry in real_output()} <= tracked


def test_no_tracked_file_with_the_marker_lacks_a_node() -> None:
    expected = {entry.path.as_posix() for entry in real_output()}
    for relative in git(REPO, "ls-files", "--", ".", ":(exclude)fixtures/project").splitlines():
        path = REPO / relative
        if path.suffix == ".md" and is_generated(path.read_bytes()):
            assert relative in expected


def test_each_link_in_a_committed_file_resolves() -> None:
    generated = {(REPO / entry.path).resolve() for entry in real_output()}
    count = 0
    for entry in real_output():
        path = REPO / entry.path
        links = local_links(path.read_text(encoding="utf-8"))
        for link in links:
            count += 1
            assert link_target(link, path.parent) in generated, f"{entry.path}: {link}"
    assert count >= len(real_output())


def test_each_link_in_a_review_file_resolves(tmp_path: Path) -> None:
    shutil.copytree(REPO / "knowledge", tmp_path / "knowledge")
    report = generate_runtime(tmp_path, proposals=True)
    assert not report.problems
    review = tmp_path / REVIEW_FOLDER
    files = list(review.rglob("*.md"))
    assert len(files) == len(report.files)
    generated = {path.resolve() for path in files}
    for path in files:
        for link in local_links(path.read_text(encoding="utf-8")):
            assert link_target(link, path.parent) in generated, f"{path}: {link}"


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
    assert hook["entry"] == "uv run --frozen densho runtime --verify"
    assert hook["always_run"] is True
    assert hook["pass_filenames"] is False
    assert hook["verbose"] is True


def test_the_real_root_names_the_domains_the_governance_and_each_skill() -> None:
    text = (REPO / "AGENTS.md").read_text(encoding="utf-8")
    assert (
        "Read [Digital product development](.claude/references/digital-product-development.md)."
        in text
    )
    assert "[Governance](.claude/rules/knowledge/governance.md) loads by itself." in text
    for policy in ("lifecycle", "approval", "change-rules", "language-rules", "schema-rules"):
        assert f"(.claude/references/{policy}.md)" in text
    for skill in ("design-interface", "review-screen-hierarchy"):
        assert f" | `{skill}` |\n" in text
    assert "- `propose-knowledge`: " in text
    for skill in ("design-interface", "review-screen-hierarchy", "propose-knowledge"):
        assert f"]({skill}" not in text
        assert f"skills/{skill}" not in text
    assert "node.md)" not in text


def test_the_real_root_holds_no_setup_and_no_command() -> None:
    text = (REPO / "AGENTS.md").read_text(encoding="utf-8")
    for word in ("uv run", "uv sync", "pre-commit", "pyproject", "densho build", "pytest"):
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
        text = outside_code_blocks((REPO / entry.path).read_text(encoding="utf-8"))
        assert listed_directives(text) <= in_force
        assert "(proposed)" not in text
        assert "NOT IN FORCE" not in text


def test_the_directive_search_skips_only_an_example_in_a_code_block() -> None:
    text = (
        "- Keep it. ^kept\n- Read it. ^read (proposed)\n\n"
        "```markdown\n- Run it. ^example\n```\n\n- Show it. ^shown\n"
    )
    assert listed_directives(text) == {"kept", "read", "shown"}
    unfenced = text.replace("```markdown\n", "")
    assert listed_directives(unfenced) == {"kept", "read", "example", "shown"}
    assert "(proposed)" not in outside_code_blocks("```sh\ngrep '^<id> (proposed)'\n```\n")
    assert "(proposed)" in outside_code_blocks("Run grep '^<id> (proposed)'.\n")


def placed_ids(
    view: NodeView | StepView, applied: Mapping[str, Sequence[AppliedDirective]]
) -> list[str]:
    ids = [line.id for group in view.groups for line in group.directives]
    for read in view.reads:
        ids += list(read.directives) or [
            entry.directive.id
            for entry in applied[read.holder.id]
            if entry.holder == read.holder.id
        ]
    return ids


def test_the_review_result_of_the_real_seed_places_each_applied_directive_once() -> None:
    report = compile_tree(REPO, proposals=True)
    assert report.compiled is not None
    compiled = report.compiled
    view = build_view(compiled)
    tree = Tree([compiled.graph.root, *compiled.graph.nodes])
    for skill in view.skills:
        if skill.copy_steps:
            continue
        if not skill.steps:
            placed = placed_ids(skill, compiled.applied)
            assert sorted(placed) == sorted(
                {entry.directive.id for entry in compiled.applied[skill.link.id]}
            )
            continue
        (discipline,) = next(
            node.uses or []
            for node in compiled.graph.nodes
            if node.id == skill.link.id and isinstance(node, Skill)
        )
        expected = {
            entry.directive.id
            for node_id in [skill.link.id, *tree.subtree(discipline)]
            for entry in compiled.applied.get(node_id, ())
        }
        placed = placed_ids(skill, compiled.applied)
        assert len(placed) == len(set(placed)), skill.link.id
        in_steps = {item for step in skill.steps for item in placed_ids(step, compiled.applied)}
        assert not in_steps & set(placed), skill.link.id
        assert set(placed) | in_steps == expected, skill.link.id
    files = {entry.path.as_posix(): entry for entry in render_files(view)}
    assert all(entry.text.count("NOT IN FORCE") == 1 for entry in files.values())
    assert all(
        entry.limit is None or len(entry.whole_part) <= entry.limit for entry in files.values()
    )


def test_the_real_review_result_lists_directives_at_a_leaf_with_its_inherited_ones() -> None:
    report = compile_tree(REPO, proposals=True)
    assert report.compiled is not None
    files = {entry.path.as_posix(): entry for entry in render_files(build_view(report.compiled))}
    text = files[f"{REVIEW}/claude/references/visual-grouping.proposals.md"].text
    expected = {entry.directive.id for entry in report.compiled.applied["visual-grouping"]}
    found = set(re.findall(r" \^([a-z0-9-]+) \(proposed\)$", text, re.MULTILINE))
    assert found == expected
    assert "name-user-and-task" in found


REVIEW_SOURCE = "knowledge/skills/review/node.md"
PERSON_SAMPLE = {
    **SAMPLE,
    REVIEW_SOURCE: SAMPLE[REVIEW_SOURCE].replace("invocation: agent", "invocation: person"),
}
COPIES = ".claude/skills/review/scripts"
REVIEW_COPIES = f"{REVIEW}/claude/skills/review/scripts"
PERSON_LINE = "Only a person can start this skill."


def test_a_person_skill_turns_off_the_model_invocation() -> None:
    files = rendered(PERSON_SAMPLE)
    text = files[".claude/skills/review/SKILL.md"].text
    assert front_matter(text) == {
        "name": "review",
        "description": "Review a sample. Use when a sample needs a review.",
        "disable-model-invocation": True,
    }
    assert (
        f"- `review`: Review a sample. Use when a sample needs a review. {PERSON_LINE}\n"
        in files["AGENTS.md"].text
    )


def test_an_agent_skill_keeps_the_model_invocation() -> None:
    files = rendered()
    assert "disable-model-invocation" not in files[".claude/skills/review/SKILL.md"].text
    assert "ask the person" not in files[".claude/skills/review/SKILL.md"].text
    assert PERSON_LINE not in files["AGENTS.md"].text


def test_the_review_copy_of_a_person_skill_turns_off_the_model_invocation() -> None:
    files = rendered(PERSON_SAMPLE, proposals=True)
    text = files[f"{REVIEW}/claude/skills/review/SKILL.proposals.md"].text
    assert front_matter(text)["disable-model-invocation"] is True
    assert PERSON_LINE in files[f"{REVIEW}/AGENTS.proposals.md"].text


def write_skill_scripts(repository: Path, scripts: dict[str, bytes], skill: str = "review") -> Path:
    folder = repository / "knowledge/skills" / skill / "scripts"
    for name, data in scripts.items():
        path = folder / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    return folder


def is_executable(path: Path) -> bool:
    return bool(path.stat().st_mode & 0o111)


def test_a_run_copies_each_script_with_its_mode(tmp_path: Path) -> None:
    write_tree(tmp_path)
    source = write_skill_scripts(tmp_path, {"check.py": b"print(1)\n", "lib/notes.md": b"# N\n"})
    (source / "check.py").chmod(0o755)
    report = generate_runtime(tmp_path)
    assert report.problems == []
    copies = tmp_path / COPIES
    assert (copies / "check.py").read_bytes() == b"print(1)\n"
    assert (copies / "lib/notes.md").read_bytes() == b"# N\n"
    assert is_executable(copies / "check.py")
    assert not is_executable(copies / "lib/notes.md")
    expected = {PurePosixPath(f"{COPIES}/check.py"), PurePosixPath(f"{COPIES}/lib/notes.md")}
    assert expected <= set(report.files)
    assert expected <= set(report.written)
    again = generate_runtime(tmp_path)
    assert (again.written, again.removed, again.problems) == ((), (), [])


def test_a_mode_change_of_a_script_rewrites_its_copy(tmp_path: Path) -> None:
    write_tree(tmp_path)
    source = write_skill_scripts(tmp_path, {"check.py": b"x\n"})
    generate_runtime(tmp_path)
    copy = tmp_path / COPIES / "check.py"
    assert not is_executable(copy)
    (source / "check.py").chmod(0o755)
    assert generate_runtime(tmp_path).written == (PurePosixPath(f"{COPIES}/check.py"),)
    assert is_executable(copy)
    copy.chmod(0o644)
    assert generate_runtime(tmp_path).written == (PurePosixPath(f"{COPIES}/check.py"),)
    assert is_executable(copy)
    (source / "check.py").chmod(0o644)
    assert generate_runtime(tmp_path).written == (PurePosixPath(f"{COPIES}/check.py"),)
    assert not is_executable(copy)


def test_a_hand_edit_of_a_copied_script_is_rewritten(tmp_path: Path) -> None:
    write_tree(tmp_path)
    write_skill_scripts(tmp_path, {"check.py": b"x\n"})
    generate_runtime(tmp_path)
    (tmp_path / COPIES / "check.py").write_bytes(b"changed\n")
    assert generate_runtime(tmp_path).written == (PurePosixPath(f"{COPIES}/check.py"),)
    assert (tmp_path / COPIES / "check.py").read_bytes() == b"x\n"


def test_a_run_removes_a_stale_copied_script(tmp_path: Path) -> None:
    write_tree(tmp_path)
    source = write_skill_scripts(tmp_path, {"old.py": b"o\n", "keep.py": b"k\n", "deep/a.py": b"a"})
    generate_runtime(tmp_path)
    (source / "old.py").unlink()
    shutil.rmtree(source / "deep")
    (tmp_path / COPIES / "hand.py").write_bytes(b"h\n")
    report = generate_runtime(tmp_path)
    assert report.problems == []
    assert report.removed == (
        PurePosixPath(f"{COPIES}/deep/a.py"),
        PurePosixPath(f"{COPIES}/hand.py"),
        PurePosixPath(f"{COPIES}/old.py"),
    )
    assert sorted(path.name for path in (tmp_path / COPIES).iterdir()) == ["keep.py"]


def test_a_removed_scripts_folder_removes_each_copy_and_the_folder(tmp_path: Path) -> None:
    write_tree(tmp_path)
    source = write_skill_scripts(tmp_path, {"a.py": b"a", "deep/b.py": b"b"})
    generate_runtime(tmp_path)
    shutil.rmtree(source)
    report = generate_runtime(tmp_path)
    assert set(report.removed) == {
        PurePosixPath(f"{COPIES}/a.py"),
        PurePosixPath(f"{COPIES}/deep/b.py"),
    }
    assert not (tmp_path / COPIES).exists()
    assert (tmp_path / ".claude/skills/review/SKILL.md").is_file()


def test_a_removed_skill_removes_its_copied_scripts(tmp_path: Path) -> None:
    tool = node(
        "tool",
        "densho:Skill",
        front=SKILL_FRONT.replace("Use when a sample needs a review.", "Use when you need tool."),
        rules=[rule("tool-rule", scope="node")],
    )
    with_tool = {
        **SAMPLE,
        "knowledge/node.md": node(
            "root",
            "densho:Root",
            front=pointers(
                pointer("TextPointer", "alpha"),
                pointer("PathPointer", "gamma", "src/**/*"),
                pointer("AlwaysPointer", "delta"),
                pointer("TextPointer", "policies"),
                pointer("SkillPointer", "tool"),
            ),
        ),
        "knowledge/skills/tool/node.md": tool,
    }
    write_tree(tmp_path, with_tool)
    write_skill_scripts(tmp_path, {"run.sh": b"echo\n"}, skill="tool")
    assert generate_runtime(tmp_path).problems == []
    assert (tmp_path / ".claude/skills/tool/scripts/run.sh").is_file()
    shutil.rmtree(tmp_path / "knowledge/skills/tool")
    (tmp_path / "knowledge/node.md").write_text(SAMPLE["knowledge/node.md"], encoding="utf-8")
    report = generate_runtime(tmp_path)
    assert report.problems == []
    assert set(report.removed) == {
        PurePosixPath(".claude/skills/tool/SKILL.md"),
        PurePosixPath(".claude/skills/tool/scripts/run.sh"),
    }
    assert not (tmp_path / ".claude/skills/tool").exists()


def test_a_scripts_folder_of_a_hand_skill_stays(tmp_path: Path) -> None:
    write_tree(tmp_path)
    hand = tmp_path / ".claude/skills/mine"
    (hand / "scripts").mkdir(parents=True)
    (hand / "SKILL.md").write_bytes(b"---\nname: mine\n---\n# Mine\n")
    (hand / "scripts/run.sh").write_bytes(f"{MARKER}\n".encode())
    report = generate_runtime(tmp_path)
    assert report.problems == []
    assert (hand / "scripts/run.sh").is_file()


def test_a_hand_file_at_a_copy_path_stops_the_run(tmp_path: Path) -> None:
    write_tree(tmp_path)
    write_skill_scripts(tmp_path, {"check.py": b"x\n"})
    hand = tmp_path / COPIES / "check.py"
    hand.parent.mkdir(parents=True)
    hand.write_bytes(b"mine\n")
    report = generate_runtime(tmp_path)
    assert [(problem.path, problem.code) for problem in report.problems] == [
        (hand, "not-generated")
    ]
    assert hand.read_bytes() == b"mine\n"


def test_a_copy_of_a_skill_with_a_hand_skill_file_stops_the_run(tmp_path: Path) -> None:
    write_tree(tmp_path)
    write_skill_scripts(tmp_path, {"check.py": b"x\n"})
    generate_runtime(tmp_path)
    (tmp_path / ".claude/skills/review/SKILL.md").write_bytes(b"# Mine\n")
    report = generate_runtime(tmp_path)
    assert sorted(
        (problem.path.relative_to(tmp_path).as_posix(), problem.code) for problem in report.problems
    ) == [
        (".claude/skills/review/SKILL.md", "not-generated"),
        (f"{COPIES}/check.py", "not-generated"),
    ]


def test_a_git_ignored_file_in_a_copied_folder_stays(tmp_path: Path) -> None:
    write_tree(tmp_path)
    git(tmp_path, "init", "-q", "--template=", "--initial-branch=main")
    (tmp_path / ".gitignore").write_text("__pycache__/\n", encoding="utf-8")
    write_skill_scripts(tmp_path, {"check.py": b"x\n"})
    generate_runtime(tmp_path)
    cache = tmp_path / COPIES / "__pycache__/check.pyc"
    cache.parent.mkdir()
    cache.write_bytes(b"cache")
    stale = tmp_path / COPIES / "stale.py"
    stale.write_bytes(b"s")
    report = generate_runtime(tmp_path)
    assert report.problems == []
    assert report.removed == (PurePosixPath(f"{COPIES}/stale.py"),)
    assert cache.read_bytes() == b"cache"


def test_an_anchored_ignore_works_with_a_relative_repository(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repository = tmp_path / "repo"
    write_tree(repository)
    git(repository, "init", "-q", "--template=", "--initial-branch=main")
    source = "knowledge/skills/review/scripts"
    (repository / ".gitignore").write_text(
        f"/{source}/local.bin\n/{COPIES}/cache.bin\n", encoding="utf-8"
    )
    write_skill_scripts(repository, {"check.py": b"x\n", "local.bin": b"l"})
    monkeypatch.chdir(tmp_path)
    assert generate_runtime(Path("repo")).problems == []
    assert sorted(path.name for path in (repository / COPIES).iterdir()) == ["check.py"]
    cache = repository / COPIES / "cache.bin"
    cache.write_bytes(b"cache")
    report = generate_runtime(Path("repo"))
    assert (report.problems, report.removed) == ([], ())
    assert cache.read_bytes() == b"cache"


def test_a_body_link_to_a_script_resolves_only_when_the_script_exists(tmp_path: Path) -> None:
    sources = {
        **SAMPLE,
        REVIEW_SOURCE: SAMPLE[REVIEW_SOURCE].replace(
            SKILL_BODY, f"{SKILL_BODY}2. Run [the check](scripts/check.py).\n"
        ),
    }
    write_tree(tmp_path, sources)
    assert codes(generate_runtime(tmp_path).problems) == ["link"]
    write_skill_scripts(tmp_path, {"check.py": b"x\n"})
    assert generate_runtime(tmp_path).problems == []


def test_the_review_copy_holds_the_scripts(tmp_path: Path) -> None:
    write_tree(tmp_path)
    source = write_skill_scripts(tmp_path, {"check.py": b"x\n", "old.sh": b"echo\n"})
    (source / "check.py").chmod(0o755)
    assert generate_runtime(tmp_path, proposals=True).problems == []
    review = tmp_path / REVIEW_COPIES
    assert (review / "check.py").read_bytes() == b"x\n"
    assert is_executable(review / "check.py")
    assert (review / "old.sh").read_bytes() == b"echo\n"
    assert not (tmp_path / COPIES).exists()
    (source / "old.sh").unlink()
    report = generate_runtime(tmp_path, proposals=True)
    assert report.removed == (PurePosixPath(f"{REVIEW_COPIES}/old.sh"),)


def test_a_run_counts_the_entities_that_wait_for_review(tmp_path: Path) -> None:
    write_tree(tmp_path)
    entities, _ = pending_entities(tmp_path)
    report = generate_runtime(tmp_path)
    assert report.pending == len(entities) > 0


def test_a_rejected_entity_is_not_counted(tmp_path: Path) -> None:
    rejected = (
        "- Run the old check. ^old\n  - scope: node\n  - basis: judgment\n"
        "  - status: rejected\n  - origin: template\n  - rejection_reason: No need.\n"
    )
    write_tree(tmp_path)
    before = generate_runtime(tmp_path).pending
    (tmp_path / "knowledge/nodes/delta/node.md").write_text(
        node("delta", rules=[rejected]), encoding="utf-8"
    )
    report = generate_runtime(tmp_path)
    assert report.problems == []
    assert report.pending == before
    generated = {
        path: data for path, data in disk_files(tmp_path).items() if MARKER.encode() in data
    }
    assert ".claude/rules/knowledge/delta.md" in generated
    assert not [path for path, data in generated.items() if b"old check" in data]
    assert generate_runtime(tmp_path, proposals=True).problems == []
    review = {path: data for path, data in disk_files(tmp_path).items() if path.startswith(REVIEW)}
    assert f"{REVIEW}/claude/rules/knowledge/delta.proposals.md" in review
    assert not [path for path, data in review.items() if b"old check" in data]


def test_verify_passes_with_entities_that_wait_for_review(tmp_path: Path) -> None:
    committed_repository(tmp_path)
    report = generate_runtime(tmp_path, verify=True)
    assert report.problems == []
    assert report.pending is not None
    assert report.pending > 0


def test_a_failed_compile_counts_nothing(tmp_path: Path) -> None:
    write_tree(tmp_path, {**SAMPLE, "knowledge/nodes/delta/node.md": "---\nid: delta\n---\n"})
    report = generate_runtime(tmp_path)
    assert report.problems
    assert report.pending is None


def test_the_command_prints_the_pending_count(tmp_path: Path) -> None:
    write_tree(tmp_path)
    count = generate_runtime(tmp_path).pending
    result = RUNNER.invoke(app, ["runtime", str(tmp_path)])
    assert result.exit_code == 0
    assert (
        f"{count} entities wait for review. Run uv run densho governance --pending to list them.\n"
        in result.output
    )
    launcher = tmp_path / "knowledge/.densho/densho"
    launcher.parent.mkdir(parents=True)
    launcher.write_text("#!/bin/sh\n", encoding="utf-8")
    result = RUNNER.invoke(app, ["runtime", str(tmp_path)])
    assert "Run knowledge/.densho/densho governance --pending" in result.output


def test_the_command_prints_no_count_after_a_failed_compile(tmp_path: Path) -> None:
    write_tree(tmp_path, {**SAMPLE, "knowledge/nodes/delta/node.md": "---\nid: delta\n---\n"})
    result = RUNNER.invoke(app, ["runtime", str(tmp_path)])
    assert result.exit_code == 1
    assert "wait for review" not in result.output


FLOW_ROW = "  - kind: densho:SkillPointer\n    target: flow\n    trigger: You change the area.\n"
FLOW_FRONT = (
    "description: Run the area flow. Use when you change the area.\n"
    "invocation: agent\nskill_type: task\nuses: [disc]\nsteps: [one, two]\n"
    "exceptions:\n  - directive: disc-stopped\n    reason: The flow skips it.\n"
    "    status: accepted\n"
)
FLOW_SAMPLE = {
    "knowledge/node.md": node(
        "root",
        "densho:Root",
        front=pointers(pointer("TextPointer", "area"), pointer("TextPointer", "other")) + FLOW_ROW,
    ),
    "knowledge/nodes/area/node.md": node(
        "area",
        front=pointers(pointer("TextPointer", "disc")),
        rules=[rule("area-rule")],
    ),
    "knowledge/nodes/area/disc/node.md": node(
        "disc",
        "densho:Discipline",
        front="broader: [area]\n"
        + pointers(
            pointer("TextPointer", "one"),
            pointer("TextPointer", "two"),
            pointer("TextPointer", "side"),
        ),
        rules=[rule("disc-rule"), rule("disc-stopped")],
    ),
    "knowledge/nodes/area/disc/one/node.md": node(
        "one",
        "densho:PracticeArea",
        front="broader: [disc]\ninforms: [two, out]\n" + pointers(pointer("TextPointer", "one-c")),
        rules=[rule("one-own", scope="node")],
    ),
    "knowledge/nodes/area/disc/one/one-c/node.md": node(
        "one-c", "densho:Concept", front="broader: [one]\n", rules=[rule("one-concept")]
    ),
    "knowledge/nodes/area/disc/two/node.md": node(
        "two",
        "densho:PracticeArea",
        front="broader: [disc]\n" + pointers(pointer("TextPointer", "two-c")),
    ),
    "knowledge/nodes/area/disc/two/two-c/node.md": node(
        "two-c",
        "densho:Concept",
        front="broader: [two]\n",
        rules=[rule("two-concept")],
    ),
    "knowledge/nodes/area/disc/side/node.md": node(
        "side", "densho:PracticeArea", front="broader: [disc]\n", rules=[rule("side-rule")]
    ),
    "knowledge/nodes/other/node.md": node(
        "other",
        front=pointers(
            pointer("TextPointer", "far"),
            pointer("TextPointer", "near"),
            pointer("TextPointer", "out"),
        ),
    ),
    "knowledge/nodes/other/far/node.md": node(
        "far",
        "densho:Discipline",
        front="broader: [other]\n",
        rules=[
            rule("far-kept", scope="node").replace(
                "  - origin: template\n", "  - origin: template\n  - also_attached_to: one-c\n"
            ),
            rule("far-alone", scope="node"),
        ],
    ),
    "knowledge/nodes/other/near/node.md": node(
        "near",
        "densho:Discipline",
        front="broader: [other]\n",
        rules=[
            rule("near-all", scope="node").replace(
                "  - origin: template\n", "  - origin: template\n  - also_attached_to: two-c\n"
            )
        ],
    ),
    "knowledge/nodes/other/out/node.md": node(
        "out", "densho:Discipline", front="broader: [other]\n"
    ),
    "knowledge/skills/flow/node.md": node("flow", "densho:Skill", front=FLOW_FRONT),
}
STEP_SOURCE = (
    "## Inputs\n\n- The {0} input\n\n## Procedure\n\n1. Run {0}.\n\n## Output\n\n"
    "The {0} output.\n\n## Exit gate\n\nThe {0} gate holds.\n"
)


def flow_step_files() -> tuple[StepFile, ...]:
    return tuple(
        StepFile(
            step,
            (
                ("Inputs", f"- The {step} input"),
                ("Procedure", f"1. Run {step}."),
                ("Output", f"The {step} output."),
                ("Exit gate", f"The {step} gate holds."),
            ),
        )
        for step in ("one", "two")
    )


def flow_files(
    sources: dict[str, str] | None = None, *, proposals: bool = False
) -> dict[str, RenderedFile]:
    items = [
        replace(item, step_files=flow_step_files()) if item.node.id == "flow" else item
        for item in parsed(FLOW_SAMPLE if sources is None else sources)
    ]
    view = build_view(compile_items(items, Path(), proposals=proposals))
    return {entry.path.as_posix(): entry for entry in render_files(view)}


FLOW_SKILL = ".claude/skills/flow/SKILL.md"
STEP_ONE = ".claude/skills/flow/steps/one.md"
STEP_TWO = ".claude/skills/flow/steps/two.md"


def test_a_flow_puts_each_directive_in_one_file() -> None:
    files = flow_files()
    assert listed_directives(files[FLOW_SKILL].text) == {"disc-rule", "one-own", "side-rule"}
    assert listed_directives(files[STEP_ONE].text) == {"one-concept"}
    assert listed_directives(files[STEP_TWO].text) == {"two-concept"}


def test_a_flow_links_each_directive_from_another_branch_as_a_required_read() -> None:
    files = flow_files()
    assert (
        "- Read [area](../../references/area.md), and follow each directive from area.\n"
        in files[FLOW_SKILL].text
    )
    assert (
        "- Read [far](../../../references/far.md), and follow these directives from it: "
        "`far-kept`.\n" in files[STEP_ONE].text
    )
    assert (
        "- Read [near](../../../references/near.md), and follow each directive from near.\n"
        in files[STEP_TWO].text
    )
    assert "Required reads" not in files[FLOW_SKILL].text.split("## Steps")[1]


def test_an_exception_of_the_flow_stops_its_directive_in_each_file() -> None:
    files = flow_files()
    assert all("disc-stopped" not in entry.text for path, entry in files.items() if "steps" in path)
    assert "disc-stopped" not in listed_directives(files[FLOW_SKILL].text)
    assert "- `disc-stopped` does not apply at this node. The flow skips it.\n" in (
        files[FLOW_SKILL].text
    )


def test_a_flow_lists_its_steps_in_their_order() -> None:
    text = flow_files()[FLOW_SKILL].text
    assert "1. [one](steps/one.md)\n2. [two](steps/two.md)\n" in text
    assert "4. Go to the next step only after the exit gate of the step passes.\n" in text
    assert "## References" not in text


def test_a_step_file_holds_its_place_its_sections_and_its_links() -> None:
    files = flow_files()
    one = files[STEP_ONE].text
    assert "This file is step 1 of 2 of the skill `flow`." in one
    assert "## Inputs\n\n- The one input\n" in one
    assert "## Procedure\n\n1. Run one.\n" in one
    assert "## Exit gate\n\nThe one gate holds.\n" in one
    assert "- [out](../../../references/out.md)\n- [two](two.md)\n" in one
    assert "## Next step\n\nRead [two](two.md).\n" in one
    assert "- You need one-c. Read [one-c](../../../references/one-c.md).\n" in one
    two = files[STEP_TWO].text
    assert "This file is step 2 of 2 of the skill `flow`." in two
    assert (
        "The output of each node in this list is an input of this step:\n\n- [one](one.md)\n" in two
    )
    assert "This step is the last step of the skill.\n" in two
    assert "The output of this step is an input" not in two


def test_no_generated_skill_file_holds_a_compaction_line() -> None:
    skill = ".claude/skills/review/SKILL.md"
    texts = {
        "agent skill": rendered()[skill].text,
        "person skill": rendered(PERSON_SAMPLE)[skill].text,
        "person review copy": rendered(PERSON_SAMPLE, proposals=True)[
            f"{REVIEW}/{review_path(PurePosixPath(skill)).as_posix()}"
        ].text,
        "flow skill": flow_files()[FLOW_SKILL].text,
        "step file": flow_files()[STEP_ONE].text,
        "last step file": flow_files()[STEP_TWO].text,
        "step review copy": flow_files(proposals=True)[
            f"{REVIEW}/{review_path(PurePosixPath(STEP_ONE)).as_posix()}"
        ].text,
    }
    for name, text in texts.items():
        assert "## Directives" in text, name
        assert not COMPACTION_SENTENCE.search(text), name


def test_no_committed_skill_file_holds_a_compaction_line() -> None:
    folders = (REPO / ".claude/skills", REPO / "fixtures/project/claude/skills")
    paths = [
        path
        for folder in folders
        for path in sorted(folder.rglob("*.md"))
        if is_generated(path.read_bytes())
    ]
    for folder in folders:
        assert any(path.is_relative_to(folder) and path.name == "SKILL.md" for path in paths)
        assert any(path.is_relative_to(folder) and path.parent.name == "steps" for path in paths)
    for path in paths:
        assert not COMPACTION_SENTENCE.search(path.read_text(encoding="utf-8")), path


def test_the_root_tells_the_agent_to_invoke_a_skill_again_after_a_compaction() -> None:
    roots = {
        "sample": rendered(PERSON_SAMPLE)["AGENTS.md"].text,
        "repo": (REPO / "AGENTS.md").read_text(encoding="utf-8"),
        "fixture": (REPO / "fixtures/project/AGENTS.fixture.md").read_text(encoding="utf-8"),
    }
    for name, text in roots.items():
        section = text.partition("\n## Use a skill\n\n")[2].partition("\n## Create a rule\n")[0]
        assert section.endswith(f"{ROOT_COMPACTION_LINE}\n"), name
        assert text.count(ROOT_COMPACTION_LINE) == 1, name


def test_a_step_file_names_its_source_for_a_problem() -> None:
    files = flow_files()
    assert files[STEP_ONE].node_path == "knowledge/skills/flow/steps/one.md"
    assert files[STEP_ONE].limit == claude_code.STEP_CHARACTERS
    assert files[STEP_ONE].line_limit is None


def test_a_step_file_can_hold_one_read_call_and_no_more() -> None:
    assert claude_code.STEP_CHARACTERS == 25_000 * LOW_CHARACTERS_PER_TOKEN
    text = "x" * (claude_code.STEP_CHARACTERS + 1)
    entry = RenderedFile(
        PurePosixPath(STEP_ONE),
        text,
        "knowledge/skills/flow/steps/one.md",
        text,
        claude_code.STEP_CHARACTERS,
    )
    (problem,) = size_problems([entry], Path("/repo"))
    assert (problem.path, problem.code) == (
        Path("/repo/knowledge/skills/flow/steps/one.md"),
        "size",
    )
    fits = replace(entry, text=text[1:], whole_part=text[1:])
    assert size_problems([fits], Path("/repo")) == []


def test_the_review_copy_renames_each_step_file() -> None:
    items = [
        replace(item, step_files=flow_step_files()) if item.node.id == "flow" else item
        for item in parsed(FLOW_SAMPLE)
    ]
    view = build_view(compile_items(items, Path(), proposals=True))
    paths = {entry.path.as_posix() for entry in render_files(view)}
    assert f"{REVIEW}/claude/skills/flow/steps/one.proposals.md" in paths
    text = next(e.text for e in render_files(view) if e.path.name == "one.proposals.md")
    assert "Read [two](two.proposals.md)." in text


def test_the_root_holds_a_row_for_each_skill_pointer_on_the_root() -> None:
    text = flow_files()["AGENTS.md"].text
    assert "| Activity | Skill |\n| --- | --- |\n| You change the area. | `flow` |\n" in text
    assert "These skills have no row" not in text
    assert "- `flow`:" not in text
    assert "Use the skill `flow`." not in text


def test_a_row_escapes_a_pipe_in_its_activity() -> None:
    sources = {
        **FLOW_SAMPLE,
        "knowledge/node.md": FLOW_SAMPLE["knowledge/node.md"].replace(
            "You change the area.", "You change a | b."
        ),
    }
    assert "| You change a \\| b. | `flow` |\n" in flow_files(sources)["AGENTS.md"].text


def test_a_skill_without_a_row_sits_under_the_table() -> None:
    sources = {
        **FLOW_SAMPLE,
        "knowledge/skills/review/node.md": node(
            "review",
            "densho:Skill",
            front=SKILL_FRONT.replace("gamma", "area"),
            body=SKILL_BODY,
        ),
    }
    text = flow_files(sources)["AGENTS.md"].text
    assert "These skills have no row:\n\n- `review`: Review a sample." in text


def test_a_run_writes_each_step_file_and_removes_a_stale_one(tmp_path: Path) -> None:
    write_tree(tmp_path, FLOW_SAMPLE)
    steps = tmp_path / "knowledge/skills/flow/steps"
    steps.mkdir()
    for step in ("one", "two"):
        (steps / f"{step}.md").write_text(STEP_SOURCE.format(step), encoding="utf-8")
    report = generate_runtime(tmp_path)
    assert report.problems == []
    assert (tmp_path / STEP_TWO).read_text(encoding="utf-8").startswith(MARKER)
    stale = tmp_path / ".claude/skills/flow/steps/old.md"
    stale.write_text((tmp_path / STEP_TWO).read_text(encoding="utf-8"), encoding="utf-8")
    again = generate_runtime(tmp_path)
    assert again.removed == (PurePosixPath(".claude/skills/flow/steps/old.md"),)
    assert not stale.exists()


LENS_SAMPLE = {
    **FLOW_SAMPLE,
    "knowledge/nodes/area/disc2/node.md": node(
        "disc2",
        "densho:Discipline",
        front="broader: [area]\n",
        rules=[
            rule("sib-rule", scope="node").replace(
                "  - origin: template\n", "  - origin: template\n  - also_attached_to: one-c\n"
            )
        ],
    ),
    "knowledge/skills/lens/node.md": node(
        "lens",
        "densho:Skill",
        front=(
            "description: Review the area. Use when you review the area.\n"
            "invocation: agent\nskill_type: lens\nuses: [one-c]\n"
        ),
    ),
    "knowledge/skills/wide/node.md": node(
        "wide",
        "densho:Skill",
        front=(
            "description: Review the area. Use when you review all of it.\n"
            "invocation: agent\nskill_type: lens\nuses: [area]\n"
        ),
    ),
}


def test_a_lens_copies_its_discipline_and_reads_the_rest() -> None:
    text = flow_files(LENS_SAMPLE)[".claude/skills/lens/SKILL.md"].text
    assert listed_directives(text) == {"one-concept", "disc-rule", "disc-stopped"}
    assert "- Read [area](../../references/area.md), and follow each directive from area.\n" in (
        text
    )
    assert (
        "- Read [disc2](../../references/disc2.md), and follow each directive from disc2.\n" in text
    )


def test_a_skill_that_uses_a_domain_copies_the_domain() -> None:
    text = flow_files(LENS_SAMPLE)[".claude/skills/wide/SKILL.md"].text
    assert listed_directives(text) == {"area-rule"}
    assert "## Required reads" not in text


def test_the_compiled_graph_keeps_the_order_of_steps() -> None:
    sources = {
        **FLOW_SAMPLE,
        "knowledge/skills/flow/node.md": FLOW_SAMPLE["knowledge/skills/flow/node.md"].replace(
            "steps: [one, two]", "steps: [two, one]"
        ),
    }
    text = flow_files(sources)[FLOW_SKILL].text
    assert "1. [two](steps/two.md)\n2. [one](steps/one.md)\n" in text
    two = flow_files(sources)[STEP_TWO].text
    assert "This file is step 1 of 2 of the skill `flow`." in two
    assert "Read [one](one.md)." in two


MAKE_ROW = "  - kind: densho:SkillPointer\n    target: make\n    trigger: You make the area.\n"
MAKE_BODY = "## Exit checklist\n\n- [ ] Each step has its output.\n\n## Output\n\nThe made area.\n"


def make_front(steps: tuple[str, ...], skill_type: str = "task") -> str:
    return (
        "description: Run the area work. Use when you make the area.\n"
        f"invocation: agent\nskill_type: {skill_type}\nuses: [disc]\n"
        f"steps: [{', '.join(steps)}]\n"
    )


def copy_source(
    title: str,
    directives: tuple[str, ...] = (),
    *,
    pages: tuple[str, ...] = (),
    branches: tuple[tuple[str, tuple[str, ...]], ...] = (),
    missing: tuple[str, ...] = (),
) -> str:
    lines = ["---", f"title: {title}"]
    if pages:
        lines += ["pages:"]
        lines += [f"  - target: {page}\n    trigger: You need {page}." for page in pages]
    if directives:
        lines += ["directives:", *[f"  - {name}" for name in directives]]
    if branches:
        lines += ["branches:"]
        for condition, names in branches:
            lines += [f"  - condition: {condition}", "    directives:"]
            lines += [f"      - {name}" for name in names]
    if missing:
        lines += ["missing_rules:", *[f"  - {rule}" for rule in missing]]
    lines += ["---", "", "## Procedure", "", f"1. Run {title}.", "", "## Output", ""]
    return "\n".join([*lines, f"The {title} output.", ""])


THREE_STEPS = {
    "first": copy_source("first", ("area-rule", "make-own"), pages=("disc",)),
    "second": copy_source(
        "second",
        ("disc-rule", "one-own"),
        branches=(("If the area is wide", ("two-concept",)),),
        missing=("No directive covers a narrow area.",),
    ),
    "third": copy_source(
        "third",
        ("side-rule", "one-concept", "far-kept", "far-alone", "near-all", "disc-stopped"),
    ),
}


def copy_files(
    steps: dict[str, str] | None = None,
    *,
    skill_type: str = "task",
    proposals: bool = False,
    status: str = "accepted",
) -> dict[str, RenderedFile]:
    chosen = THREE_STEPS if steps is None else steps
    sources = {
        **FLOW_SAMPLE,
        "knowledge/node.md": FLOW_SAMPLE["knowledge/node.md"].replace(
            FLOW_ROW, FLOW_ROW + MAKE_ROW
        ),
        "knowledge/skills/make/node.md": node(
            "make",
            "densho:Skill",
            front=make_front(tuple(chosen), skill_type),
            rules=[rule("make-own", status, "node")],
            body=MAKE_BODY,
        ),
    }
    folder = Path("knowledge/skills/make/steps")
    step_files: list[StepFile] = []
    for name, text in chosen.items():
        found = read_step_source(text, folder / f"{name}.md")
        assert isinstance(found, StepFile), found
        step_files.append(found)
    items = [
        replace(item, step_files=flow_step_files())
        if item.node.id == "flow"
        else replace(item, step_files=tuple(sorted(step_files)))
        if item.node.id == "make"
        else item
        for item in parsed(sources)
    ]
    view = build_view(compile_items(items, Path(), proposals=proposals))
    return {entry.path.as_posix(): entry for entry in render_files(view)}


MAKE_SKILL = ".claude/skills/make/SKILL.md"
MAKE_STEPS = ".claude/skills/make/steps"


def test_a_skill_with_copies_holds_its_run_list_and_its_steps_in_order() -> None:
    text = copy_files()[MAKE_SKILL].text
    order = [
        "# make",
        "## Run the skill",
        "1. Run the steps in their order.",
        "2. If the output of a step exists already, skip the step.",
        "3. If a step has a step file, read the step file.",
        "4. Follow each directive of the step.",
        "5. If a branch heading matches the work, follow each directive under it.",
        "6. If you need the definition or the notes of a page, read the page.",
        "7. After each step, check its output against each directive of the step.",
        "8. Before you start the next step, correct each part of the output that breaks a",
        "## 1. first",
        "1. Run first.",
        "Pages:",
        "- You need disc. Read [disc](../../references/disc.md).",
        "Directives:",
        "- Run the area-rule check. ^area-rule\n",
        "- Run the make-own check. ^make-own\n",
        "Output: The first output.",
        "## 2. second",
        "Step file: [steps/second.md](steps/second.md)",
        "1. Run second.",
        "Missing rule: No directive covers a narrow area.",
        "Output: The second output.",
        "## 3. third",
        "Step file: [steps/third.md](steps/third.md)",
        "## Exit checklist",
        "## Output",
    ]
    places = [text.index(part) for part in order]
    assert places == sorted(places)
    assert "^disc-rule" not in text
    assert "^two-concept" not in text
    assert "## Directives" not in text


def test_only_a_step_with_a_branch_or_over_five_directives_gets_a_file() -> None:
    files = copy_files()
    assert f"{MAKE_STEPS}/first.md" not in files
    assert f"{MAKE_STEPS}/second.md" in files
    assert f"{MAKE_STEPS}/third.md" in files
    five = {**THREE_STEPS, "third": THREE_STEPS["third"].replace("  - disc-stopped\n", "")}
    assert f"{MAKE_STEPS}/third.md" not in copy_files(five)


def test_a_step_file_holds_its_place_its_copies_and_its_way_back() -> None:
    files = copy_files()
    second = files[f"{MAKE_STEPS}/second.md"].text
    order = [
        "# second",
        "This file is step 2 of 3 of the skill `make`.",
        "## Directives",
        "- Run the disc-rule check. ^disc-rule\n",
        "- Run the one-own check. ^one-own\n",
        "## Branches",
        "If a heading matches the work, follow each directive under it.",
        "### If the area is wide",
        "- Run the two-concept check. ^two-concept\n",
        "## Next step",
        "Return to step 3 of [the skill](../SKILL.md).",
    ]
    places = [second.index(part) for part in order]
    assert places == sorted(places)
    third = files[f"{MAKE_STEPS}/third.md"].text
    assert "Return to the exit checklist of [the skill](../SKILL.md)." in third
    assert "## Branches" not in third
    assert "## Pages" not in third


def test_a_step_file_lists_its_pages() -> None:
    steps = {
        **THREE_STEPS,
        "second": THREE_STEPS["second"].replace(
            "title: second\n",
            "title: second\npages:\n  - target: two\n    trigger: You need two.\n",
        ),
    }
    second = copy_files(steps)[f"{MAKE_STEPS}/second.md"].text
    assert "## Pages\n\n- You need two. Read [two](../../../references/two.md).\n" in second


def test_a_single_step_has_no_number_no_file_and_no_order_lines() -> None:
    steps = {"only": THREE_STEPS["second"].replace("title: second", "title: only")}
    steps["only"] = steps["only"].replace("  - one-own\n", "  - one-own\n  - make-own\n")
    files = copy_files(steps)
    text = files[MAKE_SKILL].text
    assert "## only\n" in text
    assert "## 1. only" not in text
    assert f"{MAKE_STEPS}/only.md" not in files
    assert "### If the area is wide\n\n- Run the two-concept check. ^two-concept\n" in text
    assert "1. Follow each directive of the skill.\n" in text
    for line in ("Run the steps", "skip the step", "read the step file", "After each step"):
        assert line not in text


def test_a_lens_checks_the_work_against_its_copies() -> None:
    steps = {"only": THREE_STEPS["second"].replace("  - one-own\n", "  - one-own\n  - make-own\n")}
    text = copy_files(steps, skill_type="lens")[MAKE_SKILL].text
    assert "1. Check the work against each directive of the skill.\n" in text
    assert "2. If a branch heading matches the work, check the work against each directive" in text


def test_a_lens_step_file_checks_the_work_in_its_branches() -> None:
    steps = {
        "first": THREE_STEPS["first"],
        "second": THREE_STEPS["second"],
    }
    files = copy_files(steps, skill_type="lens")
    second = files[f"{MAKE_STEPS}/second.md"].text
    assert (
        "If a heading matches the work, check the work against each directive under it." in second
    )
    text = files[MAKE_SKILL].text
    assert "After each step" not in text
    assert "Before you start the next step" not in text


def test_a_copy_that_is_not_in_force_drops_out() -> None:
    in_force = copy_files(status="proposed")[MAKE_SKILL].text
    assert "^make-own" not in in_force
    assert "^area-rule" in in_force
    files = copy_files(status="proposed", proposals=True)
    review = files[f"{REVIEW}/claude/skills/make/SKILL.proposals.md"].text
    assert "- Run the make-own check. ^make-own (proposed)\n" in review


def test_a_step_with_no_copy_in_force_says_so() -> None:
    steps = {**THREE_STEPS, "first": copy_source("first", ("make-own",))}
    text = copy_files(steps, status="proposed")[MAKE_SKILL].text
    assert "Directives:\n\nNo directive of this step is in force.\n" in text


def test_a_skill_with_copies_has_no_directive_section_and_no_uses_links() -> None:
    text = copy_files()[MAKE_SKILL].text
    assert "Read [disc](../../references/disc.md)." in text
    assert "## References" not in text
    assert "Required reads" not in text


def root_with_sections(front: str, statuses: dict[str, str] | None = None) -> dict[str, str]:
    marks = statuses or {}
    root = node(
        "root",
        "densho:Root",
        front=pointers(
            pointer("TextPointer", "alpha"),
            pointer("PathPointer", "gamma", "src/**/*"),
            pointer("AlwaysPointer", "delta"),
            pointer("TextPointer", "policies"),
        )
        + front,
        rules=[
            rule(name, marks.get(name, "accepted"), "node")
            for name in ("each-one", "use-one", "rule-one", "rule-two")
        ],
        body="## Architecture\n\nA fact that no file shows.\n",
    )
    return {**SAMPLE, "knowledge/node.md": root}


def section_of(text: str, heading: str) -> str:
    after = text.partition(f"\n## {heading}\n\n")[2]
    return after.partition("\n## ")[0]


def test_the_root_puts_each_named_directive_in_its_section() -> None:
    sources = root_with_sections("use_a_skill: [use-one]\ncreate_a_rule: [rule-two, rule-one]\n")
    text = rendered(sources)["AGENTS.md"].text
    each = section_of(text, "Rules for each task")
    assert "^each-one" in each
    assert "^use-one" not in each
    assert "^rule-one" not in each
    use = section_of(text, "Use a skill")
    assert use.startswith("- Run the use-one check. ^use-one\n\nIf compaction")
    create = section_of(text, "Create a rule")
    assert create.index("^rule-two") < create.index("^rule-one")
    assert create.startswith("A rule starts when a person states a new rule or corrects your work.")


def test_a_root_section_can_name_a_directive_of_another_node() -> None:
    sources = root_with_sections("create_a_rule: [keep]\n")
    text = rendered(sources)["AGENTS.md"].text
    assert "- Run the keep check. ^keep\n" in section_of(text, "Create a rule")


def test_an_empty_create_a_rule_section_says_so() -> None:
    sources = root_with_sections("create_a_rule: [rule-one]\n", {"rule-one": "proposed"})
    text = rendered(sources)["AGENTS.md"].text
    assert "No directive of this section is in force.\n" in section_of(text, "Create a rule")
    plain = rendered(root_with_sections(""), proposals=True)
    review = plain[f"{REVIEW}/AGENTS.proposals.md"].text
    assert "No directive is in this section.\n" in section_of(review, "Create a rule")


def test_the_root_without_a_root_rule_says_how_to_add_one() -> None:
    text = rendered()["AGENTS.md"].text
    message = (
        "No other directive applies to each task. A project adds a rule for each task as a "
        "directive on the root with `scope: node`."
    )
    assert message in section_of(text, "Rules for each task")


def test_the_root_leaves_out_its_body() -> None:
    text = rendered(root_with_sections(""))["AGENTS.md"].text
    assert "A fact that no file shows." not in text
    assert "## Architecture" not in text


def test_a_root_with_no_skill_has_no_use_a_skill_section() -> None:
    sources = {
        "knowledge/node.md": node(
            "root", "densho:Root", front=pointers(pointer("TextPointer", "lone"))
        ),
        "knowledge/nodes/lone/node.md": node("lone"),
    }
    text = rendered(sources)["AGENTS.md"].text
    assert "## Use a skill" not in text
    assert "## Create a rule" in text
