from dataclasses import dataclass
from typing import TYPE_CHECKING, Annotated, Any, Literal, Self, cast

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    ValidationError,
    model_validator,
)
from ruamel.yaml import YAML
from ruamel.yaml.error import MarkedYAMLError, YAMLError

from knowledge_architecture.parser.result import FieldPath, Problem

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping
    from pathlib import Path

PROFILE_CODE = "language-profile"
LISTING_ENTRY_CAP = 1536
GRAMMAR_FILE = "grammar.yaml"
RULE_SECTIONS = ("directive_rules", "trigger_rules", "description_rules")
BRANCH_FOLDER = "branches"
BRANCH_SUFFIX = ".yaml"
FOLDER_MARKER = ".gitkeep"

type CheckCode = Literal[
    "sentence",
    "word-count",
    "opening",
    "imperative",
    "second-directive",
    "condition-count",
    "unless-count",
    "prohibited",
    "literal",
    "duplicate-rule",
    "ste",
    "trigger-form",
    "description-form",
    "description-length",
    "listing-budget",
]
type Limit = Annotated[int, Field(gt=0)]
type Word = Annotated[str, StringConstraints(pattern=r"^[a-z]+(-[a-z]+)*$")]
type Term = Annotated[str, StringConstraints(pattern=r"^\S+( \S+)*$")]


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class DirectiveLimits(_Strict):
    max_words: Limit
    max_conditions: Annotated[int, Field(ge=0)]
    max_unless: Annotated[int, Field(ge=0)]


class TriggerLimits(_Strict):
    max_words: Limit


class DescriptionLimits(_Strict):
    max_sentence_words: Limit
    max_characters: Annotated[int, Field(gt=0, le=LISTING_ENTRY_CAP)]
    max_listing_characters: Limit


class GrammarRule(_Strict):
    text: Term
    checks: tuple[CheckCode, ...] = ()
    review: bool = False

    @model_validator(mode="after")
    def _needs_a_check_or_review(self) -> Self:
        if not self.checks and not self.review:
            message = "A rule needs at least one check, or review: true."
            raise ValueError(message)
        return self


class Grammar(_Strict):
    conditions: tuple[Word, ...]
    scopes: tuple[Word, ...]
    directive: DirectiveLimits
    trigger: TriggerLimits
    skill_description: DescriptionLimits
    directive_rules: tuple[GrammarRule, ...]
    trigger_rules: tuple[GrammarRule, ...]
    description_rules: tuple[GrammarRule, ...]


class Vocabulary(_Strict):
    approved_verbs: tuple[Word, ...] = ()
    prohibited: dict[Term, tuple[Term, ...]] = Field(default_factory=dict[str, tuple[str, ...]])


@dataclass(frozen=True, slots=True)
class Terms:
    verbs: frozenset[str]
    prohibited: Mapping[str, str]


@dataclass(frozen=True, slots=True)
class LanguageProfile:
    grammar: Grammar
    vocabulary: Vocabulary
    branches: Mapping[str, Vocabulary]
    branch_paths: Mapping[str, Path]

    def terms_for(self, node_ids: Iterable[str]) -> Terms:
        chosen = [
            self.vocabulary,
            *(self.branches[node_id] for node_id in sorted(set(node_ids) & set(self.branches))),
        ]
        prohibited: dict[str, str] = {}
        for vocabulary in chosen:
            for category, terms in vocabulary.prohibited.items():
                for term in terms:
                    prohibited.setdefault(term.casefold(), category)
        return Terms(
            frozenset(verb for vocabulary in chosen for verb in vocabulary.approved_verbs),
            prohibited,
        )

    def all_prohibited_terms(self) -> set[str]:
        return set(self.terms_for(self.branches).prohibited)


def read_profile(folder: Path) -> LanguageProfile | list[Problem]:
    grammar = _read_model(folder / GRAMMAR_FILE, Grammar)
    vocabulary = _read_model(folder / "vocabulary.yaml", Vocabulary)
    problems: list[Problem] = []
    branches: dict[str, Vocabulary] = {}
    branch_paths: dict[str, Path] = {}
    for path in _branch_files(folder / BRANCH_FOLDER):
        if path.suffix != BRANCH_SUFFIX:
            message = f"A branch vocabulary must be a file with the suffix {BRANCH_SUFFIX}."
            problems.append(Problem(path, 1, PROFILE_CODE, message))
            continue
        branch = _read_model(path, Vocabulary)
        if isinstance(branch, list):
            problems += branch
        else:
            branches[path.stem] = branch
            branch_paths[path.stem] = path
    if isinstance(grammar, list):
        problems = [*grammar, *problems]
    if isinstance(vocabulary, list):
        problems = [*vocabulary, *problems]
    if isinstance(grammar, list) or isinstance(vocabulary, list) or problems:
        return problems
    return LanguageProfile(grammar, vocabulary, branches, branch_paths)


def rule_locations(path: Path, grammar: Grammar) -> list[tuple[str, int]]:
    yaml: Any = YAML(typ="rt")
    data = cast("object", yaml.load(path.read_text(encoding="utf-8")))
    return [
        (rule.text, _line_of(data, (section, index, "text")))
        for section in RULE_SECTIONS
        for index, rule in enumerate(cast("tuple[GrammarRule, ...]", getattr(grammar, section)))
    ]


def _branch_files(folder: Path) -> list[Path]:
    if not folder.is_dir():
        return []
    return sorted(path for path in folder.iterdir() if path.name != FOLDER_MARKER)


def _read_model[ModelT: BaseModel](path: Path, model: type[ModelT]) -> ModelT | list[Problem]:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return [Problem(path, 1, PROFILE_CODE, "The file is not valid UTF-8.")]
    except OSError as error:
        return [Problem(path, 1, PROFILE_CODE, _one_line(error))]
    yaml: Any = YAML(typ="rt")
    try:
        data = cast("object", yaml.load(text))
    except YAMLError as error:
        return [Problem(path, _error_line(error), PROFILE_CODE, _one_line(error))]
    except (ValueError, OverflowError, RecursionError) as error:
        return [Problem(path, 1, PROFILE_CODE, f"YAML cannot read a value: {_one_line(error)}")]
    try:
        return model.model_validate(data)
    except ValidationError as error:
        return [
            Problem(
                path,
                _line_of(data, detail["loc"]),
                PROFILE_CODE,
                f"{_dotted(detail['loc'])}: {detail['msg']}",
            )
            for detail in error.errors()
        ]


def _one_line(error: BaseException) -> str:
    return " ".join(str(error).split())


def _error_line(error: YAMLError) -> int:
    if isinstance(error, MarkedYAMLError):
        marked: Any = error
        if marked.problem_mark is not None:
            return cast("int", marked.problem_mark.line) + 1
    return 1


def _position(container: Any, part: str | int) -> int:  # noqa: ANN401
    start: Any = container.lc.key(part)
    return cast("int", start[0])


def _line_of(data: object, location: FieldPath) -> int:
    line = 0
    current: Any = data
    for part in location:
        try:
            line = _position(current, part)
            current = current[part]
        except AttributeError, IndexError, KeyError, TypeError:
            break
    return line + 1


def _dotted(location: FieldPath) -> str:
    return ".".join(str(part) for part in location) or "file"
