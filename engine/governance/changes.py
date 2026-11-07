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
    "pull-promotion",
)
CLOSED_STATUSES = frozenset({Status.deprecated, Status.rejected})
OUT_OF_PROPOSAL = frozenset({Status.accepted, Status.deprecated})


def _report(entity: Entity, code: str, message: str) -> Problem:
    return Problem(entity.path, entity.line, code, message)


def _changed_fields(old: Entity, new: Entity) -> str:
    fields = {
        field
        for field in old.reviewed.keys() | new.reviewed.keys()
        if old.reviewed.get(field) != new.reviewed.get(field)
    }
    return ", ".join(sorted(fields))


def _rejection_message(old: Entity, new: Entity) -> str | None:
    if new.status != Status.rejected or old.status not in OUT_OF_PROPOSAL:
        return None
    if old.status == Status.accepted:
        return (
            f"HEAD has {new.label} as accepted. Set it to deprecated. A person rejects a proposal."
        )
    return f"HEAD has {new.label} as deprecated. Keep it deprecated. A person rejects a proposal."


def _transition_problems(old: Entity, new: Entity) -> list[Problem]:
    problems: list[Problem] = []
    if old.origin != new.origin:
        message = f"Keep the origin of {new.label}. HEAD has {old.origin}."
        problems.append(_report(new, "origin-change", message))
    rejection = _rejection_message(old, new)
    if rejection is not None:
        problems.append(_report(new, "status-jump", rejection))
    if new.status != Status.accepted:
        return problems
    changed = _changed_fields(old, new)
    if old.status in CLOSED_STATUSES:
        message = f"Set {new.label} to proposed first. HEAD has it as {Status(old.status).value}."
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


def _new_status_message(
    key: EntityKey, new: Entity, template_accepted: Collection[EntityKey] | None
) -> str | None:
    if template_accepted is None or new.status != Status.accepted:
        return f"HEAD does not have {new.label}. Set its status to proposed."
    if key in template_accepted:
        return None
    return (
        f"HEAD does not have {new.label}, and the template history holds no accepted line "
        "with its content. Set its status to proposed."
    )


def _removed_message(old: Entity, discipline: str | None) -> str:
    if discipline is None:
        return (
            f"HEAD has {old.label} as accepted. Set its status to deprecated in one commit, "
            "and remove it in a later commit."
        )
    return (
        f"HEAD has {old.label} as accepted, and disciplines leaves out {discipline}. "
        f"Put {discipline} back in disciplines, and set each accepted entity of {discipline} "
        "to deprecated in one commit. Then leave it out in a later pull."
    )


def _pull_promotion(old: Entity, new: Entity) -> Problem | None:
    if old.status != Status.proposed or new.status != Status.accepted:
        return None
    message = (
        f"This commit pulls a template change and accepts {new.label}. "
        "A pull cannot accept an entity. Run ka adopt, commit the pull, "
        "and accept it in a later commit."
    )
    return _report(new, "pull-promotion", message)


def check_changes(  # noqa: PLR0913
    base: Mapping[EntityKey, Entity],
    current: Mapping[EntityKey, Entity],
    unreadable: Collection[Path] = (),
    template_accepted: Collection[EntityKey] | None = None,
    left_out: Mapping[EntityKey, str] | None = None,
    *,
    pulled: bool = False,
) -> list[Problem]:
    problems: list[Problem] = []
    for key, new in current.items():
        old = base.get(key)
        if old is not None:
            problems += _transition_problems(old, new)
            promotion = _pull_promotion(old, new) if pulled else None
            if promotion is not None:
                problems.append(promotion)
        elif new.status != Status.proposed and new.path not in unreadable:
            message = _new_status_message(key, new, template_accepted)
            if message is not None:
                problems.append(_report(new, "new-status", message))
    for key, old in base.items():
        if key not in current and old.status == Status.accepted and old.kind != EXCEPTION:
            message = _removed_message(old, (left_out or {}).get(key))
            problems.append(_report(old, "removed-accepted", message))
    return problems
