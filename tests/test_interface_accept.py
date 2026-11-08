import shutil
import subprocess
from pathlib import Path

import pytest
from typer.testing import CliRunner

from engine.cli import app
from engine.generated.metamodel import Status
from engine.governance import check_governance, pending_entities
from engine.governance.entities import Entity
from engine.governance.status_line import set_status_lines
from engine.graph import check_tree
from engine.interface import accept_entities, command_prefix
from engine.runtime import claude_code, generate_runtime

REPO = Path(__file__).resolve().parents[1]
RUNNER = CliRunner()
GIT = shutil.which("git") or "git"
USAGE_ERROR = 2
GROUP_READABLE = 0o640
ROOT = """---
id: root
kind: densho:Root
title: Root
status: proposed
origin: template
pointers:
  - kind: densho:TextPointer
    target: alpha
    trigger: You need alpha.
  - kind: densho:TextPointer
    target: gamma
    trigger: You need gamma.
---
"""
ALPHA = """---
id: alpha
kind: densho:Domain
title: Alpha
status: proposed
origin: template
knowledge_type: domain
pointers:
  - kind: densho:TextPointer
    target: beta
    trigger: You need beta.
  - kind: densho:SkillPointer
    target: review
    trigger: You need review.
---

## Definition

The meaning of alpha.

## Directives

- Run the check. ^keep
  - scope: subtree
  - basis: judgment
  - status: proposed
  - origin: template
- Run the other check. ^wait
  - scope: subtree
  - basis: judgment
  - status: proposed
  - origin: template
"""
BETA = """---
id: beta
kind: densho:Concept
title: Beta
status: proposed
origin: template
knowledge_type: domain
broader:
  - alpha
exceptions:
  - directive: wait
    reason: A reason for beta.
    status: proposed
---

## Definition

The meaning of beta.

## Directives

- Run the third check. ^bound
  - scope: node
  - basis: judgment
  - status: proposed
  - origin: template
"""
GAMMA = """---
id: gamma
kind: densho:Domain
title: Gamma
status: proposed
origin: template
knowledge_type: domain
---

## Definition

The meaning of gamma.
"""
SKILL = """---
id: review
kind: densho:Skill
title: Review
status: proposed
origin: template
knowledge_type: domain
description: Review a sample. Use when a sample needs a review.
invocation: agent
skill_type: system
uses:
  - beta
---

## Directives

- Run the skill check. ^own-rule
  - scope: node
  - basis: judgment
  - status: proposed
  - origin: template

## Procedure

1. Read each directive.
"""
TREE = {
    "knowledge/node.md": ROOT,
    "knowledge/nodes/alpha/node.md": ALPHA,
    "knowledge/nodes/alpha/beta/node.md": BETA,
    "knowledge/nodes/gamma/node.md": GAMMA,
    "knowledge/skills/review/node.md": SKILL,
}


def git(folder: Path, *arguments: str) -> str:
    return subprocess.run(  # noqa: S603
        [
            GIT,
            "-C",
            str(folder),
            "-c",
            "user.name=Test",
            "-c",
            "user.email=test@example.com",
            *arguments,
        ],
        capture_output=True,
        check=True,
        text=True,
    ).stdout


def write_tree(folder: Path, tree: dict[str, str] | None = None) -> None:
    def no_branch_files(path: str, names: list[str]) -> list[str]:
        return [name for name in names if Path(path).name == "branches" and name != ".gitkeep"]

    shutil.copytree(
        REPO / "knowledge/governance/language",
        folder / "knowledge/governance/language",
        ignore=no_branch_files,
    )
    for relative, text in (TREE if tree is None else tree).items():
        path = folder / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(text.encode("utf-8"))


def commit(folder: Path, message: str = "a commit") -> None:
    git(folder, "add", "-A")
    git(folder, "commit", "-qm", message, "--no-verify", "--allow-empty")


def make_repository(folder: Path, tree: dict[str, str] | None = None) -> Path:
    write_tree(folder, tree)
    (folder / ".gitignore").write_text("build/\n", encoding="utf-8")
    git(folder, "init", "-q", "--template=", "--initial-branch=main")
    commit(folder, "the tree")
    return folder


@pytest.fixture
def repository(tmp_path: Path) -> Path:
    return make_repository(tmp_path)


def source_bytes(folder: Path) -> dict[str, bytes]:
    return {
        path.relative_to(folder).as_posix(): path.read_bytes()
        for root in ("knowledge", "skills")
        for path in (folder / root).rglob("*")
        if path.is_file()
    }


def status_after_line(text: str, marker: str) -> str:
    lines = text.split("\n")
    start = next(index for index, line in enumerate(lines) if marker in line)
    found = next(line for line in lines[start:] if "status:" in line)
    return found.split("status:")[1].strip()


def read(folder: Path, relative: str) -> str:
    return (folder / relative).read_text(encoding="utf-8")


