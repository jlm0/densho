# pyright: reportUnknownVariableType=false
import re
from typing import TYPE_CHECKING, TypedDict, cast

from engine.language.prose import CODE_WORD, words_of
from engine.vendor.ste_lint import lint

if TYPE_CHECKING:
    from engine.language.profile import Grammar, Terms

type Finding = tuple[str, str]


class _SteFinding(TypedDict):
    rule: str
    level: str
    message: str


USE_WHEN = "Use when "
EXCLUSION = "Do not use it for "
DO_NOT = ["do", "not"]
PREFER = "prefer"
PREFER_FINDING: Finding = (
    "opening",
    (
        "Do not start a rule with Prefer. Write the rule, and write the other case with unless "
        "or as a second rule."
    ),
)
UNLESS = "unless"
DESCRIPTION_SENTENCES = (2, 3)
INTERIOR_END = re.compile(r"[.!?](?=\s+\S)")
SENTENCE_BREAK = re.compile(r"(?<=[.!?])\s+")
LITERAL_SHAPE = re.compile(
    r"\d|[/\\]|^-{1,2}\w|\w_\w|\w\.\w|\w\(|^[a-z]+[A-Z]|[=<>{}\[\]$@#%^*~|+\"\u201c\u201d]"
)
QUOTED = re.compile(r"(?<!\w)['\u2018][^'\u2019]+['\u2019](?!\w)")
TRAILING_PUNCTUATION = ".,:;!?"
HARD_LEVEL = "advisory-free"
STE_REPLACED_RULES = frozenset({"long-sentence"})


def _sentence(text: str) -> list[Finding]:
    findings: list[Finding] = []
    if not text[:1].isupper():
        findings.append(("sentence", "Start the sentence with a capital letter."))
    if not text.endswith(".") or text.endswith(".."):
        findings.append(("sentence", "End the sentence with one period."))
    if INTERIOR_END.search(text):
        findings.append(("sentence", "Write one sentence. A period, ! or ? ends it early."))
    return findings


def _word_count(text: str, limit: int) -> list[Finding]:
    count = len(words_of(text))
    if count <= limit:
        return []
    return [("word-count", f"The sentence has {count} words. The limit is {limit}.")]


def _literals(text: str) -> list[Finding]:
    found = [token.rstrip(TRAILING_PUNCTUATION) for token in text.split()]
    shaped = [token for token in found if LITERAL_SHAPE.search(token)]
    return [
        ("literal", f"Put {literal!a} in backticks. It reads as a command, a path, or a value.")
        for literal in [*shaped, *QUOTED.findall(text)]
    ]


def _ste(text: str) -> list[Finding]:
    findings = cast("tuple[list[_SteFinding], int]", lint(text))[0]
    return [
        ("ste", f"{finding['rule']}: {finding['message']}")
        for finding in findings
        if finding["level"] == HARD_LEVEL and finding["rule"] not in STE_REPLACED_RULES
    ]


def _starts_directive(words: list[str], terms: Terms) -> bool:
    if words[:2] == DO_NOT:
        return len(words) > len(DO_NOT) and words[len(DO_NOT)] in terms.verbs
    return bool(words) and words[0] in terms.verbs


def _opens_with_prefer(text: str, grammar: Grammar) -> bool:
    head, *tails = text.split(",")
    words = words_of(head)
    if words and words[0] in {*grammar.conditions, *grammar.scopes}:
        return any(words_of(tail)[:1] == [PREFER] for tail in tails)
    return words[:1] == [PREFER]


def _opening(text: str, grammar: Grammar, terms: Terms) -> list[Finding]:
    if _opens_with_prefer(text, grammar):
        return [PREFER_FINDING]
    return _approved_opening(text, grammar, terms)


def _approved_opening(text: str, grammar: Grammar, terms: Terms) -> list[Finding]:
    head, *tails = text.split(",")
    words = words_of(head)
    if words and words[0] in {*grammar.conditions, *grammar.scopes}:
        if not tails:
            return [("opening", "Put a comma after the condition or the scope.")]
        if any(_starts_directive(words_of(tail), terms) for tail in tails):
            return []
        message = "After the comma, start the directive with an approved verb or Do not."
        return [("opening", message)]
    if _starts_directive(words_of(text), terms):
        return []
    if words[:2] == DO_NOT:
        return [("opening", "Follow Do not with a verb from the approved list.")]
    first = words[0] if words else ""
    message = (
        f"Start the rule with an approved verb, Do not, a condition, or a scope. "
        f"The vocabulary does not approve {first!a}."
    )
    return [("opening", message)]


def _shared(text: str) -> list[Finding]:
    return [*_literals(text), *_ste(text)]


def directive_findings(masked: str, grammar: Grammar, terms: Terms) -> list[Finding]:
    limits = grammar.directive
    findings = [
        *_sentence(masked),
        *_word_count(masked, limits.max_words),
        *_opening(masked, grammar, terms),
        *_shared(masked),
    ]
    unless = words_of(masked).count(UNLESS)
    if unless > limits.max_unless:
        message = f"The rule has {unless} unless clauses. The limit is {limits.max_unless}."
        findings.append(("unless-count", message))
    return findings


def trigger_findings(masked: str, grammar: Grammar) -> list[Finding]:
    return [
        *_sentence(masked),
        *_word_count(masked, grammar.trigger.max_words),
        *_shared(masked),
    ]


def description_parts(masked: str) -> list[str]:
    return SENTENCE_BREAK.split(masked)


def description_findings(source: str, masked: str, grammar: Grammar, terms: Terms) -> list[Finding]:
    limits = grammar.skill_description
    findings = _shared(masked)
    if len(source) > limits.max_characters:
        message = (
            f"The description has {len(source)} characters. The limit is {limits.max_characters}."
        )
        findings.append(("description-length", message))
    parts = description_parts(masked)
    for part in parts:
        findings += _sentence(part)
        findings += _word_count(part, limits.max_sentence_words)
    if len(parts) not in DESCRIPTION_SENTENCES:
        message = (
            "Write 2 or 3 sentences: the action of the skill, Use when and a trigger, "
            "and Do not use it for with the sibling skills."
        )
        return [*findings, ("description-form", message)]
    action, use_when, *exclusion = parts
    first = next(iter(words_of(action)), "")
    if first not in terms.verbs:
        message = f"Start the first sentence with an approved verb, not {first!a}."
        findings.append(("description-form", message))
    if not use_when.startswith(USE_WHEN):
        findings.append(("description-form", "Start the second sentence with Use when."))
    for sentence in exclusion:
        if not sentence.startswith(EXCLUSION):
            findings.append(
                ("description-form", "Start the third sentence with Do not use it for.")
            )
        if CODE_WORD not in sentence:
            message = "Name each sibling skill of the third sentence in backticks."
            findings.append(("description-form", message))
    return findings
