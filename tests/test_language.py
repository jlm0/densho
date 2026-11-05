# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportPrivateUsage=false
import hashlib
import json
import shutil
import subprocess
import sys
import textwrap
from dataclasses import replace
from pathlib import Path
from typing import get_args

import pytest

from knowledge_architecture.generated.metamodel import Skill
from knowledge_architecture.language import check_items, check_language
from knowledge_architecture.language.profile import (
    LISTING_ENTRY_CAP,
    CheckCode,
    LanguageProfile,
    Vocabulary,
    read_profile,
)
from knowledge_architecture.language.prose import read_prose
from knowledge_architecture.parser import ParsedNode, Problem, parse_source
from knowledge_architecture.vendor import ste_lint

REPO = Path(__file__).resolve().parents[1]
LANGUAGE = REPO / "governance/language"
VENDORED = REPO / "engine/knowledge_architecture/vendor"
VENDORED_DIGEST = "fff04bf85c1e8bd8dc69dcedc63a5d88ed513dfa24e505f9cb8318a4596c99cd"
HARNESS_ENTRY_CAP = 1536
LISTING_BUDGET = 8000
GOOD_DESCRIPTION = "Review a pull request. Use when a pull request changes code."


def load_profile() -> LanguageProfile:
    profile = read_profile(LANGUAGE)
    assert isinstance(profile, LanguageProfile), profile
    return profile


PROFILE = load_profile()


def node_source(
    node_id: str = "sample",
    *,
    directives: tuple[str, ...] = (),
    triggers: tuple[str, ...] = (),
    description: str | None = None,
    broader: tuple[str, ...] = (),
) -> str:
    kind = "ka:Skill" if description is not None else "ka:Concept" if broader else "ka:Domain"
    lines = [
        "---",
        f"id: {node_id}",
        f"kind: {kind}",
        "title: Sample",
        "status: accepted",
        "origin: template",
        "knowledge_type: domain",
    ]
    if broader:
        lines.append(f"broader: {json.dumps(list(broader))}")
    if description is not None:
        lines += [f"description: {json.dumps(description)}", "uses: [other]"]
    if triggers:
        lines.append("pointers:")
    for trigger in triggers:
        lines += ["  - kind: ka:TextPointer", "    target: other"]
        lines.append(f"    trigger: {json.dumps(trigger)}")
    lines.append("---")
    if description is None:
        lines += ["", "## Definition", "", "A sample."]
    if directives:
        lines += ["", "## Directives", ""]
    for index, text in enumerate(directives):
        lines += [f"- {text} ^{node_id}-rule-{index}", "  - scope: subtree"]
        lines += ["  - status: accepted", "  - origin: template"]
    return "\n".join(lines) + "\n"


def parsed(source: str, path: str = "node.md") -> ParsedNode:
    result = parse_source(source, Path(path))
    assert isinstance(result, ParsedNode), result
    return result


def problems_of(source: str, profile: LanguageProfile = PROFILE) -> list[Problem]:
    return check_items([parsed(source)], profile)[1]


def codes_of(source: str, profile: LanguageProfile = PROFILE) -> set[str]:
    return {problem.code for problem in problems_of(source, profile)}


def directive_codes(text: str, profile: LanguageProfile = PROFILE) -> set[str]:
    return codes_of(node_source(directives=(text,)), profile)


def trigger_codes(text: str, profile: LanguageProfile = PROFILE) -> set[str]:
    return codes_of(node_source(triggers=(text,)), profile)


def description_codes(text: str, profile: LanguageProfile = PROFILE) -> set[str]:
    return codes_of(node_source(description=text), profile)


def words(count: int) -> str:
    return " ".join(["test"] * count)


@pytest.mark.parametrize(
    "text",
    [
        "Write a failing test before you change behavior.",
        "Run `pytest` before you commit.",
        "Do not commit a secret.",
        "Do not push to `main` unless a reviewer asks.",
        "If a test fails, stop the release.",
        "If a test, a lint, or a build fails, stop the run.",
        "If a test fails, do not merge the branch.",
        "If a fixture is slow, prefer a small fixture.",
        "When the build fails, report the first error.",
        "In `tests/`, use a fixture for each database.",
        "For each public function, write a test.",
        "Prefer a small fixture over a large mock.",
        "Delete the temporary folder after the run.",
        "Before you merge a branch, run the tests.",
        "After a deploy, check the health endpoint.",
        "After a condition, put a comma before the directive.",
        "While a migration runs, block each write.",
        "Until the review passes, keep the branch open.",
        "Return an error when the input is empty.",
        "Reject a request that has no token.",
        "Test each route with a real database.",
        "Review each diff before you push.",
        "Set the timeout to `30` seconds.",
        "Stop the deploy if the health check fails.",
        "On each commit, run the hooks.",
        "During a release, block each merge.",
        "Across each package, use one logger.",
        "Under `src/`, keep each module small.",
        "Run `pytest` and `pyright`.",
        "Delete the file and the folder.",
        "Check the file and the folder for a change.",
        "Compare the old file and the new file.",
        "Put each command, path, and literal value in backticks.",
        "List the steps, the inputs, and the outputs.",
        "Keep tests fast and isolated.",
        "Run the suite once.",
        "When a build fails, run the suite once.",
        "Stop the release unless a reviewer approves it.",
        "Run the suite before a merge.",
        "Use the user's token.",
        "Copy each tests' fixture.",
        "Copy the user's tests' fixture.",
        "Run the suite and failed tests.",
        "Pass the token and the user ID to the client.",
        "Put the lock file and the manifest in one commit.",
        "Mock a network call when a test runs offline.",
        "Name each file in lower case, with hyphens.",
        "Format each file with `ruff`, not by hand.",
        "Use a fixture, not a mock.",
        "Review code, tests, and docs together.",
        "Fail the build on a lint error.",
        "If you edit a test and the fixture changes, run the suite.",
        "Stop the build when a test fails and a reviewer is away.",
        "Use **each** fixture.",
        "Use [each](https://example.com/a_b) fixture.",
    ],
)
def test_a_good_directive_passes(text: str) -> None:
    assert problems_of(node_source(directives=(text,))) == []