def changed_lines(before: bytes, after: bytes) -> list[tuple[bytes, bytes]]:
    old = before.split(b"\n")
    new = after.split(b"\n")
    assert len(old) == len(new)
    return [(a, b) for a, b in zip(old, new, strict=True) if a != b]


def codes(report_problems: list[object]) -> list[str]:
    return [getattr(problem, "code", "") for problem in report_problems]


def test_a_named_directive_changes_one_word_on_one_line(repository: Path) -> None:
    before = (repository / "knowledge/nodes/alpha/node.md").read_bytes()
    report = accept_entities(repository, ["keep"])
    assert report.problems == []
    assert [entity.label for entity in report.accepted] == ["directive keep"]
    after = (repository / "knowledge/nodes/alpha/node.md").read_bytes()
    assert changed_lines(before, after) == [(b"  - status: proposed", b"  - status: accepted")]
    assert status_after_line(after.decode(), "^wait") == "proposed"


def test_only_the_named_file_changes(repository: Path) -> None:
    before = source_bytes(repository)
    assert accept_entities(repository, ["keep"]).problems == []
    after = source_bytes(repository)
    assert {name for name in before if before[name] != after[name]} == {
        "knowledge/nodes/alpha/node.md"
    }


def test_a_named_node_does_not_cover_its_directives(repository: Path) -> None:
    before = (repository / "knowledge/nodes/alpha/node.md").read_bytes()
    report = accept_entities(repository, ["alpha"])
    assert [entity.label for entity in report.accepted] == ["node alpha"]
    after = (repository / "knowledge/nodes/alpha/node.md").read_bytes()
    assert changed_lines(before, after) == [(b"status: proposed", b"status: accepted")]


def test_an_exception_has_a_name_with_a_colon(repository: Path) -> None:
    before = (repository / "knowledge/nodes/alpha/beta/node.md").read_bytes()
    report = accept_entities(repository, ["beta:wait"])
    assert [entity.label for entity in report.accepted] == ["exception beta wait"]
    after = (repository / "knowledge/nodes/alpha/beta/node.md").read_bytes()
    assert changed_lines(before, after) == [(b"    status: proposed", b"    status: accepted")]


def test_a_subtree_covers_the_branch_and_nothing_else(repository: Path) -> None:
    report = accept_entities(repository, [], ["alpha"])
    assert report.problems == []
    assert sorted(entity.label for entity in report.accepted) == [
        "directive bound",
        "directive keep",
        "directive wait",
        "exception beta wait",
        "node alpha",
        "node beta",
    ]
    assert "status: proposed" in read(repository, "knowledge/nodes/gamma/node.md")
    assert "status: proposed" in read(repository, "knowledge/skills/review/node.md")
    assert "status: proposed" in read(repository, "knowledge/node.md")


def test_a_subtree_of_a_leaf_covers_its_own_directives(repository: Path) -> None:
    report = accept_entities(repository, [], ["beta"])
    assert sorted(entity.label for entity in report.accepted) == [
        "directive bound",
        "exception beta wait",
        "node beta",
    ]
    assert "node alpha" not in [entity.label for entity in report.accepted]


def test_a_subtree_of_the_root_covers_each_entity(repository: Path) -> None:
    report = accept_entities(repository, [], ["root"])
    assert report.problems == []
    assert len(report.accepted) == len(TREE) + 5
    pending, problems = pending_entities(repository)
    assert problems == []
    assert pending == []


def test_a_name_and_a_subtree_combine_with_no_repeat(repository: Path) -> None:
    report = accept_entities(repository, ["keep", "gamma"], ["alpha"])
    labels = [entity.label for entity in report.accepted]
    assert len(labels) == len(set(labels))
    assert "directive keep" in labels
    assert "node gamma" in labels


def test_the_result_passes_the_change_rules(repository: Path) -> None:
    assert accept_entities(repository, [], ["root"]).problems == []
    assert check_governance(repository).problems == []
    items, problems = check_tree(repository)
    assert problems == []
    assert items


def test_the_next_steps_reach_a_commit(repository: Path) -> None:
    assert generate_runtime(repository).problems == []
    commit(repository, "the runtime files")
    assert accept_entities(repository, ["keep", "wait", "alpha"]).problems == []
    report = generate_runtime(repository)
    assert report.problems == []
    assert ".claude/references/alpha.md" in {path.as_posix() for path in report.written}
    assert "Run the check." in read(repository, ".claude/references/alpha.md")
    git(repository, "add", "-A")
    verified = generate_runtime(repository, verify=True)
    assert verified.problems == []
    commit(repository, "accept")
    assert check_governance(repository).problems == []
    assert "accepted" in git(repository, "show", "HEAD:knowledge/nodes/alpha/node.md")


def test_an_accepted_node_changes_no_generated_file(repository: Path) -> None:
    assert generate_runtime(repository).problems == []
    commit(repository)
    assert accept_entities(repository, ["gamma", "alpha", "root"]).problems == []
    report = generate_runtime(repository)
    assert report.problems == []
    assert report.written == ()
    assert report.removed == ()


