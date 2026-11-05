# pyright: reportUnknownMemberType=false
from dataclasses import dataclass, replace
from typing import TYPE_CHECKING, Literal

import networkx as nx

from knowledge_architecture.generated.metamodel import Skill
from knowledge_architecture.graph.references import problem_at
from knowledge_architecture.graph.structure import edge_graph
from knowledge_architecture.language.form import (
    Finding,
    description_findings,
    directive_findings,
    trigger_findings,
)
from knowledge_architecture.language.profile import GRAMMAR_FILE, read_profile, rule_locations
from knowledge_architecture.language.prose import read_prose
from knowledge_architecture.language.tagging import Tagger
from knowledge_architecture.parser.node import node_folders, parse_tree
from knowledge_architecture.parser.result import Problem

if TYPE_CHECKING:
    from collections.abc import Sequence
    from pathlib import Path

    from knowledge_architecture.language.profile import Grammar, LanguageProfile, Terms
    from knowledge_architecture.parser.result import ParsedNode

MAX_TEXT_CHARACTERS = 2000


@dataclass(frozen=True, slots=True)
class _Text:
    kind: Literal["directive", "trigger", "description"]
    path: Path
    line: int
    source: str
    node_id: str | None = None

    def problem(self, finding: Finding) -> Problem:
        return Problem(self.path, self.line, *finding)


@dataclass(frozen=True, slots=True)
class _Entry:
    text: _Text
    masked: str
    terms: Terms
    form_passed: bool = False


def _texts_of(item: ParsedNode) -> list[_Text]:
    node = item.node

    def text(
        kind: Literal["directive", "trigger", "description"], *field_path: str | int, source: str
    ) -> _Text:
        return _Text(kind, item.path, item.line_of(field_path), source, node.id)

    texts = [
        text("directive", "directives", index, "text", source=directive.text)
        for index, directive in enumerate(node.directives or [])
    ]
    texts += [
        text("trigger", "pointers", index, "trigger", source=pointer.trigger)
        for index, pointer in enumerate(node.pointers or [])
    ]
    if isinstance(node, Skill):
        texts.append(text("description", "description", source=node.description))
    return texts


def _terms_by_node(
    items: Sequence[ParsedNode], profile: LanguageProfile
) -> dict[str | None, Terms]:
    broader = edge_graph(items, "broader")
    terms: dict[str | None, Terms] = {
        item.node.id: profile.terms_for({item.node.id, *nx.descendants(broader, item.node.id)})
        for item in items
    }
    terms[None] = profile.terms_for(())
    return terms


def _unknown_branches(items: Sequence[ParsedNode], profile: LanguageProfile) -> list[Problem]:
    known = {item.node.id for item in items}
    return [
        Problem(path, 1, "vocabulary-branch", f"No node has the ID {node_id!a}.")
        for node_id, path in profile.branch_paths.items()
        if node_id not in known
    ]


def _listing_budget(items: Sequence[ParsedNode], profile: LanguageProfile) -> list[Problem]:
    budget = profile.grammar.skill_description.max_listing_characters
    total = 0
    for item in items:
        if isinstance(item.node, Skill):
            total += len(item.node.id) + len(item.node.description)
            if total > budget:
                message = (
                    f"The skill listing reaches {total} characters here. The budget is {budget}."
                )
                return [problem_at(item, ("description",), "listing-budget", message)]
    return []


def _duplicate(text: _Text, plain: str, seen: dict[str, _Text]) -> list[Finding]:
    if text.kind != "directive":
        return []
    key = " ".join(plain.casefold().split())
    first = seen.setdefault(key, text)
    if first is text:
        return []
    return [("duplicate-rule", f"This rule repeats the rule at {first.path}:{first.line}.")]


def _form_findings(entry: _Entry, grammar: Grammar) -> list[Finding]:
    if entry.text.kind == "directive":
        return directive_findings(entry.masked, grammar, entry.terms)
    if entry.text.kind == "trigger":
        return trigger_findings(entry.masked, grammar)
    return description_findings(entry.text.source, entry.masked, grammar, entry.terms)


def _tagged_findings(entry: _Entry, grammar: Grammar, tagger: Tagger) -> list[Finding]:
    doc = tagger.tag(entry.masked)
    findings = tagger.prohibited(doc, entry.terms)
    if not entry.form_passed:
        return findings
    if entry.text.kind == "directive":
        return [*findings, *tagger.directive(doc, grammar)]
    if entry.text.kind == "trigger":
        return [*findings, *tagger.trigger(doc, grammar)]
    return [*findings, *tagger.description(entry.masked, grammar)]


def check_items(
    items: Sequence[ParsedNode], profile: LanguageProfile, rules: Sequence[_Text] = ()
) -> tuple[int, list[Problem]]:
    grammar = profile.grammar
    problems = [*_unknown_branches(items, profile), *_listing_budget(items, profile)]
    texts = [*rules, *(text for item in items for text in _texts_of(item))]
    terms_by_node = _terms_by_node(items, profile)
    seen: dict[str, _Text] = {}
    entries: list[_Entry] = []
    for text in texts:
        if len(text.source) > MAX_TEXT_CHARACTERS:
            message = f"The text has {len(text.source)} characters. Shorten it."
            problems.append(text.problem(("word-count", message)))
            continue
        masked, plain = read_prose(text.source)
        entry = _Entry(text, masked, terms_by_node[text.node_id])
        findings = [*_form_findings(entry, grammar), *_duplicate(text, plain, seen)]
        problems += [text.problem(finding) for finding in findings]
        entries.append(replace(entry, form_passed=not findings))
    if entries:
        tagger = Tagger(profile.all_prohibited_terms())
        problems += [
            entry.text.problem(finding)
            for entry in entries
            for finding in _tagged_findings(entry, grammar, tagger)
        ]
    return len(texts), sorted(set(problems), key=_sort_key)


def _sort_key(problem: Problem) -> tuple[str, int, str, str]:
    return (str(problem.path), problem.line, problem.code, problem.message)


def check_language(repository: Path) -> tuple[int, list[Problem]]:
    folder = repository / "governance/language"
    profile = read_profile(folder)
    if isinstance(profile, list):
        return 0, sorted(profile, key=_sort_key)
    items, problems = parse_tree(node_folders(repository))
    if problems:
        return 0, problems
    grammar_file = folder / GRAMMAR_FILE
    rules = [
        _Text("directive", grammar_file, line, text)
        for text, line in rule_locations(grammar_file, profile.grammar)
    ]
    return check_items(items, profile, rules)
