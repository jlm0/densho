from typing import TYPE_CHECKING

from engine import tree_copies
from engine.generated.metamodel import (
    Invocation,
    Root,
    Skill,
    SkillPointer,
    SkillType,
    Status,
)
from engine.graph.references import problem_at
from engine.parser.result import Problem
from engine.parser.sections import Owner, section_problems
from engine.parser.steps import STEP_SUFFIX, STEPS_FOLDER_NAME

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

    from engine.generated.metamodel import Directive
    from engine.parser.result import FieldPath, ParsedNode, StepCopies, StepFile

AGENT_SKILL_TYPES = frozenset({SkillType.task, SkillType.lens})
SKILL_SECTIONS = ("Exit checklist", "Output")
ROOT_SECTIONS = ("use_a_skill", "create_a_rule")

type Directives = Mapping[str, tuple[ParsedNode, Directive]]


def activity(trigger: str) -> str:
    text = trigger.removesuffix(".")
    return text[:1].lower() + text[1:]


def explicit_copies(item: ParsedNode) -> bool:
    return bool(item.step_files) and all(step.copies is not None for step in item.step_files)


def check_skill_types(items: Sequence[ParsedNode]) -> list[Problem]:
    by_id = {item.node.id: item for item in items}
    directives: Directives = {
        directive.id: (item, directive)
        for item in items
        for directive in item.node.directives or []
    }
    root = next(item for item in items if isinstance(item.node, Root))
    rows = {
        pointer.target for pointer in root.node.pointers or [] if isinstance(pointer, SkillPointer)
    }
    problems = [*_row_problems(root, by_id), *_root_section_problems(root)]
    for item in items:
        if isinstance(item.node, Skill):
            problems += _kind_problems(item, item.node, rows)
            problems += _step_problems(item, item.node, by_id, directives)
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


def _root_section_problems(root: ParsedNode) -> list[Problem]:
    problems: list[Problem] = []
    seen: set[str] = set()
    for field in ROOT_SECTIONS:
        for index, name in enumerate(getattr(root.node, field) or []):
            if name in seen:
                message = f"{name} is in a root section already. Name it in 1 section only."
                problems.append(problem_at(root, (field, index), "skill", message))
            seen.add(name)
    return problems


def _kind_problems(item: ParsedNode, skill: Skill, rows: set[str]) -> list[Problem]:
    problems: list[Problem] = []
    if skill.skill_type in AGENT_SKILL_TYPES:
        if skill.invocation != Invocation.agent:
            message = "A task or lens skill needs invocation: agent, so the agent starts it."
            problems.append(problem_at(item, ("invocation",), "skill", message))
        if skill.id not in rows:
            message = (
                "Add a densho:SkillPointer to this skill on the root, "
                "so the skill table of AGENTS.md names its activity."
            )
            problems.append(problem_at(item, ("skill_type",), "skill", message))
    if skill.skill_type == SkillType.system:
        if skill.steps:
            message = "A system skill has no steps. Remove steps, or set skill_type to task."
            problems.append(problem_at(item, ("steps",), "step", message))
        if item.step_files:
            message = "A system skill has no step files. Remove steps/, or set skill_type to task."
            problems.append(problem_at(item, ("skill_type",), "step", message))
    elif skill.skill_type == SkillType.task and not skill.steps:
        message = "Name the steps of the task in steps, in their order."
        problems.append(problem_at(item, ("skill_type",), "step", message))
    return problems


def _step_problems(
    item: ParsedNode, skill: Skill, by_id: Mapping[str, ParsedNode], directives: Directives
) -> list[Problem]:
    if skill.skill_type == SkillType.system:
        return []
    steps = skill.steps or []
    problems: list[Problem] = []
    files = {step.id for step in item.step_files}
    for index, step in enumerate(steps):
        if step in steps[:index]:
            message = f"steps names {step} twice."
            problems.append(problem_at(item, ("steps", index), "step", message))
        elif step not in files:
            message = f"Add the step file {STEPS_FOLDER_NAME}/{step}{STEP_SUFFIX}."
            problems.append(problem_at(item, ("steps", index), "step", message))
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
    forms = {step.copies is not None for step in item.step_files}
    if len(forms) > 1:
        message = (
            "Write each step file of the skill in the same form: each with front matter, or none."
        )
        problems.append(problem_at(item, ("steps",), "step", message))
    elif explicit_copies(item):
        problems += _copy_problems(item, skill, by_id, directives)
    elif steps and skill.skill_type == SkillType.lens:
        message = "Write the step files of a lens in the copy form, with front matter."
        problems.append(problem_at(item, ("steps",), "step", message))
    elif steps:
        problems += tree_copies.tree_step_problems(item, skill, by_id)
    return problems


def _step_problem(item: ParsedNode, step: StepFile, field_path: FieldPath, message: str) -> Problem:
    path = step.path or item.path.parent / STEPS_FOLDER_NAME / f"{step.id}{STEP_SUFFIX}"
    return Problem(path, step.line_of(field_path), "step", message)


def _copy_problems(
    item: ParsedNode, skill: Skill, by_id: Mapping[str, ParsedNode], directives: Directives
) -> list[Problem]:
    problems: list[Problem] = []
    copied: set[str] = set()
    for step in item.step_files:
        if step.copies is not None:
            copied.update(name for name, _ in step.copies.copied())
            problems += _target_problems(item, step, step.copies, by_id, directives)
    for index, directive in enumerate(skill.directives or []):
        if directive.id not in copied:
            message = f"No step of {skill.id} names {directive.id}. Add it to a step."
            problems.append(problem_at(item, ("directives", index), "step", message))
    sections = section_problems(
        skill.body or "",
        item.path,
        SKILL_SECTIONS,
        item.line_of(("body",)),
        Owner("body of the skill", "step"),
    )
    if isinstance(sections, list):
        problems += sections
    return problems


def _target_problems(
    item: ParsedNode,
    step: StepFile,
    copies: StepCopies,
    by_id: Mapping[str, ParsedNode],
    directives: Directives,
) -> list[Problem]:
    problems: list[Problem] = []
    for name, field_path in copies.copied():
        found = directives.get(name)
        if found is None:
            message = (
                f"No directive has the ID {name}. A selection can remove the node that "
                "holds it. Name a directive of the graph, or remove the ID."
            )
            problems.append(_step_problem(item, step, field_path, message))
        elif found[1].status == Status.rejected:
            message = f"{name} is rejected. Remove the ID."
            problems.append(_step_problem(item, step, field_path, message))
    for index, page in enumerate(copies.pages):
        target = by_id.get(page.target)
        if (
            target is None
            or isinstance(target.node, Skill)
            or target.node.status == Status.rejected
        ):
            message = (
                f"No page has the ID {page.target}. "
                "Name a node that is not a skill and not rejected."
            )
            problems.append(_step_problem(item, step, ("pages", index, "target"), message))
    return problems
