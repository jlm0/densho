# pyright: reportUnknownMemberType=false
import re
from pathlib import Path
from typing import TYPE_CHECKING, cast

import pytest
from ruamel.yaml import YAML

from engine.generated.metamodel import Invocation, Skill
from engine.graph.skills import explicit_copies
from engine.language.form import EXCLUSION, description_parts
from engine.parser.node import node_folders, parse_tree

if TYPE_CHECKING:
    from engine.parser.result import ParsedNode

REPO = Path(__file__).resolve().parents[1]
CASES_NAME = "trigger-cases.yaml"
MIN_POSITIVE = 3
MIN_NEGATIVE = 2
NEGATIVE_KEYS = ["prompt", "skill"]
CODE_NAME = re.compile(r"`([^`]+)`")
THIRD = 2


def template_items() -> list[ParsedNode]:
    items, problems = parse_tree(node_folders(REPO))
    assert problems == []
    return items


ITEMS = template_items()
SKILLS = {item.node.id: item for item in ITEMS if isinstance(item.node, Skill)}
DESCRIPTIONS = {
    name: item.node.description for name, item in SKILLS.items() if isinstance(item.node, Skill)
}
CONVERTED = sorted(
    name
    for name, item in SKILLS.items()
    if isinstance(item.node, Skill)
    and explicit_copies(item)
    and item.node.invocation == Invocation.agent
)


def _list(value: object) -> list[object] | None:
    return cast("list[object]", value) if isinstance(value, list) else None


def _mapping(value: object) -> dict[str, object] | None:
    return cast("dict[str, object]", value) if isinstance(value, dict) else None


def _prompt(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def case_problems(data: object, skills: set[str]) -> list[str]:
    fields = _mapping(data)
    if fields is None or sorted(fields) != ["negative", "positive"]:
        return ["The file holds exactly the keys positive and negative."]
    positive, negative = _list(fields["positive"]), _list(fields["negative"])
    problems: list[str] = []
    if positive is None or not all(_prompt(prompt) for prompt in positive):
        problems.append("Each positive case is a prompt.")
    elif len(positive) < MIN_POSITIVE:
        problems.append(f"The file holds at least {MIN_POSITIVE} positive cases.")
    if negative is None:
        return [*problems, "The negative cases are a list."]
    if len(negative) < MIN_NEGATIVE:
        problems.append(f"The file holds at least {MIN_NEGATIVE} negative cases.")
    for entry in negative:
        case = _mapping(entry)
        if case is None or sorted(case) != NEGATIVE_KEYS:
            problems.append("Each negative case holds exactly a prompt and a skill.")
            continue
        if not _prompt(case["prompt"]):
            problems.append("Each negative case has a prompt.")
        skill = case["skill"]
        if skill is not None and skill not in skills:
            problems.append(f"No skill has the ID {skill}.")
    return problems


def sibling_problems(description: str, skills: set[str], own: str) -> list[str]:
    parts = description_parts(description)
    third = parts[THIRD] if len(parts) > THIRD else ""
    if not third.startswith(EXCLUSION):
        return []
    names = CODE_NAME.findall(third)
    if not names:
        return ["The third sentence names no skill."]
    return [
        f"The third sentence names {name}, which is not another skill."
        for name in names
        if name not in skills or name == own
    ]


def read_cases(path: Path) -> object:
    return YAML(typ="safe").load(path.read_text(encoding="utf-8"))


GOOD: dict[str, object] = {
    "positive": ["One.", "Two.", "Three."],
    "negative": [{"prompt": "Four.", "skill": "other"}, {"prompt": "Five.", "skill": None}],
}


def test_the_template_has_converted_skills() -> None:
    assert len(CONVERTED) >= MIN_NEGATIVE


@pytest.mark.parametrize("name", CONVERTED)
def test_each_converted_skill_has_its_trigger_cases(name: str) -> None:
    path = SKILLS[name].path.parent / CASES_NAME
    assert path.is_file(), path
    assert case_problems(read_cases(path), set(SKILLS)) == []


@pytest.mark.parametrize("name", sorted(DESCRIPTIONS))
def test_each_third_sentence_names_other_skills(name: str) -> None:
    assert sibling_problems(DESCRIPTIONS[name], set(SKILLS), name) == []


def test_good_cases_pass() -> None:
    assert case_problems(GOOD, {"other"}) == []


@pytest.mark.parametrize(
    ("data", "problem"),
    [
        ({"positive": ["One.", "Two."], "negative": GOOD["negative"]}, "at least 3 positive"),
        (
            {"positive": GOOD["positive"], "negative": [{"prompt": "A.", "skill": None}]},
            "at least 2",
        ),
        ({"positive": ["One.", "Two.", " "], "negative": GOOD["negative"]}, "is a prompt"),
        ({"positive": "One.", "negative": GOOD["negative"]}, "is a prompt"),
        ({"positive": GOOD["positive"]}, "exactly the keys"),
        ({**GOOD, "extra": []}, "exactly the keys"),
        (["One."], "exactly the keys"),
        ({"positive": GOOD["positive"], "negative": "Four."}, "are a list"),
        (
            {"positive": GOOD["positive"], "negative": [{"prompt": "A.", "skill": "gone"}] * 2},
            "No skill has the ID gone.",
        ),
        (
            {"positive": GOOD["positive"], "negative": [{"prompt": "A."}, {"prompt": "B."}]},
            "exactly a prompt and a skill",
        ),
        (
            {"positive": GOOD["positive"], "negative": [{"prompt": 1, "skill": None}] * 2},
            "has a prompt",
        ),
        (
            {"positive": GOOD["positive"], "negative": ["Four.", "Five."]},
            "exactly a prompt and a skill",
        ),
    ],
)
def test_bad_cases_fail(data: object, problem: str) -> None:
    assert any(problem in found for found in case_problems(data, {"other"}))


@pytest.mark.parametrize(
    ("description", "problem"),
    [
        ("Do it. Use when you do it. Do not use it for `gone`.", "names gone"),
        ("Do it. Use when you do it. Do not use it for `own`.", "names own"),
        ("Do it. Use when you do it. Do not use it for other work.", "names no skill"),
    ],
)
def test_a_bad_third_sentence_fails(description: str, problem: str) -> None:
    assert any(problem in found for found in sibling_problems(description, {"own", "x"}, "own"))


def test_a_good_third_sentence_passes() -> None:
    description = "Do it. Use when you do it. Do not use it for a review (`x`)."
    assert sibling_problems(description, {"own", "x"}, "own") == []
    assert sibling_problems("Do it. Use when you do it.", {"own"}, "own") == []