def test_the_command_writes_no_commit_and_no_runtime_file(repository: Path) -> None:
    head = git(repository, "rev-parse", "HEAD")
    assert accept_entities(repository, ["keep"]).problems == []
    assert git(repository, "rev-parse", "HEAD") == head
    assert git(repository, "diff", "--cached", "--name-only") == ""
    status = git(repository, "status", "--porcelain", "--untracked-files=all")
    assert status.splitlines() == [" M knowledge/nodes/alpha/node.md"]


def test_a_dry_run_lists_and_writes_nothing(repository: Path) -> None:
    before = source_bytes(repository)
    report = accept_entities(repository, [], ["alpha"], dry_run=True)
    assert report.problems == []
    assert len(report.accepted) == len(("alpha", "beta", "keep", "wait", "bound", "exception"))
    assert source_bytes(repository) == before


def test_a_dry_run_also_reports_a_problem(repository: Path) -> None:
    report = accept_entities(repository, ["nothing"], dry_run=True)
    assert codes(list(report.problems)) == ["unknown-id"]


def test_an_unknown_name_writes_nothing(repository: Path) -> None:
    before = source_bytes(repository)
    report = accept_entities(repository, ["keep", "nothing"])
    assert codes(list(report.problems)) == ["unknown-id"]
    assert "nothing" in report.problems[0].message
    assert report.accepted == ()
    assert source_bytes(repository) == before


def test_an_unknown_subtree_writes_nothing(repository: Path) -> None:
    before = source_bytes(repository)
    report = accept_entities(repository, ["keep"], ["nothing"])
    assert codes(list(report.problems)) == ["unknown-id"]
    assert source_bytes(repository) == before


def test_a_directive_is_not_a_subtree(repository: Path) -> None:
    report = accept_entities(repository, [], ["keep"])
    assert codes(list(report.problems)) == ["unknown-id"]


def test_an_unknown_exception_name_fails(repository: Path) -> None:
    assert codes(list(accept_entities(repository, ["beta:keep"]).problems)) == ["unknown-id"]
    assert codes(list(accept_entities(repository, ["wait:beta"]).problems)) == ["unknown-id"]


def set_status(folder: Path, relative: str, marker: str, status: str) -> None:
    path = folder / relative
    lines = path.read_text(encoding="utf-8").split("\n")
    start = next(index for index, line in enumerate(lines) if marker in line)
    index = next(i for i in range(start, len(lines)) if "status:" in lines[i])
    lines[index] = lines[index].split("status:")[0] + f"status: {status}"
    path.write_text("\n".join(lines), encoding="utf-8")


def test_a_deprecated_name_fails(repository: Path) -> None:
    set_status(repository, "knowledge/nodes/alpha/node.md", "^keep", "deprecated")
    commit(repository)
    before = source_bytes(repository)
    report = accept_entities(repository, ["keep"])
    assert codes(list(report.problems)) == ["not-proposed"]
    assert "deprecated" in report.problems[0].message
    assert report.problems[0].path == repository / "knowledge/nodes/alpha/node.md"
    assert source_bytes(repository) == before


def test_a_status_deprecated_at_head_fails(repository: Path) -> None:
    set_status(repository, "knowledge/nodes/alpha/node.md", "^keep", "deprecated")
    commit(repository)
    set_status(repository, "knowledge/nodes/alpha/node.md", "^keep", "proposed")
    report = accept_entities(repository, ["keep"])
    assert codes(list(report.problems)) == ["not-proposed"]
    assert "HEAD" in report.problems[0].message
    assert (
        status_after_line(read(repository, "knowledge/nodes/alpha/node.md"), "^keep") == "proposed"
    )


def test_a_subtree_skips_what_is_not_proposed(repository: Path) -> None:
    set_status(repository, "knowledge/nodes/alpha/node.md", "^keep", "deprecated")
    set_status(repository, "knowledge/nodes/alpha/beta/node.md", "^bound", "deprecated")
    commit(repository)
    assert accept_entities(repository, ["wait"]).problems == []
    commit(repository)
    report = accept_entities(repository, [], ["alpha"])
    assert report.problems == []
    assert report.not_proposed == len(("keep", "bound", "wait"))
    assert sorted(entity.label for entity in report.accepted) == [
        "exception beta wait",
        "node alpha",
        "node beta",
    ]
    assert (
        status_after_line(read(repository, "knowledge/nodes/alpha/node.md"), "^keep")
        == "deprecated"
    )


def test_an_accepted_name_counts_and_writes_nothing(repository: Path) -> None:
    assert accept_entities(repository, ["keep"]).problems == []
    commit(repository)
    before = source_bytes(repository)
    report = accept_entities(repository, ["keep"])
    assert report.problems == []
    assert report.accepted == ()
    assert report.not_proposed == 1
    assert source_bytes(repository) == before