@pytest.mark.parametrize(
    ("text", "code"),
    [
        ("write a test.", "sentence"),
        ("Write a test", "sentence"),
        ("Write a test!", "sentence"),
        ("Write a test?", "sentence"),
        ("Write a test..", "sentence"),
        ("Write a test...", "sentence"),
        ("Write a test. Run the suite.", "sentence"),
        ("Write a test! Run the suite.", "sentence"),
        ("Write a test? Run the suite.", "sentence"),
        ("Tests pass.", "opening"),
        ("Writes a test.", "opening"),
        ("Don't push.", "opening"),
        ("The build fails.", "opening"),
        ("`pytest` runs.", "opening"),
        ("Unless a test fails, push the branch.", "opening"),
        ("Do not ever push.", "opening"),
        ("Do not.", "opening"),
        ("Do not `pytest`.", "opening"),
        ("If a test fails stop the release.", "opening"),
        ("In `tests/` use a fixture.", "opening"),
        ("If a test fails, the release stops.", "opening"),
        ("In `tests/`, a fixture is small.", "opening"),
        ("If a test fails, do not ever push.", "opening"),
        ("Test files pass.", "imperative"),
        ("Review comments stay open.", "imperative"),
        ("Review the diff and run the suite.", "second-directive"),
        ("Write and run a test.", "second-directive"),
        ("Use the fixture, then run the suite.", "second-directive"),
        ("Do not merge a branch and do not push it.", "second-directive"),
        ("Set the timeout, and run the suite.", "second-directive"),
        ("Keep the file and moves it.", "second-directive"),
        ("Run the suite and stopped the build.", "second-directive"),
        ("Run the suite, stop.", "second-directive"),
        ("Run the suite: stop the build.", "second-directive"),
        ("Start the server, wait for the port, and run the tests.", "second-directive"),
        ("If a test fails, test files pass.", "imperative"),
        ("Stop the run if the build fails when the suite runs.", "condition-count"),
        ("If the build fails, stop the run when the suite runs.", "condition-count"),
        ("Before a merge, run the suite when the build fails.", "condition-count"),
        ("Run the tests unless a file changes unless a build fails.", "unless-count"),
        ("Run the tests usually.", "prohibited"),
        ("Usually run the tests.", "prohibited"),
        ("Run the tests as needed.", "prohibited"),
        ("You should run the tests.", "prohibited"),
        ("Run the tests because they catch bugs.", "prohibited"),
        ("Run the tests so that a bug shows.", "prohibited"),
        ("Keep a test that utilizes a fixture.", "prohibited"),
        ("Keep a test that seems slow.", "prohibited"),
        ("Run pytest --verbose.", "literal"),
        ("Run the suite in src/app.", "literal"),
        ("Run the suite in C:\\app.", "literal"),
        ("Read node.md.", "literal"),
        ("Read foo_bar.", "literal"),
        ("Read foo\\_bar.", "literal"),
        ("Read fooBar.", "literal"),
        ("Call foo().", "literal"),
        ("Set the limit to 30.", "literal"),
        ('Set the name to "foo".', "literal"),
        ("Set the name to 'foo bar'.", "literal"),
        ("Set the name to \u201cfoo\u201d.", "literal"),
        ("Set the name to \u2018foo bar\u2019.", "literal"),
        ("Set KEY=value.", "literal"),
        ("Read $HOME.", "literal"),
        ("Use <b>this</b> fixture.", "literal"),
        ("Use ![a_b](x.png) in the docs.", "literal"),
        ("Run the suite; stop the build.", "ste"),
        ("Check the file and verify the output.", "ste"),
        ("Keep a robust fixture.", "ste"),
    ],
)
def test_a_bad_directive_fails(text: str, code: str) -> None:
    assert code in directive_codes(text)


def test_a_failed_form_does_not_hide_a_prohibited_term() -> None:
    assert directive_codes("You should run the tests.") == {"opening", "prohibited"}


def test_a_failed_form_skips_the_structure_checks() -> None:
    assert directive_codes("Run the tests and stop the build because a test fails") == {
        "sentence",
        "prohibited",
    }


def test_a_prohibited_term_prints_its_category() -> None:
    source = node_source(directives=("Run the tests usually.",))
    message = problems_of(source)[0].message
    assert message == "Remove 'usually'. The vocabulary lists it as: hedge."


def test_a_prohibited_term_prints_once() -> None:
    source = node_source(directives=("Run the tests usually and test usually.",))
    assert len([p for p in problems_of(source) if p.code == "prohibited"]) == 1


def test_a_prohibited_term_in_capitals_still_matches_its_inflected_forms() -> None:
    vocabulary = Vocabulary(
        approved_verbs=PROFILE.vocabulary.approved_verbs, prohibited={"term": ("Utilize",)}
    )
    profile = replace(PROFILE, vocabulary=vocabulary)
    assert "prohibited" in directive_codes("Keep a job that utilizes a file.", profile)


