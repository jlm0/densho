from typing import TYPE_CHECKING

from engine.generated.metamodel import (
    Invocation,
    Root,
    Skill,
    SkillPointer,
    SkillType,
    TaxonomyNode,
)
from engine.graph.references import edge_targets, problem_at
from engine.parser.result import Problem
from engine.parser.steps import STEP_SUFFIX, STEPS_FOLDER_NAME

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

    from engine.parser.result import ParsedNode

AGENT_SKILL_TYPES = frozenset({SkillType.flow, SkillType.lens})


def activity(trigger: str) -> str:
    text = trigger.removesuffix(".")
    return text[:1].lower() + text[1:]


def check_skill_types(items: Sequence[ParsedNode]) -> list[Problem]:
    by_id = {item.node.id: item for item in items}
    root = next(item for item in items if isinstance(item.node, Root))
    rows = {
        pointer.target for pointer in root.node.pointers or [] if isinstance(pointer, SkillPointer)
    }
    problems = _row_problems(root, by_id)
    for item in items:
        if isinstance(item.node, Skill):
            problems += _kind_problems(item, item.node, rows)
            if item.node.skill_type == SkillType.flow:
                problems += _flow_problems(item, item.node, by_id)
    return problems


def _row_problems(root: ParsedNode, by_id: Mapping[str, ParsedNode]) -> list[Problem]:
    problems: list[Problem] = []
    for index, pointer in enumerate(root.node.pointers or []):
        target = by_id.get(pointer.target)
        if not isinstance(pointer, SkillPointer) or target is None:
            continue
        skill = target.node
        if isinstance(skill, Skill) and activity(pointer.trigger) not in skill.description:
            message = (
                f"The description of {skill.id} does not name this activity. "
                "Put the activity in its Use when sentence."
            )
            problems.append(problem_at(root, ("pointers", index, "trigger"), "skill", message))
    return problems


def _kind_problems(item: ParsedNode, skill: Skill, rows: set[str]) -> list[Problem]:
    problems: list[Problem] = []
    if skill.skill_type in AGENT_SKILL_TYPES:
        if skill.invocation != Invocation.agent:
            message = "A flow or lens skill needs invocation: agent, so the agent starts it."
            problems.append(problem_at(item, ("invocation",), "skill", message))
        if skill.id not in rows:
            message = (
                "Add a densho:SkillPointer to this skill on the root, "
                "so the skill table of AGENTS.md names its activity."
            )
            problems.append(problem_at(item, ("skill_type",), "skill", message))
    if skill.skill_type != SkillType.flow:
        if skill.steps:
            message = "Only a flow skill has steps. Remove steps, or set skill_type to flow."
            problems.append(problem_at(item, ("steps",), "step", message))
        if item.step_files:
            message = "Only a flow skill has step files. Remove steps/, or set skill_type to flow."
            problems.append(problem_at(item, ("skill_type",), "step", message))
    return problems


def _flow_problems(
    item: ParsedNode, skill: Skill, by_id: Mapping[str, ParsedNode]
) -> list[Problem]:
    steps = skill.steps or []
    uses = skill.uses or []
    problems: list[Problem] = []
    if not steps:
        message = "Name the steps of the flow in steps, in their order."
        problems.append(problem_at(item, ("skill_type",), "step", message))
    if len(uses) != 1:
        message = "A flow skill uses exactly 1 node: the node of its discipline."
        problems.append(problem_at(item, ("uses",), "step", message))
    home = uses[0] if len(uses) == 1 else None
    files = {step.id for step in item.step_files}
    for index, step in enumerate(steps):
        location = ("steps", index)
        node = by_id[step].node
        if step in steps[:index]:
            problems.append(problem_at(item, location, "step", f"steps names {step} twice."))
            continue
        if home is not None and (
            not isinstance(node, TaxonomyNode) or home not in edge_targets(by_id[step], "broader")
        ):
            message = f"{step} is not under {home}. Name a node whose broader names {home}."
            problems.append(problem_at(item, location, "step", message))
        earlier = [
            other for other in steps[:index] if other in edge_targets(by_id[step], "informs")
        ]
        if earlier:
            message = f"{step} informs {earlier[0]}, so {step} comes before {earlier[0]} in steps."
            problems.append(problem_at(item, location, "step", message))
        if step not in files:
            message = f"Add the step file {STEPS_FOLDER_NAME}/{step}{STEP_SUFFIX}."
            problems.append(problem_at(item, location, "step", message))
    folder = item.path.parent / STEPS_FOLDER_NAME
    problems.extend(
        Problem(
            folder / f"{name}{STEP_SUFFIX}",
            1,
            "step",
            f"No entry in steps of {skill.id} names this step file. Add one, or remove the file.",
        )
        for name in sorted(files - set(steps))
    )
    return problems