def test_an_entity_that_head_does_not_hold_fails(repository: Path) -> None:
    path = repository / "knowledge/nodes/alpha/node.md"
    path.write_text(
        path.read_text(encoding="utf-8") + "- Run the new check. ^brand-new\n  - scope: node\n"
        "  - basis: judgment\n  - status: proposed\n"
        "  - origin: template\n",
        encoding="utf-8",
    )
    before = source_bytes(repository)
    report = accept_entities(repository, ["brand-new"])
    assert codes(list(report.problems)) == ["uncommitted"]
    assert "HEAD does not hold directive brand-new" in report.problems[0].message
    assert "uv run densho accept" in report.problems[0].message
    assert source_bytes(repository) == before


def test_an_uncommitted_template_pull_stops_the_run(repository: Path) -> None:
    history = repository / "knowledge/.densho/history.jsonl"
    history.parent.mkdir(parents=True, exist_ok=True)
    history.write_text("", encoding="utf-8")
    commit(repository, "the install")
    history.write_text('{"a pull": 1}\n', encoding="utf-8")
    before = source_bytes(repository)
    report = accept_entities(repository, ["keep"])
    assert codes(list(report.problems)) == ["uncommitted"]
    assert "Commit the pull" in report.problems[0].message
    assert source_bytes(repository) == before


def test_a_new_entity_in_a_subtree_stops_the_whole_run(repository: Path) -> None:
    path = repository / "knowledge/nodes/alpha/node.md"
    path.write_text(
        path.read_text(encoding="utf-8") + "- Run the new check. ^brand-new\n  - scope: node\n"
        "  - basis: judgment\n  - status: proposed\n"
        "  - origin: template\n",
        encoding="utf-8",
    )
    before = source_bytes(repository)
    report = accept_entities(repository, [], ["alpha"])
    assert codes(list(report.problems)) == ["uncommitted"]
    assert report.accepted == ()
    assert source_bytes(repository) == before


@pytest.mark.parametrize(
    ("name", "old", "new"),
    [
        ("keep", "Run the check. ^keep", "Run the changed check. ^keep"),
        ("alpha", "The meaning of alpha.", "The changed meaning of alpha."),
        ("beta:wait", "A reason for beta.", "A changed reason for beta."),
    ],
)
def test_a_change_to_a_reviewed_field_stays_apart(
    repository: Path, name: str, old: str, new: str
) -> None:
    for relative in ("knowledge/nodes/alpha/node.md", "knowledge/nodes/alpha/beta/node.md"):
        path = repository / relative
        path.write_text(path.read_text(encoding="utf-8").replace(old, new), encoding="utf-8")
    before = source_bytes(repository)
    report = accept_entities(repository, [name])
    assert codes(list(report.problems)) == ["uncommitted"]
    assert "differs from HEAD" in report.problems[0].message
    assert source_bytes(repository) == before


def test_a_change_to_a_field_with_no_review_passes(repository: Path) -> None:
    path = repository / "knowledge/nodes/alpha/node.md"
    path.write_text(
        path.read_text(encoding="utf-8").replace("title: Alpha", "title: New alpha"),
        encoding="utf-8",
    )
    report = accept_entities(repository, ["alpha"])
    assert report.problems == []
    assert check_governance(repository).problems == []


def test_a_folder_with_no_git_fails(tmp_path: Path) -> None:
    write_tree(tmp_path)
    before = source_bytes(tmp_path)
    report = accept_entities(tmp_path, ["keep"])
    assert codes(list(report.problems)) == ["no-history"]
    assert "not a git repository" in report.problems[0].message
    assert source_bytes(tmp_path) == before


def test_a_repository_with_no_commit_fails(tmp_path: Path) -> None:
    write_tree(tmp_path)
    git(tmp_path, "init", "-q", "--template=")
    report = accept_entities(tmp_path, ["keep"])
    assert codes(list(report.problems)) == ["no-history"]
    assert "no commit" in report.problems[0].message


def test_a_merge_in_progress_fails(repository: Path) -> None:
    head = git(repository, "rev-parse", "HEAD").strip()
    (repository / ".git/MERGE_HEAD").write_text(f"{head}\n", encoding="utf-8")
    before = source_bytes(repository)
    report = accept_entities(repository, ["keep"])
    assert codes(list(report.problems)) == ["no-history"]
    assert "merge" in report.problems[0].message
    assert source_bytes(repository) == before


def test_nothing_to_do_needs_no_history(tmp_path: Path) -> None:
    write_tree(
        tmp_path, {**TREE, "knowledge/nodes/gamma/node.md": GAMMA.replace("proposed", "accepted")}
    )
    report = accept_entities(tmp_path, ["gamma"])
    assert report.problems == []
    assert report.not_proposed == 1


def test_a_tree_with_a_problem_stops_the_command(repository: Path) -> None:
    (repository / "knowledge/nodes/gamma/node.md").write_text("not a node\n", encoding="utf-8")
    before = source_bytes(repository)
    report = accept_entities(repository, ["keep"])
    assert "front-matter" in codes(list(report.problems))
    assert source_bytes(repository) == before


