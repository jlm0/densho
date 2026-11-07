from functools import cache
from typing import TYPE_CHECKING, cast

from engine.language.form import DO_NOT, PREFER, USE_WHEN, Finding, description_parts

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping

    from spacy.language import Language
    from spacy.pipeline import Lemmatizer
    from spacy.tokens import Doc, Token

    from engine.language.profile import Grammar, Terms

MODEL = "en_core_web_sm"
SUBJECTS = frozenset({"nsubj", "nsubjpass", "csubj", "csubjpass", "expl"})
AUXILIARIES = frozenset({"aux", "auxpass"})
JOINED_VERBS = frozenset({"conj", "dep", "parataxis"})
CLAUSE_STARTS = frozenset({",", ":", "then", "and", "or"})
VERB_PARTS = frozenset({"VERB", "AUX"})
PRESENT_TAGS = frozenset({"VBZ", "VBP"})
MISREAD_VERB_TAGS = frozenset({"NNS", "VBZ"})
BASE_TAGS = frozenset({"VB", "VBP"})
INFLECTED_TAGS = frozenset({"VBZ", "VBD"})
OBJECT_STARTS = frozenset({"DET", "PRON"})
NOUN_PARTS = frozenset({"NOUN", "PROPN"})
NOUN_MODIFIED = frozenset({*NOUN_PARTS, "ADJ", "NUM"})
UNLESS = "unless"


@cache
def _language() -> Language:
    import spacy  # noqa: PLC0415

    return spacy.load(MODEL, exclude=["ner"])


@cache
def _noun_tables() -> tuple[frozenset[str], tuple[tuple[str, str], ...], Mapping[str, list[str]]]:
    lookups = cast("Lemmatizer", _language().get_pipe("lemmatizer")).lookups
    index = cast("list[str]", lookups.get_table("lemma_index")["noun"])
    rules = cast("list[list[str]]", lookups.get_table("lemma_rules")["noun"])
    exceptions = cast("dict[str, list[str]]", lookups.get_table("lemma_exc")["noun"])
    return frozenset(index), tuple((old, new) for old, new in rules), exceptions


def _has_noun_reading(word: str) -> bool:
    index, rules, exceptions = _noun_tables()
    forms = {word, *exceptions.get(word, ())}
    forms.update(word.removesuffix(old) + new for old, new in rules if word.endswith(old))
    return not index.isdisjoint(forms)


def _root(doc: Doc) -> Token:
    return doc[0].sent.root


def _subject_of(token: Token) -> Token | None:
    return next((child for child in token.children if child.dep_ in SUBJECTS), None)


def _finite_verb(root: Token) -> Token:
    return next((child for child in root.children if child.dep_ in AUXILIARIES), root)


def _is_uninflected(token: Token) -> bool:
    return token.lower_ == token.lemma_.casefold()


def _opens_a_clause(token: Token) -> bool:
    return token.i == 0 or token.nbor(-1).text == ","


def _starts_a_clause(token: Token) -> bool:
    start = token.left_edge
    return start.dep_ != "mark" and _opens_a_clause(start)


def _is_one_bare_word(subject: Token) -> bool:
    return subject.left_edge == subject


def _cannot_be_an_object(verb: Token) -> bool:
    if verb.pos_ == "AUX":
        return True
    if verb.tag_ not in INFLECTED_TAGS or _has_noun_reading(verb.lower_):
        return False
    after = verb.doc[verb.i + 1] if verb.i + 1 < len(verb.doc) else None
    return verb.tag_ == "VBZ" or after is None or after.pos_ not in NOUN_MODIFIED


def _object_is_a_verb(root: Token) -> bool:
    after = root.doc[root.i + 1] if root.i + 1 < len(root.doc) else None
    return (
        after is not None
        and after.head == root
        and after.dep_ == "dobj"
        and after.tag_ == "NNS"
        and not _has_noun_reading(after.lower_)
    )


def _reads_as_a_statement(root: Token) -> bool:
    subject = _subject_of(root)
    if subject is None:
        return _opens_a_clause(root) and _object_is_a_verb(root)
    if not _starts_a_clause(subject):
        return False
    return not _is_one_bare_word(subject) or _cannot_be_an_object(_finite_verb(root))


def _imperative(doc: Doc) -> list[Finding]:
    root = _root(doc)
    if root.pos_ not in VERB_PARTS or not _reads_as_a_statement(root):
        return []
    return [("imperative", "This reads as a statement. Write an instruction.")]


def _past_do_not(start: Token) -> Token:
    doc = start.doc
    words = [token.lower_ for token in doc[start.i : start.i + len(DO_NOT) + 1]]
    if words[: len(DO_NOT)] == DO_NOT and len(words) > len(DO_NOT):
        return doc[start.i + len(DO_NOT)]
    return start


def _directive_verb(doc: Doc, grammar: Grammar, terms: Terms) -> Token:
    root = _root(doc)
    starts = [doc[0]]
    if doc[0].lower_ in {*grammar.conditions, *grammar.scopes}:
        starts = [token.nbor(1) for token in doc[:-1] if token.text == ","]
    openings = [
        verb
        for verb in map(_past_do_not, starts)
        if verb.lower_ in terms.verbs or verb.lower_ == PREFER
    ]
    if root in openings or not openings:
        return root
    return openings[0]


def _starts_a_second_clause(token: Token) -> bool:
    before = token.i - 1
    doc = token.doc
    while before >= 0 and doc[before].head == token and doc[before].lower_ in DO_NOT:
        before -= 1
    return before >= 0 and doc[before].lower_ in CLAUSE_STARTS


def _has_a_second_action_form(token: Token) -> bool:
    if token.tag_ in BASE_TAGS:
        return True
    after = token.doc[token.i + 1] if token.i + 1 < len(token.doc) else None
    return token.tag_ in INFLECTED_TAGS and after is not None and after.pos_ in OBJECT_STARTS


def _reads_as_a_verb(token: Token, terms: Terms) -> bool:
    lemma = token.lemma_.casefold()
    if any(child.dep_ == "conj" and child.pos_ in NOUN_PARTS for child in token.children):
        return False
    return lemma in terms.verbs or not _has_noun_reading(lemma)


def _is_second_action(token: Token, terms: Terms) -> bool:
    return (
        token.pos_ == "VERB"
        and _subject_of(token) is None
        and _reads_as_a_verb(token, terms)
        and _has_a_second_action_form(token)
        and _starts_a_second_clause(token)
    )


def _second_directive(doc: Doc, grammar: Grammar, terms: Terms) -> list[Finding]:
    root = _root(doc)
    verb = _directive_verb(doc, grammar, terms)
    heads = {root.i, verb.i}
    later = [
        token
        for token in doc[verb.i + 1 :]
        if token.i == root.i or (token.dep_ in JOINED_VERBS and token.head.i in heads)
    ]
    if any(_is_second_action(token, terms) for token in later):
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
    verb = _finite_verb(root)
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

    def directive(self, doc: Doc, grammar: Grammar, terms: Terms) -> list[Finding]:
        return [
            *_imperative(doc),
            *_second_directive(doc, grammar, terms),
            *_condition_count(doc, grammar),
        ]

    def trigger(self, doc: Doc, grammar: Grammar) -> list[Finding]:
        return _trigger_structure(doc, grammar)

    def description(self, masked: str, grammar: Grammar) -> list[Finding]:
        action, use_when = description_parts(masked)
        return [
            *_imperative(self.tag(action)),
            *_trigger_structure(self.tag(use_when.removeprefix(USE_WHEN)), grammar),
        ]
