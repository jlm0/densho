import re
from typing import TYPE_CHECKING

from engine.generated.metamodel import Status

if TYPE_CHECKING:
    from collections.abc import Iterable

    from engine.governance.entities import Entity

LINE_ENDING = re.compile(rb"(\r\n|\r|\n)")
PARTS_FOR_EACH_LINE = 2


def _status_pattern(status: Status) -> re.Pattern[bytes]:
    word = re.escape(Status(status).value.encode("ascii"))
    return re.compile(rb"(?<![\w-])(status\s*:\s*[\"'`]?)" + word + rb"(?![\w-])")


def set_status_lines(
    data: bytes, entities: Iterable[Entity], status: Status
) -> tuple[bytes, list[Entity]]:
    parts = LINE_ENDING.split(data)
    replacement = rb"\g<1>" + Status(status).value.encode("ascii")
    missed: list[Entity] = []
    for entity in entities:
        index = (entity.line - 1) * PARTS_FOR_EACH_LINE
        count = 0
        if index < len(parts):
            parts[index], count = _status_pattern(entity.status).subn(
                replacement, parts[index], count=1
            )
        if not count:
            missed.append(entity)
    return b"".join(parts), missed