def test_a_language_problem_stops_the_command(repository: Path) -> None:
    path = repository / "knowledge/nodes/gamma/node.md"
    path.write_text(
        GAMMA + "\n## Directives\n\n- This sentence has no verb first. ^bad-rule\n"
        "  - scope: node\n  - basis: judgment\n  - status: proposed\n  - origin: template\n",
        encoding="utf-8",
    )
    before = source_bytes(repository)
    report = accept_entities(repository, ["keep"])
    assert "opening" in codes(list(report.problems))
    assert source_bytes(repository) == before


def tree_with(path: str, old: str, new: str) -> dict[str, str]:
    assert old in TREE[path]
    return {**TREE, path: TREE[path].replace(old, new)}


def test_quoted_status_keeps_its_quotes(tmp_path: Path) -> None:
    tree = tree_with("knowledge/nodes/gamma/node.md", "status: proposed", 'status: "proposed"')
    make_repository(tmp_path, tree)
    assert accept_entities(tmp_path, ["gamma"]).problems == []
    assert 'status: "accepted"' in read(tmp_path, "knowledge/nodes/gamma/node.md")


def test_a_status_in_backticks_keeps_its_backticks(tmp_path: Path) -> None:
    tree = tree_with(
        "knowledge/nodes/alpha/node.md",
        "^keep\n  - scope: subtree\n  - basis: judgment\n  - status: proposed",
        "^keep\n  - scope: subtree\n  - basis: judgment\n  - status: `proposed`",
    )
    make_repository(tmp_path, tree)
    report = accept_entities(tmp_path, ["keep"])
    assert report.problems == []
    assert "- status: `accepted`" in read(tmp_path, "knowledge/nodes/alpha/node.md")


def test_a_comment_on_the_status_line_stays(tmp_path: Path) -> None:
    tree = tree_with(
        "knowledge/nodes/gamma/node.md", "status: proposed", "status: proposed  # a note"
    )
    make_repository(tmp_path, tree)
    assert accept_entities(tmp_path, ["gamma"]).problems == []
    assert "status: accepted  # a note" in read(tmp_path, "knowledge/nodes/gamma/node.md")


@pytest.mark.parametrize(("name", "ending"), [("crlf", b"\r\n"), ("cr", b"\r"), ("lf", b"\n")])
def test_each_line_ending_stays(tmp_path: Path, name: str, ending: bytes) -> None:
    make_repository(tmp_path)
    path = tmp_path / "knowledge/nodes/gamma/node.md"
    path.write_bytes(GAMMA.encode().replace(b"\n", ending))
    commit(tmp_path, name)
    before = path.read_bytes()
    assert accept_entities(tmp_path, ["gamma"]).problems == []
    assert path.read_bytes() == before.replace(b"status: proposed", b"status: accepted")


def test_a_file_with_no_final_line_ending_stays_that_way(tmp_path: Path) -> None:
    make_repository(tmp_path)
    path = tmp_path / "knowledge/nodes/gamma/node.md"
    path.write_bytes(GAMMA.encode().rstrip(b"\n"))
    commit(tmp_path)
    before = path.read_bytes()
    assert accept_entities(tmp_path, ["gamma"]).problems == []
    assert path.read_bytes() == before.replace(b"status: proposed", b"status: accepted")


def test_trailing_space_and_unicode_stay(tmp_path: Path) -> None:
    tree = tree_with(
        "knowledge/nodes/gamma/node.md", "The meaning of gamma.", "The méaning of gamma.  "
    )
    make_repository(tmp_path, tree)
    path = tmp_path / "knowledge/nodes/gamma/node.md"
    before = path.read_bytes()
    assert accept_entities(tmp_path, ["gamma"]).problems == []
    assert path.read_bytes() == before.replace(b"status: proposed", b"status: accepted")


def test_the_file_mode_stays(repository: Path) -> None:
    path = repository / "knowledge/nodes/gamma/node.md"
    path.chmod(GROUP_READABLE)
    assert accept_entities(repository, ["gamma"]).problems == []
    assert path.stat().st_mode & 0o777 == GROUP_READABLE


BLOCK_EXCEPTIONS = (
    "exceptions:\n  - directive: wait\n    reason: A reason for beta.\n    status: proposed\n"
)
ONE_LINE_EXCEPTIONS = (
    "exceptions: [{directive: wait, reason: First reason., status: proposed}, "
    "{directive: keep, reason: Second reason., status: proposed}]\n"
)


def test_a_status_on_a_shared_line_that_the_edit_misses_writes_nothing(tmp_path: Path) -> None:
    make_repository(
        tmp_path,
        tree_with("knowledge/nodes/alpha/beta/node.md", BLOCK_EXCEPTIONS, ONE_LINE_EXCEPTIONS),
    )
    before = source_bytes(tmp_path)
    report = accept_entities(tmp_path, ["beta:keep"])
    assert "status-line" in codes(list(report.problems))
    assert source_bytes(tmp_path) == before


