import re
from typing import TYPE_CHECKING, Any, cast

from ruamel.yaml import YAML
from ruamel.yaml.error import YAMLError

from engine.generated.metamodel import Discipline, Origin
from engine.graph.references import edge_targets
from engine.layout import ANSWERS_FILE
from engine.parser.result import Problem

if TYPE_CHECKING:
    from collections.abc import Sequence
    from pathlib import Path

    from engine.parser.result import ParsedNode

ANSWER_KEY = "disciplines"
ID_FORM = re.compile(r"[a-z][a-z0-9]*(-[a-z0-9]+)*")


def read_answer(repository: Path) -> tuple[list[str] | None, list[Problem]]:
    path = repository / ANSWERS_FILE
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None, []
    except OSError, UnicodeDecodeError:
        return None, [Problem(path, 1, "select", "The file cannot be read as UTF-8 text.")]
    yaml: Any = YAML(typ="base")
    try:
        data = cast("object", yaml.load(text))
    except YAMLError:
        return None, [Problem(path, 1, "select", "The file is not valid YAML.")]
    if not isinstance(data, dict) or ANSWER_KEY not in data:
        return None, []
    answer = cast("dict[object, object]", data)[ANSWER_KEY]
    if not isinstance(answer, list) or not all(
        isinstance(name, str) and ID_FORM.fullmatch(name) for name in cast("list[object]", answer)
    ):
        message = f"{ANSWER_KEY} must be a list of discipline IDs."
        return None, [Problem(path, 1, "select", message)]
    return cast("list[str]", answer), []


def memberships(items: Sequence[ParsedNode]) -> dict[str, frozenset[str]]:
    by_id = {item.node.id: item for item in items}
    disciplines = {
        item.node.id
        for item in items
        if isinstance(item.node, Discipline) and item.node.origin == Origin.template
    }
    found: dict[str, frozenset[str]] = {}
    for start in by_id:
        reached: set[str] = set()
        seen = {start}
        waiting = [start]
        while waiting:
            node_id = waiting.pop()
            if node_id in disciplines:
                reached.add(node_id)
            for parent in edge_targets(by_id[node_id], "broader"):
                if parent in by_id and parent not in seen:
                    seen.add(parent)
                    waiting.append(parent)
        found[start] = frozenset(reached)
    return found