def test_a_lemma_counts_only_for_a_verb() -> None:
    vocabulary = Vocabulary(
        approved_verbs=PROFILE.vocabulary.approved_verbs, prohibited={"term": ("test",)}
    )
    profile = replace(PROFILE, vocabulary=vocabulary)
    assert "prohibited" not in directive_codes("Run the tests.", profile)
    assert "prohibited" in directive_codes("Keep a job that tests a file.", profile)


def test_a_literal_in_backticks_is_not_a_prohibited_term() -> None:
    assert directive_codes("Remove `should` from each rule.") == set()


@pytest.mark.parametrize("word", ["user's", "user\u2019s", "well-known"])
def test_an_apostrophe_or_a_hyphen_does_not_split_a_word(word: str) -> None:
    assert "word-count" not in directive_codes(f"Run {words(18)} {word}.")


def test_a_literal_message_drops_the_trailing_period() -> None:
    message = problems_of(node_source(directives=("Read node.md.",)))[0].message
    assert message == "Put 'node.md' in backticks. It reads as a command, a path, or a value."


@pytest.mark.parametrize(
    ("text", "message"),
    [
        ("Do not ever push.", "Follow Do not with a verb from the approved list."),
        (
            "Tests pass.",
            (
                "Start the rule with an approved verb, Do not, Prefer, a condition, or a scope. "
                "The vocabulary does not approve 'tests'."
            ),
        ),
        ("If a test fails stop the release.", "Put a comma after the condition or the scope."),
        (
            "If a test fails, the release stops.",
            "After the comma, start the directive with an approved verb, Do not, or Prefer.",
        ),
    ],
)
def test_an_opening_problem_says_what_to_change(text: str, message: str) -> None:
    assert [problem.message for problem in problems_of(node_source(directives=(text,)))] == [
        message
    ]


def test_each_code_span_counts_as_one_word() -> None:
    text = f"Run {words(18)} `a long command with words`."
    assert directive_codes(text) == set()


def test_the_word_limit_passes_at_the_limit_and_fails_above_it() -> None:
    assert "word-count" not in directive_codes(f"Run {words(19)}.")
    assert "word-count" in directive_codes(f"Run {words(20)}.")
    source = node_source(directives=(f"Run {words(20)}.",))
    assert any(
        problem.message == "The sentence has 21 words. The limit is 20."
        for problem in problems_of(source)
    )


def test_two_code_spans_with_no_space_count_as_two_words() -> None:
    text = f"Run {words(18)} `a`,`b`."
    assert "word-count" in directive_codes(text)


def test_a_word_limit_comes_from_the_grammar() -> None:
    grammar = PROFILE.grammar.model_copy(
        update={"directive": PROFILE.grammar.directive.model_copy(update={"max_words": 3})}
    )
    profile = replace(PROFILE, grammar=grammar)
    assert "word-count" not in directive_codes("Run the suite.", profile)
    assert "word-count" in directive_codes("Run the whole suite.", profile)


def test_the_unless_limit_comes_from_the_grammar() -> None:
    assert "unless-count" not in directive_codes("Run the suite unless a test fails.")
    grammar = PROFILE.grammar.model_copy(
        update={"directive": PROFILE.grammar.directive.model_copy(update={"max_unless": 0})}
    )
    profile = replace(PROFILE, grammar=grammar)
    assert "unless-count" in directive_codes("Run the suite unless a test fails.", profile)


def test_the_condition_limit_comes_from_the_grammar() -> None:
    text = "Run the suite when a test fails."
    assert "condition-count" not in directive_codes(text)
    grammar = PROFILE.grammar.model_copy(
        update={"directive": PROFILE.grammar.directive.model_copy(update={"max_conditions": 0})}
    )
    profile = replace(PROFILE, grammar=grammar)
    assert "condition-count" in directive_codes(text, profile)
    assert "condition-count" in directive_codes("After a merge, run the suite.", profile)


def test_a_scope_opening_is_not_a_condition() -> None:
    grammar = PROFILE.grammar.model_copy(
        update={"directive": PROFILE.grammar.directive.model_copy(update={"max_conditions": 0})}
    )
    profile = replace(PROFILE, grammar=grammar)
    assert "condition-count" not in directive_codes("In `tests/`, run the suite.", profile)


@pytest.mark.parametrize(
    "text",
    [
        "You edit a test file.",
        "You need the sample.",
        "The build fails.",
        "`pytest` fails.",
        "A test fails.",
        "Tests fail.",
        "A file is open.",
        "The agent has a failing test.",
        "The task needs a database migration.",
        "You read a node file.",
        "You set a flag.",
        "You are editing a test file.",
        "A file is changed.",
        "A pull request changes code.",
        "The user asks for a review.",
        "The diff touches `src/`.",
        "You open a file in `tests/`.",
        "A file changes.",
        "A test file changes.",
        "The build passes.",
        "The file breaks.",
        "The agent changes.",
        "Test files change.",
        "You hit a limit.",
    ],
)
def test_a_good_trigger_passes(text: str) -> None:
    assert problems_of(node_source(triggers=(text,))) == []


def test_a_noun_phrase_with_a_plural_head_passes_as_a_known_limit() -> None:
    assert trigger_codes("The test files.") == set()
    assert "trigger-form" in trigger_codes("Test files.")
    assert "trigger-form" in trigger_codes("The test file.")