def test_two_exceptions_on_one_line_accept_together(tmp_path: Path) -> None:
    make_repository(
        tmp_path,
        tree_with("knowledge/nodes/alpha/beta/node.md", BLOCK_EXCEPTIONS, ONE_LINE_EXCEPTIONS),
    )
    report = accept_entities(tmp_path, ["beta:wait", "beta:keep"])
    assert report.problems == []
    text = read(tmp_path, "knowledge/nodes/alpha/beta/node.md")
    assert text.count("status: accepted") == len(("wait", "keep"))


def test_the_first_of_two_exceptions_on_one_line_passes(tmp_path: Path) -> None:
    make_repository(
        tmp_path,
        tree_with("knowledge/nodes/alpha/beta/node.md", BLOCK_EXCEPTIONS, ONE_LINE_EXCEPTIONS),
    )
    report = accept_entities(tmp_path, ["beta:wait"])
    assert report.problems == []
    assert "First reason., status: accepted}" in read(
        tmp_path, "knowledge/nodes/alpha/beta/node.md"
    )
    assert "Second reason., status: proposed}" in read(
        tmp_path, "knowledge/nodes/alpha/beta/node.md"
    )


def test_a_decoy_in_a_reason_writes_nothing(tmp_path: Path) -> None:
    decoy = 'exceptions: [{directive: wait, reason: "status: proposed", status: proposed}]\n'
    make_repository(
        tmp_path, tree_with("knowledge/nodes/alpha/beta/node.md", BLOCK_EXCEPTIONS, decoy)
    )
    before = source_bytes(tmp_path)
    report = accept_entities(tmp_path, ["beta:wait"])
    assert codes(list(report.problems)) == ["status-line"]
    assert source_bytes(tmp_path) == before


def test_a_decoy_in_a_flow_title_writes_nothing(tmp_path: Path) -> None:
    source = (
        '---\n{id: gamma, kind: "densho:Domain", title: "status: proposed", status: proposed, '
        "origin: template, knowledge_type: domain}\n---\n\n## Definition\n\nThe meaning.\n"
    )
    make_repository(tmp_path, {**TREE, "knowledge/nodes/gamma/node.md": source})
    before = source_bytes(tmp_path)
    report = accept_entities(tmp_path, ["gamma"])
    assert codes(list(report.problems)) == ["status-line"]
    assert source_bytes(tmp_path) == before


def test_a_status_on_the_next_line_writes_nothing(tmp_path: Path) -> None:
    tree = tree_with("knowledge/nodes/gamma/node.md", "status: proposed", "status:\n  proposed")
    make_repository(tmp_path, tree)
    before = source_bytes(tmp_path)
    report = accept_entities(tmp_path, ["gamma"])
    assert codes(list(report.problems)) == ["status-line"]
    assert "gamma" in report.problems[0].message
    assert source_bytes(tmp_path) == before


def test_a_partial_acceptance_that_makes_a_conflict_writes_nothing(tmp_path: Path) -> None:
    tree = {
        **TREE,
        "knowledge/nodes/alpha/node.md": ALPHA.replace(
            "- Run the check. ^keep\n  - scope: subtree\n"
            "  - basis: judgment\n  - status: proposed\n"
            "  - origin: template\n",
            "- Use tabs in each file. ^use-tabs\n  - scope: subtree\n"
            "  - basis: judgment\n  - status: proposed\n"
            "  - origin: template\n  - conflicts_with: use-spaces\n",
        ),
        "knowledge/nodes/alpha/beta/node.md": BETA.replace(
            "exceptions:\n  - directive: wait\n    reason: A reason for beta.\n"
            "    status: proposed\n",
            "exceptions:\n  - directive: use-tabs\n    reason: A reason for beta.\n"
            "    status: proposed\n",
        ).replace(
            "- Run the third check. ^bound\n  - scope: node\n  - basis: judgment\n",
            "- Use spaces in each file. ^use-spaces\n  - scope: subtree\n  - basis: judgment\n",
        ),
    }
    make_repository(tmp_path, tree)
    assert accept_entities(tmp_path, [], ["root"], dry_run=True).problems == []
    before = source_bytes(tmp_path)
    report = accept_entities(tmp_path, ["use-tabs", "use-spaces"])
    assert "conflict" in codes(list(report.problems))
    assert source_bytes(tmp_path) == before
    assert accept_entities(tmp_path, ["use-tabs", "use-spaces", "beta:use-tabs"]).problems == []


