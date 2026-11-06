from typing import TYPE_CHECKING

from engine.generated.metamodel import Status
from engine.governance.entities import EXCEPTION
from engine.parser.result import Problem

if TYPE_CHECKING:
    from collections.abc import Collection, Mapping
    from pathlib import Path

    from engine.governance.entities import Entity, EntityKey

CHANGE_CODES = (
    "new-status",
    "promotion-change",
    "accepted-change",
    "status-jump",
    "origin-change",
    "removed-accepted",
)


def _report(entity: Entity, code: str, message: str) -> Problem:
    return Problem(entity.path, entity.line, code, message)


def _changed_fields(old: Entity, new: Entity) -> str:
    fields = {
        field
        for field in old.reviewed.keys() | new.reviewed.keys()
        if old.reviewed.get(field) != new.reviewed.get(field)
    }
    return ", ".join(sorted(fields))


def _transition_problems(old: Entity, new: Entity) -> list[Problem]:
    problems: list[Problem] = []
    if old.origin != new.origin:
        message = f"Keep the origin of {new.label}. HEAD has {old.origin}."
        problems.append(_report(new, "origin-change", message))
    if new.status != Status.accepted:
        return problems
    changed = _changed_fields(old, new)
    if old.status == Status.deprecated:
        message = f"Set {new.label} to proposed first. HEAD has it as deprecated."
        problems.append(_report(new, "status-jump", message))
    elif changed and old.status == Status.proposed:
        message = (
            f"This commit accepts {new.label} and changes {changed}. "
            "Commit the change as proposed, and accept it in a later commit."
        )
        problems.append(_report(new, "promotion-change", message))
    elif changed:
        message = f"This commit changes {changed} on {new.label}. Set its status to proposed."
        problems.append(_report(new, "accepted-change", message))
    return problems


def check_changes(
    base: Mapping[EntityKey, Entity],
    current: Mapping[EntityKey, Entity],
    unreadable: Collection[Path] = (),
) -> list[Problem]:
    problems: list[Problem] = []
    for key, new in current.items():
        old = base.get(key)
        if old is not None:
            problems += _transition_problems(old, new)
        elif new.status != Status.proposed and new.path not in unreadable:
            message = f"HEAD does not have {new.label}. Set its status to proposed."
            problems.append(_report(new, "new-status", message))
    for key, old in base.items():
        if key not in current and old.status == Status.accepted and old.kind != EXCEPTION:
            message = (
                f"HEAD has {old.label} as accepted. Set its status to deprecated in one commit, "
                "and remove it in a later commit."
            )
            problems.append(_report(old, "removed-accepted", message))
    return problems