@pytest.mark.parametrize(
    ("text", "code"),
    [
        ("Edit a test file.", "trigger-form"),
        ("When you edit a test file.", "trigger-form"),
        ("If a file changes.", "trigger-form"),
        ("You edited a test file.", "trigger-form"),
        ("You ran the tests.", "trigger-form"),
        ("You were editing a test file.", "trigger-form"),
        ("Editing a test file.", "trigger-form"),
        ("A test file.", "trigger-form"),
        ("Read this before you edit.", "trigger-form"),
        ("In `tests/` you edit a file.", "trigger-form"),
        ("You can edit a file.", "prohibited"),
        ("You usually edit a file.", "prohibited"),
        ("you edit a file.", "sentence"),
        ("You edit a test file", "sentence"),
        ("You edit a file. You run a test.", "sentence"),
        (f"You edit {words(19)}.", "word-count"),
        ("You edit a file when the build fails.", "condition-count"),
        ("You edit a file unless the build fails.", "condition-count"),
        ("You edit src/app.py.", "literal"),
        ("You edit a file; you run a test.", "ste"),
    ],
)
def test_a_bad_trigger_fails(text: str, code: str) -> None:
    assert code in trigger_codes(text)


def test_the_trigger_word_limit_passes_at_the_limit() -> None:
    assert "word-count" not in trigger_codes(f"You edit {words(18)}.")


def test_a_trigger_word_limit_comes_from_the_grammar() -> None:
    grammar = PROFILE.grammar.model_copy(
        update={"trigger": PROFILE.grammar.trigger.model_copy(update={"max_words": 2})}
    )
    profile = replace(PROFILE, grammar=grammar)
    assert "word-count" in trigger_codes("You edit a file.", profile)
    assert "word-count" not in trigger_codes("Tests fail.", profile)


@pytest.mark.parametrize(
    "text",
    [
        GOOD_DESCRIPTION,
        "Generate a release note. Use when a reviewer asks for a release.",
        "Migrate a project to this template. Use when a project has old rules.",
    ],
)
def test_a_good_description_passes(text: str) -> None:
    assert problems_of(node_source(description=text)) == []


@pytest.mark.parametrize(
    ("text", "code"),
    [
        ("Review a pull request.", "description-form"),
        ("Reviews a pull request. Use when a file changes.", "description-form"),
        ("Review a pull request. Run this when a file changes.", "description-form"),
        ("Review a file. Use it. Use when a file changes.", "description-form"),
        ("Do not review a file. Use when a file changes.", "description-form"),
        ("Test files pass. Use when a file changes.", "imperative"),
        ("Review a file. Use when review.", "trigger-form"),
        ("Review a file. Use when when a file changes.", "trigger-form"),
        ("Review a file. Use when a file changed.", "trigger-form"),
        ("Review a file. Use when you edit a file before you commit.", "condition-count"),
        ("Review a file. Use when you should review.", "prohibited"),
        ("Review a file in src/app. Use when a file changes.", "literal"),
        ("Review a file; stop. Use when a file changes.", "ste"),
        ("review a file. Use when a file changes.", "sentence"),
        ("Review a file! Use when a file changes.", "sentence"),
        ("Review a file. Use when a file changes", "sentence"),
        (f"Review {words(20)}. Use when a file changes.", "word-count"),
        (f"Review a file. Use when you edit {words(18)}.", "word-count"),
    ],
)
def test_a_bad_description_fails(text: str, code: str) -> None:
    assert code in description_codes(text)


def test_each_description_sentence_passes_at_the_word_limit() -> None:
    text = f"Review {words(19)}. Use when you edit {words(16)}."
    assert "word-count" not in description_codes(text)


def test_the_description_length_passes_at_the_limit_and_fails_above_it() -> None:
    limit = PROFILE.grammar.skill_description.max_characters
    template = "Run `{}`. Use when a pull request changes code."
    padding = "x" * (limit - len(template.format("")))
    at_limit = template.format(padding)
    above = template.format(padding + "x")
    assert len(at_limit) == limit
    assert problems_of(node_source(description=at_limit)) == []
    messages = [problem.message for problem in problems_of(node_source(description=above))]
    assert messages == [f"The description has {limit + 1} characters. The limit is {limit}."]


def test_the_description_limit_comes_from_the_grammar() -> None:
    limits = PROFILE.grammar.skill_description.model_copy(update={"max_characters": 10})
    grammar = PROFILE.grammar.model_copy(update={"skill_description": limits})
    assert "description-length" in description_codes(
        GOOD_DESCRIPTION, replace(PROFILE, grammar=grammar)
    )


def test_a_description_word_limit_comes_from_the_grammar() -> None:
    limits = PROFILE.grammar.skill_description.model_copy(update={"max_sentence_words": 2})
    grammar = PROFILE.grammar.model_copy(update={"skill_description": limits})
    assert "word-count" in description_codes(GOOD_DESCRIPTION, replace(PROFILE, grammar=grammar))


def test_the_listing_entry_cap_limits_the_grammar(tmp_path: Path) -> None:
    text = (LANGUAGE / "grammar.yaml").read_text(encoding="utf-8")
    grammar = tmp_path / "language/grammar.yaml"
    grammar.parent.mkdir()
    shutil.copy(LANGUAGE / "vocabulary.yaml", grammar.parent)
    grammar.write_text(
        text.replace("max_characters: 400", f"max_characters: {LISTING_ENTRY_CAP + 1}"),
        encoding="utf-8",
    )
    problems = read_profile(grammar.parent)
    assert isinstance(problems, list)
    assert problems[0].code == "language-profile"
    assert "skill_description.max_characters" in problems[0].message
    grammar.write_text(
        text.replace("max_characters: 400", f"max_characters: {LISTING_ENTRY_CAP}"),
        encoding="utf-8",
    )
    assert isinstance(read_profile(grammar.parent), LanguageProfile)


def test_the_listing_entry_cap_is_the_harness_cap() -> None:
    assert LISTING_ENTRY_CAP == HARNESS_ENTRY_CAP