def test_an_acceptance_that_breaks_the_size_limit_writes_nothing(
    repository: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    assert generate_runtime(repository).problems == []
    commit(repository)
    pages = (repository / ".claude/references").glob("*.md")
    limit = max(len(path.read_text(encoding="utf-8")) for path in pages) + 1
    monkeypatch.setattr(claude_code, "ON_DEMAND_CHARACTERS", limit)
    assert generate_runtime(repository).problems == []
    before = source_bytes(repository)
    report = accept_entities(repository, ["keep"])
    assert set(codes(list(report.problems))) == {"size"}
    assert report.accepted == ()
    assert source_bytes(repository) == before


def test_a_write_failure_reports_only_what_changed(tmp_path: Path) -> None:
    make_repository(tmp_path)
    blocked = tmp_path / "knowledge/nodes/gamma/node.md"
    blocked.chmod(0o444)
    try:
        report = accept_entities(tmp_path, ["keep", "gamma"])
    finally:
        blocked.chmod(0o644)
    assert codes(list(report.problems)) == ["write"]
    assert report.problems[0].path == blocked
    assert [entity.label for entity in report.accepted] == ["directive keep"]
    assert "status: proposed" in blocked.read_text(encoding="utf-8")


def test_a_write_failure_stops_at_the_first_file(tmp_path: Path) -> None:
    make_repository(tmp_path)
    blocked = tmp_path / "knowledge/nodes/alpha/node.md"
    blocked.chmod(0o444)
    try:
        report = accept_entities(tmp_path, ["keep", "gamma"])
    finally:
        blocked.chmod(0o644)
    assert codes(list(report.problems)) == ["write"]
    assert report.accepted == ()
    assert "status: proposed" in read(tmp_path, "knowledge/nodes/gamma/node.md")


def test_an_unreadable_file_reports_a_problem(
    repository: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    real = Path.read_bytes
    target = repository / "knowledge/nodes/gamma/node.md"
    seen = {"calls": 0}

    def fail_late(path: Path) -> bytes:
        if path == target:
            seen["calls"] += 1
            if seen["calls"] > 1:
                message = "blocked"
                raise OSError(13, message)
        return real(path)

    assert accept_entities(repository, ["gamma"], dry_run=True).problems == []
    seen["calls"] = 1
    monkeypatch.setattr(Path, "read_bytes", fail_late)
    report = accept_entities(repository, ["gamma"])
    assert codes(list(report.problems)) == ["write"]
    assert report.accepted == ()


def test_the_command_prefix_follows_the_wrapper(tmp_path: Path) -> None:
    assert command_prefix(tmp_path) == "uv run densho"
    (tmp_path / "knowledge/.densho").mkdir(parents=True, exist_ok=True)
    assert command_prefix(tmp_path) == "uv run densho"
    (tmp_path / "knowledge/.densho/densho").write_text("#!/bin/sh\n", encoding="utf-8")
    assert command_prefix(tmp_path) == "knowledge/.densho/densho"


def test_a_project_message_names_the_project_command(repository: Path) -> None:
    (repository / "knowledge/.densho").mkdir(parents=True, exist_ok=True)
    (repository / "knowledge/.densho/densho").write_text("#!/bin/sh\n", encoding="utf-8")
    path = repository / "knowledge/nodes/alpha/node.md"
    path.write_text(
        path.read_text(encoding="utf-8") + "- Run the new check. ^brand-new\n  - scope: node\n"
        "  - basis: judgment\n  - status: proposed\n"
        "  - origin: template\n",
        encoding="utf-8",
    )
    report = accept_entities(repository, ["brand-new"])
    assert "knowledge/.densho/densho accept" in report.problems[0].message


def test_the_cli_names_each_step_after_a_write(repository: Path) -> None:
    result = RUNNER.invoke(app, ["accept", "keep", "--repository", str(repository)])
    assert result.exit_code == 0, result.output
    assert "directive keep is now accepted" in result.output
    assert "knowledge/nodes/alpha/node.md:" in result.output
    assert "This command wrote no commit." in result.output
    assert "uv run densho runtime" in result.output
    assert "1 entities accepted, 0 not proposed, 0 problems" in result.output


def test_the_cli_runs_a_dry_run(repository: Path) -> None:
    before = source_bytes(repository)
    result = RUNNER.invoke(
        app, ["accept", "--subtree", "beta", "--dry-run", "--repository", str(repository)]
    )
    assert result.exit_code == 0, result.output
    assert "node beta would be accepted" in result.output
    assert "exception beta wait would be accepted" in result.output
    assert "This command wrote no commit." not in result.output
    assert "3 entities to accept, 0 not proposed, 0 problems" in result.output
    assert source_bytes(repository) == before


def test_the_cli_takes_more_than_one_subtree(repository: Path) -> None:
    result = RUNNER.invoke(
        app,
        ["accept", "--subtree", "beta", "--subtree", "gamma", "--repository", str(repository)],
    )
    assert result.exit_code == 0, result.output
    assert "4 entities accepted" in result.output


def test_the_cli_needs_a_name(repository: Path) -> None:
    result = RUNNER.invoke(app, ["accept", "--repository", str(repository)])
    assert result.exit_code == USAGE_ERROR
    assert "Name an ID" in result.output


def test_the_cli_reports_a_problem_with_status_one(repository: Path) -> None:
    result = RUNNER.invoke(app, ["accept", "nothing", "--repository", str(repository)])
    assert result.exit_code == 1
    assert "unknown-id" in result.output
    assert "This command wrote no commit." not in result.output


def test_the_cli_prints_no_next_step_when_nothing_changed(repository: Path) -> None:
    assert accept_entities(repository, ["keep"]).problems == []
    commit(repository)
    result = RUNNER.invoke(app, ["accept", "keep", "--repository", str(repository)])
    assert result.exit_code == 0, result.output
    assert "This command wrote no commit." not in result.output
    assert "0 entities accepted, 1 not proposed, 0 problems" in result.output


def test_the_cli_runs_in_the_current_folder(
    repository: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(repository)
    result = RUNNER.invoke(app, ["accept", "keep"])
    assert result.exit_code == 0, result.output
    assert "status: accepted" in read(repository, "knowledge/nodes/alpha/node.md")


def test_the_cli_help_states_who_runs_it() -> None:
    result = RUNNER.invoke(app, ["accept", "--help"])
    assert "A person runs this command." in " ".join(result.output.split())


def entity(status: Status, line: int) -> Entity:
    return Entity(("node", "a"), status, None, {}, Path("a"), line)


def test_the_helper_changes_only_the_named_line() -> None:
    data = b"status: proposed\nstatus: proposed\n"
    result, missed = set_status_lines(data, [entity(Status.proposed, 2)], Status.accepted)
    assert result == b"status: proposed\nstatus: accepted\n"
    assert missed == []


def test_the_helper_reads_each_line_ending_as_the_parser_does() -> None:
    data = b"a\r\nb\rc\nstatus: proposed\r\n"
    result, missed = set_status_lines(data, [entity(Status.proposed, 4)], Status.accepted)
    assert result == b"a\r\nb\rc\nstatus: accepted\r\n"
    assert missed == []


def test_the_helper_reports_a_line_past_the_end() -> None:
    wrong = entity(Status.proposed, 9)
    result, missed = set_status_lines(b"status: proposed\n", [wrong], Status.accepted)
    assert result == b"status: proposed\n"
    assert missed == [wrong]


@pytest.mark.parametrize(
    "line",
    [
        b"status: accepted",
        b"my-status: proposed",
        b"substatus: proposed",
        b"status: proposed-later",
        b"status: proposedx",
    ],
)
def test_the_helper_leaves_another_word_alone(line: bytes) -> None:
    wrong = entity(Status.proposed, 1)
    result, missed = set_status_lines(line, [wrong], Status.accepted)
    assert result == line
    assert missed == [wrong]


@pytest.mark.parametrize(
    ("line", "expected"),
    [
        (b"status: proposed", b"status: accepted"),
        (b"status:proposed", b"status:accepted"),
        (b"status : proposed", b"status : accepted"),
        (b'status: "proposed"', b'status: "accepted"'),
        (b"status: 'proposed'", b"status: 'accepted'"),
        (b"- status: `proposed`", b"- status: `accepted`"),
    ],
)
def test_the_helper_keeps_each_form(line: bytes, expected: bytes) -> None:
    assert set_status_lines(line, [entity(Status.proposed, 1)], Status.accepted)[0] == expected


def reject(folder: Path, relative: str, marker: str) -> None:
    set_status(folder, relative, marker, "rejected")
    path = folder / relative
    lines = path.read_text(encoding="utf-8").split("\n")
    start = next(index for index, line in enumerate(lines) if marker in line)
    index = next(i for i in range(start, len(lines)) if "status: rejected" in lines[i])
    prefix = lines[index].split("status:")[0]
    lines.insert(index + 1, f"{prefix}rejection_reason: No need.")
    path.write_text("\n".join(lines), encoding="utf-8")


def test_a_rejected_name_fails(repository: Path) -> None:
    reject(repository, "knowledge/nodes/alpha/node.md", "^keep")
    commit(repository)
    before = source_bytes(repository)
    report = accept_entities(repository, ["keep"])
    assert codes(list(report.problems)) == ["not-proposed"]
    assert report.problems[0].message == (
        "directive keep is rejected. Commit it as proposed before you accept it."
    )
    assert source_bytes(repository) == before


def test_a_status_rejected_at_head_fails(repository: Path) -> None:
    reject(repository, "knowledge/nodes/alpha/node.md", "^keep")
    commit(repository)
    set_status(repository, "knowledge/nodes/alpha/node.md", "^keep", "proposed")
    report = accept_entities(repository, ["keep"])
    assert codes(list(report.problems)) == ["not-proposed"]
    assert report.problems[0].message == (
        "HEAD has directive keep as rejected. Commit it as proposed first."
    )
    commit(repository)
    assert accept_entities(repository, ["keep"]).problems == []


def test_a_subtree_skips_a_rejected_entity(repository: Path) -> None:
    reject(repository, "knowledge/nodes/alpha/node.md", "^keep")
    commit(repository)
    report = accept_entities(repository, [], ["alpha"])
    assert report.problems == []
    assert "directive keep" not in [entity.label for entity in report.accepted]
    assert status_after_line(read(repository, "knowledge/nodes/alpha/node.md"), "^keep") == (
        "rejected"
    )
