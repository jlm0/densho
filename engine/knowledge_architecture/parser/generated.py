from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

MARKER = "<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->"
FRONT_MATTER_DELIMITER = b"---"


def is_generated(data: bytes) -> bool:
    lines = data.split(b"\n")
    start = 0
    if lines[0] == FRONT_MATTER_DELIMITER and FRONT_MATTER_DELIMITER in lines[1:]:
        start = lines.index(FRONT_MATTER_DELIMITER, 1) + 1
    return start < len(lines) and lines[start] == MARKER.encode("utf-8")


def is_generated_file(path: Path) -> bool:
    try:
        return is_generated(path.read_bytes())
    except OSError:
        return False