def skill_tree(sizes: list[int]) -> list[ParsedNode]:
    items = []
    for index, size in enumerate(sizes):
        skill_id = f"skill-{index}"
        description = f"Review `{'x' * size}`. Use when a file changes."
        items.append(parsed(node_source(skill_id, description=description), f"{skill_id}.md"))
    return items


def listing_size(items: list[ParsedNode]) -> int:
    skills = [item.node for item in items if isinstance(item.node, Skill)]
    return sum(len(skill.id) + len(skill.description) for skill in skills)


def test_the_listing_budget_passes_at_the_budget_and_fails_above_it() -> None:
    items = skill_tree([100, 100])
    limits = PROFILE.grammar.skill_description.model_copy(
        update={"max_listing_characters": listing_size(items)}
    )
    grammar = PROFILE.grammar.model_copy(update={"skill_description": limits})
    profile = replace(PROFILE, grammar=grammar)
    assert check_items(items, profile)[1] == []
    limits = limits.model_copy(update={"max_listing_characters": listing_size(items) - 1})
    grammar = PROFILE.grammar.model_copy(update={"skill_description": limits})
    problems = check_items(items, replace(PROFILE, grammar=grammar))[1]
    assert [(problem.code, problem.path, problem.line) for problem in problems] == [
        ("listing-budget", Path("skill-1.md"), items[1].line_of(("description",)))
    ]
    budget = listing_size(items) - 1
    assert problems[0].message == (
        f"The skill listing reaches {budget + 1} characters here. The budget is {budget}."
    )


def test_the_listing_budget_counts_the_shipped_limit() -> None:
    assert PROFILE.grammar.skill_description.max_listing_characters == LISTING_BUDGET
    items = skill_tree([390] * 25)
    assert "listing-budget" in {problem.code for problem in check_items(items, PROFILE)[1]}


def test_a_knowledge_node_does_not_count_for_the_listing() -> None:
    limits = PROFILE.grammar.skill_description.model_copy(update={"max_listing_characters": 1})
    grammar = PROFILE.grammar.model_copy(update={"skill_description": limits})
    assert codes_of(node_source(), replace(PROFILE, grammar=grammar)) == set()


def test_a_repeated_rule_fails_at_the_second_location() -> None:
    first = parsed(node_source("first", directives=("Run the suite.",)), "a.md")
    second = parsed(node_source("second", directives=("Run the  **suite**.",)), "b.md")
    problems = check_items([first, second], PROFILE)[1]
    assert [(problem.path, problem.code) for problem in problems] == [
        (Path("b.md"), "duplicate-rule")
    ]
    line = first.line_of(("directives", 0, "text"))
    assert problems[0].message == f"This rule repeats the rule at a.md:{line}."


def test_a_repeated_rule_ignores_case_but_not_code() -> None:
    first = parsed(node_source("first", directives=("Run `a`.",)), "a.md")
    second = parsed(node_source("second", directives=("Run `b`.",)), "b.md")
    third = parsed(node_source("third", directives=("RUN `A`.",)), "c.md")
    assert check_items([first, second], PROFILE)[1] == []
    assert [p.code for p in check_items([first, third], PROFILE)[1]] == ["duplicate-rule"]


def test_a_repeated_trigger_is_not_a_repeated_rule() -> None:
    first = parsed(node_source("first", triggers=("You edit a file.",)), "a.md")
    second = parsed(node_source("second", triggers=("You edit a file.",)), "b.md")
    assert check_items([first, second], PROFILE)[1] == []


def test_a_problem_points_at_its_file_and_line() -> None:
    source = node_source(
        directives=("Run the suite.", "Tests pass."),
        triggers=("You edit a file.", "Edit a file."),
    )
    problems = problems_of(source)
    lines = source.splitlines()
    assert [(problem.path, problem.code) for problem in problems] == [
        (Path("node.md"), "trigger-form"),
        (Path("node.md"), "opening"),
    ]
    assert lines[problems[0].line - 1] == '    trigger: "Edit a file."'
    assert lines[problems[1].line - 1].startswith("- Tests pass.")


def test_a_description_problem_points_at_its_line() -> None:
    source = node_source(description="Review a file.")
    line = problems_of(source)[0].line
    assert source.splitlines()[line - 1].startswith("description:")


def test_problems_print_in_a_stable_order() -> None:
    first = parsed(node_source("first", directives=("Tests pass.",)), "b.md")
    second = parsed(node_source("second", directives=("Tests fail.",)), "a.md")
    problems = check_items([first, second], PROFILE)[1]
    assert [problem.path for problem in problems] == [Path("a.md"), Path("b.md")]


def test_the_count_includes_each_text() -> None:
    source = node_source(directives=("Run the suite.",), triggers=("You edit a file.",))
    assert check_items([parsed(source)], PROFILE)[0] == len(["directive", "trigger"])
    assert check_items([parsed(node_source(description=GOOD_DESCRIPTION))], PROFILE)[0] == 1


@pytest.mark.parametrize(
    "source",
    [
        node_source(directives=("x" * 3000 + ".",)),
        node_source(triggers=("x" * 3000 + ".",)),
        node_source(description="x" * 3000 + "."),
        node_source(directives=(", " * 2000 + ".",)),
    ],
    ids=["directive", "trigger", "description", "commas"],
)
def test_a_huge_text_fails_without_a_crash(source: str) -> None:
    assert "word-count" in codes_of(source)


def test_the_problems_print_in_line_order() -> None:
    bad = tuple(f"Tests pass {name}." for name in ("one", "two", "three", "four", "five", "six"))
    lines = [problem.line for problem in problems_of(node_source(directives=bad))]
    assert len(lines) == len(bad)
    assert lines == sorted(lines)


