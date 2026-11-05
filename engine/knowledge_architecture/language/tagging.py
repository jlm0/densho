from functools import cache
from typing import TYPE_CHECKING

from knowledge_architecture.language.form import USE_WHEN, Finding, description_parts

if TYPE_CHECKING:
    from collections.abc import Iterable

    from spacy.language import Language
    from spacy.tokens import Doc, Token

    from knowledge_architecture.language.profile import Grammar, Terms

MODEL = "en_core_web_sm"
SUBJECTS = frozenset({"nsubj", "nsubjpass", "csubj", "csubjpass", "expl"})
AUXILIARIES = frozenset({"aux", "auxpass"})
JOINED_VERBS = frozenset({"conj", "dep", "parataxis"})
CLAUSE_BREAKS = frozenset({",", ":", "then"})
VERB_PARTS = frozenset({"VERB", "AUX"})
PRESENT_TAGS = frozenset({"VBZ", "VBP"})
MISREAD_VERB_TAGS = frozenset({"NNS", "VBZ"})
UNLESS = "unless"


@cache
def _language() -> Language:
    import spacy  # noqa: PLC0415

    return spacy.load(MODEL, exclude=["ner"])


def _root(doc: Doc) -> Token:
    return doc[0].sent.root


def _subject_of(token: Token) -> Token | None:
    return next((child for child in token.children if child.dep_ in SUBJECTS), None)


def _is_uninflected(token: Token) -> bool:
    return token.lower_ == token.lemma_.casefold()


def _starts_a_clause(token: Token) -> bool:
    start = token.left_edge
    return start.i == 0 or start.nbor(-1).text == ","


def _is_misread_opening_verb(subject: Token) -> bool:
    return subject.left_edge == subject


def _imperative(doc: Doc) -> list[Finding]:
    root = _root(doc)
    subject = _subject_of(root)
    if root.pos_ not in VERB_PARTS or subject is None or _is_misread_opening_verb(subject):
        return []
    if _starts_a_clause(subject):
        return [("imperative", "This reads as a statement. Write an instruction.")]
    return []


def _root_follows_a_second_clause(doc: Doc, root: Token) -> bool:
    return doc[0].pos_ == "VERB" and any(token.lower_ in CLAUSE_BREAKS for token in doc[1 : root.i])


def _second_directive(doc: Doc) -> list[Finding]:
    root = _root(doc)
    joined = [
        child
        for child in root.children
        if child.dep_ in JOINED_VERBS and child.pos_ == "VERB" and _subject_of(child) is None
    ]
    if joined or _root_follows_a_second_clause(doc, root):
        return [("second-directive", "Split this into one rule for each action.")]
    return []


def _markers(doc: Doc, words: Iterable[str]) -> list[Token]:
    chosen = set(words)
    return [
        token
        for token in doc
        if token.lower_ in chosen and (token.dep_ == "mark" or token.tag_ == "WRB")
    ]


def _condition_count(doc: Doc, grammar: Grammar) -> list[Finding]:
    markers = _markers(doc, grammar.conditions)
    first = doc[0]
    opens = first.lower_ in grammar.conditions and first not in markers
    count = len(markers) + opens
    limit = grammar.directive.max_conditions
    if count > limit:
        return [("condition-count", f"The rule has {count} conditions. The limit is {limit}.")]
    return []


def _is_misread_clause(root: Token) -> bool:
    return root.tag_ in MISREAD_VERB_TAGS and any(child.dep_ == "det" for child in root.children)


def _clause_findings(root: Token) -> list[Finding]:
    subject = _subject_of(root)
    if subject is None:
        message = "Write a clause with a subject and a verb, as in: You edit a test file."
        return [("trigger-form", message)]
    findings: list[Finding] = []
    if subject.left_edge.i != 0:
        findings.append(("trigger-form", "Start the trigger with its subject."))
    verb = next((child for child in root.children if child.dep_ in AUXILIARIES), root)
    if not (verb.tag_ in PRESENT_TAGS or _is_uninflected(verb)):
        findings.append(("trigger-form", "Write the verb in the present tense."))
    return findings


def _trigger_structure(doc: Doc, grammar: Grammar) -> list[Finding]:
    first = doc[0]
    if first.lower_ in grammar.conditions:
        message = f"Remove {first.text!a}. A trigger already states a condition."
        return [("trigger-form", message)]
    root = _root(doc)
    findings = [] if _is_misread_clause(root) else _clause_findings(root)
    if _markers(doc, [*grammar.conditions, UNLESS]):
        findings.append(("condition-count", "Do not put a second condition in a trigger."))
    return findings


class Tagger:
    def __init__(self, prohibited_terms: Iterable[str]) -> None:
        from spacy.matcher import PhraseMatcher  # noqa: PLC0415

        self._language = _language()
        self._matcher = PhraseMatcher(self._language.vocab, attr="LOWER")
        for term in sorted(prohibited_terms):
            self._matcher.add(term, [self._language.make_doc(term)])

    def tag(self, text: str) -> Doc:
        return self._language(text)

    def prohibited(self, doc: Doc, terms: Terms) -> list[Finding]:
        names = self._language.vocab.strings
        found = [names[match_id] for match_id, _, _ in self._matcher(doc)]
        found += [token.lemma_.casefold() for token in doc if token.pos_ in VERB_PARTS]
        return [
            (
                "prohibited",
                f"Remove {term!a}. The vocabulary lists it as: {terms.prohibited[term]}.",
            )
            for term in found
            if term in terms.prohibited
        ]

    def directive(self, doc: Doc, grammar: Grammar) -> list[Finding]:
        return [*_imperative(doc), *_second_directive(doc), *_condition_count(doc, grammar)]

    def trigger(self, doc: Doc, grammar: Grammar) -> list[Finding]:
        return _trigger_structure(doc, grammar)

    def description(self, masked: str, grammar: Grammar) -> list[Finding]:
        action, use_when = description_parts(masked)
        return [
            *_imperative(self.tag(action)),
            *_trigger_structure(self.tag(use_when.removeprefix(USE_WHEN)), grammar),
        ]