def test_a_huge_text_still_counts_as_a_text() -> None:
    source = node_source(directives=("x" * 3000 + ".",))
    assert check_items([parsed(source)], PROFILE)[0] == 1


def test_the_longest_allowed_text_reaches_the_form_checks() -> None:
    assert "word-count" not in directive_codes("x" * 1999 + ".")
    assert "word-count" in directive_codes("x" * 2000 + ".")
    message = "The text has 2001 characters. Shorten it."
    source = node_source(directives=("x" * 2000 + ".",))
    assert [problem.message for problem in problems_of(source)] == [message]


@pytest.mark.parametrize(
    "text",
    [
        "`a`",
        "`` ` ``.",
        "[](x)",
        "![](x)",
        "...",
        "\u00e9\u00e8.",
        "*",
        "\u2014 \u2014.",
        "<!x>",
        "`` `",
    ],
)
def test_odd_markdown_fails_without_a_crash(text: str) -> None:
    assert codes_of(node_source(triggers=(text,)))
    assert codes_of(node_source(description=text))
    if text != "*":
        assert codes_of(node_source(directives=(text,)))


def test_a_masked_text_hides_code_but_the_plain_text_keeps_it() -> None:
    assert read_prose("Run `a b` **now** [c](d) ![e](f) <g>.") == (
        "Run CODE now c e <g>.",
        "Run a b now c e <g>.",
    )


def write_tree(repository: Path, nodes: dict[str, str] | None = None) -> None:
    shutil.copytree(LANGUAGE, repository / "governance/language")
    for folder in ("knowledge", "skills"):
        (repository / folder).mkdir()
    for relative, source in (nodes or {}).items():
        path = repository / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(source, encoding="utf-8")


def test_an_empty_tree_passes(tmp_path: Path) -> None:
    write_tree(tmp_path)
    assert check_language(tmp_path) == (0, [])


def test_the_repository_language_files_are_valid() -> None:
    assert check_language(REPO)[1] == []


def test_a_tree_with_problems_reports_them(tmp_path: Path) -> None:
    write_tree(tmp_path, {"knowledge/a/node.md": node_source(directives=("Tests pass.",))})
    count, problems = check_language(tmp_path)
    assert count == 1
    assert [problem.code for problem in problems] == ["opening"]
    assert problems[0].path == tmp_path / "knowledge/a/node.md"


@pytest.mark.parametrize(
    "relative",
    ["skills/a/node.md", "governance/policies/a/node.md", "governance/language/a/node.md"],
)
def test_each_node_folder_counts(tmp_path: Path, relative: str) -> None:
    write_tree(tmp_path, {relative: node_source(directives=("Tests pass.",))})
    assert [problem.code for problem in check_language(tmp_path)[1]] == ["opening"]


def test_a_parse_problem_stops_the_language_checks(tmp_path: Path) -> None:
    write_tree(
        tmp_path,
        {
            "knowledge/a/node.md": "no front matter\n",
            "knowledge/b/node.md": node_source(directives=("Tests pass.",)),
        },
    )
    count, problems = check_language(tmp_path)
    assert count == 0
    assert [problem.code for problem in problems] == ["front-matter"]


def test_a_missing_node_folder_is_a_problem(tmp_path: Path) -> None:
    write_tree(tmp_path)
    (tmp_path / "skills").rmdir()
    assert [problem.code for problem in check_language(tmp_path)[1]] == ["folder"]


def test_a_missing_profile_is_a_problem(tmp_path: Path) -> None:
    (tmp_path / "knowledge").mkdir()
    (tmp_path / "skills").mkdir()
    count, problems = check_language(tmp_path)
    assert count == 0
    assert [(problem.path.name, problem.code) for problem in problems] == [
        ("grammar.yaml", "language-profile"),
        ("vocabulary.yaml", "language-profile"),
    ]


@pytest.mark.parametrize(
    ("name", "content", "line", "fragment"),
    [
        ("grammar.yaml", "", 1, "file: "),
        ("vocabulary.yaml", "- a\n", 1, "file: "),
        ("vocabulary.yaml", "a: [\n", 2, ""),
        ("vocabulary.yaml", "a: 1\na: 2\n", 2, ""),
        ("vocabulary.yaml", "extra: 1\n", 1, "extra: "),
        (
            "vocabulary.yaml",
            "approved_verbs: [run]\nprohibited:\n  x: [1]\n",
            3,
            "prohibited.x.0: ",
        ),
        ("vocabulary.yaml", "approved_verbs:\n  - run\n  - Run Fast\n", 3, "approved_verbs.1: "),
        ("vocabulary.yaml", "prohibited:\n  x:\n    - ok\n    - ' '\n", 4, "prohibited.x.1: "),
    ],
)
def test_a_bad_profile_file_is_a_problem(
    tmp_path: Path, name: str, content: str, line: int, fragment: str
) -> None:
    shutil.copytree(LANGUAGE, tmp_path / "language")
    (tmp_path / "language" / name).write_text(content, encoding="utf-8")
    problems = read_profile(tmp_path / "language")
    assert isinstance(problems, list)
    assert problems
    assert problems[0].path.name == name
    assert problems[0].code == "language-profile"
    assert problems[0].line == line
    assert fragment in problems[0].message
    assert "\n" not in problems[0].message


def test_a_profile_file_that_is_not_utf8_is_a_problem(tmp_path: Path) -> None:
    shutil.copytree(LANGUAGE, tmp_path / "language")
    (tmp_path / "language/vocabulary.yaml").write_bytes(b"\xff\xfe")
    problems = read_profile(tmp_path / "language")
    assert isinstance(problems, list)
    assert problems[0].message == "The file is not valid UTF-8."


def test_a_folder_in_place_of_a_profile_file_is_a_problem(tmp_path: Path) -> None:
    shutil.copytree(LANGUAGE, tmp_path / "language")
    (tmp_path / "language/vocabulary.yaml").unlink()
    (tmp_path / "language/vocabulary.yaml").mkdir()
    problems = read_profile(tmp_path / "language")
    assert isinstance(problems, list)
    assert problems[0].code == "language-profile"


def test_a_profile_value_that_yaml_cannot_read_is_a_problem(tmp_path: Path) -> None:
    shutil.copytree(LANGUAGE, tmp_path / "language")
    (tmp_path / "language/vocabulary.yaml").write_text("a: 2001-13-45\n", encoding="utf-8")
    problems = read_profile(tmp_path / "language")
    assert isinstance(problems, list)
    assert problems[0].code == "language-profile"
    assert problems[0].message.startswith("YAML cannot read a value: ")


@pytest.mark.parametrize(
    "rule",
    [
        "- text: Write a rule.\n",
        "- text: Write a rule.\n  checks: [unknown-code]\n",
        "- text: Write a rule.\n  extra: 1\n  review: true\n",
    ],
)
def test_a_bad_rule_is_a_problem(tmp_path: Path, rule: str) -> None:
    shutil.copytree(LANGUAGE, tmp_path / "language")
    path = tmp_path / "language/grammar.yaml"
    text = path.read_text(encoding="utf-8")
    addition = textwrap.indent(rule, "  ")
    path.write_text(
        text.replace("trigger_rules:\n", f"trigger_rules:\n{addition}"), encoding="utf-8"
    )
    problems = read_profile(tmp_path / "language")
    assert isinstance(problems, list)
    assert problems[0].code == "language-profile"


def test_a_rule_without_a_check_or_review_says_why(tmp_path: Path) -> None:
    shutil.copytree(LANGUAGE, tmp_path / "language")
    path = tmp_path / "language/grammar.yaml"
    text = path.read_text(encoding="utf-8")
    path.write_text(
        text.replace("trigger_rules:\n", "trigger_rules:\n  - text: Write a rule.\n"),
        encoding="utf-8",
    )
    problems = read_profile(tmp_path / "language")
    assert isinstance(problems, list)
    assert "A rule needs at least one check, or review: true." in problems[0].message


def branch_tree(repository: Path, branch: str, content: str) -> None:
    write_tree(
        repository,
        {
            "knowledge/top/node.md": node_source("top", directives=("Frob the top file.",)),
            "knowledge/top/mid/node.md": node_source(
                "mid", broader=("top",), directives=("Frob the middle file.",)
            ),
            "knowledge/top/mid/low/node.md": node_source(
                "low", broader=("mid",), directives=("Frob the lowest file.",)
            ),
            "knowledge/other/node.md": node_source("other", directives=("Frob the other file.",)),
        },
    )
    (repository / f"governance/language/branches/{branch}.yaml").write_text(
        content, encoding="utf-8"
    )


def problem_folders(repository: Path) -> list[str]:
    return [problem.path.parent.name for problem in check_language(repository)[1]]


def test_a_branch_verb_applies_to_the_node_and_each_node_under_it(tmp_path: Path) -> None:
    branch_tree(tmp_path, "mid", "approved_verbs: [frob]\n")
    assert problem_folders(tmp_path) == ["other", "top"]


def test_a_branch_verb_at_the_top_reaches_the_lowest_node(tmp_path: Path) -> None:
    branch_tree(tmp_path, "top", "approved_verbs: [frob]\n")
    assert problem_folders(tmp_path) == ["other"]


def test_a_branch_can_prohibit_a_term_for_its_nodes_only(tmp_path: Path) -> None:
    branch_tree(tmp_path, "mid", "approved_verbs: [frob]\nprohibited:\n  x: [file]\n")
    problems = check_language(tmp_path)[1]
    assert {
        (problem.path.parent.name, problem.code)
        for problem in problems
        if problem.code == "prohibited"
    } == {("mid", "prohibited"), ("low", "prohibited")}


def test_a_branch_can_prohibit_a_base_verb() -> None:
    profile = replace(PROFILE, branches={"sample": Vocabulary(prohibited={"x": ("Run",)})})
    assert directive_codes("Run the suite.", profile) == {"prohibited"}
    assert directive_codes("Test the suite.", profile) == set()


def test_a_branch_prohibition_keeps_the_base_category() -> None:
    profile = replace(PROFILE, branches={"sample": Vocabulary(prohibited={"x": ("usually",)})})
    terms = profile.terms_for(["sample"])
    assert terms.prohibited["usually"] == "hedge"


def test_a_branch_with_no_node_is_a_problem(tmp_path: Path) -> None:
    write_tree(tmp_path)
    path = tmp_path / "governance/language/branches/missing.yaml"
    path.write_text("approved_verbs: [frob]\n", encoding="utf-8")
    problems = check_language(tmp_path)[1]
    assert [(problem.path, problem.code, problem.line) for problem in problems] == [
        (path, "vocabulary-branch", 1)
    ]
    assert problems[0].message == "No node has the ID 'missing'."


def test_a_bad_branch_file_is_a_problem(tmp_path: Path) -> None:
    write_tree(tmp_path)
    path = tmp_path / "governance/language/branches/sample.yaml"
    path.write_text("approved_verbs: 1\n", encoding="utf-8")
    problems = check_language(tmp_path)[1]
    assert [(problem.path, problem.code) for problem in problems] == [(path, "language-profile")]


@pytest.mark.parametrize("name", ["sample.yml", "sample.txt"])
def test_a_branch_file_with_a_wrong_suffix_is_a_problem(tmp_path: Path, name: str) -> None:
    write_tree(tmp_path)
    path = tmp_path / "governance/language/branches" / name
    path.write_text("approved_verbs: [frob]\n", encoding="utf-8")
    problems = check_language(tmp_path)[1]
    assert [(problem.path, problem.code) for problem in problems] == [(path, "language-profile")]


def test_all_profile_problems_print_together(tmp_path: Path) -> None:
    write_tree(tmp_path)
    language = tmp_path / "governance/language"
    (language / "grammar.yaml").write_text("", encoding="utf-8")
    (language / "vocabulary.yaml").write_text("", encoding="utf-8")
    (language / "branches/sample.yaml").write_text("x: 1\n", encoding="utf-8")
    (language / "branches/other.txt").write_text("", encoding="utf-8")
    problems = check_language(tmp_path)[1]
    assert sorted(problem.path.name for problem in problems) == [
        "grammar.yaml",
        "other.txt",
        "sample.yaml",
        "vocabulary.yaml",
    ]


def test_the_language_folder_needs_no_branch_folder(tmp_path: Path) -> None:
    write_tree(tmp_path)
    shutil.rmtree(tmp_path / "governance/language/branches")
    assert check_language(tmp_path) == (0, [])


NO_MODEL_SCRIPT = """
import sys
from pathlib import Path

from knowledge_architecture.language import check_language

result = check_language(Path(sys.argv[1]))
print(result[0], len(result[1]), "spacy" in sys.modules)
"""


def run_no_model_script(repository: Path) -> str:
    result = subprocess.run(  # noqa: S603
        [sys.executable, "-c", NO_MODEL_SCRIPT, str(repository)],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def test_an_empty_tree_does_not_load_the_model(tmp_path: Path) -> None:
    write_tree(tmp_path)
    assert run_no_model_script(tmp_path) == "0 0 False"


def test_a_node_with_no_text_does_not_load_the_model(tmp_path: Path) -> None:
    write_tree(tmp_path, {"knowledge/a/node.md": node_source()})
    assert run_no_model_script(tmp_path) == "0 0 False"


def test_a_tree_with_text_loads_the_model(tmp_path: Path) -> None:
    write_tree(tmp_path, {"knowledge/a/node.md": node_source(directives=("Run the suite.",))})
    assert run_no_model_script(tmp_path) == "1 0 True"


def all_rules() -> list[str]:
    grammar = PROFILE.grammar
    rules = (*grammar.directive_rules, *grammar.trigger_rules, *grammar.description_rules)
    return [rule.text for rule in rules]


@pytest.mark.parametrize("text", all_rules())
def test_each_grammar_rule_passes_the_grammar(text: str) -> None:
    assert problems_of(node_source(directives=(text,))) == []


def test_the_grammar_rules_do_not_repeat() -> None:
    assert len(all_rules()) == len(set(all_rules()))


def test_each_check_has_a_rule() -> None:
    grammar = PROFILE.grammar
    rules = (*grammar.directive_rules, *grammar.trigger_rules, *grammar.description_rules)
    covered = {code for rule in rules for code in rule.checks}
    assert covered == set(get_args(CheckCode.__value__))


def test_the_grammar_rules_state_the_limits() -> None:
    grammar = PROFILE.grammar
    rules = all_rules()
    assert f"Write each rule in `{grammar.directive.max_words}` words or fewer." in rules
    assert f"Put at most `{grammar.directive.max_conditions}` condition in a rule." in rules
    assert f"Put at most `{grammar.directive.max_unless}` `unless` in a rule." in rules
    assert f"Write each trigger in `{grammar.trigger.max_words}` words or fewer." in rules
    limits = grammar.skill_description
    assert (
        f"Write each sentence of a skill description in `{limits.max_sentence_words}` "
        "words or fewer."
    ) in rules
    assert (
        f"Write each skill description in `{limits.max_characters}` characters or fewer." in rules
    )
    assert (
        f"Keep the skill listing at `{limits.max_listing_characters}` characters or fewer." in rules
    )


def test_the_semantic_rules_are_marked_for_review() -> None:
    review = {rule.text for rule in PROFILE.grammar.directive_rules if rule.review}
    assert {
        "Write one directive in each rule.",
        "Name the concrete object of each rule.",
        "Write each condition as a state or an event that the reader observes.",
    } <= review
    assert "Write each rule as one sentence that ends with a period." not in review


def test_the_vendored_linter_is_unchanged() -> None:
    digest = hashlib.sha256((VENDORED / "ste_lint.py").read_bytes()).hexdigest()
    assert digest == VENDORED_DIGEST


def test_the_vendored_linter_keeps_its_license() -> None:
    assert "MIT License" in (VENDORED / "ste_lint.LICENSE").read_text(encoding="utf-8")


def test_the_vendored_linter_passes_its_own_tests(capsys: pytest.CaptureFixture[str]) -> None:
    ste_lint.selftest()
    assert capsys.readouterr().out == "selftest OK\n"


def test_an_advisory_finding_does_not_fail() -> None:
    assert "ste" not in directive_codes("Keep the file that is changed.")
    assert "ste" not in trigger_codes("A file has changed.")


def test_the_grammar_word_limit_replaces_the_linter_limit() -> None:
    limits = PROFILE.grammar.directive.model_copy(update={"max_words": 40})
    profile = replace(PROFILE, grammar=PROFILE.grammar.model_copy(update={"directive": limits}))
    assert "ste" not in directive_codes(f"Run {words(30)}.", profile)
